"""Explicit single-role direct-hypercube corroboration,not complete DRS validity."""
import copy
import re
from collections import deque
from urllib.parse import urljoin
from .xbrl_instance import X,L,XL,tag,digest,canonical,XBRLError
D='http://xbrl.org/2005/xbrldt';ARC='http://xbrl.org/int/dim/arcrole/';PROFILE='EXPLICIT_CLOSED_HYPERCUBE_V1'
OPEN_PROFILE='DIRECT_EXPLICIT_HYPERCUBE_V2'
INHERITED_PROFILE='INHERITED_POSITIVE_EXPLICIT_HYPERCUBES_V3'
NEGATIVE_PROFILE='INHERITED_EXPLICIT_NEGATIVE_HYPERCUBES_V4'
NEGATIVE_ONLY_PROFILE='NEGATIVE_ONLY_EXPLICIT_HYPERCUBES_V5'
TYPED_PROFILE='DIRECT_CLOSED_TYPED_HYPERCUBE_V6'
PROFILES=(PROFILE,OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE,TYPED_PROFILE)
ROLES={'all','notAll','hypercube-dimension','dimension-domain','domain-member','dimension-default'}

def networks(linkbases,locators,*,node_provenance=False):
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
    if node_provenance:arcs[-1]['source_link_ordinal']=link.source_ordinal;arcs[-1]['source_arc_ordinal']=node.source_ordinal
    if len(arcs)>4096:raise XBRLError('drs_arc_budget')
   result.append({'role':link.attrs[tag(XL,'role')],'source_uri':source,'arcs':arcs,'issues':sorted(issues),'usable_for_restricted_profile':not issues})
 if len(result)!=1:
  for network in result:network['usable_for_restricted_profile']=False;network['issues'].append('MULTIPLE_DEFINITION_LINKS_UNSUPPORTED')
 return result

