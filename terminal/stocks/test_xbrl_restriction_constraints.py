"""Bounded schema restriction-definition checks, separate from fact validity."""
import unittest,hashlib
from decimal import localcontext
from .test_xbrl_types import sample,restriction,result,proof
from .test_xbrl_binding import entry
from .xbrl_types import RESTRICTION_PROFILE,PROFILE,COMPLEX_PROFILE,WHITESPACE_PROFILE,ENUMERATION_PROFILE
from .xbrl_collection import FilingCollection
from .xbrl_instance import XBRLError

def evaluate(types,value='1',kind='t:Amount'):return result(sample(value,kind=kind,types=types),profile=RESTRICTION_PROFILE)
def nil_sample(types):
 e=sample('1',types=types);raw=e['raw'].replace(b'>1</g:Assets>',b' xsi:nil="true"/>');doc=e['documents'][0]['raw'].replace(b'nillable="false"',b'nillable="true"');return entry(raw,doc)
class RestrictionConstraints(unittest.TestCase):
 def test_fixed_digits_preserve_source_and_equal_value_lexicals(self):
  types=restriction('Base','s:decimal','<s:totalDigits value="06" fixed="true"/>')+restriction('Amount','t:Base','<s:totalDigits value="6" fixed="false"/><s:fractionDigits value="2"/>')
  p=proof(evaluate(types,'123.45'))['numeric_value_validation'];self.assertEqual(p['restriction_definition_validation'],'BOUNDED_DIGITS_FIXED_AND_LOCAL_BOUNDS_V1');self.assertTrue(p['facts'][0]['restrictions'][1]['declaration']['facets'][0]['fixed'])
 def test_legacy_profiles_refuse_explicit_fixed_digit_support(self):
  e=sample(types=restriction(facets='<s:totalDigits value="6" fixed="true"/>'))
  for profile in(PROFILE,COMPLEX_PROFILE,WHITESPACE_PROFILE,ENUMERATION_PROFILE):
   with self.assertRaisesRegex(XBRLError,'fixed_profile_unsupported'):result(e,profile=profile)
 def test_fixed_narrowing_or_widening_reject_even_matching_fact(self):
  for value in('5','7'):
   types=restriction('Base','s:decimal','<s:totalDigits value="6" fixed="1"/>')+restriction('Amount','t:Base',f'<s:totalDigits value="{value}"/>')
   with self.assertRaisesRegex(XBRLError,'fixed_digit'):evaluate(types)
 def test_nonfixed_digit_limits_can_narrow_but_not_widen(self):
  base=restriction('Base','s:decimal','<s:totalDigits value="6"/><s:fractionDigits value="2"/>')
  self.assertTrue(evaluate(base+restriction('Amount','t:Base','<s:totalDigits value="3"/><s:fractionDigits value="1"/>'),'1.2')['history']['assets'])
  for f in('<s:totalDigits value="7"/>','<s:fractionDigits value="3"/>'):
   with self.assertRaisesRegex(XBRLError,'digit_widening'):evaluate(base+restriction('Amount','t:Base',f))
 def test_inherited_fraction_digits_cannot_exceed_total_digits(self):
  for types in(restriction(facets='<s:totalDigits value="2"/><s:fractionDigits value="3"/>'),restriction('Base','s:decimal','<s:fractionDigits value="3"/>')+restriction('Amount','t:Base','<s:totalDigits value="2"/>')):
   with self.assertRaisesRegex(XBRLError,'fraction_exceeds_total'):evaluate(types)
 def test_builtin_integer_fraction_digits_remains_fixed_zero(self):
  self.assertTrue(evaluate(restriction(base='s:integer',facets='<s:fractionDigits value="0" fixed="true"/>'))['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'fixed_digit'):evaluate(restriction(base='s:integer',facets='<s:fractionDigits value="1"/>'))
 def test_contradictory_bounds_reject_for_nil_facts(self):
  for facets in('<s:minInclusive value="10"/><s:maxInclusive value="0"/>','<s:minInclusive value="0"/><s:minExclusive value="0"/>','<s:maxInclusive value="10"/><s:maxExclusive value="10"/>'):
   with self.assertRaisesRegex(XBRLError,'restriction_'):result(nil_sample(restriction(facets=facets)),profile=RESTRICTION_PROFILE)
 def test_closed_singleton_valid_and_empty_interval_explicitly_unsupported(self):
  self.assertTrue(evaluate(restriction(facets='<s:minInclusive value="1"/><s:maxInclusive value="1"/>'))['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'empty_interval_unsupported'):evaluate(restriction(facets='<s:minExclusive value="1"/><s:maxInclusive value="1"/>'))
 def test_bound_lexicals_must_match_numeric_base_even_for_nil(self):
  e=nil_sample(restriction(base='s:unsignedByte',facets='<s:maxInclusive value="256"/>'))
  with self.assertRaisesRegex(XBRLError,'integer_range'):result(e,profile=RESTRICTION_PROFILE)
 def test_fixed_boolean_is_strict_and_unknown_fixed_facets_stay_unsupported(self):
  with self.assertRaisesRegex(XBRLError,'fixed_boolean'):evaluate(restriction(facets='<s:totalDigits value="6" fixed="yes"/>'))
  with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):evaluate(restriction(facets='<s:minInclusive value="0" fixed="true"/>'))
 def test_low_decimal_precision_cannot_round_bound_order(self):
  with localcontext()as ctx:
   ctx.prec=2
   with self.assertRaisesRegex(XBRLError,'reversed_bounds'):evaluate(restriction(facets='<s:minInclusive value="123456789.123456790"/><s:maxInclusive value="123456789.123456789"/>'))
 def test_failed_batch_keeps_original_collection_and_sources(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([sample()],numeric_profile=RESTRICTION_PROFILE);before=c.page()
  with self.assertRaises(XBRLError):c.ingest_dts_batch([sample(accession='0000000123-24-000002'),sample(types=restriction(facets='<s:fractionDigits value="2"/><s:totalDigits value="1"/>'),accession='0000000123-24-000003')],numeric_profile=RESTRICTION_PROFILE)
  self.assertEqual(c.page(),before)
