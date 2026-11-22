"""Bounded numeric value/facet corroboration for supplied taxonomy declarations.

This is not an XML Schema validator. It does not validate DRS, attributes,
complex content, arbitrary derived types or accounting meaning. Unknown selected
types fail closed only when this explicit profile is requested.
"""
import copy,re
from decimal import Decimal
from .xbrl_instance import X,ISO,tag,qname,digest,canonical,XBRLError

XS='http://www.w3.org/2001/XMLSchema'
PROFILE='NUMERIC_VALUE_FACETS_V1'
COMPLEX_PROFILE='NUMERIC_SIMPLE_CONTENT_V2'
WHITESPACE_PROFILE='NUMERIC_WHITESPACE_V3'
ENUMERATION_PROFILE='NUMERIC_ENUMERATION_V4'
RESTRICTION_PROFILE='NUMERIC_RESTRICTION_CONSTRAINTS_V5'
BOUNDS_PROFILE='NUMERIC_BOUND_RESTRICTIONS_V6'
PROFILES=(PROFILE,COMPLEX_PROFILE,WHITESPACE_PROFILE,ENUMERATION_PROFILE,RESTRICTION_PROFILE,BOUNDS_PROFILE)
MAX_OUTPUT_BYTES=8*1024*1024
FACETS={'minInclusive','maxInclusive','minExclusive','maxExclusive','totalDigits','fractionDigits'}
DECIMAL=re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)\Z')
INTEGER_BOUNDS={'integer':(None,None),'nonPositiveInteger':(None,0),'negativeInteger':(None,-1),
 'long':(-(2**63),2**63-1),'int':(-(2**31),2**31-1),'short':(-(2**15),2**15-1),'byte':(-128,127),
 'nonNegativeInteger':(0,None),'unsignedLong':(0,2**64-1),'unsignedInt':(0,2**32-1),
 'unsignedShort':(0,2**16-1),'unsignedByte':(0,255),'positiveInteger':(1,None)}

