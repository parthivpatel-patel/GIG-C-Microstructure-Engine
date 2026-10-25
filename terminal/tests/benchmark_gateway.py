"""Bounded authored single-process timing; never targets provider endpoints."""
import hashlib
import http.client
import json
import platform
from pathlib import Path
import resource
import subprocess
import time
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import gig_microstructure as gig
from terminal.server.engine import NativeSession
from terminal.server.fixtures import FIXTURE_SHA256

ROOT=Path(__file__).resolve().parents[2]
def measure():
    rows=[]
    for iteration in range(4):
        session=NativeSession();start=time.perf_counter_ns();events=0
        while session.step():events+=1
        elapsed=time.perf_counter_ns()-start
        begin=time.perf_counter_ns()
        for _ in range(100):json.dumps(session.state(),separators=(',',':'))
        snapshots=time.perf_counter_ns()-begin
        if iteration:rows.append({'events':events,'processing_ns':elapsed,'events_per_second':events*1e9/elapsed,'snapshot_serialization_calls':100,'snapshot_serialization_ns':snapshots,'pmr':session.replay.status()})
    cpu=next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),'unavailable')
    return {'schema':'gig.terminal.gateway_performance.v1','origin':'HISTORICAL_SYNTHETIC','architecture':platform.machine(),'cpu':cpu,'python':platform.python_version(),'native_build':gig.native_build_info(),'fixture_sha256':FIXTURE_SHA256,'seed':'0','warmup':1,'repetitions':3,'samples':rows,'process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'terminal/server').glob('*.py'))},'scope':'Existing native validation plus Python adapter calls; snapshot timing includes exact document encoding and metadata. RSS includes interpreter/imports, not isolated native payload. Shared-cloud sample, no latency SLA/exchange throughput claim.'}

if __name__=='__main__':print(json.dumps(measure(),indent=2))
