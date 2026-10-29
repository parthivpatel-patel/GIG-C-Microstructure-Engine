"""Fixed authored11k asset reference,not provider coverage or transport performance."""
import sys,time,json,resource,statistics,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.alpaca_reference import parse
from terminal.stocks.test_alpaca_data import asset
batches=[('active',[asset(f'X{i:05}',identity=i+1) for i in range(10000)]),('inactive',[asset(f'Y{i:05}','inactive',identity=i+10001) for i in range(1000)])]
samples=[]
for i in range(4):
 start=time.perf_counter();c=parse(batches,'HISTORICAL_SYNTHETIC');elapsed=time.perf_counter()-start
 if i:samples.append(elapsed)
assert len(c.rows)==11000
assert c.search_index.search('',filters={'listing_status':'INACTIVE'})['matches']==1000
out=Path(os.environ.get('GIG_MARKET_EVIDENCE','build/phase-next'));out.mkdir(parents=True,exist_ok=True)
r={'classification':'AUTHORED_ASSET_REFERENCE_NOT_OBSERVED_SOURCE_OR_PROVIDER_PERFORMANCE','accepted_identities':len(c.rows),'authored_batch_json_bytes':[len(json.dumps(rows).encode()) for _,rows in batches],'warmups':1,'repetitions':3,'parse_and_index_seconds':samples,'median_parse_and_index_seconds':statistics.median(samples),'peak_process_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'limitations':['Shared local host;no HTTP/credentials/real account reference','RSS is process high-water mark,not per-catalog bytes or long-run fragmentation']}
(out/'asset-reference-performance.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
