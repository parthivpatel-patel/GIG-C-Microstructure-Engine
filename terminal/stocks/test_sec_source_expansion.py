"""Authored offline acquisition/schedule integration; no provider requests."""
import copy,hashlib,json,unittest
from .test_sec_filing_ingest import client,resources,CIK,ACC,META,PREFIX
from .test_inline_set import html,numeric
from .test_xbrl_binding import declaration
from .sec_filing_ingest import IngestError
from .xbrl_instance import canonical

def inline_data():
 raw=html(numeric('<b>1,234</b>.50'),resources=True)
 schema=declaration(period='duration',name='Revenues')
 data=resources();meta=json.loads(data[META]);meta['filings']['recent']['primaryDocument']=['primary.htm'];data[META]=canonical(meta)
 data[PREFIX+'primary.htm']=raw;data[PREFIX+'authored.xsd']=schema
 data[PREFIX+'index.json']=canonical({'directory':{'name':PREFIX.removeprefix('https://www.sec.gov').rstrip('/'),'item':[{'name':n,'size':len(data[PREFIX+n]),'type':'file'}for n in ('primary.htm','authored.xsd')]}})
 return data

def historical():
 data=resources();meta=json.loads(data[META]);cols=copy.deepcopy(meta['filings']['recent']);cols['accessionNumber']=['0000000123-23-000001'];cols['filingDate']=['2023-02-01'];cols['acceptanceDateTime']=['2023-02-01T12:00:00Z']
 name='CIK'+CIK+'-submissions-001.json';meta['filings']['files']=[{'name':name,'filingCount':1,'filingFrom':'2023-02-01','filingTo':'2023-02-01'}];data[META]=canonical(meta);data['https://data.sec.gov/submissions/'+name]=canonical(cols)
 return data,name

