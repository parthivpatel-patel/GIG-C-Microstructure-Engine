"""Single-event-loop analytical admission;worker lifetime survives client cancellation."""
import asyncio
import threading
import time


class AnalysisGate:
    def __init__(self):
        self._worker=None;self._closed=False
        self._metrics_lock=threading.Lock()
        self._active=0;self._peak=0;self._started=0;self._completed=0;self._failed=0
        self._canceled_waiters=0;self._rejected=0;self._work_seconds=0.

    def status(self):
        with self._metrics_lock:
            metrics={'physical_active_workers':self._active,'peak_physical_workers':self._peak,
                     'started':self._started,'completed':self._completed,'failed':self._failed,
                     'total_worker_wall_seconds':self._work_seconds}
        return {'schema':'gig.analysis.resources.v1',**metrics,'admitted_workers':int(self.busy),
                'maximum_workers':1,'application_queue_depth':0,'busy_rejections':self._rejected,
                'canceled_waiters':self._canceled_waiters,'closed':self._closed,
                'scope':'Per application/event loop;no global executor quota or preemptive CPU deadline'}

    def _execute(self,function,args):
        started=time.monotonic()
        with self._metrics_lock:
            self._active+=1;self._peak=max(self._peak,self._active);self._started+=1
        try:return function(*args)
        except BaseException:
            with self._metrics_lock:self._failed+=1
            raise
        finally:
            elapsed=time.monotonic()-started
            with self._metrics_lock:
                self._active-=1;self._completed+=1;self._work_seconds+=elapsed

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
        if self.busy:
            self._rejected+=1;raise ValueError('analysis_busy')
        # Admission and assignment contain no await and are atomic on this loop.
        # Shield owns the actual thread future,not just the HTTP request lock.
        worker=asyncio.create_task(asyncio.to_thread(self._execute,function,args))
        self._worker=worker;worker.add_done_callback(self._observe)
        try:return await asyncio.shield(worker)
        except asyncio.CancelledError:
            self._canceled_waiters+=1
            raise
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
