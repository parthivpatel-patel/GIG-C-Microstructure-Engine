"""Single-event-loop, bounded feed lifecycle; production endpoint is fixed.

Injected transports are synthetic-only regardless of their Permission assertions.
No provider credentials, arbitrary URLs, raw payload logging or automatic startup.
"""
import asyncio
from contextlib import suppress
import os
import random
import math
import time
import gig_microstructure as gig
from .kraken import (BOOK_SESSION_PROFILE, BOOK_DEPTH_SESSION_PROFILE, BOOK_LARGE_DEPTH_PROFILE,
                     LARGE_DEPTHS, KrakenBookAdapter, Permission, ProviderError, live_messages)

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
                 wall_clock=time.time_ns,sleep=asyncio.sleep,jitter=None,shutdown_seconds=3.):
        if type(shutdown_seconds)not in (int,float)or not math.isfinite(shutdown_seconds)or not .001<=shutdown_seconds<=5:raise ProviderError('shutdown_budget')
        self.command_lock=asyncio.Lock();self.retired=None;self.shutdown_seconds=shutdown_seconds;self.consecutive_failures=0;self.retry_budget=8
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
        self.subscribed_depth=10
        self.session_profile=None;self.coordinator=None;self.capture_token=None
        self.coordinated_receipt=None;self.joint_research_ready=False;self.joint_sources={};self.joint_book_ordinal=None

    def _configured_joint_depth(self, profile):
        token = self.environment.get('GIG_LIVE_KRAKEN_BOOK_DEPTH')
        if token is None:
            return 10
        if profile is None or token not in ('10', '25', '100', '500', '1000'):
            raise ProviderError('coordinator_depth_configuration')
        return int(token)

    def recording_writer_type(self):
        """Select a versioned writer before allocation; never reuse legacy receipts."""
        from terminal.l2_recording import L2Writer
        from terminal.kraken_joint_recording import JointL2Writer
        from .kraken_coordinator import PROFILE as JOINT_PROFILE
        profile=self.environment.get('GIG_LIVE_KRAKEN_SESSION_PROFILE')
        if self.provider!='kraken' or profile not in(None,JOINT_PROFILE):raise ProviderError('provider_recording_profile_unavailable')
        if self.session_profile != profile or self.subscribed_depth != self._configured_joint_depth(profile):
            raise ProviderError('provider_recording_profile_unavailable')
        return JointL2Writer if profile==JOINT_PROFILE else L2Writer

    def require_recording_profile(self,capture=None):
        from terminal.kraken_joint_recording import JointL2Writer
        joint=isinstance(getattr(capture,'writer',None),JointL2Writer)
        if self.session_profile is not None:
            from .kraken_coordinator import PROFILE as JOINT_PROFILE
            if self.session_profile!=JOINT_PROFILE or not joint or self.subscribed_depth != capture.writer.recording_depth:raise ProviderError('provider_recording_profile_unavailable')
        elif joint or self.environment.get('GIG_LIVE_KRAKEN_SESSION_PROFILE')is not None:
            raise ProviderError('provider_recording_profile_unavailable')

    def _new_book(self):
        if self.session_profile is not None:
            from .kraken_coordinator import KrakenSessionCoordinator
            if self.coordinator is None:
                if self.subscribed_depth in LARGE_DEPTHS:
                    book_profile = BOOK_LARGE_DEPTH_PROFILE
                elif self.subscribed_depth == 10:
                    book_profile = BOOK_SESSION_PROFILE
                else:
                    book_profile = BOOK_DEPTH_SESSION_PROFILE
                self.coordinator=KrakenSessionCoordinator(profile=self.session_profile,
                    depth=self.subscribed_depth,book_profile=book_profile,
                    native_capacity=max(256, 2 * self.subscribed_depth),
                    symbol=self.symbol,price_scale=self.price_scale,quantity_scale=self.quantity_scale,
                    origin='LIVE_OBSERVED' if self.observed_transport else 'HISTORICAL_SYNTHETIC')
            self.aggregate=None;self.adapter=self.coordinator._book
            self.capture_token=None;self.coordinated_receipt=None;self.joint_research_ready=False;self.joint_sources={};self.joint_book_ordinal=None
            self.exchange_ns=self.received_at_ns=None
            from terminal.l2_research import ResearchWindow
            self.research=ResearchWindow(aggressor_side_confirmed=self.environment.get('GIG_LIVE_AGGRESSOR_SIDE_REVIEWED')=='1')
            self.research_cache=None;self.research_cache_until=0
            return
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
        if old is not None:self.retired=old
        old=self.retired
        if old and not old.done():old.cancel()
        self.state,self.reason='DISCONNECTED','operator_disconnected'
        if self.coordinator:self.coordinator.disconnected()
        self.capture_token=None
        if self.adapter:self.adapter.disconnected()
        self.received_at_ns=self.exchange_ns=None
        return old

    async def close(self):
        async with self.command_lock:await self._close()

    async def _close(self):
        old=self.cancel();epoch=self.epoch
        if old:
            done,_=await asyncio.wait({old},timeout=self.shutdown_seconds)
            if not done:
                self.state,self.reason='ERROR','worker_shutdown_pending'
                raise ProviderError(self.reason)
            with suppress(asyncio.CancelledError,Exception):old.result()
            if self.retired is old:self.retired=None
        if self.capture is not None:await self.capture.stop()
        return epoch

    async def start(self,symbol='BTC/USD',*,provider='kraken'):
        async with self.command_lock:return await self._start(symbol,provider=provider)

    async def _start(self,symbol,*,provider):
        if symbol not in SYMBOLS or provider not in ('kraken','coinbase'):raise ProviderError('configuration')
        epoch=await self._close()
        if epoch!=self.epoch:raise ProviderError('control_command_superseded')
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
        from .kraken_coordinator import PROFILE as JOINT_PROFILE
        profile=self.environment.get('GIG_LIVE_KRAKEN_SESSION_PROFILE') if provider=='kraken' else None
        if profile not in(None,JOINT_PROFILE):
            self.state,self.reason='ERROR','coordinator_profile';raise ProviderError(self.reason)
        try:
            self.subscribed_depth = self._configured_joint_depth(profile) if provider == 'kraken' else 10
        except ProviderError as error:
            self.state, self.reason = 'ERROR', error.code
            raise
        self.session_profile=profile;self.coordinator=None;self.capture_token=None;self.coordinated_receipt=None;self.joint_sources={}
        if profile is not None:self.capture=None
        self.reconnects=self.messages=self.failures=self.consecutive_failures=0
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
                deadline=self.clock()+15_000_000_000;stable_since=None
                token=None;options={}
                if self.coordinator:
                    token=self.coordinator.connect(f'kraken:{epoch}:{self.reconnects}')
                    self.capture_token=token;self.adapter=self.coordinator._book
                    options['subscriptions']=self.coordinator.subscription_requests(token)
                    if self.subscribed_depth in LARGE_DEPTHS:
                        options['book_profile'] = BOOK_LARGE_DEPTH_PROFILE
                stream=self.transport(self.permission,stop=self.stop_event,symbol=self.symbol,**options)
                try:
                    async with asyncio.timeout(15):
                        # Includes connection establishment; subsequent receives each have a budget.
                        first=await anext(stream)
                    raw=first
                    while epoch==self.epoch and not self.stop_event.is_set():
                        self.pending=False
                        if self.messages>=1_000_000_000:raise ProviderError('session_record_budget')
                        now=self.clock();unix=str(self.wall_clock())
                        if self.coordinator:
                            receipt=self.coordinator.feed(raw,now,token=token)
                            self.coordinated_receipt=receipt
                            self.adapter=self.coordinator._book;self.aggregate=self.coordinator._native
                            joint=self.coordinator.view(now)
                            observed=receipt['source_receipt']
                            kind=observed['kind']
                            source_channel=('book' if kind in ('snapshot','update') else 'trade' if kind=='trades' else
                                ('book_subscription' if 'book_session_profile' in observed else 'trade_subscription') if kind=='acknowledgment' else kind)
                            self.joint_sources[source_channel]={key:receipt[key] for key in ('sha256','source_sha256','capture','local_generation','connection_id','receive_monotonic_ns','kind','origin')}
                            if joint['reconnect_required']:raise ProviderError('coordinated_session_reconnect_required')
                            if kind in ('snapshot','update'):
                                self.received_at_ns=unix;self.exchange_ns=observed.get('source_timestamp_ns')
                                self.joint_book_ordinal=self.messages+1
                            if joint['book_eligible']:
                                self.state='LIVE_VERIFIED' if self.observed_transport else 'TESTED_WITH_FIXTURES'
                                self.reason='provisional_joint_L2_and_trade_not_full_market_or_L3'
                            if not joint['book_eligible'] and now>deadline:raise ProviderError('snapshot_deadline')
                            seeded_research=False
                            if joint['book_eligible'] and not self.joint_research_ready:
                                # The initial book can arrive before the trade subscription
                                # becomes eligible. Seed from its admitted state and receive
                                # boundary, independent of the frame that unlocked the joint view.
                                native=joint['book']
                                baseline={side:native[side][:self.depth] for side in ('bids','asks')}
                                self.research.observe({'kind':'snapshot'},baseline,
                                                      self.adapter.last_book_receive_ns,self.joint_book_ordinal)
                                self.joint_research_ready=True
                                seeded_research=True
                        else:
                            seeded_research=False
                            receipt=self.adapter.feed(raw,now)
                            observed=receipt
                        if self.provider=='coinbase':
                            from .coinbase_transport import research_receipt
                            observed=research_receipt(receipt)
                        researchable=observed['kind'] in ('snapshot','update','trades')
                        if seeded_research and observed['kind'] in ('snapshot','update'):
                            researchable=False  # The same native state already seeded the window.
                        if researchable and (not self.coordinator or joint['book_eligible'] and self.joint_research_ready):
                            historical=observed.get('type')=='snapshot' if self.coordinator else getattr(self.adapter,'last_trade_snapshot',False)
                            research_event={**observed,'historical_snapshot':historical} if self.provider=='kraken' and observed['kind']=='trades' else observed
                            state=gig._checked(self.aggregate.state()) if observed['kind']!='trades' else None
                            if state is not None:state={**state,'bids':state['bids'][:self.depth],'asks':state['asks'][:self.depth]}
                            self.research.observe(research_event,state,now,self.messages+1)
                        if self.capture is not None and self.capture.state in ('RECORDING','FINALIZING'):
                            self.require_recording_profile(self.capture)
                            self.capture.offer(raw,now,unix,receipt)
                        self.messages+=1;self.kind=receipt['kind']
                        if self.messages%64==0:await asyncio.sleep(0)
                        if receipt['kind'] in ('snapshot','update') and (not self.coordinator or joint['book_eligible']):
                            self.received_at_ns=unix
                            self.exchange_ns=(observed if self.coordinator else receipt).get('source_timestamp_ns')
                            self.state='LIVE_VERIFIED' if self.observed_transport else 'TESTED_WITH_FIXTURES'
                            self.reason='provisional_joint_L2_and_trade_not_full_market_or_L3' if self.coordinator else 'validated_subscribed_L2_not_full_market_or_L3'
                            if stable_since is None:stable_since=now
                            elif now-stable_since>=30_000_000_000:attempt=0;self.consecutive_failures=0
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
                        if self.coordinator:self.coordinator.disconnected()
                        self.capture_token=None
                        if self.capture is not None:await self.capture.abort('source_interrupted')
                    # Explicit generator closure closes socket even on parsing/native rejection.
                    if hasattr(stream,'aclose'):await stream.aclose()
                return
            except asyncio.CancelledError:
                raise
            except Exception as error:
                # Do not publish exception text: it may contain provider payload or URLs.
                if epoch!=self.epoch:return
                self.failures+=1;self.consecutive_failures+=1
                self.reason=error.code if isinstance(error,ProviderError) else 'provider_transport_or_integrity_failure'
                terminal=isinstance(error,ProviderError) and error.code=='session_record_budget'
                self.state='ERROR' if terminal else 'RESYNCING'
                if self.adapter:self.adapter.disconnected()
                self.received_at_ns=self.exchange_ns=None
                if terminal:return
                if self.consecutive_failures>=self.retry_budget:
                    self.state,self.reason='ERROR','retry_budget_exhausted';return
            finally:self.pending=False
            if epoch!=self.epoch or self.stop_event.is_set():break
            self.reconnects+=1
            delay=min(30.0,2.0**min(attempt,5));attempt=min(attempt+1,5)
            jitter=self.jitter(.8,1.2)
            if type(jitter)not in (int,float)or not math.isfinite(jitter)or not .8<=jitter<=1.2:
                self.state,self.reason='ERROR','invalid_retry_jitter';return
            await self.sleep(delay*jitter)

    def view(self):
        now=self.clock()
        trusted=self.state in ('LIVE_VERIFIED','TESTED_WITH_FIXTURES')
        joint=None
        if self.coordinator:
            try:joint=self.coordinator.view(now)
            except ProviderError as error:
                self.state,self.reason='ERROR',error.code;trusted=False
            if joint is not None and not joint['book_eligible']:
                if trusted:
                    self.state='STALE' if joint['reason']=='coordinator_book_stale' else 'RESYNCING'
                    self.reason=joint['reason']
                trusted=False
        elif trusted:
            status=self.adapter.status(now)
            if status['state'] not in ('LIVE','CANDIDATE_READY'):
                self.state='STALE' if status['state']=='STALE' else 'RESYNCING'
                self.reason=status['reason'];trusted=False
        native=(joint['book'] if self.coordinator else gig._checked(self.aggregate.state())) if trusted else None
        origin=('LIVE_OBSERVED' if self.observed_transport else 'HISTORICAL_SYNTHETIC') if native else 'UNAVAILABLE'
        metrics={name:None for name in ('spread','midprice','microprice','imbalance','bid_depth','ask_depth')}
        if native:
            for target,source in [('spread','spread'),('midprice','midpoint'),('microprice','microprice'),('imbalance','depth_imbalance'),('bid_depth','bid_depth'),('ask_depth','ask_depth')]:
                metrics[target]=native['metrics'][source]
        research={'status':'UNAVAILABLE','reason':'untrusted_or_stale_source'}
        if native and self.coordinator and not self.joint_research_ready:
            research['reason']='awaiting_jointly_eligible_book_snapshot'
        if native and (not self.coordinator or self.joint_research_ready):
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
                'reconnections':self.reconnects,'messages':self.messages,'failures':self.failures,'consecutive_failures':self.consecutive_failures,'retry_budget':self.retry_budget,'retry_reset_after_stable_seconds':30,'retired_worker_pending':bool(self.retired and not self.retired.done()),
                'depth':self.depth,'native_depth_counts':{s:len(native[s]) if native else 0 for s in ('bids','asks')},'last_kind':self.kind,'pending_receive':self.pending,
                'snapshots':self.adapter.snapshots if self.adapter else 0,
                'updates':self.adapter.updates if self.adapter else 0,
                'trade_window_count':len(self.coordinator._public.trades if self.coordinator else self.adapter.trades) if trusted else 0,
                'joint_session':None if joint is None else {key:value for key,value in joint.items() if key!='book'},
                'integrity':'candidate_CRC32_scoped_no_exchange_sequence' if self.provider=='kraken' else 'ordered_capture_no_documented_L2_sequence_or_checksum_proof','protocol_review':'operator_attested' if self.permission else 'unverified'},
            'native_core_status':({'scope':self.provider+'_L2','initialized':native['initialized'],'revision':native['revision'],'sequence':native['sequence'],'pmr_live_bytes':native['pmr_live_bytes'],'pmr_peak_bytes':native['pmr_peak_bytes']} if native else {'scope':self.provider+'_L2','published':False,'state':self.state}),
            'research':research,
            'recording':self.capture.status() if self.capture else {'state':'DISABLED'},
            'flow':{'trades':([dict(t) for t in self.coordinator._public.trades] if self.coordinator else list(self.adapter.trades)) if trusted else [],'classification':'provider_reported_side_not_inferred_cancellations'},
            'provenance':{'category':origin,'dataset':None,'complete_initialization':False,
                'initialization_scope':'subscribed aggregate L2 only','recording_enabled':self.capture is not None and self.capture.state=='RECORDING',
                'clock':'receive:monotonic_ns;wall:unix_ns;exchange:optional_RFC3339',
                'native_metrics_scope':'all admitted native levels;display is top '+str(self.depth),
                'profile':self.session_profile or ('provisional_kraken_v2' if self.provider=='kraken' else 'provisional_coinbase_exchange'),'permission':'operator_attested' if self.permission else 'unverified',
                'joint_source_receipts':{key:dict(value) for key,value in self.joint_sources.items()},
                'source_sequence':None,'session_segment':f'{self.provider}:{self.epoch}:{self.reconnects}',
                'session_segment_scope':'local_capture_boundary_not_exchange_session_or_sequence','redistribution_permitted':False},
            'capabilities':{'live':self.observed_transport and self.permission is not None,'aggregate_l2':True,
                'native_replay':True,'simulation':True,'recording':bool(self.subscribed_depth == 10 and self.observed_transport and self.provider=='kraken' and self.permission and self.permission.recording_approved and self.environment.get('GIG_LIVE_RECORDING_ENABLED')=='1'),'observed_lobster':False,
                'observed_itch':False,'order_ids':False,'fifo':False}}
