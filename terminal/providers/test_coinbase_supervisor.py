"""Independent two-provider native integration and recovery. Every source frame is authored."""
import asyncio,json,unittest
import gig_microstructure as gig
from copy import deepcopy
from unittest.mock import patch
from .supervisor import FeedSupervisor
from .test_supervisor import ENV
from .test_coinbase_candidate import SNAP,UPDATE
from .test_kraken import book
from .kraken import Permission,ProviderError
from .coinbase_transport import research_receipt,live_messages

CB={k.replace('GIG_LIVE_','GIG_COINBASE_'):v for k,v in ENV.items()}

class SupervisedCoinbase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):self.feeds=[]
    async def asyncTearDown(self):
        for feed in self.feeds:await feed.close()
    async def settle(self,predicate):
        for _ in range(200):
            if predicate():return
            await asyncio.sleep(.002)
        self.fail('authored state did not settle')
    def feed(self,source,**kwargs):
        f=FeedSupervisor(environment={**ENV,**CB},transport=source,**kwargs);self.feeds.append(f);return f
    async def test_coinbase_separate_gates_prevent_any_connection(self):
        async def source(*args,**kwargs):self.fail('must not connect');yield ''
        f=self.feed(source);f.environment=ENV
        with self.assertRaises(ProviderError):await f.start(provider='coinbase')
        self.assertIsNone(f.task);self.assertEqual(f.view()['provider'],'coinbase');self.assertEqual(f.view()['book']['bids'],[])
    async def test_native_snapshot_update_trade_and_venue_scope(self):
        release=asyncio.Event()
        async def source(*args,**kwargs):
            yield json.dumps(SNAP);yield json.dumps(UPDATE)
            yield json.dumps({'type':'match','product_id':'BTC-USD','side':'sell','trade_id':1,'price':'101','size':'1','time':'2026-01-01T00:00:00Z'})
            await release.wait()
        f=self.feed(source);await f.start(provider='coinbase');await self.settle(lambda:f.messages==3)
        r=f.view();self.assertEqual(r['provider'],'coinbase');self.assertEqual(r['venue'],'Coinbase Exchange')
        self.assertEqual(r['origin'],'HISTORICAL_SYNTHETIC');self.assertFalse(r['feed']['real_time'])
        self.assertEqual(r['book']['bids'][0]['quantity'],'400000000');self.assertEqual(r['source_instrument'],'BTC-USD')
        self.assertEqual(r['flow']['trades'][0]['reported_side_role'],'maker_candidate_unverified')
        self.assertIsNone(r['research']['metrics']['effective_spread']['value'])
    async def test_venue_switch_replaces_native_state_and_source_segment(self):
        async def source(*args,**kwargs):
            yield book() if f.provider=='kraken' else json.dumps(SNAP)
            await asyncio.Event().wait()
        f=self.feed(source);await f.start();await self.settle(lambda:f.messages==1);old=f.view()['provenance']['session_segment']
        await f.start('ETH/USD',provider='coinbase')
        # The BTC-authored snapshot cannot contaminate an ETH-selected native book.
        await self.settle(lambda:f.failures>0)
        self.assertEqual(f.view()['book']['bids'],[]);self.assertNotEqual(f.view()['provenance']['session_segment'],old)
    async def test_disconnect_requires_new_snapshot_no_update_only_recovery(self):
        resume=asyncio.Event();attempts=[]
        async def sleep(_):await resume.wait()
        async def source(*args,**kwargs):
            attempts.append(1)
            if len(attempts)==1:yield json.dumps(SNAP);return
            if len(attempts)==2:yield json.dumps(UPDATE);return
            yield json.dumps(SNAP);await asyncio.Event().wait()
        f=self.feed(source,sleep=sleep);await f.start(provider='coinbase')
        await self.settle(lambda:f.reconnects==1);self.assertEqual(f.view()['book']['bids'],[])
        resume.set();await self.settle(lambda:len(attempts)>=3 and f.messages==2)
        self.assertEqual(f.view()['book']['bids'][0]['quantity'],'200000000')
    async def test_session_budget_stops_before_another_native_mutation(self):
        release=asyncio.Event()
        async def source(*args,**kwargs):
            yield json.dumps(SNAP);await release.wait();yield json.dumps(UPDATE)
            await asyncio.Event().wait()
        f=self.feed(source);await f.start(provider='coinbase');await self.settle(lambda:f.messages==1)
        f.messages=1_000_000_000;release.set();await self.settle(lambda:f.failures>0)
        self.assertEqual(f.state,'ERROR');self.assertTrue(f.task.done())
        self.assertEqual(f.messages,1_000_000_000)
        self.assertEqual(gig._checked(f.aggregate.state())['revision'],'1')
    async def test_full_bounded_native_depth_is_not_truncated_to_display(self):
        p=deepcopy(SNAP);p['bids']=[[str(100-i),'1'] for i in range(20)]
        async def source(*args,**kwargs):yield json.dumps(p);await asyncio.Event().wait()
        f=self.feed(source);await f.start(provider='coinbase');await self.settle(lambda:f.messages==1)
        r=f.view();self.assertEqual(len(r['book']['bids']),10);self.assertEqual(r['feed']['native_depth_counts']['bids'],20)
        self.assertIn('top 10',r['research']['methodology']['depth_scope'])
    async def test_fixture_research_cannot_leak_into_terminal_live_mode(self):
        from terminal.server.engine import NativeSession
        async def source(*args,**kwargs):yield json.dumps(SNAP);await asyncio.Event().wait()
        f=self.feed(source);await f.start(provider='coinbase');await self.settle(lambda:f.messages==1)
        n=NativeSession();n.live_feed=f;n.mode='LIVE';r=n.state()
        self.assertEqual(r['origin'],'UNAVAILABLE');self.assertEqual(r['research']['status'],'UNAVAILABLE')
    async def test_transport_fixed_endpoint_limits_resubscribe_and_close(self):
        calls=[];sent=[];stop=asyncio.Event()
        class Connector:
            def __init__(self,*args,**kwargs):calls.append((args,kwargs));calls.append(self)
            async def __aenter__(self):return self
            async def __aexit__(self,*args):calls.append('closed')
            async def send(self,value):sent.append(json.loads(value))
            async def recv(self):return '{"type":"heartbeat","product_id":"ETH-USD"}'
        with patch('websockets.asyncio.client.connect',Connector):
            stream=live_messages(Permission(True,True,True,False,'authored'),stop=stop,symbol='ETH/USD')
            await anext(stream);error=ValueError('redirect');self.assertIs(calls[1].process_redirect(error),error)
            await stream.aclose()
        self.assertEqual(calls[0][0],('wss://ws-feed.exchange.coinbase.com/',));self.assertEqual(calls[0][1]['max_queue'],4)
        self.assertEqual(sent,[{'type':'subscribe','product_ids':['ETH-USD'],'channels':['level2','matches','heartbeat']}]);self.assertEqual(calls[-1],'closed')
    async def test_permission_failure_before_transport_and_unreviewed_trade_side(self):
        with patch('websockets.asyncio.client.connect') as connect:
            stream=live_messages(Permission(),stop=asyncio.Event())
            with self.assertRaises(ProviderError):await anext(stream)
            connect.assert_not_called()
        raw={'kind':'trade','duplicate':False,'trade':{'trade_id':'1','price_ticks':'100','quantity':'1','reported_side':'sell','reported_side_role':'maker_candidate_unverified','source_timestamp_ns':'1','origin':'HISTORICAL_SYNTHETIC'}}
        result=research_receipt(raw);self.assertEqual(result['trades'][0]['side'],'sell');self.assertIsNone(result['trades'][0]['aggressor_side'])

if __name__=='__main__':unittest.main()
