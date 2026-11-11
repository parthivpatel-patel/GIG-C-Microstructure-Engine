"""Bounded SEC XBRL 2.1 *instance* profile. No DTS/network fetch or inline HTML.

Expanded concepts,contexts,dimensions,units and exact lexical values are retained.
A supplied concept profile is an explicit input contract,not proof of taxonomy or
historical completeness. Unknown concepts never become selected financial facts.
"""
import copy,hashlib,json,re
from dataclasses import dataclass,field
from decimal import Decimal
from xml.parsers import expat
from . import sec

X='http://www.xbrl.org/2003/instance';L='http://www.xbrl.org/2003/linkbase';D='http://xbrl.org/2006/xbrldi';I='http://www.w3.org/2001/XMLSchema-instance';XL='http://www.w3.org/1999/xlink';ISO='http://www.xbrl.org/2003/iso4217'
MAX_BYTES=2*1024*1024;MAX_FACTS=4096;MAX_CONTEXTS=512;MAX_UNITS=128
class XBRLError(ValueError):pass

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(v):return hashlib.sha256(canonical(v)).hexdigest()
def tag(ns,name):return '{'+ns+'}'+name

def name(value):
 if '}'not in value:return value
 uri,local=value.split('}',1);return tag(uri,local)
def identifier(v):
 if type(v)is not str or not re.fullmatch('[A-Za-z_][A-Za-z0-9_.:-]{0,127}',v):raise XBRLError('xbrl_identifier_profile')
 return v
@dataclass(slots=True)
class Node:
 name:str;attrs:dict;ns:tuple;children:list=field(default_factory=list);parts:list=field(default_factory=list);length:int=0
 def text(self):return ''.join(self.parts)

def parse_xml(raw):
 if type(raw)is not bytes or not 1<=len(raw)<=MAX_BYTES:raise XBRLError('xbrl_input_budget')

 try:raw.decode('utf-8')
 except UnicodeError:raise XBRLError('xbrl_encoding_profile')from None
 if b'\x00'in raw:raise XBRLError('xbrl_encoding_profile')
 stack=[];roots=[];active={};prior={};snapshot=();nodes=declarations=0
 parser=expat.ParserCreate(namespace_separator='}');parser.buffer_text=True
 def reject(*args):raise XBRLError('xbrl_external_or_dtd_disabled')
 def namespace(prefix,uri):
  nonlocal declarations,snapshot
  declarations+=1
  if declarations>256 or len(active)>=32 and prefix not in active or len(uri or '')>512:raise XBRLError('xbrl_namespace_budget')
  prior.setdefault(prefix,[]).append(active.get(prefix));active[prefix]=uri or '';snapshot=tuple(sorted(active.items(),key=lambda x:x[0]or''))
 def end_namespace(prefix):
  nonlocal snapshot
  old=prior[prefix].pop()
  if old is None:active.pop(prefix,None)
  else:active[prefix]=old
  snapshot=tuple(sorted(active.items(),key=lambda x:x[0]or''))
 def start(value,attrs):
  nonlocal nodes
  nodes+=1
  if nodes>30000 or len(stack)>=32 or len(attrs)>24 or any(len(k)>640 or len(v)>1024 for k,v in attrs.items()):raise XBRLError('xbrl_structure_budget')
  if value.startswith('http://www.w3.org/2001/XInclude}'):raise XBRLError('xbrl_xinclude_disabled')
  n=Node(name(value),{name(k):v for k,v in attrs.items()},snapshot)
  if stack:stack[-1].children.append(n)
  else:roots.append(n)
  stack.append(n)
 def text(value):
  if not stack:return
  n=stack[-1]
  if len(stack)==1 and not value.strip():return
  n.length+=len(value)
  if n.length>16384:raise XBRLError('xbrl_text_budget')
  n.parts.append(value)
 parser.StartNamespaceDeclHandler=namespace;parser.EndNamespaceDeclHandler=end_namespace;parser.StartElementHandler=start;parser.EndElementHandler=lambda _:stack.pop();parser.CharacterDataHandler=text
 parser.StartDoctypeDeclHandler=reject;parser.EntityDeclHandler=reject;parser.ExternalEntityRefHandler=reject;parser.ProcessingInstructionHandler=reject;parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
 def declaration(version,encoding,standalone):
  if version!='1.0'or encoding and encoding.upper().replace('-','')!='UTF8':raise XBRLError('xbrl_encoding_profile')
 parser.XmlDeclHandler=declaration
 try:
  for offset in range(0,len(raw),4096):parser.Parse(raw[offset:offset+4096],False)
  parser.Parse(b'',True)
 except XBRLError:raise
 except (expat.ExpatError,UnicodeError,ValueError):raise XBRLError('xbrl_xml_malformed')from None
 if len(roots)!=1:raise XBRLError('xbrl_xml_root')
 return roots[0]

