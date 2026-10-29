import unittest,asyncio
from .service import StockWorkspace
from .discovery import search
from .directory import DirectoryService
class Discovery(unittest.TestCase):
 def test_registrants_are_indexed_without_guessing_exchange_or_merging_aliases(self):
  w=StockWorkspace(environment={});w.issuers={'NEWQ':{'company_name':'Authored New Issuer','cik':'0000000042'},'BRK-B':{'company_name':'Authored class identifier','cik':'0000000050'}};w.issuer_source={'classification':'HISTORICAL_SYNTHETIC','received_at':None}
  r=search(w,'NEWQ');self.assertEqual(r['results'][0]['exchange'],'UNVERIFIED');self.assertEqual(r['results'][0]['cik'],'0000000042');self.assertEqual(r['results'][0]['identity_kind'],'SEC_TICKER_MAPPING_ONLY');self.assertEqual(search(w,'new issuer')['results'][0]['symbol'],'NEWQ');self.assertEqual(search(w,'BRK.B')['results'],[])
 def test_ready_reference_refresh_is_automatic_for_normal_server_and_opt_in_for_injected_context(self):
  async def run():
   w=StockWorkspace(environment={});w.production_configuration=True;called=asyncio.Event()
   w.permission=lambda provider: {}
   async def refresh():called.set()
   w.refresh_identities=refresh;d=DirectoryService(w);task=asyncio.create_task(d.run());await asyncio.wait_for(called.wait(),1);task.cancel()
   with self.assertRaises(asyncio.CancelledError):await task
   self.assertEqual(d.sec_status,'ACCEPTED')
  asyncio.run(run())
 def test_replacement_invalidates_index_and_new_identifiers_enter_without_import(self):
  w=StockWorkspace(environment={});self.assertEqual(search(w,'NEWQ')['results'],[]);w.issuers={'NEWQ':{'company_name':'Authored newly accepted identifier','cik':'0000000042'}};w.issuer_source={'classification':'HISTORICAL_SYNTHETIC','received_at':None};self.assertEqual(search(w,'NEWQ')['results'][0]['symbol'],'NEWQ');w.issuers={};self.assertEqual(search(w,'NEWQ')['results'],[])
 def test_repeated_snapshot_replacement_never_reuses_stale_identity_index(self):
  w=StockWorkspace(environment={})
  for i in range(100):
   w.issuers={f'NEW{i}':{'company_name':f'Authored replacement {i}','cik':str(i+1).zfill(10)}};w.issuer_source={'classification':'HISTORICAL_SYNTHETIC'}
   r=search(w,f'NEW{i}');self.assertEqual([v['symbol'] for v in r['results']],[f'NEW{i}']);self.assertIs(w._discovery_cache[1],w.issuers)
 def test_reference_cache_reuses_receipt_until_ttl_and_optout_prevents_startup_request(self):
  import json
  from .test_repair import ENV
  async def run():
   ticks=[100];calls=[]
   async def fetch(url,*args):calls.append(url);return json.dumps({'0':{'ticker':'NEWQ','title':'Authored issuer','cik_str':42}}).encode()
   w=StockWorkspace(environment=ENV,fetcher=fetch,clock=lambda:ticks[0]);first=await w.refresh_identities();second=await w.refresh_identities();self.assertEqual(second['source'],first['source']);self.assertEqual(second['refresh'],'CACHED_ACCEPTED_REFERENCE');self.assertEqual(len(calls),1);ticks[0]=161;await w.refresh_identities();self.assertEqual(len(calls),2)
   w.production_configuration=True;w.environment={**ENV,'GIG_SEC_DIRECTORY_AUTO_REFRESH':'0'};d=DirectoryService(w);task=asyncio.create_task(d.run());await asyncio.sleep(.01);task.cancel()
   with self.assertRaises(asyncio.CancelledError):await task
   self.assertEqual(d.sec_status,'AUTOMATIC_REFRESH_DISABLED');self.assertEqual(len(calls),2)
  asyncio.run(run())
