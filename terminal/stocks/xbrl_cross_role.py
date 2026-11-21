"""Original-DTS closed explicit targetRole traversal;not general DRS conformance."""
import copy,re
from urllib.parse import urljoin,urldefrag
from .xbrl_instance import X,L,XL,tag,qname,parse_xml,canonical,digest,XBRLError
from .xbrl_dts import XS,uri,walk
D='http://xbrl.org/2005/xbrldt';ARC='http://xbrl.org/int/dim/arcrole/'
PROFILE='ORIGINAL_DTS_CROSS_ROLE_CLOSED_EXPLICIT_V7';STANDARD='http://www.xbrl.org/2003/role/link'
KINDS={'all','hypercube-dimension','dimension-domain','domain-member','dimension-default'}
MAX_OUTPUT=8*1024*1024

def _role(value):
 if type(value)is not str or not 1<=len(value)<=512 or not re.match('[A-Za-z][A-Za-z0-9+.-]*:',value)or any(ord(c)<33 for c in value):raise XBRLError('drs_cross_role_uri')
 return value

def _originals(parsed,dts,documents,allow_observed,instance_uri):
 # Permission/hash binding precedes every original XML read.
 from .xbrl_dimensions import _typed_original_graph
 if type(parsed)is not dict or type(dts)is not dict or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256')or digest({k:v for k,v in dts.items()if k!='canonical_sha256'})!=dts.get('canonical_sha256'):raise XBRLError('drs_cross_input_identity')
 if parsed.get('schema')not in('gig.sec.xbrl.instance.v1','gig.sec.xbrl.inline_set.v1'):raise XBRLError('drs_cross_derived_schema_unsupported_or_already_applied')
 origin=parsed.get('origin')
 if type(allow_observed)is not bool or origin not in('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE')or dts.get('origin')!=origin or parsed.get('source',{}).get('origin')!=origin:raise XBRLError('drs_cross_origin_scope')
 if origin=='OBSERVED_OFFICIAL_RESPONSE':
  if not allow_observed:raise XBRLError('drs_cross_observed_processing_not_approved')
  if parsed['schema']=='gig.sec.xbrl.inline_set.v1':expected=[d['source'].get('permission_reference_sha256')for d in parsed.get('document_set',{}).get('documents',[])];actual=dts.get('permission_reference_sha256s')
  else:expected=[parsed['source'].get('permission_reference_sha256')];actual=[dts.get('permission_reference_sha256')]
  if not expected or any(type(v)is not str or not re.fullmatch('[0-9a-f]{64}',v)for v in expected)or expected!=actual:raise XBRLError('drs_cross_observed_permission_binding')
 if len(canonical(parsed))>MAX_OUTPUT or len(canonical(dts))>MAX_OUTPUT:raise XBRLError('drs_cross_input_budget')
 proof=parsed.get('dts_corroboration',{})
 if proof.get('dts_sha256')!=dts['canonical_sha256']:raise XBRLError('drs_cross_dts_binding_required')
 if canonical(proof.get('documents'))!=canonical(dts['documents'])or canonical(proof.get('concept_declarations'))!=canonical(dts['concepts']):raise XBRLError('drs_cross_retained_binding_mismatch')
 if dts.get('structural_closure')is not True or dts.get('unresolved'):raise XBRLError('drs_cross_closure_required')
 if dts.get('embedded_linkbase_profile')is not None or any(u['feature']=='EMBEDDED_LINKBASE_UNSUPPORTED'for u in dts['unsupported_semantics']):raise XBRLError('drs_cross_embedded_unsupported')
 return _typed_original_graph(parsed,dts,documents,instance_uri)

