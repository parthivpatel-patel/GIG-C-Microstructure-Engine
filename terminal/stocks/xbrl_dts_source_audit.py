"""Opt-in exact reconstruction of a plain-instance/DTS artifact from raw sources.

Hashes establish identity consistency,not independent source authentication. This
separate API requires original bytes and explicit parse choices;legacy binders and
source permissions/defaults are unchanged. Inline sets require a future contract.
"""
from .xbrl_instance import parse_instance,validate_manifest,digest,canonical,XBRLError
from .xbrl_dts import discover,uri,EMBEDDED_PROFILE,_supplied_documents
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
