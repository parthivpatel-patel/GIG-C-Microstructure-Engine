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
ALTERNATIVE_PROFILE='ORIGINAL_DTS_ALTERNATIVE_CLOSED_EXPLICIT_V13'
ALTERNATIVE_SCOPE='Original-DTS closed explicit alternatives across assignment roles;each applicable role uses a positive/negative conjunction with a positive assignment;one or more valid roles required;no typed,open,negative-only or cross-role primary inheritance'
PRIMARY_TARGET_ROLE_PROFILE='ORIGINAL_DTS_PRIMARY_TARGET_ROLE_EXPLICIT_V16'
PRIMARY_TARGET_ROLE_SCOPE='Original-DTS closed explicit alternatives with bounded consecutive primary domain-member targetRole traversal;effective positive/negative conjunctions and at least one valid applicable base;no typed,open,negative-only or ambiguous primary role paths'
OPEN_CROSS_ROLE_PROFILE='ORIGINAL_DTS_OPEN_EXPLICIT_V17'
OPEN_CROSS_ROLE_SCOPE='Original-DTS effective open and closed explicit base alternatives;consecutive primary and dimensional targetRole paths;reported extras require a supplied usable domain;each applicable role has a positive assignment;no typed,negative-only or source-fact inference'
USABLE_DOMAIN_PROFILE='ORIGINAL_DTS_EXPLICIT_DOMAIN_USABILITY_V18'
USABLE_DOMAIN_SCOPE=OPEN_CROSS_ROLE_SCOPE+';unusable members are excluded while descendant paths stay traversable;conflicting usability or unusable primary paths reject'
NEGATIVE_ONLY_CROSS_ROLE_PROFILE='ORIGINAL_DTS_NEGATIVE_ONLY_EXPLICIT_V19'
NEGATIVE_ONLY_CROSS_ROLE_SCOPE='Original-DTS effective explicit alternatives allowing negative-only conjunctions;reported members require a usable supplied domain;unsupported relationships or malformed contexts reject before negation'
TYPED_EFFECTIVE_PROFILE='ORIGINAL_DTS_TYPED_EFFECTIVE_HYPERCUBES_V20'
TYPED_EFFECTIVE_SCOPE='Original-DTS effective explicit and typed open/closed alternatives with bounded primary inheritance, consecutive role traversal and source scalar validation;no typed value equality or dimensional fact promotion'
MULTIPLE_CONTEXT_PROFILE='ORIGINAL_DTS_SEPARATE_CONTEXT_HYPERCUBES_V21'
MULTIPLE_CONTEXT_SCOPE='Original-DTS effective typed and explicit hypercubes evaluate each assigned segment or scenario separately;cross-placement default interpretation and typed equality remain unsupported'
MAX_OUTPUT=8*1024*1024;MAX_ASSIGNMENTS=64;MAX_FACT_ASSIGNMENTS=16
MAX_DOMAIN_STATES=32768;MAX_PRIMARY_STATES=32768


