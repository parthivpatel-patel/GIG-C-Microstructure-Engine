#!/usr/bin/env python3
"""Explicitly owner-approved bounded provider candidate test. Disabled by default,no recording."""
import argparse,asyncio,hashlib,json,os,sys,time
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gig_microstructure as gig
from terminal.providers.supervisor import configured_permission
from terminal.providers.kraken import ProviderError,KrakenBookAdapter,MAX_PAYLOAD
from terminal.providers.coinbase_candidate import CoinbaseCandidate

async def qualify(provider,symbol,seconds,*,environment=None,transport=None):
    if provider not in ('kraken','coinbase') or symbol not in ('BTC/USD','ETH/USD') or type(seconds) is not int or not 1<=seconds<=20:raise ValueError('bounded_configuration')
    e=os.environ if environment is None else environment;prefix='GIG_LIVE_' if provider=='kraken' else 'GIG_COINBASE_'
    if e.get('GIG_PROVIDER_SUBSCRIPTION_TEST_APPROVED')!='1' or e.get(prefix+'ENABLED')!='1':raise ProviderError('explicit_owner_subscription_test_approval_required')
    permission=configured_permission(e,provider);permission.require_live()
    fixture=transport is not None
    if transport is None:
        if provider=='kraken':from terminal.providers.kraken import live_messages as transport
        else:from terminal.providers.coinbase_transport import live_messages as transport
    native=gig._native.AggregateDepth(32 if provider=='kraken' else 256,1048576)
    def apply(**event):return gig._checked((native.snapshot if event['snapshot'] else native.update)(event['bids'],event['asks'],event['sequence']))
    origin='HISTORICAL_SYNTHETIC' if fixture else 'LIVE_OBSERVED'
    adapter=KrakenBookAdapter(apply,symbol=symbol,origin=origin) if provider=='kraken' else CoinbaseCandidate(apply,symbol=symbol.replace('/','-'),origin=origin)
    adapter.connect();stop=asyncio.Event();counts=Counter();size=0;started=time.monotonic();reason='source_ended';stream=transport(permission,stop=stop,symbol=symbol)
    try:
        async with asyncio.timeout(seconds):
            while sum(counts.values())<256 and size+MAX_PAYLOAD<=2*1024*1024:
                try:raw=await anext(stream)
                except StopAsyncIteration:break
                if type(raw) is not str or len(raw.encode())>MAX_PAYLOAD:raise ProviderError('payload_limit')
                size+=len(raw.encode());receipt=adapter.feed(raw,time.monotonic_ns());counts[receipt['kind']]+=1
            else:reason='application_budget_boundary'
    except TimeoutError:reason='time_boundary'
    finally:
        stop.set();await stream.aclose()
    state=gig._checked(native.state());books=counts['snapshot']+counts['update']
    return {'schema':'gig.provider.bounded_candidate.v1','provider':provider,'instrument':symbol,'classification':origin,'status':'TESTED_WITH_FIXTURES' if fixture else 'OPERATOR_ATTESTED_BOUNDED_OBSERVATIONS' if books else 'INCONCLUSIVE','message_kinds':dict(counts),'consumed_application_bytes':size,'duration_seconds':round(time.monotonic()-started,3),'stop_reason':reason,'native_book_transactions':books,'native_revision':state['revision'],'native_state_sha256':hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest(),'recording':False,'raw_payloads_retained':False,'maximum_application_frames':256,'maximum_consumed_application_bytes':2*1024*1024,'scope':'candidate parser/native integrity,not independent current official protocol qualification;wire/TLS bytes unmeasured;no displayed prices or trade rows printed'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--provider',choices=['kraken','coinbase'],default='kraken');p.add_argument('--symbol',choices=['BTC/USD','ETH/USD'],default='BTC/USD');p.add_argument('--seconds',type=int,default=10);a=p.parse_args()
    try:print(json.dumps(asyncio.run(qualify(a.provider,a.symbol,a.seconds)),indent=2))
    except ProviderError as exc:print(json.dumps({'status':'BLOCKED_OR_REJECTED','code':exc.code,'recording':False}));raise SystemExit(2)
    except Exception:print(json.dumps({'status':'REJECTED','code':'sanitized_transport_or_validation_failure','recording':False}));raise SystemExit(2)

