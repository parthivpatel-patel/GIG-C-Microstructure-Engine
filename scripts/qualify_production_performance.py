#!/usr/bin/env python3
"""Correctness-gated, authored-only single-process qualification; no latency target.

Uses the existing native book benchmark plus actual Python/native replay and the
bounded IEX/projection fixture. No provider, order, account or retained market data.
"""
import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))


def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def distribution(values):
    if not values or any(type(v)is not int or v<=0 for v in values):raise ValueError('unresolved_latency_sample')
    ordered=sorted(values)
    return {**{f'p{q}_ns':ordered[math.ceil(len(ordered)*q/100)-1]for q in (50,95,99)},
            'maximum_ns':ordered[-1],'samples':len(ordered),'percentiles':'nearest_rank_serial_service_not_arrival_latency'}


def replay_trial(events,expected_quantity):
    import gig_microstructure as gig
    import python_fixtures as f
    replay=gig.Replay(f.rules(),f.replay_config());samples=[];begin=time.perf_counter_ns()
    for event in events:
        start=time.perf_counter_ns();replay.apply(event);samples.append(time.perf_counter_ns()-start)
    elapsed=time.perf_counter_ns()-begin
    book=replay.snapshot('4')['data']['book']
    assert sum(int(row['quantity'])for row in book['bids'])==expected_quantity and not book['asks']
    status=replay.status();assert int(status['journal_size'])==len(events) and not status['needs_recovery']
    return dict(elapsed_ns=elapsed,service_ns=samples,output_sha256=sha(replay.canonical().encode()),status=status)


def provider_trial(count):
    from terminal.stocks.test_final import client,packet,quote
    from terminal.server.market_delta import MarketProjection
    stream=client();stream.phase='SUBSCRIBED';stream.symbols=('AAPL','MSFT','NVDA','AMZN')
    projection=MarketProjection();cache={};samples=[];wire_peak=0;retained=[]
    begin=time.perf_counter_ns()
    for i in range(count):
        q=quote();q['S']=stream.symbols[i%4];q['bs']=i+1
        start=time.perf_counter_ns();stream.process(packet(q));full=stream.view();wire=projection.project(full)
        delta=wire['browser_delta']
        if delta['mode']=='full':cache={}
        cache.update({r['receipt_index']:r for r in wire['history']})
        cache={n:{**cache[n],'state':state,'receive_age_seconds':age}for n,state,age in delta['history_status']}
        samples.append(time.perf_counter_ns()-start)
        assert list(cache)==list(range(max(1,i+2-256),i+2))
        assert delta['sequence']==i+1 and len(cache)<=256
        wire_peak=max(wire_peak,len(encoded(wire)))
        if i%128==127:retained.append(len(stream.history))
    elapsed=time.perf_counter_ns()-begin
    assert stream.receipts==count and len(stream.history)==min(256,count) and len(stream.seen)<=256
    assert stream.evicted==max(0,count-256)
    return dict(elapsed_ns=elapsed,service_ns=samples,accepted=count,retained=len(stream.history),
                evicted=stream.evicted,maximum_wire_bytes=wire_peak,retained_counts_each128=retained,
                output_sha256=sha(encoded([(r['receipt_index'],r['symbol'],r['data'])for r in stream.history])),
                scope='Authored four-symbol quote normalization+metrics+projection+independent client reconstruction;no network or real slow consumer')