def _read(parsed,dts,supplied,*,effective=False):
 roots={key:parse_xml(doc['raw'])for key,doc in sorted(supplied.items())};kinds={d['uri']:d['kind']for d in dts['documents']};locators={};role_types={};role_uris=set()
 for key,root in roots.items():
  if kinds[key]!='schema':continue
  ids=set();allowed_role_types={id(c)for a in root.children if a.name==tag(XS,'annotation')for app in a.children if app.name==tag(XS,'appinfo')for c in app.children if c.name==tag(L,'roleType')}
  for node in walk(root):
   id_=node.attrs.get('id')
   if id_ is not None:
    if not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',id_)or id_ in ids:raise XBRLError('drs_cross_duplicate_schema_id')
    ids.add(id_)
   if node.name==tag(L,'roleType'):
    if id(node)not in allowed_role_types:raise XBRLError('drs_cross_role_type_location')
    if set(node.attrs)-{'id','roleURI'}or 'roleURI'not in node.attrs or node.text().strip()or not 1<=len(node.children)<=32 or [c.name for c in node.children]not in([tag(L,'usedOn')]*len(node.children),[tag(L,'definition')]+[tag(L,'usedOn')]*(len(node.children)-1)):raise XBRLError('drs_cross_role_type_structure')
    role=_role(node.attrs['roleURI']);used=[]
    if role==STANDARD or role in role_uris:raise XBRLError('drs_cross_duplicate_or_standard_role_declaration_unsupported')
    role_uris.add(role)
    if len(role_uris)>128:raise XBRLError('drs_cross_role_type_budget')
    if any(c.name==tag(L,'definition')and(c.attrs or c.children)for c in node.children):raise XBRLError('drs_cross_role_definition_structure')
    for c in node.children:
     if c.name==tag(L,'usedOn'):
      if c.attrs or c.children:raise XBRLError('drs_cross_used_on')
      used.append(qname(c.text().strip(),c))
    if tag(L,'definitionLink')not in used or len(used)!=len(set(used)):raise XBRLError('drs_cross_role_used_on')
    if id_ is not None:role_types[key+'#'+id_]=(role,node.source_ordinal)
  for node in root.children:
   if node.name==tag(XS,'element')and node.attrs.get('id')is not None:locators[key+'#'+node.attrs['id']]=tag(root.attrs['targetNamespace'],node.attrs['name'])
 arcs=[];refs=[];links=0
 for key,root in roots.items():
  if kinds[key]!='linkbase':continue
  declared={}
  for child in root.children:
   if child.name!=tag(L,'roleRef'):continue
   if set(child.attrs)!={'roleURI',tag(XL,'type'),tag(XL,'href')}or child.attrs[tag(XL,'type')]!='simple'or child.children or child.text().strip():raise XBRLError('drs_cross_role_ref_structure')
   role=_role(child.attrs['roleURI']);target=uri(urljoin(key,child.attrs[tag(XL,'href')]),fragment=True);schema,id_=urldefrag(target)
   if role in declared or schema not in supplied or kinds[schema]!='schema'or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',id_)or target not in role_types or role_types[target][0]!=role:raise XBRLError('drs_cross_role_not_resolved')
   declared[role]=target;refs.append({'source_uri':key,'source_sha256':supplied[key]['sha256'],'role':role,'role_type_uri':target,'schema_sha256':supplied[schema]['sha256'],'role_type_node_ordinal':role_types[target][1]})
   if len(refs)>128:raise XBRLError('drs_cross_role_ref_budget')
  for link in root.children:
   if link.name==tag(L,'roleRef'):continue
   if link.name!=tag(L,'definitionLink'):raise XBRLError('drs_cross_linkbase_content_unsupported')
   links+=1
   if links>64:raise XBRLError('drs_cross_network_budget')
   if set(link.attrs)!={tag(XL,'type'),tag(XL,'role')}or link.attrs[tag(XL,'type')]!='extended'or link.text().strip():raise XBRLError('drs_cross_definition_structure')
   role=_role(link.attrs[tag(XL,'role')])
   if role!=STANDARD and role not in declared:raise XBRLError('drs_cross_source_role_not_resolved')
   labels={}
   for node in link.children:
    if node.name!=tag(L,'loc'):continue
    a=node.attrs;label=a.get(tag(XL,'label'))
    if set(a)!={tag(XL,'type'),tag(XL,'label'),tag(XL,'href')}or a[tag(XL,'type')]!='locator'or type(label)is not str or not 1<=len(label)<=128 or label in labels or node.children or node.text().strip():raise XBRLError('drs_cross_locator_structure')
    concept=locators.get(uri(urljoin(key,a[tag(XL,'href')]),fragment=True))
    if concept is None:raise XBRLError('drs_cross_unresolved_locator')
    labels[label]=concept
   for node in link.children:
    if node.name==tag(L,'loc'):continue
    a=node.attrs;kind=a.get(tag(XL,'arcrole'),'').removeprefix(ARC)
    allowed={tag(XL,k)for k in('type','from','to','arcrole')}|{'order','priority','use'}|{tag(D,k)for k in('closed','contextElement','targetRole','usable')}
    if node.name!=tag(L,'definitionArc')or node.children or node.text().strip()or a.get(tag(XL,'type'))!='arc'or kind not in KINDS or not a.get(tag(XL,'arcrole'),'').startswith(ARC)or a.get(tag(XL,'from'))not in labels or a.get(tag(XL,'to'))not in labels:raise XBRLError('drs_cross_arc_structure_or_unsupported')
    if set(a)-allowed or a.get(tag(D,'usable'),'true')not in('true','1'):raise XBRLError('drs_cross_precedence_or_unusable_unsupported')
    if effective:
     if not re.fullmatch('[+-]?[0-9]{1,6}',a.get('priority','0'))or a.get('use','optional')not in('optional','prohibited'):raise XBRLError('drs_effective_priority_or_use')
    elif a.get('priority','0')!='0'or a.get('use','optional')!='optional':raise XBRLError('drs_cross_precedence_or_unusable_unsupported')
    if not re.fullmatch('[+-]?[0-9]{1,24}(?:\\.[0-9]{1,12})?',a.get('order','1')):raise XBRLError('drs_cross_order')
    placement=a.get(tag(D,'contextElement'));closed=a.get(tag(D,'closed'),'false');target=a.get(tag(D,'targetRole'))
    if closed not in('true','false','0','1')or kind=='all'and placement not in('segment','scenario'):raise XBRLError('drs_cross_assignment_attributes')
    if kind!='all'and(tag(D,'closed')in a or tag(D,'contextElement')in a)or kind not in('dimension-domain','domain-member')and tag(D,'usable')in a or kind=='dimension-default'and target is not None:raise XBRLError('drs_cross_attribute_scope_unsupported')
    if target is not None:
     _role(target)
     if target!=STANDARD and target not in declared:raise XBRLError('drs_cross_target_role_not_resolved')
    arcs.append({'kind':kind,'from':labels[a[tag(XL,'from')]],'to':labels[a[tag(XL,'to')]],'role':role,'target_role':target,'context_element':placement,'closed':closed in('true','1'),'source_uri':key,'source_sha256':supplied[key]['sha256'],'link_node_ordinal':link.source_ordinal,'arc_node_ordinal':node.source_ordinal})
    if effective:arcs[-1].update(from_label=a[tag(XL,'from')],to_label=a[tag(XL,'to')],priority=int(a.get('priority','0')),use=a.get('use','optional'),order_lexical=a.get('order','1'),dimensional_attributes={k:v for k,v in a.items()if k.startswith('{'+D+'}')})
    if len(arcs)>4096:raise XBRLError('drs_cross_arc_budget')
 return arcs,sorted(refs,key=lambda r:(r['source_uri'],r['role']))

