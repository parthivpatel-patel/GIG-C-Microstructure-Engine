"""Explicit bounded SEC filing/DTS acquisition with injected read-only transport.

No default transport,network activation,startup hook or automatic permission change.
Transport.open must be an async context manager whose read(n) returns at most n
bytes. Tests supply authored HTTP fixtures. Receipts are original completion times,
never filing acceptance timestamps. Source snapshots are immutable and bounded.
"""
import asyncio,base64,copy,datetime,hashlib,re,time,random
from urllib.parse import urlsplit,urljoin
from . import sec
from .retry import retry_delay
from .sec_config import user_agent_valid
from .xbrl_instance import X,L,tag,parse_xml,digest,canonical,selected_concepts,XBRLError
from .xbrl_dts import discover,EMBEDDED_PROFILE
from .xbrl_collection import FilingCollection
from .xbrl_types import COMPLEX_PROFILE
from terminal.verification.artifacts import decode,read_bytes
MAX_SOURCE=2*1024*1024;MAX_TOTAL=8*1024*1024;MAX_SOURCES=32;MAX_REQUESTS=24;MAX_IMAGE=12*1024*1024

class IngestError(ValueError):pass

def filename(value):
 if type(value)is not str or not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',value)or '..'in value:raise IngestError('sec_ingest_filename')
 return value

def clock_utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def directory(payload,cik,accession):
 root=f'/Archives/edgar/data/{int(cik)}/{accession.replace("-","")}'
 if type(payload)is not dict or type(payload.get('directory'))is not dict:raise IngestError('sec_ingest_index')
 d=payload['directory'];items=d.get('item')
 if d.get('name')not in(root,root+'/')or type(items)is not list or len(items)>1024:raise IngestError('sec_ingest_index_scope')
 out={}
 for row in items:
  if type(row)is not dict:raise IngestError('sec_ingest_index_row')
  name=filename(row.get('name'));size=row.get('size')
  if type(size)is str and re.fullmatch('[0-9]{1,10}',size):size=int(size)
  if type(size)is not int or size<0 or name in out:raise IngestError('sec_ingest_index_size_or_duplicate')
  out[name]={'name':name,'size':size,'type':row.get('type')}
 return out

