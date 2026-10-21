#!/usr/bin/env python3
"""Run the scaffold baseline; emit a complete checksummed manifest, not a speed claim."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def command(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-dir', type=Path, default=ROOT / 'build/release')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--events', type=int, default=262144)
    parser.add_argument('--repetitions', type=int, default=7)
    parser.add_argument('--warmup', type=int, default=2)
    parser.add_argument('--batches', type=int, default=64)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    build = args.build_dir.resolve()
    output = args.output.resolve()
    if output.exists():
        parser.error('refusing to overwrite existing evidence')
    cache = {}
    for line in (build / 'CMakeCache.txt').read_text().splitlines():
        if line and not line.startswith(('#', '//')) and '=' in line and ':' in line.split('=',1)[0]:
            key, value = line.split('=', 1)
            cache[key.split(':', 1)[0]] = value
    if cache.get('CMAKE_BUILD_TYPE') != 'Release':
        parser.error('timing evidence requires Release')
    if any(cache.get(key) == 'ON' for key in ('GIG_ENABLE_ASAN', 'GIG_ENABLE_UBSAN', 'GIG_ENABLE_TSAN')):
        parser.error('timing evidence must not use sanitizers')
    # Reconfigure/rebuild so metadata and executable correspond to current source.
    subprocess.run(['cmake', '-S', str(ROOT), '-B', str(build)], check=True)
    subprocess.run(['cmake', '--build', str(build), '--parallel', '2'], check=True)
    subprocess.run(['ctest', '--test-dir', str(build), '--output-on-failure', '--no-tests=error'], check=True)
    exe = build / 'benchmarks/gig_validator_benchmark'
    status_before = command('git', 'status', '--porcelain=v1', '--untracked-files=all')
    head_before = command('git', 'rev-parse', 'HEAD')
    source_paths = ['include/gig/market_event.hpp', 'benchmarks/validator_benchmark.cpp',
                    'benchmarks/validator_batch.cpp', 'benchmarks/validator_batch.hpp',
                    'benchmarks/CMakeLists.txt', 'CMakeLists.txt', 'CMakePresets.json',
                    'scripts/run_benchmark.py']
    source_hashes = {p: sha(ROOT / p) for p in source_paths}
    raw = command(str(exe), str(args.events), str(args.repetitions), str(args.warmup),
                  str(args.batches), str(args.seed))
    result = json.loads(raw)
    canonical_result = json.dumps(result, sort_keys=True, separators=(',', ':')).encode()
    cpu = 'unknown'
    info = Path('/proc/cpuinfo')
    if info.exists():
        for line in info.read_text().splitlines():
            if line.startswith('model name'):
                cpu = line.split(':',1)[1].strip()
                break
    identity = Path('/etc/os-release')
    flags = {k:v for k,v in cache.items() if k.startswith('CMAKE_CXX_FLAGS') or
             k.startswith('CMAKE_EXE_LINKER_FLAGS') or k.startswith('GIG_')}
    durations = [sample['elapsed_ns'] for sample in result['samples']]
    work = result['events'] * result['batches']
    for sample in result['samples']:
        if sample['checked_count'] != result['oracle_valid_per_batch'] * result['batches']:
            raise RuntimeError('benchmark result failed independent count check')
    # No concurrent source edits may occur during a provenance-bearing run.
    if head_before != command('git','rev-parse','HEAD') or status_before != command('git','status','--porcelain=v1','--untracked-files=all'):
        raise RuntimeError('Git state changed during measurement')
    if source_hashes != {p:sha(ROOT/p) for p in source_paths}:
        raise RuntimeError('source changed during measurement')
    manifest = {
        'schema_version': 1, 'complete': True,
        'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'provenance': {'origin':'synthetic', 'source':'deterministic_fixture_generator',
                       'transformation':'measured_scaffold_validation', 'parent_artifacts':[],
                       'license':'repository synthetic fixture; no external market data'},
        'git': {'commit':head_before,'dirty':bool(status_before)},
        'source_sha256':source_hashes, 'executable_sha256':sha(exe),
        'result_sha256':hashlib.sha256(canonical_result).hexdigest(),
        'environment': {'cpu':cpu, 'architecture':platform.machine(), 'kernel':platform.release(),
                        'os_release':identity.read_text() if identity.exists() else platform.platform(),
                        'logical_cpus':os.cpu_count(), 'affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
                        'compiler':command(cache['CMAKE_CXX_COMPILER'],'--version'),
                        'compiler_path':cache['CMAKE_CXX_COMPILER'],
                        'cmake':command('cmake','--version'), 'generator':cache.get('CMAKE_GENERATOR'),
                        'build_type':cache['CMAKE_BUILD_TYPE'], 'flags':flags,
                        'compile_commands':json.loads((build/'compile_commands.json').read_text()),
                        'build_ninja_sha256':sha(build/'build.ninja') if (build/'build.ninja').exists() else None,
                        'timing_clock':'std::chrono::steady_clock',
                        'frequency_control':'not controlled', 'isolation':'shared cloud; not controlled'},
        'result':result,
        'summary': {'median_batch_elapsed_ns':statistics.median(durations),
                    'median_events_per_second':statistics.median(work*1e9/ns for ns in durations),
                    'min_batch_elapsed_ns':min(durations),'max_batch_elapsed_ns':max(durations)},
        'limitations':['validator only; no LOB/replay/analytics',
                       'batch throughput; no per-event latency percentiles',
                       'no allocation or peak-memory measurements',
                       'workload fingerprint is noncryptographic; source/result hashes provide integrity']}
    output.parent.mkdir(parents=True, exist_ok=True)
    # Publish a whole JSON document atomically without replacing prior evidence.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=output.parent, prefix='.gig-manifest-', delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(manifest, stream, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(json.dumps({'manifest':str(output),'sha256':sha(output), 'git':manifest['git'],
                      'summary':manifest['summary']}))

if __name__ == '__main__':
    main()
