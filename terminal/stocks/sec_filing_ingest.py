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

def source_keys(plan):return [plan['metadata_key'],plan['index_key'],plan['instance_key'],*plan['document_keys']]+([plan['history_key']]if 'history_key'in plan else[])+plan.get('inline_keys',[])

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
 def _url(self,url,accession,*,submission_shard=False):
  if type(url)is not str or not 1<=len(url)<=512:raise IngestError('sec_ingest_url')
  u=urlsplit(url)
  if u.scheme!='https'or u.username or u.password or u.query or u.fragment or '%'in url or '\\'in url or any(ord(c)<33 for c in url):raise IngestError('sec_ingest_url')
  if url in self.taxonomy_urls:return url
  if url==f'https://data.sec.gov/submissions/CIK{self.cik}.json':return url
  if submission_shard and re.fullmatch(r'https://data\.sec\.gov/submissions/CIK'+self.cik+r'-submissions-[0-9]{3}\.json',url):return url
  prefix=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{accession.replace("-","")}/'
  if not url.startswith(prefix):raise IngestError('sec_ingest_reference_outside_scope')
  filename(url[len(prefix):]);return url
 async def _read(self,url,accession,stage,budget,*,fresh=False,submission_shard=False):
  self._url(url,accession,submission_shard=submission_shard);self._headers()
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
 def _manifest(self,row,raw,amends_accession):
  return {'issuer_cik':self.cik,'accession':row['accession'],'form':row['form'],'filed':row['filed'],'accepted_at':row['accepted_at'],'received_at':raw['received_at'],'origin':self.origin,'source_sha256':raw['sha256'],'source_url':raw['url'],'amends_accession':amends_accession,'permission_reference':self.reference}
 def _inline_inputs(self,plan,sources,available,prefix):
  from .sec_inline_manifest import normalize
  manifest=normalize(plan['inline_manifest'],self.cik,plan['metadata']['accession'])
  if manifest!=plan['inline_manifest']or plan['inline_manifest_sha256']!=digest(manifest):raise IngestError('sec_inline_manifest_identity')
  keys=plan['inline_keys']
  if type(keys)is not list or len(keys)!=len(manifest['documents'])or any(type(k)is not str or k not in sources for k in keys)or len(set(keys))!=len(keys):raise IngestError('sec_inline_manifest_sources')
  originals=[]
  for expected,key in zip(manifest['documents'],keys):
   raw=sources[key];name=expected['name']
   if raw['url']!=prefix+name or raw['sha256']!=expected['sha256']or name not in available or available[name]['type']!='file'or available[name]['size']!=len(raw['body']):raise IngestError('sec_inline_manifest_source_binding')
   originals.append({'uri':raw['url'],'raw':raw['body'],'manifest':self._manifest(plan['metadata'],raw,plan['amends_accession'])})
  primary=prefix+manifest['primary_document']
  if sources[plan['instance_key']]['url']!=primary or plan['metadata']['url']!=primary or plan['instance_key']not in keys:raise IngestError('sec_inline_manifest_primary_binding')
  return originals
 def _graph(self,entry,documents):
  if 'inline_documents'in entry:
   from .inline_set import parse_document_set
   from .xbrl_dts import discover_inline_set
   parsed=parse_document_set(entry['inline_documents'],entry['concepts'],allow_observed=self.allow_observed)
   return discover_inline_set(parsed,documents,allow_observed=self.allow_observed,permission_references=[self.reference]*len(entry['inline_documents']),embedded_profile=EMBEDDED_PROFILE)
  return discover(entry['raw'],entry['instance_uri'],entry['manifest']['source_sha256'],documents,origin=self.origin,allow_observed=self.allow_observed,permission_reference=self.reference,embedded_profile=EMBEDDED_PROFILE)
 def _entries(self,plans,sources):
  entries=[]
  for plan in plans.values():
   metadata=plan['metadata'];raw=sources[plan['instance_key']];payload=decode(sources[plan['metadata_key']]['body']);recorded=sec.filings(payload,self.cik,limit=1024)
   if 'history_key'in plan:
    from .sec_filing_schedule import historical_rows
    history=sources[plan['history_key']];name=history['url'].removeprefix('https://data.sec.gov/submissions/')
    historical=historical_rows(payload,decode(history['body']),name,self.cik)
    current={r['accession']:r for r in recorded['filings']}
    if any(r['accession']in current and current[r['accession']]!=r for r in historical['filings']):raise IngestError('sec_schedule_contradictory_filing')
    recorded=historical
   if metadata not in recorded['filings']:raise IngestError('sec_ingest_metadata_binding')
   prefix=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{metadata["accession"].replace("-","")}/'
   if sources[plan['metadata_key']]['url']!=f'https://data.sec.gov/submissions/CIK{self.cik}.json'or sources[plan['index_key']]['url']!=prefix+'index.json':raise IngestError('sec_ingest_metadata_source_url')
   available=directory(decode(sources[plan['index_key']]['body']),self.cik,metadata['accession']);name=filename(raw['url'].rsplit('/',1)[-1])
   if name not in available or available[name]['type']!='file'or available[name]['size']!=len(raw['body'])or raw['url']!=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{metadata["accession"].replace("-","")}/{name}':raise IngestError('sec_ingest_document_binding')
   manifest={'issuer_cik':self.cik,'accession':metadata['accession'],'form':metadata['form'],'filed':metadata['filed'],'accepted_at':metadata['accepted_at'],'received_at':raw['received_at'],'origin':self.origin,'source_sha256':raw['sha256'],'source_url':raw['url'],'amends_accession':plan['amends_accession'],'permission_reference':self.reference}
   for key in plan['document_keys']:
    resource=sources[key];self._url(resource['url'],metadata['accession'])
    if resource['url'].startswith(prefix):
     local=resource['url'][len(prefix):]
     if local not in available or available[local]['type']!='file'or available[local]['size']!=len(resource['body']):raise IngestError('sec_ingest_dependency_binding')
   docs=[{'uri':sources[k]['url'],'raw':sources[k]['body'],'sha256':sources[k]['sha256']}for k in plan['document_keys']]
   entry={'raw':raw['body'],'manifest':manifest,'concepts':selected_concepts(plan['gaap_namespace']),'instance_uri':raw['url'],'documents':docs}
   if 'inline_manifest'in plan:entry['inline_documents']=self._inline_inputs(plan,sources,available,prefix)
   entries.append(entry)
  return entries
 def _rebuild(self,plans,sources):
  c=FilingCollection(self.cik,origin=self.origin,allow_observed=self.allow_observed);entries=self._entries(plans,sources)
  for entry in entries:
   g=self._graph(entry,entry['documents'])
   if not g['structural_closure']:raise IngestError('sec_ingest_checkpoint_dependencies')
   namespaces={q[1:].split('}',1)[0]for q in g['concepts']if re.fullmatch(r'\{https?://fasb\.org/us-gaap/[0-9]{4}\}.+',q)}
   expected=next(iter(entry['concepts'])).split('}',1)[0][1:]
   if namespaces!={expected}:raise IngestError('sec_ingest_checkpoint_taxonomy_scope')
  for entry in entries:
   if 'inline_documents'not in entry and parse_xml(entry['raw']).name==tag(X,'xbrl'):
    c.ingest_dts_batch([entry],numeric_profile=COMPLEX_PROFILE,embedded_profile=EMBEDDED_PROFILE)
   else:
    # A single acquired original is an explicit one-document set. Never repair
    # HTML or discover sibling documents from arbitrary hyperlinks.
    c.ingest_inline_set_batch([{'documents':entry.get('inline_documents',[{'uri':entry['instance_uri'],'raw':entry['raw'],'manifest':entry['manifest']}]),'concepts':entry['concepts'],'taxonomy_documents':entry['documents']}],numeric_profile=COMPLEX_PROFILE,embedded_profile=EMBEDDED_PROFILE)
  return c
 async def discover_filings(self,*,start,end,max_shards=2,max_filings=8):
  """Explicit bounded metadata scan. Returns a plan; never executes filings.

  Shards are admitted only from this transaction's issuer submissions index.
  No discovery record is published into the accepted collection/checkpoint.
  """
  from .sec_filing_schedule import query,shards,schedule
  query(start,end,max_shards,max_filings);self._headers()
  if self.lock.locked():raise IngestError('sec_ingest_busy')
  async with self.lock:
   stage={};budget={'requests':0,'bytes':0}
   async with asyncio.timeout(30):
    key=await self._read(f'https://data.sec.gov/submissions/CIK{self.cik}.json','',stage,budget,fresh=True)
    payload=decode(stage[key]['body']);recent=sec.filings(payload,self.cik,limit=1024)
    advertised=shards(payload,self.cik,start,end)
    def source(k):return {a:stage[k][a]for a in('url','sha256','received_at')}
    groups=[(recent['filings'],source(key))];row_truncated=recent['integrity']['truncated']
    for item in advertised[:max_shards]:
     k=await self._read('https://data.sec.gov/submissions/'+item['name'],'',stage,budget,fresh=True,submission_shard=True)
     columns=decode(stage[k]['body'])
     if type(columns)is not dict or type(columns.get('form'))is not list or len(columns['form'])!=item['count']:raise IngestError('sec_schedule_shard_count_binding')
     parsed=sec.filings({'cik':self.cik,'filings':{'recent':columns}},self.cik,limit=1024)
     if any(not item['start']<=r['filed']<=item['end']for r in parsed['filings']):raise IngestError('sec_schedule_shard_date_binding')
     row_truncated|=parsed['integrity']['truncated'];groups.append((parsed['filings'],source(k)))
    rows,truncated=schedule(groups,start,end,max_filings)
    return {'schema':'gig.sec.filing_schedule.v1','issuer_cik':self.cik,'start':start,'end':end,'entries':rows,'shards_read':min(len(advertised),max_shards),'shards_deferred':max(0,len(advertised)-max_shards),'truncated':truncated or row_truncated or len(advertised)>max_shards,'complete_history':False,'requests':budget['requests'],'response_bytes':budget['bytes'],'scope':'Explicit metadata plan only;explicit ingest requires advertised shard name and independent source revalidation'}
 async def ingest(self,accession,*,document=None,amends_accession=None,fresh=False,store=None,metadata_shard=None,inline_manifest=None):
  if type(accession)is not str or not re.fullmatch('[0-9]{10}-[0-9]{2}-[0-9]{6}',accession):raise IngestError('sec_ingest_accession')
  if document is not None:filename(document)
  if inline_manifest is not None:
   from .sec_inline_manifest import normalize
   inline_manifest=normalize(inline_manifest,self.cik,accession)
   if document is not None and document!=inline_manifest['primary_document']:raise IngestError('sec_inline_manifest_primary_binding')
  if metadata_shard is not None and(type(metadata_shard)is not str or not re.fullmatch('CIK'+self.cik+r'-submissions-[0-9]{3}\.json',metadata_shard)):raise IngestError('sec_schedule_shard_name')
  if type(fresh)is not bool:raise IngestError('sec_ingest_query')
  self._headers()
  if self.lock.locked():raise IngestError('sec_ingest_busy')
  async with self.lock:
   self.state='LOADING';stage={};budget={'requests':0,'bytes':0}
   try:
    async with asyncio.timeout(30):
     meta=await self._read(f'https://data.sec.gov/submissions/CIK{self.cik}.json',accession,stage,budget,fresh=fresh);payload=decode(stage[meta]['body']);rows=sec.filings(payload,self.cik,limit=1024)['filings'];history=None
     if metadata_shard is not None:
      from .sec_filing_schedule import shards,historical_rows
      if metadata_shard not in [r['name']for r in shards(payload,self.cik,'0001-01-01','9999-12-31')]:raise IngestError('sec_schedule_shard_not_advertised')
      history=await self._read('https://data.sec.gov/submissions/'+metadata_shard,accession,stage,budget,fresh=fresh,submission_shard=True)
      historical=historical_rows(payload,decode(stage[history]['body']),metadata_shard,self.cik)['filings'];current={r['accession']:r for r in rows}
      if any(r['accession']in current and current[r['accession']]!=r for r in historical):raise IngestError('sec_schedule_contradictory_filing')
      rows=historical
     matches=[r for r in rows if r['accession']==accession]
     if len(matches)!=1 or matches[0]['form']not in('10-K','10-K/A','10-Q','10-Q/A'):raise IngestError('sec_ingest_filing_not_advertised')
     row=matches[0];prefix=f'https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{accession.replace("-","")}/';index=await self._read(prefix+'index.json',accession,stage,budget,fresh=fresh);items=directory(decode(stage[index]['body']),self.cik,accession);name=document or row['url'].rsplit('/',1)[-1]
     if inline_manifest is not None and(name!=inline_manifest['primary_document']or prefix+name!=row['url']):raise IngestError('sec_inline_manifest_primary_binding')
     if name not in items or items[name]['type']!='file'or items[name]['size']>MAX_SOURCE:raise IngestError('sec_ingest_document_not_eligible')
     if not name.lower().endswith(('.xml','.htm','.html','.xhtml')):raise IngestError('sec_ingest_primary_format_unsupported')
     instance=await self._read(prefix+name,accession,stage,budget,fresh=fresh);original=stage[instance]
     if len(original['body'])!=items[name]['size']:raise IngestError('sec_ingest_index_length')
     if inline_manifest is not None and original['sha256']!=next(d['sha256']for d in inline_manifest['documents']if d['name']==name):raise IngestError('sec_inline_manifest_source_binding')
     root=parse_xml(original['body'])
     if root.name not in(tag(X,'xbrl'),tag('http://www.w3.org/1999/xhtml','html')):raise IngestError('sec_ingest_instance_format_unsupported')
     entry={'raw':original['body'],'instance_uri':original['url'],'manifest':self._manifest(row,original,amends_accession),'concepts':{}};inline_keys=[]
     if inline_manifest is not None:
      # Preflight all advertised members before any supplemental read.
      if any(d['name']not in items or items[d['name']]['type']!='file'or not 0<items[d['name']]['size']<=MAX_SOURCE for d in inline_manifest['documents']):raise IngestError('sec_inline_manifest_not_advertised')
      if sum(items[d['name']]['size']for d in inline_manifest['documents'])>MAX_TOTAL:raise IngestError('sec_inline_manifest_byte_budget')
      for d in inline_manifest['documents']:
       key=instance if d['name']==name else await self._read(prefix+d['name'],accession,stage,budget,fresh=fresh)
       inline_keys.append(key)
      temporary={'inline_manifest':inline_manifest,'inline_manifest_sha256':digest(inline_manifest),'inline_keys':inline_keys,'metadata':row,'instance_key':instance,'amends_accession':amends_accession}
      entry['inline_documents']=self._inline_inputs(temporary,stage,items,prefix)
     docs={};graph=None
     for _ in range(17):
      graph=self._graph(entry,list(docs.values()))
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
     if history is not None:plan['history_key']=history
     if inline_manifest is not None:plan.update(inline_manifest=inline_manifest,inline_manifest_sha256=digest(inline_manifest),inline_keys=inline_keys)
     plans={**self.plans,accession:plan};sources={**self.sources,**stage}
     used={k for p in plans.values()for k in source_keys(p)}
     sources={k:v for k,v in sources.items()if k in used}
     if len(plans)>8 or len(sources)>MAX_SOURCES or sum(len(r['body'])for r in sources.values())>MAX_TOTAL:raise IngestError('sec_ingest_retained_budget')
     # An already admitted resource URI cannot silently acquire different bytes.
     admitted={self.sources[k]['url']:self.sources[k]['sha256']for p in self.plans.values()for k in[p['instance_key'],*p['document_keys'],*p.get('inline_keys',[])]}
     if any(r['url']in admitted and admitted[r['url']]!=r['sha256']for r in stage.values()):raise IngestError('sec_ingest_immutable_source_changed')
     previous=self.plans.get(accession)
     if previous is not None and previous.get('inline_manifest')!=plan.get('inline_manifest'):raise IngestError('sec_inline_manifest_immutable')
     if previous is not None and any(previous[k]!=plan[k]for k in('metadata','instance_key','gaap_namespace','amends_accession')):raise IngestError('sec_ingest_immutable_filing_changed')
     if previous is not None and set(previous['document_keys'])!=set(plan['document_keys']):raise IngestError('sec_ingest_immutable_filing_changed')
     candidate=self._rebuild(plans,sources)
     if store is not None:store.save(self._image(plans,sources,candidate))
     self.plans=plans;self.sources=sources;self.collection=candidate;self.cache={url:v for url,v in self.cache.items()if v[1]in sources};self.cache.update({r['url']:(self.clock(),k)for k,r in stage.items()if k in sources});self.state='ACCEPTED';self.last_error=None;self.metrics['committed_filings']=len(plans)
     return {'schema':'gig.sec.filing_ingestion.v1','status':'ACCEPTED','origin':self.origin,'issuer_cik':self.cik,'filings':len(plans),'collection_sha256':candidate._identity(candidate._filings),'requests':budget['requests'],'response_bytes':budget['bytes'],'complete_history':False,'live_stream_connected':False,'scope':'Bounded read-only source transaction;not streaming or independent source authentication'}
   except BaseException as exc:
    self.state='CANCELLED'if isinstance(exc,asyncio.CancelledError)else'FAILED';self.last_error=str(exc)if isinstance(exc,IngestError)else'sec_ingest_validation_or_resource_failure';self.metrics['failed_transactions']+=1;raise
 def _image(self,plans,sources,collection):
  core={'schema':'gig.sec.filing_ingestion.checkpoint.v3'if any('inline_manifest'in p for p in plans.values())else'gig.sec.filing_ingestion.checkpoint.v2'if any('history_key'in p for p in plans.values())else'gig.sec.filing_ingestion.checkpoint.v1','issuer_cik':self.cik,'origin':self.origin,'permission_reference_sha256':hashlib.sha256(self.reference.encode()).hexdigest()if self.reference is not None else None,'taxonomy_urls':sorted(self.taxonomy_urls),'plans':plans,'sources':{k:{**{a:r[a]for a in('url','sha256','received_at')},'body_base64':base64.b64encode(r['body']).decode()}for k,r in sources.items()},'collection_sha256':collection._identity(collection._filings)}
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
  if set(v)!={'schema','issuer_cik','origin','permission_reference_sha256','taxonomy_urls','plans','sources','collection_sha256'}or v['schema']not in('gig.sec.filing_ingestion.checkpoint.v1','gig.sec.filing_ingestion.checkpoint.v2','gig.sec.filing_ingestion.checkpoint.v3')or v['issuer_cik']!=self.cik or v['origin']!=self.origin or v['taxonomy_urls']!=sorted(self.taxonomy_urls)or v['permission_reference_sha256']!=(hashlib.sha256(self.reference.encode()).hexdigest()if self.reference is not None else None):raise IngestError('sec_ingest_checkpoint_scope')
  if type(v['sources'])is not dict or len(v['sources'])>MAX_SOURCES or type(v['plans'])is not dict or len(v['plans'])>8:raise IngestError('sec_ingest_checkpoint_counts')
  sources={};total=0
  for key,r in v['sources'].items():
   if type(r)is not dict or set(r)!={'url','sha256','received_at','body_base64'}or type(r['body_base64'])is not str or len(r['body_base64'])>4*((MAX_SOURCE+2)//3):raise IngestError('sec_ingest_checkpoint_source')
   try:body=base64.b64decode(r['body_base64'],validate=True)
   except ValueError:raise IngestError('sec_ingest_checkpoint_base64')from None
   total+=len(body)
   if len(body)>MAX_SOURCE or total>MAX_TOTAL or hashlib.sha256(body).hexdigest()!=r['sha256']or key!=digest({'url':r['url'],'sha256':r['sha256']}):raise IngestError('sec_ingest_checkpoint_source_integrity')
   sec.acceptance_ns(r['received_at']);sources[key]={k:r[k]for k in('url','sha256','received_at')};sources[key]['body']=body
  expected_version='gig.sec.filing_ingestion.checkpoint.v3'if any(type(p)is dict and 'inline_manifest'in p for p in v['plans'].values())else'gig.sec.filing_ingestion.checkpoint.v2'if any(type(p)is dict and 'history_key'in p for p in v['plans'].values())else'gig.sec.filing_ingestion.checkpoint.v1'
  if v['schema']!=expected_version:raise IngestError('sec_ingest_checkpoint_version')
  used=set()
  for accession,plan in v['plans'].items():
   required={'metadata','metadata_key','index_key','instance_key','document_keys','gaap_namespace','amends_accession'}
   if type(plan)is not dict:raise IngestError('sec_ingest_checkpoint_plan')
   if 'history_key'in plan:required.add('history_key')
   if 'inline_manifest'in plan:required.update(('inline_manifest','inline_manifest_sha256','inline_keys'))
   if set(plan)!=required or type(plan['metadata'])is not dict or plan['metadata'].get('accession')!=accession:raise IngestError('sec_ingest_checkpoint_plan')
   if 'inline_manifest'in plan and(type(plan['inline_keys'])is not list or not 1<=len(plan['inline_keys'])<=8):raise IngestError('sec_inline_manifest_sources')
   if type(plan['document_keys'])is not list or len(plan['document_keys'])>16 or len(set(plan['document_keys']))!=len(plan['document_keys']):raise IngestError('sec_ingest_checkpoint_document_budget')
   for key in source_keys(plan):
    if type(key)is not str or key not in sources:raise IngestError('sec_ingest_checkpoint_source_reference')
    self._url(sources[key]['url'],accession,submission_shard=key==plan.get('history_key'));used.add(key)
  if used!=set(sources):raise IngestError('sec_ingest_checkpoint_unused_source')
  candidate=self._rebuild(v['plans'],sources)
  if candidate._identity(candidate._filings)!=v['collection_sha256']:raise IngestError('sec_ingest_checkpoint_collection')
  self.sources=sources;self.plans=v['plans'];self.collection=candidate;self.cache={};self.state='PAUSED_RESTORED';self.last_error=None
  return {'status':self.state,'collection_sha256':v['collection_sha256'],'filings':len(self.plans),'network_used':False}
