"""Bounded offline queue/worker/endurance controls;no external provider traffic."""
import asyncio
import json
import threading
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from terminal.server.analysis import AnalysisGate
from terminal.server.market_events import MarketEvents
from terminal.stocks.test_final import client,ready,packet,quote


class Workers(unittest.IsolatedAsyncioTestCase):
    async def test_cancellation_reports_physical_worker_until_drain(self):
        gate=AnalysisGate();entered=threading.Event();release=threading.Event()
        def work():entered.set();assert release.wait(3);return 7
        task=asyncio.create_task(gate.run(work));closing=None
        try:
            self.assertTrue(await asyncio.to_thread(entered.wait,1))
            self.assertEqual(gate.status()['physical_active_workers'],1)
            task.cancel();await asyncio.gather(task,return_exceptions=True)
            for _ in range(100):
                with self.assertRaisesRegex(ValueError,'analysis_busy'):await gate.run(lambda:0)
            self.assertEqual(gate.status()['busy_rejections'],100)
            self.assertEqual(gate.status()['canceled_waiters'],1)
            closing=asyncio.create_task(gate.close());await asyncio.sleep(.001)
            self.assertFalse(closing.done());self.assertEqual(gate.status()['application_queue_depth'],0)
        finally:
            release.set();await asyncio.gather(task,return_exceptions=True)
            if closing:await closing
            else:await gate.close()
        s=gate.status();self.assertEqual(s['physical_active_workers'],0)
        self.assertEqual((s['started'],s['completed'],s['peak_physical_workers']),(1,1,1))
        self.assertTrue(s['closed']);self.assertGreaterEqual(s['total_worker_wall_seconds'],0)

    async def test_repeated_success_and_failure_preserve_admission_budget(self):
        gate=AnalysisGate()
        def fail():raise ValueError('authored_failure')
        for _ in range(100):self.assertEqual(await gate.run(lambda:3),3)
        for _ in range(10):
            with self.assertRaisesRegex(ValueError,'authored_failure'):await gate.run(fail)
        await gate.close();s=gate.status()
        self.assertEqual((s['started'],s['completed'],s['failed']),(110,110,10))
        self.assertEqual(s['peak_physical_workers'],1);self.assertEqual(s['physical_active_workers'],0)
        with self.assertRaisesRegex(ValueError,'analysis_closed'):await gate.run(lambda:0)


def source():
    return SimpleNamespace(receipts=0,generation=0,state='SIMULATED',phase='SUBSCRIBED',
                           duplicates=0,out_of_order=0,pending=None,view=lambda:{'history':[]})


class BrowserPush(unittest.IsolatedAsyncioTestCase):
    async def test_quiet_source_coalesces_checks_and_emits_heartbeat(self):
        hub=MarketEvents(source(),interval=.001,heartbeat=.02);frames=hub.frames()
        await anext(frames);await anext(frames)
        self.assertGreater(hub.coalesced,0);self.assertEqual(hub.sent,2)
        self.assertEqual(hub.status()['application_queue_depth'],0)
        hub.closed=True
        with self.assertRaises(StopAsyncIteration):await anext(frames)
        await frames.aclose()

    async def test_slow_reader_in_flight_bytes_and_cancellation_cleanup(self):
        hub=MarketEvents(source());response=hub.response();entered=asyncio.Event()
        async def send(message):
            if message.get('body'):
                entered.set();await asyncio.Event().wait()
        task=asyncio.create_task(response.stream_response(send))
        try:
            await asyncio.wait_for(entered.wait(),1)
            self.assertEqual(hub.status()['in_flight_sends'],1)
            self.assertGreater(hub.status()['in_flight_body_bytes'],0)
        finally:
            task.cancel();await asyncio.gather(task,return_exceptions=True)
            await response.body_iterator.aclose()
        self.assertEqual((hub.in_flight_sends,hub.in_flight_bytes),(0,0))

    async def test_real_send_timeout_cleans_up_without_disabling_deadline(self):
        hub=MarketEvents(source());response=hub.response()
        async def blocked(message):
            if message.get('body'):await asyncio.sleep(3)
        await asyncio.wait_for(response.stream_response(blocked),3.5)
        await response.body_iterator.aclose()
        self.assertEqual(hub.timeouts,1)
        self.assertEqual((hub.in_flight_sends,hub.in_flight_bytes),(0,0))

    async def test_client_and_payload_exhaustion_are_explicit(self):
        s=source();hub=MarketEvents(s)
        for _ in range(8):self.assertTrue(hub.reserve())
        self.assertFalse(hub.reserve());self.assertEqual(hub.clients,8)
        s.view=lambda:{'authored_padding':'x'*(1024*1024)}
        frames=hub.frames();self.assertIn('MARKET_SNAPSHOT_BUDGET',await anext(frames))
        with self.assertRaises(StopAsyncIteration):await anext(frames)
        await frames.aclose()

    async def test_five_thousand_burst_quiet_and_reconnect_prefixes_stay_bounded(self):
        c=client();ready(c);hub=MarketEvents(c,interval=.001)
        for i in range(5000):
            q=quote();q['bs']=i+1;c.process(packet(q))
        self.assertEqual((len(c.history),len(c.seen)),(256,256))
        self.assertEqual((c.receipts,c.evicted),(5000,4744))
        frames=hub.frames('delta-v1');first=await anext(frames)
        parsed=json.loads(first.split('data: ',1)[1]);self.assertEqual(parsed['browser_delta']['mode'],'full')
        self.assertEqual(len(parsed['history']),256)
        await frames.aclose()
        # A new browser gets a complete bounded view;no upstream/provider open.
        reconnect=hub.frames('delta-v1');again=await anext(reconnect)
        self.assertEqual(json.loads(again.split('data: ',1)[1])['browser_delta']['mode'],'full')
        await reconnect.aclose()
        c.clock=lambda:131.;self.assertEqual(c.view()['observations'][0]['state'],'STALE')
        c.phase='DISCONNECTED';self.assertEqual(c.view()['observations'][0]['state'],'UNAVAILABLE')
        c.generation+=1;c.phase='SUBSCRIBED'
        self.assertEqual(c.view()['metrics']['AAPL']['valid_ordered_quotes'],0)
        self.assertEqual(hub.status()['upstream_queue_depth'],'UNAVAILABLE_NO_PUBLIC_TRANSPORT_METRIC')


class ResourceHTTP(unittest.TestCase):
    def test_health_exposes_local_resources_without_source_loss_claims(self):
        from terminal.server.app import create_app
        from starlette.testclient import TestClient
        with patch.dict('os.environ',{k:'0' for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED')}):
            c=TestClient(create_app(),base_url='http://127.0.0.1:8787')
            result=c.get('/api/v1/health').json()
        self.assertEqual(result['analytical_resources']['physical_active_workers'],0)
        self.assertEqual(result['analytical_resources']['maximum_workers'],1)
        self.assertEqual(result['browser_push_resources']['application_queue_depth'],0)
        self.assertEqual(result['browser_push_resources']['upstream_queue_depth'],'UNAVAILABLE_NO_PUBLIC_TRANSPORT_METRIC')
