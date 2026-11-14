"""Adversarial authored multi-document acquisitions; never a provider transport."""
import asyncio,copy,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .test_sec_source_expansion import inline_data
from .test_sec_filing_ingest import client,CIK,ACC,PREFIX,Reply
from .test_inline_set import html
from .sec_filing_ingest import IngestError
from .xbrl_instance import canonical

def fixture():
 data=inline_data();raw=data[PREFIX+'primary.htm'].replace(b'</body>',b'<ix:nonNumeric name="g:Narrative" contextRef="D" continuedAt="tail">A<b>B</b></ix:nonNumeric></body>')
 data[PREFIX+'primary.htm']=raw;data[PREFIX+'a-tail.xhtml']=html('<ix:continuation id="tail">C<i>D</i></ix:continuation>')
 index=json.loads(data[PREFIX+'index.json']);index['directory']['item'][0]['size']=len(raw);index['directory']['item'].append({'name':'a-tail.xhtml','type':'file','size':len(data[PREFIX+'a-tail.xhtml'])});data[PREFIX+'index.json']=canonical(index)
 manifest={'schema':'gig.sec.inline_acquisition_manifest.v1','issuer_cik':CIK,'accession':ACC,'primary_document':'primary.htm','documents':[{'name':name,'sha256':hashlib.sha256(data[PREFIX+name]).hexdigest()}for name in ('primary.htm','a-tail.xhtml')]}
 return data,manifest