def _records(parsed,concepts,arcs,*,alternative=False,cross_primary=False,open_cubes=False,allow_unusable=False,allow_negative_only=False,typed_members=None,separate_context_elements=False):
 """Evaluate the supported conjunction without changing any reported source fact."""
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise XBRLError('drs_mixed_cross_arc_budget')
 by={};seen=set();defaults={};parents={}
 admitted_typed_axes=set() if typed_members is None else {axis for context in typed_members.values() for axis in context}
 groups={'all':(tag(X,'item'),tag(D,'hypercubeItem')),'notAll':(tag(X,'item'),tag(D,'hypercubeItem')),'hypercube-dimension':(tag(D,'hypercubeItem'),tag(D,'dimensionItem')),'dimension-domain':(tag(D,'dimensionItem'),tag(X,'item')),'domain-member':(tag(X,'item'),tag(X,'item')),'dimension-default':(tag(D,'dimensionItem'),tag(X,'item'))}
 for a in arcs:
  if a['kind']not in groups:raise XBRLError('drs_mixed_cross_relationship_unsupported')
  key=(a['role'],a['kind'],a['from'],a['to'])
  if key in seen:raise XBRLError('drs_mixed_cross_duplicate_relationship_unsupported')
  seen.add(key);by.setdefault((a['role'],a['kind'],a['from']),[]).append(a)
  for name,group in zip((a['from'],a['to']),groups[a['kind']]):
   accepts_typed=typed_members is not None and a['kind']=='hypercube-dimension' and group==tag(D,'dimensionItem')
   decl=_declaration(concepts,name,group,typed_axis=accepts_typed)
   if accepts_typed and decl.get('typed_domain_ref') is not None and name not in admitted_typed_axes:
    raise XBRLError('drs_typed_effective_axis_source_not_corroborated')
  if a['kind']=='dimension-default':
   prior=defaults.get(a['from'])
   if prior is not None and prior!=a['to']:raise XBRLError('drs_mixed_cross_global_default_conflict')
   defaults[a['from']]=a['to']
  elif a['kind']=='domain-member':parents.setdefault(a['to'],[]).append(a)
 assignments=[a for a in arcs if a['kind']in('all','notAll')]
 if len(defaults)>32:raise XBRLError('drs_mixed_cross_global_default_budget')
 if not 1<=len(assignments)<=MAX_ASSIGNMENTS or not open_cubes and any(a['closed']is not True for a in assignments):raise XBRLError('drs_mixed_cross_closed_assignment_budget')
 roles={a['role']for a in assignments}
 if not alternative and len(roles)!=1:raise XBRLError('drs_mixed_cross_alternative_base_roles_unsupported')
 if alternative and not (1 if cross_primary else 2)<=len(roles)<=8:raise XBRLError('drs_alternative_role_budget')
 next_role=lambda a:a['target_role']or a['role'];domain_cache={};shape_cache={};ancestor_cache={};domain_states=0;primary_states=0
 def domain(axis,source_role,*,require_default_in_domain=True):
  key=(axis,source_role)
  def checked(result):
   members,default,_=result
   if require_default_in_domain and default is not None and default not in members:
    raise XBRLError('drs_mixed_cross_default_outside_selected_domain')
   return result
  if key in domain_cache:return checked(domain_cache[key])
  roots=by.get((source_role,'dimension-domain',axis),[])
  if cross_primary:
   if not 1<=len(roots)<=16:raise XBRLError('drs_primary_dimension_domain_root_budget')
  elif len(roots)!=1:raise XBRLError('drs_mixed_cross_single_domain_required')
  members=set();completed=set();count=0;usability={}
  def visit(current,member,path,depth,usable):
   nonlocal count,domain_states
   if member in path:raise XBRLError('drs_mixed_cross_domain_cycle')
   if depth>=32:raise XBRLError('drs_mixed_cross_domain_depth')
   state=(current,member)
   prior=usability.setdefault(member,usable)
   if prior!=usable:raise XBRLError('drs_domain_member_usability_ambiguous')
   if state in completed:return
   count+=1;domain_states+=1
   if domain_states>MAX_DOMAIN_STATES:raise XBRLError('drs_mixed_cross_total_domain_state_budget')
   if count>2048:raise XBRLError('drs_mixed_cross_member_budget')
   members.add(member)
   for child in by.get((current,'domain-member',member),[]):
    visit(next_role(child),child['to'],path|{member},depth+1,child.get('usable',True))
   completed.add(state)
  for root in roots:visit(next_role(root),root['to'],set(),0,root.get('usable',True))
  default=defaults.get(axis)
  usable_members={member for member in members if usability[member]}
  domain_cache[key]=(usable_members,default,members);return checked(domain_cache[key])
 def shape(a):
  key=(a['from'],a['to'],next_role(a))
  if key in shape_cache:return shape_cache[key]
  axes=by.get((next_role(a),'hypercube-dimension',a['to']),[])
  if not 1<=len(axes)<=32 or len({v['to']for v in axes})!=len(axes):raise XBRLError('drs_mixed_cross_dimension_budget_or_missing')
  result={}
  for axis in axes:
   name=axis['to']
   result[name]=None if typed_members is not None and concepts[name]['declaration'].get('typed_domain_ref') is not None else domain(name,next_role(axis))
  if any(a['from']in value[2] for value in result.values() if value is not None):raise XBRLError('drs_mixed_cross_primary_item_polymorphism')
  shape_cache[key]=result;return result
 # Every supplied assignment's supported cube shape must be well formed, even
 # when a particular selected fact does not inherit that assignment.
 for a in assignments:shape(a)
 def ancestors(concept,role):
  nonlocal primary_states
  key=(concept,role)
  if key in ancestor_cache:return ancestor_cache[key]
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
    if alternative and a['role']!=role and next_role(a)!=role:continue
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
  ancestor_cache[key]=found;return found
 def primary_closure(assignment):
  nonlocal primary_states
  root=assignment['from'];root_role=assignment['role']
  reached={};edges={};incoming={};pending=deque([(root,root_role)])
  while pending:
   concept,role=pending.popleft()
   if concept in reached:
    if reached[concept]!=role:raise XBRLError('drs_primary_ambiguous_target_roles')
    continue
   reached[concept]=role;primary_states+=1
   if len(reached)>2048 or primary_states>MAX_PRIMARY_STATES:
    raise XBRLError('drs_mixed_cross_total_primary_state_budget')
   outgoing=by.get((role,'domain-member',concept),[])
   edges[concept]=set()
   for relation in outgoing:
    if relation.get('usable')is False:raise XBRLError('drs_unusable_primary_inheritance_unsupported')
    child=relation['to']
    edges[concept].add(child)
    incoming.setdefault(child,set()).add(concept)
    pending.append((child,next_role(relation)))
  degree={concept:len(incoming.get(concept,())) for concept in reached}
  depth={concept:0 for concept in reached}
  queue=deque(concept for concept,count in degree.items()if not count)
  seen=0
  while queue:
   concept=queue.popleft();seen+=1
   if depth[concept]>=32:raise XBRLError('drs_mixed_cross_primary_depth')
   for child in edges[concept]:
    degree[child]-=1
    depth[child]=max(depth[child],depth[concept]+1)
    if not degree[child]:queue.append(child)
  if seen!=len(reached):raise XBRLError('drs_mixed_cross_primary_cycle')
  return reached,incoming

 closures={}
 if cross_primary:
  for assignment in assignments:
   key=(assignment['role'],assignment['from'])
   if key not in closures:closures[key]=primary_closure(assignment)
 def inherited_in_role(concept,role):
  nonlocal primary_states
  key=(concept,role)
  if key in ancestor_cache:return ancestor_cache[key]
  found={concept}
  for (source_role,_),(reached,incoming) in closures.items():
   if source_role!=role or concept not in reached:continue
   visited=set();pending=deque([concept])
   while pending:
    current=pending.popleft()
    if current in visited:continue
    visited.add(current);found.add(current);primary_states+=1
    if primary_states>MAX_PRIMARY_STATES:raise XBRLError('drs_mixed_cross_total_primary_state_budget')
    pending.extend(incoming.get(current,()))
  ancestor_cache[key]=found
  return found

 extra_roles={}
 if open_cubes:
  for arc in arcs:
   if arc['kind']=='dimension-domain':extra_roles.setdefault(arc['from'],set()).add(arc['role'])
 def has_member(axis,member):
  return any(member in domain(axis,role,require_default_in_domain=False)[0]
             for role in sorted(extra_roles.get(axis,())))
 def evaluate(fact,role,selected,inherited,reported,typed,positions):
  aggregate={axis:member for axis,member in sorted(defaults.items())if axis not in reported}
  details=[];given=set(reported)|set(typed);all_axes=set(defaults)|given;invalid=[]
  if len(all_axes)>32:raise XBRLError('drs_mixed_cross_combined_dimension_budget')
  for a in selected:
   domains=shape(a);all_axes.update(domains)
   if len(all_axes)>32:raise XBRLError('drs_mixed_cross_combined_dimension_budget')
   placement=a['context_element']
   placed={axis for axis in given if positions[axis]==placement}
   extras=sorted(placed-set(domains))
   if any(fact['concept']in value[2] for value in domains.values() if value is not None):raise XBRLError('drs_mixed_cross_primary_item_polymorphism')
   if open_cubes and not a['closed']:
    for axis in extras:
     if axis not in typed and not has_member(axis,reported[axis]):
      raise XBRLError('drs_open_extra_dimension_without_supplied_domain')
   used={};failure='drs_mixed_cross_closed_extra_dimension'if extras and a['closed']else None
   for axis,domain_values in sorted(domains.items()):
    if domain_values is None:
     if (axis not in typed or axis not in placed) and failure is None:failure='drs_mixed_cross_required_typed_dimension_missing'
     continue
    members,default,_=domain_values
    if separate_context_elements and default is not None and axis in given and axis not in placed:
     raise XBRLError('drs_cross_context_default_unsupported')
    if axis in reported and axis in placed:
     if reported[axis]not in members and failure is None:failure='drs_mixed_cross_member_outside_domain'
    elif default is not None:used[axis]=default
    elif failure is None:failure='drs_mixed_cross_required_dimension_missing'
   negative=a['kind']=='notAll'
   if negative:
    if failure is None:invalid.append('drs_mixed_cross_negative_hypercube_satisfied')
    used={}
   elif failure is not None:
    invalid.append(failure)
    if alternative:used={}
   if invalid and not alternative:raise XBRLError(invalid[0])
   for axis,value in used.items():
    if axis in aggregate and aggregate[axis]!=value:raise XBRLError('drs_mixed_cross_default_conflict')
    aggregate[axis]=value
   details.append({'primary_item':a['from'],'hypercube':a['to'],'kind':a['kind'],'context_element':placement,'closed':a['closed'],'used_defaults':used,'extra_dimensions':extras,'hypercube_valid':failure is None,'failure_reason':failure,'inherited':a['from']!=fact['concept'],'source_uri':a['source_uri'],'source_arc_node_ordinal':a['arc_node_ordinal']})
  evidence={'role':role,'primary_ancestors':sorted(inherited),'assignments':details}
  return evidence,dict(sorted(aggregate.items())),invalid

 records=[];size=0
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  candidates=[];placements=set()
  for role in sorted(roles):
   concept=fact['concept']
   inherited=inherited_in_role(concept,role) if cross_primary else ancestors(concept,role)
   eligible=lambda a:concept in closures[role,a['from']][0] if cross_primary else a['from'] in inherited
   selected=sorted((a for a in assignments if a['role']==role and eligible(a)),key=lambda a:(a['kind']!='all',a['from'],a['to']))
   if not selected and alternative:continue
   if not 1<=len(selected)<=MAX_FACT_ASSIGNMENTS:raise XBRLError('drs_mixed_cross_fact_assignment_budget_or_missing')
   if not allow_negative_only and not any(a['kind']=='all'for a in selected):raise XBRLError('drs_mixed_cross_positive_assignment_required')
   placements.update(a['context_element']for a in selected)
   candidates.append((role,selected,inherited))
  if not candidates:raise XBRLError('drs_alternative_no_applicable_base')
  if not separate_context_elements and len(placements)!=1:raise XBRLError('drs_mixed_cross_mixed_context_assignments_unsupported')
  placement=next(iter(placements)) if len(placements)==1 else 'multiple'
  context=parsed['contexts'][fact['context_ref']]
  if type(context)is not dict or type(context.get('dimensions'))is not list or type(context.get('opaque_segment'))is not list:raise XBRLError('drs_mixed_cross_context_unsupported')
  dims=context['dimensions']
  if len(dims)>32 or context['opaque_segment'] or context['semantic_sha256']!=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')}):
   raise XBRLError('drs_mixed_cross_context_unsupported')
  reported={};typed={};positions={};scalar_receipts={} if typed_members is None else typed_members.get(fact['context_ref'],{})
  for dim in dims:
   if type(dim)is not dict or set(dim)!={'dimension','member','context_element','kind'}or (dim['context_element'] not in ('segment','scenario') if separate_context_elements else dim['context_element']!=placement) or type(dim['dimension'])is not str or not QN.fullmatch(dim['dimension']):
    raise XBRLError('drs_mixed_cross_context_unsupported')
   axis=dim['dimension'];positions[axis]=dim['context_element']
   if axis in reported or axis in typed:raise XBRLError('drs_mixed_cross_duplicate_dimension')
   if dim['kind']=='explicit' and type(dim['member'])is str and QN.fullmatch(dim['member']):
    reported[axis]=dim['member']
   elif dim['kind']=='typed' and axis in scalar_receipts and scalar_receipts[axis]['member_tree_sha256']==digest(dim['member']):
    typed[axis]=scalar_receipts[axis]
   else:raise XBRLError('drs_mixed_cross_context_unsupported')
  if typed.keys()!=scalar_receipts.keys():raise XBRLError('drs_mixed_cross_typed_context_receipt')
  for axis,member in reported.items():
   _declaration(concepts,axis,tag(D,'dimensionItem'));_declaration(concepts,member,tag(X,'item'))
   if defaults.get(axis)==member:raise XBRLError('drs_mixed_cross_explicit_default_member')
   if allow_negative_only and not has_member(axis,member):raise XBRLError('drs_negative_only_member_without_supplied_domain')
  record={'source_fact_id':fact['source_fact_id'],'context_element':placement,'global_defaults':dict(sorted(defaults.items()))}
  if typed_members is not None:record['typed_members']=[typed[key]for key in sorted(typed)]
  if separate_context_elements:record['reported_placements']=dict(sorted(positions.items()))
  if alternative:
   alternatives=[];used=None
   for role,selected,inherited in candidates:
    evidence,aggregate,invalid=evaluate(fact,role,selected,inherited,reported,typed,positions)
    if not invalid:
     if used is not None and used!=aggregate:raise XBRLError('drs_alternative_conflicting_effective_defaults')
     used=aggregate
    alternatives.append({**evidence,'valid':not invalid,'failure_reasons':invalid})
   if used is None:raise XBRLError('drs_alternative_no_valid_base')
   record.update(status='VALIDATED_RESTRICTED_ALTERNATIVE_CROSS_ROLE_CONTEXT',used_defaults=used,alternatives=alternatives)
  else:
   role,selected,inherited=candidates[0]
   evidence,aggregate,_=evaluate(fact,role,selected,inherited,reported,typed,positions)
   record.update(evidence,status='VALIDATED_RESTRICTED_MIXED_CROSS_ROLE_CONTEXT',used_defaults=aggregate)
  size+=len(canonical(record))
  if size>MAX_OUTPUT:raise XBRLError('drs_mixed_cross_output_budget')
  records.append(record)
 return records