def _records(parsed,concepts,arcs):
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise XBRLError('drs_cross_arc_budget')
 seen=set();by={};defaults={}
 def declaration(name,group):
  decl=concepts.get(name,{}).get('declaration',{})
  if decl.get('substitution_group')!=group or decl.get('typed_domain_ref')is not None or group in(tag(D,'hypercubeItem'),tag(D,'dimensionItem'))and decl.get('abstract')is not True:raise XBRLError('drs_cross_declaration_unsupported')
 for a in arcs:
  key=(a['role'],a['kind'],a['from'],a['to'])
  if key in seen:raise XBRLError('drs_cross_duplicate_relationship_unsupported')
  seen.add(key);by.setdefault((a['role'],a['kind'],a['from']),[]).append(a)
  if a['kind']=='dimension-default':
   declaration(a['from'],tag(D,'dimensionItem'));declaration(a['to'],tag(X,'item'));prior=defaults.get(a['from'])
   if prior is not None and prior!=a['to']:raise XBRLError('drs_cross_global_default_conflict')
   defaults[a['from']]=a['to']
 assignments=[a for a in arcs if a['kind']=='all']
 if len(assignments)!=1 or assignments[0]['closed']is not True:raise XBRLError('drs_cross_single_direct_closed_assignment_required')
 assignment=assignments[0];primary=assignment['from'];cube=assignment['to'];declaration(primary,tag(X,'item'));declaration(cube,tag(D,'hypercubeItem'))
 next_role=lambda a:a['target_role']or a['role']
 axes=by.get((next_role(assignment),'hypercube-dimension',cube),[])
 if not 1<=len(axes)<=32 or len({a['to']for a in axes})!=len(axes):raise XBRLError('drs_cross_dimension_budget_or_missing')
 domains={}
 for a in axes:
  axis=a['to'];declaration(axis,tag(D,'dimensionItem'));domain=by.get((next_role(a),'dimension-domain',axis),[])
  if len(domain)!=1:raise XBRLError('drs_cross_single_domain_required')
  root=domain[0];members=set();complete=set();count=0
  def visit(role,member,path,depth):
   nonlocal count
   if member in path:raise XBRLError('drs_cross_domain_cycle')
   if depth>=32:raise XBRLError('drs_cross_domain_depth')
   state=(role,member)
   if state in complete:return
   count+=1
   if count>2048:raise XBRLError('drs_cross_member_budget')
   declaration(member,tag(X,'item'));members.add(member)
   for child in by.get((role,'domain-member',member),[]):visit(next_role(child),child['to'],path|{member},depth+1)
   complete.add(state)
  visit(next_role(root),root['to'],set(),0)
  if primary in members:raise XBRLError('drs_cross_primary_item_polymorphism')
  default=defaults.get(axis)
  if default is not None and default not in members:raise XBRLError('drs_cross_default_outside_selected_domain')
  domains[axis]=(members,default)
 records=[]
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  if fact['concept']!=primary:raise XBRLError('drs_cross_direct_assignment_required')
  context=parsed['contexts'][fact['context_ref']]
  if type(context)is not dict or type(context.get('dimensions'))is not list or type(context.get('opaque_segment'))is not list:raise XBRLError('drs_cross_context_unsupported')
  dims=context['dimensions']
  if any(type(d)is not dict or set(d)!={'dimension','member','context_element','kind'}or any(type(d[k])is not str for k in d)or not re.fullmatch(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}',d['dimension'])or not re.fullmatch(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}',d['member'])for d in dims):raise XBRLError('drs_cross_context_unsupported')
  if context['semantic_sha256']!=digest({k:context[k]for k in('issuer_cik','period','dimensions','opaque_segment')})or context['opaque_segment']or len(dims)>32 or any(d['kind']!='explicit'or d['context_element']!=assignment['context_element']for d in dims):raise XBRLError('drs_cross_context_unsupported')
  reported={d['dimension']:d['member']for d in dims}
  if len(reported)!=len(dims):raise XBRLError('drs_cross_duplicate_dimension')
  if set(reported)-set(domains):raise XBRLError('drs_cross_closed_extra_dimension')
  used={}
  for axis,(members,default)in sorted(domains.items()):
   if axis in reported:
    if reported[axis]not in members:raise XBRLError('drs_cross_member_outside_domain')
    if reported[axis]==default:raise XBRLError('drs_cross_explicit_default_member')
   elif default is not None:used[axis]=default
   else:raise XBRLError('drs_cross_required_dimension_missing')
  records.append({'source_fact_id':fact['source_fact_id'],'role':assignment['role'],'hypercube':cube,'context_element':assignment['context_element'],'used_defaults':used,'status':'VALIDATED_RESTRICTED_CROSS_ROLE_CONTEXT'})
 return records

