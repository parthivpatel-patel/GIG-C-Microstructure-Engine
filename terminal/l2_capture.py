"""One bounded background writer; rejected/overflowed capture is never published as complete."""
import asyncio
from copy import deepcopy
from .l2_recording import L2Writer,MAX_RECORDS

class Capture:
    def __init__(self,writer):
        self.writer=writer;self.queue=asyncio.Queue(maxsize=4)
        self.state='RECORDING';self.reason=None;self.accepted=self.written=0
        self.saw_snapshot=False;self.manifest=None;self.abort_requested=False
        self.task=asyncio.create_task(self._write(),name='gig-one-bounded-recorder')
    @classmethod
    async def create(cls,*args,**kwargs):
        writer=await asyncio.to_thread(L2Writer,*args,**kwargs)
        return cls(writer)
    def offer(self,raw,now,unix,receipt):
        if self.state=='ERROR':raise ValueError('recording_failed')
        if self.state!='RECORDING':return
        try:value=(raw,now,unix,deepcopy(receipt))
        except MemoryError:
            self.state,self.reason='ERROR','recording_allocation_failure';self.abort_requested=True
            raise
        try:self.queue.put_nowait(value)
        except asyncio.QueueFull:
            self.state,self.reason='ERROR','recording_queue_overflow';self.abort_requested=True
            raise ValueError('recording_queue_overflow') from None
        self.accepted+=1;self.saw_snapshot|=receipt.get('kind')=='snapshot'
        if self.accepted==MAX_RECORDS:self.state='FINALIZING'
    async def _write(self):
        try:
            while True:
                item=await self.queue.get()
                if self.abort_requested:break
                if item is None:
                    if not self.saw_snapshot:raise ValueError('recording_snapshot_missing')
                    self.manifest=await asyncio.to_thread(self.writer.finish,'operator_stopped')
                    self.state='COMPLETE';return
                raw,now,unix,receipt=item
                await asyncio.to_thread(self.writer.append,raw,now,receive_unix_ns=unix,normalized=receipt)
                self.written+=1
                if self.written==MAX_RECORDS:
                    if not self.saw_snapshot:raise ValueError('recording_snapshot_missing')
                    self.manifest=await asyncio.to_thread(self.writer.finish,'record_budget')
                    self.state='COMPLETE';return
        except Exception:
            self.state='ERROR';self.reason=self.reason or 'recording_write_or_finalize_failed'
        finally:
            if self.state!='COMPLETE':await asyncio.to_thread(self.writer.abort)
            while not self.queue.empty():self.queue.get_nowait()
    async def stop(self):
        if not self.task.done():
            if self.state=='RECORDING':self.state='FINALIZING'
            # Race-safe wait: a failed worker must not leave a full queue put hanging.
            put=asyncio.create_task(self.queue.put(None))
            done,_=await asyncio.wait((put,self.task),return_when=asyncio.FIRST_COMPLETED)
            if self.task in done and not put.done():put.cancel()
            try:await put
            except asyncio.CancelledError:pass
        await self.task
        while not self.queue.empty():self.queue.get_nowait()
        return self.status()
    async def abort(self,reason='source_interrupted'):
        if self.task.done() and self.state=='COMPLETE':return self.status()
        self.abort_requested=True;self.state='ERROR';self.reason=reason
        await self.stop()
    def status(self):
        return {'state':self.state,'reason':self.reason,'identity':self.writer.identity,
                'accepted':self.accepted,'written':self.written,'queue_capacity':4,
                'queue_occupancy':self.queue.qsize(),'maximum_records':MAX_RECORDS,
                'market_session_complete':False,'sha256':self.manifest['sha256'] if self.manifest else None}
