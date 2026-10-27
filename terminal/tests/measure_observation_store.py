"""Reproducible private authored ledger measurement;no market input or provider access."""
import sys,json,tempfile,time,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.test_observation_store import Store
from terminal.stocks.observation_store import ObservationStore
rows=Store().events(1000)
with tempfile.TemporaryDirectory() as d:
 s=ObservationStore(d);start=time.perf_counter()
 for i in range(0,len(rows),128):s.append('a'*32,rows[i:i+128])
 seconds=time.perf_counter()-start;start=time.perf_counter();recovered=ObservationStore(d).recover();recovery=time.perf_counter()-start
 result={'classification':'SINGLE_AUTHORED_X86_64_LOCAL_SQLITE_NOT_PROVIDER_BENCHMARK','events':len(rows),'append_seconds':seconds,'events_per_second':len(rows)/seconds,'verified_recovery_seconds':recovery,'recovered':len(recovered),'database_bytes':s.path.stat().st_size,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_scope':'includes interpreter,native module,fixture construction and retained reference;not isolated ledger allocation','summary':s.cached}
 Path('build/continuation/store-measurements.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
