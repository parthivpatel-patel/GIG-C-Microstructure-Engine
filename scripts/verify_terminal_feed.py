#!/usr/bin/env python3
"""Bounded live verification after server-side legal/protocol attestation. No recording."""
import argparse,asyncio,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.providers.supervisor import FeedSupervisor
from terminal.providers.kraken import ProviderError

async def main():
    p=argparse.ArgumentParser();p.add_argument('--symbol',choices=['BTC/USD','ETH/USD'],default='BTC/USD')
    p.add_argument('--seconds',type=int,default=20);a=p.parse_args()
    if not 1<=a.seconds<=60:p.error('seconds must be between1 and60')
    feed=FeedSupervisor();started=time.monotonic()
    try:
        await feed.start(a.symbol)
        async with asyncio.timeout(a.seconds+1):await asyncio.sleep(a.seconds)
        view=feed.view()
        report={'schema':'gig.live.smoke.v1','provider':'kraken','endpoint':'wss://ws.kraken.com/v2',
            'symbol':a.symbol,'duration_seconds':round(time.monotonic()-started,3),'feed':view['feed'],
            'origin':view['origin'],'native_metrics':view['metrics'],
            'bid_levels':len(view['book']['bids']),'ask_levels':len(view['book']['asks']),
            'source_timestamp_ns':view['source_timestamp_ns'],'received_at_ns':view['received_at_ns'],
            'observed_recording':False,'browser_verified':False}
        print(json.dumps(report,indent=2))
        return 0 if view['feed']['state']=='LIVE_VERIFIED' else 1
    except ProviderError as e:
        print(json.dumps({'status':'BLOCKED','code':e.code,'socket_started':False,'recording':False}));return 2
    finally:await feed.close()

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
