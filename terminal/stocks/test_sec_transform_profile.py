"""Explicit acquired registry profiles are immutable source interpretation intent."""
import copy,hashlib,json,subprocess,sys,tempfile,unittest
from .test_sec_multidoc import fixture
from .test_sec_filing_ingest import client,ACC,PREFIX
from .inline_set import TRANSFORMATION_PROFILE
from .sec_filing_ingest import IngestError
from .sec_ingest_store import FilingCheckpointStore
from .xbrl_instance import canonical

def transformed_fixture(*,zero=False):
 data,m=fixture();raw=data[PREFIX+'primary.htm']
 if zero:raw=raw.replace(b'ixt:numdotdecimal',b'ixt:zerodash').replace(b'<b>1,234</b>.50',b'-')
 else:raw=raw.replace(b'ixt:numdotdecimal',b'ixt:numdotdecimalin').replace(b'<b>1,234</b>.50',b'<b>1</b> 23 456.70')
 data[PREFIX+'primary.htm']=raw;m['documents'][0]['sha256']=hashlib.sha256(raw).hexdigest();idx=json.loads(data[PREFIX+'index.json']);idx['directory']['item'][0]['size']=len(raw);data[PREFIX+'index.json']=canonical(idx)
 return data,m

class AcquiredTransformProfile(unittest.IsolatedAsyncioTestCase):
 async def test_explicit_registry_profile_transforms_acquired_set_with_provenance(self):
  data,m=transformed_fixture();c,w,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);p=c.collection._filings[ACC]
  self.assertEqual(p['facts'][0]['value'],'123456.70');self.assertEqual(p['facts'][1]['lexical_value'],'ABCD');self.assertEqual(p['document_set']['transformation_profile'],TRANSFORMATION_PROFILE)
  self.assertEqual(p['document_set']['facts'][0]['extracted_text'],'1 23 456.70');self.assertEqual(p['document_set']['documents'][1]['source']['source_sha256'],m['documents'][0]['sha256']);self.assertEqual(len(w.calls),5)
 async def test_explicit_zero_dash_is_reported_zero_not_missing(self):
  data,m=transformed_fixture(zero=True);c,_,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);fact=c.collection._filings[ACC]['facts'][0]
  self.assertEqual(fact['value'],'0');self.assertFalse(fact['nil']);self.assertEqual(fact['inline_source_segments'][0]['document_uri'],PREFIX+'primary.htm')
 async def test_legacy_new_function_rejection_keeps_collection_empty(self):
  data,m=transformed_fixture();c,_,_=client(data)
  with self.assertRaisesRegex(ValueError,'transform_unsupported'):await c.ingest(ACC,inline_manifest=m)
  self.assertEqual(c.plans,{});self.assertEqual(c.collection.page()['total'],0)
 async def test_invalid_selector_and_missing_manifest_precede_transport(self):
  for profile in('unknown',True,{},[],''):
   data,m=fixture();c,w,_=client(data)
   with self.assertRaisesRegex(IngestError,'profile_unsupported'):await c.ingest(ACC,inline_manifest=m,transformation_profile=profile)
   self.assertEqual(w.calls,[])
  c,w,_=client()
  with self.assertRaisesRegex(IngestError,'manifest_required'):await c.ingest(ACC,transformation_profile=TRANSFORMATION_PROFILE)
  self.assertEqual(w.calls,[])
 async def test_accepted_default_cannot_silently_gain_profile(self):
  data,m=fixture();c,w,_=client(data);await c.ingest(ACC,inline_manifest=m);before=c.checkpoint();calls=len(w.calls)
  with self.assertRaisesRegex(IngestError,'profile_immutable'):await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE)
  self.assertEqual(c.checkpoint(),before);self.assertEqual(len(w.calls),calls)
 async def test_accepted_profile_cannot_silently_fall_back_to_default(self):
  data,m=fixture();c,w,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);before=c.checkpoint();calls=len(w.calls)
  with self.assertRaisesRegex(IngestError,'profile_immutable'):await c.ingest(ACC,inline_manifest=m,fresh=True)
  self.assertEqual(c.checkpoint(),before);self.assertEqual(len(w.calls),calls)
 async def test_v4_restore_reparses_without_transport_and_remains_paused(self):
  data,m=transformed_fixture();c,_,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);raw=c.checkpoint();v=json.loads(raw);self.assertEqual(v['schema'],'gig.sec.filing_ingestion.checkpoint.v4');self.assertEqual(v['plans'][ACC]['transformation_profile'],TRANSFORMATION_PROFILE)
  r,wire,_=client();r.enabled=False;r.restore(raw,hashlib.sha256(raw).hexdigest());self.assertEqual(r.state,'PAUSED_RESTORED');self.assertEqual(wire.calls,[]);self.assertEqual(r.collection._filings,c.collection._filings);self.assertEqual(r.checkpoint(),raw)
 async def test_default_manifest_still_emits_v3_without_profile_field(self):
  data,m=fixture();c,_,_=client(data);await c.ingest(ACC,inline_manifest=m);v=json.loads(c.checkpoint());self.assertEqual(v['schema'],'gig.sec.filing_ingestion.checkpoint.v3');self.assertNotIn('transformation_profile',v['plans'][ACC]);self.assertNotIn('transformation_profile',c.collection._filings[ACC]['document_set'])
 async def test_corrupted_version_profile_and_manifest_binding_reject_atomically(self):
  data,m=transformed_fixture();c,_,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);image=json.loads(c.checkpoint());r,wire,_=client();before=r.checkpoint()
  for kind in('downgrade','unknown','null','remove_manifest','remove_profile'):
   v=copy.deepcopy(image)
   if kind=='downgrade':v['schema']='gig.sec.filing_ingestion.checkpoint.v3'
   elif kind=='unknown':v['plans'][ACC]['transformation_profile']='future'
   elif kind=='null':v['plans'][ACC]['transformation_profile']=None
   elif kind=='remove_manifest':del v['plans'][ACC]['inline_manifest']
   else:del v['plans'][ACC]['transformation_profile']
   raw=canonical(v)
   with self.assertRaises(ValueError):r.restore(raw,hashlib.sha256(raw).hexdigest())
   self.assertEqual(r.checkpoint(),before);self.assertEqual(wire.calls,[])
 async def test_interpretation_metadata_cannot_be_stripped_from_compatible_sources(self):
  data,m=fixture();c,_,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);v=json.loads(c.checkpoint());del v['plans'][ACC]['transformation_profile'];v['schema']='gig.sec.filing_ingestion.checkpoint.v3';raw=canonical(v);r,wire,_=client()
  with self.assertRaisesRegex(IngestError,'checkpoint_collection'):r.restore(raw,hashlib.sha256(raw).hexdigest())
  self.assertEqual(r.plans,{});self.assertEqual(wire.calls,[])
 async def test_private_cross_process_v4_restore_forbids_sockets(self):
  data,m=transformed_fixture();c,_,_=client(data)
  with tempfile.TemporaryDirectory()as directory:
   store=FilingCheckpointStore(directory,enabled=True,retention_approved=True);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE,store=store);sha=hashlib.sha256(c.checkpoint()).hexdigest()
   code="""import socket,sys
from terminal.stocks.test_sec_filing_ingest import client,ACC
from terminal.stocks.sec_ingest_store import FilingCheckpointStore
from terminal.stocks.inline_set import TRANSFORMATION_PROFILE
def forbidden(*a,**k):raise AssertionError('NO_SOCKET')
socket.socket.connect=forbidden;socket.socket.bind=forbidden
s=FilingCheckpointStore(sys.argv[1],enabled=True,retention_approved=True);c,w,_=client();c.enabled=False;c.restore(s.load(sys.argv[2]),sys.argv[2]);assert c.state=='PAUSED_RESTORED'and not w.calls;assert c.collection._filings[ACC]['facts'][0]['value']=='123456.70';assert c.plans[ACC]['transformation_profile']==TRANSFORMATION_PROFILE
"""
   result=subprocess.run([sys.executable,'-c',code,directory,sha],capture_output=True,text=True,timeout=20);self.assertEqual(result.returncode,0,result.stderr)
 async def test_cached_repeat_keeps_original_receipts_and_interpretation_identity(self):
  data,m=transformed_fixture();c,w,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);before=c.checkpoint();calls=len(w.calls)
  await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE);self.assertEqual(c.checkpoint(),before);self.assertEqual(len(w.calls),calls)
 async def test_one_and_eight_member_sets_bind_profile_without_duplicate_reads(self):
  from .test_sec_source_expansion import inline_data
  from .test_sec_filing_ingest import CIK
  from .test_inline_set import html
  for count in(1,8):
   data=inline_data();m={'schema':'gig.sec.inline_acquisition_manifest.v1','issuer_cik':CIK,'accession':ACC,'primary_document':'primary.htm','documents':[{'name':'primary.htm','sha256':hashlib.sha256(data[PREFIX+'primary.htm']).hexdigest()}]};idx=json.loads(data[PREFIX+'index.json'])
   for i in range(count-1):
    name=f'part-{i}.xhtml';raw=html('');data[PREFIX+name]=raw;m['documents'].append({'name':name,'sha256':hashlib.sha256(raw).hexdigest()});idx['directory']['item'].append({'name':name,'size':len(raw),'type':'file'})
   data[PREFIX+'index.json']=canonical(idx);c,w,_=client(data);await c.ingest(ACC,inline_manifest=m,transformation_profile=TRANSFORMATION_PROFILE)
   self.assertEqual(len(c.plans[ACC]['inline_keys']),count);self.assertEqual(len(w.calls),count+3);self.assertEqual(c.collection._filings[ACC]['facts'][0]['value'],'1234.50');self.assertEqual(json.loads(c.checkpoint())['schema'],'gig.sec.filing_ingestion.checkpoint.v4')