def corroborate(parsed,dts,*,profile=PROFILE,documents=None,allow_observed=False,instance_uri=None):
 if profile not in PROFILES:raise XBRLError('drs_profile_unsupported')
 if profile==TYPED_PROFILE:return _corroborate_typed(parsed,dts,documents,allow_observed,instance_uri)
 if type(parsed)is not dict or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256')or type(dts)is not dict or digest({k:v for k,v in dts.items()if k!='canonical_sha256'})!=dts.get('canonical_sha256'):raise XBRLError('drs_input_identity')
 if parsed.get('dts_corroboration',{}).get('dts_sha256')!=dts['canonical_sha256']:raise XBRLError('drs_binding_required')
 schemas={'gig.sec.xbrl.instance.v1':'gig.sec.xbrl.dimensional_instance.v1','gig.sec.xbrl.inline_set.v1':'gig.sec.xbrl.dimensional_inline_set.v1'}
 if profile in(OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):schemas={key:value[:-1]+('5'if profile==NEGATIVE_ONLY_PROFILE else'4'if profile==NEGATIVE_PROFILE else'3'if profile==INHERITED_PROFILE else'2')for key,value in schemas.items()}
 if parsed.get('schema')not in schemas:raise XBRLError('drs_derived_schema_unsupported_or_already_applied')
 nets=dts.get('definition',[])
 if not dts['structural_closure']or len(nets)!=1 or not nets[0]['usable_for_restricted_profile']:raise XBRLError('drs_profile_unsupported')
 arcs=nets[0]['arcs'];concepts=dts['concepts'];adj={};domains={}
 if profile not in(NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE)and any(a['kind']=='notAll'for a in arcs):raise XBRLError('drs_not_all_unsupported')
 positive=[a for a in arcs if a['kind']=='all'or profile in(NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE)and a['kind']=='notAll']
 if profile not in(INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE)and len(positive)!=1:raise XBRLError('drs_single_positive_assignment_required')
 if profile in(INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):
  if not 1<=len(positive)<=64:raise XBRLError('drs_positive_assignment_budget')
  keys=[(a['from'],a['to'],a['kind'])for a in positive]
  if len(keys)!=len(set(keys)):raise XBRLError('drs_duplicate_positive_assignment')
  positive=sorted(positive,key=lambda a:(a['from'],a['to'],a['context_element'],a['closed']))
  if profile in(NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):positive=sorted(positive,key=lambda a:(a['kind']!='all',a['from'],a['to'],a['context_element'],a['closed']))
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
 global_defaults={}
 if profile==NEGATIVE_ONLY_PROFILE:
  for arc in arcs:
   if arc['kind']!='dimension-default':continue
   axis,member=arc['from'],arc['to']
   if axis in global_defaults:raise XBRLError('drs_ambiguous_global_default')
   global_defaults[axis]=member
   if len(global_defaults)>32:raise XBRLError('drs_global_default_budget')
  global_defaults=dict(sorted(global_defaults.items()))
  for axis,member in global_defaults.items():
   members,defaults=domain(axis)
   if member not in members or defaults!=[member]:raise XBRLError('drs_default_conflict_or_domain')
 def negative_only_context(fact,placement):
  context=parsed['contexts'][fact['context_ref']]
  if context['opaque_segment']or any(d['kind']!='explicit'or d['context_element']!=placement for d in context['dimensions']):raise XBRLError('drs_context_profile_unsupported')
  reported={d['dimension']:d['member']for d in context['dimensions']}
  if len(set(reported)|set(global_defaults))>32:raise XBRLError('drs_dimension_budget_or_missing')
  for axis,member in reported.items():
   members,defaults=domain(axis)
   if member not in members:raise XBRLError('drs_member_outside_domain')
   if defaults and member==defaults[0]:raise XBRLError('drs_explicit_default_member')
  return {axis:member for axis,member in global_defaults.items()if axis not in reported}
 parents={};ancestor_cache={}
 if profile in(INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):
  for arc in arcs:
   if arc['kind']=='domain-member':parents.setdefault(arc['to'],set()).add(arc['from'])
 def ancestors(concept):
  if concept in ancestor_cache:return ancestor_cache[concept]
  found=set();pending=deque([concept])
  while pending:
   node=pending.popleft()
   if node in found:continue
   declaration(node,tag(X,'item'));found.add(node)
   if len(found)>2048:raise XBRLError('drs_primary_item_budget')
   pending.extend(sorted(parents.get(node,())))
  # Directed cycles are invalid, but converging inheritance paths are legal.
  degree={node:0 for node in found};children={node:set()for node in found};depth={node:0 for node in found}
  for child in found:
   for parent in parents.get(child,()):
    degree[child]+=1;children[parent].add(child)
  pending=deque(sorted(node for node in found if degree[node]==0));visited=0
  while pending:
   parent=pending.popleft();visited+=1
   if depth[parent]>=32:raise XBRLError('drs_primary_item_depth')
   for child in sorted(children[parent]):
    degree[child]-=1;depth[child]=max(depth[child],depth[parent]+1)
    if degree[child]==0:pending.append(child)
  if visited!=len(found):raise XBRLError('drs_primary_item_cycle')
  ancestor_cache[concept]=found;return found
 def negative_shape(fact,assignment):
  cube=assignment['to'];declaration(fact['concept'],tag(X,'item'));declaration(assignment['from'],tag(X,'item'));declaration(cube,tag(D,'hypercubeItem'))
  axes=targets('hypercube-dimension',cube)
  if not axes or len(axes)>32:raise XBRLError('drs_dimension_budget_or_missing')
  for axis in axes:
   members,_=domain(axis)
   if assignment['from']in members:raise XBRLError('drs_primary_item_polymorphism')
  context=parsed['contexts'][fact['context_ref']]
  if context['opaque_segment']or any(d['kind']!='explicit'or d['context_element']!=assignment['context_element']for d in context['dimensions']):raise XBRLError('drs_context_profile_unsupported')
  given={d['dimension']for d in context['dimensions']};extras=given-set(axes)
  if len(set(axes)|extras)>32:raise XBRLError('drs_dimension_budget_or_missing')
  return cube,extras,set(axes)|extras
 def validate_assignment(fact,assignment):
  cube=assignment['to'];declaration(fact['concept'],tag(X,'item'));declaration(assignment['from'],tag(X,'item'));declaration(cube,tag(D,'hypercubeItem'))
  axes=targets('hypercube-dimension',cube)
  if not axes or len(axes)>32:raise XBRLError('drs_dimension_budget_or_missing')
  context=parsed['contexts'][fact['context_ref']]
  if context['opaque_segment']or any(d['kind']!='explicit'or d['context_element']!=assignment['context_element']for d in context['dimensions']):raise XBRLError('drs_context_profile_unsupported')
  given={d['dimension']:d['member']for d in context['dimensions']}
  extras=set(given)-set(axes)
  if extras and assignment['closed']:raise XBRLError('drs_closed_extra_dimension')
  check_axes=sorted(set(axes)|extras)if profile in(OPEN_PROFILE,INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE)else axes
  if len(check_axes)>32:raise XBRLError('drs_dimension_budget_or_missing')
  defaults={}
  for axis in check_axes:
   members,default=domain(axis)
   if profile in(INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE)and assignment['from']in members:raise XBRLError('drs_primary_item_polymorphism')
   if axis in given:
    if given[axis]not in members:raise XBRLError('drs_member_outside_domain')
    if default and given[axis]==default[0]:raise XBRLError('drs_explicit_default_member')
   elif default:defaults[axis]=default[0]
   else:raise XBRLError('drs_required_dimension_missing')
  return cube,defaults,extras,set(check_axes)
 records=[];size=len(canonical(parsed))
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  if profile in(INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):
   sources=ancestors(fact['concept']);assignments=[a for a in positive if a['from']in sources]
   if not assignments or profile==NEGATIVE_PROFILE and not any(a['kind']=='all'for a in assignments):raise XBRLError('drs_positive_assignment_required')
   if profile==NEGATIVE_ONLY_PROFILE and any(a['kind']!='notAll'for a in assignments):raise XBRLError('drs_negative_only_assignments_required')
   if len(assignments)>16:raise XBRLError('drs_fact_assignment_budget')
   if len({a['context_element']for a in assignments})!=1:raise XBRLError('drs_mixed_context_assignments_unsupported')
   details=[];aggregate=negative_only_context(fact,assignments[0]['context_element'])if profile==NEGATIVE_ONLY_PROFILE else{};all_axes=set(global_defaults)if profile==NEGATIVE_ONLY_PROFILE else set()
   for assignment in assignments:
    failure=None
    if profile in(NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE)and assignment['kind']=='notAll':
     cube,extras,axes=negative_shape(fact,assignment)
     try:validate_assignment(fact,assignment)
     except XBRLError as exc:
      # Only evaluated context invalidity negates a well-formed supported cube.
      # Resource, declaration, schema/domain, default and unsupported errors reject.
      if str(exc)not in('drs_closed_extra_dimension','drs_member_outside_domain','drs_required_dimension_missing'):raise
      failure=str(exc)
     if failure is None:raise XBRLError('drs_negative_hypercube_satisfied')
     defaults={} # Negative evaluation never supplies defaults to the reported fact.
    else:cube,defaults,extras,axes=validate_assignment(fact,assignment)
    all_axes.update(axes)
    if len(all_axes)>32:raise XBRLError('drs_dimension_budget_or_missing')
    for axis,member in defaults.items():
     if axis in aggregate and aggregate[axis]!=member:raise XBRLError('drs_default_conflict_or_domain')
     aggregate[axis]=member
    detail={'primary_item':assignment['from'],'hypercube':cube,'context_element':assignment['context_element'],'closed':assignment['closed'],'used_defaults':defaults,'extra_dimensions':sorted(extras),'inherited':assignment['from']!=fact['concept']}
    if profile in(NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):detail.update(kind=assignment['kind'],hypercube_valid=failure is None,failure_reason=failure)
    details.append(detail)
   record={'source_fact_id':fact['source_fact_id'],'role':nets[0]['role'],'context_element':assignments[0]['context_element'],'used_defaults':aggregate,'status':'VALIDATED_RESTRICTED_EXPLICIT_CONTEXT','assignments':details}
   if profile==NEGATIVE_ONLY_PROFILE:record['global_defaults']=global_defaults.copy()
  else:
   assignments=[a for a in arcs if a['kind']=='all'and a['from']==fact['concept']]
   if len(assignments)!=1 or profile==PROFILE and not assignments[0]['closed']:raise XBRLError('drs_direct_closed_assignment_required')
   assignment=assignments[0];cube,defaults,extras,_=validate_assignment(fact,assignment)
   record={'source_fact_id':fact['source_fact_id'],'role':nets[0]['role'],'hypercube':cube,'context_element':assignment['context_element'],'used_defaults':defaults,'status':'VALIDATED_RESTRICTED_EXPLICIT_CONTEXT'}
   if profile==OPEN_PROFILE:record.update(closed=assignment['closed'],extra_dimensions=sorted(extras))
  size+=len(canonical(record))+1
  if size>8*1024*1024:raise XBRLError('drs_output_budget')
  records.append(record)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256');result['schema']=schemas[parsed['schema']];result['dts_corroboration']['dimensional_validation']={'profile':profile,'facts':records,'complete_drs_validation':False,'scope':'Single direct positive closed hypercube,one role,explicit dimensions and supplied domains/defaults only;no context/fact synthesis'}
 if profile==OPEN_PROFILE:result['dts_corroboration']['dimensional_validation']['scope']='Single direct positive open/closed hypercube,one role,supplied usable explicit dimensions/domains/defaults;open additional dimensions independently validated;no context/fact synthesis'
 if profile in(INHERITED_PROFILE,NEGATIVE_PROFILE,NEGATIVE_ONLY_PROFILE):result['dts_corroboration']['dimensional_validation']['scope']='One role,positive direct/transitively inherited explicit hypercubes with conjunctive validity;supplied usable domains/defaults only;no negative/typed/cross-role semantics or context/fact synthesis'
 if profile==NEGATIVE_PROFILE:result['dts_corroboration']['dimensional_validation']['scope']='One role,inherited explicit positive/negative hypercube conjunction;negative cubes prevalidated before contextual exclusion;positive defaults only;no negative-only,typed/cross-role semantics or context/fact synthesis'
 if profile==NEGATIVE_ONLY_PROFILE:result['dts_corroboration']['dimensional_validation']['scope']='One role,inherited negative-only explicit hypercubes with conjunctive exclusion;global reported-context/default validation before cube negation;no typed/cross-role semantics or reported context/fact synthesis'
 if len(canonical(result))>8*1024*1024:raise XBRLError('drs_output_budget')
 result['canonical_sha256']=digest(result);return result

