"""Actual supervisor/native/product path with authored frames; no sockets or app."""
import asyncio
import copy
import hashlib
import json
import unittest
from unittest.mock import patch

import gig_microstructure as gig
from .kraken import Permission, ProviderError, live_messages, transport_subscriptions
from .kraken_coordinator import PROFILE
from .supervisor import FeedSupervisor
from .test_supervisor import ENV
from .test_kraken_depth_session import wire
from .test_kraken_public_session import raw, status, trade, trades


def acknowledgment(request):
    params=request['params']
    result={'channel':params['channel'],'symbol':params['symbol'][0],'snapshot':params['snapshot']}
    if params['channel']=='book':result['depth']=params['depth']
    return raw({'method':'subscribe','success':True,'req_id':request['req_id'],'result':result})


class SupervisedJoint(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):self.feeds=[]
    async def asyncTearDown(self):
        for feed in self.feeds:await feed.close()
    def feed(self,transport,**kwargs):
        environment={**ENV,'GIG_LIVE_KRAKEN_SESSION_PROFILE':PROFILE}
        feed=FeedSupervisor(environment=environment,transport=transport,**kwargs)
        self.feeds.append(feed);return feed
    async def settle(self,predicate):
        for _ in range(150):
            if predicate():return
            await asyncio.sleep(.001)
        self.fail('authored bounded joint lifecycle did not settle')
    def source(self,frames=None):
        queue=asyncio.Queue();requests=[]
        async def transport(permission,*,stop,symbol,subscriptions):
            requests.append(copy.deepcopy(subscriptions))
            for frame in [raw(status()),*[acknowledgment(r) for r in subscriptions],
                          wire([('100','2')],[('101','1')])]:yield frame
            for frame in frames or []:yield frame
            while True:yield await queue.get()
        return transport,queue,requests
    async def ready(self,**kwargs):
        transport,queue,requests=self.source()
        feed=self.feed(transport,**kwargs);await feed.start()
        await self.settle(lambda:feed.messages==4)
        return feed,queue,requests

    async def test_joint_raw_frames_reach_actual_native_book_and_product_metrics(self):
        feed,queue,requests=await self.ready()
        view=feed.view();native=gig._checked(feed.aggregate.state())
        self.assertIs(feed.aggregate,feed.coordinator._native)
        self.assertEqual(native['revision'],'1')
        self.assertEqual(view['book']['bids'],native['bids'])
        self.assertEqual(view['metrics']['midprice'],{'numerator':'10050000000','denominator':'1'})
        self.assertEqual(view['origin'],'HISTORICAL_SYNTHETIC')
        self.assertFalse(view['feed']['real_time']);self.assertFalse(view['feed']['sequence_complete'])
        self.assertEqual(view['provenance']['profile'],PROFILE)
        joint=view['feed']['joint_session']
        self.assertTrue(joint['book_eligible']);self.assertEqual(joint['connection_id'],'42')
        self.assertNotIn('book',joint);self.assertFalse(joint['full_protocol_qualified'])
        self.assertFalse(joint['independent_source_authentication'])
        sources=view['provenance']['joint_source_receipts']
        self.assertEqual(set(sources),{'status','book_subscription','trade_subscription','book'})
        snapshot=wire([('100','2')],[('101','1')])
        self.assertEqual(sources['book']['source_sha256'],hashlib.sha256(snapshot.encode()).hexdigest())
        self.assertEqual(joint['native_book_source_sha256'],sources['book']['source_sha256'])
        self.assertEqual([r['req_id'] for r in requests[0]],[101,201])
        self.assertEqual(sources['book']['capture'],feed.capture_token.capture)
        sources['book']['source_sha256']='tampered'
        self.assertNotEqual(feed.view()['provenance']['joint_source_receipts']['book']['source_sha256'],'tampered')

    async def test_trade_flow_and_research_consume_joint_receipts_without_mutating_l2(self):
        feed,queue,_=await self.ready()
        book_received_at=feed.view()['received_at_ns']
        body=raw(trades(trade(price=100)));await queue.put(body)
        await self.settle(lambda:feed.messages==5)
        view=feed.view()
        self.assertEqual(view['flow']['trades'][0]['price_ticks'],'10000000000')
        self.assertEqual(view['feed']['trade_window_count'],1)
        self.assertEqual(view['revision'],'1')
        self.assertEqual(view['received_at_ns'],book_received_at)
        self.assertEqual(len(feed.research.trades),1)
        self.assertEqual(view['provenance']['joint_source_receipts']['trade']['source_sha256'],hashlib.sha256(body.encode()).hexdigest())
        self.assertNotEqual(view['provenance']['joint_source_receipts']['trade']['source_sha256'],view['feed']['joint_session']['native_book_source_sha256'])
        view['flow']['trades'][0]['price_ticks']='tampered'
        self.assertEqual(feed.view()['flow']['trades'][0]['price_ticks'],'10000000000')
        await queue.put(body);await self.settle(lambda:feed.messages==6)
        self.assertEqual(len(feed.view()['flow']['trades']),1)
        self.assertEqual(len(feed.research.trades),1)

    async def test_book_before_trade_ack_cannot_publish_until_both_subscriptions_bind(self):
        release=asyncio.Event()
        async def transport(permission,*,stop,symbol,subscriptions):
            yield raw(status());yield acknowledgment(subscriptions[0])
            yield wire([('100','2')],[('101','1')]);await release.wait()
            yield acknowledgment(subscriptions[1]);await asyncio.Event().wait()
        feed=self.feed(transport);await feed.start();await self.settle(lambda:feed.messages==3)
        self.assertEqual(feed.view()['origin'],'UNAVAILABLE')
        self.assertEqual(feed.view()['book']['bids'],[])
        release.set();await self.settle(lambda:feed.messages==4)
        view=feed.view();self.assertEqual(view['book']['bids'][0]['quantity'],'200000000')
        self.assertIsNotNone(view['metrics']['midprice'])
        self.assertFalse(feed.joint_research_ready)
        self.assertEqual(view['research']['status'],'UNAVAILABLE')

    async def test_staleness_fences_book_flow_and_research_before_receive_timeout(self):
        clock=[1];feed,_,_=await self.ready(clock=lambda:clock[0])
        clock[0]=10_000_000_002;view=feed.view()
        self.assertEqual(view['feed']['state'],'STALE');self.assertEqual(view['book']['bids'],[])
        self.assertEqual(view['flow']['trades'],[]);self.assertIsNone(view['metrics']['midprice'])
        self.assertEqual(view['research']['status'],'UNAVAILABLE')
        self.assertTrue(view['feed']['joint_session']['reconnect_required'])

    async def test_status_halt_hides_native_before_awaiting_transport_close(self):
        closing=asyncio.Event();release=asyncio.Event()
        async def transport(permission,*,stop,symbol,subscriptions):
            try:
                for frame in [raw(status()),*[acknowledgment(r) for r in subscriptions],wire([('100','2')],[('101','1')]),raw(status('maintenance'))]:yield frame
            finally:closing.set();await release.wait()
        feed=self.feed(transport);await feed.start();await self.settle(closing.is_set)
        try:
            view=feed.view();self.assertEqual(view['book']['bids'],[])
            self.assertEqual(view['flow']['trades'],[]);self.assertIsNone(feed.capture_token)
            self.assertFalse(view['feed']['joint_session']['book_eligible'])
            self.assertEqual(view['provenance']['joint_source_receipts']['status']['source_sha256'],hashlib.sha256(raw(status('maintenance')).encode()).hexdigest())
        finally:release.set()

    async def test_bad_crc_conflicting_trade_and_source_mismatch_fence_actual_consumer(self):
        for frame in [wire([('100','3')],[('101','1')],checksum=0),
                      raw(trades(trade(symbol='ETH/USD'))),
                      raw(trades(trade(),trade(qty=2)))]:
            with self.subTest(frame=frame):
                feed,queue,_=await self.ready(sleep=lambda _:asyncio.Event().wait())
                await queue.put(frame);await self.settle(lambda:feed.failures==1)
                view=feed.view();self.assertEqual(view['origin'],'UNAVAILABLE')
                self.assertEqual(view['book']['bids'],[]);self.assertEqual(view['flow']['trades'],[])

    async def test_reconnect_binds_new_capture_generation_and_subscription_ids(self):
        calls=[];retry=asyncio.Event();next_snapshot=asyncio.Event();old=[]
        async def transport(permission,*,stop,symbol,subscriptions):
            calls.append(copy.deepcopy(subscriptions))
            if len(calls)==1:
                old.append(feed.capture_token)
                for frame in [raw(status()),*[acknowledgment(r) for r in subscriptions],wire([('100','2')],[('101','1')])]:yield frame
                raise OSError('private raw failure must not escape')
            yield raw(status(connection_id=43))
            for request in subscriptions:yield acknowledgment(request)
            await next_snapshot.wait();yield wire([('99','7')],[('102','1')])
            await asyncio.Event().wait()
        async def sleep(_):await retry.wait()
        feed=self.feed(transport,sleep=sleep,jitter=lambda a,b:1);await feed.start()
        await self.settle(lambda:feed.failures==1)
        self.assertEqual(feed.view()['book']['bids'],[]);retry.set()
        await self.settle(lambda:len(calls)==2 and feed.messages==7)
        self.assertEqual(feed.view()['book']['bids'],[])
        self.assertEqual([r['req_id'] for r in calls[1]],[102,203])
        self.assertNotEqual(old[0].capture,feed.capture_token.capture)
        self.assertEqual(feed.capture_token.generation,2)
        next_snapshot.set();await self.settle(lambda:feed.messages==8)
        view=feed.view();self.assertEqual(view['book']['bids'][0]['quantity'],'700000000')
        self.assertEqual(view['feed']['joint_session']['connection_id'],'43')
        self.assertEqual(view['revision'],'1');self.assertNotIn('private raw failure',str(view))
        with self.assertRaisesRegex(ProviderError,'capture_token'):
            feed.coordinator.feed(raw(status()),feed.clock(),token=old[0])
        self.assertEqual(feed.view()['book']['bids'],[])

    async def test_explicit_profile_and_existing_permission_gate_precede_transport(self):
        calls=[]
        async def transport(*args,**kwargs):calls.append(kwargs);yield ''
        for changes,reason in [({'GIG_LIVE_KRAKEN_SESSION_PROFILE':'future'},'coordinator_profile'),
                               ({'GIG_LIVE_ENABLED':'0'},'live_disabled'),
                               ({'GIG_LIVE_PRIVATE_DISPLAY_APPROVED':'0'},'permission')]:
            feed=self.feed(transport);feed.environment.update(changes)
            with self.assertRaisesRegex(ProviderError,reason):await feed.start()
            self.assertIsNone(feed.task)
        self.assertEqual(calls,[])

    async def test_recording_contract_is_explicitly_rejected_without_app_or_writer(self):
        feed,_,_=await self.ready()
        with self.assertRaisesRegex(ProviderError,'provider_recording_profile_unavailable'):feed.require_recording_profile()
        self.assertFalse(feed.view()['capabilities']['recording'])
        feed.session_profile=None
        with self.assertRaisesRegex(ProviderError,'provider_recording_profile_unavailable'):feed.require_recording_profile()
        feed.environment.pop('GIG_LIVE_KRAKEN_SESSION_PROFILE')
        self.assertIsNone(feed.require_recording_profile())
        feed.session_profile=PROFILE

    async def test_cancel_and_symbol_change_clear_old_native_and_public_trades(self):
        feed,queue,_=await self.ready();await queue.put(raw(trades(trade())))
        await self.settle(lambda:feed.messages==5)
        feed.cancel();self.assertEqual(feed.view()['book']['bids'],[])
        self.assertEqual(feed.view()['flow']['trades'],[]);self.assertIsNone(feed.capture_token)
        await feed.close()

    async def test_symbol_change_subscriptions_and_native_owner_cannot_retain_old_book(self):
        seen=[];release=asyncio.Event()
        async def transport(permission,*,stop,symbol,subscriptions):
            seen.append((symbol,copy.deepcopy(subscriptions)))
            yield raw(status());yield acknowledgment(subscriptions[0]);yield acknowledgment(subscriptions[1])
            if symbol=='ETH/USD':await release.wait()
            yield wire([('100','2')],[('101','1')]).replace('BTC/USD',symbol)
            await asyncio.Event().wait()
        feed=self.feed(transport);await feed.start();await self.settle(lambda:feed.messages==4)
        await feed.start('ETH/USD');await self.settle(lambda:feed.messages==3)
        view=feed.view();self.assertEqual(view['book']['bids'],[]);self.assertEqual(view['instrument'],'ETH/USD')
        self.assertTrue(all(r['params']['symbol']==['ETH/USD'] for r in seen[1][1]))
        self.assertEqual(view['flow']['trades'],[]);release.set()
        await self.settle(lambda:feed.messages==4)
        self.assertEqual(feed.view()['origin'],'HISTORICAL_SYNTHETIC')
        self.assertNotEqual(seen[0][0],seen[1][0])

    async def test_fixture_origin_stays_unavailable_in_actual_terminal_live_consumer(self):
        from terminal.server.engine import NativeSession
        feed,_,_=await self.ready()
        native=NativeSession();native.live_feed=feed;native.mode='LIVE'
        state=native.state()
        self.assertEqual(state['origin'],'UNAVAILABLE');self.assertEqual(state['book']['bids'],[])
        self.assertIsNone(state['metrics']['midprice']);self.assertEqual(state['flow']['trades'],[])
        self.assertNotIn('book',state['feed']['joint_session'])
        self.assertTrue(all(r['origin']=='HISTORICAL_SYNTHETIC' for r in state['provenance']['joint_source_receipts'].values()))
        self.assertFalse(state['diagnostics']['native_status']['published'])


