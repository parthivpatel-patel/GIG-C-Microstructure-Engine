"""Exact bounded accuracy enclosures for conventional reported XBRL numerics.

Closed endpoints are conservative at ties. This is interval compatibility,not
full XBRL2.1/Calculations1.1 conformance or proof of an underlying exact value.
"""
import re
from fractions import Fraction
from decimal import Decimal
from .xbrl_instance import XBRLError
from .xbrl_relationships import rational
PROFILE='CLOSED_REPORTED_ACCURACY_V1';MAX_EXPONENT=128;MAX_TERMS=128

def _power(n):return Fraction(10**n)if n>=0 else Fraction(1,10**(-n))
def _number(value):
 if type(value)is not str or not 1<=len(value)<=80 or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]+)?)(?:[eE][+-]?[0-9]{1,3})?',value):raise XBRLError('accuracy_numeric_contract')
 d=Decimal(value)
 if not -MAX_EXPONENT<=d.as_tuple().exponent<=MAX_EXPONENT or abs(d.adjusted())>MAX_EXPONENT:raise XBRLError('accuracy_numeric_budget')
 return Fraction(d)
def _record(lo,hi):return {'lower':rational(lo),'upper':rational(hi),'lower_closed':True,'upper_closed':True}
def _read(i):
 if type(i)is not dict or i.get('lower_closed')is not True or i.get('upper_closed')is not True:raise XBRLError('accuracy_interval_contract')
 values=[]
 for key in('lower','upper'):
  r=i.get(key)
  if type(r)is not dict or set(r)!={'numerator','denominator'}or type(r['numerator'])is not str or not re.fullmatch(r'-?[0-9]{1,256}',r['numerator'])or type(r['denominator'])is not str or not re.fullmatch(r'[0-9]{1,256}',r['denominator'])or int(r['denominator'])<=0:raise XBRLError('accuracy_rational_contract')
  den=int(r['denominator']);rest=den
  for factor in(2,5):
   while rest%factor==0:rest//=factor
  if rest!=1 or den>2*10**MAX_EXPONENT:raise XBRLError('accuracy_interval_grid_unsupported')
  values.append(Fraction(int(r['numerator']),int(r['denominator'])))
 if values[0]>values[1]:raise XBRLError('accuracy_interval_order')
 return tuple(values)

def enclosure(value,decimals=None,precision=None,*,nil=False):
 if type(nil)is not bool:raise XBRLError('accuracy_nil_contract')
 if decimals is not None and precision is not None:raise XBRLError('accuracy_declaration_conflict')
 if decimals is not None and(type(decimals)is not str or not re.fullmatch(r'INF|-?(?:0|[1-9][0-9]{0,2})',decimals)):raise XBRLError('accuracy_decimals_contract')
 if precision is not None and(type(precision)is not str or not re.fullmatch(r'INF|[1-9][0-9]{0,2}',precision)):raise XBRLError('accuracy_precision_contract')
 result={'profile':PROFILE,'status':'UNAVAILABLE','reason':None,'declared_decimals':decimals,'declared_precision':precision,'effective_decimals':None,'interval':None}
 if nil:
  if value is not None:raise XBRLError('accuracy_nil_value')
  result['reason']='NIL_REPORTED';return result
 v=_number(value)
 if decimals is None and precision is None:result['reason']='ACCURACY_NOT_DECLARED';return result
 if decimals=='INF'or precision=='INF':result.update(status='EXACT',effective_decimals='INF',interval=_record(v,v));return result
 if decimals is not None:d=int(decimals)
 else:
  if v==0:result['reason']='ZERO_WITH_FINITE_PRECISION_UNSUPPORTED';return result
  # Decimal.adjusted() is exact and independent of the active decimal context.
  d=int(precision)-1-Decimal(value).copy_abs().adjusted()
 if not -MAX_EXPONENT<=d<=MAX_EXPONENT:result['reason']='ACCURACY_EXPONENT_OUTSIDE_PROFILE';return result
 quantum=_power(-d)
 if (v/quantum).denominator!=1:result['reason']='NONCANONICAL_REPORTED_ACCURACY_UNSUPPORTED';return result
 result.update(status='BOUNDED',effective_decimals=d,interval=_record(v-quantum/2,v+quantum/2));return result

