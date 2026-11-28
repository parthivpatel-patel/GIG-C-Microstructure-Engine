"""Standalone source-bound typed-domain scalar checks; never full DRS acceptance.

Original contexts/facts/identities are not rewritten or promoted. Only the explicit
profile is supported. Complex and anonymous domain types remain outside the supported profiles.
"""
from datetime import date
import re
from urllib.parse import urljoin,urldefrag
from .xbrl_instance import X,I,tag,qname,parse_xml,canonical,digest,XBRLError,MAX_CONTEXTS,MAX_FACTS
from .xbrl_dts import _supplied_documents,uri
from .xbrl_types import XS,RESTRICTION_PROFILE,declaration,_resolve,_numeric_lexical,_facet_checks,_enumeration_definitions

D='http://xbrl.org/2005/xbrldt';PROFILE='TYPED_DOMAIN_SCALAR_V1'
BOUNDS_PROFILE='TYPED_DOMAIN_SCALAR_V2'
QNAME_NIL_PROFILE='TYPED_DOMAIN_SCALAR_V3'
TEMPORAL_PROFILE='TYPED_DOMAIN_SCALAR_V4'
SCALAR_PROFILES=(PROFILE,BOUNDS_PROFILE,QNAME_NIL_PROFILE,TEMPORAL_PROFILE)
TEMPORAL_TYPES={tag(XS,k):k for k in ('date','dateTime','time')}
STRING_TYPES={tag(XS,k):k for k in ('normalizedString','token','language')}
XML_NAMESPACE='http://www.w3.org/XML/1998/namespace'
NCNAME=re.compile('[A-Za-z_][A-Za-z0-9_.-]{0,127}')
MAX_RECORDS=4096;MAX_OUTPUT=8*1024*1024;MAX_TEXT=4096

def _identity(value):
 return type(value)is dict and digest({k:v for k,v in value.items()if k!='canonical_sha256'})==value.get('canonical_sha256')

def _sources(dts,documents):
 supplied=_supplied_documents(documents);loaded={row['uri']:row for row in dts['documents']};elements={};types={};records=[];seen_concepts=set()
 if any(key not in loaded or doc['sha256']!=loaded[key]['sha256']for key,doc in supplied.items()):raise XBRLError('typed_source_not_bound_to_dts')
 if any(row['kind']=='schema'and key not in supplied for key,row in loaded.items()):raise XBRLError('typed_original_schema_required')
 for key in sorted(supplied):
  if loaded[key]['kind']!='schema':continue
  doc=supplied[key];root=parse_xml(doc['raw'])
  if root.name!=tag(XS,'schema')or type(root.attrs.get('targetNamespace'))is not str:raise XBRLError('typed_schema_root')
  namespace=root.attrs['targetNamespace'];names=set();ids=set()
  pending=[root]
  while pending:
   node=pending.pop()
   if '{http://www.w3.org/XML/1998/namespace}base'in node.attrs:raise XBRLError('typed_xml_base_unsupported')
   pending.extend(node.children)
  for node in root.children:
   if node.name in(tag(XS,'simpleType'),tag(XS,'complexType')):
    name=node.attrs.get('name');expanded=tag(namespace,name)if type(name)is str else None;entry=dts.get('type_declarations',{}).get(expanded)
    if entry is None or declaration(node)!=entry['declaration']or key not in entry['source_documents']:raise XBRLError('typed_type_source_binding')
    types.setdefault(expanded,[]).append(node.name)
   if node.name!=tag(XS,'element'):continue
   name=node.attrs.get('name');id_=node.attrs.get('id')
   if type(name)is not str or name in names or id_ is not None and id_ in ids:raise XBRLError('typed_schema_element_identity')
   names.add(name)
   if id_ is not None:ids.add(id_)
   expanded=tag(namespace,name);seen_concepts.add(expanded);entry=dts['concepts'].get(expanded)
   if entry is None or key not in entry['source_documents']:raise XBRLError('typed_element_source_binding')
   record={'concept':expanded,'type':qname(node.attrs['type'],node)if 'type'in node.attrs else None,'substitution_group':qname(node.attrs['substitutionGroup'],node)if 'substitutionGroup'in node.attrs else None,'period_type':node.attrs.get(tag(X,'periodType')),'balance':node.attrs.get(tag(X,'balance')),'abstract':node.attrs.get('abstract','false')in('true','1'),'nillable':node.attrs.get('nillable','false')in('true','1')}
   if tag(D,'typedDomainRef')in node.attrs:record['typed_domain_ref']=uri(urljoin(key,node.attrs[tag(D,'typedDomainRef')]),fragment=True)
   if record!=entry['declaration']:raise XBRLError('typed_element_source_binding')
   if id_ is not None:elements[key+'#'+id_]=(expanded,node,key)
  records.append({'uri':key,'sha256':doc['sha256']})
 if seen_concepts!=set(dts['concepts'])or set(types)!=set(dts.get('type_declarations',{})):raise XBRLError('typed_original_declaration_coverage')
 return elements,types,records

