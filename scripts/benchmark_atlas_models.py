#!/usr/bin/env python3
"""Bounded authored model timing/memory observation;no network or forecast claim."""
import sys,json,time,tracemalloc,resource,platform,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.models import fit
values=[f'{(i%13-6)/1000:.6f}' for i in range(256)]
fit(values)
tracemalloc.start();times=[];hashes=set()
for _ in range(3):
    start=time.perf_counter();x=fit(values);times.append(time.perf_counter()-start)
    hashes.add(hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest())
_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();assert len(hashes)==1
print(json.dumps({'schema':'gig.atlas.phase4.model_measurement.v1','classification':'AUTHORED_DIAGNOSTIC_FITS_NOT_EMPIRICAL_FORECASTING','fixture':'mod13_returns_256','python':platform.python_version(),'architecture':platform.machine(),'warmups':1,'repetitions':3,'seconds':times,'traced_peak_bytes':peak,'process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'deterministic_output_sha256':next(iter(hashes)),'models_source_sha256':hashlib.sha256(Path(__file__).resolve().parents[1].joinpath('terminal/stocks/models.py').read_bytes()).hexdigest(),'hmm_converged':x['hmm'].get('converged'),'hmm_iterations':x['hmm'].get('iterations'),'garch_candidates':x['garch'].get('evaluated_candidates'),'limitations':['Tracemalloc overhead;small local sample,not a latency SLO','RSS includes interpreter/imports,not incremental model memory','No out-of-sample,ARM64 or observed-data performance evidence']},indent=2))
