"""Bounded immutable filing-instance batches and acceptance-time selection.

No fetch,persistence or automatic UI-cache replacement. Original source receipts
are carried unchanged. Full XBRL DTS/inline/presentation is deliberately outside
this strict instance profile;hash consistency is not source authentication.
"""
import copy,datetime
from . import sec
from .financials import calculate
from .xbrl_instance import selected_financials,canonical,digest,XBRLError
from .inline_xbrl import parse_filing

MAX_FILINGS=32;MAX_BATCH=8;MAX_BATCH_BYTES=8*1024*1024;MAX_COLLECTION_BYTES=16*1024*1024
class FilingCollection:
 def __init__(self,cik,*,origin='HISTORICAL_SYNTHETIC',allow_observed=False):
  import re
  if type(cik)is not str or not re.fullmatch('[0-9]{10}',cik)or int(cik)==0:raise XBRLError('xbrl_collection_issuer')
  if origin not in ('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE')or type(allow_observed)is not bool or origin=='OBSERVED_OFFICIAL_RESPONSE'and not allow_observed:raise XBRLError('xbrl_collection_origin')
  self.cik=cik;self.origin=origin;self.allow_observed=allow_observed;self._filings={}
 def _identity(self,rows):return digest({a:r['canonical_sha256']for a,r in sorted(rows.items())})
 def ingest_batch(self,entries):
  if type(entries)is not list or not 1<=len(entries)<=MAX_BATCH:raise XBRLError('xbrl_batch_budget')
  size=0
  for entry in entries:
   if type(entry)is not dict or set(entry)!={'raw','manifest','concepts'}or type(entry['raw'])is not bytes:raise XBRLError('xbrl_batch_contract')
   size+=len(entry['raw'])
  if size>MAX_BATCH_BYTES:raise XBRLError('xbrl_batch_byte_budget')
  values=[parse_filing(entry['raw'],entry['manifest'],entry['concepts'],allow_observed=self.allow_observed)for entry in entries]
  return self._commit_parsed(values)
 def ingest_dts_batch(self,entries,*,numeric_profile=None,dimensional_profile=None):
  # New explicit contract;the original strict batch keys and behavior stay intact.
  from .xbrl_dts import discover
  from .xbrl_binding import bind_declarations
  from .xbrl_types import PROFILES,corroborate
  if numeric_profile not in(None,*PROFILES):raise XBRLError('xbrl_numeric_profile_unsupported')
  from .xbrl_dimensions import PROFILE as DIMENSIONS,corroborate as dimensions
  if dimensional_profile not in(None,DIMENSIONS):raise XBRLError('xbrl_dimensional_profile_unsupported')
  if type(entries)is not list or not 1<=len(entries)<=MAX_BATCH:raise XBRLError('xbrl_batch_budget')
  total=0
  for entry in entries:
   if type(entry)is not dict or set(entry)!={'raw','manifest','concepts','instance_uri','documents'}or type(entry['raw'])is not bytes or type(entry['documents'])is not list or len(entry['documents'])>16:raise XBRLError('xbrl_dts_batch_contract')
   total+=len(entry['raw'])
   for doc in entry['documents']:
    if type(doc)is not dict or type(doc.get('raw'))is not bytes:raise XBRLError('xbrl_dts_batch_contract')
    total+=len(doc['raw'])
  if total>MAX_BATCH_BYTES:raise XBRLError('xbrl_dts_batch_byte_budget')
  values=[]
  for entry in entries:
   parsed=parse_filing(entry['raw'],entry['manifest'],entry['concepts'],allow_observed=self.allow_observed);source=parsed['source']
   if source['origin']=='OBSERVED_OFFICIAL_RESPONSE'and entry['instance_uri']!=source['source_url']:raise XBRLError('dts_binding_source_uri')
   graph=discover(entry['raw'],entry['instance_uri'],source['source_sha256'],entry['documents'],origin=source['origin'],allow_observed=self.allow_observed,permission_reference=entry['manifest']['permission_reference'])
   bound=bind_declarations(parsed,graph)
   if numeric_profile is not None:bound=corroborate(bound,graph,profile=numeric_profile)
   values.append(dimensions(bound,graph)if dimensional_profile is not None else bound)
  return self._commit_parsed(values)
 def ingest_inline_set_batch(self,entries,*,numeric_profile=None,dimensional_profile=None):
  from .inline_set import parse_document_set
  from .xbrl_dts import discover_inline_set
  from .xbrl_binding import bind_declarations
  from .xbrl_types import PROFILES,corroborate
  if numeric_profile not in(None,*PROFILES):raise XBRLError('xbrl_numeric_profile_unsupported')
  from .xbrl_dimensions import PROFILE as DIMENSIONS,corroborate as dimensions
  if dimensional_profile not in(None,DIMENSIONS):raise XBRLError('xbrl_dimensional_profile_unsupported')
  if type(entries)is not list or not 1<=len(entries)<=MAX_BATCH:raise XBRLError('xbrl_batch_budget')
  total=0
  for entry in entries:
   if type(entry)is not dict or set(entry)!={'documents','concepts','taxonomy_documents'}or type(entry['documents'])is not list or not 1<=len(entry['documents'])<=8 or entry['taxonomy_documents']is not None and(type(entry['taxonomy_documents'])is not list or len(entry['taxonomy_documents'])>16):raise XBRLError('xbrl_inline_set_batch_contract')
   if (numeric_profile is not None or dimensional_profile is not None)and entry['taxonomy_documents']is None:raise XBRLError('xbrl_numeric_profile_requires_dts')
   for document in entry['documents']+(entry['taxonomy_documents']or[]):
    if type(document)is not dict or type(document.get('raw'))is not bytes:raise XBRLError('xbrl_inline_set_batch_contract')
    total+=len(document['raw'])
  if total>MAX_BATCH_BYTES:raise XBRLError('xbrl_batch_byte_budget')
  values=[]
  for entry in entries:
   parsed=parse_document_set(entry['documents'],entry['concepts'],allow_observed=self.allow_observed)
   if entry['taxonomy_documents']is not None:
    references=[doc['manifest']['permission_reference']for doc in sorted(entry['documents'],key=lambda d:d['uri'])]
    graph=discover_inline_set(parsed,entry['taxonomy_documents'],allow_observed=self.allow_observed,permission_references=references);parsed=bind_declarations(parsed,graph)
    if numeric_profile is not None:parsed=corroborate(parsed,graph,profile=numeric_profile)
    if dimensional_profile is not None:parsed=dimensions(parsed,graph)
   values.append(parsed)
  return self._commit_parsed(values)
 def _commit_parsed(self,values):
  candidate=dict(self._filings);sizes={a:len(canonical(v))for a,v in candidate.items()}
  for value in values:
   source=value['source']
   if source['issuer_cik']!=self.cik or source['origin']!=self.origin:raise XBRLError('xbrl_collection_source_scope')
   accession=source['accession']
   if accession in candidate and candidate[accession]!=value:raise XBRLError('xbrl_accession_content_conflict')
   sizes[accession]=len(canonical(value))
   if sum(sizes.values())>MAX_COLLECTION_BYTES:raise XBRLError('xbrl_collection_memory_budget')
   candidate[accession]=value
  if len(candidate)>MAX_FILINGS:raise XBRLError('xbrl_collection_filing_budget')
  # Only declared amendment links;never infer a predecessor from date proximity.
  for accession,value in candidate.items():
   seen={accession};source=value['source'];target=source['amends_accession']
   while target in candidate:
    if target in seen:raise XBRLError('xbrl_amendment_cycle')
    seen.add(target);parent=candidate[target]['source']
    if parent['form'].removesuffix('/A')!=source['form'].removesuffix('/A')or parent['filed']>source['filed']:raise XBRLError('xbrl_amendment_lineage')
    if source['accepted_at']is not None and parent['accepted_at']is not None and sec.acceptance_ns(parent['accepted_at'])>sec.acceptance_ns(source['accepted_at']):raise XBRLError('xbrl_amendment_acceptance_order')
    source=parent;target=parent['amends_accession']
  if len(canonical(candidate))>MAX_COLLECTION_BYTES:raise XBRLError('xbrl_collection_memory_budget')
  identity=self._identity(candidate);self._filings=candidate
  return {'schema':'gig.sec.xbrl.batch.v1','filings':len(candidate),'collection_sha256':identity,'origin':self.origin,'atomic':True,'complete_history':False}
 def page(self,*,offset=0,limit=8,expected_collection_sha256=None):
  if type(offset)is not int or type(limit)is not int or not 0<=offset<=MAX_FILINGS or not 1<=limit<=8:raise XBRLError('xbrl_page_budget')
  identity=self._identity(self._filings)
  if (offset and expected_collection_sha256 is None)or expected_collection_sha256 is not None and expected_collection_sha256!=identity:raise XBRLError('xbrl_stale_collection_cursor')
  keys=sorted(self._filings)
  if offset>len(keys):raise XBRLError('xbrl_page_offset')
  records=[copy.deepcopy(self._filings[a]['source'])for a in keys[offset:offset+limit]]
  return {'schema':'gig.sec.xbrl.filings.v1','records':records,'total':len(keys),'collection_sha256':identity,'next_offset':offset+len(records)if offset+len(records)<len(keys)else None,'completeness':'BOUNDED_SUPPLIED_INSTANCES_NOT_COMPLETE_HISTORY'}
 def statement_at(self,as_of,*,role=None,form='10-K'):
  from .xbrl_statements import select
  return select(self._filings,self.cik,self.origin,self._identity(self._filings),as_of,role=role,form=form)
 def at_acceptance_time(self,as_of):
  cutoff=sec.acceptance_ns(as_of)
  # Calendar guards must use the same UTC instant as the nanosecond cutoff.
  # Taking the lexical date would change eligibility for equivalent offsets.
  cutoff_date=(datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=cutoff//1000000000)).date().isoformat()
  groups={};excluded={'unknown_acceptance_filings':0,'after_cutoff_filings':0,'ambiguous_same_time_facts':0};coverage=[];lineage=[]
  for accession,parsed in sorted(self._filings.items()):
   source=parsed['source'];accepted=source['accepted_at']
   if accepted is None:excluded['unknown_acceptance_filings']+=1;continue
   ns=sec.acceptance_ns(accepted)
   if ns>cutoff or source['filed']>cutoff_date:excluded['after_cutoff_filings']+=1;continue
   financials=selected_financials(parsed);coverage.append({'accession':accession,'selected_coverage':financials['coverage'],'xbrl_coverage':financials['xbrl_coverage']});lineage.append(copy.deepcopy(source));seen=set()
   for metric,rows in financials['history'].items():
    for row in rows+financials.get('revision_history',{}).get(metric,[]):
     if row['source_fact_id']in seen:continue
     seen.add(row['source_fact_id']);key=(metric,row['source_xbrl_concept'],row['start'],row['end'],row['unit'])
     groups.setdefault(key,[]).append((ns,{**copy.deepcopy(row),'accepted_at':accepted,'availability_source':'supplied_instance_filing_manifest'}))
  history={metric:[]for metric in sec.TAGS};superseded=[]
  for key,rows in groups.items():
   latest=max(ns for ns,_ in rows);winners=[r for ns,r in rows if ns==latest]
   if len(winners)!=1:excluded['ambiguous_same_time_facts']+=len(winners);continue
   history[key[0]].append(winners[0]);superseded.extend(r['source_fact_id']for ns,r in rows if ns<latest)
  truncated={}
  for metric,rows in history.items():
   rows.sort(key=lambda r:(r['end'],r['start']or'',r['filed'],r['concept']),reverse=True);truncated[metric]=max(0,len(rows)-256);history[metric]=rows[:256]
  unresolved=[s['accession']for s in lineage if s['form'].endswith('/A')and(s['amends_accession']is None or s['amends_accession']not in self._filings)]
  result={'schema':'gig.sec.xbrl.acceptance.v1','issuer_cik':self.cik,'origin':self.origin,'as_of':as_of,'cutoff_ns':str(cutoff),'history':history,'descriptors':calculate({'history':history,'as_of_filing_date':cutoff_date}),'source_filings':lineage,'superseded_source_fact_ids':sorted(superseded),'unresolved_amendment_filings':unresolved,'exclusions':excluded,'selected_input_coverage':coverage,'output_truncated':truncated,'collection_sha256':self._identity(self._filings),'completeness':'BOUNDED_SUPPLIED_INSTANCES_NOT_COMPLETE_STATEMENTS_DTS_OR_HISTORY','receipt_authority':'Original supplied receipt preserved;missing is unknown,never reconstructed','selection_policy':'Latest known acceptance per expanded namespace-qualified concept/period/unit;no calendar-quarter inference or additive amendment statements'}
  result['selection_sha256']=digest(result);return result