def declaration(node):
 """Retain a named restriction or an explicit reason it cannot be validated."""
 result={'base':None,'facets':[],'unsupported':[]}
 if node.text().strip()or set(node.attrs)-{'name','id'}:
  result['unsupported']=['TYPE_ATTRIBUTES_OR_TEXT_UNSUPPORTED'];return result
 body=[n for n in node.children if n.name!=tag(XS,'annotation')]
 if node.name==tag(XS,'complexType'):
  if len(body)!=1 or body[0].name!=tag(XS,'simpleContent')or body[0].text().strip()or set(body[0].attrs)-{'id'}:result['unsupported']=['COMPLEX_CONTENT_UNSUPPORTED'];return result
  content=[n for n in body[0].children if n.name!=tag(XS,'annotation')]
  if len(content)!=1 or content[0].name not in(tag(XS,'extension'),tag(XS,'restriction')):result['unsupported']=['SIMPLE_CONTENT_STRUCTURE_UNSUPPORTED'];return result
  restriction=content[0];result['derivation']='SIMPLE_CONTENT_EXTENSION'if restriction.name==tag(XS,'extension')else'SIMPLE_CONTENT_RESTRICTION'
 elif node.name==tag(XS,'simpleType')and len(body)==1 and body[0].name==tag(XS,'restriction'):restriction=body[0]
 else:result['unsupported']=['ONLY_NAMED_SIMPLE_RESTRICTIONS_SUPPORTED'];return result
 if restriction.text().strip()or set(restriction.attrs)-{'base','id'}or 'base'not in restriction.attrs:
  result['unsupported']=['RESTRICTION_STRUCTURE_UNSUPPORTED'];return result
 result['base']=qname(restriction.attrs['base'],restriction);seen=set()
 for n in restriction.children:
  if n.name==tag(XS,'annotation'):continue
  if result.get('derivation')=='SIMPLE_CONTENT_EXTENSION':result['unsupported'].append('EXTENSION_ATTRIBUTES_OR_CONTENT_UNSUPPORTED');continue
  kind=n.name.removeprefix('{'+XS+'}')
  if kind=='enumeration':
   # Multiple enumeration elements represent one value-space set. Keep each
   # source lexical, including value-equivalent alternatives, in source order.
   if n.children or n.text().strip()or set(n.attrs)-{'value','id'}:
    result['unsupported'].append('ENUMERATION_FACET_STRUCTURE_UNSUPPORTED');continue
   value=n.attrs.get('value')
   if type(value)is not str or len(value)>64 or not DECIMAL.fullmatch(value.strip(' \t\r\n')):raise XBRLError('dts_type_enumeration_lexical')
   result['facets'].append({'kind':kind,'value':value})
   if len(result['facets'])>16:raise XBRLError('dts_type_facet_budget')
   continue
  if kind=='whiteSpace':
   if n.children or n.text().strip()or set(n.attrs)-{'value','id','fixed'}or kind in seen or n.attrs.get('value')!='collapse'or n.attrs.get('fixed','false')not in('true','false','1','0'):
    result['unsupported'].append('WHITESPACE_FACET_UNSUPPORTED');continue
   seen.add(kind);result['facets'].append({'kind':kind,'value':'collapse','fixed':n.attrs.get('fixed','false')in('true','1')});continue
  if kind not in FACETS or n.children or n.text().strip()or set(n.attrs)-({'value','id','fixed'}if kind in('totalDigits','fractionDigits')else{'value','id'})or kind in seen:
   result['unsupported'].append('FACET_OR_STRUCTURE_UNSUPPORTED');continue
  seen.add(kind);value=n.attrs.get('value')
  if type(value)is not str or len(value)>64:raise XBRLError('dts_type_facet_budget')
  if kind in('totalDigits','fractionDigits'):
   if not re.fullmatch('[0-9]{1,2}',value)or not (1 if kind=='totalDigits'else 0)<=int(value)<=64:raise XBRLError('dts_type_digit_facet')
  elif not DECIMAL.fullmatch(value):raise XBRLError('dts_type_numeric_facet')
  facet={'kind':kind,'value':value}
  if 'fixed'in n.attrs:
   if n.attrs['fixed']not in('true','false','1','0'):raise XBRLError('dts_type_fixed_boolean')
   facet['fixed']=n.attrs['fixed']in('true','1')
  result['facets'].append(facet)
  if len(result['facets'])>16:raise XBRLError('dts_type_facet_budget')
 if len(result['facets'])>16:raise XBRLError('dts_type_facet_budget')
 result['unsupported']=sorted(set(result['unsupported']));return result

def _resolve(name,definitions,profile):
 path=[];seen=set();current=name
 while True:
  if current in seen:raise XBRLError('dts_type_cycle')
  if len(path)>=8:raise XBRLError('dts_type_depth')
  seen.add(current)
  if current.startswith('{'+XS+'}'):
   local=current.split('}',1)[1]
   if local=='decimal'or local in INTEGER_BOUNDS:
    if profile in(RESTRICTION_PROFILE,BOUNDS_PROFILE):_restriction_constraints(current,path)
    if profile==BOUNDS_PROFILE:_bound_restrictions(current,path)
    return current,path
  if current.startswith('{'+X+'}')and current.split('}',1)[1]in('decimalItemType','monetaryItemType','sharesItemType','pureItemType','integerItemType','nonNegativeIntegerItemType','positiveIntegerItemType'):
   if profile in(RESTRICTION_PROFILE,BOUNDS_PROFILE):_restriction_constraints(current,path)
   if profile==BOUNDS_PROFILE:_bound_restrictions(current,path)
   return current,path
  entry=definitions.get(current)
  if entry is None or entry['declaration']['unsupported']or entry['declaration']['base']is None:raise XBRLError('dts_selected_type_unsupported')
  if 'derivation'in entry['declaration']and profile not in(COMPLEX_PROFILE,WHITESPACE_PROFILE,ENUMERATION_PROFILE,RESTRICTION_PROFILE,BOUNDS_PROFILE):raise XBRLError('dts_selected_type_profile_unsupported')
  if any(f['kind']=='whiteSpace'for f in entry['declaration']['facets'])and profile not in(WHITESPACE_PROFILE,ENUMERATION_PROFILE,RESTRICTION_PROFILE,BOUNDS_PROFILE):raise XBRLError('dts_selected_whitespace_profile_unsupported')
  if any(f['kind']=='enumeration'for f in entry['declaration']['facets'])and profile not in(ENUMERATION_PROFILE,RESTRICTION_PROFILE,BOUNDS_PROFILE):raise XBRLError('dts_selected_enumeration_profile_unsupported')
  if any(f['kind']in('totalDigits','fractionDigits')and 'fixed'in f for f in entry['declaration']['facets'])and profile not in(RESTRICTION_PROFILE,BOUNDS_PROFILE):raise XBRLError('dts_selected_fixed_profile_unsupported')
  path.append({'type':current,**entry});current=entry['declaration']['base']

