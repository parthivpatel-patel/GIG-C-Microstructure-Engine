"""Independent exact references for the agreed ratio-trends feature;authored facts only."""
import copy,unittest,datetime
from fractions import Fraction
from .ratio_history import reported_history
from . import test_backend
class RatioHistory(unittest.TestCase):
 def data(self):return test_backend.FinancialMetrics().normalized()
 def test_independent_margin_growth_and_cash_references(self):
  f=self.data();before=copy.deepcopy(f);r=reported_history(f);m=r['metrics'];self.assertEqual(Fraction(**{k:int(v) for k,v in m['net_profit_margin'][0]['value'].items()}),Fraction(1,5));self.assertEqual([Fraction(int(p['value']['numerator']),int(p['value']['denominator'])) for p in m['net_profit_margin']],[Fraction(1,5),Fraction(1,5)]);self.assertEqual(m['annual_revenue_growth'][0]['value'],{'numerator':'1','denominator':'4'});self.assertEqual(m['free_cash_flow'][0]['value'],{'numerator':'20','denominator':'1'});self.assertEqual(f,before)
 def test_missing_historical_input_never_carries_forward_newer_value(self):
  r=reported_history(self.data());old=r['metrics']['gross_margin'][1];self.assertEqual(old['status'],'UNAVAILABLE');self.assertIsNone(old['value']);self.assertEqual(old['requested_period']['end'],'2022-12-31');self.assertEqual(old['period']['end'],'2022-12-31')
 def test_zero_denominator_and_conflicting_concepts_remain_unavailable(self):
  f=self.data();f['history']['revenue'][0]['value']='0';self.assertIsNone(reported_history(f)['metrics']['net_profit_margin'][0]['value']);f=self.data();f['history']['revenue'].append({**f['history']['revenue'][0],'concept':'CompetingRevenue'});self.assertEqual(reported_history(f)['metrics']['net_profit_margin'][0]['reason'],'ambiguous_accounting_concepts_revenue')
 def test_period_filters_do_not_synthesize_quarters_or_hide_instant_ratios(self):
  f=self.data();self.assertEqual(reported_history(f,'quarter')['metrics']['net_profit_margin'],[]);self.assertEqual(len(reported_history(f,'quarter')['metrics']['current_ratio']),1)
  for period,days in [('quarter',90),('ytd',180)]:
   row=copy.deepcopy(f['history']['revenue'][0]);row.update(start='2024-01-01',end=(datetime.date(2024,1,1)+datetime.timedelta(days=days-1)).isoformat(),form='10-Q');f['history']['revenue'].append(row);r=reported_history(f,period);self.assertTrue(any(p['requested_period']['end']==row['end'] for p in r['metrics']['net_profit_margin']))
 def test_output_bound_and_invalid_query(self):
  f=self.data();f['history']['assets_current']=[{**f['history']['assets_current'][0],'end':f'{year}-12-31'} for year in range(1750,2006)];r=reported_history(f);self.assertEqual(len(r['metrics']['current_ratio']),12);self.assertTrue(r['truncated_periods']['current_ratio'])
  for args in [('bad',12),('annual',13),('annual',True)]:
   with self.assertRaises(ValueError):reported_history(f,*args)
 def test_current_restated_snapshot_is_not_relabelled_as_period_end_availability(self):
  f=self.data();r=reported_history(f);old=r['metrics']['net_profit_margin'][1];self.assertEqual(old['as_of_filing_date'],'2024-12-31');self.assertIn('NOT_POINT_IN_TIME',r['availability']);self.assertEqual(old['input_facts'][0]['accession'],f['history']['revenue'][1]['accession'])
 def test_missing_prior_balance_or_growth_period_is_not_imputed(self):
  f=self.data();f['history']['assets']=[f['history']['assets'][0]];f['history']['revenue']=[f['history']['revenue'][0]];r=reported_history(f);self.assertIsNone(r['metrics']['return_on_assets'][0]['value']);self.assertIsNone(r['metrics']['annual_revenue_growth'][0]['value'])
 def test_readonly_api_no_source_request_and_query_budget(self):
  from .service import StockWorkspace
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  w=StockWorkspace(environment={},fetcher=lambda *args:None);w.cache['AAPL']={'sec':{'status':'AVAILABLE','financials':self.data()}}
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
   before=c.get('/api/v1/state').json()['book'];r=c.get('/api/v2/companies/AAPL/ratio-history');self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['metrics']),12);self.assertIsNone(c.get('/api/v2/companies/APLD/ratio-history').json()['instrument']['cik']);self.assertEqual(c.get('/api/v2/companies/AAPL/ratio-history?period=bad').status_code,422);self.assertEqual(c.get('/api/v2/companies/AAPL/ratio-history?limit=100').status_code,422);self.assertEqual(c.get('/api/v1/state').json()['book'],before)
 def test_accepted_sec_identity_is_discoverable_for_market_selection_without_feed_permission(self):
  from .service import StockWorkspace
  w=StockWorkspace(environment={});w.issuers={'PLTR':{'symbol':'PLTR','company_name':'Authored non-seed issuer','cik':'0000000042'}};w.issuer_source={'classification':'HISTORICAL_SYNTHETIC','received_at':'2024-01-01T00:00:00Z'}
  result=w.market_search('PLTR');self.assertEqual(result['results'][0]['symbol'],'PLTR');self.assertEqual(result['results'][0]['exchange'],'UNVERIFIED');self.assertIsNone(result['results'][0]['asset_id']);self.assertFalse(w.view('PLTR')['capabilities']['iex_refresh']);self.assertEqual(w.market_search('AAPL')['results'][0]['symbol'],'AAPL')
 def test_source_context_accepts_known_non_seed_identity_only_after_existing_authorization(self):
  import asyncio
  from .test_final import client,ready,packet,quote
  c=client();ready(c);c.workspace.issuers={'PLTR':{'symbol':'PLTR','company_name':'Authored non-seed issuer','cik':'0000000042'}};c.workspace.issuer_source={'classification':'HISTORICAL_SYNTHETIC','received_at':'2024-01-01T00:00:00Z'};c.symbols=('PLTR',);q=quote();q['S']='PLTR';event=c.process(packet(q))[0];self.assertEqual(event['instrument_metadata']['exchange'],'UNVERIFIED');self.assertEqual(event['origin'],'HISTORICAL_SYNTHETIC')
  async def run():
   c.workspace.environment={}
   with self.assertRaises(ValueError):await c.start(['PLTR'])
  asyncio.run(run())
 def test_analytical_concurrency_returns_bounded_busy_without_second_worker(self):
  import threading
  from concurrent.futures import ThreadPoolExecutor
  from unittest.mock import patch
  from starlette.testclient import TestClient
  from .service import StockWorkspace
  from terminal.server.app import create_app
  entered=threading.Event();release=threading.Event();original=reported_history
  def held(*args):entered.set();release.wait(5);return original(*args)
  w=StockWorkspace(environment={},fetcher=lambda *args:None);w.cache['AAPL']={'sec':{'status':'AVAILABLE','financials':self.data()}}
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c,patch('terminal.stocks.ratio_history.reported_history',held),ThreadPoolExecutor(max_workers=1) as pool:
   future=pool.submit(c.get,'/api/v2/companies/AAPL/ratio-history')
   try:self.assertTrue(entered.wait(3));self.assertEqual(c.get('/api/v2/companies/AAPL/ratio-history').status_code,429)
   finally:release.set()
   self.assertEqual(future.result(timeout=5).status_code,200)
 def test_non_seed_authorized_history_ingestion_is_not_blocked_by_curated_sec_seeds(self):
  import tempfile,asyncio,json
  from .service import StockWorkspace
  from .test_repair import ENV
  from .test_workspace import bars
  from .history_store import HistoryStore
  from .acquisition import ingest
  calls=[]
  async def fetch(url,*args):calls.append(url);p=bars();p['symbol']='PLTR';return json.dumps(p,default=float).encode()
  with tempfile.TemporaryDirectory() as d:
   w=StockWorkspace(environment=ENV,fetcher=fetch,history_store=HistoryStore(d));w.issuers={'PLTR':{'symbol':'PLTR','company_name':'Authored non-seed issuer','cik':'0000000042'}};w.issuer_source={'classification':'HISTORICAL_SYNTHETIC','received_at':None}
   result=asyncio.run(ingest(w,'PLTR','2024-01-01','2024-01-03'));self.assertEqual(result['symbol'],'PLTR');self.assertEqual(len(calls),1);self.assertEqual(w.cache,{})
 def test_generic_symbol_and_session_scope_do_not_require_curated_financial_identity(self):
  import json
  from .identity import symbol
  from .session_schedule import SessionSchedule
  self.assertEqual(symbol('XYZ123.WT'),'XYZ123.WT')
  schedule=SessionSchedule(json.dumps({'schema':'gig.session.schedule.v1','source':'AUTHORED_NOT_EXCHANGE_SCHEDULE','symbols':['PLTR'],'intervals':[{'start':'2024-01-02T14:30:00Z','end':'2024-01-02T21:00:00Z','state':'REGULAR'}]}).encode());self.assertIn('OWNER_CONFIGURED',schedule.at('PLTR','2024-01-02T15:00:00Z')['authority'])
