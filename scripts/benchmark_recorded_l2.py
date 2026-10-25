#!/usr/bin/env python3
"""Reproducible authored L2 IO/replay timings; no market/provider data or performance gate."""
import argparse,hashlib,json,math,platform,resource,statistics,subprocess,sys,tempfile,time,tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gig_microstructure as gig
from terminal.providers.kraken import KrakenBookAdapter
from terminal.providers.fixtures import EVENTS
from terminal.l2_recording import L2Writer
from terminal.l2_playback import RecordedSession

def source(n):
    update=json.dumps({**json.loads(EVENTS[0]),'type':'update'},separators=(',',':'))
    return [EVENTS[0]]+[EVENTS[1] if i%2 else update for i in range(1,n)]

def run(raws,record=False):
    b=gig._native.AggregateDepth(32,1048576)
    def apply(**e):gig._checked((b.snapshot if e['snapshot'] else b.update)(e['bids'],e['asks'],None))
    a=KrakenBookAdapter(apply,price_scale=100000000)
    with tempfile.TemporaryDirectory(prefix='gig-authored-benchmark-') as d:
        writer=L2Writer(d,'authored',enabled=True,version=2) if record else None
        start=time.perf_counter()
        for i,raw in enumerate(raws):
            receipt=a.feed(raw,i*1000000)
            if writer:writer.append(raw,i*1000000,normalized=receipt)
        if writer:manifest=writer.finish('fixture_complete')
        processing=time.perf_counter()-start
        compile_time=None;latencies=[];digest=None;cache=0;log_bytes=0
        if writer:
            start=time.perf_counter();session=RecordedSession(d,'authored');compile_time=time.perf_counter()-start
            cache=session.cache_bytes;log_bytes=manifest['bytes']
            for i in range(session.event_count+1):
                start=time.perf_counter_ns();session.view(i,False,1);latencies.append(time.perf_counter_ns()-start)
            last=session.view(session.event_count,False,1)
            digest=hashlib.sha256(json.dumps(last,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        return {'processing_seconds':processing,'compile_seconds':compile_time,'view_nanoseconds':latencies,
            'cache_encoded_bytes':cache,'log_bytes':log_bytes,'final_sha256':digest,
            'native_pmr_peak_bytes':gig._checked(b.state())['pmr_peak_bytes']}

p=argparse.ArgumentParser();p.add_argument('--events',type=int,default=128);p.add_argument('--repetitions',type=int,default=3);a=p.parse_args()
if not 2<=a.events<=512 or not 1<=a.repetitions<=5:p.error('events2..512,repetitions1..5')
raws=source(a.events);run(source(8),True)
baseline=[run(raws) for _ in range(a.repetitions)];recorded=[run(raws,True) for _ in range(a.repetitions)]
assert len({r['final_sha256'] for r in recorded})==1
tracemalloc.start();memory=run(raws,True);current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
latencies=sorted(x for r in recorded for x in r['view_nanoseconds'])
def q(f):return latencies[max(0,math.ceil(len(latencies)*f)-1)]
native=gig._native.AggregateDepth(32,1048576)
gig._checked(native.snapshot([{'price_ticks':'100','quantity':'2'}],[{'price_ticks':'101','quantity':'3'}],None))
native_latencies=[]
for i in range(1100):
    begin=time.perf_counter_ns();gig._checked(native.update([{'price_ticks':'100','quantity':str(2+i%2)}],[],None));elapsed=time.perf_counter_ns()-begin
    if i>=100:native_latencies.append(elapsed)
native_latencies.sort()
info={'schema':'gig.recorded_l2.benchmark.v1','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    'worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),
    'architecture':platform.machine(),'python':platform.python_version(),'native_build':gig.native_build_info(),
    'source_files_sha256':{name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in ('terminal/l2_recording.py','terminal/l2_playback.py','terminal/l2_research.py',__file__)},
    'classification':'HISTORICAL_SYNTHETIC','workload':'one snapshot,alternating absolute bid sizes;CRC/native metrics;recorded native research prefixes',
    'seed':None,'fixture_sha256':hashlib.sha256(('\n'.join(raws)+'\n').encode()).hexdigest(),
    'native_binding_update_latency_nanoseconds':{'count':1000,'warmup':100,'p50':native_latencies[499],'p95':native_latencies[949],'p99':native_latencies[989],'scope':'Python binding+native atomic depth update;no socket or pure C++ cycle isolation'},
    'events':a.events,'repetitions':a.repetitions,'warmup_events':8,'unrecorded_seconds':[r['processing_seconds'] for r in baseline],
    'recorded_seconds':[r['processing_seconds'] for r in recorded],'compile_seconds':[r['compile_seconds'] for r in recorded],
    'median_unrecorded_events_per_second':a.events/statistics.median(r['processing_seconds'] for r in baseline),
    'median_recorded_events_per_second':a.events/statistics.median(r['processing_seconds'] for r in recorded),
    'view_latency_nanoseconds':{'count':len(latencies),'p50':q(.5),'p95':q(.95),'p99':q(.99),'method':'sorted nearest rank;owned Python cache view,not exchange latency'},
    'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'python_traced_peak_bytes':peak,
    'encoded_cache_bytes':memory['cache_encoded_bytes'],'log_bytes':memory['log_bytes'],'final_sha256':memory['final_sha256'],
    'native_pmr_peak_bytes':memory['native_pmr_peak_bytes'],'limits':['Linux whole-process RSS high-water mark','No network or disk-hardware durability claim','Processing timers exclude writer construction/setup;final fsync is included','Synchronous writer microbenchmark;async production path separately fault tested','No total allocator-call count or production tail-latency claim']}
print(json.dumps(info,indent=2))
