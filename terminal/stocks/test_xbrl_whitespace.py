"""Narrow numeric whiteSpace facet; W3C XML Schema Datatypes 4.3.6."""
import unittest
from .test_xbrl_types import sample,restriction,result,proof
from .xbrl_types import WHITESPACE_PROFILE,PROFILE,COMPLEX_PROFILE
from .xbrl_instance import XBRLError

class NumericWhitespace(unittest.TestCase):
 def test_explicit_collapse_retains_numeric_value_and_facet_provenance(self):
  types=restriction(facets='<s:whiteSpace value="collapse" fixed="true"/><s:fractionDigits value="2"/>')
  p=result(sample(' \t123.4500\n',types=types),profile=WHITESPACE_PROFILE)
  self.assertEqual(p['history']['assets'][0]['value'],'123.4500')
  facets=proof(p)['numeric_value_validation']['facts'][0]['restrictions'][0]['declaration']['facets'];self.assertEqual(facets[0],{'kind':'whiteSpace','value':'collapse','fixed':True})
 def test_legacy_profiles_keep_explicit_rejection(self):
  e=sample(types=restriction(facets='<s:whiteSpace value="collapse"/>'))
  for profile in(PROFILE,COMPLEX_PROFILE):
   with self.assertRaisesRegex(XBRLError,'whitespace_profile_unsupported'):result(e,profile=profile)
 def test_internal_xml_whitespace_is_not_removed_from_digits(self):
  for value in('12 3','1\t23','1\n23'):
   with self.assertRaises(ValueError):result(sample(value,types=restriction(facets='<s:whiteSpace value="collapse"/>')),profile=WHITESPACE_PROFILE)
 def test_unsupported_whitespace_and_fixed_forms_fail_closed(self):
  for facet in('<s:whiteSpace value="preserve"/>','<s:whiteSpace value="replace"/>','<s:whiteSpace value="collapse" fixed="yes"/>','<s:whiteSpace value="collapse"/><s:whiteSpace value="collapse"/>'):
   with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):result(sample(types=restriction(facets=facet)),profile=WHITESPACE_PROFILE)
 def test_derived_range_and_fraction_facets_are_still_applied(self):
  types=restriction('Base','s:decimal','<s:whiteSpace value="collapse"/><s:minInclusive value="0"/>')+restriction('Amount','t:Base','<s:maxExclusive value="10"/>')
  self.assertTrue(result(sample('9',types=types),profile=WHITESPACE_PROFILE)['history']['assets'])
  for value in('-1','10'):
   with self.assertRaisesRegex(XBRLError,'facet_violation'):result(sample(value,types=types),profile=WHITESPACE_PROFILE)
 def test_non_numeric_base_does_not_gain_numeric_admission(self):
  with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):result(sample(types=restriction(base='s:string',facets='<s:whiteSpace value="collapse"/>')),profile=WHITESPACE_PROFILE)
