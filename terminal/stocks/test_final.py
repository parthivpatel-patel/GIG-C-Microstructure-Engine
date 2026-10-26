"""Independent synthetic final-program regressions;no provider network."""
import asyncio,copy,json,math,tempfile,time,unittest
from unittest.mock import patch
import msgpack
from .live import LiveIEX,ProtocolError,unpack,stamp
from .service import StockWorkspace
from .test_repair import ENV

def packet(*rows):return msgpack.packb(list(rows))
def quote():return {'T':'q','S':'AAPL','t':'2024-01-02T14:30:00.123456789Z','bp':100.,'ap':101.,'bs':4,'as':5}
def client():
 c=LiveIEX(StockWorkspace(environment={**ENV,'GIG_ALPACA_LIVE_ENABLED':'1'}),connector=lambda:None,clock=lambda:100.,wall=lambda:1704205800.1234567);c.symbols=('AAPL',);c.phase='CONNECTED_PENDING';return c

def ready(c):
 c.process(packet({'T':'success','msg':'connected'}));c.phase='AUTH_SENT';c.process(packet({'T':'success','msg':'authenticated'}));c.phase='SUBSCRIBE_SENT';c.process(packet({'T':'subscription','quotes':['AAPL'],'trades':['AAPL']}))

class Stream(unittest.TestCase):
 def test_official_handshake_and_exact_quote_metadata(self):
  c=client();ready(c);events=c.process(packet(quote()));self.assertEqual(len(events),1);self.assertEqual(events[0]['data'],{'bid':'100.0','ask':'101.0','bid_size':'4','ask_size':'5'});self.assertEqual(events[0]['source_timestamp_ns'],'1704205800123456789');self.assertEqual(c.view()['observations'][0]['state'],'SIMULATED')
 def test_duplicate_and_stale_and_disconnect(self):
  c=client();ready(c);c.process(packet(quote()));c.process(packet(quote()));self.assertEqual((c.receipts,c.duplicates),(1,1));c.clock=lambda:131.;self.assertEqual(c.view()['observations'][0]['state'],'STALE');c.phase='DISCONNECTED';self.assertEqual(c.view()['observations'][0]['state'],'UNAVAILABLE')
 def test_bad_batch_is_failure_atomic(self):
  c=client();ready(c);before=copy.deepcopy(c.view());bad=quote();bad['bp']=-1
  with self.assertRaises(ValueError):c.process(packet(quote(),bad))
  self.assertEqual(c.view(),before)
 def test_unknown_types_auth_subscription_and_symbols(self):
  for row in [{'T':'unknown'},{'T':'success','msg':'authenticated'},{'T':'error','code':409},quote()]:
   c=client()
   with self.assertRaises(ValueError):c.process(packet(row))
  c=client();ready(c);q=quote();q['S']='NVDA'
  with self.assertRaises(ValueError):c.process(packet(q))
 def test_binary_budgets_duplicate_keys_and_corruption(self):
  for raw in [b'',b'x'*32769,packet(*[{}]*129),b'\x91\x82\xa1T\xa1q\xa1T\xa1q',b'\xc1',b'\x91\x91\xc0']:
   with self.assertRaises(ValueError):unpack(raw)
 def test_nan_future_and_timestamp_precision(self):
  c=client();ready(c)
  for k,v in [('bp',float('nan')),('t','2099-01-01T00:00:00Z'),('bs',True)]:
   q=quote();q[k]=v
   with self.assertRaises((ValueError,TypeError)):c.process(packet(q))
  self.assertEqual(stamp(msgpack.Timestamp(1704205800,123456789)),'2024-01-02T14:30:00.123456789Z')
 def test_trade_does_not_touch_native_or_infer_execution(self):
  c=client();ready(c);e=c.process(packet({'T':'t','S':'AAPL','t':quote()['t'],'p':101.,'s':2,'i':7}))[0];self.assertEqual(e['kind'],'trade');self.assertNotIn('order_id',e);self.assertIn('no native book mutation',e['scope'])
 def test_gates_precede_connector_and_invalid_restart_preserves_running(self):
  c=LiveIEX(StockWorkspace(environment={}),connector=lambda *a,**k:self.fail('network'))
  with self.assertRaises(ValueError):asyncio.run(c.start(['AAPL']))
  self.assertIsNone(c.task)
 def test_full_fake_transport_auth_subscription_cleanup(self):
  sent=[];closed=[]
  class Socket:
   def __init__(self):self.i=0
   async def __aenter__(self):return self
   async def __aexit__(self,*args):closed.append(True)
   async def send(self,b):sent.append(msgpack.unpackb(b))
   async def recv(self):
    rows=[{'T':'success','msg':'connected'},{'T':'success','msg':'authenticated'},{'T':'subscription','quotes':['AAPL'],'trades':['AAPL']},quote()]
    if self.i==len(rows):await asyncio.sleep(100)
    row=rows[self.i];self.i+=1;return packet(row)
  def connection(url,**kw):self.assertEqual(url,'wss://stream.data.alpaca.markets/v2/iex');self.assertEqual(kw['max_queue'],4);return Socket()
  async def run():
   c=client();c.connector=connection;await c.start(['AAPL'])
   for _ in range(100):
    if c.receipts:break
    await asyncio.sleep(.001)
   self.assertEqual(c.receipts,1);self.assertEqual(sent[0]['action'],'auth');self.assertEqual(sent[1],{'action':'subscribe','quotes':['AAPL'],'trades':['AAPL']});await c.close();self.assertIsNone(c.task);self.assertTrue(closed)
  asyncio.run(run())
 def test_api_gates_and_foreign_origin(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  with TestClient(create_app(stock_workspace=StockWorkspace(environment={})),base_url='http://127.0.0.1:8787') as c:
   self.assertEqual(c.get('/api/v1/stocks/live').json()['state'],'DISABLED')
   self.assertEqual(c.post('/api/v1/stocks/live',json={'action':'start','symbols':['AAPL']},headers={'Origin':'https://evil.invalid'}).status_code,403)

class Numeric(unittest.TestCase):
 def test_constrained_search_monotone_independent_recursion(self):
  from .advanced_models import optimize_garch
  values=['0.01','-0.02','0.03','-0.005']*10;r=optimize_garch(values)
  self.assertGreaterEqual(r['log_likelihood'],r['grid_baseline_log_likelihood']);self.assertLess(r['alpha']+r['beta'],.995);self.assertGreater(r['omega'],0)
  h=r['initial_variance'];ll=0
  for x in map(float,values):
   ll-=math.log(2*math.pi*h)/2+(x-r['mean'])**2/(2*h);h=r['omega']+r['alpha']*(x-r['mean'])**2+r['beta']*h
  self.assertAlmostEqual(ll,r['log_likelihood'],places=10);self.assertAlmostEqual(h,r['next_variance'],places=14)
  self.assertEqual(r,optimize_garch(values));self.assertLessEqual(r['evaluations'],721)
 def test_missing_hmm_independent_transition_and_label_permutation(self):
  from .advanced_models import missing_hmm
  a=[[.8,.2],[.3,.7]];r=missing_hmm([None,None,None],[0,.1],[.01,.04],a,[.6,.4]);self.assertAlmostEqual(r['states'][1]['probabilities'][0],.6);self.assertEqual(r['observed_log_likelihood'],0)
  x=['0.01',None,'-0.02'];v=missing_hmm(x,[0,.1],[.01,.04],a,[.6,.4]);w=missing_hmm(x,[.1,0],[.04,.01],[[.7,.3],[.2,.8]],[.4,.6]);self.assertAlmostEqual(v['observed_log_likelihood'],w['observed_log_likelihood']);self.assertAlmostEqual(v['states'][-1]['probabilities'][0],w['states'][-1]['probabilities'][1])
 def test_model_boundaries_and_constant_sample(self):
  from .advanced_models import optimize_garch,missing_hmm
  self.assertFalse(optimize_garch(['0']*20)['fitted'])
  for x in [[],['nan']*20,[None]*20,['2']*20]:
   with self.assertRaises(ValueError):optimize_garch(x)
  with self.assertRaises(ValueError):missing_hmm([None],[0,0],[0,1],[[.5,.5]]*2,[.5,.5])
 def test_dataset_exact_repeating_return_alignment_and_retention(self):
  from .datasets import analyze_revisions
  from .history import normalize
  from .history_store import HistoryStore
  from .test_phase3 import source,pages,bar
  from datetime import date,timedelta
  with tempfile.TemporaryDirectory() as root:
   store=HistoryStore(root);rows=[]
   for i in range(21):rows.append(bar(str(date(2024,1,1)+timedelta(days=i))+'T14:30:00Z',close='100' if i%2 else '99'))
   first=normalize('AAPL','1Day',pages(rows),source());second=copy.deepcopy(first);second['symbol']='NVDA'
   # normalize recomputes the symbol-bound digest.
   second=normalize('NVDA','1Day',pages(rows),source());a=store.save(first)['revision'];b=store.save(second)['revision'];r=analyze_revisions(store,{'ASSET_A':a,'ASSET_B':b},{'ASSET_A':'0.6','ASSET_B':'0.4'})
   self.assertEqual(r['aligned_intervals'],20);self.assertEqual(r['analysis']['portfolio_returns'][0],{'numerator':'1','denominator':'99'});self.assertEqual(r['excluded_intervals'],{'ASSET_A':0,'ASSET_B':0})
   store.delete(a)
   with self.assertRaises(ValueError):analyze_revisions(store,{'A':a},{'A':'1'})

class Further(unittest.TestCase):
 def test_subscription_order_not_fabricated_sequence(self):
  c=client();c.symbols=('AAPL','NVDA');c.phase='SUBSCRIBE_SENT';c.process(packet({'T':'subscription','quotes':['NVDA','AAPL'],'trades':['AAPL','NVDA'],'bars':[]}));self.assertEqual(c.phase,'SUBSCRIBED')
  c.phase='SUBSCRIBE_SENT'
  with self.assertRaises(ValueError):c.process(packet({'T':'subscription','quotes':['AAPL','AAPL'],'trades':['AAPL','NVDA']}))
 def test_reconnect_restores_subscription_and_stops_in_backoff(self):
  calls=[];sent=[]
  class Socket:
   def __init__(self):self.i=0
   async def __aenter__(self):return self
   async def __aexit__(self,*a):pass
   async def send(self,b):sent.append(msgpack.unpackb(b))
   async def recv(self):
    rows=[{'T':'success','msg':'connected'},{'T':'success','msg':'authenticated'},{'T':'subscription','quotes':['AAPL'],'trades':['AAPL']},quote()]
    if self.i==4:await asyncio.sleep(100)
    r=rows[self.i];self.i+=1;return packet(r)
  def connect(*a,**k):
   calls.append(True)
   if len(calls)==1:raise OSError('fixture disconnect')
   return Socket()
  async def run():
   c=client();c.connector=connect;await c.start(['AAPL'])
   for _ in range(250):
    if c.receipts:break
    await asyncio.sleep(.01)
   self.assertEqual(c.receipts,1);self.assertEqual(c.generation,2);self.assertEqual(sent[-1]['action'],'subscribe');await c.close()
   c=client();c.connector=lambda *a,**k:(_ for _ in ()).throw(OSError());await c.start(['AAPL']);await asyncio.sleep(.01);await c.close();self.assertEqual(c.state,'STOPPED')
  asyncio.run(run())
 def test_official_vintage_never_invents_missing_older_facts(self):
  from .vintages import at_filing_date
  from .sec import facts
  from .test_workspace import facts as fixture
  f=facts(fixture(),'0000320193','2026-01-01')
  # Source rows accepted by independent existing fixture,not production-derived expected values.
  r=at_filing_date(f,'2000-01-01');self.assertTrue(all(not rows for rows in r['history'].values()));self.assertIn('PARTIAL',r['completeness'])
  with self.assertRaises(ValueError):at_filing_date(f,'2099-01-01')
 def test_new_proof_targets_exact_and_unauthorized(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  with patch.dict('os.environ',{'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787'}),TestClient(create_app(),base_url='http://127.0.0.1:8787') as c:
   for path in ['live','garch-optimization','dataset-analysis']:
    p=c.get('/api/v1/request-proof',headers={'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':'http://127.0.0.1:8787','X-GIG-Target':'/api/v1/stocks/'+path,'Sec-Fetch-Site':'same-origin'});self.assertEqual(p.status_code,200)
    self.assertEqual(c.post('/api/v1/stocks/'+path,json={},headers={'Origin':'https://evil.invalid','X-Forwarded-Host':'127.0.0.1:8787','X-Forwarded-Proto':'https'}).status_code,403)
