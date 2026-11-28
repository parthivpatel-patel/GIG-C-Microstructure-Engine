"""Explicit private financial-intelligence analysis of supplied or admitted originals."""
import copy
from .xbrl_instance import canonical,digest,XBRLError
from .xbrl_accounting_statements import _accounting_sources
from .xbrl_dts_source_audit import reconstruct_admitted_inline
from .xbrl_product import company_contract
from .xbrl_lineage import filing_lineage

MAX_OUTPUT=256*1024
CONFIDENCE={'basis':'SUPPLIED_ORIGINAL_AUDIT_RECEIPT','independent_issuer_authentication':False,'browser_original_xml_validation':False}

def _finish(value):
 value['sha256']=digest(value)
 if len(canonical(value))>MAX_OUTPUT:raise XBRLError('financial_intelligence_export_budget')
 return value

def company_source_accounting(workspace,symbol,as_of,source_inputs,role_bindings,*,form='10-K',expected_collection_sha256=None):
 packet,parsed,graph=_accounting_sources(workspace,symbol,as_of,source_inputs,role_bindings,form=form,expected_collection_sha256=expected_collection_sha256)
 return _finish({'schema':'gig.backend.company_source_accounting.v1','instrument':copy.deepcopy(packet['instrument']),'as_of':as_of,'cutoff_ns':packet['cutoff_ns'],'collection_sha256':packet['collection_sha256'],'status':packet['status'],'reason':packet['reason'],'accounting':packet,'source':parsed,'dts':graph,'source_confidence':copy.deepcopy(CONFIDENCE),'read_only':True,'provider_requested':False})

def company_inline_audit(workspace,symbol,as_of,originals,*,form='10-K',expected_collection_sha256=None):
 if type(originals)is not dict or len(originals)>32:raise XBRLError('financial_intelligence_original_mapping')
 view=company_contract(workspace,symbol,as_of,form=form,profile='accuracy-extension-v2')['statement_view'];collection=workspace.visible_xbrl_collection(symbol);identity=view['collection_sha256']
 if expected_collection_sha256 is not None and expected_collection_sha256!=identity:raise XBRLError('financial_intelligence_stale_collection')
 result={'schema':'gig.backend.company_inline_source_audit.v1','instrument':copy.deepcopy(workspace.resolve(symbol)),'as_of':as_of,'cutoff_ns':view['cutoff_ns'],'form_family':form,'collection_sha256':identity,'status':'UNAVAILABLE','reason':view['reason'],'lineage':None,'admitted_parsed_sha256':None,'parsed_sha256':None,'dts_sha256':None,'receipt':None,'source_confidence':copy.deepcopy(CONFIDENCE),'read_only':True,'provider_requested':False}
 source=view['source_filing']
 if view['status']=='AMBIGUOUS':result['reason']='AMBIGUOUS_LATEST_FILING';return _finish(result)
 if source is None or collection is None:return _finish(result)
 accession=source['accession'];result['lineage']=filing_lineage(collection,accession,as_of)
 if result['lineage']['status']!='SUPPLIED_CHAIN_RESOLVED':result['reason']='EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED';return _finish(result)
 if accession not in originals:result['reason']='SELECTED_INLINE_ORIGINALS_NOT_SUPPLIED';return _finish(result)
 stored=collection._filings[accession];coordinator=workspace.visible_filing_ingestor(symbol)
 has_plan=coordinator is not None and accession in coordinator.plans
 planned_identity=coordinator.plans[accession].get('inline_manifest_sha256')if has_plan else None
 parsed,graph,receipt=reconstruct_admitted_inline(originals[accession],stored,allow_observed=collection.allow_observed,planned_identity=planned_identity,has_plan=has_plan)
 result.update(status='AVAILABLE',reason=None,admitted_parsed_sha256=stored['canonical_sha256'],parsed_sha256=parsed['canonical_sha256'],dts_sha256=graph['canonical_sha256'],receipt=receipt)
 return _finish(result)


def admitted_filing_analysis(workspace,symbol,as_of,form,action,role_binding=None,*,expected_collection_sha256,previous_as_of=None):
 """Analyze the same authorized bytes that produced the installed collection."""
 from .sec import acceptance_ns
 collection=workspace.visible_xbrl_collection(symbol)
 coordinator=workspace.visible_filing_ingestor(symbol)
 if collection is None or coordinator is None:
  raise XBRLError('financial_intelligence_admitted_source_required')
 cutoffs=[as_of]
 if action=='comparison':
  if acceptance_ns(previous_as_of)>=acceptance_ns(as_of):
   raise XBRLError('statement_comparison_cutoff_order')
  cutoffs.insert(0,previous_as_of)
 recipes={}
 for cutoff in cutoffs:
  selected=company_contract(workspace,symbol,cutoff,form=form,profile='accuracy-extension-v2')['statement_view']
  source=selected['source_filing']
  if selected['collection_sha256']!=expected_collection_sha256:
   raise XBRLError('financial_intelligence_stale_collection')
  if source is not None and selected['status']!='AMBIGUOUS':
   accession=source['accession']
   if accession not in recipes:
    candidate=coordinator.original_recipe(accession,inline_required=action=='inline')
    if candidate is not None:recipes[accession]=candidate
 if action=='inline':
  return company_inline_audit(workspace,symbol,as_of,recipes,form=form,
                             expected_collection_sha256=expected_collection_sha256)
 roles={accession:role_binding for accession in recipes}
 if action=='accounting':
  return company_source_accounting(workspace,symbol,as_of,recipes,roles,form=form,
                                   expected_collection_sha256=expected_collection_sha256)
 if action=='comparison':
  from .xbrl_statement_comparison import company_statement_vintage_comparison
  return company_statement_vintage_comparison(workspace,symbol,cutoffs,recipes,roles,form=form,
                                             expected_collection_sha256=expected_collection_sha256)
 raise XBRLError('financial_intelligence_action')
