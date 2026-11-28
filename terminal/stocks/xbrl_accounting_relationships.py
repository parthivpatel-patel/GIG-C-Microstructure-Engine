"""Explicit original-source essence/require relationships,never an inferred GAAP map."""
import copy,re
from collections import Counter,deque
from decimal import Decimal
from urllib.parse import urljoin
from .xbrl_instance import X,L,XL,tag,parse_xml,canonical,digest,XBRLError
from .xbrl_dts import uri,EMBEDDED_PROFILE,_supplied_documents
from .xbrl_dts_source_audit import audit_dts_sources
from .xbrl_relationships import number,rational
from .xbrl_types import _resolve,_value_check,BOUNDS_PROFILE

PROFILE='SOURCE_ACCOUNTING_RELATIONSHIPS_V1';SCHEMA='gig.sec.xbrl.accounting_relationships.v1'
INLINE_PROFILE='SOURCE_INLINE_ACCOUNTING_RELATIONSHIPS_V2'
INLINE_SCHEMA='gig.sec.xbrl.accounting_relationships.v2'
SCOPED_PROFILE='SOURCE_SCOPED_ACCOUNTING_RELATIONSHIPS_V3'
SCOPED_SCHEMA='gig.sec.xbrl.accounting_relationships.v3'
ESSENCE='http://www.xbrl.org/2003/arcrole/essence-alias'
REQUIRES='http://www.xbrl.org/2003/arcrole/requires-element'
MAX_ARCS=4096;MAX_NETWORKS=64;MAX_CHECKS=4096;MAX_OUTPUT=4*1024*1024

def _declarations(arc,concepts,kind):
 values=[]
 for key in('from','to'):
  item=concepts[arc[key]];decl=item['declaration']
  if decl.get('substitution_group')!=tag(X,'item'):raise XBRLError('accounting_direct_item_declaration_required')
  values.append(decl)
 a,b=values
 if kind=='essence-alias':
  if a['type']is None or b['type']is None:raise XBRLError('accounting_alias_named_type_required')
  if a['type']!=b['type']:raise XBRLError('accounting_alias_type_conflict')
  if a['period_type']not in('instant','duration')or b['period_type']not in('instant','duration'):raise XBRLError('accounting_alias_period_required')
  if a['period_type']!=b['period_type']:raise XBRLError('accounting_alias_period_conflict')
  if a['balance']is not None and b['balance']is not None and a['balance']!=b['balance']:raise XBRLError('accounting_alias_balance_conflict')
 return {'status':'SUPPORTED_DECLARATIONS','type':a['type']if kind=='essence-alias'else None,'period_type':a['period_type']if kind=='essence-alias'else None,'from_declaration':copy.deepcopy(a),'to_declaration':copy.deepcopy(b),'from_sources':list(concepts[arc['from']]['source_documents']),'to_sources':list(concepts[arc['to']]['source_documents'])}

def _member(fact,parsed,dts):
 declaration=dts['concepts'][fact['concept']]['declaration'];context=parsed['contexts'][fact['context_ref']]
 if declaration['abstract']:raise XBRLError('accounting_abstract_fact')
 if context['period']['kind']!='forever'and declaration['period_type']!=context['period']['kind']:raise XBRLError('accounting_declared_period_conflict')
 result={key:fact[key]for key in('source_fact_id','context_ref','context_sha256','unit_ref','unit_sha256','lexical_value','decimals','precision','nil')};result['reported_value']=None
 if fact['nil']:
  if not dts['concepts'][fact['concept']]['declaration']['nillable']:raise XBRLError('accounting_nil_not_declared')
  return result,'NIL_PARTICIPANT'
 typ=dts['concepts'][fact['concept']]['declaration']['type']
 if typ==tag(X,'stringItemType'):
  if fact['unit_ref']is not None:return result,'NONNUMERIC_UNIT_UNSUPPORTED'
  if fact['decimals'] is not None or fact['precision'] is not None:
   return result,'NONNUMERIC_ACCURACY_ATTRIBUTES_UNSUPPORTED'
  result['reported_value']=fact['lexical_value'];result['value_kind']='string';return result,None
 if typ==tag(X,'booleanItemType'):
  if fact['unit_ref'] is not None:return result,'NONNUMERIC_UNIT_UNSUPPORTED'
  if fact['decimals'] is not None or fact['precision'] is not None:
   return result,'NONNUMERIC_ACCURACY_ATTRIBUTES_UNSUPPORTED'
  lexical=fact['lexical_value'].strip(' \t\r\n')
  if lexical not in ('true','false','1','0'):return result,'BOOLEAN_LEXICAL_UNSUPPORTED'
  result.update(reported_value='true' if lexical in ('true','1') else 'false',value_kind='boolean')
  return result,None
 try:base,path=_resolve(typ,dts.get('type_declarations',{}),BOUNDS_PROFILE)
 except XBRLError as exc:
  if 'unsupported'in str(exc):return result,'ITEM_TYPE_VALUE_SEMANTICS_UNSUPPORTED'
  raise
 if fact['unit_ref']not in parsed['units']:return result,'NUMERIC_UNIT_MISSING'
 _value_check(fact,base,path,parsed['units'])
 result['reported_value']=format(Decimal(fact['lexical_value'].strip()),'f');result['value_kind']='numeric';return result,None

