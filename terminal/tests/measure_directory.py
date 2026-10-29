"""Authored 50k listing/profile ingestion and search;no network or exchange data."""
import sys,time,json,resource,statistics,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.directory import parse_files,HEADERS
from terminal.stocks.test_directory import files
f=files();f['nasdaq']=('|'.join(HEADERS['nasdaq'])+'\n'+'\n'.join(f'X{i:05}|Authored industry security {i}|Q|N|N|100|N|N' for i in range(50000))+'\nFile Creation Time: 1028202616:00'+'|'*7+'\n').encode();start=time.perf_counter();c=parse_files(f);seconds=time.perf_counter()-start
results=[]
for q,reps in [('X49999',1000),('X49',100),('authored industry',100)]:
 elapsed=[]
 for warm in range(6):
  start=time.perf_counter()
  for i in range(reps):r=c.search(q,0,20)
  if warm:elapsed.append((time.perf_counter()-start)/reps*1000)
 results.append({'query':q,'matches':r['matches'],'returned':r['returned'],'queries_per_repetition':reps,'warmups':1,'repetitions':5,'median_ms_per_query':statistics.median(elapsed)})
out=Path(os.environ.get('GIG_MARKET_EVIDENCE','build/product'));out.mkdir(parents=True,exist_ok=True);v={'classification':'AUTHORED_COMPLETE_FILES_NOT_US_LISTING_IMPORT','accepted_identities':len(c.rows),'nasdaq_input_bytes':len(f['nasdaq']),'parse_and_index_seconds':seconds,'results':results,'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limitations':['In-process fixed authored names,not HTTP/server/provider latency','Shared-host observations,not a capacity guarantee or real-universe count']};(out/'directory-performance.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
