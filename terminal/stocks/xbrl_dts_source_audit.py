"""Opt-in exact reconstruction of a plain-instance/DTS artifact from raw sources.

Hashes establish identity consistency,not independent source authentication. This
separate API requires original bytes and explicit parse choices;legacy binders and
source permissions/defaults are unchanged. A separate explicit API audits inline sets.
"""
from .xbrl_instance import parse_instance,validate_manifest,digest,canonical,XBRLError
from .xbrl_dts import discover,discover_inline_set,uri,EMBEDDED_PROFILE,_supplied_documents
from .inline_set import parse_document_set,TRANSFORMATION_PROFILE
from .sec_inline_manifest import normalize as normalize_inline_manifest
PROFILE='ORIGINAL_PLAIN_DTS_SOURCE_AUDIT_V1'
SCHEMA='gig.sec.xbrl.dts_source_audit.v1'
MAX_INSTANCE=2*1024*1024;MAX_INPUT=8*1024*1024;MAX_GRAPH=16*1024*1024;MAX_PARSED=8*1024*1024;MAX_OUTPUT=1024*1024

def _identity(value,limit):
 if type(value)is not dict:raise XBRLError('dts_audit_artifact_identity')
 try:
  raw=canonical(value)
  if len(raw)>limit:raise XBRLError('dts_audit_artifact_budget')
  expected=digest({k:v for k,v in value.items()if k!='canonical_sha256'})
 except (TypeError,ValueError,RecursionError)as exc:
  if isinstance(exc,XBRLError):raise
  raise XBRLError('dts_audit_artifact_identity')from None
 if expected!=value.get('canonical_sha256'):raise XBRLError('dts_audit_artifact_identity')

def audit_dts_sources(parsed,dts,instance_raw,documents,*,manifest,concepts,instance_uri,allow_observed=False,embedded_profile=None):
 """Reparse explicit originals and require exact parsed/DTS identity equality.

 No source activation,fetch,storage,replacement or automatic profile selection.
 Successful receipts contain hashes and source IDs,never original bytes/text.
 """
 if type(instance_raw)is not bytes or not 1<=len(instance_raw)<=MAX_INSTANCE:raise XBRLError('dts_audit_instance_budget')
 # Processing approval/source identity precedes every XML parse,including schemas.
 source=validate_manifest(instance_raw,manifest,allow_observed)
 if embedded_profile not in(None,EMBEDDED_PROFILE):raise XBRLError('dts_audit_embedded_profile')
 uri(instance_uri)
 if source['source_url']is not None and instance_uri!=source['source_url']:raise XBRLError('dts_audit_original_uri_scope')
 if type(documents)is not list or not 1<=len(documents)<=16:raise XBRLError('dts_audit_document_budget')
 supplied=_supplied_documents(documents)
 if len(supplied)!=len(documents):raise XBRLError('dts_audit_duplicate_original_uri')
 if len(instance_raw)+sum(len(d['raw'])for d in documents)>MAX_INPUT:raise XBRLError('dts_audit_input_budget')
 _identity(parsed,MAX_PARSED);_identity(dts,MAX_GRAPH)
 if parsed.get('schema')!='gig.sec.xbrl.instance.v1'or dts.get('schema')!='gig.sec.xbrl.dts.v1':raise XBRLError('dts_audit_original_plain_artifact_required')
 if parsed.get('source')!=source or parsed.get('origin')!=source['origin']or dts.get('origin')!=source['origin']:raise XBRLError('dts_audit_origin_scope')
 original=parse_instance(instance_raw,manifest,concepts,allow_observed=allow_observed)
 if original!=parsed:raise XBRLError('dts_audit_original_parsed_mismatch')
 reconstructed=discover(instance_raw,instance_uri,source['source_sha256'],documents,origin=source['origin'],allow_observed=allow_observed,permission_reference=manifest['permission_reference'],embedded_profile=embedded_profile)
 if reconstructed['structural_closure']is not True or reconstructed['unresolved']:raise XBRLError('dts_audit_original_closure_required')
 # Reject unreferenced extras rather than claiming that their presence proves DTS
 # coverage. Every loaded body and every supplied body must be exactly accounted.
 originals={d['uri']:d['sha256']for d in reconstructed['documents']}
 if set(originals)!=set(supplied)or any(originals[u]!=supplied[u]['sha256']for u in originals):raise XBRLError('dts_audit_original_document_coverage')
 if reconstructed!=dts:raise XBRLError('dts_audit_reconstructed_graph_mismatch')
 result={'schema':SCHEMA,'profile':PROFILE,'status':'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION','instance_uri':instance_uri,'source_sha256':source['source_sha256'],'parsed_sha256':parsed['canonical_sha256'],'dts_sha256':dts['canonical_sha256'],'embedded_profile':embedded_profile,'origin':source['origin'],'source_fact_ids':[f['source_fact_id']for f in parsed['facts']],'source_context_sha256s':{key:v['semantic_sha256']for key,v in sorted(parsed['contexts'].items())},'source_unit_sha256s':{key:v['semantic_sha256']for key,v in sorted(parsed['units'].items())},'documents':[{'uri':u,'sha256':originals[u]}for u in sorted(originals)],'provider_requested':False,'independent_source_authentication':False,'limitations':['Plain original pre-binding artifact only;explicit manifest/concepts/URI/profile required','Source bytes are caller supplied;hash agreement is not independent provider authentication','Reconstruction preserves supported/unsupported DTS diagnostics;not complete schema/DRS/calculation conformance']}
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('dts_audit_output_budget')
 return result


