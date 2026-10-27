"""Offline interleaved before/after ledger benchmark;requires trusted full Git history.
Executes this repository's fixed baseline module,never a downloaded module or data.
"""
import importlib.util,tempfile,time,statistics,json,sys,platform,subprocess,os
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
out=Path(os.environ.get('GIG_MARKET_EVIDENCE',str(root/'build/readiness')));out.mkdir(parents=True,exist_ok=True)
from terminal.stocks.observation_store import ObservationStore
from terminal.stocks.test_observation_store import Store
p=out/'baseline_store.py';p.write_bytes(subprocess.check_output(['git','show','ff41c97abbd79012ea9232eb56dfb5481e5f94c2:terminal/stocks/observation_store.py'],cwd=root));spec=importlib.util.spec_from_file_location('baseline_store',p);baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
rows=Store().events(1000);samples={'baseline':[],'repaired':[]};digests=set()
for trial in range(6):
 for name,kind in [('baseline',baseline.ObservationStore),('repaired',ObservationStore)]:
  with tempfile.TemporaryDirectory() as d:
   s=kind(d,clock=lambda:100.);start=time.perf_counter()
   for i in range(0,1000,128):s.append('a'*32,rows[i:i+128])
   elapsed=time.perf_counter()-start;digests.add(s.summary()['last_digest']);assert len(s.recover())==1000
   if trial:samples[name].append(elapsed)
assert len(digests)==1
result={'classification':'INTERLEAVED_LOCAL_AUTHORED_SQLITE_NOT_PROVIDER_OR_STATISTICAL_PERFORMANCE_GATE','baseline_sha':'ff41c97abbd79012ea9232eb56dfb5481e5f94c2','architecture':platform.machine(),'python':platform.python_version(),'events':1000,'batch_limit':128,'warmups_per_variant':1,'measured_repetitions_per_variant':5,'samples_seconds':samples,'median_seconds':{k:statistics.median(v) for k,v in samples.items()},'canonical_ledger_digests_equal':True,'conclusion':'Short shared-host filesystem trials;no production throughput or statistically significant regression/improvement claim'}
(out/'store-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
