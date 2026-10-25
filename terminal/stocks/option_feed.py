"""Provisional Alpaca indicative option snapshots;strictly distinct from paid OPRA."""
from decimal import Decimal,InvalidOperation
from .options import contract
from .prices import quote,trade,decimal,timestamp

def signed(value):
    if type(value) not in (int,Decimal,str) or isinstance(value,bool) or len(str(value))>48:raise ValueError('option_model_value')
    try:n=Decimal(value)
    except InvalidOperation:raise ValueError('option_model_value') from None
    if not n.is_finite() or abs(n)>1000000 or not -12<=n.as_tuple().exponent<=12:raise ValueError('option_model_value')
    return str(n)

def snapshots(payload,ticker):
    data=payload.get('snapshots')
    if type(data) is not dict or len(data)>100:raise ValueError('option_snapshot_budget')
    rows=[]
    for code,s in data.items():
        identity=contract(code)
        if identity['underlying']!=ticker or type(s) is not dict:raise ValueError('option_underlying')
        row={**identity,'symbol':code,'quote':None,'trade':None,'provider_implied_volatility':None,'provider_greeks':{}}
        if s.get('latestQuote') is not None:row['quote']={**quote({'symbol':code,'quote':s['latestQuote']},code),'scope':'indicative option quote;not IEX equity,OPRA or executable price'}
        if s.get('latestTrade') is not None:row['trade']={**trade({'symbol':code,'trade':s['latestTrade']},code),'scope':'indicative-feed option print;feed-specific delay unverified'}
        if s.get('impliedVolatility') is not None:
            v=decimal(s['impliedVolatility'])
            if Decimal(v)>10:raise ValueError('option_iv_range')
            row['provider_implied_volatility']=v
        if s.get('greeks') is not None:
            if type(s['greeks']) is not dict:raise ValueError('option_greeks')
            row['provider_greeks']={k:signed(v) for k,v in s['greeks'].items() if k in ('delta','gamma','theta','vega','rho') and v is not None}
        rows.append(row)
    rows.sort(key=lambda r:(r['expiration'],int(r['strike_millis']),r['right']))
    return {'contracts':rows,'feed':'indicative','observation_class':'INDICATIVE_FEED_NOT_OPRA_NOT_EXECUTABLE_PRICE','delay_seconds':None,'delay_authority':'current feed-specific quote/trade delay not independently verified','model_value_scope':'IV/Greeks are provider-supplied derived estimates,not independent observed market quantities','complete_chain':False,'next_page_available':bool(payload.get('next_page_token')),'reason':None if rows else 'no_contracts_returned;check underlying,feed entitlement and current API profile','open_interest_available':False}
