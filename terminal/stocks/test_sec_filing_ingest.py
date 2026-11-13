"""Authored SEC-shaped streams;never a socket,account or observed provider copy."""
import asyncio,copy,hashlib,json,tempfile,unittest
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch
from .test_xbrl_embedded import embedded
from .test_xbrl_statements import ROLE,LATE
from .sec_filing_ingest import FilingIngestor,IngestError,directory
from .xbrl_instance import digest,canonical
CIK='0000320193';ACC='0000000123-24-000001';PREFIX='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/';META='https://data.sec.gov/submissions/CIK0000320193.json';AGENT='GIG authored fixture research@example.invalid'
class Clock:
 def __init__(self):self.value=0;self.sleeps=[]
 def __call__(self):return self.value
 async def sleep(self,delay):self.sleeps.append(delay);self.value+=delay
class Reply:
 def __init__(self,url,body,status=200,headers=None,*,pause=False):self.url=url;self.status=status;self.body=body;self.headers={'content-length':str(len(body)),**(headers or{})};self.pos=0;self.requests=[];self.closed=False;self.pause=pause
 async def read(self,n):
  self.requests.append(n)
  if self.pause:await asyncio.Event().wait()
  out=self.body[self.pos:self.pos+n];self.pos+=len(out);return out
class Wire:
 def __init__(self,resources,clock):self.resources=resources;self.clock=clock;self.calls=[];self.replies=[];self.errors={}
 @asynccontextmanager
 async def open(self,url,headers,*,timeout):
  self.calls.append((url,self.clock()));assert set(headers)=={'User-Agent','Accept-Encoding'};assert timeout==8
  if url in self.errors:
   response=self.errors[url].pop(0)
   if not self.errors[url]:del self.errors[url]
  else:response=Reply(url,self.resources[url])
  self.replies.append(response)
  try:yield response
  finally:response.closed=True

def resources(e=None):
 e=e or embedded();items=[{'name':'instance.xml','size':str(len(e['raw'])),'type':'file'}]+[{'name':d['uri'].rsplit('/',1)[-1],'size':str(len(d['raw'])),'type':'file'}for d in e['documents']]
 metadata={'cik':CIK,'filings':{'recent':{'accessionNumber':[ACC],'form':['10-K'],'filingDate':['2024-02-01'],'acceptanceDateTime':['2024-02-01T12:00:00.000000001Z'],'primaryDocument':['instance.xml']}}}
 index={'directory':{'name':PREFIX.removeprefix('https://www.sec.gov').rstrip('/'),'item':items}}
 return {META:canonical(metadata),PREFIX+'index.json':canonical(index),PREFIX+'instance.xml':e['raw'],**{PREFIX+d['uri'].rsplit('/',1)[-1]:d['raw']for d in e['documents']}}
def client(data=None,**kwargs):
 clock=Clock();wire=Wire(data or resources(),clock);c=FilingIngestor(CIK,transport=wire,permission=lambda:{'User-Agent':AGENT},enabled=True,clock=clock,receipt_clock=lambda:'2026-11-13T12:00:00Z',sleep=clock.sleep,random_source=lambda:0,**kwargs);return c,wire,clock