class JointTransport(unittest.IsolatedAsyncioTestCase):
    async def test_actual_transport_sends_coordinator_subscriptions_without_socket(self):
        sent=[];calls=[];stop=asyncio.Event()
        class AuthoredSocket:
            def __init__(self,*args,**kwargs):calls.append((args,kwargs))
            async def __aenter__(self):return self
            async def __aexit__(self,*args):pass
            async def send(self,body):sent.append(json.loads(body))
            async def recv(self):return raw(status())
        from .kraken_coordinator import KrakenSessionCoordinator
        coordinator=KrakenSessionCoordinator(profile=PROFILE);token=coordinator.connect('authored')
        requests=coordinator.subscription_requests(token)
        with patch('websockets.asyncio.client.connect',AuthoredSocket):
            stream=live_messages(Permission(True,True,True,False,'authored'),stop=stop,subscriptions=requests)
            self.assertEqual(await anext(stream),raw(status()));await stream.aclose()
        self.assertEqual(sent,requests);self.assertEqual(calls[0][0],('wss://ws.kraken.com/v2',))

    async def test_malformed_subscriptions_rejected_before_client_creation(self):
        from .kraken_coordinator import KrakenSessionCoordinator
        coordinator=KrakenSessionCoordinator(profile=PROFILE);token=coordinator.connect('authored')
        requests=coordinator.subscription_requests(token)
        bad=[]
        for change in ('method','symbol','depth','request_id','same_id','snapshot','extra'):
            value=copy.deepcopy(requests)
            if change=='method':value[0]['method']='add_order'
            elif change=='symbol':value[0]['params']['symbol']=['ETH/USD']
            elif change=='depth':value[0]['params']['depth']=500
            elif change=='request_id':value[0]['req_id']=True
            elif change=='same_id':value[0]['req_id']=value[1]['req_id']
            elif change=='snapshot':value[1]['params']['snapshot']=1
            else:value[0]['params']['token']='not permitted'
            bad.append(value)
        for value in bad:
            with self.subTest(value=value),patch('websockets.asyncio.client.connect') as connect:
                stream=live_messages(Permission(True,True,True,False,'authored'),stop=asyncio.Event(),subscriptions=value)
                with self.assertRaisesRegex(ProviderError,'transport_subscriptions'):await anext(stream)
                connect.assert_not_called()
        legacy=transport_subscriptions('BTC/USD')
        self.assertTrue(all('req_id' not in request for request in legacy))


if __name__=='__main__':unittest.main()