class SourceExpansion(unittest.IsolatedAsyncioTestCase):
 async def test_inline_primary_transform_and_exact_original_provenance(self):
  data=inline_data();c,w,_=client(data);r=await c.ingest(ACC)
  self.assertEqual(r['requests'],4);p=c.collection._filings[ACC]
  self.assertEqual(p['facts'][0]['value'],'1234.50');self.assertEqual(p['schema'],'gig.sec.xbrl.inline_set.v1')
  original=p['document_set']['documents'][0]
  self.assertEqual(original['source']['source_sha256'],hashlib.sha256(data[PREFIX+'primary.htm']).hexdigest());self.assertEqual(original['uri'],PREFIX+'primary.htm')
  self.assertEqual(original['source']['accepted_at'],'2024-02-01T12:00:00.000000001Z');self.assertFalse(p['dts_corroboration']['schema_type_validation']);self.assertTrue(p['dts_corroboration']['structural_closure'])
 async def test_inline_checkpoint_roundtrip_and_immutable_refresh(self):
  c,w,_=client(inline_data());await c.ingest(ACC);raw=c.checkpoint();r,wire,_=client();r.enabled=False;r.restore(raw,hashlib.sha256(raw).hexdigest());self.assertEqual(r.collection.page(),c.collection.page());self.assertEqual(wire.calls,[])
  w.resources[PREFIX+'primary.htm']=w.resources[PREFIX+'primary.htm'].replace(b'1,234',b'9,999')
  with self.assertRaisesRegex(IngestError,'immutable_source_changed'):await c.ingest(ACC,fresh=True)
  self.assertEqual(c.checkpoint(),raw)
 async def test_inline_unknown_transform_and_missing_continuation_are_atomic(self):
  for old,new in ((b'ixt:numdotdecimal',b'ixt:unsupported'),(b' decimals="2"',b' decimals="2" continuedAt="missing"')):
   data=inline_data();data[PREFIX+'primary.htm']=data[PREFIX+'primary.htm'].replace(old,new);idx=json.loads(data[PREFIX+'index.json']);idx['directory']['item'][0]['size']=len(data[PREFIX+'primary.htm']);data[PREFIX+'index.json']=canonical(idx);c,_,_=client(data)
   with self.assertRaises(ValueError):await c.ingest(ACC)
   self.assertEqual(c.sources,{});self.assertEqual(c.collection.page()['total'],0)
 async def test_inline_does_not_repair_non_xml_html(self):
  data=inline_data();data[PREFIX+'primary.htm']=b'<html><body>unclosed';idx=json.loads(data[PREFIX+'index.json']);idx['directory']['item'][0]['size']=len(data[PREFIX+'primary.htm']);data[PREFIX+'index.json']=canonical(idx);c,_,_=client(data)
  with self.assertRaises(ValueError):await c.ingest(ACC)
  self.assertEqual(c.plans,{})
 async def test_historical_discovery_is_deterministic_bounded_and_not_installation(self):
  data,name=historical();c,w,_=client(data);before=c.checkpoint();r=await c.discover_filings(start='2023-01-01',end='2024-12-31')
  self.assertEqual([v['filing']['filed']for v in r['entries']],['2024-02-01','2023-02-01']);self.assertEqual(r['requests'],2);self.assertFalse(r['complete_history']);self.assertEqual(c.checkpoint(),before)
  source=r['entries'][1]['metadata_sources'][0];self.assertEqual(source['sha256'],hashlib.sha256(data[source['url']]).hexdigest());self.assertEqual(r,await c.discover_filings(start='2023-01-01',end='2024-12-31'))
 async def test_shard_deferral_and_filing_limit_are_explicit(self):
  c,w,_=client(historical()[0]);r=await c.discover_filings(start='2023-01-01',end='2024-12-31',max_shards=0,max_filings=1);self.assertEqual(r['shards_deferred'],1);self.assertTrue(r['truncated']);self.assertEqual(len(w.calls),1)
  r=await c.discover_filings(start='2023-01-01',end='2024-12-31',max_filings=1);self.assertTrue(r['truncated']);self.assertEqual(len(r['entries']),1)
 async def test_query_admission_precedes_source_access(self):
  for kwargs in ({'start':'bad'},{'max_shards':True},{'max_filings':9},{'start':'2025-01-01'}):
   c,w,_=client();q={'start':'2023-01-01','end':'2024-12-31',**kwargs}
   with self.assertRaises(ValueError):await c.discover_filings(**q)
   self.assertEqual(w.calls,[])
 async def test_malicious_or_duplicate_advertisement_never_fetches_shard(self):
  for name in ('../secret.json','https://evil.invalid/a.json','CIK0000000001-submissions-001.json'):
   data,_=historical();meta=json.loads(data[META]);meta['filings']['files'][0]['name']=name;data[META]=canonical(meta);c,w,_=client(data)
   with self.assertRaisesRegex(ValueError,'shard_name'):await c.discover_filings(start='2023-01-01',end='2024-12-31')
   self.assertEqual(len(w.calls),1)
 async def test_shard_count_and_date_binding_are_checked(self):
  for field,value in (('filingCount',2),('filingFrom','2023-03-01')):
   data,_=historical();meta=json.loads(data[META]);meta['filings']['files'][0][field]=value;data[META]=canonical(meta);c,_,_=client(data)
   with self.assertRaises(ValueError):await c.discover_filings(start='2023-01-01',end='2024-12-31')
   self.assertEqual(c.plans,{})
 async def test_discovery_obeys_shared_source_lock_and_permission(self):
  c,w,_=client();await c.lock.acquire()
  try:
   with self.assertRaisesRegex(IngestError,'busy'):await c.discover_filings(start='2023-01-01',end='2024-12-31')
  finally:c.lock.release()
  c.enabled=False
  with self.assertRaisesRegex(IngestError,'disabled'):await c.discover_filings(start='2023-01-01',end='2024-12-31')
  self.assertEqual(w.calls,[])
 async def test_historical_plan_can_be_explicitly_ingested_and_restored(self):
  data,name=historical();meta=json.loads(data[META]);cols=copy.deepcopy(meta['filings']['recent']);meta['filings']['recent']={k:[]for k in cols};meta['filings']['files'][0].update(filingFrom='2024-02-01',filingTo='2024-02-01');data[META]=canonical(meta);data['https://data.sec.gov/submissions/'+name]=canonical(cols)
  c,w,_=client(data);plan=await c.discover_filings(start='2024-01-01',end='2024-12-31');self.assertEqual(plan['entries'][0]['filing']['accession'],ACC)
  result=await c.ingest(ACC,metadata_shard=name);self.assertEqual(result['requests'],6);self.assertEqual(c.collection.page()['total'],1)
  raw=c.checkpoint();r,wire,_=client();r.enabled=False;r.restore(raw,hashlib.sha256(raw).hexdigest());self.assertEqual(r.collection.page(),c.collection.page());self.assertEqual(wire.calls,[])
 async def test_unadvertised_shard_ingestion_is_rejected_before_shard_fetch(self):
  c,w,_=client()
  with self.assertRaisesRegex(IngestError,'not_advertised'):await c.ingest(ACC,metadata_shard='CIK'+CIK+'-submissions-001.json')
  self.assertEqual(len(w.calls),1);self.assertEqual(c.plans,{})
 async def test_bad_shard_ingestion_name_is_rejected_before_transport(self):
  c,w,_=client()
  with self.assertRaisesRegex(IngestError,'shard_name'):await c.ingest(ACC,metadata_shard='../secret.json')
  self.assertEqual(w.calls,[])
 async def test_contradictory_shard_rows_reject_discovery_atomically(self):
  data,name=historical();cols=json.loads(data['https://data.sec.gov/submissions/'+name]);cols['accessionNumber']=[ACC];meta=json.loads(data[META]);meta['filings']['files'][0].update(filingFrom='2023-01-01',filingTo='2024-12-31');data[META]=canonical(meta);data['https://data.sec.gov/submissions/'+name]=canonical(cols);c,_,_=client(data)
  with self.assertRaisesRegex(ValueError,'contradictory'):await c.discover_filings(start='2023-01-01',end='2024-12-31')
  self.assertEqual(c.plans,{})
 async def test_duplicate_shard_advertisement_rejects_before_shard_fetch(self):
  data,_=historical();meta=json.loads(data[META]);meta['filings']['files']*=2;data[META]=canonical(meta);c,w,_=client(data)
  with self.assertRaisesRegex(ValueError,'shard_name'):await c.discover_filings(start='2023-01-01',end='2024-12-31')
  self.assertEqual(len(w.calls),1)
 async def test_restore_revalidates_dependency_directory_advertisement(self):
  import base64
  from .xbrl_instance import digest
  c,_,_=client();await c.ingest(ACC);image=json.loads(c.checkpoint());plan=image['plans'][ACC];old=plan['index_key'];record=image['sources'].pop(old);index=json.loads(base64.b64decode(record['body_base64']));index['directory']['item']=index['directory']['item'][:1];body=canonical(index);record['body_base64']=base64.b64encode(body).decode();record['sha256']=hashlib.sha256(body).hexdigest();key=digest({'url':record['url'],'sha256':record['sha256']});plan['index_key']=key;image['sources'][key]=record;raw=canonical(image)
  r,wire,_=client();before=r.checkpoint()
  with self.assertRaisesRegex(IngestError,'dependency_binding'):r.restore(raw,hashlib.sha256(raw).hexdigest())
  self.assertEqual(r.checkpoint(),before);self.assertEqual(wire.calls,[])
 async def test_dts_reference_cannot_authorize_an_unadvertised_submissions_shard(self):
  data=resources();name='CIK'+CIK+'-submissions-999.json';url='https://data.sec.gov/submissions/'+name
  raw=data[PREFIX+'instance.xml'].replace(b'authored.xsd',url.encode());data[PREFIX+'instance.xml']=raw;index=json.loads(data[PREFIX+'index.json']);index['directory']['item'][0]['size']=len(raw);data[PREFIX+'index.json']=canonical(index);c,w,_=client(data)
  with self.assertRaisesRegex(IngestError,'outside_scope'):await c.ingest(ACC)
  self.assertFalse(any(u==url for u,_ in w.calls));self.assertEqual(c.plans,{})
