"""Independent numeric/facet expectations against authored supplied taxonomies."""
import copy,unittest
from decimal import localcontext
from .test_xbrl_binding import entry,declaration
from .test_xbrl_instance import xml,NS,manifest
from .xbrl_collection import FilingCollection
from .xbrl_types import PROFILE
from .xbrl_instance import XBRLError

def restriction(name='Amount',base='s:decimal',facets='<s:totalDigits value="6"/><s:fractionDigits value="2"/>'):
 return '<s:simpleType name="'+name+'"><s:restriction base="'+base+'">'+facets+'</s:restriction></s:simpleType>'
def sample(value='123.4500',kind='t:Amount',types=None,**meta):
 raw=xml('<g:Assets contextRef="I" unitRef="USD">'+value+'</g:Assets>');doc=declaration().replace(b'<s:schema',('<s:schema xmlns:t="'+NS+'"').encode(),1).replace(b'type="x:monetaryItemType"',('type="'+kind+'"').encode())
 doc=doc.replace(b'</s:schema>',(restriction()if types is None else types).encode()+b'</s:schema>')
 return entry(raw,doc,**meta)
def result(e,*,profile=PROFILE):
 c=FilingCollection('0000320193');c.ingest_dts_batch([e],numeric_profile=profile);return c.at_acceptance_time('2024-02-02T00:00:00Z')