class SECIngestion(unittest.IsolatedAsyncioTestCase):
 async def test_full_automatic_closure_and_source_scoped_product(self):
  c,w,clock=client();r=await c.ingest(ACC);self.assertEqual(r['status'],'ACCEPTED');self.assertEqual(r['requests'],5);v=c.collection.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2');self.assertEqual(v['periods'][0]['rows'][-1]['value'],'400');self.assertEqual(v['source_filing']['received_at'],'2026-11-13T12:00:00Z');self.assertEqual(v['source_filing']['accepted_at'],'2024-02-01T12:00:00.000000001Z');self.assertTrue(all(b-a>=1.009 for a,b in zip([x[1]for x in w.calls],[x[1]for x in w.calls][1:])));self.assertTrue(all(r.closed for r in w.replies));self.assertFalse(r['complete_history'])
 async def test_disabled_and_identification_fail_before_transport(self):
  c,w,_=client();c.enabled=False
  with self.assertRaisesRegex(IngestError,'disabled'):await c.ingest(ACC)
  c.enabled=True;c.permission=lambda:{'User-Agent':'not identifying'}
  with self.assertRaisesRegex(IngestError,'identification'):await c.ingest(ACC)
  self.assertEqual(w.calls,[])
 async def test_idempotent_cached_repeat_preserves_receipts_and_identity(self):
  c,w,_=client();await c.ingest(ACC);first=c.checkpoint();calls=len(w.calls);r=await c.ingest(ACC);self.assertEqual(r['requests'],0);self.assertEqual(len(w.calls),calls);self.assertEqual(c.checkpoint(),first)
 async def test_exact_advertised_filename_and_identity_are_required(self):
  c,w,_=client()
  for name in('../secret.xml','https://evil.invalid/x.xml'):
   with self.assertRaises(IngestError):await c.ingest(ACC,document=name)
  self.assertEqual(w.calls,[])
  with self.assertRaisesRegex(IngestError,'not_eligible'):await c.ingest(ACC,document='not-listed.xml')
 async def test_directory_conflict_and_unsupported_primary_are_explicit(self):
  data=resources();idx=json.loads(data[PREFIX+'index.json']);idx['directory']['item'].append(idx['directory']['item'][0]);data[PREFIX+'index.json']=canonical(idx);c,_,_=client(data)
  with self.assertRaisesRegex(IngestError,'duplicate'):await c.ingest(ACC)
  c,_,_=client();meta=json.loads(c.transport.resources[META]);meta['filings']['recent']['primaryDocument']=['primary.htm'];c.transport.resources[META]=canonical(meta);idx=json.loads(c.transport.resources[PREFIX+'index.json']);idx['directory']['item'][0]['name']='primary.htm';c.transport.resources[PREFIX+'index.json']=canonical(idx)
  with self.assertRaisesRegex(IngestError,'format_unsupported'):await c.ingest(ACC)
 async def test_bad_status_redirect_encoding_length_never_publishes(self):
  for response in(Reply(META,b'x',302),Reply('https://evil.invalid/',b'x'),Reply(META,b'x',headers={'content-encoding':'gzip'}),Reply(META,b'xx',headers={'content-length':'1'})):
   c,w,_=client();w.errors[META]=[response]
   with self.assertRaises(IngestError):await c.ingest(ACC)
   self.assertEqual(c.plans,{});self.assertEqual(c.sources,{});self.assertTrue(response.closed)
 async def test_rate_limit_retry_is_bounded_and_finite(self):
  c,w,clock=client();w.errors[META]=[Reply(META,b'',429,{'retry-after':'2'})];r=await c.ingest(ACC);self.assertEqual(r['requests'],6);self.assertIn(2,clock.sleeps)
  c,w,_=client();w.errors[META]=[Reply(META,b'',503),Reply(META,b'',503)]
  with self.assertRaisesRegex(IngestError,'retry_exhausted'):await c.ingest(ACC)
  self.assertEqual(len(w.calls),2)
 async def test_invalid_retry_after_does_not_expand_budget(self):
  c,w,_=client();w.errors[META]=[Reply(META,b'',429,{'retry-after':'9999'})]
  with self.assertRaisesRegex(IngestError,'retry_after'):await c.ingest(ACC)
  self.assertEqual(len(w.calls),1)
 async def test_ssrf_and_unapproved_taxonomy_reference_is_never_requested(self):
  e=embedded();d=e['documents'][0];d['raw']=d['raw'].replace(b'extension.xsd',b'https://169.254.169.254/secret.xsd');c,w,_=client(resources(e))
  with self.assertRaisesRegex(IngestError,'outside_scope'):await c.ingest(ACC)
  self.assertFalse(any('169.254' in url for url,_ in w.calls))
 async def test_explicit_official_taxonomy_allowlist_is_exact(self):
  e=embedded();e['documents'][0]['raw']=e['documents'][0]['raw'].replace(b'extension.xsd',b'https://www.xbrl.org/authored.xsd');data=resources(e);data['https://www.xbrl.org/authored.xsd']=data[PREFIX+'extension.xsd'];c,w,_=client(data,taxonomy_urls=['https://www.xbrl.org/authored.xsd']);await c.ingest(ACC);self.assertTrue(any(u=='https://www.xbrl.org/authored.xsd'for u,_ in w.calls))
  with self.assertRaises(IngestError):client(taxonomy_urls=['https://www.xbrl.org.evil.invalid/a.xsd'])
 async def test_resource_limits_and_transport_contract_are_fail_closed(self):
  c,w,_=client()
  with patch('terminal.stocks.sec_filing_ingest.MAX_REQUESTS',1),self.assertRaisesRegex(IngestError,'request_budget'):await c.ingest(ACC)
  c,w,_=client()
  with patch('terminal.stocks.sec_filing_ingest.MAX_TOTAL',16),self.assertRaisesRegex(IngestError,'body_budget'):await c.ingest(ACC)
  self.assertEqual(c.collection.page()['total'],0)
 async def test_failed_refresh_preserves_prior_accepted_state(self):
  c,w,_=client();await c.ingest(ACC);before=c.checkpoint();w.resources[PREFIX+'instance.xml']=w.resources[PREFIX+'instance.xml'].replace(b'>1000<',b'>9999<')
  with self.assertRaisesRegex(IngestError,'immutable_source_changed'):await c.ingest(ACC,fresh=True)
  self.assertEqual(c.checkpoint(),before);self.assertEqual(c.state,'FAILED')
 async def test_cancellation_closes_response_and_keeps_accepted_state(self):
  c,w,_=client();await c.ingest(ACC);before=c.checkpoint();w.errors[META]=[Reply(META,b'never read',pause=True)];task=asyncio.create_task(c.ingest(ACC,fresh=True));await asyncio.sleep(0.001);task.cancel()
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertEqual(c.state,'CANCELLED');self.assertTrue(w.replies[-1].closed);self.assertEqual(c.checkpoint(),before);self.assertFalse(c.lock.locked())
 async def test_checkpoint_restore_reparses_and_stays_paused_without_source_calls(self):
  c,w,_=client();await c.ingest(ACC);raw=c.checkpoint();restored,wire,_=client();restored.enabled=False;r=restored.restore(raw,hashlib.sha256(raw).hexdigest());self.assertEqual(r['status'],'PAUSED_RESTORED');self.assertEqual(wire.calls,[]);self.assertEqual(restored.collection.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2'),c.collection.statement_at(LATE,role=ROLE,profile='accuracy-extension-v2'));self.assertEqual(restored.cache,{})
 async def test_corrupt_unknown_and_source_scope_checkpoints_reject_atomically(self):
  c,_,_=client();await c.ingest(ACC);raw=c.checkpoint();restored,_,_=client()
  with self.assertRaisesRegex(IngestError,'integrity'):restored.restore(raw+b'x',hashlib.sha256(raw).hexdigest())
  for key,value in [('schema','future'),('issuer_cik','0000000001'),('collection_sha256','0'*64)]:
   v=json.loads(raw);v[key]=value;payload=canonical(v)
   with self.assertRaises(ValueError):restored.restore(payload,hashlib.sha256(payload).hexdigest())
  self.assertEqual(restored.collection.page()['total'],0)
 async def test_source_digest_and_metadata_binding_are_revalidated_even_after_rehash(self):
  c,_,_=client();await c.ingest(ACC);v=json.loads(c.checkpoint());key=next(iter(v['sources']));v['sources'][key]['sha256']='0'*64;raw=canonical(v);r,_,_=client()
  with self.assertRaisesRegex(IngestError,'source_integrity'):r.restore(raw,hashlib.sha256(raw).hexdigest())
 async def test_read_permission_does_not_authorize_retention(self):
  from .sec_ingest_store import FilingCheckpointStore
  with tempfile.TemporaryDirectory()as directory:
   with self.assertRaisesRegex(IngestError,'retention_disabled'):FilingCheckpointStore(directory,enabled=True)
 async def test_store_failure_prevents_memory_publication(self):
  c,_,_=client()
  class Fail:
   def save(self,_):raise OSError('authored disk full')
  with self.assertRaises(OSError):await c.ingest(ACC,store=Fail())
  self.assertEqual(c.collection.page()['total'],0);self.assertEqual(c.plans,{})
 async def test_acceptance_metadata_cannot_change_an_immutable_admitted_filing(self):
  c,w,_=client();await c.ingest(ACC);before=c.checkpoint();meta=json.loads(w.resources[META]);meta['filings']['recent']['acceptanceDateTime']=['2024-02-01T13:00:00Z'];w.resources[META]=canonical(meta)
  with self.assertRaisesRegex(IngestError,'immutable_filing_changed'):await c.ingest(ACC,fresh=True)
  self.assertEqual(c.checkpoint(),before)
 async def test_new_snapshot_with_missing_source_reference_is_rejected(self):
  c,_,_=client();await c.ingest(ACC);v=json.loads(c.checkpoint());v['plans'][ACC]['instance_key']='f'*64;raw=canonical(v);fresh,_,_=client()
  with self.assertRaisesRegex(IngestError,'source_reference'):fresh.restore(raw,hashlib.sha256(raw).hexdigest())
 async def test_httpx_wire_uses_only_read_only_fixed_destinations(self):
  import httpx
  from .sec_read_wire import SECReadWire
  clock=Clock();data=resources();calls=[]
  class Stream(httpx.AsyncByteStream):
   def __init__(self,body):self.body=body
   async def __aiter__(self):
    for i in range(0,len(self.body),13):yield self.body[i:i+13]
  async def handler(request):
   calls.append(request);return httpx.Response(200,stream=Stream(data[str(request.url)]),headers={'Content-Length':str(len(data[str(request.url)]))})
  c=FilingIngestor(CIK,transport=SECReadWire(httpx.MockTransport(handler)),permission=lambda:{'User-Agent':AGENT},enabled=True,clock=clock,sleep=clock.sleep);await c.ingest(ACC);self.assertTrue(all(r.method=='GET'and not r.content for r in calls));self.assertTrue(all(r.url.host in('www.sec.gov','data.sec.gov')for r in calls))