def _checks(parsed,dts,arc,kind,facts):
 left=facts.get(arc['from'],[]);right=facts.get(arc['to'],[])
 if kind=='requires-element':
  return [{'status':'SATISFIED'if left and right else'REQUIRED_ELEMENT_MISSING'if left else'NOT_TRIGGERED','source_fact_ids':[f['source_fact_id']for f in left+right],'from_fact_ids':[f['source_fact_id']for f in left],'to_fact_ids':[f['source_fact_id']for f in right],'scope':'Global concept occurrence;no context,unit,value or tuple-location comparison','selected_reported_value':None}]
 groups={}
 for side,rows in(('essence_facts',left),('alias_facts',right)):
  for fact in rows:
   context=parsed['contexts'][fact['context_ref']];key=(context['semantic_sha256'],context['identifier_lexical'])
   group=groups.setdefault(key,{'essence_facts':[],'alias_facts':[]});group[side].append(fact)
 checks=[];size=0
 for (context_hash,identifier),group in sorted(groups.items()):
  record={'context_sha256':context_hash,'identifier_lexical':identifier,'source_fact_ids':[f['source_fact_id']for f in group['essence_facts']+group['alias_facts']],'essence_facts':[],'alias_facts':[],'selected_reported_value':None,'comparison_policy':'EXACT_REPORTED_VALUES_ONLY_NOT_ROUNDING_V_EQUAL','standards_value_equality_established':False};reasons=[];units=set();values=[];exact=True
  for side in('essence_facts','alias_facts'):
   for fact in group[side]:
    member,reason=_member(fact,parsed,dts);record[side].append(member)
    if reason:reasons.append(reason)
    context=parsed['contexts'][fact['context_ref']]
    if context['dimensions']or context['opaque_segment']or context['period']['kind']=='forever':reasons.append('DIMENSIONAL_OPAQUE_OR_FOREVER_CONTEXT_UNSUPPORTED')
    if fact['unit_ref']is not None:units.add(parsed['units'][fact['unit_ref']]['semantic_sha256'])
    if member['reported_value']is not None:values.append((member['value_kind'],Decimal(member['reported_value'])if member['value_kind']=='numeric'else member['reported_value']))
    if member.get('value_kind')=='numeric'and fact['decimals']!='INF'and fact['precision']!='INF':exact=False
  record['unit_sha256s']=sorted(units)
  if len(units)>1:reasons.append('UNIT_SEMANTIC_CONFLICT')
  if reasons:record.update(status='UNSUPPORTED_ASPECTS',reason=','.join(sorted(set(reasons))))
  elif not group['essence_facts']or not group['alias_facts']:record.update(status='MISSING_COUNTERPART',reason='ESSENCE_NOT_REPORTED'if not group['essence_facts']else'ALIAS_NOT_REPORTED')
  elif len(set(values))!=1:record.update(status='CONFLICTING_REPORTED_VALUES',reason='DIFFERING_REPORTED_VALUES_NO_SELECTION_OR_ROUNDING_INFERENCE')
  else:record.update(status='SUPPORTED_EQUAL',standards_value_equality_established=exact)
  size+=len(canonical(record))
  if size>MAX_OUTPUT:raise XBRLError('accounting_relationship_output_budget')
  checks.append(record)
 if not checks:checks=[{'status':'MISSING_COUNTERPART','reason':'NEITHER_CONCEPT_REPORTED','source_fact_ids':[],'essence_facts':[],'alias_facts':[],'selected_reported_value':None}]
 return checks

def extract_accounting_relationships(parsed,dts,instance_raw,documents,*,manifest,concepts,instance_uri,allow_observed=False,embedded_profile=None,profile=PROFILE):
 if profile!=PROFILE:raise XBRLError('accounting_relationship_profile_unsupported')
 audit=audit_dts_sources(parsed,dts,instance_raw,documents,manifest=manifest,concepts=concepts,instance_uri=instance_uri,allow_observed=allow_observed,embedded_profile=embedded_profile)
 return _extract(parsed,dts,documents,audit,embedded_profile=embedded_profile)