def _numeric_lexical(lexical,base):
 if len(lexical)>64 or not DECIMAL.fullmatch(lexical):raise XBRLError('dts_type_decimal_lexical')
 value=Decimal(lexical);local=base.split('}',1)[1]
 integer=local.removesuffix('ItemType')if base.startswith('{'+X+'}')else local
 # xs:integer lexical space does not admit a decimal point, even zero fraction.
 if integer in INTEGER_BOUNDS:
  if not re.fullmatch('[+-]?[0-9]+',lexical):raise XBRLError('dts_type_integer_lexical')
  lower,upper=INTEGER_BOUNDS[integer]
  if lower is not None and value<lower or upper is not None and value>upper:raise XBRLError('dts_type_integer_range')
 return value

def _facet_checks(value,lexical,path):
 unsigned=lexical.lstrip('+-');whole,_,fraction=unsigned.partition('.');fraction=fraction.rstrip('0')
 total_digits=max(1,len((whole.lstrip('0')+fraction).lstrip('0')));fraction_digits=len(fraction)
 for entry in path:
  facets=entry['declaration']['facets'];values=[Decimal(f['value'].strip(' \t\r\n'))for f in facets if f['kind']=='enumeration']
  if values and value not in values:raise XBRLError('dts_type_enumeration_violation')
  for f in facets:
   kind=f['kind'];bound=f['value']
   if kind in('whiteSpace','enumeration'):continue
   invalid=total_digits>int(bound)if kind=='totalDigits'else fraction_digits>int(bound)if kind=='fractionDigits'else value<Decimal(bound)if kind=='minInclusive'else value>Decimal(bound)if kind=='maxInclusive'else value<=Decimal(bound)if kind=='minExclusive'else value>=Decimal(bound)
   if invalid:raise XBRLError('dts_type_facet_violation')

def _enumeration_definitions(base,path):
 # Every listed member must be valid for its immediate base, even when no
 # reported fact uses that member (or the selected fact is nil).
 for index,entry in enumerate(path):
  for facet in entry['declaration']['facets']:
   if facet['kind']!='enumeration':continue
   lexical=facet['value'].strip(' \t\r\n');value=_numeric_lexical(lexical,base)
   _facet_checks(value,lexical,path[index+1:])

