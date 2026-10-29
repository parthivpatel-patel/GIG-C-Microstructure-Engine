#!/usr/bin/env python3
"""Explicit bounded account-reference qualification;counts/hashes only,never credentials."""
import argparse,asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.service import StockWorkspace
async def qualify():
    from terminal.stocks.qualification import nonretaining_environment
    w=StockWorkspace(environment=nonretaining_environment())
    await w.asset_reference.refresh()
    from terminal.stocks.qualification import reference_summary
    qualification=reference_summary(w)
    rows=w.catalog.rows
    return {'schema':'gig.alpaca.reference.qualification.v1','status':'ACCEPTED_ACCOUNT_REFERENCE_NOT_COMPLETE_US_LISTING_PROOF',
        'qualification_status':qualification['status'],'provider':'alpaca','account_endpoint':'paper /v2/assets GET only','accepted_identities':len(rows),
        'active':sum(r['listing_status']=='ACTIVE' for r in rows.values()),'inactive':sum(r['listing_status']=='INACTIVE' for r in rows.values()),
        'source':w.catalog.source,'representative_symbols':{s:s in rows for s in ('AAPL','GOOGL','MSFT','NVDA','AMZN','APLD','CRWV')},
        'sec_mapping_count':0,'orders_or_raw_market_observations_emitted':False,'market_data_entitlement_verified':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');a=p.parse_args()
    if not a.execute:p.error('No request made;explicit --execute and existing server permissions required')
    try:r=asyncio.run(qualify())
    except Exception:print(json.dumps({'status':'BLOCKED_OR_REJECTED','reason':'source_permissions_credentials_network_or_validation','credential_values_emitted':False}));return 2
    print(json.dumps(r,indent=2));return 0 if r['qualification_status']=='PASS_OBSERVED_ACCOUNT_REFERENCE' else 1
if __name__=='__main__':raise SystemExit(main())
