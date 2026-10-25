#!/usr/bin/env python3
"""Authored disclosure/model microbenchmarks,no observed data or latency gate."""
import argparse,datetime,hashlib,json,platform,resource,statistics,subprocess,sys,time,tracemalloc
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gig_microstructure as gig
from terminal.stocks.sec import facts
from terminal.stocks.options import scenario
from terminal.stocks.research import analyze
from terminal.stocks.quote_analytics import analyze as quote_analytics

def main():
    p=argparse.ArgumentParser();p.add_argument('--repetitions',type=int,default=3);p.add_argument('--iterations',type=int,default=30);a=p.parse_args()
    if not 1<=a.repetitions<=5 or not 1<=a.iterations<=100:p.error('bounded repetitions1..5,iterations1..100')
    def records(base,instant=False):
        result=[]
        for i in range(128):
            row={'val':base+i,'end':str(datetime.date(2023,1,1)+datetime.timedelta(days=i)),'filed':'2024-02-01','form':'10-K','accn':'0000000123-24-000001'}
            if not instant:row['start']='2023-01-01'
            result.append(row)
        return result
    payload={'cik':123,'facts':{'us-gaap':{tag:{'units':{'USD':records(base,instant)}} for tag,base,instant in [('Revenues',100,False),('NetIncomeLoss',20,False),('Assets',1000,True),('Liabilities',250,True)]}}}
    returns=['-0.01' if i%3==0 else '0.005' for i in range(128)];config={'spot':100,'strike':100,'years':1,'volatility':.2}
    operations={'sec_512_authored_facts':lambda:facts(payload,'0000000123','2024-12-31'),'options_153_grid':lambda:scenario(config),'research_128_returns':lambda:analyze(returns),'native_L1_quote':lambda:quote_analytics({'bid':'100','ask':'101','bid_size':'3','ask_size':'1'})}
    assert operations['native_L1_quote']()['metrics']['spread']=={'numerator':'1','denominator':'1'}
    expected=operations['sec_512_authored_facts']()['ratios']['net_margin']['value'];assert Fraction(int(expected['numerator']),int(expected['denominator']))==Fraction(147,227)
    assert abs(operations['options_153_grid']()['metrics']['price']-7.965567455405804)<1e-10
    measurements={};digests={}
    for name,operation in operations.items():
        for _ in range(5):operation()
        times=[];identities=[]
        for _ in range(a.repetitions):
            started=time.perf_counter_ns()
            for _ in range(a.iterations):result=operation()
            times.append((time.perf_counter_ns()-started)/a.iterations)
            identities.append(hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest())
        assert len(set(identities))==1
        measurements[name]={'ns_per_call':times,'median_ns_per_call':statistics.median(times)};digests[name]=identities[0]
    tracemalloc.start()
    for operation in operations.values():operation()
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    print(json.dumps({'schema':'gig.stock.benchmark.v1','classification':'HISTORICAL_SYNTHETIC','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'worktree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],text=True).strip()),'architecture':platform.machine(),'python':platform.python_version(),'native_build':gig.native_build_info(),'cpu':next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),platform.processor()),'repetitions':a.repetitions,'iterations_per_repeat':a.iterations,'warmup_calls_per_operation':5,'seed':None,'fixture_sha256':hashlib.sha256(json.dumps([payload,returns,config],sort_keys=True).encode()).hexdigest(),'measurements':measurements,'canonical_result_sha256':digests,'python_traced_peak_bytes_separate_untimed_pass':peak,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limitations':['Shared-cloud Python call timings,not network/exchange or production latency','Input construction outside timing/tracing;whole-process RSS includes imports/native module','Small repetition counts,no tail percentile or total allocation-call claim','No observed-data calibration or forecasts fitted']},indent=2))

if __name__=='__main__':main()