def _restriction_constraints(base,path):
 # Ancestors first: digit limits may narrow, never widen. Integer's built-in
 # fractionDigits=0 is fixed. This remains bounded declaration corroboration.
 local=base.split('}',1)[1].removesuffix('ItemType');integer=local in INTEGER_BOUNDS
 digits={'fractionDigits':0}if integer else{};fixed={'fractionDigits':0}if integer else{}
 for entry in reversed(path):
  facets=entry['declaration']['facets'];by_kind={f['kind']:f for f in facets if f['kind']not in('enumeration','whiteSpace')}
  if {'minInclusive','minExclusive'}<=by_kind.keys()or {'maxInclusive','maxExclusive'}<=by_kind.keys():raise XBRLError('dts_restriction_mutually_exclusive_bounds')
  for kind in('totalDigits','fractionDigits'):
   if kind not in by_kind:continue
   facet=by_kind[kind];value=int(facet['value'])
   if kind in fixed and value!=fixed[kind]:raise XBRLError('dts_restriction_fixed_digit')
   if kind in digits and value>digits[kind]:raise XBRLError('dts_restriction_digit_widening')
   digits[kind]=value
   if facet.get('fixed'):fixed[kind]=value
  if 'fractionDigits'in digits and 'totalDigits'in digits and digits['fractionDigits']>digits['totalDigits']:raise XBRLError('dts_restriction_fraction_exceeds_total')
  for f in facets:
   if f['kind']in('minInclusive','minExclusive','maxInclusive','maxExclusive'):_numeric_lexical(f['value'],base)
  lower=by_kind.get('minInclusive',by_kind.get('minExclusive'));upper=by_kind.get('maxInclusive',by_kind.get('maxExclusive'))
  if lower and upper:
   lo=Decimal(lower['value']);hi=Decimal(upper['value'])
   if lo>hi:raise XBRLError('dts_restriction_reversed_bounds')
   if lo==hi and(lower['kind']=='minExclusive'or upper['kind']=='maxExclusive'):raise XBRLError('dts_restriction_empty_interval_unsupported')

def _value_check(fact,base,path,units):
 _enumeration_definitions(base,path)
 if fact['nil']:return
 lexical=fact['lexical_value'].strip(' \t\r\n');value=_numeric_lexical(lexical,base);local=base.split('}',1)[1]
 unit=units[fact['unit_ref']]
 if base==tag(X,'monetaryItemType'):
  if unit['denominator']or len(unit['numerator'])!=1 or not re.fullmatch(re.escape('{'+ISO+'}')+'[A-Z]{3}',unit['numerator'][0]):raise XBRLError('dts_type_monetary_unit')
 elif base in(tag(X,'sharesItemType'),tag(X,'pureItemType')):
  if unit['denominator']or unit['numerator']!=[tag(X,'shares'if local=='sharesItemType'else'pure')]:raise XBRLError('dts_type_unit')
 _facet_checks(value,lexical,path)

def corroborate(parsed,dts,*,profile=PROFILE):
 """Add an explicit selected-numeric profile after normal declaration binding."""
 if profile not in PROFILES:raise XBRLError('xbrl_numeric_profile_unsupported')
 if type(parsed)is not dict or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256')or type(dts)is not dict or digest({k:v for k,v in dts.items()if k!='canonical_sha256'})!=dts.get('canonical_sha256'):raise XBRLError('dts_type_input_identity')
 proof=parsed.get('dts_corroboration')
 if not proof or proof['dts_sha256']!=dts['canonical_sha256']:raise XBRLError('dts_type_binding_required')
 if profile==BOUNDS_PROFILE:
  _bound_sources(parsed)
  for key,expected in(('documents',dts['documents']),('concept_declarations',dts['concepts']),('type_declarations',dts.get('type_declarations',{}))):
   if canonical(proof.get(key,{}))!=canonical(expected):raise XBRLError('dts_bound_retained_graph_mismatch')
 records=[];definitions=dts.get('type_declarations',{});size=len(canonical(parsed))
 if size>MAX_OUTPUT_BYTES:raise XBRLError('dts_type_output_budget')
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  declaration=dts['concepts'][fact['concept']]['declaration'];declared=declaration['type']
  if type(declared)is not str or declaration['substitution_group']!=tag(X,'item'):raise XBRLError('dts_selected_type_or_substitution_unsupported')
  base,path=_resolve(declared,definitions,profile);_value_check(fact,base,path,parsed['units'])
  record={'source_fact_id':fact['source_fact_id'],'declared_type':declared,'resolved_numeric_base':base,'restrictions':path,'value_validation':'NIL_UNAVAILABLE'if fact['nil']else'VALIDATED_BOUNDED_NUMERIC_PROFILE'}
  if profile==BOUNDS_PROFILE:record['effective_bounds']=_bound_restrictions(base,path)
  size+=len(canonical(record))+1
  if size>MAX_OUTPUT_BYTES:raise XBRLError('dts_type_output_budget')
  records.append(record)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256')
 result['dts_corroboration']['numeric_value_validation']={'profile':profile,'facts':records,'scope':'Selected numeric values,known standard units and explicitly supported numeric derivations/facets only;not complete schema/DRS validation'}
 if profile==BOUNDS_PROFILE:
  result['numeric_interpretation_profile']=BOUNDS_PROFILE
  result['dts_corroboration']['numeric_value_validation'].update(scope=BOUND_SCOPE,restriction_definition_validation='BOUNDED_INHERITED_NUMERIC_BOUNDS_V2',source_declarations_sha256=digest({k:proof.get(k,{})for k in('dts_sha256','documents','concept_declarations','type_declarations')}))
 if profile==RESTRICTION_PROFILE:result['dts_corroboration']['numeric_value_validation']['restriction_definition_validation']='BOUNDED_DIGITS_FIXED_AND_LOCAL_BOUNDS_V1'
 if len(canonical(result))>MAX_OUTPUT_BYTES:raise XBRLError('dts_type_output_budget')
 result['canonical_sha256']=digest(result);return result


