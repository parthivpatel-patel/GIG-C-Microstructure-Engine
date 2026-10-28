import unittest
from .service import StockWorkspace
from terminal.server.app import create_app
from starlette.testclient import TestClient
class Availability(unittest.TestCase):
 def test_identity_null_mapping_and_unknown_are_distinct(self):
  with TestClient(create_app(stock_workspace=StockWorkspace(environment={})),base_url='http://127.0.0.1:8787') as c:
   self.assertEqual(c.get('/api/v2/companies/CRWV/availability').json()['state'],'IDENTITY_FOUND_CIK_UNVERIFIED');self.assertEqual(c.get('/api/v2/companies/AAPL/availability').json()['state'],'CIK_PRESENT_FILINGS_UNAVAILABLE');self.assertEqual(c.get('/api/v2/companies/ZZZZZZZ/availability').status_code,404)
 def test_partial_facts_and_temporary_source_failure_preserve_missingness(self):
  w=StockWorkspace(environment={});w.cache['AAPL']={'sec':{'status':'AVAILABLE','filings':[{'form':'10-K'}]}}
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
   self.assertEqual(c.get('/api/v2/companies/AAPL/availability').json()['state'],'FILINGS_AVAILABLE_FACTS_UNAVAILABLE');w.cache['AAPL']['sec']['financials']={'history':{'revenue':[{'value':'100'}],'net_income':[]}};r=c.get('/api/v2/companies/AAPL/availability').json();self.assertEqual(r['financials']['available_selected_concepts'],['revenue']);self.assertEqual(r['state'],'SELECTED_REPORTED_FACTS_AVAILABLE');w.errors[('AAPL','sec')]='upstream_timeout';r=c.get('/api/v2/companies/AAPL/availability').json();self.assertEqual(r['state'],'SOURCE_TEMPORARILY_UNAVAILABLE');self.assertTrue(r['source_error_cache_preserved'])
