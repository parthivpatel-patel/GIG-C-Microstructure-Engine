"""Supplied-DTS declaration corroboration,not complete XML Schema validation.

Join by exact source hash and expanded concept name. Contradictions in selected
facts fail the whole batch. Custom types,dimensions/DRS,calculations and complete
statements remain unverified;no QName/type/unit mapping is guessed here.
"""
import copy
from .xbrl_instance import digest,canonical,XBRLError

def bind_declarations(parsed,dts):
 if type(parsed)is not dict or parsed.get('schema')not in('gig.sec.xbrl.instance.v1','gig.sec.xbrl.inline_set.v1')or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256'):raise XBRLError('dts_binding_instance_identity')
 if type(dts)is not dict or dts.get('schema')not in('gig.sec.xbrl.dts.v1','gig.sec.xbrl.dts_set.v1')or digest({k:v for k,v in dts.items()if k!='canonical_sha256'})!=dts.get('canonical_sha256'):raise XBRLError('dts_binding_graph_identity')
 is_set=parsed['schema']=='gig.sec.xbrl.inline_set.v1'
 if is_set:
  if dts['schema']!='gig.sec.xbrl.dts_set.v1'or parsed['document_set']['sha256']!=dts['document_set_sha256']:raise XBRLError('dts_binding_source_scope')
 elif dts['schema']!='gig.sec.xbrl.dts.v1'or parsed['source']['source_sha256']!=dts['instance_sha256']:raise XBRLError('dts_binding_source_scope')
 if parsed['origin']!=dts['origin']or parsed['source']['origin']!=parsed['origin']:raise XBRLError('dts_binding_source_scope')
 selected=[];unverified=0
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):unverified+=1;continue
  entry=dts['concepts'].get(fact['concept'])
  if entry is None:raise XBRLError('dts_binding_selected_declaration_missing')
  declaration=entry['declaration'];period=parsed['contexts'][fact['context_ref']]['period']['kind']
  if declaration['period_type']!=period:raise XBRLError('dts_binding_period_conflict')
  if declaration['abstract']:raise XBRLError('dts_binding_abstract_fact')
  if fact['nil']and not declaration['nillable']:raise XBRLError('dts_binding_nil_not_declared')
  selected.append({'source_fact_id':fact['source_fact_id'],'concept':fact['concept'],'source_documents':entry['source_documents'],'period_type':period,'declared_type':declaration['type'],'type_validation':'NOT_PERFORMED'})
 result=copy.deepcopy(parsed);result.pop('canonical_sha256')
 result['dts_corroboration']={'profile':'SELECTED_DECLARATION_CONSISTENCY_V1','dts_sha256':dts['canonical_sha256'],'documents':dts['documents'],'selected_facts':selected,'unverified_facts':unverified,'structural_closure':dts['structural_closure'],'unresolved':dts['unresolved'],'unsupported_semantics':dts['unsupported_semantics'],'schema_type_validation':False,'complete_statements':False,'accounting_mapping':'Existing explicit selected-fact profile;not derived from presentation ordering','received_at_authority':'Original supplied receipt only;missing stays unknown'}
 result['dts_corroboration']['definition_relationships_present']=None if any(u['feature']=='EMBEDDED_LINKBASE_UNSUPPORTED'for u in dts['unsupported_semantics'])else bool(dts.get('definition'))
 if 'type_declarations'in dts:result['dts_corroboration']['type_declarations']=copy.deepcopy(dts['type_declarations'])
 if 'effective_relationships'in dts:result['dts_corroboration']['effective_relationships']=copy.deepcopy(dts['effective_relationships']);result['dts_corroboration']['concept_declarations']=copy.deepcopy(dts['concepts'])
 result['taxonomy_authority']='Supplied DTS declaration consistency plus explicit selected-fact profile;full type/DRS/accounting validation not performed'
 if len(canonical(result))>8*1024*1024:raise XBRLError('dts_binding_output_budget')
 result['canonical_sha256']=digest(result);return result
