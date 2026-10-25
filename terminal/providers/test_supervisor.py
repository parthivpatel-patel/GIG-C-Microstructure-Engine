"""Independent transport orchestration fixtures: no exchange or external network."""
import asyncio
import unittest
from .supervisor import FeedSupervisor,configured_permission
from .kraken import ProviderError
from .test_kraken import book

ENV={'GIG_LIVE_ENABLED':'1','GIG_LIVE_PROTOCOL_REVIEWED':'1',
     'GIG_LIVE_PRIVATE_DISPLAY_APPROVED':'1','GIG_LIVE_CLOUD_PROCESSING_APPROVED':'1',
     'GIG_LIVE_PERMISSION_REFERENCE':'authored-test-not-a-real-license'}

class Supervisor(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):self.feeds=[]
    async def asyncTearDown(self):
        for feed in self.feeds:await feed.close()
    def feed(self,transport,**kwargs):
        feed=FeedSupervisor(environment=ENV,transport=transport,**kwargs);self.feeds.append(feed);return feed
    async def settle(self,predicate):
        for _ in range(100):
            if predicate():return
            await asyncio.sleep(.001)
        self.fail('bounded authored lifecycle did not settle')
    async def test_disabled_never_calls_transport(self):
        calls=[]
        async def source(*args,**kwargs):calls.append(1);yield book()
        feed=self.feed(source);feed.environment={}
        with self.assertRaisesRegex(ProviderError,'live_disabled'):await feed.start()
        self.assertEqual(calls,[]);self.assertIsNone(feed.task);self.assertEqual(feed.view()['book']['bids'],[])
    async def test_incomplete_permission_never_connects(self):
        async def source(*args,**kwargs):self.fail('must not connect');yield ''
        feed=self.feed(source);feed.environment={'GIG_LIVE_ENABLED':'1'}
        with self.assertRaisesRegex(ProviderError,'permission'):await feed.start()
        self.assertIsNone(feed.task)
    async def test_fixture_native_book_is_not_observed(self):
        hold=asyncio.Event()
        async def source(*args,**kwargs):yield book();await hold.wait()
        feed=self.feed(source);await feed.start();await self.settle(lambda:feed.messages==1)
        view=feed.view();self.assertEqual(view['origin'],'HISTORICAL_SYNTHETIC')
        self.assertEqual(view['feed']['state'],'TESTED_WITH_FIXTURES')
        self.assertFalse(view['feed']['real_time']);self.assertEqual(view['book']['bids'][0]['price_ticks'],'10000000000')
        self.assertEqual(view['metrics']['midprice'],{'numerator':'10050000000','denominator':'1'})
        await feed.close();self.assertEqual(feed.view()['book']['bids'],[])
    async def test_disconnect_during_snapshot_has_no_trusted_book(self):
        closed=asyncio.Event()
        async def source(*args,**kwargs):
            try:await asyncio.Event().wait();yield ''
            finally:closed.set()
        feed=self.feed(source);await feed.start();await asyncio.sleep(.005);await feed.close()
        self.assertTrue(closed.is_set());self.assertEqual(feed.view()['origin'],'UNAVAILABLE')
        self.assertEqual(feed.view()['feed']['state'],'DISCONNECTED')
    async def test_corruption_reconnect_requires_fresh_snapshot(self):
        attempts=[];resume=asyncio.Event();delays=[]
        async def sleep(delay):delays.append(delay);await resume.wait()
        async def source(*args,**kwargs):
            attempts.append(1)
            if len(attempts)==1:yield book();yield book(checksum=123)
            else:yield book([('99','1')],[('102','1')]);await asyncio.Event().wait()
        feed=self.feed(source,sleep=sleep,jitter=lambda a,b:1)
        await feed.start();await self.settle(lambda:len(delays)==1)
        self.assertEqual(feed.view()['book']['bids'],[]);self.assertEqual(feed.state,'RESYNCING')
        resume.set();await self.settle(lambda:feed.messages==2)
        self.assertEqual(feed.reconnects,1);self.assertEqual(delays,[1])
        self.assertEqual(feed.view()['book']['bids'][0]['price_ticks'],'9900000000')
    async def test_failure_hidden_before_asynchronous_socket_close(self):
        closing=asyncio.Event();release=asyncio.Event()
        async def source(*args,**kwargs):
            try:yield book();yield book(checksum=123)
            finally:closing.set();await release.wait()
        feed=self.feed(source);await feed.start()
        await self.settle(closing.is_set)
        try:
            view=feed.view()
            self.assertEqual(view['book']['bids'],[])
            self.assertNotEqual(view['feed']['state'],'TESTED_WITH_FIXTURES')
        finally:release.set()

    async def test_stale_depth_hidden_even_before_receive_timeout(self):
        clock=[1]
        async def source(*args,**kwargs):yield book();await asyncio.Event().wait()
        feed=self.feed(source,clock=lambda:clock[0]);await feed.start();await self.settle(lambda:feed.messages==1)
        clock[0]=10_000_000_002
        view=feed.view();self.assertEqual(view['feed']['state'],'STALE');self.assertEqual(view['book']['bids'],[])
        self.assertIsNone(view['metrics']['microprice'])
    async def test_mode_switch_cancels_old_symbol_before_new_state(self):
        seen=[]
        async def source(permission,*,stop,symbol):
            seen.append(symbol);yield book().replace('BTC/USD',symbol);await asyncio.Event().wait()
        feed=self.feed(source);await feed.start();await self.settle(lambda:feed.messages==1)
        await feed.start('ETH/USD');await self.settle(lambda:feed.messages==1)
        self.assertEqual(seen,['BTC/USD','ETH/USD']);self.assertEqual(feed.view()['instrument'],'ETH/USD')
    async def test_jitter_backoff_bounded_and_payload_not_in_error(self):
        delays=[]
        async def sleep(delay):delays.append(delay);await asyncio.sleep(0)
        async def source(*args,**kwargs):raise RuntimeError('PRIVATE_PAYLOAD');yield ''
        feed=self.feed(source,sleep=sleep,jitter=lambda a,b:b);await feed.start()
        await self.settle(lambda:len(delays)>=7);await feed.close()
        self.assertEqual(delays[:6],[1.2,2.4,4.8,9.6,19.2,36.0])
        self.assertNotIn('PRIVATE_PAYLOAD',str(feed.view()))
    async def test_unknown_symbols_and_urls_fail_before_start(self):
        async def source(*args,**kwargs):self.fail('must not connect');yield ''
        feed=self.feed(source)
        for symbol in ('BTC/EUR','https://attacker.invalid',None):
            with self.assertRaises(ProviderError):await feed.start(symbol)
        self.assertIsNone(feed.task)
    def test_permission_reference_bounded_no_control_characters(self):
        for value in ('x'*257,'a\nb'):
            with self.assertRaises(ProviderError):configured_permission({'GIG_LIVE_PERMISSION_REFERENCE':value})

if __name__=='__main__':unittest.main()