def proof(v):return v['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']
class NumericTypes(unittest.TestCase):
 def test_restriction_value_and_provenance_are_exact_and_not_schema_clearance(self):
  e=sample();before=copy.deepcopy(e);v=result(e);p=proof(v);self.assertEqual(v['history']['assets'][0]['value'],'123.4500');self.assertEqual(p['numeric_value_validation']['profile'],PROFILE);self.assertFalse(p['schema_type_validation']);self.assertFalse(p['complete_statements']);self.assertEqual(p['numeric_value_validation']['facts'][0]['restrictions'][0]['source_documents'],['https://authored.invalid/authored.xsd']);self.assertEqual(e,before)
 def test_digit_facets_count_values_instead_of_lexical_padding(self):
  for value in('000123.4500','0.0000','9999.99'):self.assertTrue(result(sample(value))['history']['assets'])
  for value in('12345.67','1.234','0.001'):
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'facet_violation'):result(sample(value))
 def test_decimal_context_precision_cannot_round_facet_checks(self):
  with localcontext()as ctx:
   ctx.prec=2;self.assertEqual(result(sample('123.4500'))['history']['assets'][0]['value'],'123.4500')
   with self.assertRaisesRegex(XBRLError,'facet_violation'):result(sample('123.456'))
 def test_inclusive_and_exclusive_bounds_are_applied_at_every_derivation(self):
  types=restriction('Base','s:decimal','<s:minInclusive value="0"/><s:maxInclusive value="10"/>')+restriction('Amount','t:Base','<s:minExclusive value="2"/><s:maxExclusive value="9"/>')
  self.assertTrue(result(sample('2.001',types=types))['history']['assets'])
  for value in('-1','0','2','9','10','11'):
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'facet_violation'):result(sample(value,types=types))
 def test_integer_lexical_and_signed_unsigned_bounds_are_not_suppressed(self):
  for value in('0','255','+001'):self.assertTrue(result(sample(value,'s:unsignedByte',types=''))['history']['assets'])
  for value in('-1','256','1.0'):
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'integer_'):result(sample(value,'s:unsignedByte',types=''))
  self.assertTrue(result(sample(str(-(2**63)),'s:long',types=''))['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'integer_range'):result(sample(str(2**63),'s:long',types=''))
 def test_standard_monetary_unit_matches_selected_contract(self):
  self.assertTrue(result(sample('123','x:monetaryItemType',types=''))['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'type_unit'):result(sample('123','x:sharesItemType',types=''))
 def test_unknown_custom_or_nonnumeric_type_fails_only_explicit_strict_profile(self):
  for kind,types in [('t:Missing',''),('s:string',''),('t:Amount','<s:complexType name="Amount"/>')]:
   e=sample(kind=kind,types=types);self.assertNotIn('numeric_value_validation',proof(result(e,profile=None)))
   with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):result(e)
 def test_cycles_depth_and_unsupported_facets_fail_closed(self):
  for types in(restriction('Amount','t:Amount'),restriction(facets='<s:pattern value="[0-9]+"/>'),restriction(facets='<s:fractionDigits value="2"/><s:fractionDigits value="3"/>'),''.join(restriction('Amount'if i==0 else'T'+str(i),'t:T'+str(i+1),'')for i in range(9))):
   with self.assertRaises(XBRLError):result(sample(types=types))
 def test_conflicting_duplicate_and_over_budget_types_reject_atomically(self):
  for types in(restriction()+restriction(),restriction()+restriction(base='s:integer'),''.join(restriction('T'+str(i))for i in range(129))):
   with self.assertRaises(XBRLError):result(sample(types=types))
 def test_invalid_later_type_filing_preserves_accepted_collection(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([sample()],numeric_profile=PROFILE);before=c.at_acceptance_time('2024-02-02T00:00:00Z')
  with self.assertRaises(XBRLError):c.ingest_dts_batch([sample(accession='0000000123-24-000002'),sample('1.234',accession='0000000123-24-000003')],numeric_profile=PROFILE)
  self.assertEqual(c.at_acceptance_time('2024-02-02T00:00:00Z'),before)
 def test_nil_has_missing_value_and_keeps_declaration_checks(self):
  e=sample();raw=e['raw'].replace(b'>123.4500</g:Assets>',b' xsi:nil="true"/>');doc=e['documents'][0]['raw'].replace(b'nillable="false"',b'nillable="true"');e=entry(raw,doc);p=proof(result(e));self.assertEqual(p['numeric_value_validation']['facts'][0]['value_validation'],'NIL_UNAVAILABLE');self.assertFalse(result(e)['history']['assets'])
 def test_profile_and_substitution_are_explicit(self):
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):result(sample(),profile='invented')
  e=sample();doc=e['documents'][0]['raw'].replace(b'substitutionGroup="x:item"',b'substitutionGroup="x:tuple"');e=entry(e['raw'],doc)
  with self.assertRaisesRegex(XBRLError,'substitution_unsupported'):result(e)
 def test_invalid_facet_values_are_not_accepted_as_valid_types(self):
  for f in('<s:totalDigits value="0"/>','<s:fractionDigits value="65"/>','<s:minInclusive value="NaN"/>'):
   with self.assertRaises(XBRLError):result(sample(types=restriction(facets=f)))
 def test_direct_corroboration_rejects_modified_hashed_inputs(self):
  from .xbrl_dts import discover
  from .xbrl_instance import parse_instance,selected_concepts
  from .xbrl_binding import bind_declarations
  from .xbrl_types import corroborate
  e=sample();g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);p=bind_declarations(parse_instance(e['raw'],e['manifest'],selected_concepts(NS)),g)
  for component in('instance','graph'):
   a,b=copy.deepcopy(p),copy.deepcopy(g)
   if component=='instance':a['facts'][0]['lexical_value']='0'
   else:b['type_declarations']['{'+NS+'}Amount']['declaration']['facets']=[]
   with self.assertRaisesRegex(XBRLError,'input_identity'):corroborate(a,b)
 def test_type_evidence_is_bounded_before_record_accumulation(self):
  from unittest.mock import patch
  with patch('terminal.stocks.xbrl_types.MAX_OUTPUT_BYTES',1):
   with self.assertRaisesRegex(XBRLError,'output_budget'):result(sample())
 def test_standard_xbrl_integer_and_zero_are_not_coerced(self):
  self.assertTrue(result(sample('0','x:nonNegativeIntegerItemType',types=''))['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'integer_range'):result(sample('-1','x:nonNegativeIntegerItemType',types=''))
  with self.assertRaisesRegex(XBRLError,'integer_lexical'):result(sample('1.0','x:integerItemType',types=''))
 def test_numeric_whitespace_does_not_expand_xml_schema_lexical_space(self):
  self.assertTrue(result(sample(' \t123.4500\n'))['history']['assets'])
  with self.assertRaisesRegex(XBRLError,'decimal_lexical'):result(sample('\u00a0123.4500\u00a0'))
 def test_simple_content_extension_requires_explicit_v2_profile(self):
  from .xbrl_types import COMPLEX_PROFILE
  types='<s:complexType name="Amount"><s:simpleContent><s:extension base="x:monetaryItemType"/></s:simpleContent></s:complexType>';e=sample(types=types)
  with self.assertRaisesRegex(XBRLError,'type_profile_unsupported'):result(e)
  v=result(e,profile=COMPLEX_PROFILE);self.assertEqual(v['history']['assets'][0]['value'],'123.4500');p=proof(v);self.assertEqual(p['numeric_value_validation']['profile'],COMPLEX_PROFILE);self.assertFalse(p['schema_type_validation'])
 def test_simple_content_restriction_inherits_base_facets_and_units(self):
  from .xbrl_types import COMPLEX_PROFILE
  types='<s:complexType name="Base"><s:simpleContent><s:extension base="x:monetaryItemType"/></s:simpleContent></s:complexType><s:complexType name="Amount"><s:simpleContent><s:restriction base="t:Base"><s:minInclusive value="0"/><s:maxExclusive value="1000"/><s:fractionDigits value="2"/></s:restriction></s:simpleContent></s:complexType>'
  self.assertTrue(result(sample(types=types),profile=COMPLEX_PROFILE)['history']['assets'])
  for value in('-1','1000','1.234'):
   with self.subTest(value=value),self.assertRaisesRegex(XBRLError,'facet_violation'):result(sample(value,types=types),profile=COMPLEX_PROFILE)
 def test_complex_content_attributes_wildcards_and_mixed_types_remain_unsupported(self):
  from .xbrl_types import COMPLEX_PROFILE
  for body in('<s:complexContent><s:extension base="x:monetaryItemType"/></s:complexContent>','<s:simpleContent><s:extension base="x:monetaryItemType"><s:attribute name="extra"/></s:extension></s:simpleContent>','<s:simpleContent><s:restriction base="x:monetaryItemType"><s:anyAttribute/></s:restriction></s:simpleContent>'):
   with self.assertRaisesRegex(XBRLError,'selected_type_unsupported'):result(sample(types='<s:complexType name="Amount">'+body+'</s:complexType>'),profile=COMPLEX_PROFILE)
 def test_v2_complex_derivation_cycles_and_invalid_later_filing_are_atomic(self):
  from .xbrl_types import COMPLEX_PROFILE
  types='<s:complexType name="Amount"><s:simpleContent><s:extension base="t:Amount"/></s:simpleContent></s:complexType>'
  with self.assertRaisesRegex(XBRLError,'type_cycle'):result(sample(types=types),profile=COMPLEX_PROFILE)
  c=FilingCollection('0000320193');c.ingest_dts_batch([sample()],numeric_profile=COMPLEX_PROFILE);before=c.page()
  with self.assertRaises(XBRLError):c.ingest_dts_batch([sample(types=types,accession='0000000123-24-000002')],numeric_profile=COMPLEX_PROFILE)
  self.assertEqual(c.page(),before)
