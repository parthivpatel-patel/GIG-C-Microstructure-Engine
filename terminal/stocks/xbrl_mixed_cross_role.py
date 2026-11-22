"""V10 effective original-source positive/negative closed explicit DRS subset.

All supplied shapes must be supported and well formed. Only evaluated context
invalidity negates notAll; schema, source, resource and unsupported errors reject.
"""
import copy
from collections import deque
from .xbrl_instance import X,tag,canonical,digest,XBRLError
from .xbrl_cross_role import D,_originals,_read
from .xbrl_inherited_cross_role import _declaration,_validate_receipts,QN
from .xbrl_effective_cross_role import _schema_sources,_validate_schema_sources,_endpoint_sources,_effective,_project
PROFILE='ORIGINAL_DTS_MIXED_CLOSED_EXPLICIT_V10'
SCOPE='Original-DTS effective closed explicit positive/negative conjunction;at least one applicable positive cube per fact;bounded same-base primary inheritance and cross-role cube/domain paths;no typed,negative-only,open,alternative-base,unusable or general PSVI semantics'
MAX_OUTPUT=8*1024*1024;MAX_ASSIGNMENTS=64;MAX_FACT_ASSIGNMENTS=16
MAX_DOMAIN_STATES=32768;MAX_PRIMARY_STATES=32768


