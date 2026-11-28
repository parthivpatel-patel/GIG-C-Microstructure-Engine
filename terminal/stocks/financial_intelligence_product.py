"""Explicit private financial-intelligence exports; no route or source activation."""
import copy
from .xbrl_instance import canonical,digest,XBRLError
from .xbrl_dts import discover_inline_set,uri,_supplied_documents,EMBEDDED_PROFILE
from .inline_set import parse_document_set,TRANSFORMATION_PROFILE
from .xbrl_accounting_statements import _accounting_sources
from .xbrl_dts_source_audit import audit_inline_dts_sources
from .xbrl_product import company_contract
from .xbrl_lineage import filing_lineage

MAX_OUTPUT=256*1024
CONFIDENCE={'basis':'SUPPLIED_ORIGINAL_AUDIT_RECEIPT','independent_issuer_authentication':False,'browser_original_xml_validation':False}

def _finish(value):
 value['sha256']=digest(value)
 if len(canonical(value))>MAX_OUTPUT:raise XBRLError('financial_intelligence_export_budget')
 return value

def _inline_preflight(entry,stored,allow_observed,planned_identity=None,has_plan=False):
 """Bind processing grants and original byte receipts before any XML parsing.

 The retained set identifies sorted document receipts and transformation choices.
 Authored acquisition order requires its separately retained intent digest. The
 embedded-linkbase choice is not retained separately; its exact graph identity is
 checked after reconstruction rather than inferred from source bytes or features.
 """
 from .xbrl_instance import validate_manifest
 from .sec_inline_manifest import normalize
 if entry['transformation_profile']not in(None,TRANSFORMATION_PROFILE)or entry['embedded_profile']not in(None,EMBEDDED_PROFILE):raise XBRLError('financial_intelligence_inline_profile')
 documents=entry['documents'];taxonomies=entry['taxonomy_documents']
 if type(documents)is not list or not 1<=len(documents)<=8:raise XBRLError('financial_intelligence_inline_budget')
 supplied={};authored=[];total=0
 for doc in documents:
  if type(doc)is not dict or set(doc)!={'uri','raw','manifest'}or type(doc['raw'])is not bytes or not 1<=len(doc['raw'])<=2*1024*1024:raise XBRLError('financial_intelligence_inline_recipe')
  key=uri(doc['uri'])
  if key in supplied:raise XBRLError('financial_intelligence_inline_duplicate_uri')
  source=validate_manifest(doc['raw'],doc['manifest'],allow_observed)
  if source['source_url']is not None and source['source_url']!=key:raise XBRLError('financial_intelligence_inline_uri_scope')
  supplied[key]=source;authored.append(key);total+=len(doc['raw'])
  if total>8*1024*1024:raise XBRLError('financial_intelligence_inline_budget')
 if type(taxonomies)is not list or not 1<=len(taxonomies)<=16:raise XBRLError('financial_intelligence_inline_budget')
 taxonomy=_supplied_documents(taxonomies)
 if len(taxonomy)!=len(taxonomies)or set(taxonomy)&set(supplied):raise XBRLError('financial_intelligence_inline_duplicate_uri')
 if total+sum(len(d['raw'])for d in taxonomies)>8*1024*1024:raise XBRLError('financial_intelligence_inline_budget')
 ds=stored.get('document_set');sources=[{'uri':key,'source':supplied[key]}for key in sorted(supplied)]
 if type(ds)is not dict or canonical(ds.get('documents'))!=canonical(sources)or ds.get('sha256')!=digest(sources):raise XBRLError('financial_intelligence_inline_source_mismatch')
 if ('transformation_profile'in ds)!=(entry['transformation_profile']is not None)or ds.get('transformation_profile')!=entry['transformation_profile']:raise XBRLError('financial_intelligence_inline_profile_scope')
 retained=stored.get('dts_corroboration',{}).get('documents')
 if type(retained)is not list or {d['uri']:d['sha256']for d in retained}!={key:doc['sha256']for key,doc in taxonomy.items()}:raise XBRLError('financial_intelligence_inline_taxonomy_scope')
 expected=entry['expected_acquisition_manifest_sha256'];manifest=entry['acquisition_manifest']
 if has_plan and planned_identity!=expected:raise XBRLError('financial_intelligence_inline_plan_mismatch')
 if manifest is not None:
  normalized=normalize(manifest,stored['source']['issuer_cik'],stored['source']['accession'])
  if type(expected)is not str or digest(normalized)!=expected:raise XBRLError('financial_intelligence_inline_acquisition_identity')
  if [key.rsplit('/',1)[-1]for key in authored]!=[row['name']for row in normalized['documents']]:raise XBRLError('financial_intelligence_inline_acquisition_order')
  primary=[key for key in authored if key.rsplit('/',1)[-1]==normalized['primary_document']]
  if len(primary)!=1:raise XBRLError('financial_intelligence_inline_acquisition_primary')
  prefix=primary[0].rsplit('/',1)[0]+'/'
  if any(key!=prefix+row['name']or supplied[key]['source_sha256']!=row['sha256']for key,row in zip(authored,normalized['documents'])):raise XBRLError('financial_intelligence_inline_acquisition_binding')
 elif expected is not None:raise XBRLError('financial_intelligence_inline_acquisition_manifest_required')

