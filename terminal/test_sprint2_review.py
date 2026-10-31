"""Independent lifecycle review regressions;no provider orowner server access."""
import asyncio
import threading
import unittest
from terminal.server.analysis import AnalysisGate


class ShutdownOwnership(unittest.IsolatedAsyncioTestCase):
    async def test_canceled_close_retains_worker_and_later_close_drains(self):
        gate=AnalysisGate();entered=threading.Event();release=threading.Event()
        def worker():entered.set();assert release.wait(3);return 1
        request=asyncio.create_task(gate.run(worker));closing=None;retry=None
        try:
            self.assertTrue(await asyncio.to_thread(entered.wait,1))
            closing=asyncio.create_task(gate.close());await asyncio.sleep(.01)
            closing.cancel();await asyncio.gather(closing,return_exceptions=True)
            self.assertEqual(gate.status()['physical_active_workers'],1)
            self.assertTrue(gate.busy,'cancelled shutdown must retain ownership of running physical work')
            retry=asyncio.create_task(gate.close());await asyncio.sleep(.01)
            self.assertFalse(retry.done(),'retry shutdown must still await the original worker')
            with self.assertRaisesRegex(ValueError,'analysis_closed'):await gate.run(lambda:2)
        finally:
            release.set();await asyncio.gather(request,return_exceptions=True)
            if retry:await retry
            if closing:await asyncio.gather(closing,return_exceptions=True)
            await gate.close()
        self.assertEqual(gate.status()['physical_active_workers'],0)
        self.assertFalse(gate.busy)

    async def test_repeated_canceled_close_and_failed_worker_remain_accounted(self):
        gate=AnalysisGate();entered=threading.Event();release=threading.Event()
        def worker():entered.set();assert release.wait(3);raise ValueError('authored_worker_failure')
        request=asyncio.create_task(gate.run(worker))
        try:
            self.assertTrue(await asyncio.to_thread(entered.wait,1))
            for _ in range(3):
                close=asyncio.create_task(gate.close());await asyncio.sleep(.001)
                close.cancel();await asyncio.gather(close,return_exceptions=True)
                self.assertTrue(gate.busy)
        finally:
            release.set();await asyncio.gather(request,return_exceptions=True);await gate.close()
        self.assertEqual(gate.status()['failed'],1)
        self.assertEqual(gate.status()['completed'],1)
