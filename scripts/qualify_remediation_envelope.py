"""Bounded synthetic research-session resource measurements;no market-data input."""
import asyncio,hashlib,json,os,platform,resource,subprocess,sys,time,tracemalloc
from pathlib import Path
import argparse,threading
root=Path(__file__).resolve().parents[1];work=root
parser=argparse.ArgumentParser(description='Linux fixture-only resource qualification;never opens a provider connection.')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--native-build',type=Path,required=True)
parser.add_argument('--child',action='store_true',help=argparse.SUPPRESS)
args=parser.parse_args();out=args.output.resolve();native=args.native_build.resolve()
if sys.platform!='linux':raise SystemExit('Linux resource/wait4 qualification required;other platforms not qualified')
if args.child:
 resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024));resource.setrlimit(resource.RLIMIT_CPU,(20,22));resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024*1024,32*1024*1024))
 sys.path.insert(0,str(work));sys.path.insert(0,str(native/'python'))
 from terminal.stocks.test_final import client,ready,packet,quote
 from terminal.server.concentration import calculate
 from terminal.test_concentration import authored
 # Fixture-only code has no permission to open even a loopback/provider socket.
 from unittest.mock import patch
 started=time.perf_counter();tracemalloc.start();c=client();ready(c)
 with patch('socket.socket.connect',side_effect=AssertionError('offline_network_forbidden')):
  for i in range(5000):
   q=quote();q['bs']=i+1;c.process(packet(q))
  view=c.view();current,peak=tracemalloc.get_traced_memory();elapsed=time.perf_counter()-started
  assert len(view['history'])==256 and len(c.seen)==256 and c.evicted==4744
  assert all(r['origin']=='HISTORICAL_SYNTHETIC'for r in view['history'])
  samples=[];value=None;state=authored([2**64-1]*20,[2**64-1]*20)
  calculate(state,depth=20)
  for _ in range(5):
   begin=time.perf_counter_ns()
   for i in range(100):value=calculate(state,depth=20)
   samples.append((time.perf_counter_ns()-begin)/100)
  assert value['hhi']=={'numerator':'1','denominator':'40'}
 safe={'receipts':c.receipts,'evicted':c.evicted,'history':len(c.history),'dedup':len(c.seen)}
 result={'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'source_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)),'schema':'gig.remediation.envelope.v1','source':'AUTHORED_SYNTHETIC_ONLY','platform':platform.machine(),'input_events':5000,'source_records':safe,'elapsed_seconds':elapsed,'fixture_processing_events_per_second':5000/elapsed,'python_tracked_current_bytes':current,'python_tracked_peak_bytes':peak,'peak_process_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'cpu_user_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime,'cpu_system_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_stime,'concentration_ns_per_call':samples,'concentration_workload':'40uint64-max levels;1warmup,5samples each100calls;tracemalloc enabled','accepted_count_identity_sha256':hashlib.sha256(json.dumps(safe,sort_keys=True).encode()).hexdigest(),'limits':{'address_space_bytes':512*1024*1024,'cpu_soft_seconds':20,'cpu_hard_seconds':22,'single_output_file_bytes':32*1024*1024,'parent_wall_timeout_seconds':30},'limitations':['Not exchange throughput or one-way latency','Tracemalloc overhead/shared-host contention included;not a speedup benchmark','Virtual-address cap is not a global RSS quota;browser/native resources separate']}
 print(json.dumps(result));sys.exit(0)
env=dict(os.environ)
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):env[k]='0'
out.mkdir(parents=True,exist_ok=False)
r=subprocess.run([sys.executable,__file__,'--child','--output',str(out),'--native-build',str(native)],cwd=work,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,check=True)
x=json.loads(r.stdout);(out/'envelope.json').write_text(json.dumps(x,indent=2)+'\n');(out/'envelope.stderr').write_bytes(r.stderr)
# Separately reproduce unchanged journal scaling and zero-after-destruction ledgers.
rows=[]
for count,reset in [(128,0),(1024,0),(4096,0),(1024,128)]:
 cmd=[str(native/'benchmarks/gig_journal_memory_probe'),str(count),str(reset)]
 with (out/f'journal-{count}-{reset}.json').open('wb')as f,(out/f'journal-{count}-{reset}.stderr').open('wb')as err:
  def limits():
   resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))
   resource.setrlimit(resource.RLIMIT_CPU,(20,22))
   resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024*1024,32*1024*1024))
  p=subprocess.Popen(cmd,stdout=f,stderr=err,cwd=work,preexec_fn=limits)
  watchdog=threading.Timer(10,p.kill);watchdog.daemon=True;watchdog.start()
  try:_,status,usage=os.wait4(p.pid,0)
  finally:watchdog.cancel()
  p.returncode=os.waitstatus_to_exitcode(status);assert p.returncode==0
 x=json.loads((out/f'journal-{count}-{reset}.json').read_text());assert x['post_destroy_live_bytes']==0
 x.update(peak_process_RSS_KiB=usage.ru_maxrss,command=cmd);rows.append(x)
(out/'journal-scaling.json').write_text(json.dumps({'origin':'AUTHORED_NATIVE_STATUS_EVENTS','unchanged_native_core':True,'samples':rows,'scope':'One bounded process per case;not a speedup/tail-latency benchmark'},indent=2)+'\n')
print('PASS bounded fixture envelope and four journal ledger checks',flush=True)
