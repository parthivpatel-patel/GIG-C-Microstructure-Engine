"""Original-DTS positive closed cube conjunction with bounded primary inheritance.

V8 keeps one original has-hypercube base role. Cross-role primary inheritance,
alternative-base OR, negative/open/typed/precedence semantics remain unsupported.
"""
import copy,re
from collections import deque
from urllib.parse import urldefrag
from .xbrl_instance import X,tag,canonical,digest,XBRLError
from .xbrl_dts import uri
from .xbrl_cross_role import D,KINDS,STANDARD,_role,_originals,_read
PROFILE='ORIGINAL_DTS_INHERITED_CLOSED_EXPLICIT_V8'
MAX_OUTPUT=8*1024*1024;MAX_ASSIGNMENTS=64;MAX_FACT_ASSIGNMENTS=16
MAX_DOMAIN_STATES=32768;MAX_PRIMARY_STATES=32768
SHA=re.compile('[0-9a-f]{64}');QN=re.compile(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}')


def _declaration(concepts,name,group):
 entry=concepts.get(name);decl=entry.get('declaration')if type(entry)is dict else None
 if type(name)is not str or not QN.fullmatch(name)or type(decl)is not dict or decl.get('substitution_group')!=group or decl.get('typed_domain_ref')is not None or group in(tag(D,'dimensionItem'),tag(D,'hypercubeItem'))and decl.get('abstract')is not True:raise XBRLError('drs_inherited_cross_declaration_unsupported')
 return decl


