"""Authored128-intent capacity experiment;no account/provider connection."""
import asyncio
import json
import platform
from pathlib import Path
import resource
import tempfile
import time
import tracemalloc
from terminal.paper.contracts import PaperError,MAX_ORDERS
from terminal.paper.store import IntentStore
from terminal.paper.fake import FakeBroker
from terminal.paper.engine import PaperEngine

async def main():
    with tempfile.TemporaryDirectory() as private:
        tracemalloc.start();clock=lambda:1000;store=IntentStore(Path(private)/'fake');broker=FakeBroker(store,clock);engine=PaperEngine(store,broker,clock=clock)
        await engine.arm_demo(True);samples=[];start=time.perf_counter()
        definition={'symbol':'AAPL','side':'buy','quantity':'1','limit_price':'100','type':'limit','time_in_force':'day'}
        for i in range(MAX_ORDERS):
            await engine.submit(str(i),definition);await engine.cancel(str(i))
            if i+1 in (1,16,64,128):
                current,peak=tracemalloc.get_traced_memory();samples.append({'intents':i+1,'tracked_current_bytes':current,'tracked_peak_bytes':peak,'database_bytes':store.path.stat().st_size,'audit_entries':store.audit_receipt()['entries']})
        elapsed=time.perf_counter()-start
        try:await engine.submit('overflow',definition)
        except PaperError as exc:assert exc.code=='paper_intent_capacity'
        else:raise AssertionError('capacity not enforced')
        assert len(store.read()['orders'])==128 and broker.place_calls==128
        print(json.dumps({'schema':'gig.paper.resource.v1','classification':'AUTHORED_FAKE_NOT_BROKER_PERFORMANCE','python':platform.python_version(),'architecture':platform.machine(),'platform':platform.platform(),'clock':'fixed1000ms','maximum_intents':MAX_ORDERS,'elapsed_seconds':elapsed,'intent_cancel_pairs_per_second':MAX_ORDERS/elapsed,'peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'samples':samples,'limitations':['One cold run with tracemalloc overhead;no latency percentile or provider performance claim.','Database budget16MiB;SQLite rollback sidecar may require an additional16MiB during a transaction.','Audit capacity2048 intentionally refuses further mutation;no unbounded archival or broker hot recovery.']},indent=2))
if __name__=='__main__':asyncio.run(main())
