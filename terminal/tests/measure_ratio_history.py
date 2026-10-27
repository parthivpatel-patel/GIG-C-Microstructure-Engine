"""Bounded authored ratio-history profiling;no source download or credentials."""
from pathlib import Path
import sys,json,time,statistics,resource,platform,os
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.sec import TAGS,UNITS,facts
from terminal.stocks.ratio_history import reported_history
raw={'cik':320193,'facts':{'us-gaap':{}}}
for name,tags in TAGS.items():
 rows=[]
 for y in range(1750,2006):
  r={'val':100,'end':f'{y}-12-31','filed':f'{y+1}-02-01','accn':f'0000000123-{y%100:02d}-{y:06d}','form':'10-K'}
  if name not in ('assets','liabilities','equity','cash','assets_current','liabilities_current','short_term_borrowings','long_term_debt_current','long_term_debt_noncurrent'):r['start']=f'{y}-01-01'
  rows.append(r)
 raw['facts']['us-gaap'][tags[0]]={'units':{UNITS.get(name,'USD'):rows}}
n=facts(raw,'0000320193','2024-12-31');measure=[]
for i in range(6):
 start=time.perf_counter();result=reported_history(n);seconds=time.perf_counter()-start
 if i:measure.append(seconds)
assert all(len(v)<=12 for v in result['metrics'].values())
output={'classification':'AUTHORED_256_PERIOD_NORMALIZED_INPUT_NOT_SEC_QUALIFICATION','python':platform.python_version(),'architecture':platform.machine(),'input_selected_facts':sum(len(v) for v in n['history'].values()),'warmups':1,'measured_repetitions':5,'seconds':measure,'median_seconds':statistics.median(measure),'encoded_response_bytes':len(json.dumps(result,separators=(',',':')).encode()),'output_points':sum(len(v) for v in result['metrics'].values()),'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
out=Path(os.environ.get('GIG_MARKET_EVIDENCE','build/scope-audit'));out.mkdir(parents=True,exist_ok=True)
(out/'ratio-performance.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