def _typed_member_index(parsed,proof):
 from .xbrl_typed_bounds import _validate_scalar_receipts,_diagnostics
 from .xbrl_typed_dimensions import TEMPORAL_PROFILE as SCALARS
 retained,concepts,types,kinds,domains,_=_validate_scalar_receipts(parsed,proof)
 graph={'concepts':concepts,'type_declarations':types,'unsupported_semantics':retained['unsupported_semantics']}
 checked=_diagnostics(parsed,graph,kinds,domains,SCALARS)
 return {row['context_id']:{m['dimension']:m for m in row['typed_members']} for row in checked['contexts']}


def corroborate_mixed_cross_role(parsed,dts,documents,allow_observed,instance_uri,*,alternative=False,cross_primary=False,open_cubes=False,allow_unusable=False,allow_negative_only=False,typed=False,separate_context_elements=False):
 supplied=_originals(parsed,dts,documents,allow_observed,instance_uri)
 schema_sources=_schema_sources(supplied,dts['documents']);schemas=_validate_schema_sources(schema_sources,dts['documents'])
 arcs,refs=_read(parsed,dts,supplied,effective=True,negative=True,allow_unusable=allow_unusable);_endpoint_sources(arcs,dts['concepts'],schemas);effective,resolution=_effective(arcs,negative=True,allow_unusable=allow_unusable)
 scalar_proof={}
 member_index=None
 if typed:
  from .xbrl_typed_dimensions import check_typed_contexts,TEMPORAL_PROFILE as SCALARS
  from .xbrl_typed_bounds import _schema_receipts
  diagnostics=check_typed_contexts(parsed,dts,documents,profile=SCALARS,allow_observed=allow_observed)
  _,types,domains=_schema_receipts(supplied,dts,diagnostics)
  scalar_proof={'type_sources':types,'domain_sources':domains}
  if not domains and not separate_context_elements:raise XBRLError('drs_typed_effective_members_required')
  member_index=_typed_member_index(parsed,{'schema_sources':schema_sources,**scalar_proof})
 records=_records(parsed,dts['concepts'],effective,alternative=alternative,cross_primary=cross_primary,open_cubes=open_cubes,allow_unusable=allow_unusable,allow_negative_only=allow_negative_only,typed_members=member_index,separate_context_elements=separate_context_elements)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256')
 form='inline_set' if parsed['schema']=='gig.sec.xbrl.inline_set.v1' else 'instance'
 if separate_context_elements:version,profile,scope=21,MULTIPLE_CONTEXT_PROFILE,MULTIPLE_CONTEXT_SCOPE
 elif typed:version,profile,scope=20,TYPED_EFFECTIVE_PROFILE,TYPED_EFFECTIVE_SCOPE
 elif allow_negative_only:version,profile,scope=19,NEGATIVE_ONLY_CROSS_ROLE_PROFILE,NEGATIVE_ONLY_CROSS_ROLE_SCOPE
 elif allow_unusable:version,profile,scope=18,USABLE_DOMAIN_PROFILE,USABLE_DOMAIN_SCOPE
 elif open_cubes:version,profile,scope=17,OPEN_CROSS_ROLE_PROFILE,OPEN_CROSS_ROLE_SCOPE
 elif cross_primary:version,profile,scope=16,PRIMARY_TARGET_ROLE_PROFILE,PRIMARY_TARGET_ROLE_SCOPE
 elif alternative:version,profile,scope=13,ALTERNATIVE_PROFILE,ALTERNATIVE_SCOPE
 else:version,profile,scope=10,PROFILE,SCOPE
 result['schema']=f'gig.sec.xbrl.dimensional_{form}.v{version}'
 result['dts_corroboration']['dimensional_validation']={'profile':profile,'facts':records,'relationships':arcs,'role_references':refs,'schema_sources':schema_sources,'effective_relationships':effective,'resolution':resolution,'complete_drs_validation':False,'scope':scope,**scalar_proof}
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('drs_mixed_cross_output_budget')
 result['canonical_sha256']=digest(result);return result


