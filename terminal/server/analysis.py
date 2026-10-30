"""Single-event-loop analytical admission;worker lifetime survives client cancellation."""
import asyncio


class AnalysisGate:
    def __init__(self):
        self._worker=None;self._closed=False

    @property
    def busy(self):
        return self._worker is not None and not self._worker.done()

    def _observe(self,task):
        # A disconnected caller cannot leave an unobserved worker exception.
        # Never log exception text or retain its response/input in a job history.
        if not task.cancelled():task.exception()
        if self._worker is task:self._worker=None

    async def run(self,function,*args):
        if self._closed:raise ValueError('analysis_closed')
        if self.busy:raise ValueError('analysis_busy')
        # Admission and assignment contain no await and are atomic on this loop.
        # Shield owns the actual thread future,not just the HTTP request lock.
        worker=asyncio.create_task(asyncio.to_thread(function,*args))
        self._worker=worker;worker.add_done_callback(self._observe)
        try:return await asyncio.shield(worker)
        finally:
            if worker.done()and self._worker is worker:self._worker=None

    async def close(self):
        self._closed=True
        worker=self._worker
        if worker is not None:
            try:await asyncio.shield(worker)
            except Exception:pass  # Caller owns operation errors;shutdown only drains.
            finally:
                if worker.done()and self._worker is worker:self._worker=None