def _extract(parsed,dts,documents,audit,*,embedded_profile=None):
 inline=parsed['schema']=='gig.sec.xbrl.inline_set.v1'
 if parsed['unsupported_nodes']:raise XBRLError('accounting_instance_unsupported_nodes')
 from .xbrl_dimensions import ARC as XDT_ARC,ROLES as XDT_ROLES
 supplied=_supplied_documents(documents);groups={};locators={};bases=[];count=0;excluded=Counter()
 facts={}
 for fact in parsed['facts']:facts.setdefault(fact['concept'],[]).append(fact)
 def exclude(source,name):
  excluded[source,name]+=1
  if len(excluded)>128 or excluded[source,name]>MAX_ARCS:raise XBRLError('accounting_relationship_exclusion_budget')
 for key,doc in sorted(supplied.items()):
  root=parse_xml(doc['raw'])
  if root.name=='{http://www.w3.org/2001/XMLSchema}schema':
   ns=root.attrs['targetNamespace']
   for node in root.children:
    if node.name=='{http://www.w3.org/2001/XMLSchema}element'and 'id'in node.attrs:locators[key+'#'+node.attrs['id']]=tag(ns,node.attrs['name'])
   embedded=[n for a in root.children if a.name=='{http://www.w3.org/2001/XMLSchema}annotation'for app in a.children if app.name=='{http://www.w3.org/2001/XMLSchema}appinfo'for n in app.children if n.name==tag(L,'linkbase')]
   if embedded and embedded_profile!=EMBEDDED_PROFILE:raise XBRLError('accounting_embedded_definition_profile_required')
   bases.extend((key,n)for n in embedded)
  elif root.name==tag(L,'linkbase'):bases.append((key,root))
 for source,root in bases:
  for link in root.children:
   if link.name in(tag(L,'presentationLink'),tag(L,'calculationLink')):continue
   if link.name in(tag(L,'labelLink'),tag(L,'referenceLink')):
    if link.attrs.get(tag(XL,'type'))!='extended':raise XBRLError('accounting_non_definition_link_structure')
    exclude(source,link.name.split('}',1)[1]);continue
   if link.name in(tag(L,'roleRef'),tag(L,'arcroleRef')):
    ref_key='roleURI' if link.name==tag(L,'roleRef') else 'arcroleURI'
    reference=link.attrs.get(ref_key,'')
    if (link.attrs.get(tag(XL,'type'))!='simple' or link.children or link.text().strip() or
        not 1<=len(reference)<=512 or not re.fullmatch(r'[A-Za-z][A-Za-z0-9+.-]*:[^\s]+',reference) or
        type(link.attrs.get(tag(XL,'href')))is not str):raise XBRLError('accounting_non_definition_reference_structure')
    uri(urljoin(source,link.attrs[tag(XL,'href')]),fragment=True)
    exclude(source,link.name.split('}',1)[1]);continue
   if link.name!=tag(L,'definitionLink'):raise XBRLError('accounting_definition_content_unsupported')
   if set(link.attrs)!={tag(XL,'type'),tag(XL,'role')}or link.attrs[tag(XL,'type')]!='extended':raise XBRLError('accounting_definition_link_structure')
   role=link.attrs[tag(XL,'role')]
   if not 1<=len(role)<=512:raise XBRLError('accounting_definition_role')
   labels={}
   for node in link.children:
    if node.name!=tag(L,'loc'):continue
    a=node.attrs
    if set(a)!={tag(XL,'type'),tag(XL,'label'),tag(XL,'href')}or a[tag(XL,'type')]!='locator'or not 1<=len(a[tag(XL,'label')])<=128 or a[tag(XL,'label')]in labels:raise XBRLError('accounting_definition_locator')
    target=locators.get(uri(urljoin(source,a[tag(XL,'href')]),fragment=True))
    if target is None:raise XBRLError('accounting_definition_unresolved_locator')
    labels[a[tag(XL,'label')]]=target
   for node in link.children:
    if node.name==tag(L,'loc'):continue
    a=node.attrs
    if node.name!=tag(L,'definitionArc')or node.children or node.text().strip()or a.get(tag(XL,'type'))!='arc'or a.get(tag(XL,'from'))not in labels or a.get(tag(XL,'to'))not in labels:raise XBRLError('accounting_definition_arc_structure')
    arcrole=a.get(tag(XL,'arcrole'))
    if type(arcrole)is str and arcrole.startswith(XDT_ARC) and arcrole[len(XDT_ARC):] in XDT_ROLES:
     # A dimensional arc is in a different base set. Keep its presence in the
     # audit receipt without interpreting it as an accounting relationship.
     exclude(source,'dimensional-definition-arc');continue
    if arcrole not in(ESSENCE,REQUIRES):raise XBRLError('accounting_definition_arcrole_unsupported')
    if set(a)-({tag(XL,k)for k in('type','from','to','arcrole')}|{'priority','use','order'}):raise XBRLError('accounting_definition_attribute_unsupported')
    priority=a.get('priority','0');use=a.get('use','optional')
    if not re.fullmatch(r'\+?[0-9]{1,6}',priority)or use not in('optional','prohibited'):raise XBRLError('accounting_definition_priority_or_use')
    order=number(a.get('order','1'),'accounting_definition_order');arcrole=a[tag(XL,'arcrole')];kind='essence-alias'if arcrole==ESSENCE else'requires-element'
    group=groups.setdefault((role,arcrole),{'kind':kind,'role':role,'arcrole':arcrole,'link_qname':tag(L,'definitionLink'),'arc_qname':tag(L,'definitionArc'),'records':[]})
    count+=1
    if count>MAX_ARCS or len(groups)>MAX_NETWORKS:raise XBRLError('accounting_relationship_budget')
    group['records'].append({'from':labels[a[tag(XL,'from')]],'to':labels[a[tag(XL,'to')]],'order':rational(order),'provenance':{'source_uri':source,'source_sha256':supplied[source]['sha256'],'link_node_ordinal':link.source_ordinal,'arc_node_ordinal':node.source_ordinal,'priority':int(priority),'use':use,'order_lexical':a.get('order','1')}})
 networks=[];check_count=0;output_size=len(canonical(audit))
 for _,group in sorted(groups.items()):
  equivalents={};arcs=[];suppressed=[]
  for record in group.pop('records'):equivalents.setdefault(canonical({k:record[k]for k in('from','to','order')}),[]).append(record)
  for _,records in sorted(equivalents.items()):
   highest=max(r['provenance']['priority']for r in records);winners=[r for r in records if r['provenance']['priority']==highest];provenance=sorted((r['provenance']for r in records),key=canonical)
   if any(r['provenance']['use']=='prohibited'for r in winners):suppressed.append({'from':records[0]['from'],'to':records[0]['to'],'order':records[0]['order'],'reason':'PROHIBITED_AT_MAX_PRIORITY','provenance':provenance});continue
   arc={k:winners[0][k]for k in('from','to','order')};arc.update(priority=highest,provenance=provenance);arc['declaration_constraints']=_declarations(arc,dts['concepts'],group['kind']);arc['checks']=_checks(parsed,dts,arc,group['kind'],facts);check_count+=len(arc['checks'])
   if check_count>MAX_CHECKS:raise XBRLError('accounting_relationship_check_budget')
   output_size+=len(canonical(arc))
   if output_size>MAX_OUTPUT:raise XBRLError('accounting_relationship_output_budget')
   arcs.append(arc)
  if group['kind']=='essence-alias':
   adjacent={};degree={}
   for arc in arcs:adjacent.setdefault(arc['from'],set()).add(arc['to']);degree.setdefault(arc['from'],0);degree.setdefault(arc['to'],0)
   for targets in adjacent.values():
    for target in targets:degree[target]+=1
   pending=deque(v for v,n in degree.items()if n==0);seen=0
   while pending:
    item=pending.popleft();seen+=1
    for target in adjacent.get(item,()):
     degree[target]-=1
     if degree[target]==0:pending.append(target)
   if seen!=len(degree):raise XBRLError('accounting_essence_directed_cycle')
  group.update(usable=True,issues=[],arcs=arcs,suppressed=suppressed);networks.append(group)
 result={'schema':INLINE_SCHEMA if inline else SCHEMA,'profile':INLINE_PROFILE if inline else PROFILE,'status':'AVAILABLE','source_filing':copy.deepcopy(parsed['source']),'parsed_sha256':parsed['canonical_sha256'],'dts_sha256':dts['canonical_sha256'],'source_audit':audit,'complete_definition_scope':True,'networks':networks,'input_arcs':count,'selected_reported_value':None,'gaap_aliases_inferred':False,'facts_inferred':False,'provider_requested':False,'complete_taxonomy_validation':False,'scope':'Original plain-source direct-item essence-alias/requires-element only;exact reported-value diagnostics,no optional value inference,no accounting metric alias or full rounding-V-equality claim'}
 if inline:result['scope']='Original inline-set direct-item essence-alias/requires-element only;exact reported-value diagnostics,no optional value inference,no accounting metric alias or full rounding-V-equality claim'
 if excluded:
  result.update(schema=SCOPED_SCHEMA,profile=SCOPED_PROFILE,
    scope='Supported source accounting arcroles only, with separate dimensional and non-accounting linkbase content recorded',
    excluded_source_content=[{'source_uri':u,'source_sha256':supplied[u]['sha256'],'kind':kind,'count':count}
                             for (u,kind),count in sorted(excluded.items())])
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('accounting_relationship_output_budget')
 result['sha256']=digest(result);return result