def qname(value,node):
 value=value.strip();parts=value.split(':')
 if len(parts)>2 or any(not re.fullmatch('[A-Za-z_][A-Za-z0-9_.-]{0,127}',p)for p in parts):raise XBRLError('xbrl_qname_profile')
 ns=dict(node.ns);prefix=parts[0]if len(parts)==2 else None
 if prefix not in ns:raise XBRLError('xbrl_unbound_qname')
 return tag(ns[prefix],parts[-1])

def children(node,value):return [n for n in node.children if n.name==value]
def one(node,value):
 values=children(node,value)
 if len(values)!=1:raise XBRLError('xbrl_required_structure')
 return values[0]
def tree(node):return {'name':node.name,'attributes':node.attrs,'namespaces':{k or'':v for k,v in node.ns},'text':node.text(),'children':[tree(n)for n in node.children]}

def context(node,cik):
 entity=one(node,tag(X,'entity'));ident=one(entity,tag(X,'identifier'));wire=ident.text().strip()
 if ident.children:raise XBRLError('xbrl_identifier_structure')
 if ident.attrs.get('scheme')!='http://www.sec.gov/CIK'or not re.fullmatch('[0-9]{1,10}',wire)or wire.zfill(10)!=cik:raise XBRLError('xbrl_entity_scope')
 period=one(node,tag(X,'period'));p=period.children
 if any(n.children for n in p):raise XBRLError('xbrl_period_profile')
 if len(p)==1 and p[0].name==tag(X,'instant'):span={'kind':'instant','start':None,'end':sec.date(p[0].text().strip())}
 elif len(p)==2 and {n.name for n in p}=={tag(X,'startDate'),tag(X,'endDate')}:
  start=sec.date(one(period,tag(X,'startDate')).text().strip());end=sec.date(one(period,tag(X,'endDate')).text().strip())
  if start>end:raise XBRLError('xbrl_period_order')
  span={'kind':'duration','start':start,'end':end}
 elif len(p)==1 and p[0].name==tag(X,'forever'):span={'kind':'forever','start':None,'end':None}
 else:raise XBRLError('xbrl_period_profile')
 dims=[];opaque=[tree(n)for n in node.children if n.name not in (tag(X,'entity'),tag(X,'period'),tag(X,'scenario'))]+[tree(n)for n in entity.children if n.name not in (tag(X,'identifier'),tag(X,'segment'))];seen=set()
 containers=children(one(node,tag(X,'entity')),tag(X,'segment'))+children(node,tag(X,'scenario'))
 for container in containers:
  for child in container.children:
   if child.name in (tag(D,'explicitMember'),tag(D,'typedMember')):
    dimension=qname(child.attrs.get('dimension',''),child)
    if dimension in seen:raise XBRLError('xbrl_duplicate_dimension')
    seen.add(dimension)
    if child.name==tag(D,'explicitMember'):
     if child.children:raise XBRLError('xbrl_explicit_member_structure')
     member={'dimension':dimension,'kind':'explicit','member':qname(child.text(),child)}
    else:
     if len(child.children)!=1:raise XBRLError('xbrl_typed_member_structure')
     member={'dimension':dimension,'kind':'typed','member':tree(child.children[0])}
    dims.append(member)
   else:opaque.append(tree(child))
 if len(dims)>32 or len(opaque)>32:raise XBRLError('xbrl_dimension_budget')
 core={'issuer_cik':cik,'period':span,'dimensions':sorted(dims,key=lambda d:d['dimension']),'opaque_segment':opaque}
 return {**core,'identifier_lexical':wire,'semantic_sha256':digest(core)}