def duplicates(facts,*,values=None):
 if type(facts)is not list or not 1<=len(facts)<=8:raise XBRLError('accuracy_duplicate_budget')
 results=[];numbers=set();ids=set();nil=False
 for f in facts:
  id_=f['source_fact_id']
  if type(id_)is not str or not 1<=len(id_)<=64 or id_ in ids:raise XBRLError('accuracy_duplicate_identity')
  ids.add(id_);value=values[id_]if values is not None else f['value'];nil|=f['nil']
  if not f['nil']:numbers.add(_number(value))
  results.append({'source_fact_id':id_,**enclosure(value,f.get('decimals'),f.get('precision'),nil=f['nil'])})
 result={'profile':PROFILE,'status':'UNAVAILABLE','reason':None,'source_fact_ids':sorted(ids),'facts':results,'interval':None}
 if len(numbers)>1 or nil and numbers:result['reason']='CONFLICTING_DUPLICATE_VALUES';return result
 if any(r['interval']is None for r in results):result['reason']='NIL_OR_UNSUPPORTED_ACCURACY';return result
 bounds=[_read(r['interval'])for r in results];lo=max(v[0]for v in bounds);hi=min(v[1]for v in bounds)
 if lo>hi:result['reason']='DISJOINT_DUPLICATE_ENCLOSURES';return result
 result.update(status='SUPPORTED',interval=_record(lo,hi),reason=None);return result

def consistency(parent,terms):
 if type(terms)is not list or not 1<=len(terms)<=MAX_TERMS:raise XBRLError('accuracy_term_budget')
 result={'profile':PROFILE,'status':'INCOMPLETE','reason':None,'parent_interval':None,'weighted_sum_interval':None,'residual_interval':None,'terms':[],'policy':'Closed conservative enclosures;boundary overlap compatible,not proof;no missing zeros or dimensional/period/unit aggregation'}
 if parent is None or any(t.get('accuracy')is None for t in terms):result['reason']='MISSING_OR_INELIGIBLE_FACT';return result
 if parent.get('interval')is None or any(t['accuracy'].get('interval')is None for t in terms):result.update(status='UNSUPPORTED_ACCURACY',reason='ACCURACY_UNAVAILABLE_OR_DUPLICATE_CONFLICT');return result
 lo=hi=Fraction(0)
 for t in terms:
  w=t.get('weight')
  if type(w)is not int or w not in(-1,1):raise XBRLError('accuracy_weight_outside_profile')
  a,b=_read(t['accuracy']['interval']);a,b=(a*w,b*w)if w>0 else(b*w,a*w);lo+=a;hi+=b
  result['terms'].append({'concept':t['concept'],'weight':w,'source_fact_ids':t['accuracy']['source_fact_ids'],'weighted_interval':_record(a,b)})
 a,b=_read(parent['interval']);result.update(status='DEFINITELY_INCONSISTENT'if a>hi or b<lo else'ROUNDING_COMPATIBLE',parent_interval=_record(a,b),weighted_sum_interval=_record(lo,hi),residual_interval=_record(a-hi,b-lo));return result

def duplicate_diagnostic(facts,*,values=None):
 """Explain duplicate accuracy without resolving differing values or selecting a fact."""
 prior=duplicates(facts,values=values);records=prior['facts'];reported=[values[f['source_fact_id']]if values is not None else f['value']for f in facts];numeric={_number(v)for v in reported if v is not None}
 result={'profile':'DUPLICATE_ACCURACY_DIAGNOSTICS_V1','status':'ACCURACY_UNAVAILABLE','source_fact_ids':prior['source_fact_ids'],'numeric_values_equal':len(numeric)==1 if numeric else None,'intersection_interval':None,'facts':[{**r,'reported_value':v}for r,v in zip(records,reported)],'selection_policy':'Diagnostics only;differing values remain conflicting and no source fact is selected'}
 nil=any(f['nil']for f in facts)
 if not numeric:result['status']='NIL_ONLY';return result
 if nil:result['status']='MIXED_NIL_CONFLICT';return result
 if any(r['interval']is None for r in records):return result
 bounds=[_read(r['interval'])for r in records];lo=max(v[0]for v in bounds);hi=min(v[1]for v in bounds)
 if lo<=hi:result['intersection_interval']=_record(lo,hi)
 result['status']='NUMERICALLY_IDENTICAL'if len(numeric)==1 else'OVERLAPPING_ACCURACY_AMBIGUOUS'if lo<=hi else'DISJOINT_ACCURACY_DUPLICATES'
 return result

# Additive calculation-only contract. Legacy enclosures/duplicate APIs above stay
# conservative and unchanged. Callers must bind one OIM-compatible data point
# (concept,entity,period,unit,dimensions) before supplying its source facts.
CALCULATION_PROFILE='EXACT_CALCULATION_INTERVALS_V2'
ROUNDING_MODES=('round-to-nearest','truncation')

def _mode(value):
 if type(value)is not str or value not in ROUNDING_MODES:raise XBRLError('calculation_rounding_mode')
 return value

def _interval(lo,hi,lc=True,uc=True):
 return {'lower':rational(lo),'upper':rational(hi),'lower_closed':lc,'upper_closed':uc}

