#!/usr/bin/env python3
"""Owner-executed bounded historical qualification;all existing gates are mandatory."""
import argparse,asyncio,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.service import StockWorkspace,AccessError
from terminal.stocks.acquisition import ingest

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--symbol',default='AAPL');p.add_argument('--start',required=True);p.add_argument('--end',required=True);p.add_argument('--timeframe',default='1Day',choices=('1Day','1Hour','1Min'));p.add_argument('--max-pages',type=int,default=1,choices=range(1,5));a=p.parse_args()
    if not a.execute:p.error('explicit --execute and existing server-side authorization required')
    try:
        workspace=StockWorkspace();result=asyncio.run(ingest(workspace,a.symbol,a.start,a.end,a.timeframe,a.max_pages))
    except Exception as e:
        print(json.dumps({'status':'BLOCKED_OR_FAILED','reason':str(e) if isinstance(e,AccessError) else 'sanitized_configuration_source_or_storage_failure','live_provider_qualification':False}));return 2
    print(json.dumps({**result,'scope':'Historical REST only;not live WebSocket qualification','raw_rows_printed':False},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