def _domain(axis,dts,elements,schema_uris):
 entry=dts['concepts'].get(axis)
 if entry is None:raise XBRLError('typed_axis_declaration_missing')
 value=entry['declaration']
 if value.get('abstract')is not True:raise XBRLError('typed_axis_declaration_invalid')
 if value.get('substitution_group')!=tag(D,'dimensionItem'):
  if value.get('substitution_group')in(tag(X,'item'),tag(D,'hypercubeItem')):raise XBRLError('typed_axis_declaration_invalid')
  return None,'TYPED_AXIS_SUBSTITUTION_CHAIN_UNSUPPORTED'
 reference=value.get('typed_domain_ref')
 if type(reference)is not str or not urldefrag(reference)[1]:raise XBRLError('typed_domain_reference_required')
 # Only a bare schema element ID is supported; no guessed XPointer evaluation.
 if not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',urldefrag(reference)[1]):return None,'TYPED_DOMAIN_POINTER_UNSUPPORTED'
 if urldefrag(reference)[0]not in schema_uris:raise XBRLError('typed_domain_schema_outside_dts')
 if reference not in elements:raise XBRLError('typed_domain_global_element_missing')
 concept,node,key=elements[reference];decl=dts['concepts'][concept]['declaration']
 if decl['abstract']:raise XBRLError('typed_domain_abstract_target')
 if set(node.attrs)-{'id','name','type','abstract','nillable'}or any(child.name!=tag(XS,'annotation')for child in node.children):return None,'TYPED_DOMAIN_DECLARATION_STRUCTURE_UNSUPPORTED'
 if decl['type']is None:return None,'TYPED_DOMAIN_ANONYMOUS_TYPE_UNSUPPORTED'
 return {'concept':concept,'type':decl['type'],'schema_uri':key,'schema_id':node.attrs['id'],'typed_domain_ref':reference},None

def _qname_value(lexical,namespaces):
 parts=lexical.split(':')
 if len(parts)>2 or not all(NCNAME.fullmatch(part) for part in parts):
  raise XBRLError('typed_qname_lexical')
 if len(parts)==1:
  return {'namespace':namespaces.get('') or None,'local_name':parts[0]}
 prefix,local=parts
 namespace=XML_NAMESPACE if prefix=='xml' else namespaces.get(prefix)
 if not namespace or prefix=='xmlns':
  raise XBRLError('typed_qname_unbound_prefix')
 return {'namespace':namespace,'local_name':local}