BOUND_SCOPE='Selected original-bound numeric declarations and exact values;inherited range restriction checks and source receipts only;not complete XML Schema/OIM/accounting validation'
QN=re.compile(r'\{[^{}]{1,512}\}[A-Za-z_][A-Za-z0-9_.-]{0,127}\Z')


def _bound_restrictions(base,path):
 """XSD 1.0 Datatypes 4.3.7–4.3.10; preserve exact Decimal comparisons.

 Exact repetition of the effective parent exclusive bound is the specification's
 exception to base value-space membership. It does not bypass a newer narrowed
 parent boundary. Other bounds must also satisfy inherited digit/enumeration facets.
 Empty supported domains remain an explicit unsupported case.
 """
 local=base.split('}',1)[1].removesuffix('ItemType');integer=local in INTEGER_BOUNDS
 limits=INTEGER_BOUNDS.get(local,(None,None));lower=None if limits[0]is None else(Decimal(limits[0]),True);upper=None if limits[1]is None else(Decimal(limits[1]),True)
 for index in range(len(path)-1,-1,-1):
  entry=path[index];parent_lower=lower;parent_upper=upper
  for facet in entry['declaration']['facets']:
   kind=facet['kind']
   if kind not in('minInclusive','minExclusive','maxInclusive','maxExclusive'):continue
   lexical=facet['value'];value=_numeric_lexical(lexical,base);minimum=kind.startswith('min');inclusive=kind in('minInclusive','maxInclusive');parent=parent_lower if minimum else parent_upper
   if parent is not None and((value<parent[0]if minimum else value>parent[0])or value==parent[0]and inclusive and not parent[1]):raise XBRLError('dts_bound_restriction_outside_base_value_space')
   repeated_exclusive=not inclusive and parent is not None and parent==(value,False)
   if not repeated_exclusive:
    try:_facet_checks(value,lexical,path[index+1:])
    except XBRLError:raise XBRLError('dts_bound_restriction_outside_base_value_space')from None
   if minimum:lower=(value,inclusive)
   else:upper=(value,inclusive)
  if lower is not None and upper is not None:
   if lower[0]>upper[0]or lower[0]==upper[0]and not(lower[1]and upper[1]):raise XBRLError('dts_bound_empty_domain_unsupported')
   if integer and int(lower[0])+(not lower[1])>int(upper[0])-(not upper[1]):raise XBRLError('dts_bound_empty_integer_domain_unsupported')
 def limit(value):return None if value is None else{'value':format(value[0],'f'),'inclusive':value[1]}
 return {'lower':limit(lower),'upper':limit(upper),'integer_value_space':integer}


