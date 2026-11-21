"""V9 original-byte effective DRS, followed by the bounded V8 cube evaluator.

This is an opt-in subset, not general XBRL/Dimensions conformance. All supplied
arcs (including prohibited ones) must fit the independently validated vocabulary.
"""
import copy,re
from fractions import Fraction
from .xbrl_instance import X,L,XL,tag,canonical,digest,parse_xml,XBRLError
from .xbrl_cross_role import D,_originals,_read
from .xbrl_inherited_cross_role import _records,_validate_receipts,MAX_OUTPUT,QN
from .xbrl_dts import XS,uri

PROFILE='ORIGINAL_DTS_EFFECTIVE_CLOSED_EXPLICIT_V9'
BASE_FIELDS={'kind','from','to','role','target_role','context_element','closed','source_uri','source_sha256','link_node_ordinal','arc_node_ordinal'}
EXTRA_FIELDS={'from_label','to_label','priority','use','order_lexical','dimensional_attributes'}
ORDER=re.compile(r'[+-]?[0-9]{1,24}(?:\.[0-9]{1,12})?')
RESERVED_NAMESPACES={XS,X,L,XL,D,'http://www.w3.org/2001/XMLSchema-instance','http://www.w3.org/XML/1998/namespace','http://www.w3.org/2000/xmlns/','http://xbrl.org/2006/xbrldi'}
SCOPE='Original-DTS effective positive closed explicit cube conjunction;bounded same-base primary inheritance and cross-role cube/domain paths;all input arcs retained;no negative,typed,alternative-base,unusable or general PSVI support'


def _schema_sources(supplied,documents):
 """Original-byte receipt of the supported schema namespace boundary."""
 receipts=[]
 for doc in documents:
  if doc['kind']!='schema':continue
  root=parse_xml(supplied[doc['uri']]['raw']);namespace=root.attrs.get('targetNamespace')
  if root.name!=tag(XS,'schema')or type(namespace)is not str or not 1<=len(namespace)<=512 or namespace in RESERVED_NAMESPACES:raise XBRLError('drs_effective_reserved_or_invalid_schema_namespace_unsupported')
  receipts.append({'source_uri':doc['uri'],'source_sha256':doc['sha256'],'target_namespace':namespace})
 return sorted(receipts,key=lambda r:r['source_uri'])


def _validate_schema_sources(receipts,documents):
 if type(receipts)is not list or not 1<=len(receipts)<=16:raise XBRLError('drs_effective_schema_source_contract')
 expected={d['uri']:d['sha256']for d in documents if d['kind']=='schema'};seen={}
 for r in receipts:
  if type(r)is not dict or set(r)!={'source_uri','source_sha256','target_namespace'}or any(type(r[k])is not str for k in r):raise XBRLError('drs_effective_schema_source_contract')
  source=r['source_uri'];namespace=r['target_namespace'];uri(source)
  if source in seen or source not in expected or expected[source]!=r['source_sha256']or not 1<=len(namespace)<=512 or namespace in RESERVED_NAMESPACES:raise XBRLError('drs_effective_schema_source_contract')
  seen[source]=namespace
 if set(seen)!=set(expected)or receipts!=sorted(receipts,key=lambda r:r['source_uri']):raise XBRLError('drs_effective_schema_source_contract')
 return seen


def _endpoint_sources(arcs,concepts,schemas):
 # A concept QName alone does not prove identity of the XML fragment targeted
 # by a locator. V9 admits one original declaration document per endpoint; DTS
 # metadata that merges identical declarations from distinct sources is rejected.
 for a in arcs:
  for field in('from','to'):
   concept=a[field];entry=concepts.get(concept);sources=entry.get('source_documents')if type(entry)is dict else None
   if type(concept)is not str or not QN.fullmatch(concept)or type(sources)is not list or len(sources)!=1 or type(sources[0])is not str or sources[0]not in schemas or schemas[sources[0]]!=concept.split('}',1)[0][1:]:raise XBRLError('drs_effective_endpoint_source_ambiguous_or_unsupported')


def _project(a):return {k:a[k]for k in BASE_FIELDS}


