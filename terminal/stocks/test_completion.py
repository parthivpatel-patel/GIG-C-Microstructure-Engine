"""Independent handover,framing/security and slow-consumer fixtures;no provider calls."""
import asyncio,copy,json,unittest
from types import SimpleNamespace
from .test_final import client,packet,quote,ready
from terminal.server.market_events import MarketEvents

class Completion(unittest.TestCase):
 def test_in_place_handover_acknowledges_empty_then_new_without_second_socket(self):
  async def run():
   c=client();ready(c);c.socket=SimpleNamespace(send=None);sent=[]
   async def send(b):sent.append(__import__('msgpack').unpackb(b))
   c.socket.send=send;c.task=asyncio.create_task(asyncio.sleep(100));c.process(packet(quote()))
   await c.start(['NVDA'],['quotes']);self.assertEqual(sent,[{'action':'unsubscribe','quotes':['AAPL'],'trades':['AAPL']}]);self.assertEqual(c.symbols,('AAPL',));self.assertIsNotNone(c.pending)
   with self.assertRaises(ValueError):await c.start(['MSFT'])
   c.process(packet({'T':'subscription','quotes':[],'trades':[]}));self.assertEqual(c.pending['step'],'SUBSCRIBE_READY');self.assertEqual(c.symbols,());self.assertTrue(all(r['state']=='UNAVAILABLE' for r in c.view()['observations']))
   c.pending['step']='SUBSCRIBE_SENT';before=c.generation;c.process(packet({'T':'subscription','quotes':['NVDA']}));self.assertEqual(c.symbols,('NVDA',));self.assertEqual(c.generation,before+1);self.assertIsNone(c.pending);self.assertFalse(c.latest)
   q=quote();q['S']='NVDA';c.process(packet(q));self.assertEqual(c.view()['metrics']['NVDA']['valid_ordered_quotes'],1);await c.close()
  asyncio.run(run())
 def test_bad_handover_ack_is_atomic_and_cannot_exceed_limit(self):
  c=client();ready(c);c.pending={'step':'SUBSCRIBE_SENT','symbols':('NVDA',),'channels':('quotes',)};before=copy.deepcopy(c.view())
  with self.assertRaises(ValueError):c.process(packet({'T':'subscription','quotes':['NVDA','AAPL']}))
  self.assertEqual(c.view(),before)
 def test_coalesced_push_has_no_source_mutation_and_bounded_capacity(self):
  async def run():
   c=client();ready(c);c.process(packet(quote()));h=MarketEvents(c,clients=1,interval=.001,heartbeat=.002);self.assertTrue(h.reserve());self.assertFalse(h.reserve());before=c.receipts
   it=h.frames();frame=await anext(it);self.assertTrue(frame.startswith('event: state\ndata: '));j=json.loads(frame.split('data: ',1)[1]);self.assertEqual(j['history'][0]['origin'],'HISTORICAL_SYNTHETIC');self.assertEqual(c.receipts,before);await it.aclose()
  asyncio.run(run())
 def test_push_cleanup_on_cancel_and_payload_guard(self):
  async def run():
   c=client();h=MarketEvents(c);h.reserve();response=h.response()
   async def send(message):raise asyncio.CancelledError
   async def receive():await asyncio.sleep(100)
   with self.assertRaises(asyncio.CancelledError):await response({'type':'http','asgi':{'spec_version':'2.4'}},receive,send)
   self.assertEqual(h.clients,0)
   c.view=lambda:{'oversize':'x'*(1024*1024)};it=h.frames();self.assertIn('MARKET_SNAPSHOT_BUDGET',await anext(it));await it.aclose()
  asyncio.run(run())
 def test_foreign_origin_and_forwarded_headers_cannot_open_stock_push(self):
  from starlette.testclient import TestClient
  from terminal.server.app import create_app
  from .service import StockWorkspace
  with TestClient(create_app(stock_workspace=StockWorkspace(environment={})),base_url='http://127.0.0.1:8787') as c:
   for headers in [{},{'Origin':'https://evil.invalid'},{'Origin':'https://untrusted.invalid','X-Forwarded-Host':'127.0.0.1:8787','X-Forwarded-Proto':'https'}]:self.assertEqual(c.post('/api/v1/stocks/events',json={},headers=headers).status_code,403)
   self.assertEqual(c.post('/api/v1/stocks/events',json={'wrong':True},headers={'Origin':'http://127.0.0.1:8787'}).status_code,422)
   r=c.get('/api/v1/request-proof',headers={'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':'http://127.0.0.1:8787','X-GIG-Target':'/api/v1/stocks/events'});self.assertEqual(r.status_code,200)
   proof=r.json()['proof'];self.assertEqual(c.post('/api/v1/stocks/live',json={'action':'stop'},headers={'Origin':'http://127.0.0.1:8787','X-GIG-Request-Proof':proof}).status_code,403)
 def test_session_schedule_boundaries_gaps_and_provenance(self):
  from .session_schedule import SessionSchedule
  p={'schema':'gig.session.schedule.v1','source':'AUTHORED_SCHEDULE_NOT_EXCHANGE_OBSERVATION','symbols':['AAPL'],'intervals':[{'start':'2024-01-02T14:30:00Z','end':'2024-01-02T21:00:00Z','state':'REGULAR'}]};s=SessionSchedule(json.dumps(p).encode())
  self.assertEqual(s.at('AAPL','2024-01-02T14:30:00Z')['state'],'REGULAR');self.assertEqual(s.at('AAPL','2024-01-02T21:00:00Z')['state'],'UNKNOWN');self.assertEqual(s.at('NVDA','2024-01-02T15:00:00Z')['state'],'UNKNOWN');self.assertEqual(len(s.at('AAPL',None)['schedule_sha256']),64);self.assertEqual(SessionSchedule().at('AAPL',None)['state'],'UNKNOWN')
 def test_schedule_duplicate_fields_overlap_and_limits_rejected(self):
  from .session_schedule import SessionSchedule
  for raw in [b'x'*65537,b'{"schema":1,"schema":2}',b'{}']:
   with self.assertRaises(ValueError):SessionSchedule(raw)
  p={'schema':'gig.session.schedule.v1','source':'authored','symbols':['AAPL'],'intervals':[{'start':'2024-01-02T14:30:00Z','end':'2024-01-02T21:00:00Z','state':'REGULAR'}]*2}
  with self.assertRaises(ValueError):SessionSchedule(json.dumps(p).encode())
  self.assertEqual(SessionSchedule.configured({'GIG_MARKET_SESSION_FILE':'/nonexistent/authored-path'}).reason,'configured_schedule_invalid')
 def test_codespaces_rewritten_push_requires_one_use_target_bound_proof(self):
  from terminal.server.request_proofs import RequestProofs,authorize_mutation
  p=RequestProofs();origin='https://authored-8787.app.github.dev';target='/api/v1/stocks/events';h={'origin':'http://localhost:8787','host':'localhost:8787','x-forwarded-host':origin[8:],'x-forwarded-proto':'https'}
  self.assertIsNone(authorize_mutation(h,target,[origin],origin,p)[0]);h['x-gig-request-proof']=p.issue(origin,target)
  self.assertEqual(authorize_mutation(h,target,[origin],origin,p)[0],origin);self.assertIsNone(authorize_mutation(h,target,[origin],origin,p)[0])
 def test_slow_push_consumer_times_out_and_releases_slot(self):
  async def run():
   h=MarketEvents(client());h.reserve()
   async def send(message):await asyncio.sleep(10)
   async def receive():await asyncio.sleep(10)
   await h.response()({'type':'http','asgi':{'spec_version':'2.4'}},receive,send)
   self.assertEqual(h.timeouts,1);self.assertEqual(h.clients,0)
  asyncio.run(run())
 def test_idle_market_keeps_one_authenticated_socket_without_inventing_market_close(self):
  from unittest.mock import patch
  async def run():
   c=client();connections=[];real_wait=asyncio.wait_for
   class Socket:
    def __init__(self):self.i=0
    async def __aenter__(self):connections.append(1);return self
    async def __aexit__(self,*a):pass
    async def send(self,b):pass
    async def recv(self):
     rows=[{'T':'success','msg':'connected'},{'T':'success','msg':'authenticated'},{'T':'subscription','quotes':['AAPL'],'trades':['AAPL']}]
     if self.i<len(rows):row=rows[self.i];self.i+=1;return packet(row)
     await asyncio.sleep(100)
   async def wait(value,timeout):return await real_wait(value,.001 if timeout==30 else timeout)
   c.connector=lambda *a,**k:Socket()
   with patch('terminal.stocks.live.asyncio.wait_for',wait):
    await c.start(['AAPL'])
    for _ in range(100):
     if c.state=='IDLE':break
     await asyncio.sleep(.001)
    self.assertEqual(c.state,'IDLE');self.assertEqual(c.failures,0);self.assertEqual(len(connections),1);self.assertIn('session_unverified',c.reason);await c.close()
  asyncio.run(run())
