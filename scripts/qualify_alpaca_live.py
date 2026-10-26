#!/usr/bin/env python3
"""Owner-only bounded qualification. No connection without --execute AND all gates."""
import argparse,asyncio,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.service import StockWorkspace
from terminal.stocks.live import LiveIEX

async def qualify(args):
    stream=LiveIEX(StockWorkspace());start=time.monotonic()
    try:
        await stream.start([args.symbol])
        while time.monotonic()-start<args.seconds and stream.state!='FAILED':await asyncio.sleep(.25)
        status=stream.view();kinds={r['kind'] for r in status['observations'] if r['state']=='LIVE'}
        ok=status['state']=='SUBSCRIBED' and {'quote','trade'}<=kinds
        report={'schema':'gig.alpaca.live.qualification.v1','status':'PASS_BOUNDED_LIVE_OBSERVATIONS' if ok else 'INCOMPLETE_OR_FAILED','provider':'alpaca','feed':'iex','symbol':args.symbol,'elapsed_seconds':time.monotonic()-start,'phase':status['phase'],'reason':status['reason'],'accepted_observations':status['accepted_observations'],'duplicates':status['duplicate_observations'],'generation':status['generation'],'observed_kinds':sorted(kinds),'source_sha256':[r['source_sha256'] for r in status['observations']],'limitations':['No independent exchange comparison or market-wide completeness','No crash durability,broker execution or forecasting qualification','No raw observations or credentials emitted by this report']}
        print(json.dumps(report,indent=2));return 0 if ok else 1
    finally:await stream.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--symbol',default='AAPL');p.add_argument('--seconds',type=int,default=30,choices=range(5,61));a=p.parse_args()
    if not a.execute:p.error('No network attempted;explicit --execute and all server permission gates required')
    try:return asyncio.run(qualify(a))
    except (ValueError,TypeError):print(json.dumps({'status':'BLOCKED','reason':'server_permissions_or_configuration_unavailable','network_activation':'no permission bypass'}));return 2
if __name__=='__main__':raise SystemExit(main())