def _effective(arcs):
 if type(arcs)is not list or not 1<=len(arcs)<=4096:raise XBRLError('drs_effective_arc_budget')
 groups={};xpath_orders={};label_pairs=set();labels={}
 for i,a in enumerate(arcs):
  if type(a)is not dict or set(a)!=BASE_FIELDS|EXTRA_FIELDS:raise XBRLError('drs_effective_arc_contract')
  if type(a['priority'])is not int or not -999999<=a['priority']<=999999 or a['use']not in('optional','prohibited')or type(a['order_lexical'])is not str or not ORDER.fullmatch(a['order_lexical']):raise XBRLError('drs_effective_priority_or_use')
  for field,concept in(('from_label','from'),('to_label','to')):
   label=a[field]
   if type(label)is not str or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',label):raise XBRLError('drs_effective_label_subset')
   identity=(a['source_uri'],a['link_node_ordinal'],label)
   if identity in labels and labels[identity]!=a[concept]:raise XBRLError('drs_effective_locator_binding')
   labels[identity]=a[concept]
  pair=(a['source_uri'],a['link_node_ordinal'],a['from_label'],a['to_label'])
  if pair in label_pairs:raise XBRLError('drs_effective_duplicate_xlink_arc')
  label_pairs.add(pair)
  attrs=a['dimensional_attributes']
  if type(attrs)is not dict or set(attrs)-{tag(D,k)for k in('closed','contextElement','targetRole','usable')}or any(type(v)is not str for v in attrs.values()):raise XBRLError('drs_effective_attribute_contract')
  closed=attrs.get(tag(D,'closed'),'false');usable=attrs.get(tag(D,'usable'),'true')
  if closed not in('true','false','0','1')or usable not in('true','1')or a['closed']!=(closed in('true','1'))or a['context_element']!=attrs.get(tag(D,'contextElement'))or a['target_role']!=attrs.get(tag(D,'targetRole')):raise XBRLError('drs_effective_attribute_binding')
  if a['kind']!='all'and any(tag(D,k)in attrs for k in('closed','contextElement'))or a['kind']not in('dimension-domain','domain-member')and tag(D,'usable')in attrs:raise XBRLError('drs_effective_attribute_scope')
  # order is a declared default on arcType. Dimensional attributes are validated
  # through its lax wildcard: absent global attributes are not injected into the
  # PSVI attribute-use set. Preserve their authored presence, even if their DRS
  # semantic defaults happen to be equal. Boolean values use XML Schema value space.
  non_exempt={k:(v in('true','1')if k in(tag(D,'closed'),tag(D,'usable'))else v)for k,v in attrs.items()}
  order=Fraction(a['order_lexical']);key={'role':a['role'],'kind':a['kind'],'from':a['from'],'to':a['to'],'attributes':non_exempt}
  # XBRL 2.1 4.10 specifies XPath 1.0 number equality. Reject distinct exact
  # decimal orders which collide in that number space rather than guess at them.
  xpath_key=canonical([key,float(order).hex()]);prior=xpath_orders.get(xpath_key)
  if prior is not None and prior!=order:raise XBRLError('drs_effective_order_xpath_ambiguity_unsupported')
  xpath_orders[xpath_key]=order;key['order']={'numerator':str(order.numerator),'denominator':str(order.denominator)}
  groups.setdefault(canonical(key),[]).append(i)
 effective=[];resolution=[]
 for key,indexes in sorted(groups.items()):
  priority=max(arcs[i]['priority']for i in indexes);winners=[i for i in indexes if arcs[i]['priority']==priority]
  prohibited=any(arcs[i]['use']=='prohibited'for i in winners);chosen=None if prohibited else winners[0]
  resolution.append({'equivalence_sha256':digest(key.decode()),'arc_indexes':indexes,'max_priority':priority,'effective_arc_index':chosen,'status':'PROHIBITED_AT_MAX_PRIORITY'if prohibited else'EFFECTIVE'})
  if chosen is not None:effective.append(_project(arcs[chosen]))
 return effective,resolution


def corroborate_effective_cross_role(parsed,dts,documents,allow_observed,instance_uri):
 supplied=_originals(parsed,dts,documents,allow_observed,instance_uri)
 schema_sources=_schema_sources(supplied,dts['documents']);schemas=_validate_schema_sources(schema_sources,dts['documents'])
 arcs,refs=_read(parsed,dts,supplied,effective=True);_endpoint_sources(arcs,dts['concepts'],schemas);effective,resolution=_effective(arcs)
 records=_records(parsed,dts['concepts'],effective)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256')
 result['schema']='gig.sec.xbrl.dimensional_inline_set.v9'if parsed['schema']=='gig.sec.xbrl.inline_set.v1'else'gig.sec.xbrl.dimensional_instance.v9'
 result['dts_corroboration']['dimensional_validation']={'profile':PROFILE,'facts':records,'relationships':arcs,'role_references':refs,'schema_sources':schema_sources,'effective_relationships':effective,'resolution':resolution,'complete_drs_validation':False,'scope':SCOPE}
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('drs_effective_output_budget')
 result['canonical_sha256']=digest(result);return result


def validate_effective_cross_role_result(parsed):
 """Independently derive effective selection and all retained context claims.

The producer replays original XML; this retained-artifact consumer checks internal
source binding and semantics, and does not authenticate those XML bytes or issuer.
"""
 fail=lambda:XBRLError('xbrl_dimensional_result_contract')
 try:
  p=parsed['dts_corroboration']['dimensional_validation']
  if type(p)is not dict or set(p)!={'profile','facts','relationships','role_references','schema_sources','effective_relationships','resolution','complete_drs_validation','scope'}or p['profile']!=PROFILE or p['scope']!=SCOPE or p['complete_drs_validation']is not False or len(canonical(parsed))>MAX_OUTPUT:raise fail()
  effective,resolution=_effective(p['relationships'])
  receipts={'relationships':[_project(a)for a in p['relationships']],'role_references':p['role_references']}
  concepts,_=_validate_receipts(parsed,receipts)
  schemas=_validate_schema_sources(p['schema_sources'],parsed['dts_corroboration']['documents']);_endpoint_sources(p['relationships'],concepts,schemas)
  if p['relationships']!=sorted(p['relationships'],key=lambda a:(a['source_uri'],a['arc_node_ordinal'])):raise fail()
  if canonical(effective)!=canonical(p['effective_relationships'])or canonical(resolution)!=canonical(p['resolution'])or canonical(_records(parsed,concepts,effective))!=canonical(p['facts']):raise fail()
 except (XBRLError,KeyError,TypeError,ValueError,OverflowError):raise fail()from None
