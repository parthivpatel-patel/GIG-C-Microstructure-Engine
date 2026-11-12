"""Explicit single-role closed-hypercube corroboration,not complete DRS validity."""
import copy
import re
from collections import deque
from urllib.parse import urljoin
from .xbrl_instance import X,L,XL,tag,digest,canonical,XBRLError
D='http://xbrl.org/2005/xbrldt';ARC='http://xbrl.org/int/dim/arcrole/';PROFILE='EXPLICIT_CLOSED_HYPERCUBE_V1'
ROLES={'all','notAll','hypercube-dimension','dimension-domain','domain-member','dimension-default'}

def networks(linkbases,locators):
 from .xbrl_dts import uri
 result=[]
 for source,root in linkbases:
  for link in root.children:
   if link.name!=tag(L,'definitionLink'):continue
   if len(result)>=64:raise XBRLError('drs_network_budget')
   if link.attrs.get(tag(XL,'type'))!='extended'or type(link.attrs.get(tag(XL,'role')))is not str or not 1<=len(link.attrs[tag(XL,'role')])<=512:raise XBRLError('drs_link_structure')
   labels={};arcs=[];issues=set()
   for node in link.children:
    if node.name==tag(L,'loc'):
     label=node.attrs.get(tag(XL,'label'));href=node.attrs.get(tag(XL,'href'))
     if node.attrs.get(tag(XL,'type'))!='locator'or type(label)is not str or not 1<=len(label)<=128 or type(href)is not str or label in labels:raise XBRLError('drs_locator')
     labels[label]=locators.get(uri(urljoin(source,href),fragment=True))
     if labels[label]is None:issues.add('UNRESOLVED_LOCATOR')
   for node in link.children:
    if node.name==tag(L,'loc'):continue
    if node.name!=tag(L,'definitionArc'):issues.add('UNSUPPORTED_DEFINITION_CONTENT');continue
    a=node.attrs;role=a.get(tag(XL,'arcrole'),'');kind=role[len(ARC):]if role.startswith(ARC)else''
    if a.get(tag(XL,'type'))!='arc'or a.get(tag(XL,'from'))not in labels or a.get(tag(XL,'to'))not in labels:raise XBRLError('drs_arc_structure')
    if not re.fullmatch(r'[+-]?[0-9]{1,24}(?:\.[0-9]{1,12})?',a.get('order','1')):raise XBRLError('drs_order_subset')
    allowed={tag(XL,k)for k in('type','arcrole','from','to')}|{'order','priority','use'}|{tag(D,k)for k in('closed','contextElement','usable','targetRole')}
    if kind not in ROLES or set(a)-allowed or a.get('priority','0')!='0'or a.get('use','optional')!='optional'or tag(D,'targetRole')in a:issues.add('ROLE_PRECEDENCE_OR_ATTRIBUTE_UNSUPPORTED')
    if a.get(tag(D,'usable'),'true')not in('true','1'):issues.add('UNUSABLE_RELATIONSHIP_UNSUPPORTED')
    closed=a.get(tag(D,'closed'),'false');placement=a.get(tag(D,'contextElement'))
    if closed not in('true','false','1','0'):raise XBRLError('drs_boolean')
    if kind in('all','notAll')and placement not in('segment','scenario'):raise XBRLError('drs_context_element')
    if kind not in('all','notAll')and(tag(D,'closed')in a or tag(D,'contextElement')in a):issues.add('RELATIONSHIP_ATTRIBUTE_SCOPE_UNSUPPORTED')
    arcs.append({'kind':kind,'from':labels[a[tag(XL,'from')]],'to':labels[a[tag(XL,'to')]],'closed':closed in('true','1'),'context_element':placement,'source_uri':source})
    if len(arcs)>4096:raise XBRLError('drs_arc_budget')
   result.append({'role':link.attrs[tag(XL,'role')],'source_uri':source,'arcs':arcs,'issues':sorted(issues),'usable_for_restricted_profile':not issues})
 if len(result)!=1:
  for network in result:network['usable_for_restricted_profile']=False;network['issues'].append('MULTIPLE_DEFINITION_LINKS_UNSUPPORTED')
 return result

