"""Synthetic native receipts only; bounded asynchronous capture and fault behavior."""
import asyncio,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from .l2_capture import Capture
from .l2_playback import RecordedSession
from .providers.kraken import KrakenBookAdapter
from .providers.fixtures import EVENTS

class CaptureTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.captures=[]
        native=gig._native.AggregateDepth(32,1048576)
        def apply(**e):gig._checked((native.snapshot if e['snapshot'] else native.update)(e['bids'],e['asks'],None))
        self.adapter=KrakenBookAdapter(apply,price_scale=100000000)
    async def asyncTearDown(self):
        for c in self.captures:
            if not c.task.done():await c.abort('test_cleanup')
        self.tmp.cleanup()
    async def create(self):
        c=await Capture.create(self.root,'authored',enabled=True,version=2);self.captures.append(c);return c
    async def settle(self,predicate):
        for _ in range(100):
            if predicate():return
            await asyncio.sleep(.005)
        self.fail('bounded capture did not settle')
    async def test_capture_native_prefix_and_timestamps(self):
        c=await self.create()
        for i,raw in enumerate(EVENTS):
            receipt=self.adapter.feed(raw,i)
            c.offer(raw,i,str(1000+i),receipt)
            await self.settle(lambda:c.written==i+1)
        result=await c.stop();self.assertEqual(result['state'],'COMPLETE');self.assertEqual(result['accepted'],5)
        session=RecordedSession(self.root,'authored');self.assertEqual(session.view(5,False,1)['received_at_ns'],'1004')
        self.assertEqual(session.view(5,False,1)['book']['bids'][0]['price_ticks'],'9900000000')
    async def test_burst_overflow_never_publishes_partial_log(self):
        c=await self.create();receipt=self.adapter.feed(EVENTS[0],0)
        for i in range(4):c.offer(EVENTS[0],i,None,receipt)
        with self.assertRaisesRegex(ValueError,'queue_overflow'):c.offer(EVENTS[0],4,None,receipt)
        await c.abort();self.assertEqual(c.state,'ERROR');self.assertEqual(list(self.root.iterdir()),[])
    async def test_disk_failure_aborts_and_stop_does_not_hang(self):
        c=await self.create();receipt=self.adapter.feed(EVENTS[0],0)
        with patch.object(c.writer,'append',side_effect=OSError('authored ENOSPC')):
            c.offer(EVENTS[0],0,None,receipt);await self.settle(lambda:c.task.done())
        await asyncio.wait_for(c.stop(),1)
        self.assertEqual(c.state,'ERROR');self.assertEqual(list(self.root.iterdir()),[])
    async def test_allocation_failure_aborts(self):
        c=await self.create();receipt=self.adapter.feed(EVENTS[0],0)
        with patch('terminal.l2_capture.deepcopy',side_effect=MemoryError()):
            with self.assertRaises(MemoryError):c.offer(EVENTS[0],0,None,receipt)
        await c.abort();self.assertEqual(list(self.root.iterdir()),[])
    async def test_no_snapshot_cannot_be_finalized(self):
        c=await self.create();await c.stop();self.assertEqual(c.state,'ERROR');self.assertEqual(list(self.root.iterdir()),[])
    async def test_completed_interval_survives_subsequent_source_disconnect(self):
        c=await self.create();receipt=self.adapter.feed(EVENTS[0],0);c.offer(EVENTS[0],0,None,receipt)
        await c.stop();await c.abort('later_disconnect');self.assertEqual(c.state,'COMPLETE')
        self.assertEqual(RecordedSession(self.root,'authored').event_count,1)

if __name__=='__main__':unittest.main()