def _typed_original_graph(parsed,dts,documents,instance_uri):
 """Reconstruct raw DTS closure against retained real references,never fake XML."""
 from .xbrl_dts import _supplied_documents,_discover_roots,uri
 from .xbrl_binding import bind_declarations
 supplied=_supplied_documents(documents)
 if len(supplied)!=len(documents):raise XBRLError('drs_typed_duplicate_source_uri')
 bind_declarations(parsed,dts) # Recheck plain/set source scope and selected declarations.
 if parsed['schema']=='gig.sec.xbrl.instance.v1':
  uri(instance_uri)
  if parsed['source']['source_url']is not None and parsed['source']['source_url']!=instance_uri:raise XBRLError('drs_typed_instance_uri_scope')
  roots=[uri(urljoin(instance_uri,r['href']))for r in parsed['schema_references']]
  metadata={'schema':'gig.sec.xbrl.dts.v1','origin':parsed['origin'],'instance_sha256':parsed['source']['source_sha256'],'permission_reference_sha256':parsed['source']['permission_reference_sha256']}
 else:
  ds=parsed['document_set'];sources=ds['documents']
  if ds['sha256']!=digest(sources)or parsed['source']['source_sha256']!=ds['sha256']:raise XBRLError('drs_typed_document_set_identity')
  roots=[uri(r['uri'])for r in ds['schema_references']]
  metadata={'schema':'gig.sec.xbrl.dts_set.v1','origin':parsed['origin'],'document_set_sha256':ds['sha256'],'original_inline_documents':[{'uri':s['uri'],'source_sha256':s['source']['source_sha256']}for s in sources],'permission_reference_sha256s':[s['source']['permission_reference_sha256']for s in sources]}
 if not 1<=len(roots)<=32:raise XBRLError('drs_typed_schema_roots')
 rebuilt=_discover_roots(roots,supplied,metadata,embedded_profile=dts.get('embedded_linkbase_profile'))
 if {d['uri']for d in rebuilt['documents']}!=set(supplied):raise XBRLError('drs_typed_original_document_coverage')
 # Canonical equality distinguishes false/0 and compares all source diagnostics.
 if canonical(rebuilt)!=canonical(dts):raise XBRLError('drs_typed_reconstructed_graph_mismatch')
 return supplied