def unit(node):
 if children(node,tag(X,'divide')):
  d=one(node,tag(X,'divide'))
  if len(node.children)!=1 or len(d.children)!=2:raise XBRLError('xbrl_unit_structure')
  numerator=one(d,tag(X,'unitNumerator'));denominator=one(d,tag(X,'unitDenominator'));num=numerator.children;den=denominator.children
  if not den:raise XBRLError('xbrl_unit_profile')
 else:num=node.children;den=[]
 if not 1<=len(num)<=8 or len(den)>8 or any(n.name!=tag(X,'measure')or n.children for n in num+den):raise XBRLError('xbrl_unit_profile')
 core={'numerator':sorted(qname(n.text(),n)for n in num),'denominator':sorted(qname(n.text(),n)for n in den)}
 return {**core,'semantic_sha256':digest(core)}

def validate_manifest(raw,manifest,allow_observed):
 fields={'issuer_cik','accession','form','filed','accepted_at','received_at','origin','source_sha256','source_url','amends_accession','permission_reference'}
 if type(manifest)is not dict or set(manifest)!=fields:raise XBRLError('xbrl_manifest_fields')
 if type(manifest['issuer_cik'])is not str or not re.fullmatch('[0-9]{10}',manifest['issuer_cik'])or int(manifest['issuer_cik'])==0:raise XBRLError('xbrl_issuer')
 if type(manifest['accession'])is not str or not re.fullmatch('[0-9]{10}-[0-9]{2}-[0-9]{6}',manifest['accession'])or manifest['form']not in ('10-K','10-K/A','10-Q','10-Q/A'):raise XBRLError('xbrl_filing')
 sec.date(manifest['filed'])
 for k in ('accepted_at','received_at'):
  if manifest[k]is not None:sec.acceptance_ns(manifest[k])
 amends=manifest['amends_accession']
 if amends is not None and (not manifest['form'].endswith('/A')or type(amends)is not str or not re.fullmatch('[0-9]{10}-[0-9]{2}-[0-9]{6}',amends)or amends==manifest['accession']):raise XBRLError('xbrl_amendment_identity')
 if type(allow_observed)is not bool or manifest['origin']not in ('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'):raise XBRLError('xbrl_origin')
 if manifest['origin']=='OBSERVED_OFFICIAL_RESPONSE'and(not allow_observed or type(manifest['permission_reference'])is not str or not 1<=len(manifest['permission_reference'])<=256):raise XBRLError('xbrl_observed_processing_not_approved')
 if manifest['source_url']is not None:
  if type(manifest['source_url'])is not str or len(manifest['source_url'])>512 or not re.fullmatch(r'https://www\.sec\.gov/Archives/edgar/data/[0-9]+/[0-9]{18}/[A-Za-z0-9_.-]{1,160}',manifest['source_url']):raise XBRLError('xbrl_source_url')
 if manifest['source_url']is not None:
  parts=manifest['source_url'].split('/')
  if int(parts[-3])!=int(manifest['issuer_cik'])or parts[-2]!=manifest['accession'].replace('-','')or '..'in parts[-1]:raise XBRLError('xbrl_source_identity')
 if manifest['origin']=='OBSERVED_OFFICIAL_RESPONSE'and manifest['source_url']is None:raise XBRLError('xbrl_observed_source_url_required')
 if hashlib.sha256(raw).hexdigest()!=manifest['source_sha256']:raise XBRLError('xbrl_source_digest')
 result=copy.deepcopy(manifest);reference=result.pop('permission_reference')
 if reference is not None and(type(reference)is not str or len(reference)>256):raise XBRLError('xbrl_permission_reference')
 result['permission_reference_sha256']=hashlib.sha256(reference.encode()).hexdigest()if reference is not None else None
 return result

