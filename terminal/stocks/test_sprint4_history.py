"""Independent authored data/time/transport cases;no credentials or provider access."""
import asyncio,copy,datetime as dt,hashlib,json,unittest
from urllib.parse import urlsplit,parse_qs
from terminal.alpaca_wire import FixtureWire,WireResponse,WireError,decode,HTTPWire
from .historical_v2 import HistoricalClient,HistoricalPermission,validate_query,validate_plan,ns,utc

QUERY={'symbol':'AAPL','kind':'bars','feed':'iex','start':'2024-01-02T14:30:00Z','end':'2024-01-03T14:30:00Z','timeframe':'1Min','adjustment':'raw','max_pages':4}
PERMISSION=HistoricalPermission(True,True,True,True,True,'AUTHORED_TEST_PERMISSION_NOT_OWNER',('iex','sip'))
def bar(t='2024-01-02T14:30:00Z',close=100):return dict(t=t,o=close,h=close+1,l=close-1,c=close,v=10,vw=close,n=1)
def response(value,status=200,headers=None):return WireResponse(status,json.dumps(value).encode(),headers or {})
class Clock:
 def __init__(self):self.now=1704400000;self.mono=100;self.waits=[]
 def time(self):return self.now
 def monotonic(self):return self.mono
 async def sleep(self,v):self.waits.append(v);self.now+=v;self.mono+=v

class Contracts(unittest.TestCase):
 def test_exact_offsets_nanos(self):
  self.assertEqual(ns('2024-01-02T09:30:00.123456789-05:00'),ns('2024-01-02T14:30:00.123456789Z'))
  self.assertEqual(utc(ns('2024-01-02T09:30:00.123456789-05:00')),'2024-01-02T14:30:00.123456789Z')
 def test_timestamp_invalid(self):
  for v in ('2024-02-30T00:00:00Z','2024-01-02T00:00:00','2024-01-02T00:00:00-00:00','2024-01-02T00:00:60Z','2024-01-02T00:00:00+25:00','1969-12-31T23:59:59Z','2263-01-01T00:00:00Z',1,None):
   with self.subTest(v=v),self.assertRaises(WireError):ns(v)
 def test_sip_exact_delay_boundary(self):
  q={**QUERY,'feed':'sip'};end=ns(q['end'])
  self.assertEqual(validate_query(q,end+900*10**9)['feed'],'sip')
  with self.assertRaisesRegex(WireError,'minimum_delay'):validate_query(q,end+900*10**9-1)
 def test_query_validation(self):
  for patch in ({'symbol':'aapl'},{'feed':'opra'},{'max_pages':True},{'max_pages':5},{'adjustment':'guess'},{'start':QUERY['end']},{'end':'2024-02-01T00:00:00Z'},{'extra':0},{'kind':'quotes','adjustment':'split'}):
   with self.subTest(patch=patch),self.assertRaises(WireError):validate_query({**QUERY,**patch},ns('2025-01-01T00:00:00Z'))
 def test_permission_independent(self):
  for p in (HistoricalPermission(),HistoricalPermission.configured({'GIG_ALPACA_ENABLED':'1'}),HistoricalPermission(True,True,False,True,True,'x',('iex',))):
   with self.assertRaises(WireError):p.require('iex')
  with self.assertRaisesRegex(WireError,'feed_not_authorized'):HistoricalPermission(True,True,True,True,True,'authored',('iex',)).require('sip')
 def test_fixed_destination(self):
  for method,url in [('POST','https://data.alpaca.markets/v2/stocks/bars'),('GET','https://evil.invalid/v2/stocks/bars'),('GET','https://paper-api.alpaca.markets/v2/orders'),('GET','https://data.alpaca.markets/v2/stocks/bars?feed=iex&feed=sip')]:
   with self.assertRaises(WireError):validate_plan(method,url)
 def test_wire_json_and_redaction(self):
  for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'\xff',b'['*2000):
   with self.assertRaises(WireError):decode(WireResponse(200,raw))
  for status in (401,403,404,422,429,500,503):
   with self.assertRaises(WireError)as c:decode(WireResponse(status,b'owner-secret-contact'))
   self.assertNotIn('owner-secret',str(c.exception));self.assertEqual(c.exception.status,status)
 def test_wire_body_budget(self):
  with self.assertRaises(WireError):decode(WireResponse(200,b' '*524289))
 def test_disabled_http_never_reads_credentials(self):
  def denied():raise WireError('disabled')
  def secret():raise AssertionError('must not read')
  wire=HTTPWire(denied,secret,validate_plan)
  with self.assertRaisesRegex(WireError,'disabled'):asyncio.run(wire.send('GET','https://data.alpaca.markets/v2/stocks/bars'))

