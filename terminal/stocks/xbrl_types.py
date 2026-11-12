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
 if node.name!=tag(XS,'simpleType')or len(body)!=1 or body[0].name!=tag(XS,'restriction'):
  result['unsupported']=['ONLY_NAMED_SIMPLE_RESTRICTIONS_SUPPORTED'];return result
 restriction=body[0]
 if restriction.text().strip()or set(restriction.attrs)-{'base','id'}or 'base'not in restriction.attrs:
  result['unsupported']=['RESTRICTION_STRUCTURE_UNSUPPORTED'];return result
 result['base']=qname(restriction.attrs['base'],restriction);seen=set()
 for n in restriction.children:
  if n.name==tag(XS,'annotation'):continue
  kind=n.name.removeprefix('{'+XS+'}')
  if kind not in FACETS or n.children or n.text().strip()or set(n.attrs)-{'value','id'}or kind in seen:
   result['unsupported'].append('FACET_OR_STRUCTURE_UNSUPPORTED');continue
  seen.add(kind);value=n.attrs.get('value')
  if type(value)is not str or len(value)>64:raise XBRLError('dts_type_facet_budget')
  if kind in('totalDigits','fractionDigits'):
   if not re.fullmatch('[0-9]{1,2}',value)or not (1 if kind=='totalDigits'else 0)<=int(value)<=64:raise XBRLError('dts_type_digit_facet')
  elif not DECIMAL.fullmatch(value):raise XBRLError('dts_type_numeric_facet')
  result['facets'].append({'kind':kind,'value':value})
  if len(result['facets'])>16:raise XBRLError('dts_type_facet_budget')
 result['unsupported']=sorted(set(result['unsupported']));return result

def _resolve(name,definitions):
 path=[];seen=set();current=name
 while True:
  if current in seen:raise XBRLError('dts_type_cycle')
  if len(path)>=8:raise XBRLError('dts_type_depth')
  seen.add(current)
  if current.startswith('{'+XS+'}'):
   local=current.split('}',1)[1]
   if local=='decimal'or local in INTEGER_BOUNDS:return current,path
  if current.startswith('{'+X+'}')and current.split('}',1)[1]in('decimalItemType','monetaryItemType','sharesItemType','pureItemType','integerItemType','nonNegativeIntegerItemType','positiveIntegerItemType'):
   return current,path
  entry=definitions.get(current)
  if entry is None or entry['declaration']['unsupported']or entry['declaration']['base']is None:raise XBRLError('dts_selected_type_unsupported')
  path.append({'type':current,**entry});current=entry['declaration']['base']

def _value_check(fact,base,path,units):
 if fact['nil']:return
 lexical=fact['lexical_value'].strip(' \t\r\n')
 if len(lexical)>64 or not DECIMAL.fullmatch(lexical):raise XBRLError('dts_type_decimal_lexical')
 value=Decimal(lexical);local=base.split('}',1)[1]
 integer=local.removesuffix('ItemType')if base.startswith('{'+X+'}')else local
 # xs:integer lexical space does not admit a decimal point, even a zero fraction.
 if integer in INTEGER_BOUNDS:
  if not re.fullmatch('[+-]?[0-9]+',lexical):raise XBRLError('dts_type_integer_lexical')
  lower,upper=INTEGER_BOUNDS[integer]
  if lower is not None and value<lower or upper is not None and value>upper:raise XBRLError('dts_type_integer_range')
 unit=units[fact['unit_ref']]
 if base==tag(X,'monetaryItemType'):
  if unit['denominator']or len(unit['numerator'])!=1 or not re.fullmatch(re.escape('{'+ISO+'}')+'[A-Z]{3}',unit['numerator'][0]):raise XBRLError('dts_type_monetary_unit')
 elif base in(tag(X,'sharesItemType'),tag(X,'pureItemType')):
  if unit['denominator']or unit['numerator']!=[tag(X,'shares'if local=='sharesItemType'else'pure')]:raise XBRLError('dts_type_unit')
 unsigned=lexical.lstrip('+-');whole,_,fraction=unsigned.partition('.');fraction=fraction.rstrip('0')
 total_digits=max(1,len((whole.lstrip('0')+fraction).lstrip('0')));fraction_digits=len(fraction)
 for entry in path:
  for f in entry['declaration']['facets']:
   kind=f['kind'];bound=f['value']
   invalid=total_digits>int(bound)if kind=='totalDigits'else fraction_digits>int(bound)if kind=='fractionDigits'else value<Decimal(bound)if kind=='minInclusive'else value>Decimal(bound)if kind=='maxInclusive'else value<=Decimal(bound)if kind=='minExclusive'else value>=Decimal(bound)
   if invalid:raise XBRLError('dts_type_facet_violation')

def corroborate(parsed,dts):
 """Add an explicit selected-numeric profile after normal declaration binding."""
 if type(parsed)is not dict or digest({k:v for k,v in parsed.items()if k!='canonical_sha256'})!=parsed.get('canonical_sha256')or type(dts)is not dict or digest({k:v for k,v in dts.items()if k!='canonical_sha256'})!=dts.get('canonical_sha256'):raise XBRLError('dts_type_input_identity')
 proof=parsed.get('dts_corroboration')
 if not proof or proof['dts_sha256']!=dts['canonical_sha256']:raise XBRLError('dts_type_binding_required')
 records=[];definitions=dts.get('type_declarations',{});size=len(canonical(parsed))
 if size>MAX_OUTPUT_BYTES:raise XBRLError('dts_type_output_budget')
 for fact in parsed['facts']:
  if fact['admission']not in('ADMITTED_PROFILE','CONFLICTED_EXACT_VALUES'):continue
  declaration=dts['concepts'][fact['concept']]['declaration'];declared=declaration['type']
  if type(declared)is not str or declaration['substitution_group']!=tag(X,'item'):raise XBRLError('dts_selected_type_or_substitution_unsupported')
  base,path=_resolve(declared,definitions);_value_check(fact,base,path,parsed['units'])
  record={'source_fact_id':fact['source_fact_id'],'declared_type':declared,'resolved_numeric_base':base,'restrictions':path,'value_validation':'NIL_UNAVAILABLE'if fact['nil']else'VALIDATED_BOUNDED_NUMERIC_PROFILE'}
  size+=len(canonical(record))+1
  if size>MAX_OUTPUT_BYTES:raise XBRLError('dts_type_output_budget')
  records.append(record)
 result=copy.deepcopy(parsed);result.pop('canonical_sha256')
 result['dts_corroboration']['numeric_value_validation']={'profile':PROFILE,'facts':records,'scope':'Selected numeric values,known standard units and supported simple restriction facets only;not complete schema/DRS validation'}
 if len(canonical(result))>MAX_OUTPUT_BYTES:raise XBRLError('dts_type_output_budget')
 result['canonical_sha256']=digest(result);return result
