import json,unittest,tempfile,os
from .market_catalog import MarketCatalog
class Catalog(unittest.TestCase):
 def doc(self,n=1):return {'schema':'gig.market.catalog.v1','source':{'reference':'AUTHORED_NOT_EXCHANGE_DIRECTORY','as_of':None},'assets':[{'symbol':'X'+str(i),'name':'Authored '+str(i),'exchange':'AUTHORED','asset_id':None} for i in range(n)]}
 def test_large_universe_is_bounded_searchable_without_sec_identity_or_entitlement(self):
  c=MarketCatalog(json.dumps(self.doc(10000)).encode());self.assertEqual(c.search('x9999')['results'][0]['symbol'],'X9999');self.assertEqual(c.search('')['returned'],20);self.assertEqual(c.search('')['matches'],10000);self.assertNotIn('cik',c.instrument('X1'));self.assertIsNone(c.source['as_of'])
 def test_duplicate_and_malformed_metadata_rejected(self):
  for mutate in [lambda p:p['assets'].append(p['assets'][0]),lambda p:p['assets'][0].update(symbol='bad/symbol'),lambda p:p['source'].update(as_of='not-date')]:
   p=self.doc();mutate(p)
   with self.assertRaises(ValueError):MarketCatalog(json.dumps(p).encode())
  with self.assertRaises(ValueError):MarketCatalog(b'x'*(8*1024*1024+1))
 def test_private_import_requires_permission_and_never_exposes_path(self):
  with tempfile.TemporaryDirectory() as d:
   p=d+'/catalog.json';__import__('pathlib').Path(p).write_bytes(json.dumps(self.doc()).encode());os.chmod(p,0o600);e={'GIG_MARKET_CATALOG_FILE':p};self.assertIsNotNone(MarketCatalog.configured(e).reason);e['GIG_MARKET_CATALOG_USE_APPROVED']='1';self.assertEqual(MarketCatalog.configured(e).search('')['catalog_count'],1)
 def test_required_symbols_resolve_without_claiming_sec_or_feed_entitlement(self):
  from .service import StockWorkspace
  w=StockWorkspace(environment={})
  for symbol in ('AAPL','APLD','CRWV'):
   self.assertEqual(w.catalog.search(symbol)['results'][0]['symbol'],symbol)
   v=w.view(symbol);self.assertEqual(v['instrument']['symbol'],symbol);self.assertFalse(any(v['capabilities'].values()));self.assertEqual(v['classification'],'UNAVAILABLE')
   self.assertEqual(v['instrument']['cik'],'0000320193' if symbol=='AAPL' else None)
 def test_stock_intelligence_api_routes_market_only_symbols_and_retains_aapl(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  from .service import StockWorkspace
  with TestClient(create_app(stock_workspace=StockWorkspace(environment={})),base_url='http://127.0.0.1:8787') as c:
   for symbol in ('AAPL','APLD','CRWV'):
    self.assertEqual(c.get('/api/v1/stocks/search',params={'q':symbol}).json()['results'][0]['symbol'],symbol)
    for path in ('/api/v1/stocks/company?symbol='+symbol,'/api/v2/companies/'+symbol):
     r=c.get(path);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['instrument']['symbol'],symbol)
   self.assertEqual(c.get('/api/v1/stocks/company?symbol=UNKNOWN').status_code,400)
 def test_market_only_discovery_never_sends_unverified_sec_issuer_request(self):
  import asyncio
  from .service import StockWorkspace
  from .test_repair import ENV
  calls=[]
  async def fetch(*args):calls.append(args);raise AssertionError('no request allowed')
  w=StockWorkspace(environment=ENV,fetcher=fetch)
  for symbol in ('APLD','CRWV'):
   self.assertFalse(w.view(symbol)['capabilities']['sec_refresh'])
   with self.assertRaisesRegex(ValueError,'sec_issuer_identity_unavailable'):asyncio.run(w.refresh(symbol,'sec'))
  self.assertFalse(calls)
