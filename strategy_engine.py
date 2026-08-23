abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    name='Base Strategy'
    def prepare(self,data): return data.copy().reset_index(drop=True)
    @abstractmethod
    def generate_signal(self,data,index): raise NotImplementedError

class PriceActionReversalStrategy(BaseStrategy):
    name='Price Action Reversal'
    def __init__(self,risk_reward=2.0): self.risk_reward=max(.1,float(risk_reward))
    def generate_signal(self,data,index):
        if index<1:return {}
        p,c=data.iloc[index-1],data.iloc[index]
        po,pc=float(p.open),float(p.close); co,cc=float(c.open),float(c.close)
        if pc<po and cc>co and co<=pc and cc>=po:
            r=cc-float(c.low)
            return {'side':'LONG','stop_loss':float(c.low),'take_profit':cc+r*self.risk_reward,'metadata':{'pattern':'bullish_engulfing'}} if r>0 else {}
        if pc>po and cc<co and co>=pc and cc<=po:
            r=float(c.high)-cc
            return {'side':'SHORT','stop_loss':float(c.high),'take_profit':cc-r*self.risk_reward,'metadata':{'pattern':'bearish_engulfing'}} if r>0 else {}
        return {}

class EmaTrendPullbackStrategy(BaseStrategy):
    name='EMA Trend Pullback'
    def __init__(self,fast_period=20,slow_period=200,risk_reward=2.0):
        self.fast_period=max(2,int(fast_period)); self.slow_period=max(self.fast_period+1,int(slow_period)); self.risk_reward=max(.1,float(risk_reward))
    def prepare(self,data):
        df=super().prepare(data); df['ema_fast']=df.close.ewm(span=self.fast_period,adjust=False).mean(); df['ema_slow']=df.close.ewm(span=self.slow_period,adjust=False).mean(); return df
    def generate_signal(self,data,index):
        if index<self.slow_period:return {}
        p,c=data.iloc[index-1],data.iloc[index]
        if pd.isna([p.close,p.ema_fast,c.close,c.ema_fast,c.ema_slow]).any():return {}
        long_=float(p.close)<=float(p.ema_fast) and float(c.close)>float(c.ema_fast) and float(c.close)>float(c.ema_slow)
        short_=float(p.close)>=float(p.ema_fast) and float(c.close)<float(c.ema_fast) and float(c.close)<float(c.ema_slow)
        if long_:
            r=float(c.close)-float(c.low); return {'side':'LONG','stop_loss':float(c.low),'take_profit':float(c.close)+r*self.risk_reward,'metadata':{}} if r>0 else {}
        if short_:
            r=float(c.high)-float(c.close); return {'side':'SHORT','stop_loss':float(c.high),'take_profit':float(c.close)-r*self.risk_reward,'metadata':{}} if r>0 else {}
        return {}

STRATEGY_REGISTRY={PriceActionReversalStrategy.name:PriceActionReversalStrategy,EmaTrendPullbackStrategy.name:EmaTrendPullbackStrategy}
def create_strategy(name,**params):
    if name not in STRATEGY_REGISTRY: raise ValueError(f'Unknown strategy: {name}')
    return STRATEGY_REGISTRY[name](**params)
