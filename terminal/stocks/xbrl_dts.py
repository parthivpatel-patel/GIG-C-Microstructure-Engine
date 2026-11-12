"""Bounded offline DTS discovery and explicit presentation-relationship profile.

Never fetches a URI. Closure/known declarations are structural evidence,not full
XML Schema validation,extension semantics or complete financial statements.
"""
import hashlib,re
from collections import deque
from fractions import Fraction
from urllib.parse import urljoin,urlsplit
from .xbrl_instance import X,L,XL,tag,parse_xml,qname,digest,canonical,XBRLError
XS='http://www.w3.org/2001/XMLSchema';PARENT='http://www.xbrl.org/2003/arcrole/parent-child'

def uri(value,*,fragment=False):
 if type(value)is not str or not 1<=len(value)<=512:raise XBRLError('dts_uri')
 u=urlsplit(value)
 if u.scheme not in('http','https')or not u.hostname or u.username or u.password or u.query or u.port is not None or not fragment and u.fragment or any(ord(c)<33 for c in value):raise XBRLError('dts_uri')
 return value

def walk(root):
 pending=[root]
 while pending:
  node=pending.pop()
  if '{http://www.w3.org/XML/1998/namespace}base'in node.attrs:raise XBRLError('dts_xml_base_unsupported')
  yield node;pending.extend(reversed(node.children))

def discover(raw,instance_uri,expected_instance_sha256,documents,*,origin='HISTORICAL_SYNTHETIC',allow_observed=False,permission_reference=None):
 if origin not in('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE')or type(allow_observed)is not bool:raise XBRLError('dts_origin')
 if origin!='HISTORICAL_SYNTHETIC'and(not allow_observed or type(permission_reference)is not str or not 1<=len(permission_reference)<=256):raise XBRLError('dts_observed_processing_not_approved')
 uri(instance_uri)
 if type(raw)is not bytes or not 1<=len(raw)<=2*1024*1024 or hashlib.sha256(raw).hexdigest()!=expected_instance_sha256:raise XBRLError('dts_instance_digest_or_budget')
 if type(documents)is not list or len(documents)>16:raise XBRLError('dts_document_budget')
 supplied=_supplied_documents(documents)
 root=parse_xml(raw);requests=deque();edges=[];schema_roots=[]
 for node in walk(root):
  if node.name==tag(L,'schemaRef'):
   href=node.attrs.get(tag(XL,'href'))
   if node.attrs.get(tag(XL,'type'))!='simple'or type(href)is not str or not href:raise XBRLError('dts_schema_reference')
   target=uri(urljoin(instance_uri,href));schema_roots.append(target);requests.append((target,0,None,'schema'))
   if len(schema_roots)>32:raise XBRLError('dts_schema_root_budget')
 if not schema_roots:raise XBRLError('dts_schema_reference_required')
 return _discover_roots(schema_roots,supplied,{'schema':'gig.sec.xbrl.dts.v1','origin':origin,'instance_sha256':expected_instance_sha256,'permission_reference_sha256':hashlib.sha256(permission_reference.encode()).hexdigest()if type(permission_reference)is str else None})

def _supplied_documents(documents):
 if type(documents)is not list or len(documents)>16:raise XBRLError('dts_document_budget')
 supplied={};total=0
 for doc in documents:
  if type(doc)is not dict or set(doc)!={'uri','raw','sha256'}or type(doc['raw'])is not bytes or not 1<=len(doc['raw'])<=2*1024*1024:raise XBRLError('dts_document_contract')
  key=uri(doc['uri']);total+=len(doc['raw'])
  if total>8*1024*1024:raise XBRLError('dts_total_byte_budget')
  if hashlib.sha256(doc['raw']).hexdigest()!=doc['sha256']:raise XBRLError('dts_document_digest')
  if key in supplied and supplied[key]!=doc:raise XBRLError('dts_document_conflict')
  supplied[key]=doc
 return supplied