def company_source_accounting(workspace,symbol,as_of,source_inputs,role_bindings,*,form='10-K',expected_collection_sha256=None):
 packet,parsed,graph=_accounting_sources(workspace,symbol,as_of,source_inputs,role_bindings,form=form,expected_collection_sha256=expected_collection_sha256)
 return _finish({'schema':'gig.backend.company_source_accounting.v1','instrument':copy.deepcopy(packet['instrument']),'as_of':as_of,'cutoff_ns':packet['cutoff_ns'],'collection_sha256':packet['collection_sha256'],'status':packet['status'],'reason':packet['reason'],'accounting':packet,'source':parsed,'dts':graph,'source_confidence':copy.deepcopy(CONFIDENCE),'read_only':True,'provider_requested':False})

def company_inline_audit(workspace,symbol,as_of,originals,*,form='10-K',expected_collection_sha256=None):
 if type(originals)is not dict or len(originals)>32:raise XBRLError('financial_intelligence_original_mapping')
 view=company_contract(workspace,symbol,as_of,form=form,profile='accuracy-extension-v2')['statement_view'];collection=workspace.xbrl_collections.get(symbol);identity=view['collection_sha256']
 if expected_collection_sha256 is not None and expected_collection_sha256!=identity:raise XBRLError('financial_intelligence_stale_collection')
 result={'schema':'gig.backend.company_inline_source_audit.v1','instrument':copy.deepcopy(workspace.resolve(symbol)),'as_of':as_of,'cutoff_ns':view['cutoff_ns'],'form_family':form,'collection_sha256':identity,'status':'UNAVAILABLE','reason':view['reason'],'lineage':None,'admitted_parsed_sha256':None,'parsed_sha256':None,'dts_sha256':None,'receipt':None,'source_confidence':copy.deepcopy(CONFIDENCE),'read_only':True,'provider_requested':False}
 source=view['source_filing']
 if view['status']=='AMBIGUOUS':result['reason']='AMBIGUOUS_LATEST_FILING';return _finish(result)
 if source is None or collection is None:return _finish(result)
 accession=source['accession'];result['lineage']=filing_lineage(collection,accession,as_of)
 if result['lineage']['status']!='SUPPLIED_CHAIN_RESOLVED':result['reason']='EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED';return _finish(result)
 if accession not in originals:result['reason']='SELECTED_INLINE_ORIGINALS_NOT_SUPPLIED';return _finish(result)
 e=originals[accession];required={'documents','concepts','taxonomy_documents','transformation_profile','embedded_profile','acquisition_manifest','expected_acquisition_manifest_sha256'}
 if type(e)is not dict or set(e)!=required:raise XBRLError('financial_intelligence_inline_recipe')
 stored=collection._filings[accession];coordinator=workspace.filing_ingestors.get(symbol)
 has_plan=coordinator is not None and accession in coordinator.plans
 planned_identity=coordinator.plans[accession].get('inline_manifest_sha256')if has_plan else None
 _inline_preflight(e,stored,collection.allow_observed,planned_identity,has_plan)
 parsed=parse_document_set(e['documents'],e['concepts'],allow_observed=collection.allow_observed,transformation_profile=e['transformation_profile'])
 if canonical(parsed['source'])!=canonical(source)or any(canonical(parsed[k])!=canonical(stored[k])for k in('facts','contexts','units','document_set')):raise XBRLError('financial_intelligence_inline_source_mismatch')
 refs=[d['manifest']['permission_reference']for d in sorted(e['documents'],key=lambda d:d['uri'])]
 graph=discover_inline_set(parsed,e['taxonomy_documents'],allow_observed=collection.allow_observed,permission_references=refs,embedded_profile=e['embedded_profile'])
 if stored.get('dts_corroboration',{}).get('dts_sha256')!=graph['canonical_sha256']:raise XBRLError('financial_intelligence_inline_dts_mismatch')
 receipt=audit_inline_dts_sources(parsed,graph,e['documents'],e['taxonomy_documents'],concepts=e['concepts'],acquisition_manifest=e['acquisition_manifest'],expected_acquisition_manifest_sha256=e['expected_acquisition_manifest_sha256'],transformation_profile=e['transformation_profile'],allow_observed=collection.allow_observed,embedded_profile=e['embedded_profile'])
 result.update(status='AVAILABLE',reason=None,admitted_parsed_sha256=stored['canonical_sha256'],parsed_sha256=parsed['canonical_sha256'],dts_sha256=graph['canonical_sha256'],receipt=receipt)
 return _finish(result)