def _records(parsed,concepts,arcs):
 """Evaluate the supported conjunction without changing any reported source fact."""
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise XBRLError('drs_inherited_cross_arc_budget')
 by={};seen=set();defaults={};parents={}
 groups={'all':(tag(X,'item'),tag(D,'hypercubeItem')),'hypercube-dimension':(tag(D,'hypercubeItem'),tag(D,'dimensionItem')),'dimension-domain':(tag(D,'dimensionItem'),tag(X,'item')),'domain-member':(tag(X,'item'),tag(X,'item')),'dimension-default':(tag(D,'dimensionItem'),tag(X,'item'))}
 for a in arcs:
  if a['kind']not in groups:raise XBRLError('drs_inherited_cross_relationship_unsupported')
  key=(a['role'],a['kind'],a['from'],a['to'])
  if key in seen:raise XBRLError('drs_inherited_cross_duplicate_relationship_unsupported')
  seen.add(key);by.setdefault((a['role'],a['kind'],a['from']),[]).append(a)
  for name,group in zip((a['from'],a['to']),groups[a['kind']]):_declaration(concepts,name,group)
  if a['kind']=='dimension-default':
   prior=defaults.get(a['from'])
   if prior is not None and prior!=a['to']:raise XBRLError('drs_inherited_cross_global_default_conflict')
   defaults[a['from']]=a['to']
  elif a['kind']=='domain-member':parents.setdefault(a['to'],[]).append(a)
 assignments=[a for a in arcs if a['kind']=='all']
 if not 1<=len(assignments)<=MAX_ASSIGNMENTS or any(a['closed']is not True for a in assignments):raise XBRLError('drs_inherited_cross_positive_closed_assignment_budget')
 roles={a['role']for a in assignments}
 if len(roles)!=1:raise XBRLError('drs_inherited_cross_alternative_base_roles_unsupported')
 role=assignments[0]['role'];next_role=lambda a:a['target_role']or a['role'];domain_cache={};shape_cache={};ancestor_cache={};domain_states=0;primary_states=0
 def domain(axis,source_role):
  key=(axis,source_role)
  if key in domain_cache:return domain_cache[key]
  roots=by.get((source_role,'dimension-domain',axis),[])
  if len(roots)!=1:raise XBRLError('drs_inherited_cross_single_domain_required')
  root=roots[0];members=set();completed=set();count=0
  def visit(current,member,path,depth):
   nonlocal count,domain_states
   if member in path:raise XBRLError('drs_inherited_cross_domain_cycle')
   if depth>=32:raise XBRLError('drs_inherited_cross_domain_depth')
   state=(current,member)
   if state in completed:return
   count+=1;domain_states+=1
   if domain_states>MAX_DOMAIN_STATES:raise XBRLError('drs_inherited_cross_total_domain_state_budget')
   if count>2048:raise XBRLError('drs_inherited_cross_member_budget')
   members.add(member)
   for child in by.get((current,'domain-member',member),[]):visit(next_role(child),child['to'],path|{member},depth+1)
   completed.add(state)
  visit(next_role(root),root['to'],set(),0);default=defaults.get(axis)
  if default is not None and default not in members:raise XBRLError('drs_inherited_cross_default_outside_selected_domain')
  domain_cache[key]=(members,default);return domain_cache[key]
 def shape(a):
  key=(a['from'],a['to'])
  if key in shape_cache:return shape_cache[key]
  axes=by.get((next_role(a),'hypercube-dimension',a['to']),[])
  if not 1<=len(axes)<=32 or len({v['to']for v in axes})!=len(axes):raise XBRLError('drs_inherited_cross_dimension_budget_or_missing')
  result={axis['to']:domain(axis['to'],next_role(axis))for axis in axes}
  if any(a['from']in members for members,_ in result.values()):raise XBRLError('drs_inherited_cross_primary_item_polymorphism')
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
   if primary_states>MAX_PRIMARY_STATES:raise XBRLError('drs_inherited_cross_total_primary_state_budget')
   _declaration(concepts,node,tag(X,'item'))
   if len(found)>2048:raise XBRLError('drs_inherited_cross_primary_item_budget')
   incoming[node]=[]
   for a in parents.get(node,[]):
    # The supported inherited chain stays in the original assignment base.
    # Reaching a primary ancestor through any other role is an explicit gap,
    # never an implicit role union or a guessed alternate-base conjunction.
    if a['role']!=role or next_role(a)!=role:raise XBRLError('drs_inherited_cross_primary_inheritance_role_unsupported')
    incoming[node].append(a['from']);pending.append(a['from'])
  degree={node:len(set(incoming[node]))for node in found};children={node:set()for node in found};depth={node:0 for node in found}
  for child,parents_ in incoming.items():
   for parent in parents_:children[parent].add(child)
  pending=deque(sorted(node for node in found if degree[node]==0));visited=0
  while pending:
   node=pending.popleft();visited+=1
   if depth[node]>=32:raise XBRLError('drs_inherited_cross_primary_depth')
   for child in sorted(children[node]):
    degree[child]-=1;depth[child]=max(depth[child],depth[node]+1)
    if degree[child]==0:pending.append(child)
  if visited!=len(found):raise XBRLError('drs_inherited_cross_primary_cycle')
  ancestor_cache[concept]=found;return found
 records=[];size=0
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  inherited=ancestors(fact['concept']);selected=sorted((a for a in assignments if a['from']in inherited),key=lambda a:(a['from'],a['to']))
  if not 1<=len(selected)<=MAX_FACT_ASSIGNMENTS:raise XBRLError('drs_inherited_cross_fact_assignment_budget_or_missing')
  placements={a['context_element']for a in selected}
  if len(placements)!=1:raise XBRLError('drs_inherited_cross_mixed_context_assignments_unsupported')
  placement=selected[0]['context_element'];context=parsed['contexts'][fact['context_ref']]
  if type(context)is not dict or type(context.get('dimensions'))is not list or type(context.get('opaque_segment'))is not list:raise XBRLError('drs_inherited_cross_context_unsupported')
  dims=context['dimensions']
  if any(type(d)is not dict or set(d)!={'dimension','member','context_element','kind'}or any(type(d[k])is not str for k in d)or not QN.fullmatch(d['dimension'])or not QN.fullmatch(d['member'])for d in dims):raise XBRLError('drs_inherited_cross_context_unsupported')
  if context['semantic_sha256']!=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')})or context['opaque_segment']or len(dims)>32 or any(d['kind']!='explicit'or d['context_element']!=placement for d in dims):raise XBRLError('drs_inherited_cross_context_unsupported')
  reported={d['dimension']:d['member']for d in dims}
  if len(reported)!=len(dims):raise XBRLError('drs_inherited_cross_duplicate_dimension')
  aggregate={};details=[];all_axes=set()
  for a in selected:
   domains=shape(a);all_axes.update(domains)
   if len(all_axes)>32:raise XBRLError('drs_inherited_cross_combined_dimension_budget')
   if set(reported)-set(domains):raise XBRLError('drs_inherited_cross_closed_extra_dimension')
   if any(fact['concept']in members for members,_ in domains.values()):raise XBRLError('drs_inherited_cross_primary_item_polymorphism')
   used={}
   for axis,(members,default)in sorted(domains.items()):
    if axis in reported:
     if reported[axis]not in members:raise XBRLError('drs_inherited_cross_member_outside_domain')
     if reported[axis]==default:raise XBRLError('drs_inherited_cross_explicit_default_member')
    elif default is not None:used[axis]=default
    else:raise XBRLError('drs_inherited_cross_required_dimension_missing')
   for axis,value in used.items():
    if axis in aggregate and aggregate[axis]!=value:raise XBRLError('drs_inherited_cross_default_conflict')
    aggregate[axis]=value
   details.append({'primary_item':a['from'],'hypercube':a['to'],'context_element':placement,'closed':True,'used_defaults':used,'inherited':a['from']!=fact['concept'],'source_uri':a['source_uri'],'source_arc_node_ordinal':a['arc_node_ordinal']})
  record={'source_fact_id':fact['source_fact_id'],'role':role,'context_element':placement,'used_defaults':dict(sorted(aggregate.items())),'status':'VALIDATED_RESTRICTED_INHERITED_CROSS_ROLE_CONTEXT','primary_ancestors':sorted(inherited),'assignments':details}
  size+=len(canonical(record))
  if size>MAX_OUTPUT:raise XBRLError('drs_inherited_cross_output_budget')
  records.append(record)
 return records


