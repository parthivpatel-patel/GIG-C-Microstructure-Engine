"""Exact authored Calc1.1 interval math;not report/OIM conformance claims."""
import copy,unittest
from fractions import Fraction
from decimal import localcontext
from .test_xbrl_accuracy import f,raw
from .xbrl_accuracy import calculation_enclosure as enc,calculation_duplicates as dup,calculation_consistency as calc,duplicates,consistency,MAX_TERMS
from .xbrl_instance import XBRLError

def acc(value,d='0',mode='round-to-nearest',id_='a'):return dup([f(value,d,id_=id_)],rounding_mode=mode)
def term(value,d='0',mode='round-to-nearest',weight=1,concept='child',id_='b'):return {'concept':concept,'weight':weight,'accuracy':acc(value,d,mode,id_)}
def bounds(interval):return(raw(interval,'lower'),raw(interval,'upper'),interval['lower_closed'],interval['upper_closed'])

class CalculationIntervals(unittest.TestCase):
 def test_truncation_positive_negative_and_zero_exact_open_bounds(self):
  for value,expected in [('100',(Fraction(100),Fraction(101),True,False)),('-100',(Fraction(-101),Fraction(-100),False,True)),('0',(Fraction(-1),Fraction(1),False,False))]:
   self.assertEqual(bounds(enc(value,'0',rounding_mode='truncation')['interval']),expected)
 def test_infinite_accuracy_is_closed_point_under_either_mode(self):
  for mode in('round-to-nearest','truncation'):
   for value in('0','-1.25'):self.assertEqual(bounds(enc(value,'INF',rounding_mode=mode)['interval']),(Fraction(value),Fraction(value),True,True))
 def test_rounding_ties_overlap_but_truncation_touching_boundaries_do_not(self):
  rounded=calc(acc('100'),[term('99')]);self.assertEqual(rounded['status'],'CALCULATION_COMPATIBLE')
  truncated=calc(acc('100',mode='truncation'),[term('99',mode='truncation')],rounding_mode='truncation');self.assertEqual(truncated['status'],'DEFINITELY_INCONSISTENT');self.assertEqual(truncated['error_code'],'calc11e:inconsistentCalculationUsingTruncation')
 def test_negative_weight_swaps_endpoint_closure_and_decimal_weight_is_exact(self):
  r=calc(acc('-50','INF','truncation'),[term('100',mode='truncation',weight='-0.5')],rounding_mode='truncation')
  self.assertEqual(bounds(r['weighted_sum_interval']),(Fraction(-101,2),Fraction(-50),False,True));self.assertEqual(r['status'],'CALCULATION_COMPATIBLE');self.assertEqual(r['terms'][0]['weight'],{'numerator':'-1','denominator':'2'})
 def test_sum_bounds_are_open_if_any_contribution_bound_is_open(self):
  r=calc(acc('3','INF','truncation'),[term('1',mode='truncation',concept='x',id_='x'),term('2','INF','truncation',concept='y',id_='y')],rounding_mode='truncation')
  self.assertEqual(bounds(r['weighted_sum_interval']),(Fraction(3),Fraction(4),True,False));self.assertEqual(bounds(r['residual_interval']),(Fraction(-1),Fraction(0),False,True));self.assertEqual(r['source_fact_ids'],['a','x','y'])
 def test_compatible_differing_duplicates_retain_every_reported_value(self):
  facts=[f('5000','-3',id_='a'),f('5500','-2',id_='b')];p=dup(facts)
  self.assertEqual(p['status'],'INTERVAL_COMPATIBLE');self.assertFalse(p['numeric_values_equal']);self.assertIsNone(p['selected_reported_value']);self.assertEqual([v['reported_value']for v in p['facts']],['5000','5500']);self.assertEqual(bounds(p['interval']),(Fraction(5450),Fraction(5500),True,True))
  self.assertEqual(duplicates(facts)['reason'],'CONFLICTING_DUPLICATE_VALUES');self.assertIsNone(duplicates(facts)['interval'])
 def test_truncation_duplicate_intersection_respects_open_endpoints(self):
  facts=[f('5000','-3',id_='a'),f('6000','-3',id_='b')]
  self.assertEqual(dup(facts)['status'],'INTERVAL_COMPATIBLE');p=dup(facts,rounding_mode='truncation');self.assertEqual(p['status'],'INCONSISTENT_DUPLICATES');self.assertIsNone(p['interval']);self.assertEqual(p['error_code'],'calc11e:disallowedDuplicateFactsUsingTruncation')
 def test_disjoint_duplicate_error_prevents_calculation_and_retains_lineage(self):
  p=dup([f('100',id_='a'),f('103',id_='b')]);r=calc(p,[term('101')]);self.assertEqual(r['status'],'UNSUPPORTED_ACCURACY');self.assertEqual(r['source_error_codes'],['oime:disallowedDuplicateFacts']);self.assertEqual(r['source_fact_ids'],['a','b'])
 def test_excess_digits_are_explicit_and_never_truncated_into_a_fact(self):
  for mode in('round-to-nearest','truncation'):
   p=enc('1.25','1',rounding_mode=mode);self.assertEqual(p['status'],'EXCESS_DIGITS');self.assertEqual(p['reported_value'],'1.25');self.assertIsNone(p['interval']);self.assertEqual(p['error_code'],'calc11e:excessDigits')
   d=dup([f('1.25','1')],rounding_mode=mode);r=calc(d,[term('1.2','1',mode)],rounding_mode=mode);self.assertEqual(r['source_error_codes'],['calc11e:excessDigits'])
 def test_mixed_nil_missing_accuracy_and_precision_are_unavailable(self):
  self.assertEqual(dup([f(None,id_='nil',nil=True),f('0',id_='zero')])['reason'],'MIXED_NIL_CONFLICT')
  self.assertEqual(dup([f(None,id_='nil',nil=True)])['reason'],'NIL_ONLY')
  self.assertEqual(dup([f('1',None)])['reason'],'ACCURACY_UNAVAILABLE')
  p=dup([f('1',None,p='3')]);self.assertEqual(p['facts'][0]['reason'],'PRECISION_ATTRIBUTE_OUTSIDE_CALCULATION_PROFILE');self.assertIsNone(p['interval'])
  self.assertEqual(calc(None,[{'concept':'x','accuracy':None}])['status'],'INCOMPLETE')
 def test_modes_are_explicit_and_cannot_be_mixed_or_forged(self):
  for mode in('unknown',None,True,[]):
   with self.assertRaisesRegex(XBRLError,'rounding_mode'):enc('1','0',rounding_mode=mode)
  with self.assertRaisesRegex(XBRLError,'profile_or_mode'):calc(acc('1'),[term('1',mode='truncation')])
  with self.assertRaisesRegex(XBRLError,'profile_or_mode'):calc(duplicates([f('1')]),[term('1')])
 def test_resource_identity_weight_and_repeated_concept_admission(self):
  with self.assertRaisesRegex(XBRLError,'duplicate_budget'):dup([f()]*9)
  with self.assertRaisesRegex(XBRLError,'duplicate_identity'):dup([f(),f()])
  with self.assertRaisesRegex(XBRLError,'duplicate_values'):dup([f()],values={})
  for weight in(0,True,'1e2','1/3','0.0000000000001'):
   with self.assertRaises(XBRLError):calc(acc('1'),[term('1',weight=weight)])
  with self.assertRaisesRegex(XBRLError,'term_budget'):calc(acc('1'),[])
  with self.assertRaisesRegex(XBRLError,'term_budget'):calc(acc('1'),[term('1')]*(MAX_TERMS+1))
  with self.assertRaisesRegex(XBRLError,'duplicate_contributing_concept'):calc(acc('2'),[term('1'),term('1')])
 def test_malformed_intervals_and_nondecimal_grid_fail_closed(self):
  p=acc('1')
  variants=[]
  for change in('openpoint','badflag','badgrid','reversed','zero_denominator'):
   q=copy.deepcopy(p)
   if change=='openpoint':q['interval'].update(lower=q['interval']['upper'],lower_closed=False)
   elif change=='badflag':q['interval']['lower_closed']=1
   elif change=='badgrid':q['interval']['lower']['denominator']='3'
   elif change=='reversed':q['interval']['lower']={'numerator':'100','denominator':'1'}
   else:q['interval']['lower']['denominator']='0'
   with self.subTest(change=change),self.assertRaises(XBRLError):calc(q,[term('1')])
 def test_exact_results_survive_small_decimal_context_and_extreme_grids(self):
  expected=calc(acc('0.12345678901234567890123456789','29'),[term('0.12345678901234567890123456788','29',weight='1.000000000001')])
  with localcontext()as ctx:
   ctx.prec=2;self.assertEqual(calc(acc('0.12345678901234567890123456789','29'),[term('0.12345678901234567890123456788','29',weight='1.000000000001')]),expected)
  p=enc('1e-128','128',rounding_mode='truncation');self.assertEqual(raw(p['interval'],'lower'),Fraction(1,10**128));self.assertEqual(raw(p['interval'],'upper'),Fraction(2,10**128))
 def test_values_override_preserves_source_ids_and_original_numbers(self):
  p=dup([f(None,nil=False,id_='x')],values={'x':'1.20'});self.assertEqual(p['facts'][0]['reported_value'],'1.20');self.assertEqual(p['source_fact_ids'],['x']);self.assertIsNone(p['selected_reported_value'])
 def test_legacy_status_and_policy_are_unchanged(self):
  self.assertEqual(consistency(duplicates([f('100')]),[{'concept':'x','weight':1,'accuracy':duplicates([f('99')])}])['status'],'ROUNDING_COMPATIBLE')
  self.assertEqual(enc('1.25','1')['reason'],'DIGITS_IN_EXCESS_OF_DECLARED_PRECISION')

 def test_exact_lattice_witness_oracle_for_signs_weights_and_endpoint_closure(self):
  def contains(interval,x):
   lo=raw(interval,'lower');hi=raw(interval,'upper')
   return (x>lo or x==lo and interval['lower_closed'])and(x<hi or x==hi and interval['upper_closed'])
  points=[Fraction(i,8)for i in range(-48,49)]
  for mode in('round-to-nearest','truncation'):
   for parent in('-2','-1','0','1','2'):
    for child in('-2','-1','0','1','2'):
     for weight in('0.5','-0.5'):
      p=acc(parent,mode=mode);t=term(child,mode=mode,weight=weight);r=calc(p,[t],rounding_mode=mode)
      witness=any(contains(p['interval'],x)and contains(t['accuracy']['interval'],x/Fraction(weight))for x in points)
      self.assertEqual(r['status']=='CALCULATION_COMPATIBLE',witness,(mode,parent,child,weight))

 def test_conflicting_status_or_selected_value_cannot_supply_a_calculation_interval(self):
  for key,value in(('status','INCONSISTENT_DUPLICATES'),('status','future'),('selected_reported_value','1')):
   p=acc('1');p[key]=value
   with self.assertRaisesRegex(XBRLError,'proof_contract'):calc(p,[term('1')])
 def test_repeated_source_ids_in_one_proof_do_not_disappear_in_lineage_union(self):
  p=acc('1');p['source_fact_ids']*=2
  with self.assertRaisesRegex(XBRLError,'source_identity'):calc(p,[term('1')])
