#!/usr/bin/env python3
"""Bounded authored portfolio/evaluation/private-storage measurements,no network."""
import sys,json,time,tempfile,hashlib,platform,tracemalloc,resource
from pathlib import Path
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.stocks.portfolio import analyze
from terminal.stocks.evaluation import walk_forward
from terminal.stocks.history import normalize,HistorySource
from terminal.stocks.history_store import HistoryStore
from terminal.stocks.history_backup import backup,restore
assets={f'ASSET_{i}':[f'{((j+i)%7-3)/1000:.6f}' for j in range(64)] for i in range(4)};weights={k:'0.25' for k in assets};values=assets['ASSET_0'][:60]
source=HistorySource('authored','single-venue','authored benchmark pages','raw','HISTORICAL_SYNTHETIC','fixture_only','2024-02-01T00:00:00Z')
results={};outputs=[];tracemalloc.start()
def measure(name,fn):
    fn();samples=[]
    for _ in range(3):
        t=time.perf_counter();x=fn();samples.append(time.perf_counter()-t)
    results[name]=samples;return x
portfolio=measure('portfolio_4x64_seconds',lambda:analyze({'assets':assets,'weights':weights}));evaluation=measure('walk_forward_60_seconds',lambda:walk_forward(values))
with tempfile.TemporaryDirectory(prefix='gig-atlas5-bench-') as root:
    store=HistoryStore(root)
    for i in range(8):
        rows=[]
        for j in range(64):
            p=str(100+(i+j)%17);rows.append({'timestamp':(datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(minutes=j)).isoformat().replace('+00:00','Z'),'open':p,'high':p,'low':p,'close':p,'volume':'20'})
        digest=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest();store.save(normalize('AAPL','1Min',[{'bars':rows,'sha256':digest}],source))
    t=time.perf_counter();backup_record=backup(store);results['backup_8x64_seconds']=time.perf_counter()-t;assert backup_record['revisions']==8;results['stored_revisions']=backup_record['revisions']
    measure('restore_8x64_seconds',lambda:restore(store));results['main_database_bytes']=store.path.stat().st_size
_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
print(json.dumps({'schema':'gig.atlas.phase5.measurement.v1','classification':'AUTHORED_NOT_OBSERVED','python':platform.python_version(),'architecture':platform.machine(),'warmups':1,'measured_repetitions':3,'results':results,'traced_peak_bytes':peak,'process_peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'portfolio_dataset_sha256':portfolio['dataset_sha256'],'evaluation_dataset_sha256':evaluation['dataset_sha256'],'source_sha256':{f:hashlib.sha256(Path(__file__).resolve().parents[1].joinpath('terminal/stocks',f).read_bytes()).hexdigest() for f in ('portfolio.py','evaluation.py','history_store.py','history_backup.py')},'limitations':['Tracemalloc-instrumented local measurements,not latency SLOs','Backup one observation;restore warmup plus3;no power-loss/long-run guarantee','RSS includes interpreter/imports,not incremental native memory']},indent=2))