def validate_mixed_cross_role_result(parsed,*,alternative=False,cross_primary=False,open_cubes=False,allow_unusable=False,allow_negative_only=False,typed=False,separate_context_elements=False):
 fail=lambda:XBRLError('xbrl_dimensional_result_contract')
 try:
  p=parsed['dts_corroboration']['dimensional_validation']
  if separate_context_elements:profile,scope=MULTIPLE_CONTEXT_PROFILE,MULTIPLE_CONTEXT_SCOPE
  elif typed:profile,scope=TYPED_EFFECTIVE_PROFILE,TYPED_EFFECTIVE_SCOPE
  elif allow_negative_only:profile,scope=NEGATIVE_ONLY_CROSS_ROLE_PROFILE,NEGATIVE_ONLY_CROSS_ROLE_SCOPE
  elif allow_unusable:profile,scope=USABLE_DOMAIN_PROFILE,USABLE_DOMAIN_SCOPE
  elif open_cubes:profile,scope=OPEN_CROSS_ROLE_PROFILE,OPEN_CROSS_ROLE_SCOPE
  elif cross_primary:profile,scope=PRIMARY_TARGET_ROLE_PROFILE,PRIMARY_TARGET_ROLE_SCOPE
  elif alternative:profile,scope=ALTERNATIVE_PROFILE,ALTERNATIVE_SCOPE
  else:profile,scope=PROFILE,SCOPE
  fields={'profile','facts','relationships','role_references','schema_sources','effective_relationships','resolution','complete_drs_validation','scope'}
  if typed:fields.update(('domain_sources','type_sources'))
  if type(p)is not dict or set(p)!=fields or p['profile']!=profile or p['scope']!=scope or p['complete_drs_validation']is not False or len(canonical(parsed))>MAX_OUTPUT:raise fail()
  effective,resolution=_effective(p['relationships'],negative=True,allow_unusable=allow_unusable)
  receipts={'relationships':[_project(a)for a in p['relationships']],'role_references':p['role_references']}
  concepts,_=_validate_receipts(parsed,receipts,negative=True)
  schemas=_validate_schema_sources(p['schema_sources'],parsed['dts_corroboration']['documents']);_endpoint_sources(p['relationships'],concepts,schemas)
  if p['relationships']!=sorted(p['relationships'],key=lambda a:(a['source_uri'],a['arc_node_ordinal'])):raise fail()
  member_index=_typed_member_index(parsed,p) if typed else None
  if typed and not separate_context_elements and not p['domain_sources']:raise fail()
  if canonical(effective)!=canonical(p['effective_relationships'])or canonical(resolution)!=canonical(p['resolution'])or canonical(_records(parsed,concepts,effective,alternative=alternative,cross_primary=cross_primary,open_cubes=open_cubes,allow_unusable=allow_unusable,allow_negative_only=allow_negative_only,typed_members=member_index,separate_context_elements=separate_context_elements))!=canonical(p['facts']):raise fail()
 except (XBRLError,KeyError,TypeError,ValueError,OverflowError):raise fail()from None
