"""Authored submissions only;no ASGI server,listener or source network requests."""
import asyncio,copy,json,unittest
from unittest.mock import patch,AsyncMock
from .service import StockWorkspace
from .sec_history import load
from .test_workspace import submissions,CIK
from .test_repair import ENV

class SECContinuation(unittest.IsolatedAsyncioTestCase):
 def setUp(self):
  self.source=submissions();self.calls=[];self.bad=False;self.shards={}
  self.source['filings']['files']=[]
  for i in range(4):
   name=f'CIK{CIK}-submissions-{i+1:03d}.json'
   recent=copy.deepcopy(self.source['filings']['recent'])
   self.shards[name]=recent
   self.source['filings']['files'].append({'name':name,'filingCount':2,'filingFrom':'2024-02-01','filingTo':'2024-02-10'})
  async def fetch(url,*_):
   self.calls.append(url)
   raw=self.source if url.endswith(CIK+'.json') else self.shards[url.rsplit('/',1)[-1]]
   if self.bad and not url.endswith(CIK+'.json'):raw={'filingDate':[]}
   return json.dumps(raw).encode()
  self.time=1000
  def clock():self.time+=2;return self.time
  self.w=StockWorkspace(environment=ENV,fetcher=fetch,clock=clock)
  self.wait=patch('terminal.stocks.sec_history.asyncio.sleep',new=AsyncMock());self.wait.start();self.addCleanup(self.wait.stop)
 async def test_next_batches_reach_older_descriptors_without_repeating_first_shard(self):
  first=await load(self.w,'AAPL',2);c=first['fundamentals']['historical_coverage'];self.assertEqual(c['next_shard_offset'],2);self.assertEqual(len(self.calls),3)
  prior=set(self.calls[1:]);second=await load(self.w,'AAPL',2,shard_offset=2,advertisement_sha256=c['advertisement_sha256']);s=second['fundamentals']['historical_coverage']
  self.assertEqual(len(self.calls),6);self.assertFalse(prior&set(self.calls[4:]));self.assertIsNone(s['next_shard_offset']);self.assertEqual(s['remaining_shards'],0);self.assertEqual(s['accepted_shards'],2);self.assertIn('not accumulated',s['batch_policy'])
 async def test_advertisement_change_rejects_before_any_old_shard_and_preserves_cache(self):
  c=(await load(self.w,'AAPL',1))['fundamentals']['historical_coverage'];before=copy.deepcopy(self.w.cache);self.source['filings']['files'][0]['filingCount']=1;self.calls.clear()
  with self.assertRaisesRegex(ValueError,'advertisement_changed'):await load(self.w,'AAPL',1,shard_offset=1,advertisement_sha256=c['advertisement_sha256'])
  self.assertEqual(len(self.calls),1);self.assertEqual(self.w.cache,before)
 async def test_shard_failure_is_atomic_and_does_not_reset_financial_receipt(self):
  self.w.cache['AAPL']={'sec':{'financials':{'authored':True},'received_at':'2020-01-01T00:00:00Z','source_records':[{'component':'financials','url':'https://data.sec.gov/api/xbrl/companyfacts/CIK'+CIK+'.json','sha256':'a'*64}]}}
  first=await load(self.w,'AAPL',1);self.assertEqual(first['fundamentals']['received_at'],'2020-01-01T00:00:00Z');c=first['fundamentals']['historical_coverage'];before=copy.deepcopy(self.w.cache);self.bad=True
  with self.assertRaises(ValueError):await load(self.w,'AAPL',1,shard_offset=1,advertisement_sha256=c['advertisement_sha256'])
  self.assertEqual(self.w.cache,before)
 async def test_invalid_or_unbound_cursors_rejected_before_source_reads(self):
  for args in [{'shard_offset':True},{'shard_offset':129},{'shard_offset':-1},{'shard_offset':1},{'advertisement_sha256':'x'},{'advertisement_sha256':True}]:
   with self.subTest(args=args),self.assertRaises(ValueError):await load(self.w,'AAPL',1,**args)
  self.assertFalse(self.calls)
 async def test_wrong_instrument_binding_and_out_of_range_cursor_fail_closed(self):
  c=(await load(self.w,'AAPL',1))['fundamentals']['historical_coverage'];before=copy.deepcopy(self.w.cache)
  for offset in (4,128):
   with self.assertRaisesRegex(ValueError,'offset'):await load(self.w,'AAPL',1,shard_offset=offset,advertisement_sha256=c['advertisement_sha256'])
  with self.assertRaisesRegex(ValueError,'advertisement_changed'):await load(self.w,'AAPL',1,shard_offset=1,advertisement_sha256='0'*64)
  self.assertEqual(self.w.cache,before)
 async def test_old_signature_and_metadata_only_mode_remain_bounded(self):
  c=(await load(self.w,'AAPL',0))['fundamentals']['historical_coverage'];self.assertEqual(len(self.calls),1);self.assertIsNone(c['next_shard_offset']);self.assertEqual(c['accepted_shards'],0)
 async def test_disabled_permission_never_reaches_the_fetcher(self):
  self.w.environment={}
  with self.assertRaises(ValueError):await load(self.w,'AAPL',1)
  self.assertFalse(self.calls)
 async def test_public_query_admission_rejects_extra_authority_and_preserves_old_shape(self):
  from .sec_history import admit_query
  self.assertEqual(admit_query({'symbol':'AAPL','max_shards':1}),{'ticker':'AAPL','max_shards':1,'shard_offset':0,'advertisement_sha256':None})
  for data in [{'symbol':'AAPL','max_shards':1,'url':'https://evil.invalid'}, {'symbol':None,'max_shards':1},{'symbol':'AAPL'},[],None]:
   with self.subTest(data=data),self.assertRaisesRegex(ValueError,'history_query'):admit_query(data)
  value=await load(self.w,**admit_query({'symbol':'AAPL','max_shards':1}));self.assertEqual(value['instrument']['symbol'],'AAPL')
 async def test_permission_revocation_between_sources_prevents_further_reads(self):
  original=self.w.fetcher;self.w.cache['AAPL']={'sec':{'status':'PARTIAL','authored':'keep'}};before=copy.deepcopy(self.w.cache)
  async def revoke(url,*args):
   data=await original(url,*args);self.w.environment={};return data
  self.w.fetcher=revoke
  with self.assertRaises(ValueError):await load(self.w,'AAPL',1)
  self.assertEqual(len(self.calls),1);self.assertEqual(self.w.cache,before)
 async def test_immediate_next_operation_respects_shared_rate_budget_before_first_read(self):
  self.w.clock=lambda:100.;self.w.last_request=100.;waits=[]
  async def sleep(delay):waits.append(delay);self.w.last_request=0
  with patch('terminal.stocks.sec_history.asyncio.sleep',side_effect=sleep):await load(self.w,'AAPL',0)
  self.assertEqual(waits,[1.01]);self.assertEqual(len(self.calls),1)