class FilingIngestor:
 def __init__(self,cik,*,transport=None,permission=None,enabled=False,origin='HISTORICAL_SYNTHETIC',allow_observed=False,permission_reference=None,taxonomy_urls=(),clock=time.monotonic,receipt_clock=clock_utc,sleep=asyncio.sleep,random_source=random.random,rate_owner=None):
  self.collection=FilingCollection(cik,origin=origin,allow_observed=allow_observed)
  if type(enabled)is not bool or type(taxonomy_urls)not in(tuple,list)or len(taxonomy_urls)>32:raise IngestError('sec_ingest_configuration')
  if origin=='OBSERVED_OFFICIAL_RESPONSE'and(type(permission_reference)is not str or not 1<=len(permission_reference)<=256):raise IngestError('sec_ingest_processing_permission')
  self.cik=cik;self.transport=transport;self.permission=permission;self.enabled=enabled;self.origin=origin;self.allow_observed=allow_observed;self.reference=permission_reference;self.taxonomy_urls=frozenset(taxonomy_urls)
  for url in self.taxonomy_urls:
   u=urlsplit(url)
   if u.scheme!='https'or u.netloc not in('www.xbrl.org','xbrl.fasb.org','xbrl.sec.gov')or u.query or u.fragment or '%'in u.path or '..'in u.path:raise IngestError('sec_ingest_taxonomy_allowlist')
  self.clock=clock;self.receipt_clock=receipt_clock;self.sleep=sleep;self.random=random_source;self.last_request=-1e20;self.sources={};self.plans={};self.cache={};self.lock=rate_owner.lock if rate_owner is not None else asyncio.Lock();self.rate_owner=rate_owner;self.state='IDLE';self.last_error=None;self.last_http_status=None;self.metrics={'attempts':0,'received_bytes':0,'cache_hits':0,'committed_filings':0,'failed_transactions':0}
 def status(self):
  return {'schema':'gig.sec.filing_ingestion.status.v1','state':self.state,'issuer_cik':self.cik,'enabled':self.enabled,'live_stream_connected':False,'retained_filings':len(self.plans),'source_records':len(self.sources),'last_error':self.last_error,'http_status':self.last_http_status,'metrics':{k:str(v)for k,v in self.metrics.items()},'counter_scope':'This coordinator process lifetime,not complete provider-source accounting'}
 def _headers(self):
  if not self.enabled or self.transport is None or self.permission is None:raise IngestError('sec_ingest_disabled')
  try:h=self.permission()
  except ValueError:raise IngestError('sec_ingest_source_permission')from None
  if type(h)is not dict or not user_agent_valid(h.get('User-Agent')):raise IngestError('sec_ingest_identification_required')
  return {'User-Agent':h['User-Agent'],'Accept-Encoding':'identity'}
 def _url(self,url,accession):
  if type(url)is not str or not 1<=len(url)<=512:raise IngestError('sec_ingest_url')
  u=urlsplit(url)
  if u.scheme!='https'or u.username or u.password or u.query or u.fragment or '%'in url or '\\'in url or any(ord(c)<33 for c in url):raise IngestError('sec_ingest_url')
  if url in self.taxonomy_urls:return url
  if url==f'https://data.sec.gov/submissions/CIK{self.cik}.json':return url
  prefix=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{accession.replace("-","")}/'
  if not url.startswith(prefix):raise IngestError('sec_ingest_reference_outside_scope')
  filename(url[len(prefix):]);return url
 async def _read(self,url,accession,stage,budget,*,fresh=False):
  self._url(url,accession);self._headers()
  cached=self.cache.get(url)
  if not fresh and cached and 0<=self.clock()-cached[0]<600 and cached[1]in self.sources:
   self.metrics['cache_hits']+=1;stage[cached[1]]=self.sources[cached[1]];return cached[1]
  for attempt in range(2):
   if budget['requests']>=MAX_REQUESTS:raise IngestError('sec_ingest_request_budget')
   headers=self._headers();previous=max(self.last_request,self.rate_owner.last_request)if self.rate_owner is not None else self.last_request
   await self.sleep(max(0,1.01-(self.clock()-previous)));self.last_request=self.clock()
   if self.rate_owner is not None:self.rate_owner.last_request=self.last_request
   budget['requests']+=1;self.metrics['attempts']+=1
   try:
    async with self.transport.open(url,headers,timeout=8)as response:
     if type(response.status)is not int or not 100<=response.status<=599:raise IngestError('sec_ingest_http_status_contract')
     self.last_http_status=response.status
     if response.url!=url:raise IngestError('sec_ingest_redirect')
     if response.status in(429,503):
      if attempt:raise IngestError('sec_ingest_retry_exhausted')
      floor=response.headers.get('retry-after','0')
      if not re.fullmatch('[0-9]{1,2}',floor)or int(floor)>30:raise IngestError('sec_ingest_retry_after')
      delay=retry_delay(attempt+1,minimum=int(floor),random_source=self.random)
     elif response.status!=200:raise IngestError('sec_ingest_http_status')
     else:
      if response.headers.get('content-encoding','identity').lower()not in('identity',''):raise IngestError('sec_ingest_encoding')
      length=response.headers.get('content-length');declared=None
      if length is not None:
       if not re.fullmatch('[0-9]{1,10}',length)or not 0<int(length)<=MAX_SOURCE:raise IngestError('sec_ingest_content_length')
       declared=int(length)
      blocks=[];size=0
      while True:
       remaining=min(MAX_SOURCE-size,MAX_TOTAL-budget['bytes'])
       if remaining<=0:raise IngestError('sec_ingest_body_budget')
       block=await asyncio.wait_for(response.read(min(65536,remaining)),8)
       if type(block)is not bytes or len(block)>min(65536,remaining):raise IngestError('sec_ingest_transport_read_contract')
       if not block:break
       size+=len(block);budget['bytes']+=len(block);self.metrics['received_bytes']+=len(block)
       if declared is not None and size>declared:raise IngestError('sec_ingest_length_mismatch')
       blocks.append(block)
      if size==0 or declared is not None and size!=declared:raise IngestError('sec_ingest_length_mismatch')
      body=b''.join(blocks);received=self.receipt_clock();sec.acceptance_ns(received);record={'url':url,'sha256':hashlib.sha256(body).hexdigest(),'received_at':received,'body':body};key=digest({'url':url,'sha256':record['sha256']})
      if key in self.sources:record=self.sources[key]
      stage[key]=record;return key
   except TimeoutError:
    if attempt:raise IngestError('sec_ingest_timeout')from None
    delay=retry_delay(attempt+1,random_source=self.random)
   await self.sleep(delay)
  raise IngestError('sec_ingest_retry_exhausted')
 def _entries(self,plans,sources):
  entries=[]
  for plan in plans.values():
   metadata=plan['metadata'];raw=sources[plan['instance_key']];recorded=sec.filings(decode(sources[plan['metadata_key']]['body']),self.cik,limit=1024)
   if metadata not in recorded['filings']:raise IngestError('sec_ingest_metadata_binding')
   prefix=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{metadata["accession"].replace("-","")}/'
   if sources[plan['metadata_key']]['url']!=f'https://data.sec.gov/submissions/CIK{self.cik}.json'or sources[plan['index_key']]['url']!=prefix+'index.json':raise IngestError('sec_ingest_metadata_source_url')
   available=directory(decode(sources[plan['index_key']]['body']),self.cik,metadata['accession']);name=filename(raw['url'].rsplit('/',1)[-1])
   if name not in available or available[name]['type']!='file'or available[name]['size']!=len(raw['body'])or raw['url']!=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{metadata["accession"].replace("-","")}/{name}':raise IngestError('sec_ingest_document_binding')
   manifest={'issuer_cik':self.cik,'accession':metadata['accession'],'form':metadata['form'],'filed':metadata['filed'],'accepted_at':metadata['accepted_at'],'received_at':raw['received_at'],'origin':self.origin,'source_sha256':raw['sha256'],'source_url':raw['url'],'amends_accession':plan['amends_accession'],'permission_reference':self.reference}
   docs=[{'uri':sources[k]['url'],'raw':sources[k]['body'],'sha256':sources[k]['sha256']}for k in plan['document_keys']]
   entries.append({'raw':raw['body'],'manifest':manifest,'concepts':selected_concepts(plan['gaap_namespace']),'instance_uri':raw['url'],'documents':docs})
  return entries
 def _rebuild(self,plans,sources):
  c=FilingCollection(self.cik,origin=self.origin,allow_observed=self.allow_observed);entries=self._entries(plans,sources)
  for entry in entries:
   g=discover(entry['raw'],entry['instance_uri'],entry['manifest']['source_sha256'],entry['documents'],origin=self.origin,allow_observed=self.allow_observed,permission_reference=self.reference,embedded_profile=EMBEDDED_PROFILE)
   if not g['structural_closure']:raise IngestError('sec_ingest_checkpoint_dependencies')
   namespaces={q[1:].split('}',1)[0]for q in g['concepts']if re.fullmatch(r'\{https?://fasb\.org/us-gaap/[0-9]{4}\}.+',q)}
   expected=next(iter(entry['concepts'])).split('}',1)[0][1:]
   if namespaces!={expected}:raise IngestError('sec_ingest_checkpoint_taxonomy_scope')
  for i in range(0,len(entries),8):c.ingest_dts_batch(entries[i:i+8],numeric_profile=COMPLEX_PROFILE,embedded_profile=EMBEDDED_PROFILE)
  return c
 async def ingest(self,accession,*,document=None,amends_accession=None,fresh=False,store=None):
  if type(accession)is not str or not re.fullmatch('[0-9]{10}-[0-9]{2}-[0-9]{6}',accession):raise IngestError('sec_ingest_accession')
  if document is not None:filename(document)
  if type(fresh)is not bool:raise IngestError('sec_ingest_query')
  self._headers()
  if self.lock.locked():raise IngestError('sec_ingest_busy')
  async with self.lock:
   self.state='LOADING';stage={};budget={'requests':0,'bytes':0}
   try:
    async with asyncio.timeout(30):
     meta=await self._read(f'https://data.sec.gov/submissions/CIK{self.cik}.json',accession,stage,budget,fresh=fresh);rows=sec.filings(decode(stage[meta]['body']),self.cik,limit=1024)['filings'];matches=[r for r in rows if r['accession']==accession]
     if len(matches)!=1 or matches[0]['form']not in('10-K','10-K/A','10-Q','10-Q/A'):raise IngestError('sec_ingest_filing_not_advertised')
     row=matches[0];prefix=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{accession.replace("-","")}/';index=await self._read(prefix+'index.json',accession,stage,budget,fresh=fresh);items=directory(decode(stage[index]['body']),self.cik,accession);name=document or row['url'].rsplit('/',1)[-1]
     if name not in items or items[name]['type']!='file'or items[name]['size']>MAX_SOURCE:raise IngestError('sec_ingest_document_not_eligible')
     if not name.lower().endswith('.xml'):raise IngestError('sec_ingest_primary_format_unsupported')
     instance=await self._read(prefix+name,accession,stage,budget,fresh=fresh);original=stage[instance]
     if len(original['body'])!=items[name]['size']:raise IngestError('sec_ingest_index_length')
     root=parse_xml(original['body'])
     if root.name!=tag(X,'xbrl'):raise IngestError('sec_ingest_instance_format_unsupported')
     docs={};graph=None
     for _ in range(17):
      graph=discover(original['body'],original['url'],original['sha256'],list(docs.values()),origin=self.origin,allow_observed=self.allow_observed,permission_reference=self.reference,embedded_profile=EMBEDDED_PROFILE)
      if not graph['unresolved']:break
      for missing in graph['unresolved']:
       if 'uri'not in missing:raise IngestError('sec_ingest_dependency_location_unknown')
       url=self._url(missing['uri'],accession)
       if url in docs:raise IngestError('sec_ingest_dependency_stalled')
       if len(docs)>=16:raise IngestError('sec_ingest_dependency_budget')
       local=url.startswith(prefix)
       local_name=url[len(prefix):]if local else None
       if local and(local_name not in items or items[local_name]['type']!='file'or not 0<items[local_name]['size']<=MAX_SOURCE):raise IngestError('sec_ingest_dependency_not_advertised')
       key=await self._read(url,accession,stage,budget,fresh=fresh);r=stage[key]
       if local and len(r['body'])!=items[local_name]['size']:raise IngestError('sec_ingest_index_length')
       docs[url]={'uri':url,'raw':r['body'],'sha256':r['sha256']}
     if graph is None or not graph['structural_closure']:raise IngestError('sec_ingest_dependency_incomplete')
     namespaces={q[1:].split('}',1)[0]for q in graph['concepts']if re.fullmatch(r'\{https?://fasb\.org/us-gaap/[0-9]{4}\}.+',q)}
     if len(namespaces)!=1:raise IngestError('sec_ingest_taxonomy_selection_ambiguous')
     doc_keys=[digest({'url':d['uri'],'sha256':d['sha256']})for d in docs.values()];plan={'metadata':row,'metadata_key':meta,'index_key':index,'instance_key':instance,'document_keys':doc_keys,'gaap_namespace':next(iter(namespaces)),'amends_accession':amends_accession}
     plans={**self.plans,accession:plan};sources={**self.sources,**stage}
     used={k for p in plans.values()for k in[p['metadata_key'],p['index_key'],p['instance_key'],*p['document_keys']]}
     sources={k:v for k,v in sources.items()if k in used}
     if len(plans)>8 or len(sources)>MAX_SOURCES or sum(len(r['body'])for r in sources.values())>MAX_TOTAL:raise IngestError('sec_ingest_retained_budget')
     # An already admitted resource URI cannot silently acquire different bytes.
     admitted={self.sources[k]['url']:self.sources[k]['sha256']for p in self.plans.values()for k in[p['instance_key'],*p['document_keys']]}
     if any(r['url']in admitted and admitted[r['url']]!=r['sha256']for r in stage.values()):raise IngestError('sec_ingest_immutable_source_changed')
     previous=self.plans.get(accession)
     if previous is not None and any(previous[k]!=plan[k]for k in('metadata','instance_key','gaap_namespace','amends_accession')):raise IngestError('sec_ingest_immutable_filing_changed')
     if previous is not None and set(previous['document_keys'])!=set(plan['document_keys']):raise IngestError('sec_ingest_immutable_filing_changed')
     candidate=self._rebuild(plans,sources)
     if store is not None:store.save(self._image(plans,sources,candidate))
     self.plans=plans;self.sources=sources;self.collection=candidate;self.cache={url:v for url,v in self.cache.items()if v[1]in sources};self.cache.update({r['url']:(self.clock(),k)for k,r in stage.items()if k in sources});self.state='ACCEPTED';self.last_error=None;self.metrics['committed_filings']=len(plans)
     return {'schema':'gig.sec.filing_ingestion.v1','status':'ACCEPTED','origin':self.origin,'issuer_cik':self.cik,'filings':len(plans),'collection_sha256':candidate._identity(candidate._filings),'requests':budget['requests'],'response_bytes':budget['bytes'],'complete_history':False,'live_stream_connected':False,'scope':'Bounded read-only source transaction;not streaming or independent source authentication'}
   except BaseException as exc:
    self.state='CANCELLED'if isinstance(exc,asyncio.CancelledError)else'FAILED';self.last_error=str(exc)if isinstance(exc,IngestError)else'sec_ingest_validation_or_resource_failure';self.metrics['failed_transactions']+=1;raise
 def _image(self,plans,sources,collection):
  core={'schema':'gig.sec.filing_ingestion.checkpoint.v1','issuer_cik':self.cik,'origin':self.origin,'permission_reference_sha256':hashlib.sha256(self.reference.encode()).hexdigest()if self.reference is not None else None,'taxonomy_urls':sorted(self.taxonomy_urls),'plans':plans,'sources':{k:{**{a:r[a]for a in('url','sha256','received_at')},'body_base64':base64.b64encode(r['body']).decode()}for k,r in sources.items()},'collection_sha256':collection._identity(collection._filings)}
  raw=canonical(core)
  if len(raw)>MAX_IMAGE:raise IngestError('sec_ingest_checkpoint_budget')
  return raw
 def checkpoint(self):return self._image(self.plans,self.sources,self.collection)
 def restore(self,raw,expected_sha256):
  # Synchronous admission on the owning event loop;never replace an in-flight
  # transaction (including another workspace source sharing this rate lock).
  if self.lock.locked():raise IngestError('sec_ingest_busy')
  if type(raw)is not bytes or len(raw)>MAX_IMAGE or hashlib.sha256(raw).hexdigest()!=expected_sha256:raise IngestError('sec_ingest_checkpoint_integrity')
  v=decode(raw)
  if set(v)!={'schema','issuer_cik','origin','permission_reference_sha256','taxonomy_urls','plans','sources','collection_sha256'}or v['schema']!='gig.sec.filing_ingestion.checkpoint.v1'or v['issuer_cik']!=self.cik or v['origin']!=self.origin or v['taxonomy_urls']!=sorted(self.taxonomy_urls)or v['permission_reference_sha256']!=(hashlib.sha256(self.reference.encode()).hexdigest()if self.reference is not None else None):raise IngestError('sec_ingest_checkpoint_scope')
  if type(v['sources'])is not dict or len(v['sources'])>MAX_SOURCES or type(v['plans'])is not dict or len(v['plans'])>8:raise IngestError('sec_ingest_checkpoint_counts')
  sources={};total=0
  for key,r in v['sources'].items():
   if type(r)is not dict or set(r)!={'url','sha256','received_at','body_base64'}or type(r['body_base64'])is not str or len(r['body_base64'])>4*((MAX_SOURCE+2)//3):raise IngestError('sec_ingest_checkpoint_source')
   try:body=base64.b64decode(r['body_base64'],validate=True)
   except ValueError:raise IngestError('sec_ingest_checkpoint_base64')from None
   total+=len(body)
   if len(body)>MAX_SOURCE or total>MAX_TOTAL or hashlib.sha256(body).hexdigest()!=r['sha256']or key!=digest({'url':r['url'],'sha256':r['sha256']}):raise IngestError('sec_ingest_checkpoint_source_integrity')
   sec.acceptance_ns(r['received_at']);sources[key]={k:r[k]for k in('url','sha256','received_at')};sources[key]['body']=body
  used=set()
  for accession,plan in v['plans'].items():
   if type(plan)is not dict or set(plan)!={'metadata','metadata_key','index_key','instance_key','document_keys','gaap_namespace','amends_accession'}or type(plan['metadata'])is not dict or plan['metadata'].get('accession')!=accession:raise IngestError('sec_ingest_checkpoint_plan')
   if type(plan['document_keys'])is not list or len(plan['document_keys'])>16 or len(set(plan['document_keys']))!=len(plan['document_keys']):raise IngestError('sec_ingest_checkpoint_document_budget')
   for key in[plan['metadata_key'],plan['index_key'],plan['instance_key'],*plan['document_keys']]:
    if type(key)is not str or key not in sources:raise IngestError('sec_ingest_checkpoint_source_reference')
    self._url(sources[key]['url'],accession);used.add(key)
  if used!=set(sources):raise IngestError('sec_ingest_checkpoint_unused_source')
  candidate=self._rebuild(v['plans'],sources)
  if candidate._identity(candidate._filings)!=v['collection_sha256']:raise IngestError('sec_ingest_checkpoint_collection')
  self.sources=sources;self.plans=v['plans'];self.collection=candidate;self.cache={};self.state='PAUSED_RESTORED';self.last_error=None
  return {'status':self.state,'collection_sha256':v['collection_sha256'],'filings':len(self.plans),'network_used':False}