def _read_calculation(value):
 if type(value)is not dict or set(value)!={'lower','upper','lower_closed','upper_closed'}or type(value['lower_closed'])is not bool or type(value['upper_closed'])is not bool:raise XBRLError('calculation_interval_contract')
 bounds=[]
 for key in('lower','upper'):
  r=value[key]
  if type(r)is not dict or set(r)!={'numerator','denominator'}or type(r['numerator'])is not str or not re.fullmatch(r'-?[0-9]{1,512}',r['numerator'])or type(r['denominator'])is not str or not re.fullmatch(r'[0-9]{1,256}',r['denominator']):raise XBRLError('calculation_rational_contract')
  den=int(r['denominator'])
  if den<=0 or den>2*10**(MAX_EXPONENT+12):raise XBRLError('calculation_rational_budget')
  rest=den
  for factor in(2,5):
   while rest%factor==0:rest//=factor
  if rest!=1:raise XBRLError('calculation_interval_grid_unsupported')
  bounds.append(Fraction(int(r['numerator']),den))
 lo,hi=bounds;lc=value['lower_closed'];uc=value['upper_closed']
 if lo>hi or lo==hi and not(lc and uc):raise XBRLError('calculation_empty_interval')
 return lo,hi,lc,uc

def _intersection(intervals):
 lo=max(i[0]for i in intervals);hi=min(i[1]for i in intervals)
 lc=all(i[2]for i in intervals if i[0]==lo);uc=all(i[3]for i in intervals if i[1]==hi)
 return None if lo>hi or lo==hi and not(lc and uc)else(lo,hi,lc,uc)

def calculation_enclosure(value,decimals=None,*,rounding_mode='round-to-nearest',nil=False):
 """Exact rounded/truncated fact interval;not full report/OIM conformance."""
 mode=_mode(rounding_mode);base=enclosure(value,decimals,nil=nil)
 result={'profile':CALCULATION_PROFILE,'rounding_mode':mode,'status':base['status'],'reason':base['reason'],'reported_value':value,'declared_decimals':decimals,'effective_decimals':base['effective_decimals'],'interval':base['interval']}
 if base['reason']=='NONCANONICAL_REPORTED_ACCURACY_UNSUPPORTED':
  result.update(status='EXCESS_DIGITS',reason='DIGITS_IN_EXCESS_OF_DECLARED_PRECISION',error_code='calc11e:excessDigits');return result
 if base['interval']is None or base['status']=='EXACT'or mode=='round-to-nearest':return result
 v=_number(value);quantum=_power(-base['effective_decimals'])
 result['interval']=_interval(v,v+quantum,True,False)if v>0 else _interval(v-quantum,v,False,True)if v<0 else _interval(-quantum,quantum,False,False)
 return result

def calculation_duplicates(facts,*,values=None,rounding_mode='round-to-nearest'):
 """Intersect pre-bound data-point intervals;never select a reported value.

 Differing original values remain visible. A compatible intersection is only a
 calculation constraint,not an alias,financial fact or accounting reconciliation.
 """
 mode=_mode(rounding_mode)
 if type(facts)is not list or not 1<=len(facts)<=8:raise XBRLError('calculation_duplicate_budget')
 ids=set();numbers=set();results=[];nil=[]
 for f in facts:
  if type(f)is not dict or type(f.get('source_fact_id'))is not str or not 1<=len(f['source_fact_id'])<=64 or f['source_fact_id']in ids or type(f.get('nil'))is not bool:raise XBRLError('calculation_duplicate_identity')
  id_=f['source_fact_id'];ids.add(id_)
  if values is not None and(type(values)is not dict or id_ not in values):raise XBRLError('calculation_duplicate_values')
  value=values[id_]if values is not None else f.get('value');nil.append(f['nil'])
  r=calculation_enclosure(value,f.get('decimals'),rounding_mode=mode,nil=f['nil'])
  if f.get('precision')is not None:r.update(status='UNAVAILABLE',reason='PRECISION_ATTRIBUTE_OUTSIDE_CALCULATION_PROFILE',interval=None)
  if not f['nil']:numbers.add(_number(value))
  results.append({'source_fact_id':id_,**r})
 result={'profile':CALCULATION_PROFILE,'rounding_mode':mode,'status':'UNAVAILABLE','reason':None,'source_fact_ids':sorted(ids),'facts':results,'numeric_values_equal':len(numbers)==1 if numbers else None,'selected_reported_value':None,'interval':None,'policy':'Input facts must already bind one compatible data point;interval constraints never select or rewrite reported values'}
 if any(r['status']=='EXCESS_DIGITS'for r in results):result.update(reason='DIGITS_IN_EXCESS_OF_DECLARED_PRECISION',error_code='calc11e:excessDigits');return result
 if any(nil):result['reason']='NIL_ONLY'if all(nil)else'MIXED_NIL_CONFLICT';return result
 if any(r['interval']is None for r in results):result['reason']='ACCURACY_UNAVAILABLE';return result
 common=_intersection([_read_calculation(r['interval'])for r in results])
 if common is None:
  result.update(status='INCONSISTENT_DUPLICATES',reason='DISJOINT_FACT_VALUE_INTERVALS',error_code='oime:disallowedDuplicateFacts'if mode=='round-to-nearest'else'calc11e:disallowedDuplicateFactsUsingTruncation');return result
 result.update(status='INTERVAL_COMPATIBLE',interval=_interval(*common));return result

