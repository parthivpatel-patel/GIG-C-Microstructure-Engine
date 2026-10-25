#!/usr/bin/env python3
"""Authored provisional CRC/native L2 path only. No network, performance gate or L3 journal."""
import argparse,hashlib,json,platform,resource,statistics,sys,time,tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gig_microstructure as gig
from terminal.providers.kraken import KrakenBookAdapter
from terminal.providers.fixtures import EVENTS

def run(events):
    native=gig._native.AggregateDepth(32,1048576)
    def apply(**e):gig._checked((native.snapshot if e['snapshot'] else native.update)(e['bids'],e['asks'],None))
    adapter=KrakenBookAdapter(apply)
    # Fixed snapshot pair prevents contiguous duplicate shortcuts; bounded candidate cache.
    inputs=(EVENTS[0],EVENTS[4])
    t=time.perf_counter()
    for i in range(events):adapter.feed(inputs[i%2],i)
    elapsed=time.perf_counter()-t
    state=gig._checked(native.state())
    return elapsed,state,hashlib.sha256(json.dumps(state,sort_keys=True,separators=(',',':')).encode()).hexdigest()

p=argparse.ArgumentParser();p.add_argument('--events',type=int,default=10000);p.add_argument('--repetitions',type=int,default=3);a=p.parse_args()
if not 2<=a.events<=100000 or not 1<=a.repetitions<=7:p.error('bounded events2..100000; repetitions1..7')
run(100)
results=[run(a.events) for _ in range(a.repetitions)]
assert len({x[2] for x in results})==1
tracemalloc.start();run(a.events);current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
print(json.dumps({'schema':'gig.terminal.feed_benchmark.v1','origin':'HISTORICAL_SYNTHETIC','architecture':platform.machine(),
    'python':platform.python_version(),'native_build':gig.native_build_info(),'fixture_sha256':hashlib.sha256((EVENTS[0]+EVENTS[4]).encode()).hexdigest(),
    'workload':'alternating authored one-level replacement snapshots;includes JSON,CRC,native exact metrics',
    'generator_seed':None,'warmup_events':100,'events_per_repetition':a.events,'repetitions':a.repetitions,
    'seconds':[r[0] for r in results],'median_events_per_second':a.events/statistics.median(r[0] for r in results),
    'output_sha256':results[0][2],'native_pmr_live_bytes':results[0][1]['pmr_live_bytes'],'native_pmr_peak_bytes':results[0][1]['pmr_peak_bytes'],
    'python_traced_current_bytes':current,'python_traced_peak_bytes':peak,'process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'journal_entries':0,'limitations':['Python+native microbenchmark;not exchange latency or network throughput','RSS is whole-process Linux high-water mark','Tracing uses separate untimed pass','Snapshot workload;not representative of all update/trade mixtures']},indent=2))
