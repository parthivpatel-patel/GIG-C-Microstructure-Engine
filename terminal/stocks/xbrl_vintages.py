"""Explicit bounded statement vintages from one immutable admitted collection.

Cutoffs are authored instants, not inferred quarter ends. No cross-filing filling,
source requests or implicit accounting equivalence. Single-view APIs are unchanged.
"""
from . import sec
from .xbrl_product import company_contract
from .xbrl_instance import canonical,digest,XBRLError
MAX_CUTOFFS=8;MAX_BYTES=256*1024

def company_vintages(workspace,symbol,cutoffs,*,role=None,form='10-K',expected_collection_sha256=None):
 if type(cutoffs)is not list or not 1<=len(cutoffs)<=MAX_CUTOFFS:raise XBRLError('vintage_cutoff_budget')
 instants=[sec.acceptance_ns(at)for at in cutoffs]
 if any(b<=a for a,b in zip(instants,instants[1:])):raise XBRLError('vintage_cutoff_order')
 if role is not None and(type(role)is not str or not 1<=len(role)<=512)or form not in('10-K','10-Q'):raise XBRLError('vintage_query')
 identity=workspace.resolve(symbol);collection=workspace.xbrl_collections.get(symbol)
 collection_sha=digest({})if collection is None else collection._identity(collection._filings)
 if expected_collection_sha256 is not None and expected_collection_sha256!=collection_sha:raise XBRLError('vintage_stale_collection')
 entries=[];previous=None;size=0
 for at,instant in zip(cutoffs,instants):
  packet=company_contract(workspace,symbol,at,role=role,form=form,profile='accuracy-extension-v2');view=packet['statement_view']
  if view['collection_sha256']!=collection_sha:raise XBRLError('vintage_collection_changed')
  source=view['source_filing'];accession=None if source is None else source['accession']
  transition='UNAVAILABLE'if view['status']=='UNAVAILABLE'else'AMBIGUOUS'if view['status']=='AMBIGUOUS'else'FIRST_AVAILABLE'if previous is None else'UNCHANGED_SOURCE'if previous==accession else'SOURCE_CHANGED'
  row={'as_of':at,'cutoff_ns':str(instant),'transition':transition,'previous_accession':previous,'packet':packet};size+=len(canonical(row))
  if size>MAX_BYTES:raise XBRLError('vintage_output_budget')
  entries.append(row);previous=accession
 result={'schema':'gig.backend.company_xbrl_vintages.v1','instrument':identity,'collection_sha256':collection_sha,'profile':'accuracy-extension-v2','form_family':form,'role':role,'entries':entries,'complete_history':False,'read_only':True,'provider_requested':False,'selection_policy':'Independent acceptance-qualified view per authored cutoff;no additive amendment or cross-filing filling'}
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_BYTES:raise XBRLError('vintage_output_budget')
 return result
