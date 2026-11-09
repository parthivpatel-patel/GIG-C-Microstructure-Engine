"""Independently injected source failures;never contact a market-data provider."""
import unittest
from starlette.testclient import TestClient
from terminal.server.app import create_app
from .service import StockWorkspace,AccessError
from .test_repair import ENV

class HistoricalDiagnostics(unittest.TestCase):
 def test_forbidden_is_distinguished_without_source_or_native_side_effects(self):
  calls=[]
  async def denied(*_):
   calls.append(True)
   raise AccessError('upstream_http_403')
  w=StockWorkspace(environment=ENV,fetcher=denied)
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as client:
   before=client.get('/api/v1/state').json()['book']
   reply=client.post('/api/v1/stocks/market-history',json={'symbol':'AAPL','kind':'bars','start':'2026-10-20','end':'2026-10-20'},headers={'Origin':'http://127.0.0.1:8787'})
   self.assertEqual(reply.status_code,422)
   self.assertEqual(reply.json()['error']['message'],'historical_provider_forbidden')
   self.assertEqual(len(calls),1)
   self.assertFalse(w.market_history_cache)
   self.assertEqual(client.get('/api/v1/state').json()['book'],before)
 def test_fixed_failure_categories_and_redaction(self):
  import httpx
  from .alpaca_history import failure_code
  for error,expected in [(AccessError('upstream_http_401'),'historical_credentials_rejected'),(AccessError('upstream_http_429'),'historical_rate_limited'),(AccessError('upstream_failure_cooldown'),'historical_rate_limited'),(AccessError('market_history_interval'),'historical_interval_rejected'),(AccessError('market_history_page_budget'),'historical_interval_rejected'),(TimeoutError('PRIVATE_CONTACT'),'historical_deadline'),(httpx.ReadTimeout('PRIVATE_CONTACT'),'historical_deadline'),(httpx.ConnectError('PRIVATE_CONTACT'),'historical_source_unavailable')]:
   with self.subTest(expected=expected):self.assertEqual(failure_code(error),expected)
  for error in [ValueError('SECRET_TOKEN=authored'),ValueError({'private':'do not print'}),KeyError('secret-path'),TypeError(),OverflowError('private'),ValueError('upstream_http_403 secret'),ValueError('upstream_http_403\n')]:
   with self.subTest(error_type=type(error).__name__):self.assertEqual(failure_code(error),'historical_source_configuration_or_schema_rejected')
 def test_source_errors_are_single_attempt_and_preserve_prior_accepted_cache(self):
  import httpx
  for cause,expected in [(AccessError('upstream_http_429'),'historical_rate_limited'),(httpx.ReadTimeout('PRIVATE_CONTACT'),'historical_deadline'),(httpx.ConnectError('PRIVATE_CONTACT'),'historical_source_unavailable'),(ValueError('SECRET_TOKEN'),'historical_source_configuration_or_schema_rejected')]:
   calls=[]
   async def fail(*_):calls.append(True);raise cause
   w=StockWorkspace(environment=ENV,fetcher=fail)
   # Independent untouched accepted query stands in for an earlier interval.
   w.market_history_cache['authored_previous']=(0,{'symbol':'MSFT'})
   with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as client:
    result=client.post('/api/v1/stocks/market-history',json={'symbol':'AAPL','kind':'bars','start':'2026-10-20','end':'2026-10-20'},headers={'Origin':'http://127.0.0.1:8787'})
    self.assertEqual(result.status_code,422);self.assertEqual(result.json()['error']['message'],expected);self.assertEqual(len(calls),1)
    self.assertNotIn('PRIVATE_CONTACT',result.text);self.assertNotIn('SECRET_TOKEN',result.text)
    self.assertEqual(w.market_history_cache['authored_previous'],(0,{'symbol':'MSFT'}))
 def test_interval_rejection_happens_before_any_source_call(self):
  async def forbidden(*_):raise AssertionError('must not fetch')
  w=StockWorkspace(environment=ENV,fetcher=forbidden)
  with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as client:
   r=client.post('/api/v1/stocks/market-history',json={'symbol':'AAPL','kind':'bars','start':'2020-01-01','end':'2026-10-20'},headers={'Origin':'http://127.0.0.1:8787'})
   self.assertEqual(r.status_code,422);self.assertEqual(r.json()['error']['message'],'historical_interval_rejected')
