from dataclasses import dataclass
from typing import Optional,Callable
import math,numpy as np,pandas as pd
@dataclass
class Position:
    side:str; entry_time:object; entry_mid:float; entry_exec:float; stop_loss:float; take_profit:float; units:float; risk_amount:float; entry_index:int; metadata:dict
class BacktestEngine:
    def __init__(self,initial_balance=10000,risk_percent=1,spread_pips=1,slippage_pips=0,commission_per_lot=0,pip_size=.0001,lot_size=100000,min_lot=.01,lot_step=.01,intrabar_model='conservative'):
        if initial_balance<=0 or not 0<risk_percent<=100 or pip_size<=0 or lot_size<=0: raise ValueError('Invalid engine settings')
        self.initial_balance=float(initial_balance);self.risk_percent=float(risk_percent);self.spread_pips=max(0,float(spread_pips));self.slippage_pips=max(0,float(slippage_pips));self.commission_per_lot=max(0,float(commission_per_lot));self.pip_size=float(pip_size);self.lot_size=int(lot_size);self.min_lot=max(0,float(min_lot));self.lot_step=max(.000001,float(lot_step));self.intrabar_model=intrabar_model
        if intrabar_model not in {'conservative','optimistic'}: raise ValueError('intrabar_model must be conservative or optimistic')
    @property
    def half_spread(self):return self.spread_pips*self.pip_size/2
    @property
    def slippage(self):return self.slippage_pips*self.pip_size
    def _entry_exec(self,side,mid):return mid+self.half_spread+self.slippage if side=='LONG' else mid-self.half_spread-self.slippage
    def _exit_exec(self,side,mid):return mid-self.half_spread-self.slippage if side=='LONG' else mid+self.half_spread+self.slippage
    def _round_units(self,u):
        lots=u/self.lot_size
        if lots<self.min_lot:return 0
        lots=math.floor(lots/self.lot_step)*self.lot_step;return lots*self.lot_size
    def _commission(self,u):return u/self.lot_size*self.commission_per_lot
    def _size(self,balance,side,entry,sl):
        r=(entry-sl) if side=='LONG' else (sl-entry)
        if r<=0:return 0,0
        u=self._round_units(balance*self.risk_percent/100/r);return (u,u*r) if u>0 else (0,0)
    def _pnl(self,p,exit_):
        gross=(exit_-p.entry_exec)*p.units if p.side=='LONG' else (p.entry_exec-exit_)*p.units;comm=self._commission(p.units)*2;return gross-comm,gross,comm
    def _hit(self,p,row):
        sl=(float(row.low)<=p.stop_loss) if p.side=='LONG' else (float(row.high)>=p.stop_loss);tp=(float(row.high)>=p.take_profit) if p.side=='LONG' else (float(row.low)<=p.take_profit)
        if sl and tp:return (p.stop_loss,'SL') if self.intrabar_model=='conservative' else (p.take_profit,'TP')
        if sl:return p.stop_loss,'SL'
        if tp:return p.take_profit,'TP'
        return None,None
    def _metrics(self,trades,curve):
        if not trades:return {'total_trades':0,'win_rate':0.0,'net_profit':0.0,'gross_profit':0.0,'gross_loss':0.0,'profit_factor':0.0,'expectancy':0.0,'max_drawdown':0.0,'final_balance':self.initial_balance}
        p=np.array([x['net_pnl'] for x in trades],float);w=p[p>0].sum();l=abs(p[p<0].sum());eq=np.array([x['equity'] for x in curve],float);peak=np.maximum.accumulate(eq);dd=np.where(peak>0,(peak-eq)/peak*100,0)
        return {'total_trades':len(trades),'win_rate':float((p>0).mean()*100),'net_profit':float(p.sum()),'gross_profit':float(w),'gross_loss':float(l),'profit_factor':float(w/l) if l else (float('inf') if w else 0.0),'expectancy':float(p.mean()),'max_drawdown':float(dd.max()) if len(dd) else 0.0,'final_balance':float(eq[-1])}
    def run(self,data,strategy,progress_callback:Optional[Callable[[int,int],None]]=None):
        if not {'open','high','low','close'}.issubset(data.columns):raise ValueError('Data must contain open, high, low, close')
        df=strategy.prepare(data);balance=self.initial_balance;pos=None;pending=None;trades=[];curve=[];n=len(df)
        def close(exit_mid,reason,time,i):
            nonlocal pos,balance
            ex=self._exit_exec(pos.side,float(exit_mid));net,gross,comm=self._pnl(pos,ex);balance+=net;trades.append({'side':pos.side,'entry_time':pos.entry_time,'exit_time':time,'entry_mid':pos.entry_mid,'entry_price':pos.entry_exec,'exit_mid':float(exit_mid),'exit_price':ex,'stop_loss':pos.stop_loss,'take_profit':pos.take_profit,'units':pos.units,'lots':pos.units/self.lot_size,'gross_pnl':gross,'commission':comm,'net_pnl':net,'exit_reason':reason,'risk_amount':pos.risk_amount,'r_multiple':net/pos.risk_amount if pos.risk_amount else 0.0,'bars_held':i-pos.entry_index});pos=None
        for i in range(n):
            row=df.iloc[i];time=row['time'] if 'time' in df else i
            if pending and pos is None:
                side=pending['side'];mid=float(row.open);entry=self._entry_exec(side,mid);sl=float(pending['stop_loss']);tp=float(pending['take_profit']);ok=(side=='LONG' and sl<entry<tp) or (side=='SHORT' and tp<entry<sl)
                if ok:
                    u,r=self._size(balance,side,entry,sl)
                    if u>0:pos=Position(side,time,mid,entry,sl,tp,u,r,i,pending.get('metadata',{}))
                pending=None
            if pos:
                x,reason=self._hit(pos,row)
                if x is not None:close(x,reason,time,i)
            unreal=0
            if pos:unreal=self._pnl(pos,self._exit_exec(pos.side,float(row.close)))[0]
            curve.append({'time':time,'balance':balance,'equity':balance+unreal})
            if pos is None and i<n-1:
                s=strategy.generate_signal(df,i)
                if s and s.get('side') in {'LONG','SHORT'}:pending=s
            if progress_callback and (i%max(1,n//200)==0 or i==n-1):progress_callback(i+1,n)
        if pos:
            last=df.iloc[-1];time=last['time'] if 'time' in df else n-1;close(float(last.close),'END_OF_DATA',time,n-1);curve[-1]={'time':time,'balance':balance,'equity':balance}
        return {'metrics':self._metrics(trades,curve),'trades':pd.DataFrame(trades),'equity_curve':pd.DataFrame(curve),'data':df}
