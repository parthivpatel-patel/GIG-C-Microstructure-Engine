"""Isolated authored four-symbol ingest and snapshot tiers;not network/exchange latency."""
import sys,time,json,statistics,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from terminal.stocks.test_final import client,packet,quote
symbols=('AAPL','MSFT','NVDA','TSLA');frames=[]
for i in range(10256):
 q=quote();q.update(S=symbols[i%4],bp=float(100+40*(i%4)),ap=float(101+40*(i%4)),bs=i+1);frames.append(packet(q))
trials=[]
for _ in range(3):
 c=client();c.symbols=symbols;c.generation=1
 c.process(packet({'T':'success','msg':'connected'}));c.phase='AUTH_SENT';c.process(packet({'T':'success','msg':'authenticated'}));c.phase='SUBSCRIBE_SENT';c.process(packet({'T':'subscription','quotes':list(symbols),'trades':list(symbols)}));c.state='SUBSCRIBED'
 for raw in frames[:256]:c.process(raw)
 start=time.perf_counter()
 for raw in frames[256:]:c.process(raw)
 ingest=time.perf_counter()-start;start=time.perf_counter()
 for _ in range(100):output=json.dumps(c.view(),separators=(',',':'),allow_nan=False)
 snapshots=time.perf_counter()-start
 assert c.receipts==10256 and len(c.history)==256 and len(c.seen)==256
 trials.append({'ingestion_seconds':ingest,'ingestion_events_per_second':10000/ingest,'snapshot_serialization_seconds_100':snapshots,'snapshot_serialization_mean_ms':snapshots*10,'snapshot_bytes_utf8':len(output.encode()),'retained_events':len(c.history),'accepted_receipts':c.receipts})
print(json.dumps({'schema':'gig.market.tiered.microbenchmark.v1','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'implementation':'Python IEX frame validation/context commit;not native matching engine','classification':'AUTHORED_SYNTHETIC_NO_PROVIDER_NETWORK','symbols':list(symbols),'channels':'quotes only for measurement','generator':'fixed2024 timestamp;round-robin four symbols,integer size counter,no RNG','warmup_events':256,'measured_events_per_trial':10000,'input_bytes_per_trial':sum(map(len,frames[256:])),'repetitions':3,'trials':trials,'median_ingestion_events_per_second':statistics.median(t['ingestion_events_per_second'] for t in trials),'limitations':['Ingest excludes frame generation,analytics,serialization,network and browser','Snapshot tier includes retained analytics and JSON encoding,but no transport','Shared-host short runs,no tail-latency,FPS or production throughput qualification']},indent=2))
