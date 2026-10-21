#!/usr/bin/env python3
"""Common-code sequential engine baseline; no optimization or performance threshold."""
import argparse,hashlib,json,math,os,platform,statistics,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(*args):return subprocess.check_output(args,cwd=ROOT,text=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source_hashes():
 files=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=ROOT).split(b'\0')
 return {f.decode():sha(ROOT/f.decode()) for f in sorted(set(files)) if f and (f.decode().startswith(('include/','src/','benchmarks/','fixtures/','tests/','scripts/','cmake/')) or f.decode() in ['CMakeLists.txt','CMakePresets.json'])}
def summary(raw):
 if 'measurements' in raw:
  return {name:{'median_operations_per_second':statistics.median(m['operations_per_repetition']*1e9/s['elapsed_ns'] for s in m['bulk_samples']),**{f'p{q}_service_ns':sorted(m['service_time_ns'])[math.ceil(len(m['service_time_ns'])*q/100)-1] for q in [50,95,99]},'worst_observed_service_ns':max(m['service_time_ns'])} for name,m in raw['measurements'].items()}
 return {'median_operations_per_second':statistics.median(raw['operations_per_repetition']*1e9/x for x in raw['bulk_ns']),**{f'p{q}_service_ns':sorted(raw['service_ns'])[math.ceil(len(raw['service_ns'])*q/100)-1] for q in [50,95,99]},'worst_observed_service_ns':max(raw['service_ns'])}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--allow-dirty',action='store_true',help='development check only; archived baseline must be clean');a=p.parse_args()
 output=a.output_dir.resolve();build=ROOT/'build/release';head=run('git','rev-parse','HEAD').strip();status=run('git','status','--porcelain');initial_sources=source_hashes()
 if status and not a.allow_dirty:raise SystemExit('requires clean verified code checkpoint')
 if output.exists():raise SystemExit('refusing to overwrite existing evidence')
 if ROOT in output.parents and subprocess.run(['git','check-ignore','-q',str(output)],cwd=ROOT).returncode:raise SystemExit('output must be ignored or outside checkout')
 cache=(build/'CMakeCache.txt').read_text()
 if 'CMAKE_BUILD_TYPE:STRING=Release' not in cache or any(x+':BOOL=ON' in cache for x in ['GIG_ENABLE_ASAN','GIG_ENABLE_UBSAN','GIG_ENABLE_TSAN']):raise SystemExit('requires unsanitized Release')
 output.mkdir(parents=True)
 try:
  with (output/'validation.log').open('w') as log:
   subprocess.run(['cmake','--build',str(build),'--parallel','2'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
   subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure','--no-tests=error','--output-junit',str(output/'tests.xml')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  tests=ET.parse(output/'tests.xml').getroot();names={t.get('name') for t in tests.findall('testcase')}
  assert {'execution.independent_reference','simulation.independent_reference','analytics.flow_reference','analytics.book_reference','book.reference','replay.atomicity'}<=names
  assert not any(int(tests.get(k,'0')) for k in ['failures','errors','skipped','disabled'])
  compile_commands=json.loads((build/'compile_commands.json').read_text());flags=' '.join(x['command'] for x in compile_commands)
  if any(x in flags for x in ['-fsanitize','-flto',' -pg']):raise RuntimeError('sanitized/LTO/profile build cannot supply ordinary timing baseline')
  cases={};worker=ROOT/'scripts/measure_benchmark_child.py'
  for case,executable,args in [('book_replay_eventcopy','gig_book_benchmark',['512','7','2','1729']),('book_analytics','gig_research_benchmark',[]),('flow_analytics','gig_flow_benchmark',[]),('simulation','gig_simulation_benchmark',[]),('execution_tca','gig_execution_benchmark',[])]:
   directory=output/case;directory.mkdir();exe=build/'benchmarks'/executable
   if case=='book_replay_eventcopy':args+=[str(directory)]
   else:args=[str(directory/'input.canonical')]
   data=json.loads(run(sys.executable,str(worker),str(exe),*args));raw=data['raw']
   if case=='book_replay_eventcopy':assert raw['phase2_correctness_validated'] and len(raw['measurements'])==8
   else:
    expected={'book_analytics':40000000,'flow_analytics':2400000,'simulation':132096,'execution_tca':6480000}[case]
    assert raw['checksum']==expected and len(raw['bulk_ns'])==7 and len(raw['service_ns'])==7*raw['operations_per_repetition']
   data['summary']=summary(raw);data['artifacts']={f.name:{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(directory.iterdir()) if f.is_file()};cases[case]=data
  cpu=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown')
  sources=source_hashes();assert sources==initial_sources
  assert head==run('git','rev-parse','HEAD').strip() and status==run('git','status','--porcelain')
  manifest={'schema_version':1,'complete':True,'code_sha':head,'dirty':bool(status),'origin':'synthetic','cases':cases,'source_sha256':sources,
   'correctness':{'ctest_outcomes':int(tests.get('tests')),'failures':0,'errors':0,'skipped':0,'junit_sha256':sha(output/'tests.xml')},
   'environment':{'cpu':cpu,'architecture':platform.machine(),'os':platform.platform(),'compiler':run('c++','--version'),'cmake':run('cmake','--version'),'compile_commands':compile_commands,'affinity':sorted(os.sched_getaffinity(0)),'threads_per_engine':1,'execution':'sequential benchmarks; shared host scheduling/frequency uncontrolled'},
   'methodology':{'throughput':'median bulk-wrapper operations/s; setup/export outside interval','service_times':'separate serial wrapper pass, clock/checksum/lifecycle overhead; no external arrival queue; simulated scheduler still runs','percentiles':'nearest rank, finite observations','memory':'native_vm_hwm_bytes is post-exec /proc/self/status high-water; wait-accounted child RSS may retain inherited worker floor; both include native fixture/oracle/export/driver/proc-read, not engine-only RAM; PMR separately scoped','cpu_seconds':'whole child CPU, includes setup/preflight/export','artifacts':'deterministic canonical inputs/results regenerated from exact code/workload; generated files ignored, durable hashes retained','limitations':'no production/ultra-low-latency claim; copy control is not semantically equivalent to full event; no optimization inferred from noisy samples'}}
  with (output/'manifest.json').open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
  print(json.dumps({'code_sha':head,'dirty':bool(status),'cases':{k:{'peak_rss_bytes':v['peak_process_rss_bytes'],'summary':v['summary']} for k,v in cases.items()}}))
 except Exception as error:
  (output/'incomplete.json').write_text(json.dumps({'complete':False,'error_type':type(error).__name__})+'\n');raise
if __name__=='__main__':main()
