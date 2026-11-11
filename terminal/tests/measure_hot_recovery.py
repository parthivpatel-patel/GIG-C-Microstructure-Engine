"""Deterministic offline native/XBRL microbenchmarks;not exchange latency or an SLA."""
import hashlib,json,math,platform,resource,socket,statistics,subprocess,sys,time,tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
def forbidden(*a,**k):raise AssertionError('NO_APPLICATION_OR_NETWORK_ALLOWED')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
import gig_microstructure as gig
from terminal.server.fixtures import rules,replay_config,EVENTS
from terminal.stocks.test_xbrl_collection import entry,amendment,LATE
from terminal.stocks.xbrl_collection import FilingCollection
LIMITS={'max_orders':'128','max_levels':'32','max_snapshot_depth':'20'}
WARMUP=2;REPETITIONS=10

def measured(callback):
 for _ in range(WARMUP):callback()
 samples=[];cpu=time.process_time_ns()
 for _ in range(REPETITIONS):
  begin=time.perf_counter_ns();callback();samples.append(time.perf_counter_ns()-begin)
 ordered=sorted(samples)
 return {'repetitions':REPETITIONS,'warmups':WARMUP,'wall_ns':samples,'p50_wall_ns':statistics.median(samples),'p95_wall_ns':ordered[math.ceil(.95*len(samples))-1],'p99_wall_ns':ordered[math.ceil(.99*len(samples))-1],'process_cpu_ns':time.process_time_ns()-cpu,'quantiles':'nearest rank;p95/p99=max for ten samples;no SLA or exchange-latency inference'}

def main():
 cpu=next((line.split(':',1)[1].strip()for line in Path('/proc/cpuinfo').read_text().splitlines()if line.startswith('model name')),'UNKNOWN')
 native=[];rss_before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;tracemalloc.start()
 for count in (25,100,260):
  owner=gig.Replay(rules(),replay_config(),limits=LIMITS,resource_budget_bytes='33554432');owner.run(EVENTS[:count]);image=owner.checkpoint();expected=owner.canonical()
  def restore():
   candidate=gig.Replay.restore_checkpoint(image,rules(),replay_config(),LIMITS,expected,resource_budget_bytes='33554432');assert candidate.canonical()==expected
  result=measured(restore);native.append({'accepted_events':count,'checkpoint_json_bytes':len(json.dumps(image,separators=(',',':')).encode()),'canonical_sha256':hashlib.sha256(expected.encode()).hexdigest(),'restoration':result,'native_status':owner.status()})
 entries=[entry(),amendment()];expected_selection=None
 def xbrl():
  nonlocal expected_selection
  collection=FilingCollection('0000320193');collection.ingest_batch(entries);value=collection.at_acceptance_time(LATE)
  if expected_selection is None:expected_selection=value['selection_sha256']
  assert value['selection_sha256']==expected_selection
 financial=measured(xbrl);current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
 report={'schema':'gig.offline.recovery_benchmark.v1','source_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'environment':{'system':platform.system(),'architecture':platform.machine(),'cpu':cpu,'python':platform.python_version(),'native_compiler':gig._native.__compiler__,'native_build':gig._native.__build_type__,'native_binary_sha256':hashlib.sha256(Path(gig._native.__file__).read_bytes()).hexdigest()},'fixtures':{'native_events_sha256':hashlib.sha256(json.dumps(EVENTS,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'xbrl_sha256':[hashlib.sha256(e['raw']).hexdigest()for e in entries]},'native_hot_import':native,'two_authored_xbrl_filings_and_selection':financial,'xbrl_selection_sha256':expected_selection,'python_tracemalloc':{'current_bytes':current,'peak_bytes':peak,'coverage':'Python allocations only;native PMR reported separately'},'process_maxrss_kib_before':rss_before,'process_maxrss_kib_after':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limitations':['Tiny deterministic authored fixtures,not observed market performance','Single local process;no isolated hardware or universal RPO/RTO/SLA claim','Validation/canonical equality included;no source SQLite commit in timed hot-import loop','Linux maxrss is monotonic process peak,not a delta allocation counter','Tracemalloc instrumentation affects timing','No application,listener,provider or account access']}
 print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
