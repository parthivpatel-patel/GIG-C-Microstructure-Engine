"""Reproducible authored-only envelope,not provider throughput or network latency."""
import argparse,asyncio,hashlib,json,os,platform,resource,statistics,subprocess,tempfile,time,tracemalloc
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.alpaca_wire import FixtureWire
from terminal.stocks.historical_v2 import HistoricalClient
from terminal.stocks.historical_research import analyze
from terminal.stocks.test_sprint4_history import Clock,QUERY,PERMISSION,bar,response
from terminal.paper.test_alpaca import Clock as PaperClock,Provider,LIMITS,GATE,START,ACCOUNT,ORDER
from terminal.paper.alpaca import AlpacaPaperBroker,PaperAuthorization
from terminal.paper.store import IntentStore
from terminal.paper.engine import PaperEngine
from terminal.paper.contracts import canonical
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
async def history():
 clock=Clock();pages=[]
 for page in range(4):
  pages.append(response({'bars':{'AAPL':[bar(f'2024-01-02T{14+(30+page*64+i)//60:02}:{(30+page*64+i)%60:02}:00.123456789Z',100+(page*64+i)%11)for i in range(64)]},'next_page_token':'page'+str(page+1)if page<3 else None}))
 wire=FixtureWire(lambda *v:pages.pop(0));client=HistoricalClient(wire,permission=PERMISSION,clock=clock.time,monotonic=clock.monotonic,sleep=clock.sleep)
 tracemalloc.start();begin=time.perf_counter();core=await client.acquire(QUERY);result=analyze(core,window=20);elapsed=time.perf_counter()-begin;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
 assert core['record_count']==256 and len(wire.calls)==4 and not pages
 return dict(rows=256,pages=4,seconds=elapsed,rows_per_second=256/elapsed,peak_traced_python_bytes=peak,retained_traced_python_bytes=current,source_sha256=core['canonical_sha256'],analysis_sha256=result['canonical_sha256'])
async def paper():
 clock=PaperClock();source=Provider(clock);auth=PaperAuthorization(GATE,True,True,True,True,True,True,True,True,ACCOUNT,START,clock.ms+900000,hashlib.sha256(canonical(LIMITS.view())).hexdigest())
 with tempfile.TemporaryDirectory()as d:
  store=IntentStore(Path(d)/'private',profile=auth.profile());wire=FixtureWire(source.call);broker=AlpacaPaperBroker(store,wire,authorization=auth,clock=clock.now,monotonic=clock.monotonic,sleep=clock.sleep,reference=lambda s:dict(symbol=s,feed='iex',origin='HISTORICAL_SYNTHETIC',at_ms=clock.ms,price_cents=10000));e=PaperEngine(store,broker,gate=GATE,limits=LIMITS,clock=clock.now)
  tracemalloc.start();begin=time.perf_counter();await e.arm_demo(True)
  for i in range(32):await e.submit('benchmark-'+str(i),ORDER);await e.cancel('benchmark-'+str(i));await e.refresh()
  elapsed=time.perf_counter()-begin;current,peak=tracemalloc.get_traced_memory();tracemalloc.stop();view=e.view()
  assert len(view['orders'])==32 and all(o['state']=='CANCELED'for o in view['orders'])and source.post_calls==32
  sizes={p.name:p.stat().st_size for p in Path(d).rglob('*')if p.is_file()}
  return dict(intents=32,fake_creates=source.post_calls,fixture_requests=len(wire.calls),seconds=elapsed,intents_per_second=32/elapsed,peak_traced_python_bytes=peak,retained_traced_python_bytes=current,private_store_bytes=sizes,canonical_view_sha256=hashlib.sha256(canonical(view)).hexdigest())
async def run():
 await history();await paper();h=[await history()for _ in range(5)];b=[await paper()for _ in range(3)]
 assert len({x['source_sha256']for x in h})==1 and len({x['analysis_sha256']for x in h})==1 and len({x['canonical_view_sha256']for x in b})==1
 value=dict(schema='gig.sprint4.offline.measurements.v1',classification='AUTHORED_FIXTURES_NOT_PROVIDER_PERFORMANCE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tracked_dirty=bool(subprocess.check_output(['git','diff','HEAD','--name-only'])),python=platform.python_version(),architecture=platform.machine(),cpu=platform.processor(),logical_cpus=os.cpu_count(),seed='fixed authored modulo11 prices;no RNG',history_warmups=1,history_repetitions=5,paper_warmups=1,paper_repetitions=3,history=h,paper=b,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitations=['Tracemalloc measures Python allocation bytes,not native/GPU memory or total allocation count.','RSS includes interpreter/imported native package;shared concurrent environment,not isolated hardware qualification.','Throttling uses deterministic virtual time;not network/provider latency.','Historical window256rows;paper32create/cancel intents,not capacity certification or crash testing.'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'history_median_rows_per_second':statistics.median(x['rows_per_second']for x in h),'paper_median_intents_per_second':statistics.median(x['intents_per_second']for x in b),'peak_rss_kib':value['process_peak_rss_kib']}))
asyncio.run(run())
