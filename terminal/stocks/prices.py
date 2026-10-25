"""Provisional Alpaca IEX response profile; exact observed units and explicit scope."""
import datetime
from decimal import Decimal,InvalidOperation
from fractions import Fraction
from zoneinfo import ZoneInfo
from terminal.providers.kraken import timestamp_ns

def decimal(value,positive=False):
    if type(value) not in (str,int,Decimal) or isinstance(value,bool):raise ValueError('price_numeric')
    if len(str(value))>48:raise ValueError('price_numeric')
    try:n=Decimal(value)
    except InvalidOperation:raise ValueError('price_numeric') from None
    if not n.is_finite() or n<0 or n>10**15 or (positive and n==0) or not -12<=n.as_tuple().exponent<=15:raise ValueError('price_numeric')
    # Never round; even a provider number beyond eight places is retained exactly.
    return str(n)

def timestamp(value):
    if type(value) is not str or len(value)>40:raise ValueError('price_timestamp')
    timestamp_ns(value)
    t=datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('price_timestamp')
    return t

def market_window(value):
    local=timestamp(value).astimezone(ZoneInfo('America/New_York'))
    return {'timezone':'America/New_York','clock_window':'REGULAR_CLOCK_WINDOW' if local.weekday()<5 and datetime.time(9,30)<=local.time()<datetime.time(16) else 'OUTSIDE_REGULAR_CLOCK_WINDOW','authority':'weekday clock only;not exchange holiday,halt or auction calendar'}

def bars(payload,ticker):
    if payload.get('symbol')!=ticker or type(payload.get('bars')) is not list or len(payload['bars'])>256:raise ValueError('bar_identity_or_budget')
    result=[];prior=None;total=Fraction();volume=Fraction()
    for r in payload['bars']:
        timestamp(r['t']);stamp=int(timestamp_ns(r['t']))
        if prior is not None and stamp<=prior:raise ValueError('bar_order')
        prior=stamp
        item={k:decimal(r[field],True) for k,field in [('open','o'),('high','h'),('low','l'),('close','c')]}
        if not Fraction(item['low'])<=min(Fraction(item['open']),Fraction(item['close']))<=max(Fraction(item['open']),Fraction(item['close']))<=Fraction(item['high']):raise ValueError('bar_ohlc')
        v=decimal(r['v']);vwap=decimal(r['vw'],True) if r.get('vw') is not None else None
        item.update(timestamp=r['t'],volume=v,vwap=vwap,trade_count=str(r['n']) if type(r.get('n')) is int and r['n']>=0 else None)
        if vwap is not None:total+=Fraction(vwap)*Fraction(v);volume+=Fraction(v)
        result.append(item)
    complete=all(r['vwap'] is not None for r in result)
    weighted=total/volume if volume and complete else None
    return {'bars':result,'next_page_available':bool(payload.get('next_page_token')),'complete_history':False,'vwap':{'value':{'numerator':str(weighted.numerator),'denominator':str(weighted.denominator)} if weighted is not None else None,'method':'volume-weighted supplied bar VWAP over returned IEX interval;not consolidated market VWAP'},'volume_unit':'provider_reported_volume;no_lot_conversion','feed':'iex','scope':'single-venue IEX only;no SIP/NBBO/depth/full-market claim','adjustment':'raw','session':market_window(result[-1]['timestamp']) if result else None}

def quote(payload,ticker):
    if payload.get('symbol')!=ticker or type(payload.get('quote')) is not dict:raise ValueError('quote_identity')
    q=payload['quote'];timestamp(q['t'])
    return {'timestamp':q['t'],'bid':decimal(q['bp']),'ask':decimal(q['ap']),'bid_size':decimal(q['bs']),'ask_size':decimal(q['as']),'size_unit':'provider_reported_unverified;no_share_or_lot_conversion','scope':'IEX single-venue quote;not NBBO or L2 depth'}

def trade(payload,ticker):
    if payload.get('symbol')!=ticker or type(payload.get('trade')) is not dict:raise ValueError('trade_identity')
    t=payload['trade'];timestamp(t['t'])
    return {'timestamp':t['t'],'price':decimal(t['p'],True),'size':decimal(t['s'],True),'size_unit':'provider_reported_unverified;no_lot_conversion','scope':'IEX single-venue print;not inferred book execution'}