def corroborate_cross_role(parsed,dts,documents,allow_observed,instance_uri):
 supplied=_originals(parsed,dts,documents,allow_observed,instance_uri);arcs,refs=_read(parsed,dts,supplied);records=_records(parsed,dts['concepts'],arcs)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256');result['schema']='gig.sec.xbrl.dimensional_inline_set.v7'if parsed['schema']=='gig.sec.xbrl.inline_set.v1'else'gig.sec.xbrl.dimensional_instance.v7'
 result['dts_corroboration']['dimensional_validation']={'profile':PROFILE,'facts':records,'relationships':arcs,'role_references':refs,'complete_drs_validation':False,'scope':'Original-DTS direct positive closed explicit cube;targetRole replacement and global defaults;no inheritance,negative,typed,effective precedence or financial synthesis'}
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('drs_cross_output_budget')
 result['canonical_sha256']=digest(result);return result

def validate_cross_role_result(parsed):
 """Check retained proof consistency;raw-source authentication remains producer-only."""
 p=parsed['dts_corroboration']['dimensional_validation'];fail=lambda: XBRLError('xbrl_dimensional_result_contract')
 if set(p)!={'profile','facts','relationships','role_references','complete_drs_validation','scope'}or p['profile']!=PROFILE or p['complete_drs_validation']is not False or type(p['scope'])is not str or type(p['role_references'])is not list or len(p['role_references'])>128:raise fail()
 docs=parsed['dts_corroboration']['documents'];concepts=parsed['dts_corroboration'].get('concept_declarations',{})
 if type(docs)is not list or not 1<=len(docs)<=16 or type(concepts)is not dict or not 1<=len(concepts)<=2048 or any(type(d)is not dict or type(d.get('uri'))is not str or d.get('kind')not in('schema','linkbase')or type(d.get('sha256'))is not str or not re.fullmatch('[0-9a-f]{64}',d['sha256'])for d in docs):raise fail()
 sources={d['uri']:d for d in docs}
 if len(sources)!=len(docs):raise fail()
 ref_keys=set()
 for ref in p['role_references']:
  if type(ref)is not dict or set(ref)!={'source_uri','source_sha256','role','role_type_uri','schema_sha256','role_type_node_ordinal'}:raise fail()
  if any(type(ref[k])is not str for k in('source_uri','source_sha256','role','role_type_uri','schema_sha256')):raise fail()
  source=sources.get(ref['source_uri']);schema,id_=urldefrag(ref['role_type_uri']);target=sources.get(schema);key=(ref['source_uri'],ref['role'])
  if source is None or source['kind']!='linkbase'or source['sha256']!=ref['source_sha256']or target is None or target['kind']!='schema'or target['sha256']!=ref['schema_sha256']or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',id_)or key in ref_keys or type(ref['role_type_node_ordinal'])is not int or not 1<=ref['role_type_node_ordinal']<=50000:raise fail()
  _role(ref['role']);uri(ref['role_type_uri'],fragment=True);ref_keys.add(key)
 if p['role_references']!=sorted(p['role_references'],key=lambda r:(r['source_uri'],r['role'])):raise fail()
 arcs=p['relationships']
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise fail()
 for a in arcs:
  if type(a)is not dict or set(a)!={'kind','from','to','role','target_role','context_element','closed','source_uri','source_sha256','link_node_ordinal','arc_node_ordinal'}:raise fail()
  if any(type(a[k])is not str for k in('source_uri','source_sha256','role','kind','from','to'))or a['target_role']is not None and type(a['target_role'])is not str:raise fail()
  source=sources.get(a['source_uri']);_role(a['role'])
  if source is None or source['kind']!='linkbase'or source['sha256']!=a['source_sha256']or a['kind']not in KINDS or a['from']not in concepts or a['to']not in concepts or type(a['closed'])is not bool or a['kind']=='all'and a['context_element']not in('segment','scenario')or a['kind']!='all'and(a['closed']or a['context_element']is not None)or any(type(a[k])is not int or not 1<=a[k]<=50000 for k in('link_node_ordinal','arc_node_ordinal'))or a['link_node_ordinal']>=a['arc_node_ordinal']:raise fail()
  if a['role']!=STANDARD and(a['source_uri'],a['role'])not in ref_keys:raise fail()
  if a['target_role']is not None:
   _role(a['target_role'])
   if a['kind']=='dimension-default'or a['target_role']!=STANDARD and(a['source_uri'],a['target_role'])not in ref_keys:raise fail()
 try:expected=_records(parsed,concepts,arcs)
 except (XBRLError,KeyError,TypeError,ValueError):raise fail()from None
 if canonical(expected)!=canonical(p['facts']):raise fail()