def _bound_sources(parsed):
 """Validate retained normalized metadata before deriving V6 claims."""
 proof=parsed.get('dts_corroboration')
 if type(proof)is not dict:raise XBRLError('dts_bound_source_contract')
 docs=proof.get('documents');concepts=proof.get('concept_declarations');types=proof.get('type_declarations',{})
 if proof.get('structural_closure')is not True or proof.get('unresolved')or type(docs)is not list or not 1<=len(docs)<=16 or type(concepts)is not dict or not 1<=len(concepts)<=2048 or type(types)is not dict or len(types)>2048 or len(canonical(parsed))>MAX_OUTPUT_BYTES:raise XBRLError('dts_bound_source_contract')
 from .xbrl_dts import uri
 if type(proof.get('dts_sha256'))is not str or not re.fullmatch('[0-9a-f]{64}',proof['dts_sha256']):raise XBRLError('dts_bound_source_contract')
 sources={}
 for d in docs:
  if type(d)is not dict or type(d.get('uri'))is not str or d.get('kind')not in('schema','linkbase')or type(d.get('sha256'))is not str or not re.fullmatch('[0-9a-f]{64}',d['sha256'])or d['uri']in sources:raise XBRLError('dts_bound_source_contract')
  if uri(d['uri'])!=d['uri']:raise XBRLError('dts_bound_source_contract')
  sources[d['uri']]=d
 def source(entry):
  values=entry.get('source_documents')
  if type(values)is not list or not 1<=len(values)<=16 or any(type(v)is not str or v not in sources or sources[v]['kind']!='schema'for v in values)or len(set(values))!=len(values):raise XBRLError('dts_bound_declaration_source')
 for name,entry in types.items():
  if type(name)is not str or not QN.fullmatch(name)or name.startswith(('{'+XS+'}','{'+X+'}'))or type(entry)is not dict or set(entry)!={'declaration','source_documents'}:raise XBRLError('dts_bound_type_contract')
  source(entry);decl=entry['declaration']
  if type(decl)is not dict or set(decl)-{'base','facets','unsupported','derivation'}or not {'base','facets','unsupported'}<=set(decl)or type(decl['unsupported'])is not list or any(type(v)is not str for v in decl['unsupported'])or type(decl['facets'])is not list or len(decl['facets'])>16:raise XBRLError('dts_bound_type_contract')
  if decl['unsupported']:continue
  if type(decl['base'])is not str or not QN.fullmatch(decl['base'])or decl.get('derivation')not in(None,'SIMPLE_CONTENT_EXTENSION','SIMPLE_CONTENT_RESTRICTION')or decl.get('derivation')=='SIMPLE_CONTENT_EXTENSION'and decl['facets']:raise XBRLError('dts_bound_type_contract')
  seen=set()
  for f in decl['facets']:
   if type(f)is not dict or not {'kind','value'}<=set(f)or type(f['kind'])is not str or type(f['value'])is not str or not 1<=len(f['value'])<=64:raise XBRLError('dts_bound_facet_contract')
   kind=f['kind'];allowed={'kind','value'}|({'fixed'}if kind in('totalDigits','fractionDigits','whiteSpace')else set())
   if kind not in FACETS|{'whiteSpace','enumeration'}or set(f)-allowed or kind!='enumeration'and kind in seen or 'fixed'in f and type(f['fixed'])is not bool:raise XBRLError('dts_bound_facet_contract')
   seen.add(kind)
   if kind=='whiteSpace':
    if f['value']!='collapse':raise XBRLError('dts_bound_facet_contract')
   elif kind in('totalDigits','fractionDigits'):
    if not re.fullmatch('[0-9]{1,2}',f['value'])or not(1 if kind=='totalDigits'else 0)<=int(f['value'])<=64:raise XBRLError('dts_bound_facet_contract')
   elif not DECIMAL.fullmatch(f['value'].strip(' \t\r\n')if kind=='enumeration'else f['value']):raise XBRLError('dts_bound_facet_contract')
 for name,entry in concepts.items():
  if type(name)is not str or not QN.fullmatch(name)or type(entry)is not dict or type(entry.get('declaration'))is not dict:raise XBRLError('dts_bound_concept_contract')
  source(entry)
 return proof,concepts,types


