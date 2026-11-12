"""Explicit bounded default-target inline-XBRL1.1 document sets.

Preserves ordered text,original document identities and continuation lineage.
Only documented narrow numeric transformation subsets are admitted. This is not
HTML rendering,full inline-XBRL/schema validation or complete financial statements.
"""
import copy,re
from .xbrl_instance import X,L,I,XL,MAX_BYTES,MAX_FACTS,Node,tag,parse_xml,qname,identifier,validate_manifest,_interpret_instance,digest,canonical,XBRLError
from .inline_xbrl import IX,HTML,transformed
from .xbrl_dts import uri
from . import sec

MAX_DOCUMENTS=8;MAX_SET_BYTES=8*1024*1024;MAX_NODES=60000;MAX_VALUE=16384;MAX_CHAIN=32;MAX_OUTPUT=8*1024*1024
TRANSFORMS='http://www.xbrl.org/inlineXBRL/transformation/2015-02-26'
PASSIVE={'span','div','p','b','i','strong','em','small','sup','sub','br','table','thead','tbody','tfoot','tr','td','th','ul','ol','li','a'}

def _numeric(text,format_name,scale,sign):
 value=text.strip(' \t\r\n')
 if format_name is not None:
  if format_name==tag(TRANSFORMS,'numdotdecimal'):
   if not re.fullmatch(r'(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?',value):raise XBRLError('inline_set_transform_lexical_subset')
   value=value.replace(',','')
  elif format_name==tag(TRANSFORMS,'numcommadecimal'):
   if not re.fullmatch(r'(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)(?:,[0-9]+)?',value):raise XBRLError('inline_set_transform_lexical_subset')
   value=value.replace('.','').replace(',','.')
  else:raise XBRLError('inline_set_transform_unsupported')
 if not re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?',value):raise XBRLError('inline_set_plain_numeric_subset')
 return transformed(value,scale,sign,max_scale=18)

def _text(node,*,nonnumeric):
 parts=[];size=0;pending=list(reversed(node.content or node.parts))
 while pending:
  part=pending.pop()
  if isinstance(part,str):
   size+=len(part)
   if size>MAX_VALUE:raise XBRLError('inline_set_value_budget')
   parts.append(part);continue
  if part.name==tag(IX,'exclude'):
   if not nonnumeric:raise XBRLError('inline_set_numeric_exclude_unsupported')
   continue
  if not part.name.startswith('{'+HTML+'}')or part.name.split('}',1)[1]not in PASSIVE:raise XBRLError('inline_set_value_markup_unsupported')
  pending.extend(reversed(part.content or part.parts))
 return ''.join(parts)