def _temporal(lexical,kind):
 day=r'(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2})'
 clock=r'(?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2})(?:\.(?P<f>[0-9]{1,18}))?'
 timezone=r'(?P<zone>Z|[+-][0-9]{2}:[0-9]{2})?'
 shape=day if kind=='date' else clock if kind=='time' else day+'T'+clock
 match=re.fullmatch(shape+timezone,lexical)
 if match is None:raise XBRLError('typed_temporal_lexical_subset')
 parts=match.groupdict();zone=parts['zone']
 if zone not in (None,'Z'):
  hours,minutes=int(zone[1:3]),int(zone[4:])
  if hours>14 or minutes>59 or hours==14 and minutes:raise XBRLError('typed_temporal_timezone')
 if 'day'in parts:
  try:date.fromisoformat(parts['day'])
  except ValueError:raise XBRLError('typed_temporal_calendar')from None
 if 'h'in parts:
  h,m,s=(int(parts[k])for k in ('h','m','s'))
  fraction=parts['f'] or ''
  if h>24 or m>59 or s>59 or h==24 and (m or s or any(c!='0'for c in fraction)):
   raise XBRLError('typed_temporal_clock')
 return {'validation':'TEMPORAL_LEXICAL_VALIDATED','timezone_present':zone is not None}


