"""Authored directory parsing/search tiers;no downloaded identity observations."""
import sys,json,time,resource
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.sec_identity import parse
from terminal.stocks.service import StockWorkspace
payload={str(i):{'ticker':'X'+str(i),'cik_str':i+1,'title':'Authored issuer '+str(i)} for i in range(50000)}
start=time.perf_counter();rows=parse(payload);parse_seconds=time.perf_counter()-start
w=StockWorkspace(environment={});w.issuers=rows;w.issuer_source={'received_at':None};start=time.perf_counter()
for i in range(100):assert len(w.search('X49999')['results'])==1
query_seconds=time.perf_counter()-start
result={'classification':'AUTHORED_50000_ROWS_NOT_OFFICIAL_QUALIFICATION','parse_seconds':parse_seconds,'queries':100,'search_total_seconds':query_seconds,'mean_search_milliseconds':query_seconds*10,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
Path('build/development-next/directory-measurements.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