def selected_concepts(gaap_namespace):
 if type(gaap_namespace)is not str or not re.fullmatch(r'https?://fasb\.org/us-gaap/[0-9]{4}',gaap_namespace):raise XBRLError('xbrl_taxonomy_profile')
 instant={'assets','liabilities','equity','cash','assets_current','liabilities_current','short_term_borrowings','long_term_debt_current','long_term_debt_noncurrent'};out={}
 for metric,tags in sec.TAGS.items():
  for concept in tags:
   measure={'USD':[tag(ISO,'USD')],'USD/shares':[tag(ISO,'USD')],'shares':[tag(X,'shares')]}[sec.UNITS.get(metric,'USD')]
   out[tag(gaap_namespace,concept)]={'kind':'numeric','period_type':'instant'if metric in instant else'duration','numerator':measure,'denominator':[tag(X,'shares')]if sec.UNITS.get(metric)=='USD/shares'else[],'metric':metric,'local_name':concept}
 return out

def parse_instance(raw,manifest,concepts,*,allow_observed=False):
 if type(raw)is not bytes or not 1<=len(raw)<=MAX_BYTES:raise XBRLError('xbrl_input_budget')
 source=validate_manifest(raw,manifest,allow_observed)
 return _interpret_instance(parse_xml(raw),source,concepts)

