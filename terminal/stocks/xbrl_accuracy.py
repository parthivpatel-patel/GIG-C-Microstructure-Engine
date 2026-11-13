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
