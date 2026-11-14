"""Authored numeric enumeration value-space and derivation checks; no provider."""
import copy,hashlib,unittest
from decimal import localcontext
from .test_xbrl_types import sample,restriction,result,proof
from .test_xbrl_binding import entry
from .xbrl_types import ENUMERATION_PROFILE,PROFILE,COMPLEX_PROFILE,WHITESPACE_PROFILE
from .xbrl_collection import FilingCollection
from .xbrl_instance import XBRLError

def enums(*values):return ''.join('<s:enumeration value="'+v+'"/>'for v in values)
def evaluate(value='1.00',*,types=None,kind='t:Amount'):
 return result(sample(value,kind=kind,types=restriction(facets=enums('1','2'))if types is None else types),profile=ENUMERATION_PROFILE)

class NumericEnumeration(unittest.TestCase):
 def test_membership_uses_exact_value_space_and_preserves_source_lexicals(self):
  types=restriction(facets=enums('+001.000','2.00','01'))
  v=evaluate('1.0000',types=types);p=proof(v)['numeric_value_validation']
  self.assertEqual(v['history']['assets'][0]['value'],'1.0000')
  self.assertEqual([f['value']for f in p['facts'][0]['restrictions'][0]['declaration']['facets']],['+001.000','2.00','01'])
  self.assertEqual(p['profile'],ENUMERATION_PROFILE);self.assertFalse(proof(v)['schema_type_validation'])
 def test_multiple_same_step_members_form_a_set_not_simultaneous_equalities(self):
  for value in('1','2'):
   self.assertEqual(evaluate(value)['history']['assets'][0]['value'],value)
  with self.assertRaisesRegex(XBRLError,'enumeration_violation'):evaluate('3')
 def test_inherited_membership_is_applied_at_every_derivation(self):
  types=restriction('Base','s:decimal',enums('1','2','3'))+restriction('Amount','t:Base',enums('2','3'))
  self.assertTrue(evaluate('2',types=types)['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'enumeration_violation'):evaluate('1',types=types)
 def test_invalid_member_in_derived_type_rejects_even_when_fact_would_match(self):
  types=restriction('Base','s:decimal',enums('1','2'))+restriction('Amount','t:Base',enums('1','3'))
  with self.assertRaisesRegex(XBRLError,'enumeration_violation'):evaluate('1',types=types)
 def test_unselected_member_must_satisfy_numeric_base_lexical_and_bounds(self):
  for base,values,code in [('s:unsignedByte',('1','256'),'integer_range'),('s:integer',('1','1.0'),'integer_lexical')]:
   with self.assertRaisesRegex(XBRLError,code):evaluate('1',types=restriction(base=base,facets=enums(*values)))
 def test_enumeration_definition_members_must_obey_inherited_facets(self):
  types=restriction('Base','s:decimal','<s:minExclusive value="0"/><s:maxInclusive value="10"/>')+restriction('Amount','t:Base',enums('1','11'))
  with self.assertRaisesRegex(XBRLError,'facet_violation'):evaluate('1',types=types)
 def test_scalar_facets_still_apply_alongside_enumeration(self):
  types=restriction(facets=enums('1.25','1.234')+'<s:fractionDigits value="2"/>')
  self.assertTrue(evaluate('1.25',types=types)['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'facet_violation'):evaluate('1.234',types=types)
 def test_legacy_profiles_explicitly_refuse_new_semantics(self):
  e=sample('1',types=restriction(facets=enums('1','2')))
  for profile in(PROFILE,COMPLEX_PROFILE,WHITESPACE_PROFILE):
   with self.assertRaisesRegex(XBRLError,'enumeration_profile_unsupported'):result(e,profile=profile)
 def test_decimal_context_cannot_round_membership(self):
  with localcontext()as c:
   c.prec=2
   self.assertTrue(evaluate('123456789.123456789',types=restriction(facets=enums('123456789.123456789')))['history']['assets'])
   with self.assertRaisesRegex(XBRLError,'enumeration_violation'):evaluate('123456789.123456788',types=restriction(facets=enums('123456789.123456789')))
 def test_nil_is_unavailable_but_invalid_type_member_still_rejects(self):
  e=sample('1',types=restriction(facets=enums('1')));raw=e['raw'].replace(b'>1</g:Assets>',b' xsi:nil="true"/>');doc=e['documents'][0]['raw'].replace(b'nillable="false"',b'nillable="true"');v=result(entry(raw,doc),profile=ENUMERATION_PROFILE)
  self.assertFalse(v['history']['assets']);self.assertEqual(proof(v)['numeric_value_validation']['facts'][0]['value_validation'],'NIL_UNAVAILABLE')
  e=sample('1',types=restriction(base='s:unsignedByte',facets=enums('1','256')));raw=e['raw'].replace(b'>1</g:Assets>',b' xsi:nil="true"/>');doc=e['documents'][0]['raw'].replace(b'nillable="false"',b'nillable="true"')
  with self.assertRaisesRegex(XBRLError,'integer_range'):result(entry(raw,doc),profile=ENUMERATION_PROFILE)
 def test_invalid_lexicals_structure_and_budget_fail_closed(self):
  for facets in(enums('NaN'),enums('1e2'),enums('1 2'),'<s:enumeration fixed="true" value="1"/>','<s:enumeration/>',enums(*map(str,range(17))),enums(*map(str,range(16)))+'<s:whiteSpace value="collapse"/>'):
   with self.subTest(facets=facets[:80]),self.assertRaises(XBRLError):evaluate('1',types=restriction(facets=facets))
 def test_invalid_later_filing_cannot_replace_prior_collection(self):
  c=FilingCollection('0000320193');e=sample('1',types=restriction(facets=enums('1')));before=copy.deepcopy(e);c.ingest_dts_batch([e],numeric_profile=ENUMERATION_PROFILE);page=c.page()
  with self.assertRaisesRegex(XBRLError,'enumeration_violation'):c.ingest_dts_batch([sample('2',types=restriction(facets=enums('1')),accession='0000000123-24-000002')],numeric_profile=ENUMERATION_PROFILE)
  self.assertEqual(c.page(),page);self.assertEqual(e,before)
 def test_numeric_whitespace_is_supported_only_with_numeric_base(self):
  types=restriction(facets='<s:whiteSpace value="collapse"/>'+enums(' \t1.00\n'))
  self.assertTrue(evaluate('1',types=types)['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):evaluate('1',types=restriction(base='s:string',facets=enums('1')))
 def test_conflicting_reported_members_are_not_silently_selected(self):
  e=sample('1',types=restriction(facets=enums('1','2')))
  raw=e['raw'].replace(b'</x:xbrl>',b'<g:Assets contextRef="I" unitRef="USD">2</g:Assets></x:xbrl>');e=entry(raw,e['documents'][0]['raw'])
  v=result(e,profile=ENUMERATION_PROFILE)
  self.assertFalse(v['history']['assets']);self.assertEqual(len(proof(v)['numeric_value_validation']['facts']),2)
  self.assertEqual(v['selected_input_coverage'][0]['xbrl_coverage']['excluded']['unverified_or_conflicting'],2)