def _discover_roots(schema_roots,supplied,metadata):
 requests=deque((target,0,None,'schema')for target in schema_roots)
 edges=[]
 loaded={};unresolved=[];namespaces={};concepts={};locators={};linkbases=[];unsupported=[];types={}
 while requests:
  if len(edges)>4096:raise XBRLError('dts_edge_budget')
  key,depth,namespace,kind=requests.popleft()
  if depth>8:raise XBRLError('dts_discovery_depth')
  if key in loaded:
   if loaded[key]['kind']!=kind:raise XBRLError('dts_reference_document_kind')
   if namespace is not None and namespaces.get(key)!=namespace:raise XBRLError('dts_import_namespace_conflict')
   continue
  if key not in supplied:
   if {'uri':key,'reason':'NOT_SUPPLIED_NO_NETWORK_FETCH'}not in unresolved:unresolved.append({'uri':key,'reason':'NOT_SUPPLIED_NO_NETWORK_FETCH'})
   continue
  doc=supplied[key];node=parse_xml(doc['raw']);items=list(walk(node));loaded[key]={'uri':key,'sha256':doc['sha256'],'received_at':None,'fetched':False,'kind':kind}
  if node.name!=(tag(XS,'schema')if kind=='schema'else tag(L,'linkbase')):raise XBRLError('dts_reference_document_kind')
  if node.name==tag(XS,'schema'):
   target=node.attrs.get('targetNamespace')
   if type(target)is not str or not 1<=len(target)<=512:raise XBRLError('dts_chameleon_or_missing_namespace_unsupported')
   if namespace is not None and target!=namespace:raise XBRLError('dts_import_namespace_conflict')
   namespaces[key]=target
   for child in items:
    if child.name in(tag(XS,'redefine'),tag(XS,'override')):raise XBRLError('dts_schema_redefinition_unsupported')
    if child.name in(tag(XS,'import'),tag(XS,'include')):
     path=child.attrs.get('schemaLocation');expected=target if child.name==tag(XS,'include')else child.attrs.get('namespace')
     if path is None:unresolved.append({'namespace':expected,'reason':'IMPORT_LOCATION_NOT_DECLARED'});continue
     destination=uri(urljoin(key,path));edges.append({'from':key,'to':destination,'kind':'include'if child.name==tag(XS,'include')else'import','namespace':expected});requests.append((destination,depth+1,expected,'schema'))
    if child.name==tag(L,'linkbaseRef'):
     href=child.attrs.get(tag(XL,'href'))
     if child.attrs.get(tag(XL,'type'))!='simple'or type(href)is not str or not href:raise XBRLError('dts_linkbase_reference')
     destination=uri(urljoin(key,href));edges.append({'from':key,'to':destination,'kind':'linkbase'});requests.append((destination,depth+1,None,'linkbase'))
   for element in node.children:
    if element.name in(tag(XS,'simpleType'),tag(XS,'complexType')):
     from .xbrl_types import declaration
     name=element.attrs.get('name')
     if type(name)is not str or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',name):raise XBRLError('dts_type_identity')
     expanded=tag(target,name);value=declaration(element)
     if expanded in types and types[expanded]['declaration']!=value:raise XBRLError('dts_type_conflict')
     entry=types.setdefault(expanded,{'declaration':value,'source_documents':[]})
     if key in entry['source_documents']:raise XBRLError('dts_duplicate_type_declaration')
     entry['source_documents'].append(key)
     if len(types)>128:raise XBRLError('dts_type_budget')
     unsupported.append({'uri':key,'feature':'CUSTOM_TYPE_SCHEMA_VALIDATION_NOT_PERFORMED'});continue
    if element.name!=tag(XS,'element'):continue
    name=element.attrs.get('name');identifier=element.attrs.get('id')
    if type(name)is not str or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',name)or identifier is not None and not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',identifier):raise XBRLError('dts_element_identity')
    period=element.attrs.get(tag(X,'periodType'));balance=element.attrs.get(tag(X,'balance'))
    if period not in(None,'instant','duration')or balance not in(None,'credit','debit'):raise XBRLError('dts_element_semantics')
    for field in('abstract','nillable'):
     if element.attrs.get(field,'false')not in('true','false','0','1'):raise XBRLError('dts_boolean')
    concept=tag(target,name);record={'concept':concept,'type':qname(element.attrs['type'],element)if'type'in element.attrs else None,'substitution_group':qname(element.attrs['substitutionGroup'],element)if'substitutionGroup'in element.attrs else None,'period_type':period,'balance':balance,'abstract':element.attrs.get('abstract','false')in('true','1'),'nillable':element.attrs.get('nillable','false')in('true','1')}
    if concept in concepts and concepts[concept]['declaration']!=record:raise XBRLError('dts_concept_conflict')
    entry=concepts.setdefault(concept,{'declaration':record,'source_documents':[]})
    if key in entry['source_documents']:raise XBRLError('dts_duplicate_concept_declaration')
    entry['source_documents'].append(key)
    if identifier:
     ref=key+'#'+identifier
     if ref in locators:raise XBRLError('dts_duplicate_schema_id')
     locators[ref]=concept
    if len(concepts)>2048:raise XBRLError('dts_concept_budget')
  elif node.name==tag(L,'linkbase'):linkbases.append((key,node))
  else:raise XBRLError('dts_document_root')
 networks=[]
 for key,root in linkbases:
  for link in root.children:
   if link.name!=tag(L,'presentationLink'):unsupported.append({'uri':key,'feature':'NON_PRESENTATION_LINK_NOT_INTERPRETED'});continue
   if len(networks)>=64:raise XBRLError('dts_network_budget')
   if link.attrs.get(tag(XL,'type'))!='extended':raise XBRLError('dts_extended_link_type')
   role=link.attrs.get(tag(XL,'role'))
   if type(role)is not str or not 1<=len(role)<=512:raise XBRLError('dts_presentation_role')
   labels={};arcs=[];issues=[]
   for node in link.children:
    if node.name==tag(L,'loc'):
     if node.attrs.get(tag(XL,'type'))!='locator':raise XBRLError('dts_locator_type')
     label=node.attrs.get(tag(XL,'label'));href=node.attrs.get(tag(XL,'href'))
     if type(label)is not str or not 1<=len(label)<=128 or type(href)is not str:raise XBRLError('dts_locator')
     ref=uri(urljoin(key,href),fragment=True);concept=locators.get(ref)
     if label in labels:raise XBRLError('dts_duplicate_locator_label')
     labels[label]=concept
     if concept is None:issues.append('UNRESOLVED_LOCATOR')
   for node in link.children:
    if node.name!=tag(L,'presentationArc'):continue
    a=node.attrs
    if a.get(tag(XL,'type'))!='arc':raise XBRLError('dts_arc_type')
    before=a.get(tag(XL,'from'));after=a.get(tag(XL,'to'));order=a.get('order','1')
    if before not in labels or after not in labels or not re.fullmatch(r'[+-]?[0-9]{1,24}(?:\.[0-9]{1,12})?',order):raise XBRLError('dts_presentation_arc')
    if a.get(tag(XL,'arcrole'))!=PARENT or a.get('priority','0')!='0'or a.get('use','optional')!='optional':issues.append('ARC_PRECEDENCE_OR_ROLE_UNSUPPORTED');continue
    arcs.append({'from':labels[before],'to':labels[after],'order':order,'preferred_label':a.get('preferredLabel'),'source_uri':key})
    if len(arcs)>4096:raise XBRLError('dts_arc_budget')
   if issues:networks.append({'role':role,'usable':False,'issues':sorted(set(issues)),'arcs':arcs,'roots':[]});continue
   vertices={v for arc in arcs for v in(arc['from'],arc['to'])};degree={v:0 for v in vertices};children={v:[]for v in vertices}
   for arc in arcs:degree[arc['to']]+=1;children[arc['from']].append(arc['to'])
   roots=sorted(v for v,n in degree.items()if n==0);queue=deque(roots);visited=0
   while queue:
    parent=queue.popleft();visited+=1
    for child in children[parent]:
     degree[child]-=1
     if degree[child]==0:queue.append(child)
   if visited!=len(vertices):issues.append('DIRECTED_PRESENTATION_CYCLE')
   arcs.sort(key=lambda a:(a['from'],Fraction(a['order']),a['to']))
   networks.append({'role':role,'usable':not issues,'issues':issues,'arcs':arcs,'roots':roots})
   if len(networks)>64:raise XBRLError('dts_network_budget')
 # A role split across links may require cross-document equivalence/precedence.
 # Preserve the inputs but refuse to present a partial link as the complete role.
 roles={n['role']for n in networks}
 for role in roles:
  links=[n for n in networks if n['role']==role]
  if len(links)>1:
   for network in links:network['usable']=False;network['issues']=sorted(set(network['issues']+['ROLE_SPLIT_ACROSS_LINKS_UNSUPPORTED']))
 result={**metadata,'schema_roots':sorted(set(schema_roots)),'documents':sorted(loaded.values(),key=lambda d:d['uri']),'discovery_edges':sorted(edges,key=lambda e:(e['from'],e['to'])),'concepts':concepts,'presentation':networks,'unresolved':unresolved,'unsupported_semantics':unsupported,'structural_closure':not unresolved,'schema_type_validation':False,'complete_statements':False,'provider_requested':False}
 if types:result['type_declarations']=types;result['type_declaration_profile']='NAMED_RESTRICTION_METADATA_V1'
 if len(canonical(result))>16*1024*1024:raise XBRLError('dts_output_budget')
 result['canonical_sha256']=digest(result);return result

