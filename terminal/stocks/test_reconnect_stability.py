"""Fake sockets and clocks only:no listener,provider client or account connection."""
import asyncio,unittest
from unittest.mock import patch
from .live import LiveIEX,ProtocolError
from .service import StockWorkspace
from .test_repair import ENV
from .test_final import packet,quote

class FakeSocket:
 def __init__(self,owner,number,stable=False):self.owner=owner;self.number=number;self.index=0;self.stable=stable
 async def __aenter__(self):return self
 async def __aexit__(self,*_):pass
 async def send(self,_):pass
 async def recv(self):
  self.index+=1
  if self.index==1:return packet({'T':'success','msg':'connected'})
  if self.index==2:return packet({'T':'success','msg':'authenticated'})
  if self.index==3:return packet({'T':'subscription','quotes':['AAPL'],'trades':['AAPL']})
  if self.index==4:
   self.owner.time+=31 if self.stable else .1
   q=quote();q['bp']=100.+self.number;q['ap']=101.+self.number;return packet(q)
  raise OSError('AUTHORED_DISCONNECT')

class ReconnectStability(unittest.IsolatedAsyncioTestCase):
 def client(self,stable_at=None):
  self.time=100.;self.calls=0
  def connect(*_a,**_k):
   self.calls+=1
   if self.calls>5:raise ProtocolError('fixture_infinite_retry_guard')
   return FakeSocket(self,self.calls,self.calls==stable_at)
  c=LiveIEX(StockWorkspace(environment={**ENV,'GIG_ALPACA_IEX_STREAM_ENABLED':'1'}),connector=connect,clock=lambda:self.time,wall=lambda:1704205800.1234567,retry_budget=2)
  c.symbols=('AAPL',);return c
 async def test_one_valid_quote_per_flap_cannot_reset_the_retry_budget(self):
  c=self.client()
  with patch('terminal.stocks.retry.retry_delay',return_value=0):await c.run()
  self.assertEqual(self.calls,2)
  self.assertEqual(c.reason,'retry_budget_exhausted');self.assertEqual(c.failures,2)
  self.assertEqual(c.receipts,2);self.assertEqual(c.view()['phase'],'DISCONNECTED')
  self.assertTrue(all(r['state']=='UNAVAILABLE'for r in c.view()['history']))
 async def test_stable_subscription_can_reset_prior_transient_failures(self):
  c=self.client(stable_at=2)
  with patch('terminal.stocks.retry.retry_delay',return_value=0):await c.run()
  self.assertEqual(self.calls,3);self.assertEqual(c.reason,'retry_budget_exhausted');self.assertEqual(c.receipts,3)
 async def test_stability_setting_is_bounded_not_an_implicit_timing_assumption(self):
  for value in (0,301,True,float('nan'),float('inf'),'30'):
   with self.subTest(value=value),self.assertRaisesRegex(ValueError,'stability_budget'):LiveIEX(StockWorkspace(environment={}),stable_seconds=value)
  c=self.client();self.assertEqual(c.view()['retry_policy']['reset_after_stable_subscribed_seconds'],30)
 async def test_failed_or_disabled_authorization_still_never_opens_a_socket(self):
  called=[]
  c=LiveIEX(StockWorkspace(environment={}),connector=lambda *a,**k:called.append(True))
  await c.run();self.assertFalse(called);self.assertEqual(c.reason,'protocol_or_authorization_rejected')
 async def test_quiet_stable_socket_resets_retry_count_without_faking_observations(self):
  owner=self;c=self.client();c.failures=1;observed=[]
  class Quiet(FakeSocket):
   async def recv(self):
    if self.index<3:return await super().recv()
    if self.index==3:
     self.index+=1;owner.time+=31;raise asyncio.TimeoutError()
    observed.append(c.failures);c.stop_event.set();raise OSError('AUTHORED_STOP')
  c.connector=lambda *a,**k:Quiet(self,1)
  with patch('terminal.stocks.retry.retry_delay',return_value=0):await c.run()
  self.assertEqual(observed,[0]);self.assertEqual(c.receipts,0);self.assertEqual(c.history,[])
