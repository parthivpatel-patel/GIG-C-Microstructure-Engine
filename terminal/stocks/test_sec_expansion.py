"""Independently authored directory,shard and amendment references;no official observations."""
import asyncio,copy,json,unittest
from unittest.mock import patch,AsyncMock
from .service import StockWorkspace
from .sec_identity import parse,URL
from .sec_history import advertised,combine,load
from .test_workspace import submissions,facts,CIK
from .test_repair import ENV
from .sec import filings
from .vintages import at_acceptance_time
class Expansion(unittest.TestCase):
 def directory(self):return {'0':{'ticker':'AAPL','title':'Authored Apple','cik_str':320193},'1':{'ticker':'APLD','title':'Authored Applied','cik_str':42},'2':{'ticker':'CRWV','title':'Authored Core','cik_str':43}}
 def workspace(self,payload):
  async def fetch(url,*_):self.urls.append(url);return json.dumps(payload(url) if callable(payload) else payload).encode()
  ticks=iter(range(100,100000,2));self.urls=[];return StockWorkspace(environment=ENV,fetcher=fetch,clock=lambda:next(ticks))
 def test_authorized_directory_promotes_only_exact_source_identity(self):
  w=self.workspace(self.directory());self.assertIsNone(w.resolve('APLD')['cik']);r=asyncio.run(w.refresh_identities());self.assertEqual(self.urls,[URL]);self.assertEqual(r['source']['classification'],'HISTORICAL_SYNTHETIC')
  for ticker,cik in [('APLD','0000000042'),('CRWV','0000000043'),('AAPL',CIK)]:self.assertEqual(w.resolve(ticker)['cik'],cik);self.assertEqual(w.search(ticker)['results'][0]['symbol'],ticker)
  self.assertFalse(w.view('CRWV')['capabilities']['equities_depth']);self.assertEqual(w.view('CRWV')['capabilities']['options_quotes'],w.view('AAPL')['capabilities']['options_quotes'])
 def test_bad_directory_and_conflicting_cached_identity_do_not_publish(self):
  for change in [lambda p:p['1'].update(cik_str=True),lambda p:p['1'].update(ticker='../evil'),lambda p:p['2'].update(ticker='APLD'),lambda p:p['0'].update(cik_str=1)]:
   p=self.directory();change(p);w=self.workspace(p)
   with self.assertRaises(ValueError):asyncio.run(w.refresh_identities())
   self.assertFalse(w.issuers);self.assertIsNone(w.issuer_source)
 def test_unconfigured_directory_never_requests_and_keeps_nulls(self):
  calls=[]
  async def fetch(*args):calls.append(args);raise AssertionError
  w=StockWorkspace(environment={},fetcher=fetch)
  with self.assertRaises(ValueError):asyncio.run(w.refresh_identities())
  self.assertFalse(calls);self.assertIsNone(w.resolve('APLD')['cik'])
 def current(self):
  p=submissions();p['filings']['files']=[{'name':'CIK'+CIK+'-submissions-001.json','filingCount':2,'filingFrom':'2024-02-01','filingTo':'2024-02-10'}];return p
 def test_advertised_history_is_bounded_fixed_host_and_overlap_deduplicated(self):
  p=self.current();w=self.workspace(lambda url:p if 'CIK'+CIK+'.json' in url else p['filings']['recent'])
  async def run():
   with patch('terminal.stocks.sec_history.asyncio.sleep',new=AsyncMock()):return await load(w,'AAPL',1)
  w.cache['AAPL']={'sec':{'financials':{'authored':True},'received_at':'2020-01-01T00:00:00Z','source_records':[{'component':'financials','url':'https://data.sec.gov/api/xbrl/companyfacts/CIK'+CIK+'.json','sha256':'a'*64}]}}
  r=asyncio.run(run());self.assertEqual(r['fundamentals']['received_at'],'2020-01-01T00:00:00Z');self.assertEqual(r['fundamentals']['response_sha256'][0],'a'*64);self.assertEqual(len(self.urls),2);self.assertTrue(all(u.startswith('https://data.sec.gov/submissions/CIK'+CIK) for u in self.urls));self.assertEqual(len(r['fundamentals']['filings']),2);self.assertEqual(r['fundamentals']['integrity']['overlap_duplicates'],2);self.assertEqual(r['fundamentals']['historical_coverage']['accepted_shards'],1)
 def test_failed_shard_keeps_entire_accepted_financial_cache(self):
  p=self.current();w=self.workspace(lambda url:p if 'CIK'+CIK+'.json' in url else {'filingDate':[]});w.cache['AAPL']={'sec':{'status':'AVAILABLE','financials':{'authored':'preserve'}}};before=copy.deepcopy(w.cache)
  async def run():
   with patch('terminal.stocks.sec_history.asyncio.sleep',new=AsyncMock()):return await load(w,'AAPL',1)
  with self.assertRaisesRegex(ValueError,'count_mismatch'):asyncio.run(run())
  self.assertEqual(w.cache,before)
 def test_shard_urls_counts_dates_and_request_limits_are_not_user_authority(self):
  for name in ['https://evil.invalid/file','../keys','CIK0000000001-submissions-001.json']:
   p=self.current();p['filings']['files'][0]['name']=name
   with self.assertRaises(ValueError):advertised(p,CIK)
  for n in (-1,3,True):
   w=self.workspace(self.current())
   with self.assertRaises(ValueError):asyncio.run(load(w,'AAPL',n))
   self.assertFalse(self.urls)
 def test_conflicting_overlap_is_not_silently_overwritten(self):
  a=filings(submissions(),CIK);b=copy.deepcopy(a);b['filings'][0]['accepted_at']='2024-02-10T13:00:00Z'
  with self.assertRaisesRegex(ValueError,'contradictory'):combine([a,b])
 def test_amendment_cutoffs_preserve_original_then_explicit_restatement(self):
  from .sec import facts as normalize
  p=facts();raw=p['facts']['us-gaap']['Revenues']['units']['USD'];original=copy.deepcopy(raw[0]);amendment={**original,'val':200,'filed':'2024-02-10','accn':'0000000123-24-000002','form':'10-K/A'};raw.append(amendment);f=normalize(p,CIK,'2024-12-31');source=filings(submissions(),CIK)['filings']
  early=at_acceptance_time(f,source,'2024-02-05T00:00:00Z');late=at_acceptance_time(f,source,'2024-02-11T00:00:00Z');self.assertEqual(early['history']['revenue'][0]['value'],'100');self.assertEqual(late['history']['revenue'][0]['value'],'200');self.assertEqual(late['history']['revenue'][0]['form'],'10-K/A')
 def test_endpoints_keep_origin_boundary_and_query_budgets(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  w=self.workspace(self.directory())
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
   for endpoint,body in [('sec-directory',{}),('sec-history',{'symbol':'AAPL','max_shards':1})]:
    self.assertEqual(c.post('/api/v1/stocks/'+endpoint,json=body,headers={'Origin':'https://evil.invalid'}).status_code,403)
   self.assertEqual(c.post('/api/v1/stocks/sec-directory',json={},headers={'Origin':'http://127.0.0.1:8787'}).status_code,200)
   self.assertEqual(c.get('/api/v1/stocks/company?symbol=CRWV').json()['instrument']['cik'],'0000000043')
 def test_acceptance_parser_cannot_accept_a_value_the_pit_filter_cannot_read(self):
  p=submissions();p['filings']['recent']['acceptanceDateTime'][0]='2024-02-01 12:00:00Z'
  with self.assertRaisesRegex(ValueError,'sec_acceptance_timestamp'):filings(p,CIK)
 def test_removed_cached_issuer_cannot_leave_financials_with_null_identity(self):
  source=self.directory();w=self.workspace(lambda url:source);asyncio.run(w.refresh_identities());w.cache['APLD']={'sec':{'authored':True}};before=copy.deepcopy(w.issuers);del source['1']
  with self.assertRaisesRegex(ValueError,'cached_issuer_change'):asyncio.run(w.refresh_identities())
  self.assertEqual(w.issuers,before);self.assertEqual(w.resolve('APLD')['cik'],'0000000042')
 def test_expanded_filings_budget_and_default_compatibility(self):
  p=submissions();recent=p['filings']['recent'];template={k:v[0] for k,v in recent.items()};p['filings']['recent']={k:[v]*1100 for k,v in template.items()};p['filings']['recent']['accessionNumber']=[f'0000000123-24-{i:06d}' for i in range(1100)]
  self.assertEqual(len(filings(p,CIK)['filings']),128);expanded=filings(p,CIK,limit=1024);self.assertEqual(len(expanded['filings']),1024);self.assertTrue(expanded['integrity']['truncated'])
  with self.assertRaises(ValueError):filings(p,CIK,limit=1025)
 def test_codespaces_new_sec_targets_still_require_one_use_endpoint_bound_proof(self):
  from terminal.server.request_proofs import RequestProofs,bootstrap_context,authorize_mutation
  origin='https://authored-8787.app.github.dev';p=RequestProofs()
  for target in ('/api/v1/stocks/sec-directory','/api/v1/stocks/sec-history'):
   read={'x-gig-bootstrap':'same-origin-v1','x-gig-browser-origin':origin,'x-gig-target':target,'sec-fetch-site':'same-origin'}
   context,_=bootstrap_context(read,[origin],origin);self.assertEqual(context['target'],target)
   h={'origin':'http://localhost:8787','host':'localhost:8787','x-forwarded-host':origin[8:],'x-forwarded-proto':'https'};self.assertIsNone(authorize_mutation(h,target,[origin],origin,p)[0]);h['x-gig-request-proof']=p.issue(origin,target);self.assertEqual(authorize_mutation(h,target,[origin],origin,p)[0],origin);self.assertIsNone(authorize_mutation(h,target,[origin],origin,p)[0])
 def test_older_cached_page_is_readable_without_new_upstream_request(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  w=StockWorkspace(environment={});row=filings(submissions(),CIK)['filings'][0];w.cache['AAPL']={'sec':{'status':'AVAILABLE','received_at':'2020-01-01T00:00:00Z','filings_received_at':'2024-01-01T00:00:00Z','filings':[dict(row) for _ in range(1024)]}}
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
   r=c.get('/api/v2/companies/AAPL/filings?offset=1000&limit=50');self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['records']),24);self.assertEqual(r.json()['observed_at'],'2024-01-01T00:00:00Z');self.assertIsNone(r.json()['next_offset']);self.assertEqual(c.get('/api/v2/companies/AAPL/filings?offset=1025').status_code,400)
