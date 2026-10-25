#!/usr/bin/env python3
"""Bounded authored Exchange-shaped decode/native timings, not provider performance."""
import argparse,hashlib,json,platform,resource,statistics,subprocess,sys,time,tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gig_microstructure as gig
from terminal.providers.coinbase_candidate import CoinbaseCandidate


def fixture(events,depth):
    snapshot={'type':'snapshot','product_id':'BTC-USD','bids':[[str(10000-i),'1'] for i in range(depth)],'asks':[[str(20000+i),'1'] for i in range(depth)]}
    updates=[{'type':'l2update','product_id':'BTC-USD','time':'2026-01-01T00:00:00Z','changes':[['buy','10000',str(1+i%2)]]} for i in range(1,events)]
    return [json.dumps(p,separators=(',',':')) for p in [snapshot,*updates]]


def run(raws,depth):
    native=gig._native.AggregateDepth(256,1048576)
    def apply(**event):
        return gig._checked((native.snapshot if event['snapshot'] else native.update)(event['bids'],event['asks'],event['sequence']))
    adapter=CoinbaseCandidate(apply)
    adapter.connect()
    start=time.perf_counter_ns()
    for i,raw in enumerate(raws):adapter.feed(raw,i*1000000)
    elapsed=time.perf_counter_ns()-start
    state=gig._checked(native.state())
    # Independent integer state oracle from the declared fixture, not adapter output.
    expected_bids=[{'price_ticks':str((10000-i)*100000000),'quantity':str((1+(len(raws)-1)%2 if i==0 else 1)*100000000)} for i in range(depth)]
    expected_asks=[{'price_ticks':str((20000+i)*100000000),'quantity':'100000000'} for i in range(depth)]
    assert state['bids']==expected_bids and state['asks']==expected_asks
    assert state['revision']==str(len(raws))
    canonical=hashlib.sha256(json.dumps({'bids':expected_bids,'asks':expected_asks,'revision':state['revision']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return elapsed,state,canonical


def main():
    p=argparse.ArgumentParser();p.add_argument('--events',type=int,default=1024);p.add_argument('--depth',type=int,default=256);p.add_argument('--repetitions',type=int,default=3);a=p.parse_args()
    if not 2<=a.events<=8192 or not 1<=a.depth<=256 or not 1<=a.repetitions<=5:p.error('events2..8192,depth1..256,repetitions1..5')
    raws=fixture(a.events,a.depth);run(fixture(8,a.depth),a.depth)
    results=[run(raws,a.depth) for _ in range(a.repetitions)]
    tracemalloc.start();run(raws,a.depth);_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    assert len({r[2] for r in results})==1
    cpu=next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),platform.processor())
    print(json.dumps({'schema':'gig.coinbase_candidate.benchmark.v1','classification':'HISTORICAL_SYNTHETIC','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),'architecture':platform.machine(),'cpu':cpu,'python':platform.python_version(),'native_build':gig.native_build_info(),'events':a.events,'levels_per_side':a.depth,'repetitions':a.repetitions,'warmup_events':8,'generator_seed':None,'fixture_sha256':hashlib.sha256(('\n'.join(raws)+'\n').encode()).hexdigest(),'canonical_sha256':results[0][2],'processing_ns':[r[0] for r in results],'median_events_per_second':a.events*1e9/statistics.median(r[0] for r in results),'python_traced_peak_bytes':peak,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'native_pmr_peak_bytes':results[0][1]['pmr_peak_bytes'],'scope':'candidate JSON/exact conversion/native transaction;full bounded depth;no supervisor,research,socket or recording timing','limitations':['Linux whole-process RSS high-water','Input creation outside timer/tracing;native construction outside timer','Separate untimed memory pass;no total allocation count','Not live protocol qualification or production latency']},indent=2))

if __name__=='__main__':main()
