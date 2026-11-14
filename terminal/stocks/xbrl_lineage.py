"""Bounded explicit amendment ancestry at a known acceptance cutoff.

A resolved supplied chain is not complete history or an accounting restatement.
No date-neighbor,form-name or value similarity creates an amendment edge.
"""
import copy,datetime,re
from . import sec
from .xbrl_collection import FilingCollection
from .xbrl_instance import digest,canonical,XBRLError
MAX_FILINGS=32;MAX_BYTES=128*1024

def filing_lineage(collection,accession,as_of):
 cutoff=sec.acceptance_ns(as_of);date=(datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=cutoff//10**9)).date().isoformat()
 if type(collection)is not FilingCollection or type(accession)is not str or not re.fullmatch('[0-9]{10}-[0-9]{2}-[0-9]{6}',accession)or type(collection._filings)is not dict or len(collection._filings)>MAX_FILINGS:raise XBRLError('lineage_input_budget')
 identity=collection._identity(collection._filings);result={'schema':'gig.sec.xbrl.filing_lineage.v1','issuer_cik':collection.cik,'origin':collection.origin,'collection_sha256':identity,'as_of':as_of,'cutoff_ns':str(cutoff),'selected_accession':accession,'status':'UNRESOLVED','reason':None,'sources':[],'links':[],'complete_history':False,'policy':'Only explicit acceptance-qualified supplied amendment links;no inferred predecessor or additive statement reconstruction'}
 current=accession;seen=set();child=None
 while current is not None:
  if current in seen:raise XBRLError('lineage_cycle')
  if len(seen)>=MAX_FILINGS:raise XBRLError('lineage_depth_budget')
  seen.add(current);parsed=collection._filings.get(current)
  if parsed is None:result['reason']='SOURCE_NOT_SUPPLIED';break
  if type(parsed)is not dict or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256'):raise XBRLError('lineage_source_identity')
  source=parsed['source']
  if source['issuer_cik']!=collection.cik or source['origin']!=collection.origin or source['accession']!=current:raise XBRLError('lineage_source_scope')
  accepted=source['accepted_at']
  if accepted is None:result['reason']='ACCEPTANCE_UNKNOWN';break
  ns=sec.acceptance_ns(accepted)
  if ns>cutoff or source['filed']>date:result['reason']='SOURCE_AFTER_CUTOFF';break
  if child is not None and(source['form'].removesuffix('/A')!=child['form'].removesuffix('/A')or source['filed']>child['filed']or ns>sec.acceptance_ns(child['accepted_at'])):raise XBRLError('lineage_parent_order_or_form')
  result['sources'].append({'source':copy.deepcopy(source),'parsed_sha256':parsed['canonical_sha256']})
  parent=source['amends_accession']
  if not source['form'].endswith('/A'):
   if parent is not None:raise XBRLError('lineage_nonamendment_parent')
   result.update(status='SUPPLIED_CHAIN_RESOLVED',reason=None);break
  if parent is None:result['reason']='AMENDMENT_PARENT_NOT_DECLARED';break
  result['links'].append({'from_accession':current,'to_accession':parent,'basis':'EXPLICIT_SOURCE_MANIFEST'});child=source;current=parent
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_BYTES:raise XBRLError('lineage_output_budget')
 return result