def validate_bound_numeric_result(parsed):
 """Recompute V6 retained claims in actual collection/product consumers.

 This proves internal receipt/semantic consistency, not original XML or issuer
 authentication. Original DTS acquisition/audit is a separate source boundary.
 """
 try:
  from . import sec
  from .xbrl_calculation_report import _source_fact,_context
  from .xbrl_instance import identifier,MAX_CONTEXTS,MAX_UNITS,MAX_FACTS
  proof,concepts,types=_bound_sources(parsed);report=proof['numeric_value_validation'];expected=[];selected=[];seen=set()
  if parsed.get('numeric_interpretation_profile')!=BOUNDS_PROFILE or type(report)is not dict or set(report)!={'profile','facts','scope','restriction_definition_validation','source_declarations_sha256'}or report['profile']!=BOUNDS_PROFILE or report['scope']!=BOUND_SCOPE or report['restriction_definition_validation']!='BOUNDED_INHERITED_NUMERIC_BOUNDS_V2':raise XBRLError('dts_bound_result_contract')
  if report['source_declarations_sha256']!=digest({k:proof.get(k,{})for k in('dts_sha256','documents','concept_declarations','type_declarations')}):raise XBRLError('dts_bound_result_contract')
  source=parsed['source'];issuer=source['issuer_cik']
  if type(issuer)is not str or not re.fullmatch('[0-9]{10}',issuer)or int(issuer)==0 or type(source.get('source_sha256'))is not str or not re.fullmatch('[0-9a-f]{64}',source['source_sha256']):raise XBRLError('dts_bound_result_contract')
  contexts=parsed['contexts'];units=parsed['units'];facts=parsed['facts']
  if type(contexts)is not dict or not 1<=len(contexts)<=MAX_CONTEXTS or type(units)is not dict or len(units)>MAX_UNITS or type(facts)is not list or len(facts)>MAX_FACTS:raise XBRLError('dts_bound_result_contract')
  for key,context in contexts.items():identifier(key);_context(context,issuer)
  for key,unit in units.items():
   identifier(key)
   if type(unit)is not dict or set(unit)!={'numerator','denominator','semantic_sha256'}:raise XBRLError('dts_bound_result_contract')
   for side in('numerator','denominator'):
    values=unit[side]
    if type(values)is not list or not(1 if side=='numerator'else 0)<=len(values)<=8 or any(type(v)is not str or not QN.fullmatch(v)for v in values)or values!=sorted(values):raise XBRLError('dts_bound_result_contract')
   if unit['semantic_sha256']!=digest({k:unit[k]for k in('numerator','denominator')}):raise XBRLError('dts_bound_result_contract')
  # The existing source-fact verifier dispatches on the original schema. Dimensional
  # profiles preserve those exact fact IDs; normalize only this dispatch view.
  is_set=parsed.get('schema')=='gig.sec.xbrl.inline_set.v1'or type(parsed.get('schema'))is str and parsed['schema'].startswith('gig.sec.xbrl.dimensional_inline_set.v')
  identity_view={**parsed,'schema':'gig.sec.xbrl.inline_set.v1'if is_set else'gig.sec.xbrl.instance.v1'}
  if is_set:
   ds=parsed.get('document_set')
   if type(ds)is not dict or type(ds.get('documents'))is not list or not 1<=len(ds['documents'])<=8 or ds.get('sha256')!=digest(ds['documents'])or ds['sha256']!=source['source_sha256']:raise XBRLError('dts_bound_result_contract')
   original_uris=set()
   for original in ds['documents']:
    if type(original)is not dict or type(original.get('uri'))is not str or original['uri']in original_uris or type(original.get('source'))is not dict or type(original['source'].get('source_sha256'))is not str or not re.fullmatch('[0-9a-f]{64}',original['source']['source_sha256']):raise XBRLError('dts_bound_result_contract')
    original_uris.add(original['uri'])
  for fact in facts:
   if type(fact)is not dict or fact.get('admission')not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES','UNVERIFIED_CONCEPT','PERIOD_OR_UNIT_MISMATCH'):raise XBRLError('dts_bound_result_contract')
   if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
   if type(fact['nil'])is not bool or type(fact['source_fact_id'])is not str or not re.fullmatch('[0-9a-f]{64}',fact['source_fact_id'])or type(fact['lexical_value'])is not str or len(fact['lexical_value'])>16384:raise XBRLError('dts_bound_result_contract')
   identifier(fact['context_ref']);identifier(fact['unit_ref']);context=contexts[fact['context_ref']];unit=units[fact['unit_ref']]
   if fact['context_sha256']!=context['semantic_sha256']or fact['unit_sha256']!=unit['semantic_sha256']:raise XBRLError('dts_bound_result_contract')
   attributes=fact['attributes']
   if type(attributes)is not dict or len(attributes)>24 or any(type(k)is not str or len(k)>640 or type(v)is not str or len(v)>1024 for k,v in attributes.items())or any(attributes.get(k)!=fact[field]for k,field in(('contextRef','context_ref'),('unitRef','unit_ref'),('decimals','decimals'),('precision','precision'))):raise XBRLError('dts_bound_result_contract')
   nil_lexical=attributes.get(tag('http://www.w3.org/2001/XMLSchema-instance','nil'),'false')
   if nil_lexical not in('true','false','1','0')or fact['nil']!=(nil_lexical in('true','1')):raise XBRLError('dts_bound_result_contract')
   lexical=fact['lexical_value'].strip(' \t\r\n')
   if fact['nil']:
    if fact['value']is not None or lexical or fact['nil_status']!='NIL_REPORTED_UNAVAILABLE':raise XBRLError('dts_bound_result_contract')
   elif type(fact['value'])is not str or fact['nil_status']is not None or fact['value']!=sec.exact(Decimal(lexical)):raise XBRLError('dts_bound_result_contract')
   _source_fact(identity_view,fact)
   id_=fact['source_fact_id'];decl=concepts[fact['concept']]['declaration'];period=context['period']['kind']
   if type(decl.get('abstract'))is not bool or type(decl.get('nillable'))is not bool or type(decl.get('type'))is not str or not QN.fullmatch(decl['type'])or decl.get('period_type')not in('instant','duration')or id_ in seen or decl['substitution_group']!=tag(X,'item')or decl['abstract']or decl['period_type']!=period or fact['nil']and not decl['nillable']:raise XBRLError('dts_bound_result_contract')
   seen.add(id_);base,path=_resolve(decl['type'],types,BOUNDS_PROFILE);_value_check(fact,base,path,units)
   selected.append({'source_fact_id':id_,'concept':fact['concept'],'source_documents':concepts[fact['concept']]['source_documents'],'period_type':period,'declared_type':decl['type'],'type_validation':'NOT_PERFORMED'})
   expected.append({'source_fact_id':id_,'declared_type':decl['type'],'resolved_numeric_base':base,'restrictions':path,'value_validation':'NIL_UNAVAILABLE'if fact['nil']else'VALIDATED_BOUNDED_NUMERIC_PROFILE','effective_bounds':_bound_restrictions(base,path)})
  if canonical(report['facts'])!=canonical(expected)or canonical(proof['selected_facts'])!=canonical(selected):raise XBRLError('dts_bound_result_contract')
 except (XBRLError,KeyError,TypeError,ValueError,ArithmeticError,AttributeError):raise XBRLError('dts_bound_result_contract')from None
