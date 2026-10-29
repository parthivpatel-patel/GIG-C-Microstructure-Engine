#!/usr/bin/env python3
"""Bounded in-memory REST qualification,independent of disk-retention authorization."""
import argparse,asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.service import StockWorkspace
from terminal.stocks.alpaca_history import acquire
async def qualify(a):
    w=StockWorkspace()
    r=await acquire(w,a.symbol,a.kind,a.start,a.end,a.timeframe,a.max_pages)
    return {k:r[k] for k in ('schema','symbol','kind','provider','feed','origin','availability','freshness','record_count','pages','has_more','complete_market_history','requested_interval','source_records','scope','retention')}
def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--symbol',default='AAPL');p.add_argument('--kind',choices=('bars','quotes','trades'),default='bars');p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--timeframe',choices=('1Day','1Hour','1Min'),default='1Day');p.add_argument('--max-pages',type=int,choices=range(1,5),default=1);a=p.parse_args()
    if not a.execute:p.error('No request made;explicit --execute and existing server permissions required')
    try:r=asyncio.run(qualify(a))
    except Exception:print(json.dumps({'status':'BLOCKED_OR_REJECTED','reason':'source_permissions_credentials_network_interval_or_validation','credential_values_emitted':False}));return 2
    print(json.dumps({**r,'raw_records_emitted':False,'qualification':'BOUNDED_HISTORICAL_READ_ONLY_NOT_LIVE_OR_INDEPENDENT_EXCHANGE_VALIDATION'},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