class MultiDocument(unittest.IsolatedAsyncioTestCase):
 async def test_continuation_transform_order_receipts_and_no_duplicate_primary_read(self):
  data,m=fixture();c,w,_=client(data);await c.ingest(ACC,inline_manifest=m);p=c.collection._filings[ACC]
  self.assertEqual([f.get('value')or f.get('lexical_value')for f in p['facts']],['1234.50','ABCD'])
  segments=p['facts'][1]['inline_source_segments'];self.assertEqual([s['document_uri']for s in segments],[PREFIX+'primary.htm',PREFIX+'a-tail.xhtml'])
  self.assertEqual(len([url for url,_ in w.calls if url==PREFIX+'primary.htm']),1)
  self.assertEqual(c.plans[ACC]['inline_manifest'],m);self.assertEqual([d['uri']for d in p['document_set']['documents']],sorted([PREFIX+d['name']for d in m['documents']]))
  self.assertTrue(all(d['source']['received_at']=='2026-11-13T12:00:00Z'for d in p['document_set']['documents']))
 async def test_manifest_order_preserved_but_canonical_set_values_do_not_change(self):
  data,m=fixture();a,_,_=client(data);b,_,_=client(data);reverse=copy.deepcopy(m);reverse['documents'].reverse()
  await a.ingest(ACC,inline_manifest=m);await b.ingest(ACC,inline_manifest=reverse)
  self.assertEqual(a.collection.page(),b.collection.page());self.assertNotEqual(a.plans[ACC]['inline_manifest_sha256'],b.plans[ACC]['inline_manifest_sha256'])
  before=a.checkpoint()
  with self.assertRaisesRegex(IngestError,'manifest_immutable'):await a.ingest(ACC,inline_manifest=reverse)
  self.assertEqual(a.checkpoint(),before)
 async def test_schema_scope_budget_duplicate_names_and_digests_precede_transport(self):
  data,m=fixture();bad=[]
  for k,v in [('schema','bad'),('issuer_cik','0000000001'),('accession','0000000001-24-000001'),('primary_document','missing.htm'),('documents',[]),('documents',m['documents']*5)]:
   row=copy.deepcopy(m);row[k]=v;bad.append(row)
  bad.extend([{**m,'extra':True},{**m,'documents':[m['documents'][0]]*2}])
  for field,val in [('name','../bad.htm'),('name','https://evil.invalid/a.htm'),('sha256','z'*64),('sha256',None)]:
   row=copy.deepcopy(m);row['documents'][1][field]=val;bad.append(row)
  for row in bad:
   c,w,_=client(data)
   with self.assertRaises(ValueError):await c.ingest(ACC,inline_manifest=row)
   self.assertEqual(w.calls,[])
 async def test_missing_wrong_type_size_and_total_budget_are_atomic(self):
  for kind in ('missing','type','size','total'):
   data,m=fixture();idx=json.loads(data[PREFIX+'index.json'])
   if kind=='missing':idx['directory']['item'].pop()
   elif kind=='type':idx['directory']['item'][-1]['type']='dir'
   elif kind=='size':idx['directory']['item'][-1]['size']+=1
   else:idx['directory']['item'][-1]['size']=2*1024*1024+1
   data[PREFIX+'index.json']=canonical(idx);c,_,_=client(data)
   with self.assertRaises(ValueError):await c.ingest(ACC,inline_manifest=m)
   self.assertEqual(c.sources,{});self.assertEqual(c.plans,{})
 async def test_wrong_original_hash_primary_or_secondary_rejects(self):
  for i in (0,1):
   data,m=fixture();m['documents'][i]['sha256']='0'*64;c,_,_=client(data)
   with self.assertRaisesRegex(IngestError,'source_binding'):await c.ingest(ACC,inline_manifest=m)
   self.assertEqual(c.collection.page()['total'],0)
 async def test_continuation_missing_cycle_duplicate_ids_and_malformed_xml(self):
  for raw in (html(''),html('<ix:continuation id="tail" continuedAt="tail">C</ix:continuation>'),html('<div id="D"/><ix:continuation id="tail">C</ix:continuation>'),b'<html>'):
   data,m=fixture();data[PREFIX+'a-tail.xhtml']=raw;m['documents'][1]['sha256']=hashlib.sha256(raw).hexdigest();idx=json.loads(data[PREFIX+'index.json']);idx['directory']['item'][-1]['size']=len(raw);data[PREFIX+'index.json']=canonical(idx);c,_,_=client(data)
   with self.assertRaises(ValueError):await c.ingest(ACC,inline_manifest=m)
   self.assertEqual(c.plans,{})
 async def test_primary_binding_and_manifest_removal_cannot_replace_collection(self):
  data,m=fixture();c,w,_=client(data)
  with self.assertRaisesRegex(IngestError,'primary_binding'):await c.ingest(ACC,inline_manifest=m,document='a-tail.xhtml')
  self.assertEqual(w.calls,[]);await c.ingest(ACC,inline_manifest=m);before=c.checkpoint()
  # Removing the manifest would lose its continuation, so still rejects atomically.
  with self.assertRaises(ValueError):await c.ingest(ACC)
  self.assertEqual(c.checkpoint(),before)
 async def test_v3_restore_revalidates_manifest_keys_and_version_offline(self):
  data,m=fixture();c,_,_=client(data);await c.ingest(ACC,inline_manifest=m);raw=c.checkpoint();image=json.loads(raw);self.assertEqual(image['schema'],'gig.sec.filing_ingestion.checkpoint.v3')
  r,wire,_=client();r.enabled=False;r.restore(raw,hashlib.sha256(raw).hexdigest());self.assertEqual(r.collection.page(),c.collection.page());self.assertEqual(wire.calls,[])
  for kind in ('version','hash','key','order'):
   v=copy.deepcopy(image)
   if kind=='version':v['schema']='gig.sec.filing_ingestion.checkpoint.v2'
   elif kind=='hash':v['plans'][ACC]['inline_manifest_sha256']='0'*64
   elif kind=='key':v['plans'][ACC]['inline_keys'].reverse()
   else:v['plans'][ACC]['inline_manifest']['documents'].reverse()
   altered=canonical(v);before=r.checkpoint()
   with self.assertRaises(ValueError):r.restore(altered,hashlib.sha256(altered).hexdigest())
   self.assertEqual(r.checkpoint(),before)
 async def test_cancel_and_restore_lock_preserve_accepted_state(self):
  data,m=fixture();c,w,_=client(data);await c.ingest(ACC,inline_manifest=m);before=c.checkpoint();w.errors[PREFIX+'a-tail.xhtml']=[Reply(PREFIX+'a-tail.xhtml',b'pending',pause=True)]
  task=asyncio.create_task(c.ingest(ACC,inline_manifest=m,fresh=True));await asyncio.sleep(.001)
  with self.assertRaisesRegex(IngestError,'busy'):c.restore(before,hashlib.sha256(before).hexdigest())
  task.cancel()
  with self.assertRaises(asyncio.CancelledError):await task
  self.assertEqual(c.checkpoint(),before);self.assertTrue(w.replies[-1].closed)
 async def test_private_revision_child_process_restore_with_sockets_forbidden(self):
  from .sec_ingest_store import FilingCheckpointStore
  data,m=fixture();c,_,_=client(data)
  with tempfile.TemporaryDirectory()as directory:
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True);await c.ingest(ACC,inline_manifest=m,store=store);raw=c.checkpoint();sha=hashlib.sha256(raw).hexdigest()
   code="""import socket,sys,hashlib
from terminal.stocks.test_sec_filing_ingest import client
from terminal.stocks.sec_ingest_store import FilingCheckpointStore
def forbidden(*a,**k):raise AssertionError('NO_SOCKET')
socket.socket.connect=forbidden;socket.socket.bind=forbidden
s=FilingCheckpointStore(sys.argv[1],enabled=True,retention_approved=True);c,w,_=client();c.enabled=False;c.restore(s.load(sys.argv[2]),sys.argv[2]);assert c.state=='PAUSED_RESTORED'and not w.calls;assert c.collection.page()['total']==1
"""
   result=subprocess.run([sys.executable,'-c',code,directory,sha],capture_output=True,text=True,timeout=20);self.assertEqual(result.returncode,0,result.stderr)
 async def test_storage_failure_does_not_publish_new_collection(self):
  data,m=fixture();c,_,_=client(data)
  class Broken:
   def save(self,_):raise OSError('authored disk full')
  with self.assertRaises(OSError):await c.ingest(ACC,inline_manifest=m,store=Broken())
  self.assertEqual(c.plans,{});self.assertEqual(c.sources,{})
 async def test_eight_documents_are_accepted_and_advertised_total_is_bounded(self):
  data,m=fixture();idx=json.loads(data[PREFIX+'index.json'])
  for i in range(6):
   name=f'part-{i}.xhtml';raw=html('');data[PREFIX+name]=raw;m['documents'].append({'name':name,'sha256':hashlib.sha256(raw).hexdigest()});idx['directory']['item'].append({'name':name,'type':'file','size':len(raw)})
  data[PREFIX+'index.json']=canonical(idx);c,w,_=client(data);await c.ingest(ACC,inline_manifest=m);self.assertEqual(len(c.plans[ACC]['inline_keys']),8);self.assertEqual(len(w.calls),11)
  before=c.checkpoint();await c.ingest(ACC,inline_manifest=m);self.assertEqual(c.checkpoint(),before);self.assertEqual(len(w.calls),11)
  for row in idx['directory']['item']:
   if row['name'].startswith('part-'):row['size']=2*1024*1024
  data[PREFIX+'index.json']=canonical(idx);r,wire,_=client(data)
  with self.assertRaisesRegex(IngestError,'byte_budget'):await r.ingest(ACC,inline_manifest=m)
  self.assertEqual(len(wire.calls),3);self.assertEqual(r.plans,{})