def corroborate(parsed,dts):
 if type(parsed)is not dict or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256')or type(dts)is not dict or digest({k:v for k,v in dts.items()if k!='canonical_sha256'})!=dts.get('canonical_sha256'):raise XBRLError('drs_input_identity')
 if parsed.get('dts_corroboration',{}).get('dts_sha256')!=dts['canonical_sha256']:raise XBRLError('drs_binding_required')
 nets=dts.get('definition',[])
 if not dts['structural_closure']or len(nets)!=1 or not nets[0]['usable_for_restricted_profile']:raise XBRLError('drs_profile_unsupported')
 arcs=nets[0]['arcs'];concepts=dts['concepts'];adj={};domains={}
 if any(a['kind']=='notAll'for a in arcs):raise XBRLError('drs_not_all_unsupported')
 if len([a for a in arcs if a['kind']=='all'])!=1:raise XBRLError('drs_single_positive_assignment_required')
 for arc in arcs:adj.setdefault((arc['kind'],arc['from']),set()).add(arc['to'])
 def declaration(name,group):
  value=concepts.get(name,{}).get('declaration',{})
  if value.get('substitution_group')!=group or value.get('typed_domain_ref')is not None:raise XBRLError('drs_declaration_unsupported')
  if group in(tag(D,'hypercubeItem'),tag(D,'dimensionItem'))and not value.get('abstract'):raise XBRLError('drs_abstract_declaration_required')
 def targets(kind,name):return sorted(adj.get((kind,name),()))
 def domain(axis):
  if axis in domains:return domains[axis]
  declaration(axis,tag(D,'dimensionItem'));roots=targets('dimension-domain',axis)
  if len(roots)!=1:raise XBRLError('drs_single_domain_required')
  members=set();pending=deque(roots)
  while pending:
   member=pending.popleft()
   if member in members:continue
   declaration(member,tag(X,'item'));members.add(member)
   if len(members)>2048:raise XBRLError('drs_member_budget')
   pending.extend(targets('domain-member',member))
  degree={member:0 for member in members};depth={member:0 for member in members}
  for member in members:
   for child in targets('domain-member',member):degree[child]+=1
  pending=deque(member for member in members if degree[member]==0);visited=0
  while pending:
   member=pending.popleft();visited+=1
   if depth[member]>=32:raise XBRLError('drs_domain_depth')
   for child in targets('domain-member',member):
    degree[child]-=1;depth[child]=max(depth[child],depth[member]+1)
    if degree[child]==0:pending.append(child)
  if visited!=len(members):raise XBRLError('drs_domain_cycle')
  default=targets('dimension-default',axis)
  if len(default)>1 or default and default[0]not in members:raise XBRLError('drs_default_conflict_or_domain')
  domains[axis]=(members,default);return domains[axis]
 records=[];size=len(canonical(parsed))
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  assignments=[a for a in arcs if a['kind']=='all'and a['from']==fact['concept']]
  if len(assignments)!=1 or not assignments[0]['closed']:raise XBRLError('drs_direct_closed_assignment_required')
  assignment=assignments[0];cube=assignment['to'];declaration(fact['concept'],tag(X,'item'));declaration(cube,tag(D,'hypercubeItem'))
  axes=targets('hypercube-dimension',cube)
  if not axes or len(axes)>32:raise XBRLError('drs_dimension_budget_or_missing')
  context=parsed['contexts'][fact['context_ref']]
  if context['opaque_segment']or any(d['kind']!='explicit'or d['context_element']!=assignment['context_element']for d in context['dimensions']):raise XBRLError('drs_context_profile_unsupported')
  given={d['dimension']:d['member']for d in context['dimensions']}
  if set(given)-set(axes):raise XBRLError('drs_closed_extra_dimension')
  defaults={}
  for axis in axes:
   members,default=domain(axis)
   if axis in given:
    if given[axis]not in members:raise XBRLError('drs_member_outside_domain')
    if default and given[axis]==default[0]:raise XBRLError('drs_explicit_default_member')
   elif default:defaults[axis]=default[0]
   else:raise XBRLError('drs_required_dimension_missing')
  record={'source_fact_id':fact['source_fact_id'],'role':nets[0]['role'],'hypercube':cube,'context_element':assignment['context_element'],'used_defaults':defaults,'status':'VALIDATED_RESTRICTED_EXPLICIT_CONTEXT'};size+=len(canonical(record))+1
  if size>8*1024*1024:raise XBRLError('drs_output_budget')
  records.append(record)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256');result['dts_corroboration']['dimensional_validation']={'profile':PROFILE,'facts':records,'complete_drs_validation':False,'scope':'Single direct positive closed hypercube,one role,explicit dimensions and supplied domains/defaults only;no context/fact synthesis'}
 if len(canonical(result))>8*1024*1024:raise XBRLError('drs_output_budget')
 result['canonical_sha256']=digest(result);return result
