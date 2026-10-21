#!/usr/bin/env python3
"""Correctness-gated Phase 2 baseline; writes a new run directory, never overwrites evidence."""
import argparse
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]

def command(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def cache_values(build):
    values={}
    for line in (build/'CMakeCache.txt').read_text().splitlines():
        if line and not line.startswith(('#','//')) and '=' in line and ':' in line.split('=',1)[0]:
            key,value=line.split('=',1);values[key.split(':',1)[0]]=value
    return values

def source_hashes():
    raw=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=ROOT)
    files=set(x.decode() for x in raw.split(b'\0') if x)
    prefixes=('include/','src/','benchmarks/','fixtures/','tests/','scripts/','cmake/','.github/workflows/')
    chosen=sorted(f for f in files if f in ('CMakeLists.txt','CMakePresets.json') or f.startswith(prefixes))
    result={}
    for name in chosen:
        path=ROOT/name
        if ROOT not in path.resolve().parents:
            raise RuntimeError('source path escapes repository')
        result[name]=sha(path)
    return result

def quantile(values,percent):
    ordered=sorted(values)
    return ordered[max(0,math.ceil(len(ordered)*percent/100)-1)]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir',type=Path,default=ROOT/'build/release')
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--orders',type=int,default=512)
    parser.add_argument('--repetitions',type=int,default=7)
    parser.add_argument('--warmup',type=int,default=2)
    parser.add_argument('--seed',type=int,default=1729)
    parser.add_argument('--verify-against',type=Path,help='compare reproducible input/output hashes, not timings')
    args=parser.parse_args()
    for name,upper in [('orders',2048),('repetitions',30),('warmup',10),('seed',(1<<64)-1)]:
        if not 1<=getattr(args,name)<=upper:
            parser.error(name+' out of range')
    build=args.build_dir.resolve();output=args.output_dir.resolve()
    if output.exists(): parser.error('refusing to overwrite existing evidence directory')
    if ROOT in output.parents and subprocess.run(['git','check-ignore','-q',str(output)],cwd=ROOT).returncode!=0:
        parser.error('output must be ignored or outside checkout; archive selected evidence afterward')
    cache=cache_values(build)
    if cache.get('CMAKE_BUILD_TYPE')!='Release' or cache.get('BUILD_TESTING')!='ON' or cache.get('GIG_BUILD_BENCHMARKS')!='ON':
        parser.error('requires Release, BUILD_TESTING=ON and GIG_BUILD_BENCHMARKS=ON')
    if any(cache.get(k)=='ON' for k in ('GIG_ENABLE_ASAN','GIG_ENABLE_UBSAN','GIG_ENABLE_TSAN')):
        parser.error('sanitized builds are correctness runs, not timing evidence')
    head=command('git','rev-parse','HEAD');status=command('git','status','--porcelain=v1','--untracked-files=all');sources=source_hashes()
    output.mkdir(parents=True,exist_ok=False)
    try:
        with (output/'validation.log').open('w') as log:
            for cmd in (['cmake','-S',str(ROOT),'-B',str(build)],['cmake','--build',str(build),'--parallel','2'],
                        ['ctest','--test-dir',str(build),'--output-on-failure','--no-tests=error','--output-junit',str(output/'tests.xml')]):
                subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        tests=ET.parse(output/'tests.xml').getroot()
        names={x.get('name') for x in tests.findall('testcase')}
        required={'book.reference','book.allocations','replay.atomicity','replay.canonical','numeric.independent_reference','benchmark.book_smoke'}
        if not required<=names or any(int(tests.get(k,'0')) for k in ('failures','errors','skipped')):
            raise RuntimeError('required correctness tests did not all execute successfully')
        cache=cache_values(build)
        commands=json.loads((build/'compile_commands.json').read_text())
        flags={k:v for k,v in cache.items() if k.startswith(('CMAKE_CXX_FLAGS','CMAKE_EXE_LINKER_FLAGS','GIG_'))}
        compiled=' '.join(x['command'] for x in commands)+' '+' '.join(flags.values())
        if '-flto' in compiled or '-fsanitize' in compiled:
            raise RuntimeError('timing build must exclude LTO and sanitizers')
        exe=build/'benchmarks/gig_book_benchmark'
        raw=subprocess.run([str(exe),str(args.orders),str(args.repetitions),str(args.warmup),str(args.seed),str(output)],
                           cwd=ROOT,text=True,capture_output=True,check=True)
        data=json.loads(raw.stdout)
        if not data['phase2_correctness_validated'] or len(data['measurements'])!=8:
            raise RuntimeError('benchmark correctness preflight missing')
        summaries={}
        for name,m in data['measurements'].items():
            samples=m['bulk_samples'];latencies=m['service_time_ns'];count=m['operations_per_repetition']
            if len(samples)!=args.repetitions or len(latencies)!=count*args.repetitions or any(s['elapsed_ns']<=0 for s in samples):
                raise RuntimeError('incorrect executed sample count')
            if len({s['checksum'] for s in samples})!=1:
                raise RuntimeError('workload result checksum changed between repetitions')
            summaries[name]={'operations_per_repetition':count,'service_samples':len(latencies),
                'median_operations_per_second':statistics.median(count*1e9/s['elapsed_ns'] for s in samples),
                'p50_service_ns':quantile(latencies,50),'p95_service_ns':quantile(latencies,95),'p99_service_ns':quantile(latencies,99),'worst_observed_service_ns':max(latencies),
                'median_allocations_per_repetition':statistics.median(s['allocations'] for s in samples),
                'max_pmr_peak_bytes_including_setup':max(s['pmr_peak_bytes_including_setup'] for s in samples)}
        artifacts={name:{'sha256':sha(output/name),'bytes':(output/name).stat().st_size} for name in ('workload.canonical','replay.canonical')}
        if args.verify_against:
            previous=json.loads(args.verify_against.read_text())
            if previous['artifacts']!=artifacts:
                raise RuntimeError('canonical workload/replay differs from expected baseline')
        if sources!=source_hashes() or head!=command('git','rev-parse','HEAD') or status!=command('git','status','--porcelain=v1','--untracked-files=all'):
            raise RuntimeError('source or Git state changed during validation/measurement')
        cpu='unknown'
        for line in Path('/proc/cpuinfo').read_text().splitlines() if Path('/proc/cpuinfo').exists() else []:
            if line.startswith('model name'):
                cpu=line.split(':',1)[1].strip();break
        body=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
        manifest={'schema_version':1,'complete':True,'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'git':{'commit':head,'dirty':bool(status)},'source_sha256':sources,'executable_sha256':sha(exe),
            'correctness':{'ctest_outcomes':int(tests.get('tests')),'failures':0,'errors':0,'skipped':0,'benchmark_independent_reference_preflight':True,'tests_xml_sha256':sha(output/'tests.xml')},
            'provenance':{'origin':'synthetic','source':'phase2-benchmark-generator-v1','seed':args.seed,
                'dataset_versions':{'phase2-benchmark-'+n:'1' for n in ('add','cancel','execution','replay','copy-snapshot')},
                'input_container':'workload.canonical','transformation':'offline_reconstructed_book_and_replay_measurement','license_reference':'synthetic-fixture:no-external-data'},
            'artifacts':artifacts,'raw_result_sha256':hashlib.sha256(body).hexdigest(),
            'environment':{'cpu':cpu,'architecture':platform.machine(),'kernel':platform.release(),'os_release':Path('/etc/os-release').read_text(),
                'logical_cpus':os.cpu_count(),'affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
                'compiler':command(cache['CMAKE_CXX_COMPILER'],'--version'),'cmake':command('cmake','--version'),
                'generator':cache.get('CMAKE_GENERATOR'),'build_type':cache['CMAKE_BUILD_TYPE'],'flags':flags,'compile_commands':commands,
                'isolation':'shared cloud; uncontrolled scheduling/frequency','clock':'std::chrono::steady_clock','thread_count':1},
            'methodology':{'latency':'separate serial operation-wrapper service-time pass; timer/error/checksum/lifecycle overhead included; no arrival queue',
                'percentiles':'nearest-rank over all raw per-operation samples','warmup':'full untimed workload runs before each case',
                'allocations':'successful selected-PMR allocations/deallocations during bulk operation interval; setup excluded from deltas',
                'memory':'PMR live-before/after and lifetime peak INCLUDING setup; process peak RSS includes inputs/oracle/sampling/driver',
                'copy':'separate-TU by-value probes, IPO disabled; payload-only control is NOT semantically equivalent to full event',
                'timer':'raw paired-clock calibration reported; not subtracted'},
            'raw':data,'summary':summaries,
            'limitations':['no production or ultra-low-latency claim','shared-cloud finite workload, no queueing/venue latency',
                'PMR byte counts exclude allocator overhead and non-PMR driver allocations','snapshot recovery limited to Phase 1 capacities',
                'canonical artifacts are deterministic and reproducible from this code/seed; generated files remain outside Git',
                'comparison control omits metadata and is not an optimization candidate']}
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(mode='w',dir=output,prefix='.manifest-',delete=False) as stream:
                temporary=Path(stream.name);json.dump(manifest,stream,indent=2,sort_keys=True);stream.write('\n');stream.flush();os.fsync(stream.fileno())
            os.link(temporary,output/'manifest.json')
        finally:
            if temporary: temporary.unlink(missing_ok=True)
        print(json.dumps({'manifest':str(output/'manifest.json'),'sha256':sha(output/'manifest.json'),'git':manifest['git'],'summary':summaries}))
    except Exception as error:
        (output/'incomplete.json').write_text(json.dumps({'complete':False,'error_type':type(error).__name__})+'\n')
        raise

if __name__=='__main__':
    main()
