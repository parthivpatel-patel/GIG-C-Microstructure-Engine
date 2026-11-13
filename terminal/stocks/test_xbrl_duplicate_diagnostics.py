"""Duplicate ambiguity expectations independent of any source-value selection."""
import copy,unittest
from .test_xbrl_accuracy import f,raw
from .xbrl_accuracy import duplicate_diagnostic
from .test_xbrl_statement_v2 import extension,view,extrow
class DuplicateDiagnostics(unittest.TestCase):
 def test_distinct_values_with_touching_accuracy_are_ambiguous_not_resolved(self):
  r=duplicate_diagnostic([f('100'),f('101',id_='b')]);self.assertEqual(r['status'],'OVERLAPPING_ACCURACY_AMBIGUOUS');self.assertEqual(raw(r['intersection_interval'],'lower'),raw(r['intersection_interval'],'upper'));self.assertFalse(r['numeric_values_equal'])
 def test_disjoint_and_infinite_accuracy_conflicts_remain_explicit(self):
  self.assertEqual(duplicate_diagnostic([f('100'),f('102',id_='b')])['status'],'DISJOINT_ACCURACY_DUPLICATES');self.assertEqual(duplicate_diagnostic([f('100','INF'),f('101','INF',id_='b')])['status'],'DISJOINT_ACCURACY_DUPLICATES')
 def test_equal_values_do_not_lose_precision_or_any_original_source(self):
  rows=[f('100'),f('100.0','1',id_='b')];before=copy.deepcopy(rows);r=duplicate_diagnostic(rows);self.assertEqual(r['status'],'NUMERICALLY_IDENTICAL');self.assertEqual(r['source_fact_ids'],['a','b']);self.assertEqual(rows,before)
 def test_nil_missing_accuracy_and_noncanonical_accuracy_do_not_create_points(self):
  self.assertEqual(duplicate_diagnostic([f(None,None,nil=True)])['status'],'NIL_ONLY');self.assertEqual(duplicate_diagnostic([f(None,None,nil=True),f('100',id_='b')])['status'],'MIXED_NIL_CONFLICT');self.assertEqual(duplicate_diagnostic([f('100'),f('101',None,id_='b')])['status'],'ACCURACY_UNAVAILABLE')
 def test_negative_values_and_zero_are_not_dropped(self):
  self.assertEqual(duplicate_diagnostic([f('-1'),f('0',id_='b')])['status'],'OVERLAPPING_ACCURACY_AMBIGUOUS');self.assertTrue(duplicate_diagnostic([f('0'),f('0',id_='b')])['numeric_values_equal'])
 def test_product_keeps_conflicting_extension_unavailable_despite_overlap(self):
  e=extension(extra='<ext:CompanyLiquidity contextRef="I" unitRef="USD" decimals="0">401</ext:CompanyLiquidity>');r=view(e);row=extrow(r);self.assertEqual(row['status'],'CONFLICT');self.assertIsNone(row['value']);self.assertEqual(row['duplicate_diagnostic']['status'],'OVERLAPPING_ACCURACY_AMBIGUOUS');self.assertEqual(r['periods'][0]['calculations'][0]['status'],'INCOMPLETE')
