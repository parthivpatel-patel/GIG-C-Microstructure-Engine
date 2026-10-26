#!/usr/bin/env python3
"""Bounded authored history measurement;no acquisition or production latency claim."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.history import normalize,HistorySource
from datetime import datetime,timedelta,timezone
from pathlib import Path
import time,tracemalloc,resource,json,platform,sys,hashlib
source=HistorySource('authored','single-venue','synthetic measurement','raw','HISTORICAL_SYNTHETIC','fixture_only','2024-02-01T00:00:00Z')
start=datetime(2024,1,1,tzinfo=timezone.utc)
rows=[dict(timestamp=(start+timedelta(minutes=i)).isoformat().replace('+00:00','Z'),open='100',high='101',low='99',close=str(100+i%2),volume='20') for i in range(256)]
pages=[{'bars':rows,'sha256':'a'*64}]
for _ in range(5):normalize('AAPL','1Min',pages,source)
tracemalloc.start();times=[];identities=set()
for _ in range(20):
 t=time.perf_counter();result=normalize('AAPL','1Min',pages,source);times.append(time.perf_counter()-t);identities.add(result['canonical_sha256'])
_,peak=tracemalloc.get_traced_memory();tracemalloc.stop();assert len(identities)==1
print(json.dumps({'schema':'gig.atlas.phase3.history_measurement.v1','classification':'AUTHORED_NOT_OBSERVED','architecture':platform.machine(),'python':sys.version.split()[0],'bars_per_run':256,'warmups':5,'repetitions':20,'seconds':times,'throughput_bars_per_second':5120/sum(times),'traced_peak_bytes':peak,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'canonical_sha256':next(iter(identities)),'measured_source_sha256':hashlib.sha256(Path('terminal/stocks/history.py').read_bytes()).hexdigest(),'limitations':['Tracemalloc instrumented,not production performance','Process RSS includes interpreter/imports;not incremental native journal memory','No network,exchange latency or independent machine measurement']},indent=2))
