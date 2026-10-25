#!/usr/bin/env python3
"""Reproducible authored-only exploratory parser/reconstruction measurements."""
import json
import hashlib
from pathlib import Path
import platform
import resource
import subprocess
import sys
import tempfile
import time
from lobster_synthetic import book,write
from run_lobster_validation import run


def main(parser,analysis,output):
    samples=[]
    for repeat in range(4):
        p=subprocess.run([parser,'--parser-benchmark','20000'],capture_output=True,text=True,timeout=30);assert p.returncode==0,p.stderr;r=json.loads(p.stdout);assert r['checksum']==600000 and r['errors']==40000
        if repeat:samples.append(r)
    with tempfile.TemporaryDirectory() as temp:
        messages=[];references=[]
        for i in range(1000):
            messages.extend([f'1,1,{i+1},1,100,1',f'1,3,{i+1},1,100,1']);references.extend([book(21),book(20)])
        m,mp,bp=write(Path(temp)/'authored',messages,references);runs=[]
        for repeat in range(4):
            r=run(m,mp,bp,analysis)['statistics'];assert r['rows']==r['native']==2000 and r['lower_bound_violations']==0
            if repeat:runs.append(r)
    with tempfile.TemporaryDirectory() as temp:
        bad,mp,bp=write(Path(temp)/'invalid',['invalid'],[book()]);error_samples=[]
        for repeat in range(4):
            start=time.perf_counter_ns()
            try:run(bad,mp,bp,analysis)
            except ValueError as error:
                assert 'row_index=0' in str(error)
                if repeat:error_samples.append(time.perf_counter_ns()-start)
            else:raise AssertionError('invalid fixture not refused')
    report=dict(schema='gig.lobster.synthetic_performance.v1',origin='synthetic',observed_processed=False,error_subprocess_ns=error_samples,source_commit_before_validation=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('src/lobster/adapter.cpp'),Path('src/lobster/reconstruction.cpp'),Path('examples/lobster_validate.cpp')]},architecture=platform.machine(),warmups=1,measured_repetitions=3,parser_pairs_per_repetition=20000,parser_samples=samples,analysis_rows_per_repetition=2000,analysis_samples=runs,child_maxrss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,method='Parser timer excludes fixture creation/output; analysis includes native paired reading/hashing/reference comparisons/known-subset mutations. Same-timestamp input tests capture ordering; lifetime audit lookup linear. Child maximum RSS across processes, not parent or concurrent aggregate. Shared host; no exchange-latency claim.')
    with Path(output).open('x') as f:f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(parser_pairs=20000,analysis_rows=2000,repetitions=3,max_pmr_bytes=max(x['pmr_peak_bytes'] for x in runs),child_maxrss_kib=report['child_maxrss_kib'],observed_processed=False),sort_keys=True));return report

if __name__=='__main__':main(sys.argv[1],sys.argv[2],sys.argv[3])
