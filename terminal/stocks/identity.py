import re
# Curated routing seeds, not a downloaded exchange directory or price observations.
SEEDS=[('AAPL','Apple Inc.','NASDAQ',320193),('NVDA','NVIDIA Corporation','NASDAQ',1045810),('TSLA','Tesla Inc.','NASDAQ',1318605),('MSFT','Microsoft Corporation','NASDAQ',789019),('AMZN','Amazon.com Inc.','NASDAQ',1018724),('GOOG','Alphabet Inc.','NASDAQ',1652044),('META','Meta Platforms Inc.','NASDAQ',1326801),('JPM','JPMorgan Chase & Co.','NYSE',19617)]

def symbol(value):
    if type(value) is not str or not re.fullmatch(r'[A-Z]{1,5}(?:[.-][A-Z])?',value):raise ValueError('invalid_symbol')
    return value

def instrument(ticker):
    symbol(ticker)
    for t,n,e,c in SEEDS:
        if t==ticker:return {'symbol':t,'company_name':n,'exchange':e,'cik':str(c).zfill(10),'currency':'USD','identity_source':'curated_routing_seed_not_fresh_official_directory','identity_as_of':None}
    raise ValueError('unsupported_symbol')

def search(query):
    if type(query) is not str or len(query)>80 or any(ord(c)<32 for c in query):raise ValueError('invalid_query')
    q=query.strip().casefold()
    return [instrument(t) for t,n,_,_ in SEEDS if q in t.casefold() or q in n.casefold()][:20]