INLINE_PROFILE='ORIGINAL_INLINE_SET_DTS_SOURCE_AUDIT_V1'
INLINE_SCHEMA='gig.sec.xbrl.inline_dts_source_audit.v1'

def audit_inline_dts_sources(parsed,dts,inline_documents,taxonomy_documents,*,concepts,acquisition_manifest=None,expected_acquisition_manifest_sha256=None,transformation_profile=None,allow_observed=False,embedded_profile=None):
 """Reconstruct an original inline set/DTS using explicitly supplied originals.

 All original processing grants,identities,receipts and parse choices are gated
 before XML. Optional acquisition intent additionally requires its accepted digest;
 the original parsed set itself does not retain authored acquisition-list order.
 """
 if type(inline_documents)is not list or not 1<=len(inline_documents)<=8:raise XBRLError('inline_audit_document_budget')
 if transformation_profile not in(None,TRANSFORMATION_PROFILE):raise XBRLError('inline_audit_transformation_profile')
 if embedded_profile not in(None,EMBEDDED_PROFILE):raise XBRLError('inline_audit_embedded_profile')
 supplied={};authored=[];total=0
 # No XML parser is called until every original's approval and identity passes.
 for entry in inline_documents:
  if type(entry)is not dict or set(entry)!={'uri','raw','manifest'}or type(entry['raw'])is not bytes or not 1<=len(entry['raw'])<=MAX_INSTANCE:raise XBRLError('inline_audit_original_contract')
  key=uri(entry['uri'])
  if key in supplied:raise XBRLError('inline_audit_duplicate_original_uri')
  source=validate_manifest(entry['raw'],entry['manifest'],allow_observed)
  if source['source_url']is not None and key!=source['source_url']:raise XBRLError('inline_audit_original_uri_scope')
  supplied[key]={'entry':entry,'source':source};authored.append(key);total+=len(entry['raw'])
  if total>MAX_INPUT:raise XBRLError('inline_audit_input_budget')
 if type(taxonomy_documents)is not list or not 1<=len(taxonomy_documents)<=16:raise XBRLError('inline_audit_taxonomy_document_budget')
 taxonomies=_supplied_documents(taxonomy_documents)
 if len(taxonomies)!=len(taxonomy_documents):raise XBRLError('inline_audit_duplicate_taxonomy_uri')
 if set(taxonomies)&set(supplied):raise XBRLError('inline_audit_original_taxonomy_overlap')
 if total+sum(len(d['raw'])for d in taxonomy_documents)>MAX_INPUT:raise XBRLError('inline_audit_input_budget')
 ordered=sorted(supplied);sources=[{'uri':key,'source':supplied[key]['source']}for key in ordered];first=sources[0]['source']
 def filing_identity(s):
  from . import sec
  return(s['issuer_cik'],s['accession'],s['form'],s['filed'],None if s['accepted_at']is None else sec.acceptance_ns(s['accepted_at']),s['amends_accession'],s['origin'])
 if any(filing_identity(s['source'])!=filing_identity(first)for s in sources):raise XBRLError('inline_audit_filing_scope')
 acquisition_sha=None
 if acquisition_manifest is not None:
  normalized=normalize_inline_manifest(acquisition_manifest,first['issuer_cik'],first['accession']);acquisition_sha=digest(normalized)
  if type(expected_acquisition_manifest_sha256)is not str or expected_acquisition_manifest_sha256!=acquisition_sha:raise XBRLError('inline_audit_acquisition_identity')
  names=[key.rsplit('/',1)[-1]for key in authored]
  if names!=[d['name']for d in normalized['documents']]:raise XBRLError('inline_audit_acquisition_order_or_members')
  primary=[key for key in authored if key.rsplit('/',1)[-1]==normalized['primary_document']]
  if len(primary)!=1:raise XBRLError('inline_audit_acquisition_primary')
  prefix=primary[0].rsplit('/',1)[0]+'/'
  for row,key in zip(normalized['documents'],authored):
   if key!=prefix+row['name']or supplied[key]['source']['source_sha256']!=row['sha256']:raise XBRLError('inline_audit_acquisition_source_binding')
 elif expected_acquisition_manifest_sha256 is not None:raise XBRLError('inline_audit_acquisition_manifest_required')
 _identity(parsed,MAX_PARSED);_identity(dts,MAX_GRAPH)
 if parsed.get('schema')!='gig.sec.xbrl.inline_set.v1'or dts.get('schema')!='gig.sec.xbrl.dts_set.v1':raise XBRLError('inline_audit_original_set_artifact_required')
 ds=parsed.get('document_set')
 if type(ds)is not dict or ds.get('schema')!='gig.sec.xbrl.document_set.v1'or canonical(ds.get('documents'))!=canonical(sources)or ds.get('sha256')!=digest(sources):raise XBRLError('inline_audit_original_metadata_scope')
 if ('transformation_profile'in ds)!=(transformation_profile is not None)or ds.get('transformation_profile')!=transformation_profile:raise XBRLError('inline_audit_transformation_profile_scope')
 if parsed.get('origin')!=first['origin']or parsed.get('source',{}).get('source_sha256')!=ds['sha256']or dts.get('origin')!=first['origin']:raise XBRLError('inline_audit_origin_scope')
 original=parse_document_set(inline_documents,concepts,allow_observed=allow_observed,transformation_profile=transformation_profile)
 if canonical(original)!=canonical(parsed):raise XBRLError('inline_audit_original_parsed_mismatch')
 references=[supplied[key]['entry']['manifest']['permission_reference']for key in ordered]
 reconstructed=discover_inline_set(original,taxonomy_documents,allow_observed=allow_observed,permission_references=references,embedded_profile=embedded_profile)
 if reconstructed['structural_closure']is not True or reconstructed['unresolved']:raise XBRLError('inline_audit_original_closure_required')
 originals={d['uri']:d['sha256']for d in reconstructed['documents']}
 if set(originals)!=set(taxonomies)or any(originals[u]!=taxonomies[u]['sha256']for u in originals):raise XBRLError('inline_audit_original_document_coverage')
 if canonical(reconstructed)!=canonical(dts):raise XBRLError('inline_audit_reconstructed_graph_mismatch')
 result={'schema':INLINE_SCHEMA,'profile':INLINE_PROFILE,'status':'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION','origin':first['origin'],'parsed_sha256':parsed['canonical_sha256'],'dts_sha256':dts['canonical_sha256'],'document_set_sha256':ds['sha256'],'transformation_profile':transformation_profile,'embedded_profile':embedded_profile,'acquisition_manifest_sha256':acquisition_sha,'supplied_document_order':authored,'parsed_document_order':ordered,'inline_documents':[{'uri':s['uri'],'source_sha256':s['source']['source_sha256'],'received_at':s['source']['received_at'],'accepted_at':s['source']['accepted_at'],'permission_reference_sha256':s['source']['permission_reference_sha256']}for s in sources],'source_fact_ids':[f['source_fact_id']for f in original['facts']],'source_context_sha256s':{key:v['semantic_sha256']for key,v in sorted(original['contexts'].items())},'source_unit_sha256s':{key:v['semantic_sha256']for key,v in sorted(original['units'].items())},'taxonomy_documents':[{'uri':u,'sha256':originals[u]}for u in sorted(originals)],'provider_requested':False,'independent_source_authentication':False,'limitations':['Original pre-binding default-target inline-set reconstruction only;explicit concepts/original manifests/profiles required','Supplied order is audit input;accepted acquisition order requires its separately retained expected digest','No source contact/raw text returned;caller-supplied originals do not independently authenticate issuer sources','Supported passive text/continuations/transforms only;not complete inline/schema/DRS/accounting conformance']}
 result['sha256']=digest(result)
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('inline_audit_output_budget')
 return result