def discover_inline_set(parsed,documents,*,allow_observed=False,permission_references=None):
 """Discover the parsed set's exact supplied reference union;never fabricate XML."""
 if type(parsed)is not dict or parsed.get('schema')!='gig.sec.xbrl.inline_set.v1'or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256'):raise XBRLError('dts_set_identity')
 source_set=parsed['document_set'];sources=source_set['documents'];origin=parsed['origin']
 if source_set['sha256']!=digest(sources)or parsed['source']['source_sha256']!=source_set['sha256']:raise XBRLError('dts_set_source_scope')
 if origin not in('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE')or type(allow_observed)is not bool:raise XBRLError('dts_origin')
 if origin=='OBSERVED_OFFICIAL_RESPONSE':
  if not allow_observed or type(permission_references)is not list or len(permission_references)!=len(sources):raise XBRLError('dts_observed_processing_not_approved')
  for reference,source in zip(permission_references,sources):
   if type(reference)is not str or not 1<=len(reference)<=256 or hashlib.sha256(reference.encode()).hexdigest()!=source['source']['permission_reference_sha256']:raise XBRLError('dts_observed_processing_not_approved')
 roots=[uri(r['uri'])for r in source_set['schema_references']]
 if not 1<=len(roots)<=32:raise XBRLError('dts_schema_reference_required')
 supplied=_supplied_documents(documents)
 return _discover_roots(roots,supplied,{'schema':'gig.sec.xbrl.dts_set.v1','origin':origin,'document_set_sha256':source_set['sha256'],'original_inline_documents':[{'uri':s['uri'],'source_sha256':s['source']['source_sha256']}for s in sources],'permission_reference_sha256s':[s['source']['permission_reference_sha256']for s in sources]})
