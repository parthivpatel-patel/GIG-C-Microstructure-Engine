"""Bounded driver smoke and backpressure/recovery controls, not a live qualification."""
import asyncio
import unittest
from pathlib import Path
from scripts.qualify_sustained_workload import exercise,Transport,semantic,digest


class Workload(unittest.IsolatedAsyncioTestCase):
    async def test_small_real_lifecycle_and_ledger_recovery(self):
        result=await exercise(batches=6,cadence=.001,slow_delay=.005,trace=False)
        self.assertEqual(result['projection_interval_seconds'],.25)
        self.assertEqual(result['retained'],result['accepted'])
        self.assertEqual(result['storage_retained'],result['accepted'])
        self.assertEqual(result['source_opens'],result['source_closes'])
        self.assertEqual(result['counters']['injected_disk_faults'],1)
        self.assertEqual(result['counters']['cancelled_consumers'],1)
        self.assertEqual(result['backpressure']['clients'],0)
        self.assertEqual(result['backpressure']['in_flight_body_bytes'],0)
        self.assertEqual(result['origin'],'HISTORICAL_SYNTHETIC')
        self.assertLessEqual(result['source_queue_peak'],4)

    async def test_fixture_queue_backpressures_fifth_frame_and_cancel_cleans_waiter(self):
        from scripts.qualify_sustained_workload import Socket
        factory=Transport();socket=Socket(factory)
        for _ in range(4):await socket.put([{'T':'authored'}])
        blocked=asyncio.create_task(socket.put([{'T':'authored'}]));await asyncio.sleep(0)
        self.assertFalse(blocked.done());self.assertEqual(socket.queue.qsize(),4)
        blocked.cancel()
        with self.assertRaises(asyncio.CancelledError):await blocked
        self.assertEqual(socket.queue.qsize(),4);self.assertEqual(factory.queue_peak,4)

    async def test_driver_resource_limits_reject_before_runtime(self):
        for args in ({'batches':5},{'batches':3001},{'cadence':0},{'cadence':1},{'slow_delay':4}):
            with self.subTest(args=args),self.assertRaises(ValueError):await exercise(**args)

    async def test_fake_socket_drop_is_explicit_transport_failure(self):
        from scripts.qualify_sustained_workload import Socket
        socket=Socket(Transport());await socket.queue.put(OSError('AUTHORED'))
        with self.assertRaises(OSError):await socket.recv()

    async def test_cancellation_releases_stream_and_clients(self):
        task=asyncio.create_task(exercise(batches=100,cadence=.1,slow_delay=.1,trace=False))
        await asyncio.sleep(.1);task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        # No workload tasks survive cancel. Isolated test runner itself is excluded.
        pending=[t for t in asyncio.all_tasks()if t is not asyncio.current_task()and not t.done()]
        self.assertEqual(pending,[])


class Recipe(unittest.TestCase):
    def test_semantic_fingerprint_ignores_clock_but_preserves_data_and_identity(self):
        a={'receipt_index':1,'symbol':'AAPL','kind':'quote','data':{'bid':'100'},'timestamp':'authored clock A'}
        b={**a,'timestamp':'authored clock B'}
        self.assertEqual(digest([semantic(a)]),digest([semantic(b)]))
        self.assertNotEqual(digest([semantic(a)]),digest([semantic({**a,'symbol':'NVDA'})]))

    def test_owner_gated_arm_workflow_includes_this_cohort(self):
        text=(Path(__file__).resolve().parents[1]/'.github/workflows/native-arm64.yml').read_text()
        self.assertIn('terminal/tests/run_institutional_sprint2.py',text)
        self.assertIn('workflow_dispatch:',text);self.assertIn('inputs.free_usage_verified',text)
        self.assertNotIn('\n  push:',text)