def _interpret_instance(root,source,concepts):
 if type(concepts)is not dict or len(concepts)>512:raise XBRLError('xbrl_concept_budget')
 for key,spec in concepts.items():
  if type(key)is not str or not re.fullmatch(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}',key)or type(spec)is not dict or set(spec)!={'kind','period_type','numerator','denominator','metric','local_name'}or spec['kind']!='numeric'or spec['period_type']not in ('instant','duration')or spec['metric']not in sec.TAGS or spec['local_name']not in sec.TAGS[spec['metric']]:raise XBRLError('xbrl_concept_profile')
  for field_name in ('numerator','denominator'):
   values=spec[field_name]
   if type(values)is not list or len(values)>8 or field_name=='numerator'and not values or any(type(v)is not str or not re.fullmatch(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}',v)for v in values):raise XBRLError('xbrl_concept_unit_profile')
  if key.split('}',1)[1]!=spec['local_name']:raise XBRLError('xbrl_concept_name_profile')
  ns=key[1:].split('}',1)[0]
  if re.fullmatch(r'https?://fasb\.org/us-gaap/[0-9]{4}',ns)and selected_concepts(ns).get(key)!=spec:raise XBRLError('xbrl_selected_concept_contract')
 if root.text().strip():raise XBRLError('xbrl_root_text')
 if root.name!=tag(X,'xbrl'):raise XBRLError('xbrl_instance_only_inline_unsupported')
 contexts={};units={};facts=[];unsupported=[];schema_refs=[];ids=set()
 for node in root.children:
  if node.name in (tag(X,'context'),tag(X,'unit')):
   key=identifier(node.attrs.get('id'))
   if key in ids:raise XBRLError('xbrl_duplicate_id')
   ids.add(key)
   if node.name==tag(X,'context'):
    if len(contexts)>=MAX_CONTEXTS:raise XBRLError('xbrl_context_budget')
    contexts[key]=context(node,source['issuer_cik'])
   else:
    if len(units)>=MAX_UNITS:raise XBRLError('xbrl_unit_budget')
    units[key]=unit(node)
  elif node.name==tag(L,'schemaRef'):
   href=node.attrs.get(tag(XL,'href'))
   if type(href)is not str or len(href)>512:raise XBRLError('xbrl_schema_reference')
   schema_refs.append({'href':href,'fetched':False})
   if len(schema_refs)>32:raise XBRLError('xbrl_schema_reference_budget')
 for ordinal,node in enumerate(root.children):
  if node.name in (tag(X,'context'),tag(X,'unit'),tag(L,'schemaRef')):continue
  if len(facts)+len(unsupported)>=MAX_FACTS:raise XBRLError('xbrl_fact_budget')
  ref=node.attrs.get('contextRef')
  if ref is None:
   unsupported.append({'ordinal':ordinal,'name':node.name,'reason':'UNSUPPORTED_TUPLE_OR_LINKBASE_NODE','tree':tree(node)});continue
  if ref not in contexts:raise XBRLError('xbrl_unknown_context')
  fact_id=node.attrs.get('id')
  if fact_id is not None:
   identifier(fact_id)
   if fact_id in ids:raise XBRLError('xbrl_duplicate_id')
   ids.add(fact_id)
  if node.children:raise XBRLError('xbrl_simple_fact_profile')
  ctx=contexts[ref];unit_ref=node.attrs.get('unitRef')
  if unit_ref is not None and unit_ref not in units:raise XBRLError('xbrl_unknown_unit')
  nil=node.attrs.get(tag(I,'nil'),'false')
  if nil not in ('true','false','1','0'):raise XBRLError('xbrl_nil')
  nil=nil in ('true','1');lexical=node.text();spec=concepts.get(node.name);admission='UNVERIFIED_CONCEPT';value=None;nil_status='NIL_REPORTED_UNAVAILABLE'if nil else None
  if nil and lexical.strip():raise XBRLError('xbrl_nil_with_value')
  decimals=node.attrs.get('decimals');precision=node.attrs.get('precision')
  if decimals is not None and precision is not None:raise XBRLError('xbrl_precision_conflict')
  if decimals is not None and not re.fullmatch(r'INF|-?(?:0|[1-9][0-9]{0,2})',decimals):raise XBRLError('xbrl_decimals')
  if precision is not None and not re.fullmatch(r'INF|[1-9][0-9]{0,2}',precision):raise XBRLError('xbrl_precision')
  if spec:
   if unit_ref is None:raise XBRLError('xbrl_numeric_unit_required')
   if not nil:
    if not re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?',lexical.strip()):raise XBRLError('xbrl_numeric_profile')
    value=sec.exact(Decimal(lexical.strip()))
   u=units[unit_ref]
   admission='ADMITTED_PROFILE'if ctx['period']['kind']==spec['period_type']and u['numerator']==sorted(spec['numerator'])and u['denominator']==sorted(spec['denominator'])else'PERIOD_OR_UNIT_MISMATCH'
  core={'ordinal':ordinal,'concept':node.name,'context_ref':ref,'context_sha256':ctx['semantic_sha256'],'unit_ref':unit_ref,'unit_sha256':units[unit_ref]['semantic_sha256']if unit_ref else None,'lexical_value':lexical,'value':value,'nil':nil,'nil_status':nil_status,'decimals':decimals,'precision':precision,'attributes':node.attrs,'admission':admission,'metric':spec['metric']if spec else None,'local_name':spec['local_name']if spec else None}
  core['source_fact_id']=digest({'source_sha256':source['source_sha256'],'fact':core});facts.append(core)
 groups={}
 for row in facts:
  if row['admission']=='ADMITTED_PROFILE':groups.setdefault((row['concept'],row['context_sha256'],row['unit_sha256']),[]).append(row)
 conflicts=[];duplicates=0
 for key,rows in groups.items():
  values={(r['nil'],None if r['nil']else Decimal(r['value']))for r in rows}
  if len(values)>1:
   conflicts.append({'semantic_key_sha256':digest(key),'source_fact_ids':[r['source_fact_id']for r in rows],'policy':'EXACT_VALUE_CONFLICT_NOT_ACCURACY_INTERVAL_INFERENCE'})
   for row in rows:row['admission']='CONFLICTED_EXACT_VALUES'
  else:duplicates+=len(rows)-1
 result={'schema':'gig.sec.xbrl.instance.v1','source':source,'concept_profile_sha256':digest(concepts),'contexts':contexts,'units':units,'facts':facts,'schema_references':schema_refs,'unsupported_nodes':unsupported,'conflicts':conflicts,'consistent_duplicate_facts':duplicates,'completeness':'BOUNDED_INSTANCE_PROFILE_NOT_COMPLETE_DTS_INLINE_PRESENTATION_OR_HISTORY','limits':{'input_bytes':MAX_BYTES,'facts':MAX_FACTS,'contexts':MAX_CONTEXTS,'units':MAX_UNITS},'taxonomy_authority':'Explicit caller profile,not automatically verified DTS;unknown concepts preserved,never selected','origin':source['origin']}
 if len(canonical(result))>8*1024*1024:raise XBRLError('xbrl_output_budget')
 result['canonical_sha256']=digest(result);return result

def selected_financials(parsed):
 if type(parsed)is not dict or parsed.get('schema')!='gig.sec.xbrl.instance.v1'or type(parsed.get('facts'))is not list or len(parsed['facts'])>MAX_FACTS or type(parsed.get('contexts'))is not dict or len(parsed['contexts'])>MAX_CONTEXTS:raise XBRLError('xbrl_parsed_contract')
 core={k:v for k,v in parsed.items()if k!='canonical_sha256'}
 if digest(core)!=parsed.get('canonical_sha256'):raise XBRLError('xbrl_parsed_digest')
 source=parsed['source'];namespace={};refs={};concept_names={};skipped={'unverified_or_conflicting':0,'dimensioned_or_opaque':0,'nil':0,'unsupported_period':0,'unsupported_taxonomy_namespace':0}
 namespaces={r['concept'].split('}',1)[0]for r in parsed['facts']if r['admission']=='ADMITTED_PROFILE'and re.fullmatch(r'\{https?://fasb\.org/us-gaap/[0-9]{4}\}[A-Za-z0-9_]+',r['concept'])}
 if len(namespaces)>1:raise XBRLError('xbrl_multiple_taxonomy_versions_for_selection')
 for row in parsed['facts']:
  if not re.fullmatch(r'\{https?://fasb\.org/us-gaap/[0-9]{4}\}[A-Za-z0-9_]+',row['concept']):skipped['unsupported_taxonomy_namespace']+=1;continue
  if row['admission']!='ADMITTED_PROFILE':skipped['unverified_or_conflicting']+=1;continue
  context=parsed['contexts'][row['context_ref']]
  if context['dimensions']or context['opaque_segment']:skipped['dimensioned_or_opaque']+=1;continue
  if row['nil']:skipped['nil']+=1;continue
  period=context['period']
  if period['end']is None:skipped['unsupported_period']+=1;continue
  record={'val':Decimal(row['value']),'end':period['end'],'filed':source['filed'],'form':source['form'],'accn':source['accession']}
  if period['start']is not None:record['start']=period['start']
  unit_name=sec.UNITS.get(row['metric'],'USD');values=namespace.setdefault(row['local_name'],{'units':{}})['units'].setdefault(unit_name,[])
  key=(row['local_name'],period['start'],period['end'],unit_name)
  concept_names[key]=row['concept']
  refs.setdefault(key,[]).append(row['source_fact_id'])
  if not any(Decimal(r['val'])==record['val']and r.get('start')==record.get('start')and r['end']==record['end']for r in values):values.append(record)
 result=sec.facts({'cik':source['issuer_cik'],'facts':{'us-gaap':namespace}},source['issuer_cik'],source['filed'])
 for collection in (result['history'],result['revision_history']):
  for rows in collection.values():
   for row in rows:
    key=(row['concept'],row['start'],row['end'],row['unit']);ids=refs[key];row['source_xml_fact_ids']=ids;row['source_xbrl_concept']=concept_names[key];row['source_instance_sha256']=source['source_sha256'];row['source_fact_id']=digest({k:v for k,v in row.items()if k!='source_fact_id'})
 result['xbrl_coverage']={'excluded':skipped,'instance_sha256':parsed['canonical_sha256'],'completeness':parsed['completeness'],'filing_fiscal_metadata':'No fiscal-year/quarter inferred from calendar dates;reported context start/end and duration remain authoritative','original_received_at':source['received_at']}
 return result