def parse_document_set(documents,concepts,*,allow_observed=False):
 if type(documents)is not list or not 1<=len(documents)<=MAX_DOCUMENTS:raise XBRLError('inline_set_document_budget')
 supplied={};total=0
 # Gate every supplied original before parsing any XML in the set.
 for entry in documents:
  if type(entry)is not dict or set(entry)!={'uri','raw','manifest'}or type(entry['raw'])is not bytes or not 1<=len(entry['raw'])<=MAX_BYTES:raise XBRLError('inline_set_document_contract')
  key=uri(entry['uri']);total+=len(entry['raw'])
  if total>MAX_SET_BYTES:raise XBRLError('inline_set_byte_budget')
  if key in supplied:raise XBRLError('inline_set_duplicate_document')
  source=validate_manifest(entry['raw'],entry['manifest'],allow_observed)
  if source['origin']=='OBSERVED_OFFICIAL_RESPONSE'and source['source_url']!=key:raise XBRLError('inline_set_source_uri')
  supplied[key]={'raw':entry['raw'],'source':source}
 ordered=sorted(supplied);sources=[{'uri':key,'source':supplied[key]['source']}for key in ordered]
 def identity(s):return(s['issuer_cik'],s['accession'],s['form'],s['filed'],None if s['accepted_at']is None else sec.acceptance_ns(s['accepted_at']),s['amends_accession'],s['origin'])
 first=sources[0]['source']
 if any(identity(row['source'])!=identity(first)for row in sources):raise XBRLError('inline_set_filing_scope')
 set_sha=digest(sources);nodes=[];ids={};continuations={};fact_nodes=[];resources=[];refs=[];locations={}
 for key in ordered:
  root=parse_xml(supplied[key]['raw'])
  if root.name!=tag(HTML,'html'):raise XBRLError('inline_set_xhtml_profile')
  pending=[(root,False)];ordinal=0
  while pending:
   node,in_value=pending.pop();location={'document_uri':key,'document_sha256':supplied[key]['source']['source_sha256'],'node_ordinal':ordinal,'id':node.attrs.get('id')};ordinal+=1;nodes.append((node,location))
   locations[id(node)]=location
   if len(nodes)>MAX_NODES:raise XBRLError('inline_set_node_budget')
   if '{http://www.w3.org/XML/1998/namespace}base'in node.attrs:raise XBRLError('inline_set_xml_base_unsupported')
   if node.name.startswith('{http://www.xbrl.org/2008/inlineXBRL}'):raise XBRLError('inline_set_version_unsupported')
   if 'id'in node.attrs:
    id_=identifier(node.attrs['id'])
    if id_ in ids:raise XBRLError('inline_set_duplicate_id')
    ids[id_]=node
   is_ix=node.name.startswith('{'+IX+'}');kind=node.name.split('}',1)[1]if is_ix else None
   if is_ix and kind not in('header','resources','references','hidden','nonFraction','nonNumeric','continuation','exclude'):raise XBRLError('inline_set_feature_unsupported')
   if is_ix and node.attrs.get('target',''):raise XBRLError('inline_set_named_target_unsupported')
   value=kind in('nonFraction','nonNumeric','continuation')
   if value and in_value:raise XBRLError('inline_set_nested_fact_or_continuation_unsupported')
   if kind=='exclude'and not in_value:raise XBRLError('inline_set_exclude_without_value')
   if kind=='resources':
    if node.text().strip()or any(n.name not in(tag(X,'context'),tag(X,'unit'))for n in node.children):raise XBRLError('inline_set_resource_profile')
    resources.extend(node.children)
   elif kind=='references':
    for n in node.children:
     href=n.attrs.get(tag(XL,'href'))
     if n.name!=tag(L,'schemaRef')or n.attrs.get(tag(XL,'type'))!='simple'or type(href)is not str:raise XBRLError('inline_set_reference_profile')
     from urllib.parse import urljoin
     target=uri(urljoin(key,href));refs.append({'uri':target,'document_uri':key,'document_sha256':location['document_sha256']})
     if len(refs)>32:raise XBRLError('inline_set_schema_reference_budget')
   elif kind=='continuation':
    if 'id'not in node.attrs or set(node.attrs)-{'id','continuedAt'}:raise XBRLError('inline_set_continuation_contract')
    continuations[node.attrs['id']]=(node,location)
   elif kind in('nonFraction','nonNumeric'):
    if len(fact_nodes)>=MAX_FACTS:raise XBRLError('inline_set_fact_budget')
    fact_nodes.append((node,location,kind))
   pending.extend((child,in_value or value)for child in reversed(node.children))
 if not resources or not fact_nodes:raise XBRLError('inline_set_resources_and_facts_required')
 virtual=Node(tag(X,'xbrl'),{},());virtual.children.extend(resources);traces=[];used=set();trace_bytes=0
 for node,location,kind in fact_nodes:
  nonnumeric=kind=='nonNumeric';nil=node.attrs.get(tag(I,'nil'),'false')
  if any(k in node.attrs for k in('tupleRef','tupleID','order'))or node.attrs.get('escape','false')not in('false','0'):raise XBRLError('inline_set_fact_feature_unsupported')
  if not nonnumeric and 'continuedAt'in node.attrs:raise XBRLError('inline_set_numeric_continuation_unsupported')
  if nil in('true','1')and 'continuedAt'in node.attrs:raise XBRLError('inline_set_nil_continuation')
  text=_text(node,nonnumeric=nonnumeric);segments=[location];next_id=node.attrs.get('continuedAt');chain=set()
  while next_id is not None:
   identifier(next_id)
   if len(chain)>=MAX_CHAIN:raise XBRLError('inline_set_chain_budget')
   if next_id in chain:raise XBRLError('inline_set_continuation_cycle')
   if next_id in used:raise XBRLError('inline_set_shared_continuation_unsupported')
   if next_id not in continuations:raise XBRLError('inline_set_continuation_missing_or_wrong_kind')
   chain.add(next_id);used.add(next_id);part,part_location=continuations[next_id];text+=_text(part,nonnumeric=True);segments.append(part_location)
   if len(text)>MAX_VALUE:raise XBRLError('inline_set_value_budget')
   next_id=part.attrs.get('continuedAt')
  format_name=qname(node.attrs['format'],node)if 'format'in node.attrs else None;scale=node.attrs.get('scale','0');sign=node.attrs.get('sign')
  name=qname(node.attrs.get('name',''),node)
  if nonnumeric and(name in concepts or any(k in node.attrs for k in('unitRef','decimals','precision'))):raise XBRLError('inline_set_fact_kind_conflict')
  if not nonnumeric and 'unitRef'not in node.attrs:raise XBRLError('inline_set_numeric_unit_required')
  if nonnumeric or nil in('true','1'):
   if any(k in node.attrs for k in('scale','sign','format')):raise XBRLError('inline_set_nonnumeric_or_nil_transform')
   value=text
  else:value=_numeric(text,format_name,scale,sign)
  attrs={k:v for k,v in node.attrs.items()if k in('contextRef','unitRef','decimals','precision','id',tag(I,'nil'))}
  virtual.children.append(Node(name,attrs,node.ns,parts=[value],length=len(value)))
  trace={'kind':kind,'expanded_concept':name,'segments':segments,'extracted_text':text,'transformed_lexical':value,'format':format_name,'scale':scale if not nonnumeric else None,'sign':sign}
  trace_bytes+=len(canonical(trace))
  if trace_bytes>MAX_OUTPUT:raise XBRLError('inline_set_trace_budget')
  traces.append(trace)
 if used!=set(continuations):raise XBRLError('inline_set_unreferenced_continuation_unsupported')
 source=copy.deepcopy(first);source.update(source_sha256=set_sha,source_url=None,received_at=None,permission_reference_sha256=None,source_hash_kind='DERIVED_DOCUMENT_SET_MANIFEST_V1')
 result=_interpret_instance(virtual,source,concepts);result.pop('canonical_sha256');result['schema']='gig.sec.xbrl.inline_set.v1';mapping={}
 for fact,trace in zip(result['facts'],traces):
  old=fact.pop('source_fact_id');fact['inline_source_segments']=trace['segments'];fact['source_fact_id']=digest({'document_set_sha256':set_sha,'fact':fact});mapping[old]=fact['source_fact_id']
 for conflict in result['conflicts']:conflict['source_fact_ids']=[mapping[v]for v in conflict['source_fact_ids']]
 result['document_set']={'schema':'gig.sec.xbrl.document_set.v1','sha256':set_sha,'documents':sources,'resource_sources':[{'kind':r.name,**locations[id(r)]}for r in resources],'schema_references':refs,'profile':'DEFAULT_TARGET_IX11_SET_V1','facts':traces,'receipt_authority':'Original per-document receipts retained;aggregate receipt unknown','limitations':['Narrow2015numeric transforms only','No named targets,tuples,escaped HTML,nested facts or full DTS/schema validation','No inferred source coverage or complete financial statements']}
 result['completeness']='BOUNDED_SUPPLIED_INLINE_SET_NOT_COMPLETE_SCHEMA_DRS_STATEMENTS_OR_HISTORY'
 if len(canonical(result))>MAX_OUTPUT:raise XBRLError('inline_set_output_budget')
 result['canonical_sha256']=digest(result);return result
