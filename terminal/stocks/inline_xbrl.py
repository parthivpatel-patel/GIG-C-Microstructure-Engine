"""Strict offline inline-XBRL1.1 subset:plain nonFraction/nonNumeric,exact scale.

No transformation registry,continuation,tuple,HTML-repair,network or imputation.
Unsupported financial semantics reject the entire instance before publication.
"""
import re
from decimal import Decimal
from .xbrl_instance import X,L,I,MAX_BYTES,Node,tag,parse_xml,qname,validate_manifest,_interpret_instance,digest,XBRLError
IX='http://www.xbrl.org/2013/inlineXBRL';HTML='http://www.w3.org/1999/xhtml'

def transformed(text,scale,sign):
 if type(scale)is not str or not re.fullmatch('[+-]?[0-9]{1,2}',scale)or abs(int(scale))>6 or sign not in(None,'-'):raise XBRLError('inline_numeric_transform_profile')
 value=text.strip()
 if not re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?',value)or len(value)>64:raise XBRLError('inline_plain_numeric_profile')
 number=Decimal(value);negative,digits,exponent=number.as_tuple();exponent+=int(scale)
 if len(digits)+abs(exponent)+2>70:raise XBRLError('inline_numeric_budget')
 return format(Decimal((negative^(sign=='-'),digits,exponent)),'f')

def _interpret_inline(root,source,concepts):
 if root.name!=tag(HTML,'html'):raise XBRLError('inline_xhtml_profile')
 nodes=[];pending=[root]
 while pending:
  node=pending.pop();nodes.append(node);pending.extend(reversed(node.children))
  if '{http://www.w3.org/XML/1998/namespace}base'in node.attrs:raise XBRLError('inline_xml_base_unsupported')
  if node.name.startswith('{http://www.xbrl.org/2008/inlineXBRL}'):raise XBRLError('inline_version_unsupported')
 virtual=Node(tag(X,'xbrl'),{},());facts=[];resources=0;trace=[]
 for ordinal,node in enumerate(nodes):
  if node.name==tag(IX,'resources'):
   resources+=1
   if resources>1:raise XBRLError('inline_resource_targets_unsupported')
   for resource in node.children:
    if resource.name not in(tag(X,'context'),tag(X,'unit')):raise XBRLError('inline_resource_profile')
    virtual.children.append(resource)
  if node.name==tag(IX,'references'):
   if node.attrs.get('target',''):raise XBRLError('inline_named_target_unsupported')
   for reference in node.children:
    if reference.name!=tag(L,'schemaRef'):raise XBRLError('inline_reference_profile')
    virtual.children.append(reference)
  if not node.name.startswith('{'+IX+'}'):continue
  kind=node.name.split('}',1)[1]
  if kind not in('header','resources','references','hidden','nonFraction','nonNumeric'):raise XBRLError('inline_feature_unsupported')
  if kind not in('nonFraction','nonNumeric'):continue
  if node.children or any(k in node.attrs for k in('format','continuedAt','tupleRef','tupleID','order'))or node.attrs.get('target','')or node.attrs.get('escape','false')!='false':raise XBRLError('inline_fact_feature_unsupported')
  name=qname(node.attrs.get('name',''),node);nil=node.attrs.get(tag(I,'nil'),'false')
  attrs={k:v for k,v in node.attrs.items()if k in('contextRef','unitRef','decimals','precision','id',tag(I,'nil'))}
  lexical=node.text();scale=node.attrs.get('scale','0');sign=node.attrs.get('sign')
  if kind=='nonFraction'and nil not in('true','1'):value=transformed(lexical,scale,sign)
  else:
   if 'scale'in node.attrs or 'sign'in node.attrs:raise XBRLError('inline_nonnumeric_or_nil_transform')
   value=lexical
  fact=Node(name,attrs,node.ns,parts=[value],length=len(value));facts.append(fact)
  trace.append({'source_node_ordinal':ordinal,'source_inline_id':node.attrs.get('id'),'kind':kind,'expanded_concept':name,'original_lexical':lexical,'scale':scale if kind=='nonFraction'else None,'sign':sign,'transformed_lexical':value,'format':None})
 if not resources or not facts:raise XBRLError('inline_resources_and_facts_required')
 virtual.children.extend(facts);result=_interpret_instance(virtual,source,concepts)
 result['inline_profile']={'version':'PLAIN_IX11_V1','facts':trace,'source_sha256':source['source_sha256'],'limitations':['No transform registry,continuations,tuples,named targets or nested fact markup','XHTML XML only;no permissive HTML repair','Declared concept profile,not full DTS validation']}
 result['completeness']='BOUNDED_INLINE_PROFILE_NOT_COMPLETE_TRANSFORMS_DTS_OR_HISTORY';result.pop('canonical_sha256');result['canonical_sha256']=digest(result);return result

def parse_inline(raw,manifest,concepts,*,allow_observed=False):
 if type(raw)is not bytes or not 1<=len(raw)<=MAX_BYTES:raise XBRLError('xbrl_input_budget')
 source=validate_manifest(raw,manifest,allow_observed)
 return _interpret_inline(parse_xml(raw),source,concepts)
def parse_filing(raw,manifest,concepts,*,allow_observed=False):
 if type(raw)is not bytes or not 1<=len(raw)<=MAX_BYTES:raise XBRLError('xbrl_input_budget')
 source=validate_manifest(raw,manifest,allow_observed);root=parse_xml(raw)
 return _interpret_instance(root,source,concepts)if root.name==tag(X,'xbrl')else _interpret_inline(root,source,concepts)
