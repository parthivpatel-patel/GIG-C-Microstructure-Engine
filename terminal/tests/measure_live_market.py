"""Bounded synthetic parse+atomic-commit+metrics benchmark;not exchange latency."""
import sys,time,tracemalloc,json,platform,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.test_final import client,ready,quote,packet
c=client();ready(c)
for i in range(256):
 q=quote();q['bs']=i;c.process(packet(q))
tracemalloc.start();start=time.perf_counter();count=1000
for i in range(count):
 q=quote();q['bs']=i+256;c.process(packet(q));c.view()
elapsed=time.perf_counter()-start;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
print(json.dumps({'schema':'gig.live_market.measure.v1','classification':'AUTHORED_SYNTHETIC_NOT_PROVIDER_PERFORMANCE','python':platform.python_version(),'architecture':platform.machine(),'platform':platform.platform(),'warmup_events':256,'measured_events':count,'repetitions':1,'elapsed_seconds':elapsed,'events_per_second':count/elapsed,'tracemalloc_current_bytes':current,'tracemalloc_peak_bytes':peak,'process_peak_rss_kib_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'retained_events':len(c.history),'dedup_identities':len(c.seen),'receipt_count':c.receipts,'limitations':['Includes tracemalloc instrumentation and full view calculation per event','Python allocation peak is not native/GPU allocation accounting','No socket/network/exchange latency or production throughput claim','Single run on shared cloud CPU,no stable performance baseline']},indent=2))
