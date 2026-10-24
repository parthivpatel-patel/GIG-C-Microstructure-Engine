#!/usr/bin/env python3
"""Clean-code Release research-interface baseline; includes schema/ownership/native conversion overhead."""
import argparse,hashlib,json,math,os,platform,statistics,subprocess,sys,time,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args):return subprocess.check_output(args,cwd=ROOT,text=True)
def digest(data):return hashlib.sha256(data).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--build-dir',type=Path,default=ROOT/'build/python-release');p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--allow-dirty',action='store_true');a=p.parse_args()
head=run('git','rev-parse','HEAD').strip();status=run('git','status','--porcelain');build=a.build_dir.resolve();out=a.output_dir.resolve()
if status and not a.allow_dirty:raise SystemExit('requires clean code checkpoint')
if out.exists():raise SystemExit('refusing to overwrite benchmark evidence')
if ROOT in out.parents and subprocess.run(['git','check-ignore','-q',str(out)],cwd=ROOT).returncode:raise SystemExit('output must be ignored or outside checkout')
cache=(build/'CMakeCache.txt').read_text()
if 'CMAKE_BUILD_TYPE:STRING=Release' not in cache or any(k+':BOOL=ON' in cache for k in ['GIG_ENABLE_ASAN','GIG_ENABLE_UBSAN','GIG_ENABLE_TSAN']):raise SystemExit('requires unsanitized Release binding tree')
out.mkdir(parents=True)
try:
 with (out/'validation.log').open('w') as log:
  subprocess.run(['cmake','--build',str(build),'--parallel','1'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure','--no-tests=error','--output-junit',str(out/'tests.xml')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 tests=ET.parse(out/'tests.xml').getroot();names={x.get('name') for x in tests.findall('testcase')};assert {'python.research_interface','python.schema_compatibility'}<=names
 assert not any(int(tests.get(k,'0')) for k in ['failures','errors','skipped','disabled'])
 sys.path.insert(0,str(build/'python'));sys.path.insert(0,str(ROOT/'tests'))
 import gig_microstructure as gig
 import python_fixtures as f
 from gig_microstructure import _native
 if build not in Path(_native.__file__).resolve().parents:raise RuntimeError('loaded native module differs from selected build tree')
 count=256;events=[f.event(value=f.add(i+1,'0',100+i%4,2),seq=i) for i in range(count)]
 input_data=json.dumps({'rules':f.rules(),'replay_config':f.replay_config(),'events':events},sort_keys=True,separators=(',',':')).encode();(out/'input.json').write_bytes(input_data)
 bulk=[];service=[];memory=[];canonical_hash=None
 for mode in ['bulk','service']:
  for rep in range(-2 if mode=='bulk' else 0,7):
   replay=gig.Replay(f.rules(),f.replay_config());start=time.perf_counter_ns()
   for event in events:
    if mode=='service':
     before=time.perf_counter_ns();replay.apply(event);service.append(time.perf_counter_ns()-before)
    else:replay.apply(event)
   elapsed=time.perf_counter_ns()-start
   stats=replay.status()
   if rep>=0 and mode=='bulk':bulk.append(elapsed);memory.append(stats)
   snapshot=replay.snapshot('4');book=snapshot['data']['book'];assert sum(int(x['quantity']) for x in book['bids'])==512 and not book['asks']
   assert gig.as_fraction(replay.metrics('4')['data']['result']['metrics']['bid_depth'])==512
   value=digest(replay.canonical().encode());assert canonical_hash is None or value==canonical_hash;canonical_hash=value
 assert len(bulk)==7 and len(service)==1792 and all(x>0 for x in bulk)
 peak=None
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith('VmHWM:'):peak=int(line.split()[1])*1024
 assert head==run('git','rev-parse','HEAD').strip() and status==run('git','status','--porcelain')
 ordered=sorted(service)
 manifest={'schema_version':1,'complete':True,'code_sha':head,'dirty':bool(status),'origin':'synthetic','transformation':'validated_python_replay_benchmark','workload':{'generator':'python-explicit-fixture-v1','dataset':'python-synthetic','version':'1','seed':0,'orders':count,'quantity_each':2,'buy_prices':'100+i%4','streams':1,'warmup':2,'repetitions':7,'resource_budget_bytes':134217728},
 'correctness':{'ctest_outcomes':int(tests.get('tests')),'failures':0,'errors':0,'skipped':0,'input_sha256':digest(input_data),'canonical_output_sha256':canonical_hash,'expected_remaining_lots':512},
 'environment':{'cpu':next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown'),'os':platform.platform(),'architecture':platform.machine(),'python':sys.version,'native_build':gig.native_build_info(),'native_binary_sha256':digest(Path(_native.__file__).read_bytes()),'compile_commands':json.loads((build/'compile_commands.json').read_text()),'thread_count':1},
 'raw':{'bulk_ns':bulk,'service_ns':service,'selected_native_pmr_after_bulk':memory,'whole_python_process_vm_hwm_bytes':peak},
 'summary':{'median_events_per_second':statistics.median(count*1e9/x for x in bulk),**{f'p{q}_service_ns':ordered[math.ceil(len(ordered)*q/100)-1] for q in [50,95,99]},'worst_observed_service_ns':max(service)},
 'methodology':'Includes Python schema checks, immutable document normalization, native parsing/validation/book/journal; setup/fixtures/canonical/reference export outside timers. Separate bulk/serial passes; timer overhead retained. PMR is native owner only, not parser/Python heaps; VmHWM whole Python/schema/driver/native process. Shared scheduling/frequency; no C++ speedup or production claim.'}
 with (out/'manifest.json').open('x') as stream:json.dump(manifest,stream,indent=2);stream.write('\n')
 print(json.dumps(manifest['summary']))
except Exception as error:
 (out/'incomplete.json').write_text(json.dumps({'complete':False,'error_type':type(error).__name__})+'\n');raise