def _scalar(member,domain,dts,types,*,profile=PROFILE):
 if type(member)is not dict or set(member)-{'name','attributes','namespaces','text','children','content_order'}or not {'name','attributes','namespaces','text','children'}<=set(member):raise XBRLError('typed_member_tree_contract')
 if type(member['name'])is not str or type(member['attributes'])is not dict or type(member['namespaces'])is not dict or type(member['text'])is not str or type(member['children'])is not list:raise XBRLError('typed_member_tree_contract')
 if profile!=PROFILE:
  namespaces=member['namespaces']
  if len(namespaces)>32 or any(type(k)is not str or k and not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',k)or type(v)is not str or len(v)>512 for k,v in namespaces.items())or 'content_order'in member and not member['children']:raise XBRLError('typed_member_tree_contract')
 if member['name']!=domain['concept']:raise XBRLError('typed_domain_element_mismatch')
 if member['children']:return 'TYPED_DOMAIN_COMPLEX_CONTENT_UNSUPPORTED',None
 attributes=member['attributes']
 nil_attribute=tag(I,'nil')
 expanded=profile in(QNAME_NIL_PROFILE,TEMPORAL_PROFILE)
 if attributes and (not expanded or set(attributes)!={nil_attribute}):
  return 'TYPED_DOMAIN_ATTRIBUTES_OR_NIL_UNSUPPORTED',None
 nil_lexical=attributes.get(nil_attribute,'false')
 if nil_lexical not in ('true','false','1','0'):
  raise XBRLError('typed_domain_nil_lexical')
 nil=nil_lexical in ('true','1')
 text=member['text']
 if type(text)is not str or len(text)>MAX_TEXT:raise XBRLError('typed_scalar_text_budget')
 declared=domain['type']
 if nil:
  if text or dts['concepts'][domain['concept']]['declaration']['nillable'] is not True:
   raise XBRLError('typed_domain_nil_not_allowed')
  if declared in (tag(XS,'string'),tag(XS,'boolean'),tag(XS,'QName')) or (
      profile==TEMPORAL_PROFILE and declared in TEMPORAL_TYPES.keys()|STRING_TYPES.keys()):
   return None,{'resolved_type':declared,'validation':'DECLARED_NIL_TYPED_SCALAR'}
 if declared==tag(XS,'string'):return None,{'resolved_type':declared,'validation':'STRING_LEXICAL_RETAINED'}
 lexical=text.strip(' \t\r\n')
 if profile==TEMPORAL_PROFILE:
  if declared in TEMPORAL_TYPES:
   return None,{'resolved_type':declared,**_temporal(lexical,TEMPORAL_TYPES[declared])}
  if declared in STRING_TYPES:
   kind=STRING_TYPES[declared]
   normalized=re.sub('[ \t\r\n]+',' ',text).strip(' ') if kind!='normalizedString' else re.sub('[\t\r\n]',' ',text)
   if kind=='language'and not re.fullmatch('[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*',normalized):
    raise XBRLError('typed_language_lexical')
   return None,{'resolved_type':declared,'validation':'XML_WHITESPACE_NORMALIZED','normalized_value':normalized}
 if declared==tag(XS,'QName') and expanded:
  return None,{'resolved_type':declared,'validation':'QNAME_LEXICAL_VALIDATED',
               'expanded_value':_qname_value(lexical,member['namespaces'])}
 if declared==tag(XS,'boolean'):
  if lexical not in('true','false','1','0'):raise XBRLError('typed_boolean_lexical')
  return None,{'resolved_type':declared,'validation':'BOOLEAN_LEXICAL_VALIDATED'}
 numeric_profile=RESTRICTION_PROFILE
 if profile!=PROFILE:
  from .xbrl_types import BOUNDS_PROFILE as numeric_profile
 try:base,path=_resolve(declared,dts.get('type_declarations',{}),numeric_profile)
 except XBRLError as exc:
  if 'unsupported'in str(exc):return 'TYPED_DOMAIN_TYPE_UNSUPPORTED',None
  raise
 if not base.startswith('{'+XS+'}')or any(kind!=tag(XS,'simpleType')for row in path for kind in types.get(row['type'],[])):return 'TYPED_DOMAIN_NUMERIC_COMPLEX_OR_ITEM_TYPE_UNSUPPORTED',None
 _enumeration_definitions(base,path)
 if nil:
  return None,{'resolved_type':base,'declared_type':declared,'validation':'DECLARED_NIL_TYPED_SCALAR'}
 value=_numeric_lexical(lexical,base);_facet_checks(value,lexical,path)
 result={'resolved_type':base,'validation':'NUMERIC_SCALAR_VALIDATED','numeric_profile':numeric_profile,'restriction_types':[row['type']for row in path]}
 if profile!=PROFILE:
  from .xbrl_types import _bound_restrictions
  result.update(declared_type=declared,restrictions=path,effective_bounds=_bound_restrictions(base,path))
 return None,result

def check_typed_contexts(parsed,dts,documents,*,profile=PROFILE,allow_observed=False):
 """Return separate typed-scalar diagnostics;do not mutate or accept a filing."""
 if profile not in SCALAR_PROFILES:raise XBRLError('typed_profile_unsupported')
 if not _identity(parsed)or not _identity(dts):raise XBRLError('typed_input_identity')
 origin=parsed.get('origin')
 if type(allow_observed)is not bool or origin not in('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE')or dts.get('origin')!=origin or type(parsed.get('source'))is not dict or parsed['source'].get('origin')!=origin:raise XBRLError('typed_origin_scope')
 if origin=='OBSERVED_OFFICIAL_RESPONSE':
  if not allow_observed:raise XBRLError('typed_observed_processing_not_approved')
  if parsed.get('schema')=='gig.sec.xbrl.inline_set.v1':
   originals=parsed.get('document_set',{}).get('documents',[])
   hashes=[row.get('source',{}).get('permission_reference_sha256')for row in originals]
   actual=dts.get('permission_reference_sha256s')
  else:hashes=[parsed.get('source',{}).get('permission_reference_sha256')];actual=[dts.get('permission_reference_sha256')]
  if not hashes or any(type(value)is not str or not re.fullmatch('[0-9a-f]{64}',value)for value in hashes)or hashes!=actual:raise XBRLError('typed_observed_permission_binding')
 if len(canonical(parsed))>MAX_OUTPUT or len(canonical(dts))>MAX_OUTPUT:raise XBRLError('typed_input_budget')
 if parsed.get('dts_corroboration',{}).get('dts_sha256')!=dts['canonical_sha256']:raise XBRLError('typed_dts_binding_required')
 if dts.get('structural_closure')is not True:raise XBRLError('typed_dts_closure_required')
 if parsed.get('schema')not in('gig.sec.xbrl.instance.v1','gig.sec.xbrl.inline_set.v1'):raise XBRLError('typed_input_schema_unsupported')
 contexts=parsed.get('contexts');facts=parsed.get('facts')
 if type(contexts)is not dict or len(contexts)>MAX_CONTEXTS or type(facts)is not list or len(facts)>MAX_FACTS:raise XBRLError('typed_input_counts')
 if profile!=PROFILE:
  from .xbrl_types import _bound_sources
  proof,_,_=_bound_sources(parsed)
  for key,expected in(('documents',dts['documents']),('concept_declarations',dts['concepts']),('type_declarations',dts.get('type_declarations',{}))):
   if canonical(proof.get(key,{}))!=canonical(expected):raise XBRLError('typed_bound_retained_graph_mismatch')
 elements,types,sources=_sources(dts,documents)
 if profile!=PROFILE:
  from .xbrl_typed_bounds import _declarations
  from .xbrl_effective_cross_role import _schema_sources,_validate_schema_sources
  schemas=_schema_sources(_supplied_documents(documents),dts['documents'])
  _declarations(dts['concepts'],dts.get('type_declarations',{}),_validate_schema_sources(schemas,dts['documents']))
 used={key:[]for key in contexts};fact_ids=set()
 for fact in facts:
  if type(fact)is not dict or fact.get('context_ref')not in contexts or type(fact.get('source_fact_id'))is not str:raise XBRLError('typed_fact_context_binding')
  if fact['source_fact_id']in fact_ids:raise XBRLError('typed_duplicate_source_fact_id')
  fact_ids.add(fact['source_fact_id']);used[fact['context_ref']].append(fact['source_fact_id'])
 output=[];count=unsupported=0;size=0
 for context_id,context in sorted(contexts.items()):
  if type(context)is not dict or type(context.get('dimensions'))is not list or len(context['dimensions'])>32:raise XBRLError('typed_context_contract')
  semantic={key:context[key]for key in('issuer_cik','period','dimensions','opaque_segment')}
  if context.get('semantic_sha256')!=digest(semantic):raise XBRLError('typed_context_identity')
  members=[]
  for dimension in context['dimensions']:
   if type(dimension)is not dict or type(dimension.get('dimension'))is not str:raise XBRLError('typed_dimension_contract')
   if dimension.get('kind')!='typed':continue
   if set(dimension)!={'dimension','context_element','kind','member'}or type(dimension['member'])is not dict:raise XBRLError('typed_dimension_contract')
   count+=1
   if count>MAX_RECORDS:raise XBRLError('typed_record_budget')
   if dimension.get('context_element')not in('segment','scenario'):raise XBRLError('typed_context_placement')
   domain,reason=_domain(dimension.get('dimension'),dts,elements,{row['uri']for row in sources})
   record={'dimension':dimension['dimension'],'context_element':dimension['context_element'],'member_tree_sha256':digest(dimension['member'])}
   if domain is not None:
    record['domain']=domain;reason,validation=_scalar(dimension['member'],domain,dts,types,profile=profile)
    if reason is None:record['scalar_validation']=validation
   record['status']='UNSUPPORTED'if reason else'VALIDATED_SUPPORTED_TYPED_SCALAR'
   if reason:record['reason']=reason;unsupported+=1
   members.append(record);size+=len(canonical(record))
   if size>MAX_OUTPUT:raise XBRLError('typed_output_budget')
  if members:output.append({'context_id':context_id,'context_semantic_sha256':context['semantic_sha256'],'source_fact_ids':list(used[context_id]),'typed_members':members})
 result={'schema':f'gig.sec.xbrl.typed_context_diagnostics.v{SCALAR_PROFILES.index(profile)+1}','profile':profile,'parsed_sha256':parsed['canonical_sha256'],'dts_sha256':dts['canonical_sha256'],'source_schemas':sources,'contexts':output,'typed_member_count':count,'unsupported_member_count':unsupported,'status':'UNSUPPORTED_TYPED_DOMAIN_SEMANTICS'if unsupported else'VALIDATED_SUPPORTED_TYPED_SCALARS'if count else'NO_TYPED_MEMBERS','complete_drs_validation':False,'financial_admission_changed':False,'provider_requested':False,'scope':'Supplied original schema and typed scalar validation only;no hypercube validity,typed equality,context normalization,fact selection or financial promotion'}
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('typed_output_budget')
 result['sha256']=digest(result);return result