def _records(parsed,concepts,arcs):
 """Evaluate the supported conjunction without changing any reported source fact."""
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise XBRLError('drs_mixed_cross_arc_budget')
 by={};seen=set();defaults={};parents={}
 groups={'all':(tag(X,'item'),tag(D,'hypercubeItem')),'notAll':(tag(X,'item'),tag(D,'hypercubeItem')),'hypercube-dimension':(tag(D,'hypercubeItem'),tag(D,'dimensionItem')),'dimension-domain':(tag(D,'dimensionItem'),tag(X,'item')),'domain-member':(tag(X,'item'),tag(X,'item')),'dimension-default':(tag(D,'dimensionItem'),tag(X,'item'))}
 for a in arcs:
  if a['kind']not in groups:raise XBRLError('drs_mixed_cross_relationship_unsupported')
  key=(a['role'],a['kind'],a['from'],a['to'])
  if key in seen:raise XBRLError('drs_mixed_cross_duplicate_relationship_unsupported')
  seen.add(key);by.setdefault((a['role'],a['kind'],a['from']),[]).append(a)
  for name,group in zip((a['from'],a['to']),groups[a['kind']]):_declaration(concepts,name,group)
  if a['kind']=='dimension-default':
   prior=defaults.get(a['from'])
   if prior is not None and prior!=a['to']:raise XBRLError('drs_mixed_cross_global_default_conflict')
   defaults[a['from']]=a['to']
  elif a['kind']=='domain-member':parents.setdefault(a['to'],[]).append(a)
 assignments=[a for a in arcs if a['kind']in('all','notAll')]
 if len(defaults)>32:raise XBRLError('drs_mixed_cross_global_default_budget')
 if not 1<=len(assignments)<=MAX_ASSIGNMENTS or any(a['closed']is not True for a in assignments):raise XBRLError('drs_mixed_cross_closed_assignment_budget')
 roles={a['role']for a in assignments}
 if len(roles)!=1:raise XBRLError('drs_mixed_cross_alternative_base_roles_unsupported')
 role=assignments[0]['role'];next_role=lambda a:a['target_role']or a['role'];domain_cache={};shape_cache={};ancestor_cache={};domain_states=0;primary_states=0
 def domain(axis,source_role):
  key=(axis,source_role)
  if key in domain_cache:return domain_cache[key]
  roots=by.get((source_role,'dimension-domain',axis),[])
  if len(roots)!=1:raise XBRLError('drs_mixed_cross_single_domain_required')
  root=roots[0];members=set();completed=set();count=0
  def visit(current,member,path,depth):
   nonlocal count,domain_states
   if member in path:raise XBRLError('drs_mixed_cross_domain_cycle')
   if depth>=32:raise XBRLError('drs_mixed_cross_domain_depth')
   state=(current,member)
   if state in completed:return
   count+=1;domain_states+=1
   if domain_states>MAX_DOMAIN_STATES:raise XBRLError('drs_mixed_cross_total_domain_state_budget')
   if count>2048:raise XBRLError('drs_mixed_cross_member_budget')
   members.add(member)
   for child in by.get((current,'domain-member',member),[]):visit(next_role(child),child['to'],path|{member},depth+1)
   completed.add(state)
  visit(next_role(root),root['to'],set(),0);default=defaults.get(axis)
  if default is not None and default not in members:raise XBRLError('drs_mixed_cross_default_outside_selected_domain')
  domain_cache[key]=(members,default);return domain_cache[key]
 def shape(a):
  key=(a['from'],a['to'],next_role(a))
  if key in shape_cache:return shape_cache[key]
  axes=by.get((next_role(a),'hypercube-dimension',a['to']),[])
  if not 1<=len(axes)<=32 or len({v['to']for v in axes})!=len(axes):raise XBRLError('drs_mixed_cross_dimension_budget_or_missing')
  result={axis['to']:domain(axis['to'],next_role(axis))for axis in axes}
  if any(a['from']in members for members,_ in result.values()):raise XBRLError('drs_mixed_cross_primary_item_polymorphism')
  shape_cache[key]=result;return result
 # Every supplied assignment's supported cube shape must be well formed, even
 # when a particular selected fact does not inherit that assignment.
 for a in assignments:shape(a)
 def ancestors(concept):
  nonlocal primary_states
  if concept in ancestor_cache:return ancestor_cache[concept]
  found=set();incoming={};pending=deque([concept])
  while pending:
   node=pending.popleft()
   if node in found:continue
   found.add(node);primary_states+=1
   if primary_states>MAX_PRIMARY_STATES:raise XBRLError('drs_mixed_cross_total_primary_state_budget')
   _declaration(concepts,node,tag(X,'item'))
   if len(found)>2048:raise XBRLError('drs_mixed_cross_primary_item_budget')
   incoming[node]=[]
   for a in parents.get(node,[]):
    # The supported inherited chain stays in the original assignment base.
    # Reaching a primary ancestor through any other role is an explicit gap,
    # never an implicit role union or a guessed alternate-base conjunction.
    if a['role']!=role or next_role(a)!=role:raise XBRLError('drs_mixed_cross_primary_inheritance_role_unsupported')
    incoming[node].append(a['from']);pending.append(a['from'])
  degree={node:len(set(incoming[node]))for node in found};children={node:set()for node in found};depth={node:0 for node in found}
  for child,parents_ in incoming.items():
   for parent in parents_:children[parent].add(child)
  pending=deque(sorted(node for node in found if degree[node]==0));visited=0
  while pending:
   node=pending.popleft();visited+=1
   if depth[node]>=32:raise XBRLError('drs_mixed_cross_primary_depth')
   for child in sorted(children[node]):
    degree[child]-=1;depth[child]=max(depth[child],depth[node]+1)
    if degree[child]==0:pending.append(child)
  if visited!=len(found):raise XBRLError('drs_mixed_cross_primary_cycle')
  ancestor_cache[concept]=found;return found
 records=[];size=0
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  inherited=ancestors(fact['concept']);selected=sorted((a for a in assignments if a['from']in inherited),key=lambda a:(a['kind']!='all',a['from'],a['to']))
  if not 1<=len(selected)<=MAX_FACT_ASSIGNMENTS:raise XBRLError('drs_mixed_cross_fact_assignment_budget_or_missing')
  if not any(a['kind']=='all'for a in selected):raise XBRLError('drs_mixed_cross_positive_assignment_required')
  placements={a['context_element']for a in selected}
  if len(placements)!=1:raise XBRLError('drs_mixed_cross_mixed_context_assignments_unsupported')
  placement=selected[0]['context_element'];context=parsed['contexts'][fact['context_ref']]
  if type(context)is not dict or type(context.get('dimensions'))is not list or type(context.get('opaque_segment'))is not list:raise XBRLError('drs_mixed_cross_context_unsupported')
  dims=context['dimensions']
  if any(type(d)is not dict or set(d)!={'dimension','member','context_element','kind'}or any(type(d[k])is not str for k in d)or not QN.fullmatch(d['dimension'])or not QN.fullmatch(d['member'])for d in dims):raise XBRLError('drs_mixed_cross_context_unsupported')
  if context['semantic_sha256']!=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')})or context['opaque_segment']or len(dims)>32 or any(d['kind']!='explicit'or d['context_element']!=placement for d in dims):raise XBRLError('drs_mixed_cross_context_unsupported')
  reported={d['dimension']:d['member']for d in dims}
  if len(reported)!=len(dims):raise XBRLError('drs_mixed_cross_duplicate_dimension')
  for axis,member in reported.items():
   _declaration(concepts,axis,tag(D,'dimensionItem'));_declaration(concepts,member,tag(X,'item'))
   if defaults.get(axis)==member:raise XBRLError('drs_mixed_cross_explicit_default_member')
  aggregate={axis:member for axis,member in sorted(defaults.items())if axis not in reported};details=[];all_axes=set(defaults)|set(reported)
  if len(all_axes)>32:raise XBRLError('drs_mixed_cross_combined_dimension_budget')
  for a in selected:
   domains=shape(a);all_axes.update(domains)
   if len(all_axes)>32:raise XBRLError('drs_mixed_cross_combined_dimension_budget')
   extras=sorted(set(reported)-set(domains))
   if any(fact['concept']in members for members,_ in domains.values()):raise XBRLError('drs_mixed_cross_primary_item_polymorphism')
   used={};failure='drs_mixed_cross_closed_extra_dimension'if extras else None
   for axis,(members,default)in sorted(domains.items()):
    if axis in reported:
     if reported[axis]not in members and failure is None:failure='drs_mixed_cross_member_outside_domain'
    elif default is not None:used[axis]=default
    elif failure is None:failure='drs_mixed_cross_required_dimension_missing'
   negative=a['kind']=='notAll'
   if negative:
    if failure is None:raise XBRLError('drs_mixed_cross_negative_hypercube_satisfied')
    used={} # A false negative cube does not manufacture a value/default.
   elif failure is not None:raise XBRLError(failure)
   for axis,value in used.items():
    if axis in aggregate and aggregate[axis]!=value:raise XBRLError('drs_mixed_cross_default_conflict')
    aggregate[axis]=value
   details.append({'primary_item':a['from'],'hypercube':a['to'],'kind':a['kind'],'context_element':placement,'closed':True,'used_defaults':used,'extra_dimensions':extras,'hypercube_valid':not negative,'failure_reason':failure,'inherited':a['from']!=fact['concept'],'source_uri':a['source_uri'],'source_arc_node_ordinal':a['arc_node_ordinal']})
  record={'source_fact_id':fact['source_fact_id'],'role':role,'context_element':placement,'used_defaults':dict(sorted(aggregate.items())),'status':'VALIDATED_RESTRICTED_MIXED_CROSS_ROLE_CONTEXT','global_defaults':dict(sorted(defaults.items())),'primary_ancestors':sorted(inherited),'assignments':details}
  size+=len(canonical(record))
  if size>MAX_OUTPUT:raise XBRLError('drs_mixed_cross_output_budget')
  records.append(record)
 return records

