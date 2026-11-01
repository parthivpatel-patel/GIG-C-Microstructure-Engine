"""Source-bound versioned API and disabled-provider negative controls."""
import copy,hashlib,json,os,tempfile,unittest
from pathlib import Path
from starlette.testclient import TestClient
from terminal.server.app import create_app
from terminal.stocks.service import StockWorkspace
from terminal.stocks.historical_v2 import HistoricalClient
from terminal.stocks.test_sprint4_history import QUERY,PERMISSION,Clock,bar,response
from terminal.alpaca_wire import FixtureWire
from terminal.paper.provider_workspace import PaperProviderWorkspace
from terminal.paper.test_alpaca import ACCOUNT,START,GATE,LIMITS,Provider,Clock as PaperClock
from terminal.paper.alpaca import PaperAuthorization
from terminal.paper.contracts import canonical

ORIGIN='http://127.0.0.1:8787'
class API(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.clock=Clock();self.calls=0
  def fetch(method,url,body):self.calls+=1;return response({'bars':{'AAPL':[bar(),bar('2024-01-02T14:31:00Z',110),bar('2024-01-02T14:32:00Z',100)]}})
  self.history=HistoricalClient(FixtureWire(fetch),permission=PERMISSION,clock=self.clock.time,monotonic=self.clock.monotonic,sleep=self.clock.sleep)
  self.paper=PaperProviderWorkspace(Path(self.temp.name)/'private')
  self.client=TestClient(create_app(stock_workspace=StockWorkspace(environment={}),historical_client=self.history,paper_provider=self.paper),base_url=ORIGIN)
 def tearDown(self):self.client.close();self.temp.cleanup()
 def post(self,path,body,origin=ORIGIN):return self.client.post('/api/v2'+path,json=body,headers={'Origin':origin})
 def test_history_and_trailing_research_source_binding(self):
  native=self.client.get('/api/v1/state').json();r=self.post('/market/history',QUERY);self.assertEqual(r.status_code,200,r.text);c=r.json()
  r=self.post('/market/research',{'revisions':[c['canonical_sha256']],'window':2});self.assertEqual(r.status_code,200,r.text);a=r.json()['analyses'][0]
  self.assertEqual(a['source_revision'],c['canonical_sha256']);self.assertEqual(a['origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(a['series'][1]['simple_return'],{'numerator':'1','denominator':'10'})
  self.assertEqual(self.client.get('/api/v1/state').json()['book'],native['book'])
 def test_export_exact_bytes_not_browser_reserialization(self):
  c=self.post('/market/history',QUERY).json();r=self.post('/market/research',{'revisions':[c['canonical_sha256']],'window':2,'export':True})
  self.assertEqual(r.status_code,200);v=r.json();self.assertEqual(hashlib.sha256(v['payload_json'].encode()).hexdigest(),v['payload_sha256']);self.assertEqual(json.loads(v['payload_json'])['source']['symbol'],'AAPL')
 def test_cache_delete_no_acquisition(self):
  c=self.post('/market/history',QUERY).json();before=self.calls;r=self.post('/market/history/cache',{'revision':c['canonical_sha256']})
  self.assertEqual(r.json()['deleted'],1);self.assertEqual(self.calls,before);self.assertEqual(self.post('/market/research',{'revisions':[c['canonical_sha256']]}).status_code,422)
 def test_proof_target_one_use_v2(self):
  target='/api/v2/market/history';h={'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':ORIGIN,'X-GIG-Target':target}
  token=self.client.get('/api/v1/request-proof',headers=h).json()['proof'];headers={'Origin':ORIGIN,'X-GIG-Request-Proof':token}
  self.assertEqual(self.client.post(target,json=QUERY,headers=headers).status_code,200);self.assertEqual(self.client.post(target,json=QUERY,headers=headers).status_code,403)
 def test_bad_origin_and_forwarded_headers_cannot_acquire(self):
  for path,body in (('/market/history',QUERY),('/paper/control',{'action':'start_qualified_session','confirm_paper_only':True})):
   r=self.client.post('/api/v2'+path,json=body,headers={'Origin':'https://evil.invalid','X-Forwarded-Host':'127.0.0.1:8787','X-Forwarded-Proto':'https'})
   self.assertEqual(r.status_code,403)
  self.assertEqual(self.calls,0)
 def test_default_paper_provider_disabled_and_no_store(self):
  r=self.client.get('/api/v2/paper/status');self.assertEqual(r.status_code,200);v=r.json();self.assertIsNone(v['session']);self.assertFalse(v['readiness']['ready_for_explicit_qualification']);self.assertFalse(v['readiness']['account_identity_disclosed'])
  self.assertEqual(self.post('/paper/control',{'action':'start_qualified_session','confirm_paper_only':True}).status_code,422);self.assertFalse((Path(self.temp.name)/'private').exists())
 def test_input_fields_no_urls_or_auth_override(self):
  self.assertEqual(self.post('/market/history',{**QUERY,'url':'https://evil.invalid'}).status_code,422)
  for v in ({'revisions':['x']},{'revisions':[]},{'revisions':['a'*64]*5},{'revisions':['a'*64],'export':'yes'}):self.assertEqual(self.post('/market/research',v).status_code,422)
  self.assertEqual(self.calls,0)
 def test_concentration_rejects_reserved_symbol_exposure(self):
  # Pure engine tests independently bind an explicit25%session profile.
  from dataclasses import replace
  from terminal.paper.engine import PaperEngine
  from terminal.paper.store import IntentStore
  from terminal.paper.fake import FakeBroker
  import asyncio
  root=Path(self.temp.name)/'concentration';store=IntentStore(root);fake=FakeBroker(store,lambda:1000);e=PaperEngine(store,fake,limits=replace(LIMITS,max_concentration_bps=2500),clock=lambda:1000)
  async def run():
   await e.arm_demo(True)
   with self.assertRaisesRegex(ValueError,'concentration'):await e.submit('x',{'symbol':'AAPL','side':'buy','quantity':'3','limit_price':'100','type':'limit','time_in_force':'day'})
  asyncio.run(run());self.assertEqual(fake.place_calls,0)
 def test_fixture_provider_session_complete_no_real_calls(self):
  clock=PaperClock();remote=Provider(clock);wire=FixtureWire(remote.call);auth=PaperAuthorization(GATE,True,True,True,True,True,True,True,True,ACCOUNT,START,clock.ms+900000,hashlib.sha256(canonical(LIMITS.view())).hexdigest())
  paper=PaperProviderWorkspace(Path(self.temp.name)/'protocol',authorization=auth,limits=LIMITS,transport=wire,clock=clock.now,monotonic=clock.monotonic,sleep=clock.sleep,reference=lambda s:dict(symbol=s,feed='iex',origin='HISTORICAL_SYNTHETIC',at_ms=clock.ms,price_cents=10000))
  client=TestClient(create_app(stock_workspace=StockWorkspace(environment={}),paper_provider=paper),base_url=ORIGIN)
  def post(v):return client.post('/api/v2/paper/control',json=v,headers={'Origin':ORIGIN})
  for v in ({'action':'start_qualified_session','confirm_paper_only':True},{'action':'arm_reviewed_limits','confirm_reviewed_limits':True},{'action':'submit','request_id':'one','intent':{'symbol':'AAPL','side':'buy','quantity':'1','limit_price':'100','type':'limit','time_in_force':'day'}},{'action':'kill_and_cancel'}):
   r=post(v);self.assertEqual(r.status_code,200,r.text)
  s=r.json()['session'];self.assertFalse(s['external_execution_enabled']);self.assertEqual(s['classification'],'HISTORICAL_SYNTHETIC');self.assertTrue(s['kill_switch']);self.assertEqual(s['orders'][0]['state'],'CANCELED');client.close()

if __name__=='__main__':unittest.main()
