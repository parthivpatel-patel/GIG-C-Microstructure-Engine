#!/usr/bin/env python3
"""Independent arithmetic/quantile controls, without a performance threshold."""
import json
import subprocess
import sys
for n in (64,129):
    r=subprocess.run([sys.argv[1],str(n)],capture_output=True,text=True,check=True)
    x=json.loads(r.stdout);assert x['checksum']==n*(10000+100+1+1+1)
    durations=sorted(x['elapsed_ns']);assert len(durations)==n and all(type(v) is int and v>=0 for v in durations)
    for percent in (50,95,99):assert x[f'p{percent}_ns']==durations[(percent*n+99)//100-1]
    assert x['worst_ns']==durations[-1] and not x['clock_overhead_subtracted'] and x['seed'] is None
assert subprocess.run([sys.argv[1],'0'],capture_output=True).returncode!=0
print('decode timing arithmetic/nearest-rank controls passed; no performance gate or exchange latency claim')
