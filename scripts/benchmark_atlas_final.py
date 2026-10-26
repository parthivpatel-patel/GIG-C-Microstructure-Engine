#!/usr/bin/env python3
"""Authored model/codec measurements;never opens a provider connection."""
import sys,json,time,tracemalloc,resource,platform,hashlib,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.advanced_models import optimize_garch
from terminal.stocks.live import unpack
import msgpack

def main():
    values=['0.01','-0.02','0.03','-0.005']*16
    raw=msgpack.packb([{'T':'q','S':'AAPL','t':'2024-01-02T14:30:00Z','bp':100.,'ap':101.,'bs':2,'as':3}]*32)
    optimize_garch(values);unpack(raw);tracemalloc.start();timings=[]
    for _ in range(3):
        start=time.perf_counter();result=optimize_garch(values);timings.append(time.perf_counter()-start)
    start=time.perf_counter()
    for _ in range(1000):unpack(raw)
    elapsed=time.perf_counter()-start
    report={'schema':'gig.atlas.final.performance.v1','classification':'AUTHORED_NOT_MARKET_LATENCY','architecture':platform.machine(),'python':platform.python_version(),'warmups':1,'model_repetitions':3,'garch64_seconds':timings,'garch64_median_seconds':statistics.median(timings),'codec_frames':1000,'codec_rows_per_frame':32,'codec_seconds':elapsed,'codec_rows_per_second':32000/elapsed,'traced_peak_bytes':tracemalloc.get_traced_memory()[1],'process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'dataset_sha256':result['dataset_sha256'],'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path('terminal/stocks/advanced_models.py'),Path('terminal/stocks/live.py')]},'limitations':['Tracemalloc instrumentation affects timings','Codec measurement excludes transport/normalization/auth/storage','One local x86_64 process;not ARM64/exchange latency']}
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
