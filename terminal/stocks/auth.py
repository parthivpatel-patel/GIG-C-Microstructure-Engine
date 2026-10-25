"""Alpaca credential selectors;no secret value ever returned to browser diagnostics."""
import re

def credentials(environment):
    pairs=[]
    for prefix in ('ALPACA','APCA'):
        key=environment.get(prefix+'_API_KEY_ID','');secret=environment.get(prefix+'_API_SECRET_KEY','')
        if key or secret:
            if not key or not secret:raise ValueError('alpaca_incomplete_'+prefix.lower()+'_credential_pair')
            if any(not re.fullmatch(r'[A-Za-z0-9_-]{8,256}',v) for v in (key,secret)):raise ValueError('alpaca_invalid_server_credentials')
            pairs.append((prefix,key,secret))
    if not pairs:raise ValueError('alpaca_server_credentials_required')
    if len(pairs)==2 and pairs[0][1:]!=pairs[1][1:]:raise ValueError('alpaca_conflicting_credential_aliases')
    _,key,secret=pairs[0]
    return {'APCA-API-KEY-ID':key,'APCA-API-SECRET-KEY':secret}

def presence(environment):
    return {prefix+'_pair_present':bool(environment.get(prefix+'_API_KEY_ID') and environment.get(prefix+'_API_SECRET_KEY')) for prefix in ('ALPACA','APCA')}|{'paper_base_url_configured':bool(environment.get('ALPACA_PAPER_BASE_URL')),'paper_base_url_used_for_market_data':False}