def corroborate_inherited_cross_role(parsed,dts,documents,allow_observed,instance_uri):
 supplied=_originals(parsed,dts,documents,allow_observed,instance_uri);arcs,refs=_read(parsed,dts,supplied);records=_records(parsed,dts['concepts'],arcs)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256');result['schema']='gig.sec.xbrl.dimensional_inline_set.v8'if parsed['schema']=='gig.sec.xbrl.inline_set.v1'else'gig.sec.xbrl.dimensional_instance.v8'
 result['dts_corroboration']['dimensional_validation']={'profile':PROFILE,'facts':records,'relationships':arcs,'role_references':refs,'complete_drs_validation':False,'scope':'Original-DTS positive closed explicit cube conjunction;transitive primary inheritance in one preserved base role;cross-role consecutive cube/domain paths;no negative,typed,alternative-base,precedence or source-fact synthesis'}
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('drs_inherited_cross_output_budget')
 result['canonical_sha256']=digest(result);return result


def _validate_receipts(parsed,p):
 """V8 versioned retained-source checks; original role XML remains producer-only."""
 fail=lambda:XBRLError('xbrl_dimensional_result_contract')
 docs=parsed['dts_corroboration']['documents'];concepts=parsed['dts_corroboration'].get('concept_declarations',{})
 if type(docs)is not list or not 1<=len(docs)<=16 or type(concepts)is not dict or not 1<=len(concepts)<=2048 or any(type(d)is not dict or type(d.get('uri'))is not str or d.get('kind')not in('schema','linkbase')or type(d.get('sha256'))is not str or not SHA.fullmatch(d['sha256'])for d in docs):raise fail()
 sources={d['uri']:d for d in docs}
 if len(sources)!=len(docs):raise fail()
 refs=p['role_references'];ref_keys=set();role_type_nodes={};role_type_uris={}
 if type(refs)is not list or len(refs)>128:raise fail()
 for ref in refs:
  if type(ref)is not dict or set(ref)!={'source_uri','source_sha256','role','role_type_uri','schema_sha256','role_type_node_ordinal'}or any(type(ref[k])is not str for k in('source_uri','source_sha256','role','role_type_uri','schema_sha256')):raise fail()
  source=sources.get(ref['source_uri']);schema,id_=urldefrag(ref['role_type_uri']);target=sources.get(schema);key=(ref['source_uri'],ref['role'])
  if source is None or source['kind']!='linkbase'or source['sha256']!=ref['source_sha256']or target is None or target['kind']!='schema'or target['sha256']!=ref['schema_sha256']or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',id_)or key in ref_keys or type(ref['role_type_node_ordinal'])is not int or not 1<=ref['role_type_node_ordinal']<=50000:raise fail()
  _role(ref['role']);uri(ref['role_type_uri'],fragment=True)
  node_key=(schema,ref['role_type_node_ordinal']);identity=(ref['role'],ref['role_type_uri'],ref['schema_sha256'])
  if node_key in role_type_nodes and role_type_nodes[node_key]!=identity:raise fail()
  uri_identity=(ref['role'],ref['role_type_node_ordinal'],ref['schema_sha256'])
  if ref['role_type_uri']in role_type_uris and role_type_uris[ref['role_type_uri']]!=uri_identity:raise fail()
  role_type_nodes[node_key]=identity;role_type_uris[ref['role_type_uri']]=uri_identity;ref_keys.add(key)
 if refs!=sorted(refs,key=lambda r:(r['source_uri'],r['role'])):raise fail()
 arcs=p['relationships']
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise fail()
 arc_nodes=set();link_roles={}
 for a in arcs:
  if type(a)is not dict or set(a)!={'kind','from','to','role','target_role','context_element','closed','source_uri','source_sha256','link_node_ordinal','arc_node_ordinal'}or any(type(a[k])is not str for k in('source_uri','source_sha256','role','kind','from','to'))or a['target_role']is not None and type(a['target_role'])is not str:raise fail()
  source=sources.get(a['source_uri']);_role(a['role'])
  if source is None or source['kind']!='linkbase'or source['sha256']!=a['source_sha256']or a['kind']not in KINDS or a['from']not in concepts or a['to']not in concepts or type(a['closed'])is not bool or a['kind']=='all'and a['context_element']not in('segment','scenario')or a['kind']!='all'and(a['closed']or a['context_element']is not None)or any(type(a[k])is not int or not 1<=a[k]<=50000 for k in('link_node_ordinal','arc_node_ordinal'))or a['link_node_ordinal']>=a['arc_node_ordinal']:raise fail()
  arc_key=(a['source_uri'],a['arc_node_ordinal']);link_key=(a['source_uri'],a['link_node_ordinal'])
  if arc_key in arc_nodes or link_key in link_roles and link_roles[link_key]!=a['role']:raise fail()
  arc_nodes.add(arc_key);link_roles[link_key]=a['role']
  if a['role']!=STANDARD and(a['source_uri'],a['role'])not in ref_keys:raise fail()
  if a['target_role']is not None:
   _role(a['target_role'])
   if a['kind']=='dimension-default'or a['target_role']!=STANDARD and(a['source_uri'],a['target_role'])not in ref_keys:raise fail()
 return concepts,arcs


def validate_inherited_cross_role_result(parsed):
 p=parsed['dts_corroboration']['dimensional_validation'];fail=lambda:XBRLError('xbrl_dimensional_result_contract')
 if set(p)!={'profile','facts','relationships','role_references','complete_drs_validation','scope'}or p['profile']!=PROFILE or p['complete_drs_validation']is not False or type(p['scope'])is not str:raise fail()
 try:
  concepts,arcs=_validate_receipts(parsed,p);expected=_records(parsed,concepts,arcs)
 except (XBRLError,KeyError,TypeError,ValueError):raise fail()from None
 if canonical(expected)!=canonical(p['facts']):raise fail()
