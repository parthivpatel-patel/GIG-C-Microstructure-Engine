#!/usr/bin/env python3
"""Correctness-only smoke test; timings from this test are not performance evidence."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
with tempfile.TemporaryDirectory(prefix='gig-book-smoke-') as directory:
    result=subprocess.run([sys.argv[1],'16','2','1','1729',directory],text=True,capture_output=True,check=True)
    data=json.loads(result.stdout)
    if not data['phase2_correctness_validated'] or len(data['measurements'])!=8:
        raise SystemExit('benchmark correctness gate did not complete')
    for name,measurement in data['measurements'].items():
        if len(measurement['bulk_samples'])!=2 or len(measurement['service_time_ns'])!=measurement['operations_per_repetition']*2:
            raise SystemExit(f'{name}: wrong executed sample counts')
        if any(s['elapsed_ns']<=0 for s in measurement['bulk_samples']):
            raise SystemExit(f'{name}: unresolved timer samples')
    if not all((Path(directory)/name).is_file() for name in ('workload.canonical','replay.canonical')):
        raise SystemExit('missing canonical benchmark artifacts')
    bad=subprocess.run([sys.argv[1],'0','2','1','1729',directory],text=True,capture_output=True)
    if bad.returncode!=1 or 'argument out of range' not in bad.stderr:
        raise SystemExit('invalid argument not rejected correctly')
print('PASS: 8 correctness-gated workloads, sample counts, canonical artifacts and invalid CLI')