def calculation_consistency(parent,terms,*,rounding_mode='round-to-nearest'):
 """Calculation arithmetic over pre-bound source intervals;no aspect inference."""
 from .xbrl_relationships import number
 mode=_mode(rounding_mode)
 if type(terms)is not list or not 1<=len(terms)<=MAX_TERMS:raise XBRLError('calculation_term_budget')
 concepts=set()
 for t in terms:
  if type(t)is not dict or type(t.get('concept'))is not str or not 1<=len(t['concept'])<=512:raise XBRLError('calculation_term_contract')
  if t['concept']in concepts:raise XBRLError('calculation_duplicate_contributing_concept')
  concepts.add(t['concept'])
 result={'profile':CALCULATION_PROFILE,'rounding_mode':mode,'status':'INCOMPLETE','reason':None,'parent_interval':None,'weighted_sum_interval':None,'residual_interval':None,'terms':[],'source_fact_ids':[],'selected_reported_value':None,'policy':'Caller binds source-compatible concept/entity/period/unit/dimensions and effective arcs;no missing zeros,aggregation or reported-fact selection'}
 proofs=[parent]+[t.get('accuracy')if type(t)is dict else None for t in terms]
 if any(p is None for p in proofs):result['reason']='MISSING_OR_INELIGIBLE_FACT';return result
 for p in proofs:
  if type(p)is not dict or p.get('profile')!=CALCULATION_PROFILE or p.get('rounding_mode')!=mode:raise XBRLError('calculation_accuracy_profile_or_mode')
  if type(p.get('source_fact_ids'))is not list or not 1<=len(p['source_fact_ids'])<=8 or any(type(i)is not str or not 1<=len(i)<=64 for i in p['source_fact_ids']):raise XBRLError('calculation_source_identity')
  if len(set(p['source_fact_ids']))!=len(p['source_fact_ids']):raise XBRLError('calculation_source_identity')
  if p.get('selected_reported_value')is not None or p.get('status')not in('INTERVAL_COMPATIBLE','UNAVAILABLE','INCONSISTENT_DUPLICATES')or (p.get('interval')is not None)!=(p['status']=='INTERVAL_COMPATIBLE'):raise XBRLError('calculation_accuracy_proof_contract')
  result['source_fact_ids'].extend(p['source_fact_ids'])
 result['source_fact_ids']=sorted(set(result['source_fact_ids']))
 if any(p.get('interval')is None for p in proofs):
  result.update(status='UNSUPPORTED_ACCURACY',reason='SOURCE_ACCURACY_OR_DUPLICATES_UNAVAILABLE')
  codes=[p.get('error_code')for p in proofs if p.get('error_code')]
  if codes:result['source_error_codes']=sorted(set(codes))
  return result
 lo=hi=Fraction(0);lc=uc=True
 for term in terms:
  if type(term.get('concept'))is not str or not 1<=len(term['concept'])<=512:raise XBRLError('calculation_concept_identity')
  w=term.get('weight')
  if type(w)is int:w=str(w)
  w=number(w,'calculation_weight_contract')
  if not w:raise XBRLError('calculation_zero_weight')
  a,b,ac,bc=_read_calculation(term['accuracy']['interval'])
  if w<0:a,b,ac,bc=b*w,a*w,bc,ac
  else:a*=w;b*=w
  lo+=a;hi+=b;lc&=ac;uc&=bc
  result['terms'].append({'concept':term['concept'],'weight':rational(w),'source_fact_ids':term['accuracy']['source_fact_ids'],'weighted_interval':_interval(a,b,ac,bc)})
 a,b,ac,bc=_read_calculation(parent['interval']);overlap=_intersection([(a,b,ac,bc),(lo,hi,lc,uc)])
 result.update(status='CALCULATION_COMPATIBLE'if overlap is not None else'DEFINITELY_INCONSISTENT',parent_interval=_interval(a,b,ac,bc),weighted_sum_interval=_interval(lo,hi,lc,uc),residual_interval=_interval(a-hi,b-lo,ac and uc,bc and lc))
 if overlap is None:result['error_code']='calc11e:inconsistentCalculationUsingRounding'if mode=='round-to-nearest'else'calc11e:inconsistentCalculationUsingTruncation'
 return result
