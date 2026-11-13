"""Independent exact endpoint expectations,including adversarial rounding cases."""
import unittest
from decimal import localcontext
from fractions import Fraction
from .xbrl_accuracy import enclosure,duplicates,consistency
from .xbrl_instance import XBRLError

def f(value='100',d='0',p=None,id_='a',nil=False):return {'source_fact_id':id_,'value':value,'nil':nil,'decimals':d,'precision':p}
def raw(interval,key):
 x=interval[key];return Fraction(int(x['numerator']),int(x['denominator']))
def acc(value,d='0'):return duplicates([f(value,d)])
class Accuracy(unittest.TestCase):
 def test_integer_decimals_and_negative_amount_have_exact_endpoints(self):
  for value,lo,hi in [('100','199/2','201/2'),('-100','-201/2','-199/2'),('0','-1/2','1/2')]:
   i=enclosure(value,'0')['interval'];self.assertEqual(raw(i,'lower'),Fraction(lo));self.assertEqual(raw(i,'upper'),Fraction(hi))
 def test_negative_decimals_and_fractional_values(self):
  i=enclosure('1200','-2')['interval'];self.assertEqual(raw(i,'lower'),1150);self.assertEqual(raw(i,'upper'),1250)
  i=enclosure('0.125','3')['interval'];self.assertEqual(raw(i,'lower'),Fraction(249,2000));self.assertEqual(raw(i,'upper'),Fraction(251,2000))
 def test_precision_inference_exact_large_small_and_negative(self):
  for value,p,d in [('1230','3',-1),('-0.0123','3',4),('1E+30','1',-30),('1E-128','1',128)]:self.assertEqual(enclosure(value,None,p)['effective_decimals'],d)
 def test_infinite_accuracy_is_a_point_even_for_zero(self):
  for d,p in [('INF',None),(None,'INF')]:
   i=enclosure('0',d,p)['interval'];self.assertEqual(raw(i,'lower'),0);self.assertEqual(raw(i,'upper'),0)
 def test_no_accuracy_nil_and_finite_precision_zero_do_not_invent_bounds(self):
  self.assertEqual(enclosure('1')['reason'],'ACCURACY_NOT_DECLARED');self.assertEqual(enclosure(None,nil=True)['reason'],'NIL_REPORTED');self.assertEqual(enclosure('0',None,'3')['reason'],'ZERO_WITH_FINITE_PRECISION_UNSUPPORTED')
 def test_noncanonical_numeric_accuracy_and_extreme_exponents_are_explicit(self):
  self.assertEqual(enclosure('1.25','1')['reason'],'NONCANONICAL_REPORTED_ACCURACY_UNSUPPORTED');self.assertEqual(enclosure('1','999')['reason'],'ACCURACY_EXPONENT_OUTSIDE_PROFILE')
  with self.assertRaises(XBRLError):enclosure('1E-999','1')
 def test_malformed_or_ambiguous_accuracy_is_rejected(self):
  for args in [('1','0','2'),('1','NaN',None),('1',None,'0'),('1',None,'-2'),('1',True,None),('1','1e2',None)]:
   with self.subTest(args=args),self.assertRaises(XBRLError):enclosure(*args)
 def test_nil_cannot_carry_a_value(self):
  with self.assertRaises(XBRLError):enclosure('0',nil=True)
 def test_rounding_compatible_despite_nonzero_exact_residual(self):
  r=consistency(acc('100'),[{'concept':'child','weight':1,'accuracy':acc('99')}]);self.assertEqual(r['status'],'ROUNDING_COMPATIBLE');self.assertEqual(raw(r['residual_interval'],'lower'),0)
 def test_disjoint_intervals_prove_inconsistency_within_profile(self):
  r=consistency(acc('100'),[{'concept':'child','weight':1,'accuracy':acc('98')}]);self.assertEqual(r['status'],'DEFINITELY_INCONSISTENT');self.assertGreater(raw(r['residual_interval'],'lower'),0)
 def test_negative_weights_swap_bounds(self):
  r=consistency(acc('1','INF'),[{'concept':'a','weight':1,'accuracy':acc('3','INF')},{'concept':'b','weight':-1,'accuracy':acc('2','0')}]);self.assertEqual(r['status'],'ROUNDING_COMPATIBLE');self.assertEqual(raw(r['weighted_sum_interval'],'lower'),Fraction(1,2));self.assertEqual(raw(r['weighted_sum_interval'],'upper'),Fraction(3,2))
 def test_consistent_duplicates_intersect_without_dropping_lineage(self):
  r=duplicates([f(d='0'),f(d='1',id_='b')]);self.assertEqual(raw(r['interval'],'lower'),Fraction(1999,20));self.assertEqual(r['source_fact_ids'],['a','b'])
 def test_conflicting_duplicates_never_resolve_by_rounding(self):
  r=duplicates([f('100'),f('101',id_='b')]);self.assertEqual(r['reason'],'CONFLICTING_DUPLICATE_VALUES');self.assertIsNone(r['interval'])
 def test_unknown_accuracy_duplicate_and_missing_terms_stay_unavailable(self):
  d=duplicates([f(),f(d=None,id_='b')]);self.assertIsNone(d['interval']);self.assertEqual(consistency(d,[{'concept':'a','weight':1,'accuracy':acc('1')}])['status'],'UNSUPPORTED_ACCURACY');self.assertEqual(consistency(None,[{'concept':'a','accuracy':None}])['status'],'INCOMPLETE')
 def test_resource_and_weight_bounds(self):
  with self.assertRaises(XBRLError):duplicates([f()]*9)
  with self.assertRaises(XBRLError):consistency(acc('1'),[{'concept':'a','weight':0,'accuracy':acc('1')}])
  with self.assertRaises(XBRLError):consistency(acc('1'),[])
 def test_binary_and_decimal_rounding_context_cannot_change_the_result(self):
  expected=enclosure('0.12345678901234567890123456789','29')
  with localcontext()as ctx:
   ctx.prec=2;self.assertEqual(enclosure('0.12345678901234567890123456789','29'),expected)