def _inline_preflight(entry,stored,allow_observed,planned_identity=None,has_plan=False):
 """Bind processing grants and original byte receipts before any XML parsing.

 The retained set identifies sorted document receipts and transformation choices.
 Authored acquisition order requires its separately retained intent digest. The
 embedded-linkbase choice is not retained separately; its exact graph identity is
 checked after reconstruction rather than inferred from source bytes or features.
 """
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

def reconstruct_admitted_inline(e,stored,*,allow_observed=False,planned_identity=None,has_plan=False):
 required={'documents','concepts','taxonomy_documents','transformation_profile','embedded_profile','acquisition_manifest','expected_acquisition_manifest_sha256'}
 if type(e)is not dict or set(e)!=required:raise XBRLError('financial_intelligence_inline_recipe')
 _inline_preflight(e,stored,allow_observed,planned_identity,has_plan)
 parsed=parse_document_set(e['documents'],e['concepts'],allow_observed=allow_observed,transformation_profile=e['transformation_profile'])
 if parsed['concept_profile_sha256']!=stored['concept_profile_sha256']or canonical(parsed['source'])!=canonical(stored['source'])or any(canonical(parsed[k])!=canonical(stored[k])for k in('facts','contexts','units','document_set')):raise XBRLError('financial_intelligence_inline_source_mismatch')
 refs=[d['manifest']['permission_reference']for d in sorted(e['documents'],key=lambda d:d['uri'])]
 graph=discover_inline_set(parsed,e['taxonomy_documents'],allow_observed=allow_observed,permission_references=refs,embedded_profile=e['embedded_profile'])
 if stored.get('dts_corroboration',{}).get('dts_sha256')!=graph['canonical_sha256']:raise XBRLError('financial_intelligence_inline_dts_mismatch')
 receipt=audit_inline_dts_sources(parsed,graph,e['documents'],e['taxonomy_documents'],concepts=e['concepts'],acquisition_manifest=e['acquisition_manifest'],expected_acquisition_manifest_sha256=e['expected_acquisition_manifest_sha256'],transformation_profile=e['transformation_profile'],allow_observed=allow_observed,embedded_profile=e['embedded_profile'])
 return parsed,graph,receipt