def corroborate_mixed_cross_role(parsed,dts,documents,allow_observed,instance_uri):
 supplied=_originals(parsed,dts,documents,allow_observed,instance_uri)
 schema_sources=_schema_sources(supplied,dts['documents']);schemas=_validate_schema_sources(schema_sources,dts['documents'])
 arcs,refs=_read(parsed,dts,supplied,effective=True,negative=True);_endpoint_sources(arcs,dts['concepts'],schemas);effective,resolution=_effective(arcs,negative=True)
 records=_records(parsed,dts['concepts'],effective)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256')
 result['schema']='gig.sec.xbrl.dimensional_inline_set.v10'if parsed['schema']=='gig.sec.xbrl.inline_set.v1'else'gig.sec.xbrl.dimensional_instance.v10'
 result['dts_corroboration']['dimensional_validation']={'profile':PROFILE,'facts':records,'relationships':arcs,'role_references':refs,'schema_sources':schema_sources,'effective_relationships':effective,'resolution':resolution,'complete_drs_validation':False,'scope':SCOPE}
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('drs_mixed_cross_output_budget')
 result['canonical_sha256']=digest(result);return result


def validate_mixed_cross_role_result(parsed):
 fail=lambda:XBRLError('xbrl_dimensional_result_contract')
 try:
  p=parsed['dts_corroboration']['dimensional_validation']
  if type(p)is not dict or set(p)!={'profile','facts','relationships','role_references','schema_sources','effective_relationships','resolution','complete_drs_validation','scope'}or p['profile']!=PROFILE or p['scope']!=SCOPE or p['complete_drs_validation']is not False or len(canonical(parsed))>MAX_OUTPUT:raise fail()
  effective,resolution=_effective(p['relationships'],negative=True)
  receipts={'relationships':[_project(a)for a in p['relationships']],'role_references':p['role_references']}
  concepts,_=_validate_receipts(parsed,receipts,negative=True)
  schemas=_validate_schema_sources(p['schema_sources'],parsed['dts_corroboration']['documents']);_endpoint_sources(p['relationships'],concepts,schemas)
  if p['relationships']!=sorted(p['relationships'],key=lambda a:(a['source_uri'],a['arc_node_ordinal'])):raise fail()
  if canonical(effective)!=canonical(p['effective_relationships'])or canonical(resolution)!=canonical(p['resolution'])or canonical(_records(parsed,concepts,effective))!=canonical(p['facts']):raise fail()
 except (XBRLError,KeyError,TypeError,ValueError,OverflowError):raise fail()from None
