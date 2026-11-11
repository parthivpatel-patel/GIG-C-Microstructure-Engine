"""Worker recovery only,with deterministic fake transport;no listeners or provider IO."""
import asyncio,unittest
from unittest.mock import patch
from .test_final import client,ready
from .test_reconnect_stability import FakeSocket

class LiveRecovery(unittest.IsolatedAsyncioTestCase):
 async def test_finished_worker_with_stale_subscription_can_be_explicitly_restarted(self):
  c=client();ready(c)
  async def done():pass
  c.task=asyncio.create_task(done());await c.task;c.phase='DISCONNECTED';c.state='FAILED';c.pending={'step':'SUBSCRIBE_SENT','symbols':('AAPL',),'channels':('quotes','trades'),'started':100}
  with patch.object(c,'run',new=done):await c.start(['AAPL'])
  self.assertIsNone(c.pending);self.assertEqual(c.symbols,('AAPL',));await c.close()
 async def test_external_worker_interruption_cannot_keep_subscribed_status(self):
  c=client();started=asyncio.Event()
  class Hanging:
   async def __aenter__(self):self.index=0;return self
   async def __aexit__(self,*_):pass
   async def recv(self):
    from .test_final import packet
    frames=[{'T':'success','msg':'connected'},{'T':'success','msg':'authenticated'},{'T':'subscription','quotes':['AAPL'],'trades':['AAPL']}]
    if self.index<3:row=frames[self.index];self.index+=1;return packet(row)
    started.set();await asyncio.Event().wait()
   async def send(self,_):pass
  c.connector=lambda *a,**k:Hanging();task=asyncio.create_task(c.run());await started.wait();task.cancel()
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertEqual(c.state,'RECOVERY_REQUIRED');self.assertEqual(c.phase,'DISCONNECTED');self.assertIsNone(c.socket)
 async def test_invalid_restart_does_not_clear_orphan_pending_state(self):
  c=client()
  async def done():pass
  c.task=asyncio.create_task(done());await c.task;c.phase='DISCONNECTED';c.state='FAILED';c.pending={'step':'SUBSCRIBE_SENT','symbols':('AAPL',),'channels':('quotes','trades')}
  before=dict(c.pending)
  with self.assertRaises(ValueError):await c.start(['../invalid'])
  self.assertEqual(c.pending,before);self.assertEqual(c.state,'FAILED');await c.close()
 async def test_active_handover_cannot_be_overwritten_by_a_new_start(self):
  c=client();ready(c);c.task=asyncio.create_task(asyncio.Event().wait());c.pending={'step':'SUBSCRIBE_SENT','symbols':('AAPL',),'channels':('quotes','trades')}
  with self.assertRaisesRegex(ValueError,'subscription_update_pending'):await c.start(['NVDA'])
  self.assertEqual(c.pending['symbols'],('AAPL',));await c.close()
 async def test_explicit_stop_cleans_worker_socket_and_pending_state(self):
  c=client();opened=asyncio.Event()
  class Hanging:
   async def __aenter__(self):opened.set();return self
   async def __aexit__(self,*_):pass
   async def recv(self):await asyncio.Event().wait()
  c.connector=lambda *a,**k:Hanging();c.task=asyncio.create_task(c.run());await opened.wait();await c.close()
  self.assertEqual(c.state,'STOPPED');self.assertEqual(c.phase,'DISCONNECTED');self.assertIsNone(c.socket);self.assertIsNone(c.pending);self.assertTrue(c.view()['recovery']['requires_fresh_observation']);self.assertFalse(c.view()['recovery']['hot_l3_restored'])
 async def test_handover_derivation_uses_the_exact_published_symbol_window(self):
  from .test_final import packet,quote
  c=client();ready(c);c.process(packet(quote()));c.pending={'step':'SUBSCRIBE_SENT','symbols':('NVDA',),'channels':('quotes','trades'),'started':100}
  c.process(packet({'T':'subscription','quotes':['NVDA'],'trades':['NVDA']}));view=c.view()
  self.assertEqual(view['history'],[]);self.assertEqual(len(c.history),1)
  self.assertEqual(view['trade_reconciliation']['NVDA']['input_records'],len(view['history']))
 async def test_concurrent_subscription_commands_cannot_orphan_a_second_worker(self):
  c=client();ready(c);active=set();started=[];peak=[0]
  async def worker():
   task=asyncio.current_task();active.add(task);started.append(task);peak[0]=max(peak[0],len(active))
   try:await asyncio.Event().wait()
   finally:active.discard(task)
  with patch.object(c,'run',new=worker):
   try:
    await c.start(['AAPL']);await asyncio.sleep(0)
    await asyncio.gather(c.start(['NVDA']),c.start(['MSFT']));await asyncio.sleep(0)
    self.assertEqual(peak[0],1);self.assertEqual(len(active),1)
   finally:
    await c.close()
    for task in started:
     if not task.done():task.cancel()
    await asyncio.gather(*started,return_exceptions=True)
 async def test_retired_socket_cannot_publish_a_frame_into_current_generation(self):
  from .test_final import packet,quote
  c=client();ready(c);current=object();c.socket=current;before=c.view()
  with self.assertRaisesRegex(ValueError,'stale_transport_frame'):c.process(packet(quote()),socket_owner=object())
  self.assertEqual(c.view(),before)
  self.assertEqual(len(c.process(packet(quote()),socket_owner=current)),1)
 async def test_provider_auth_failure_is_classified_by_phase_without_echoing_message_or_guessing_code(self):
  from .test_final import packet
  c=client()
  class Refused:
   async def __aenter__(self):self.i=0;return self
   async def __aexit__(self,*args):pass
   async def send(self,_):pass
   async def recv(self):
    self.i+=1
    return packet({'T':'success','msg':'connected'})if self.i==1 else packet({'T':'error','code':999999999999,'msg':'AUTHORED_SECRET_MUST_NOT_BE_REFLECTED'})
  c.connector=lambda *a,**k:Refused();await c.run();r=c.view()['last_failure']
  self.assertEqual(r['category'],'PROVIDER_AUTH_REJECTION');self.assertEqual(r['phase'],'AUTH_SENT');self.assertEqual(r['provider_code'],'999999999999');self.assertNotIn('AUTHORED_SECRET',str(c.view()))
