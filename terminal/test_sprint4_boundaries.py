"""No sockets:exercise actual HTTP reader through an authored httpx transport."""
import asyncio,copy,hashlib,tempfile,unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import httpx
from terminal.alpaca_wire import HTTPWire,WireError,FixtureWire,WireResponse
from terminal.stocks.historical_v2 import HistoricalClient,HistoricalPermission
from terminal.stocks.test_sprint4_history import QUERY,PERMISSION,Clock,bar,response
from terminal.paper.test_alpaca import Provider,Clock as PaperClock,ACCOUNT,START,GATE,LIMITS
from terminal.paper.alpaca import PaperAuthorization,AlpacaPaperBroker
from terminal.paper.provider_workspace import PaperProviderWorkspace
from terminal.paper.store import IntentStore
from terminal.paper.contracts import canonical,PaperError

class Stream(httpx.AsyncByteStream):
 def __init__(self,chunks):self.chunks=chunks;self.yielded=0;self.closed=False
 async def __aiter__(self):
  for c in self.chunks:self.yielded+=1;yield c
 async def aclose(self):self.closed=True

class Boundary(unittest.IsolatedAsyncioTestCase):
 async def read(self,chunks,headers=None,status=200):
  self.stream=Stream(chunks);real=httpx.AsyncClient
  transport=httpx.MockTransport(lambda request:httpx.Response(status,headers=headers or {},stream=self.stream))
  with patch('httpx.AsyncClient',lambda **kw:real(transport=transport,**kw)):
   return await HTTPWire(lambda:None,lambda:{'APCA-API-KEY-ID':'AUTHORED','APCA-API-SECRET-KEY':'NOT_A_SECRET'},lambda *a:None).send('GET','https://data.alpaca.markets/v2/stocks/bars')
 async def test_unknown_length_stops_at_first_oversize_chunk(self):
  with self.assertRaisesRegex(WireError,'body_budget'):await self.read([b'x'*524288,b'y',b'NEVER_READ'])
  self.assertEqual(self.stream.yielded,2);self.assertTrue(self.stream.closed)
 async def test_declared_oversize_never_reads_body(self):
  with self.assertRaisesRegex(WireError,'body_budget'):await self.read([b'NEVER_READ'],{'Content-Length':'524289'})
  self.assertEqual(self.stream.yielded,0);self.assertTrue(self.stream.closed)
 async def test_false_small_length_bounded_and_rejected(self):
  with self.assertRaisesRegex(WireError,'body_length'):await self.read([b'ab'],{'Content-Length':'1'})
  self.assertTrue(self.stream.closed)
 async def test_compressed_response_never_expands(self):
  with self.assertRaisesRegex(WireError,'compressed_response'):await self.read([b'NEVER_READ'],{'Content-Encoding':'gzip'})
  self.assertEqual(self.stream.yielded,0)
 async def test_valid_fragmented_bytes_preserved(self):
  v=await self.read([b'{"v":"\xe2',b'\x82',b'\xac"}']);self.assertEqual(v.body,'{"v":"€"}'.encode());self.assertTrue(self.stream.closed)
 async def test_redirect_not_followed_or_authorized(self):
  v=await self.read([b''],{'Location':'https://evil.invalid'},302);self.assertEqual(v.status,302);self.assertEqual(self.stream.yielded,1)
 async def test_unexpected_credential_headers_fail_before_client(self):
  with patch('httpx.AsyncClient',side_effect=AssertionError('not reached')):
   with self.assertRaisesRegex(WireError,'credentials'):await HTTPWire(lambda:None,lambda:{'Authorization':'AUTHORED'},lambda *a:None).send('GET','https://data.alpaca.markets/v2/stocks/bars')
 async def test_authorization_checked_before_credential_callback(self):
  def denied():raise WireError('disabled')
  def credentials():raise AssertionError('not reached')
  with self.assertRaisesRegex(WireError,'disabled'):await HTTPWire(denied,credentials,lambda *a:None).send('GET','https://data.alpaca.markets/v2/stocks/bars')
 async def test_history_revoked_during_retry_no_second_request(self):
  clock=Clock();calls=[]
  wire=FixtureWire(lambda *a:calls.append(a)or response({},429))
  async def sleep(s):await clock.sleep(s);client.permission=HistoricalPermission()
  client=HistoricalClient(wire,permission=PERMISSION,clock=clock.time,monotonic=clock.monotonic,sleep=sleep)
  with self.assertRaisesRegex(WireError,'disabled'):await client.acquire(QUERY)
  self.assertEqual(len(calls),1);self.assertFalse(client.cache)
 async def test_paper_expiry_during_rate_wait_no_wire(self):
  clock=PaperClock();p=Provider(clock);wire=FixtureWire(p.call)
  auth=PaperAuthorization(GATE,True,True,True,True,True,True,True,True,ACCOUNT,START,clock.ms+1,hashlib.sha256(canonical(LIMITS.view())).hexdigest())
  with tempfile.TemporaryDirectory()as d:
   broker=AlpacaPaperBroker(IntentStore(Path(d)/'p',profile=auth.profile()),wire,authorization=auth,clock=clock.now,monotonic=clock.monotonic,sleep=clock.sleep)
   await broker._request('GET','/v2/account')
   with self.assertRaises(PaperError):await broker._request('GET','/v2/account')
   self.assertEqual(len(wire.calls),1)
 async def test_default_workspace_neither_loads_keys_nor_creates_store(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d)/'notcreated';calls=[];w=PaperProviderWorkspace(root,credential_headers=lambda:calls.append(1))
   self.assertFalse(w.readiness()['ready_for_explicit_qualification'])
   with self.assertRaises(PaperError):await w.action({'action':'start_qualified_session','confirm_paper_only':True})
   self.assertEqual(calls,[]);self.assertFalse(root.exists())
 async def test_legacy_history_cannot_bypass_specific_permission(self):
  from terminal.stocks.service import StockWorkspace
  from terminal.stocks.alpaca_history import acquire
  w=StockWorkspace(environment={})
  with self.assertRaisesRegex(WireError,'disabled'):await acquire(w,'AAPL','bars','2024-01-02','2024-01-03')