def _corroborate_typed(parsed,dts,documents,allow_observed,instance_uri):
 from .xbrl_typed_dimensions import check_typed_contexts
 # Approval and permission binding precede every raw XML parse in either helper.
 diagnostics=check_typed_contexts(parsed,dts,documents,allow_observed=allow_observed)
 supplied=_typed_original_graph(parsed,dts,documents,instance_uri)
 if diagnostics['unsupported_member_count']:raise XBRLError('drs_typed_scalar_semantics_unsupported')
 nets=dts.get('definition',[])
 if len(nets)!=1 or not nets[0]['usable_for_restricted_profile']or any(u['feature']=='EMBEDDED_LINKBASE_UNSUPPORTED'for u in dts['unsupported_semantics']):raise XBRLError('drs_profile_unsupported')
 arcs=nets[0]['arcs'];concepts=dts['concepts'];adj={};domains={}
 if any(a['kind']=='notAll'for a in arcs):raise XBRLError('drs_not_all_unsupported')
 assignments=[a for a in arcs if a['kind']=='all']
 if len(assignments)!=1 or not assignments[0]['closed']:raise XBRLError('drs_direct_closed_assignment_required')
 assignment=assignments[0];cube=assignment['to']
 for arc in arcs:adj.setdefault((arc['kind'],arc['from']),set()).add(arc['to'])
 def targets(kind,name):return sorted(adj.get((kind,name),()))
 def declaration(name,group,*,typed=False):
  value=concepts.get(name,{}).get('declaration',{})
  if value.get('substitution_group')!=group or not typed and value.get('typed_domain_ref')is not None:raise XBRLError('drs_declaration_unsupported')
  if group in(tag(D,'hypercubeItem'),tag(D,'dimensionItem'))and value.get('abstract')is not True:raise XBRLError('drs_abstract_declaration_required')
  return value
 declaration(assignment['from'],tag(X,'item'));declaration(cube,tag(D,'hypercubeItem'))
 axes=targets('hypercube-dimension',cube)
 if not 1<=len(axes)<=32:raise XBRLError('drs_dimension_budget_or_missing')
 typed_axes={axis for axis in axes if declaration(axis,tag(D,'dimensionItem'),typed=True).get('typed_domain_ref')is not None}
 if not typed_axes:raise XBRLError('drs_typed_axis_required')
 for axis in typed_axes:
  if targets('dimension-domain',axis)or targets('dimension-default',axis):raise XBRLError('drs_typed_explicit_relationship')
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
  degree={m:0 for m in members};depth={m:0 for m in members}
  for m in members:
   for child in targets('domain-member',m):degree[child]+=1
  pending=deque(m for m in members if degree[m]==0);visited=0
  while pending:
   m=pending.popleft();visited+=1
   if depth[m]>=32:raise XBRLError('drs_domain_depth')
   for child in targets('domain-member',m):
    degree[child]-=1;depth[child]=max(depth[child],depth[m]+1)
    if degree[child]==0:pending.append(child)
  if visited!=len(members):raise XBRLError('drs_domain_cycle')
  defaults=targets('dimension-default',axis)
  if len(defaults)>1 or defaults and defaults[0]not in members:raise XBRLError('drs_default_conflict_or_domain')
  if assignment['from']in members:raise XBRLError('drs_primary_item_polymorphism')
  domains[axis]=(members,defaults);return domains[axis]
 for axis in set(axes)-typed_axes:domain(axis)
 checked={row['context_id']:{m['dimension']:m for m in row['typed_members']}for row in diagnostics['contexts']};records=[];size=len(canonical(parsed))
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  if fact['concept']!=assignment['from']:raise XBRLError('drs_direct_closed_assignment_required')
  context=parsed['contexts'][fact['context_ref']];placement=assignment['context_element']
  if context['opaque_segment']or any(d['context_element']!=placement for d in context['dimensions']):raise XBRLError('drs_context_profile_unsupported')
  reported={d['dimension']:d for d in context['dimensions']}
  if len(reported)!=len(context['dimensions']):raise XBRLError('drs_duplicate_reported_dimension')
  if set(reported)-set(axes):raise XBRLError('drs_closed_extra_dimension')
  defaults={};typed=[]
  for axis in axes:
   member=reported.get(axis)
   if axis in typed_axes:
    if member is None:raise XBRLError('drs_required_dimension_missing')
    if member['kind']!='typed':raise XBRLError('drs_typed_reported_kind')
    row=checked.get(fact['context_ref'],{}).get(axis)
    if row is None or row['status']!='VALIDATED_SUPPORTED_TYPED_SCALAR':raise XBRLError('drs_typed_scalar_semantics_unsupported')
    domain_row=row['domain'];typed.append({'dimension':axis,'member_tree_sha256':row['member_tree_sha256'],'typed_domain_ref':domain_row['typed_domain_ref'],'domain_source_sha256':supplied[domain_row['schema_uri']]['sha256'],'scalar_validation':copy.deepcopy(row['scalar_validation'])})
   else:
    members,default=domain(axis)
    if member is None:
     if not default:raise XBRLError('drs_required_dimension_missing')
     defaults[axis]=default[0]
    else:
     if member['kind']!='explicit':raise XBRLError('drs_explicit_reported_kind')
     if member['member']not in members:raise XBRLError('drs_member_outside_domain')
     if default and member['member']==default[0]:raise XBRLError('drs_explicit_default_member')
  record={'source_fact_id':fact['source_fact_id'],'role':nets[0]['role'],'hypercube':cube,'context_element':placement,'used_defaults':defaults,'typed_dimensions':typed,'status':'VALIDATED_RESTRICTED_TYPED_CONTEXT'}
  size+=len(canonical(record))+1
  if size>8*1024*1024:raise XBRLError('drs_output_budget')
  records.append(record)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256');result['schema']='gig.sec.xbrl.dimensional_inline_set.v6'if parsed['schema']=='gig.sec.xbrl.inline_set.v1'else'gig.sec.xbrl.dimensional_instance.v6'
 result['dts_corroboration']['dimensional_validation']={'profile':TYPED_PROFILE,'facts':records,'typed_context_diagnostics_sha256':diagnostics['sha256'],'complete_drs_validation':False,'scope':'One direct positive closed hypercube,one role,original-DTS-bound supported typed scalars plus explicit domains/defaults;no typed equality,context/fact synthesis or financial promotion'}
 if len(canonical(result))>8*1024*1024:raise XBRLError('drs_output_budget')
 result['canonical_sha256']=digest(result);return result