class Adapter(unittest.IsolatedAsyncioTestCase):
 def setUp(self):
  self.clock=Clock();self.queue=[]
  self.wire=FixtureWire(lambda *a:self.queue.pop(0));self.client=HistoricalClient(self.wire,permission=PERMISSION,clock=self.clock.time,monotonic=self.clock.monotonic,sleep=self.clock.sleep)
 def enqueue(self,rows,token=None):self.queue.append(response({'bars':{'AAPL':rows},'next_page_token':token}))
 async def test_default_disabled_no_call(self):
  c=HistoricalClient(self.wire,clock=self.clock.time)
  with self.assertRaises(WireError):await c.acquire(QUERY)
  self.assertEqual(self.wire.calls,[])
 async def test_valid_adjustment_provenance(self):
  self.enqueue([bar()]);v=await self.client.acquire({**QUERY,'adjustment':'split'})
  self.assertEqual(v['origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(v['adjustment'],'split');self.assertEqual(v['record_count'],1);self.assertFalse(v['complete_history'])
  self.assertEqual(v['session']['state'],'UNKNOWN');self.assertEqual(v['source_records'][0]['records'],1)
  q=parse_qs(urlsplit(self.wire.calls[0][1]).query);self.assertEqual(q['feed'],['iex']);self.assertEqual(q['adjustment'],['split'])
 async def test_multi_page_dedup(self):
  a=bar();b=bar('2024-01-02T14:31:00Z',101)
  self.enqueue([a],'opaque_cursor');self.enqueue([a,b]);v=await self.client.acquire(QUERY)
  self.assertEqual(v['record_count'],2);self.assertEqual(v['duplicate_records_removed'],1)
  self.assertEqual(sum(r['records']for r in v['source_records']),3)
  self.assertNotIn('opaque_cursor',json.dumps(v));self.assertGreaterEqual(sum(self.clock.waits),1)
 async def test_out_of_order_atomic(self):
  self.enqueue([bar('2024-01-02T14:31:00Z'),bar()])
  with self.assertRaisesRegex(WireError,'out_of_order'):await self.client.acquire(QUERY)
  self.assertEqual(len(self.client.cache),0)
 async def test_conflicting_same_time_bar(self):
  self.enqueue([bar(),bar(close=101)])
  with self.assertRaisesRegex(WireError,'conflicting_bar'):await self.client.acquire(QUERY)
 async def test_cursor_loop(self):
  self.enqueue([bar()],'cursor');self.enqueue([bar('2024-01-02T14:31:00Z')],'cursor')
  with self.assertRaisesRegex(WireError,'cursor_loop'):await self.client.acquire(QUERY)
  self.assertEqual(len(self.client.cache),0)
 async def test_empty_page_with_cursor(self):
  self.enqueue([],'cursor')
  with self.assertRaises(WireError):await self.client.acquire(QUERY)
 async def test_bounded_prefix(self):
  self.enqueue([bar()],'more');v=await self.client.acquire({**QUERY,'max_pages':1})
  self.assertTrue(v['has_more']);self.assertEqual(v['record_count'],1)
 async def test_429_bounded_retry(self):
  self.queue=[response({},429,{'retry-after':'1'})];self.enqueue([bar()]);v=await self.client.acquire(QUERY)
  self.assertEqual(len(self.wire.calls),2);self.assertEqual(v['record_count'],1);self.assertGreaterEqual(sum(self.clock.waits),1)
 async def test_429_exhaustion_no_publication(self):
  self.queue=[response({},429)]*3
  with self.assertRaises(WireError):await self.client.acquire(QUERY)
  self.assertEqual(len(self.wire.calls),3);self.assertFalse(self.client.cache)
 async def test_long_retry_not_waited(self):
  self.queue=[response({},429,{'retry-after':'300'})]
  with self.assertRaisesRegex(WireError,'retry_budget'):await self.client.acquire(QUERY)
  self.assertEqual(len(self.wire.calls),1)
 async def test_http_errors_never_retry_or_switch_feed(self):
  for status in (401,403,404,422,500,503):
   self.queue=[response({},status)];before=len(self.wire.calls)
   with self.assertRaises(WireError):await self.client.acquire(QUERY)
   self.assertEqual(len(self.wire.calls),before+1);self.assertFalse(self.client.cache)
 async def test_oversize_and_wrong_symbol(self):
  for v in ({'bars':{'MSFT':[bar()]}},{'bars':{'AAPL':[bar()]*65}}):
   self.queue=[response(v)]
   with self.assertRaises(WireError):await self.client.acquire(QUERY)
   self.assertFalse(self.client.cache)
 async def test_time_outside_query(self):
  self.enqueue([bar('2024-01-03T14:30:00Z')])
  with self.assertRaisesRegex(WireError,'outside_interval'):await self.client.acquire(QUERY)
 async def test_cache_expiry_delete_permission(self):
  self.enqueue([bar()]);v=await self.client.acquire(QUERY);again=await self.client.acquire(QUERY)
  self.assertEqual(len(self.wire.calls),1);self.assertEqual(again['cache_status'],'ACCEPTED_MEMORY_REFERENCE')
  self.assertEqual(self.client.accepted(v['canonical_sha256'])['symbol'],'AAPL')
  self.client.permission=HistoricalPermission()
  with self.assertRaises(WireError):self.client.accepted(v['canonical_sha256'])
  self.client.permission=PERMISSION;self.clock.mono+=60;self.client.prune();self.assertFalse(self.client.cache)
  self.enqueue([bar()]);await self.client.acquire(QUERY);self.assertEqual(self.client.delete()['deleted'],1)
 async def test_cancellation_no_partial_cache(self):
  async def hang(*a):await asyncio.sleep(100)
  self.wire.handler=hang;task=asyncio.create_task(self.client.acquire(QUERY));await asyncio.sleep(.005);task.cancel()
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertFalse(self.client.cache);self.assertFalse(self.client.lock.locked())
 async def test_quotes_keep_exact_time_and_source_metadata(self):
  self.queue=[response({'quotes':{'AAPL':[dict(t='2024-01-02T09:30:00.123456789-05:00',bp=100,ap=101,bs=2,**{'as':3},bx='V',ax='V')]}})]
  v=await self.client.acquire({**QUERY,'kind':'quotes'})
  self.assertEqual(v['records'][0]['timestamp'],'2024-01-02T14:30:00.123456789Z');self.assertEqual(v['records'][0]['wire_metadata']['bx'],'V')
 async def test_trade_identity_conflict(self):
  self.queue=[response({'trades':{'AAPL':[dict(t=QUERY['start'],p=p,s=1,i=3,x='V')for p in (100,101)]}})]
  with self.assertRaisesRegex(WireError,'trade_identity'):await self.client.acquire({**QUERY,'kind':'trades'})
 async def test_sip_does_not_issue_early_request(self):
  self.client.now_ns=lambda:ns(QUERY['end'])+900*10**9-1
  with self.assertRaisesRegex(WireError,'minimum_delay'):await self.client.acquire({**QUERY,'feed':'sip'})
  self.assertEqual(len(self.wire.calls),0)

if __name__=='__main__':unittest.main()