def qualify(build,out,orders=64,observations=512,repetitions=3,warmup=1):
    if type(orders)is not int or not 16<=orders<=256:raise ValueError('orders_budget')
    if type(observations)is not int or not 512<=observations<=4096:raise ValueError('observations_budget')
    if type(repetitions)is not int or not 3<=repetitions<=9 or type(warmup)is not int or not 1<=warmup<=3:raise ValueError('repetition_budget')
    build=Path(build).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('evidence_exists')
    if ROOT in out.parents and subprocess.run(['git','check-ignore','-q',str(out)],cwd=ROOT).returncode:
        raise ValueError('output_must_be_ignored')
    cache=(build/'CMakeCache.txt').read_text()
    if 'CMAKE_BUILD_TYPE:STRING=Release' not in cache or any(k+':BOOL=ON'in cache for k in ('GIG_ENABLE_ASAN','GIG_ENABLE_UBSAN')):raise ValueError('unsanitized_release_required')
    import gig_microstructure as gig
    import python_fixtures as f
    from scripts.run_engine_baseline import compiler_metadata
    from terminal.verification.artifacts import write_private
    if build not in Path(gig._native.__file__).resolve().parents:raise ValueError('selected_native_build_mismatch')
    out.mkdir(parents=True,mode=0o700);cpu0=time.process_time();wall0=time.perf_counter()
    source_names=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=ROOT).split(b'\0')
    sources={raw.decode():sha((ROOT/raw.decode()).read_bytes())for raw in source_names if raw and raw.decode().startswith(('include/','src/','benchmarks/','scripts/','terminal/stocks/','terminal/server/'))and raw.decode().endswith(('.py','.hpp','.cpp'))}
    events=[f.event(value=f.add(i+1,'0',100+i%4,2),seq=i)for i in range(orders)]
    executable=build/'benchmarks/gig_book_benchmark';args=[str(executable),str(orders),str(repetitions),str(warmup),'1729',str(out)]
    result=subprocess.run(args,capture_output=True,text=True,check=True,timeout=120);native=json.loads(result.stdout)
    assert native['phase2_correctness_validated'] and len(native['measurements'])==8
    (out/'native-raw.json').write_text(result.stdout)
    native_summary={}
    for name,row in native['measurements'].items():
        assert len(row['bulk_samples'])==repetitions
        native_summary[name]={**distribution(row['service_time_ns']),
             'median_operations_per_second':statistics.median(row['operations_per_repetition']*1e9/s['elapsed_ns']for s in row['bulk_samples']),
             'operations_per_repetition':row['operations_per_repetition']}
    # Existing two-symbol reconstruction benchmark, checked against authored bytes.
    from scripts.check_itch_reconstruction_benchmark import fixture
    recon_exe=build/'benchmarks/gig_itch_reconstruction_benchmark'
    recon=json.loads(subprocess.check_output([str(recon_exe),str(orders),str(repetitions)],text=True,timeout=120))
    source_records,source_bytes,expected_checksum,expected_mapping=fixture(orders)
    assert recon['fixture_sha256']==sha(source_bytes) and recon['records']==len(source_records)
    assert recon['checksum']==expected_checksum and recon['receipt_fnv1a64']==expected_mapping
    assert recon['native_records']==8*orders and recon['external_records']==3
    assert recon['live_bytes_after_destroy']==0 and len(recon['elapsed_ns'])==repetitions
    assert recon['initialization']=='authored_complete_empty_synthetic' and not recon['container_complete']
    (out/'reconstruction-raw.json').write_text(json.dumps(recon,sort_keys=True)+'\n')
    for _ in range(warmup):replay_trial(events,orders*2);provider_trial(observations)
    replays=[replay_trial(events,orders*2)for _ in range(repetitions)]
    providers=[provider_trial(observations)for _ in range(repetitions)]
    assert len({r['output_sha256']for r in replays})==1 and len({r['output_sha256']for r in providers})==1
    gc.collect();tracemalloc.start();provider_trial(observations);current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    scaling=[]
    for size in (16,64,128):
        trial=replay_trial([f.event(value=f.add(i+1,'0',100+i%4,2),seq=i)for i in range(size)],size*2)
        scaling.append({'events':size,**trial['status']})
    elapsed=time.perf_counter()-wall0
    manifest=dict(schema='gig.production.performance.v1',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      tracked_dirty=bool(subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=ROOT)),classification='AUTHORED_LOCAL_NOT_PRODUCTION_LATENCY',source_sha256=sources,
      environment=dict(architecture=platform.machine(),os=platform.platform(),python=platform.python_version(),native_build=gig.native_build_info(),native_binary_sha256=sha(Path(gig._native.__file__).read_bytes()),
        cpu=next((line.split(':',1)[1].strip()for line in Path('/proc/cpuinfo').read_text().splitlines()if line.startswith('model name')),'UNKNOWN'),affinity=sorted(os.sched_getaffinity(0)),**compiler_metadata(build)),
      workload=dict(orders=orders,observations=observations,repetitions=repetitions,warmup=warmup,native_seed=1729,python_generator='explicit_fixture_v1',input_sha256=sha(encoded(events)),provider_symbols=4),
      native=native_summary,reconstruction=recon,native_physical_journal_record_bytes=native['physical_journal_record_bytes'],native_peak_process_bytes=native['native_vm_hwm_bytes'],
      python_replay=dict(**distribution([n for r in replays for n in r['service_ns']]),median_events_per_second=statistics.median(orders*1e9/r['elapsed_ns']for r in replays),output_sha256=replays[0]['output_sha256']),
      provider_projection=dict(**distribution([n for r in providers for n in r['service_ns']]),median_events_per_second=statistics.median(observations*1e9/r['elapsed_ns']for r in providers),
        **{k:providers[0][k]for k in ('output_sha256','retained','evicted','maximum_wire_bytes','retained_counts_each128','scope')}),
      sustained_memory=dict(python_traced_current_bytes=current,python_traced_peak_bytes=peak,whole_process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,replay_scaling=scaling),
      process=dict(cpu_seconds=time.process_time()-cpu0,wall_seconds=elapsed,cpu_scope='Parent process only;native child excluded;not sampled utilization'),
      artifacts={p.name:sha(p.read_bytes())for p in out.iterdir()if p.is_file()},
      methodology='Serial service times include wrapper/timer overhead;bulk and serial native passes separate. Python service pass and throughput share instrumentation. Memory tracing in separate pass. No arrival queue/network/GitHub edge/GPU benchmark;finite local workload,not long-soak or universal institutional SLA.')
    assert all(sha((ROOT/p).read_bytes())==h for p,h in sources.items()),'source_changed_during_benchmark'
    write_private(out/'manifest.json',manifest)
    return manifest


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--native-build-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--orders',type=int,default=64);p.add_argument('--observations',type=int,default=512);p.add_argument('--repetitions',type=int,default=3);p.add_argument('--warmup',type=int,default=1);a=p.parse_args()
    r=qualify(a.native_build_dir,a.output,a.orders,a.observations,a.repetitions,a.warmup)
    print(json.dumps({k:r[k]for k in ('schema','source_commit','native','reconstruction','python_replay','provider_projection','sustained_memory')}))
if __name__=='__main__':main()
