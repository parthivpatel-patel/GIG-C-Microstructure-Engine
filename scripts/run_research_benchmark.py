#!/usr/bin/env python3
"""Archive a small exact-analytics baseline after a complete Release correctness run."""
import argparse,hashlib,json,math,platform,statistics,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--component',choices=['book','flow','simulation','execution'],default='book');a=p.parse_args()
def run(*cmd):return subprocess.check_output(cmd,cwd=ROOT,text=True)
head=run('git','rev-parse','HEAD').strip();status=run('git','status','--porcelain')
if status:raise SystemExit('baseline requires a clean code checkpoint')
build=ROOT/'build/release';cache=(build/'CMakeCache.txt').read_text()
if 'CMAKE_BUILD_TYPE:STRING=Release' not in cache or any(k+':BOOL=ON' in cache for k in ['GIG_ENABLE_ASAN','GIG_ENABLE_UBSAN','GIG_ENABLE_TSAN']):raise SystemExit('requires unsanitized Release')
if a.output.exists():raise SystemExit('refusing to overwrite evidence')
subprocess.run(['cmake','--build',str(build),'--parallel','2'],cwd=ROOT,check=True)
subprocess.run(['ctest','--test-dir',str(build),'--output-on-failure','--no-tests=error'],cwd=ROOT,check=True)
exe=build/('benchmarks/'+{'book':'gig_research_benchmark','flow':'gig_flow_benchmark','simulation':'gig_simulation_benchmark','execution':'gig_execution_benchmark'}[a.component])
with tempfile.TemporaryDirectory(prefix='gig-research-') as tmp:
 canonical=Path(tmp)/'input.canonical';raw=json.loads(run(str(exe),str(canonical)));input_canonical=canonical.read_text()
assert raw['checksum']=={'book':40000000,'flow':2400000,'simulation':132096,'execution':6480000}[a.component] and len(raw['bulk_ns'])==7 and len(raw['service_ns'])==7*raw['operations_per_repetition']
assert all(x>0 for x in raw['bulk_ns'])
v=sorted(raw['service_ns'])
result={'complete':True,'code_sha':head,'dirty':False,'origin':'synthetic','transformation':raw['case'],
'workload':{'generator':'fixed seed-book fixture v1','seed':0,'buy':[[100,10],[100,10]],'sell':[[200,10]],'depth':1,'expected_midpoint':'150/1','expected_microprice':'500/3'} if a.component=='book' else {'generator':'phase4-benchmark-v1','seed':0,'quote_times_ns':[0,7,10],'trade_time_ns':5,'window_ns':10,'horizon_ns':5,'sampling_interval_ns':10,'quote_lag_ns':0,'max_quote_age_ns':100,'complete_top_updates':True,'continuity_complete':True,'expected_ofi':'30/1','expected_effective_spread':'2/1','expected_realized_spread':'0/1'} if a.component=='flow' else {'generator':'synthetic_ioc_matching_v1','seed':1729,'makers':32,'maker_quantity':8,'maker_prices':'100+id%4','takers':128,'taker_quantity':1,'taker_limit':103,'tif':'IOC','latencies_ns':0,'expected_fills':128,'expected_submitted':384,'expected_executed_sides':256} if a.component=='simulation' else {'generator':'schedule_and_tca_v1','seed':1729,'twap_target':20,'bins':2,'start_ns':0,'end_ns':1000,'first_child_id':1000,'max_child':str((1<<64)-1),'inventory_limit':20,'side':'buy','limit_ticks':105,'maker_ask_ticks':103,'maker_quantity':10,'arrival_midpoint_ticks':100,'decision_midpoint_ticks':102,'terminal_midpoint_ticks':104,'fee_ticks_per_lot':'1/10','expected_shortfall_tick_lots':'71/1','expected_shortfall_currency':'71/100'},
'environment':{'cpu':next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),'unknown'),'architecture':platform.machine(),'os':platform.platform(),'compiler':run('c++','--version'),'cmake':run('cmake','--version'),'compile_commands':json.loads((build/'compile_commands.json').read_text()),'threads':1,'isolation':'shared cloud, uncontrolled scheduling/frequency'},
'input_canonical_kind':'simulation' if a.component in ['simulation','execution'] else 'replay','input_canonical':input_canonical,'input_sha256':hashlib.sha256(input_canonical.encode()).hexdigest(),
'provenance':{'run_id':{'book':'research-benchmark-run','flow':'flow-benchmark-run','simulation':'simulation-benchmark-run','execution':'synthetic-execution-run'}[a.component],'source_prefix':{'book':3,'flow':5,'simulation':320,'execution':4}[a.component],'parent':'embedded input_canonical journal','manifest_code_sha':head},
'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'raw':raw,
'summary':{'median_operations_per_second':statistics.median(raw['operations_per_repetition']*1e9/x for x in raw['bulk_ns']),**{f'p{q}_service_ns':v[math.ceil(len(v)*q/100)-1] for q in [50,95,99]},'worst_observed_service_ns':max(v)},
'methodology':'two warmups; seven bulk-wrapper passes; seven*operations_per_repetition separate serial service wrappers; includes exact math, error handling, checksum and clock overhead; excludes fixture/setup; no arrival queue; book calculation allocates no dynamic memory; flow PMR counts include all warmups/bulk/service passes; simulation bulk PMR counts exclude setup, peak includes setup and full-State staging; no production speed claim'}
assert run('git','rev-parse','HEAD').strip()==head and not run('git','status','--porcelain')
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result['summary']))
