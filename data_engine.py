import pandas as pd
ALIASES={'time':'time','date':'time','datetime':'time','timestamp':'time','open':'open','o':'open','high':'high','h':'high','low':'low','l':'low','close':'close','c':'close','volume':'volume','tick_volume':'volume'}
def load_csv(uploaded_file): return pd.read_csv(uploaded_file)
def prepare_data(df):
    if df is None or df.empty: raise ValueError('No data provided.')
    out=df.copy(); out.columns=[str(c).strip().lower() for c in out.columns]; out=out.rename(columns={c:ALIASES[c] for c in out.columns if c in ALIASES})
    req=['open','high','low','close']; missing=[c for c in req if c not in out.columns]
    if missing: raise ValueError('Missing required columns: '+', '.join(missing))
    if 'time' in out: out['time']=pd.to_datetime(out['time'],errors='coerce')
    for c in req+(['volume'] if 'volume' in out else []): out[c]=pd.to_numeric(out[c],errors='coerce')
    out=out.dropna(subset=req)
    if 'time' in out: out=out.dropna(subset=['time']).sort_values('time').drop_duplicates('time',keep='last')
    invalid=(out.high<out[['open','close','low']].max(axis=1))|(out.low>out[['open','close','high']].min(axis=1))|(out.high<out.low)
    out=out.loc[~invalid].reset_index(drop=True)
    if len(out)<3: raise ValueError('Not enough valid candles after cleaning.')
    return out
def validate_data(df):
    r={'valid':True,'errors':[],'rows':0,'duplicates':0,'invalid_ohlc':0,'missing_bars':0}
    if df is None or df.empty: r.update(valid=False);r['errors'].append('Dataset is empty.');return r
    r['rows']=len(df); req=['open','high','low','close']; missing=[c for c in req if c not in df.columns]
    if missing:r.update(valid=False);r['errors'].append('Missing columns: '+str(missing));return r
    bad=(df.high<df[['open','close','low']].max(axis=1))|(df.low>df[['open','close','high']].min(axis=1))|(df.high<df.low);r['invalid_ohlc']=int(bad.sum())
    if r['invalid_ohlc']:r['valid']=False;r['errors'].append('Invalid OHLC candles found.')
    if 'time' in df:
        r['duplicates']=int(df.time.duplicated().sum());t=pd.to_datetime(df.time,errors='coerce').dropna().sort_values();d=t.diff().dropna()
        if len(d): base=d.mode().iloc[0];r['missing_bars']=int((d>base*1.5).sum()) if base>pd.Timedelta(0) else 0
    return r
