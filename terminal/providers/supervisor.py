"""Single-event-loop, bounded feed lifecycle; production endpoint is fixed.

Injected transports are synthetic-only regardless of their Permission assertions.
No provider credentials, arbitrary URLs, raw payload logging or automatic startup.
"""
import asyncio
from contextlib import suppress
import os
import random
import time
import gig_microstructure as gig
from .kraken import KrakenBookAdapter, Permission, ProviderError, live_messages

SYMBOLS=('BTC/USD','ETH/USD')


def configured_permission(environment,provider='kraken'):
    if provider not in ('kraken','coinbase'):raise ProviderError('configuration')
    prefix='GIG_LIVE_' if provider=='kraken' else 'GIG_COINBASE_'
    reference=environment.get(prefix+'PERMISSION_REFERENCE','')
    if len(reference)>256 or any(ord(x)<32 for x in reference):
        raise ProviderError('permission_reference')
    return Permission(environment.get(prefix+'PROTOCOL_REVIEWED')=='1',
        environment.get(prefix+'PRIVATE_DISPLAY_APPROVED')=='1',
        environment.get(prefix+'CLOUD_PROCESSING_APPROVED')=='1',
        environment.get(prefix+'RECORDING_RETENTION_APPROVED')=='1',reference)


class FeedSupervisor:
    def __init__(self,*,environment=None,transport=None,clock=time.monotonic_ns,
                 wall_clock=time.time_ns,sleep=asyncio.sleep,jitter=None):
        self.environment=os.environ if environment is None else environment
        self.transport=live_messages if transport is None else transport
        self.provider='kraken'
        self.observed_transport=transport is None
        self.clock,self.wall_clock,self.sleep=clock,wall_clock,sleep
        self.jitter=jitter or random.SystemRandom().uniform
        self.task=None;self.stop_event=None
        self.symbol='BTC/USD';self.aggregate=None;self.adapter=None
        self.state='DISCONNECTED';self.reason='explicit_connection_required'
        self.reconnects=0;self.messages=0;self.failures=0;self.received_at_ns=None
        self.exchange_ns=None;self.kind=None;self.epoch=0;self.depth=10
        self.price_scale=100000000;self.quantity_scale=100000000
        self.permission=None;self.pending=False;self.capture=None

    def _new_book(self):
        aggregate=gig._native.AggregateDepth(32 if self.provider=='kraken' else 256,1048576)
        def apply(**event):
            return gig._checked((aggregate.snapshot if event['snapshot'] else aggregate.update)(
                event['bids'],event['asks'],event['sequence']))
        origin='LIVE_OBSERVED' if self.observed_transport else 'HISTORICAL_SYNTHETIC'
        if self.provider=='kraken':
            adapter=KrakenBookAdapter(apply,symbol=self.symbol,price_scale=self.price_scale,quantity_scale=self.quantity_scale,origin=origin)
        else:
            from .coinbase_candidate import CoinbaseCandidate
            adapter=CoinbaseCandidate(apply,symbol=self.symbol.replace('/','-'),origin=origin)
        self.aggregate,self.adapter=aggregate,adapter
        self.exchange_ns=self.received_at_ns=None
        adapter.connect()
        from terminal.l2_research import ResearchWindow
        self.research=ResearchWindow(aggressor_side_confirmed=self.provider=='kraken' and self.environment.get('GIG_LIVE_AGGRESSOR_SIDE_REVIEWED')=='1')
        self.research_cache=None;self.research_cache_until=0

    def cancel(self):
        """Invalidate publication synchronously before the next event-loop await."""
        self.epoch+=1
        if self.stop_event:self.stop_event.set()
        old=self.task;self.task=None
        if old and not old.done():old.cancel()
        self.state,self.reason='DISCONNECTED','operator_disconnected'
        if self.adapter:self.adapter.disconnected()
        self.received_at_ns=self.exchange_ns=None
        return old

    async def close(self):
        old=self.cancel()
        if old:
            with suppress(asyncio.CancelledError):await old
        if self.capture is not None:await self.capture.stop()

    async def start(self,symbol='BTC/USD',*,provider='kraken'):
        if symbol not in SYMBOLS or provider not in ('kraken','coinbase'):raise ProviderError('configuration')
        await self.close()
        if self.provider!=provider:self.capture=None
        self.provider=provider;self.symbol=symbol
        if self.observed_transport:
            if provider=='kraken':self.transport=live_messages
            else:
                from .coinbase_transport import live_messages as coinbase_messages
                self.transport=coinbase_messages
        self.permission=None
        # Gate before creating a task/socket or assigning observed provenance.
        enabled='GIG_LIVE_ENABLED' if provider=='kraken' else 'GIG_COINBASE_ENABLED'
        if self.environment.get(enabled)!='1':
            self.state,self.reason='ERROR','live_disabled_pending_protocol_and_usage_review'
            raise ProviderError(self.reason)
        try:
            permission=configured_permission(self.environment,provider);permission.require_live()
        except ProviderError:
            self.state,self.reason='ERROR','permission_or_current_protocol_unverified'
            raise
        self.symbol,self.permission=symbol,permission
        self.reconnects=self.messages=self.failures=0
        self._new_book();self.stop_event=asyncio.Event()
        self.state,self.reason='CONNECTING','awaiting_provider'
        epoch=self.epoch
        self.task=asyncio.create_task(self._run(epoch),name='gig-one-public-feed')

    async def _run(self,epoch):
        attempt=0
        while epoch==self.epoch and not self.stop_event.is_set():
            self.pending=True
            try:
                self._new_book()
                self.state,self.reason='SYNCHRONIZING','fresh_snapshot_required'
                deadline=self.clock()+15_000_000_000
                stream=self.transport(self.permission,stop=self.stop_event,symbol=self.symbol)
                try:
                    async with asyncio.timeout(15):
                        # Includes connection establishment; subsequent receives each have a budget.
                        first=await anext(stream)
                    raw=first
                    while epoch==self.epoch and not self.stop_event.is_set():
                        self.pending=False
                        if self.messages>=1_000_000_000:raise ProviderError('session_record_budget')
                        now=self.clock();unix=str(self.wall_clock())
                        receipt=self.adapter.feed(raw,now)
                        observed=receipt
                        if self.provider=='coinbase':
                            from .coinbase_transport import research_receipt
                            observed=research_receipt(receipt)
                        if observed['kind'] in ('snapshot','update','trades'):
                            research_event={**observed,'historical_snapshot':self.adapter.last_trade_snapshot} if self.provider=='kraken' and observed['kind']=='trades' else observed
                            state=gig._checked(self.aggregate.state()) if observed['kind']!='trades' else None
                            if state is not None:state={**state,'bids':state['bids'][:self.depth],'asks':state['asks'][:self.depth]}
                            self.research.observe(research_event,state,now,self.messages+1)
                        if self.capture is not None and self.capture.state in ('RECORDING','FINALIZING'):
                            self.capture.offer(raw,now,unix,receipt)
                        self.messages+=1;self.kind=receipt['kind']
                        if self.messages%64==0:await asyncio.sleep(0)
                        if receipt['kind'] in ('snapshot','update'):
                            self.received_at_ns=unix
                            self.exchange_ns=receipt.get('source_timestamp_ns')
                            self.state='LIVE_VERIFIED' if self.observed_transport else 'TESTED_WITH_FIXTURES'
                            self.reason='validated_subscribed_L2_not_full_market_or_L3'
                            attempt=0
                        if self.adapter.state not in ('LIVE','CANDIDATE_READY') and self.clock()>deadline:
                            raise ProviderError('snapshot_deadline')
                        if self.adapter.status(self.clock())['state']=='STALE':
                            self.state='STALE';raise ProviderError('depth_freshness_deadline')
                        self.pending=True
                        raw=await asyncio.wait_for(anext(stream),timeout=10)
                finally:
                    # Invalidate before fallible/awaiting close; no trusted publication window.
                    if epoch==self.epoch:
                        self.state,self.reason='RESYNCING','stream_ended_snapshot_required'
                        if self.capture is not None:await self.capture.abort('source_interrupted')
                    # Explicit generator closure closes socket even on parsing/native rejection.
                    if hasattr(stream,'aclose'):await stream.aclose()
                return
            except asyncio.CancelledError:
                raise
            except Exception as error:
                # Do not publish exception text: it may contain provider payload or URLs.
                self.failures+=1
                self.reason=error.code if isinstance(error,ProviderError) else 'provider_transport_or_integrity_failure'
                terminal=isinstance(error,ProviderError) and error.code=='session_record_budget'
                self.state='ERROR' if terminal else 'RESYNCING'
                if self.adapter:self.adapter.disconnected()
                self.received_at_ns=self.exchange_ns=None
                if terminal:return
            finally:self.pending=False
            if epoch!=self.epoch or self.stop_event.is_set():break
            self.reconnects+=1
            delay=min(30.0,2.0**min(attempt,5));attempt=min(attempt+1,5)
            await self.sleep(delay*self.jitter(.8,1.2))

    def view(self):
        now=self.clock()
        trusted=self.state in ('LIVE_VERIFIED','TESTED_WITH_FIXTURES')
        if trusted:
            status=self.adapter.status(now)
            if status['state'] not in ('LIVE','CANDIDATE_READY'):
                self.state='STALE' if status['state']=='STALE' else 'RESYNCING'
                self.reason=status['reason'];trusted=False
        native=gig._checked(self.aggregate.state()) if trusted else None
        origin=('LIVE_OBSERVED' if self.observed_transport else 'HISTORICAL_SYNTHETIC') if native else 'UNAVAILABLE'
        metrics={name:None for name in ('spread','midprice','microprice','imbalance','bid_depth','ask_depth')}
        if native:
            for target,source in [('spread','spread'),('midprice','midpoint'),('microprice','microprice'),('imbalance','depth_imbalance'),('bid_depth','bid_depth'),('ask_depth','ask_depth')]:
                metrics[target]=native['metrics'][source]
        research={'status':'UNAVAILABLE','reason':'untrusted_or_stale_source'}
        if native:
            if self.research_cache is None or now>=self.research_cache_until:
                self.research_cache=self.research.view(now)
                self.research_cache['methodology']['depth_scope']='top '+str(self.depth)+' displayed levels per side;native depth totals may cover more admitted levels'
                self.research_cache_until=now+250_000_000
            from copy import deepcopy
            research=deepcopy(self.research_cache)
        age=None if not self.adapter or self.adapter.last_book_receive_ns is None else str(max(0,now-self.adapter.last_book_receive_ns))
        return {'origin':origin,'instrument':self.symbol,'source_instrument':self.symbol if self.provider=='kraken' else self.symbol.replace('/','-'),'provider':self.provider,'venue':'Kraken' if self.provider=='kraken' else 'Coinbase Exchange',
            'feed_type':'L2_AGGREGATE','price_scale':str(self.price_scale),'quantity_scale':str(self.quantity_scale),
            'book':{'bids':native['bids'][:self.depth] if native else [],'asks':native['asks'][:self.depth] if native else []},
            'revision':native['revision'] if native else '0','metrics':metrics,'source_timestamp_ns':self.exchange_ns,
            'received_at_ns':self.received_at_ns,'position':0,'event_count':0,'playing':False,
            'feed':{'state':self.state,'reason':self.reason,'real_time':bool(native and self.observed_transport),
                'sequence_complete':False,'capture_complete':False,'stale':not trusted,'data_age_ns':age,
                'reconnections':self.reconnects,'messages':self.messages,'failures':self.failures,
                'depth':self.depth,'native_depth_counts':{s:len(native[s]) if native else 0 for s in ('bids','asks')},'last_kind':self.kind,'pending_receive':self.pending,
                'snapshots':self.adapter.snapshots if self.adapter else 0,
                'updates':self.adapter.updates if self.adapter else 0,
                'trade_window_count':len(self.adapter.trades) if trusted else 0,
                'integrity':'candidate_CRC32_scoped_no_exchange_sequence' if self.provider=='kraken' else 'ordered_capture_no_documented_L2_sequence_or_checksum_proof','protocol_review':'operator_attested' if self.permission else 'unverified'},
            'native_core_status':({'scope':self.provider+'_L2','initialized':native['initialized'],'revision':native['revision'],'sequence':native['sequence'],'pmr_live_bytes':native['pmr_live_bytes'],'pmr_peak_bytes':native['pmr_peak_bytes']} if native else {'scope':self.provider+'_L2','published':False,'state':self.state}),
            'research':research,
            'recording':self.capture.status() if self.capture else {'state':'DISABLED'},
            'flow':{'trades':list(self.adapter.trades) if trusted else [],'classification':'provider_reported_side_not_inferred_cancellations'},
            'provenance':{'category':origin,'dataset':None,'complete_initialization':False,
                'initialization_scope':'subscribed aggregate L2 only','recording_enabled':self.capture is not None and self.capture.state=='RECORDING',
                'clock':'receive:monotonic_ns;wall:unix_ns;exchange:optional_RFC3339',
                'native_metrics_scope':'all admitted native levels;display is top '+str(self.depth),
                'profile':'provisional_kraken_v2' if self.provider=='kraken' else 'provisional_coinbase_exchange','permission':'operator_attested' if self.permission else 'unverified',
                'source_sequence':None,'session_segment':f'{self.provider}:{self.epoch}:{self.reconnects}',
                'session_segment_scope':'local_capture_boundary_not_exchange_session_or_sequence','redistribution_permitted':False},
            'capabilities':{'live':self.observed_transport and self.permission is not None,'aggregate_l2':True,
                'native_replay':True,'simulation':True,'recording':bool(self.observed_transport and self.provider=='kraken' and self.permission and self.permission.recording_approved and self.environment.get('GIG_LIVE_RECORDING_ENABLED')=='1'),'observed_lobster':False,
                'observed_itch':False,'order_ids':False,'fifo':False}}
