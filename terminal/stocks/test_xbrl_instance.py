"""Authored XBRL instances; independent expected contexts,exact facts and failures."""
import copy,hashlib,unittest
from .xbrl_instance import parse_instance,selected_concepts,selected_financials,XBRLError,tag,X,ISO

NS='http://fasb.org/us-gaap/2024'
def xml(facts=None,extra='',*,context_extra='',unit_extra=''):
 facts=facts if facts is not None else '<g:Revenues contextRef="D" unitRef="USD" decimals="0">100.00</g:Revenues><g:NetIncomeLoss contextRef="D" unitRef="USD" decimals="0">-20</g:NetIncomeLoss><g:Assets contextRef="I" unitRef="USD" decimals="INF">1000</g:Assets>'
 return f'''<?xml version="1.0" encoding="UTF-8"?><x:xbrl xmlns:x="http://www.xbrl.org/2003/instance" xmlns:g="{NS}" xmlns:iso="http://www.xbrl.org/2003/iso4217" xmlns:d="http://xbrl.org/2006/xbrldi" xmlns:ext="https://authored.invalid/taxonomy" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink">
 <l:schemaRef xl:type="simple" xl:href="authored.xsd"/>
 <x:context id="D"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier></x:entity><x:period><x:startDate>2023-01-01</x:startDate><x:endDate>2023-12-31</x:endDate></x:period></x:context>
 <x:context id="I"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier>{context_extra}</x:entity><x:period><x:instant>2023-12-31</x:instant></x:period></x:context>
 <x:unit id="USD"><x:measure>iso:USD</x:measure></x:unit>{unit_extra}{extra}{facts}</x:xbrl>'''.encode()
def manifest(raw,**patch):
 m={'issuer_cik':'0000320193','accession':'0000000123-24-000001','form':'10-K','filed':'2024-02-01','accepted_at':'2024-02-01T12:00:00.000000001Z','received_at':None,'origin':'HISTORICAL_SYNTHETIC','source_sha256':hashlib.sha256(raw).hexdigest(),'source_url':None,'amends_accession':None,'permission_reference':None};return {**m,**patch}
def parsed(raw=None,**kw):
 raw=xml()if raw is None else raw;return parse_instance(raw,manifest(raw,**kw),selected_concepts(NS))

class XBRLInstance(unittest.TestCase):
 def test_profile_cannot_relabel_concepts_units_or_periods_for_selected_financials(self):
  raw=xml()
  for patch in [{'local_name':'NetIncomeLoss'},{'numerator':[tag(X,'shares')]},{'period_type':'duration'}]:
   profile=selected_concepts(NS);profile[tag(NS,'Assets')].update(patch)
   with self.subTest(patch=patch),self.assertRaises(XBRLError):parse_instance(raw,manifest(raw),profile)
 def test_context_unit_exact_values_and_source_lexical_provenance(self):
  raw=xml();p=parsed(raw);self.assertEqual(p['contexts']['D']['period'],{'kind':'duration','start':'2023-01-01','end':'2023-12-31'});self.assertEqual(p['facts'][0]['lexical_value'],'100.00');self.assertEqual(p['facts'][0]['value'],'100.00');self.assertEqual(p['facts'][1]['value'],'-20');self.assertFalse(p['schema_references'][0]['fetched']);self.assertEqual(p['source']['source_sha256'],hashlib.sha256(raw).hexdigest())
  f=selected_financials(p);self.assertEqual(f['history']['revenue'][0]['value'],'100.00');self.assertEqual(f['history']['net_income'][0]['value'],'-20');self.assertTrue(f['history']['revenue'][0]['source_xml_fact_ids']);self.assertIsNone(f['xbrl_coverage']['original_received_at'])
 def test_context_dimensions_are_retained_and_never_aggregated_as_consolidated_assets(self):
  member='<x:segment><d:explicitMember dimension="ext:RegionAxis">ext:NorthMember</d:explicitMember></x:segment>';p=parsed(xml(context_extra=member));self.assertEqual(p['contexts']['I']['dimensions'][0]['member'],'{https://authored.invalid/taxonomy}NorthMember');self.assertEqual(selected_financials(p)['history']['assets'],[]);self.assertEqual(selected_financials(p)['xbrl_coverage']['excluded']['dimensioned_or_opaque'],1)
 def test_typed_dimensions_and_opaque_segments_remain_explicit(self):
  member='<x:segment><d:typedMember dimension="ext:DeskAxis"><ext:Desk code="A">Rates</ext:Desk></d:typedMember><ext:Other>opaque</ext:Other></x:segment>';p=parsed(xml(context_extra=member));self.assertEqual(p['contexts']['I']['dimensions'][0]['kind'],'typed');self.assertEqual(p['contexts']['I']['opaque_segment'][0]['text'],'opaque');self.assertEqual(selected_financials(p)['history']['assets'],[])
 def test_nil_is_unavailable_not_zero_and_bad_nil_content_rejects(self):
  p=parsed(xml('<g:Assets contextRef="I" unitRef="USD" xsi:nil="true"/>'));self.assertTrue(p['facts'][0]['nil']);self.assertIsNone(p['facts'][0]['value']);self.assertEqual(selected_financials(p)['history']['assets'],[])
  with self.assertRaisesRegex(XBRLError,'nil_with_value'):parsed(xml('<g:Assets contextRef="I" unitRef="USD" xsi:nil="true">0</g:Assets>'))
 def test_consistent_duplicates_preserve_source_ids_and_conflicts_remove_eligibility(self):
  fact='<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>';p=parsed(xml(fact+fact));self.assertEqual(p['consistent_duplicate_facts'],1);f=selected_financials(p);self.assertEqual(len(f['history']['assets']),1);self.assertEqual(len(f['history']['assets'][0]['source_xml_fact_ids']),2)
  p=parsed(xml(fact+fact.replace('1000','1001')));self.assertEqual(len(p['conflicts']),1);self.assertTrue(all(r['admission']=='CONFLICTED_EXACT_VALUES'for r in p['facts']));self.assertEqual(selected_financials(p)['history']['assets'],[])
 def test_unknown_concepts_are_retained_without_a_financial_mapping(self):
  p=parsed(xml('<ext:CustomMetric contextRef="I" unitRef="USD">77</ext:CustomMetric>'));self.assertEqual(p['facts'][0]['admission'],'UNVERIFIED_CONCEPT');self.assertEqual(p['facts'][0]['lexical_value'],'77');self.assertTrue(all(not rows for rows in selected_financials(p)['history'].values()))
 def test_unit_division_and_precision_are_preserved_without_rounding(self):
  u='<x:unit id="PER"><x:divide><x:unitNumerator><x:measure>iso:USD</x:measure></x:unitNumerator><x:unitDenominator><x:measure>x:shares</x:measure></x:unitDenominator></x:divide></x:unit>'
  p=parsed(xml('<g:EarningsPerShareDiluted contextRef="D" unitRef="PER" decimals="2">1.234567890123</g:EarningsPerShareDiluted>',unit_extra=u));self.assertEqual(p['facts'][0]['decimals'],'2');self.assertEqual(selected_financials(p)['history']['eps'][0]['value'],'1.234567890123')
 def test_unknown_refs_duplicate_ids_and_wrong_issuer_fail_before_any_result(self):
  cases=[xml().replace(b'contextRef="D"',b'contextRef="missing"'),xml().replace(b'unitRef="USD"',b'unitRef="missing"'),xml(extra='<x:unit id="USD"><x:measure>iso:USD</x:measure></x:unit>'),xml().replace(b'0000320193',b'0000000001')]
  for raw in cases:
   with self.subTest(raw_length=len(raw)),self.assertRaises(ValueError):parsed(raw)
 def test_dtd_entities_processing_instructions_xinclude_and_inline_are_refused(self):
  raw=xml();cases=[raw.replace(b'<x:xbrl',b'<!DOCTYPE xbrl [<!ENTITY leak SYSTEM "file:///etc/passwd">]><x:xbrl',1),raw.replace(b'<x:xbrl',b'<?xml-stylesheet href="https://invalid.example"?><x:xbrl',1),xml(extra='<xi:include xmlns:xi="http://www.w3.org/2001/XInclude" href="file:///etc/passwd"/>'),b'<html xmlns="http://www.w3.org/1999/xhtml"/>']
  for value in cases:
   with self.subTest(length=len(value)),self.assertRaises(XBRLError):parsed(value)
 def test_period_unit_and_concept_mismatches_never_become_selected_financials(self):
  p=parsed(xml('<g:Assets contextRef="D" unitRef="USD">99</g:Assets>'));self.assertEqual(p['facts'][0]['admission'],'PERIOD_OR_UNIT_MISMATCH');self.assertEqual(selected_financials(p)['history']['assets'],[])
 def test_observed_input_requires_explicit_policy_and_exact_source_identity(self):
  raw=xml()
  with self.assertRaisesRegex(XBRLError,'not_approved'):parse_instance(raw,manifest(raw,origin='OBSERVED_OFFICIAL_RESPONSE'),selected_concepts(NS))
  m=manifest(raw,origin='OBSERVED_OFFICIAL_RESPONSE',source_url='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/authored.xml',permission_reference='authored-policy-reference')
  p=parse_instance(raw,m,selected_concepts(NS),allow_observed=True);self.assertNotIn('permission_reference',p['source']);self.assertIsNotNone(p['source']['permission_reference_sha256'])
  m['source_url']=m['source_url'].replace('/320193/','/1/')
  with self.assertRaisesRegex(XBRLError,'source_identity'):parse_instance(raw,m,selected_concepts(NS),allow_observed=True)
 def test_source_digest_and_parsed_digest_and_unsafe_manifest_authority_reject(self):
  raw=xml()
  with self.assertRaisesRegex(XBRLError,'source_digest'):parse_instance(raw,manifest(raw,source_sha256='0'*64),selected_concepts(NS))
  p=parsed(raw);p['facts'][0]['value']='999'
  with self.assertRaisesRegex(XBRLError,'parsed_digest'):selected_financials(p)
  with self.assertRaisesRegex(XBRLError,'manifest_fields'):parse_instance(raw,{**manifest(raw),'fetch_url':'https://invalid'},selected_concepts(NS))
 def test_missing_acceptance_and_amendment_target_remain_unknown(self):
  p=parsed(form='10-K/A',accession='0000000123-24-000002',accepted_at=None);self.assertIsNone(p['source']['accepted_at']);self.assertIsNone(p['source']['amends_accession']);self.assertTrue(p['source']['form'].endswith('/A'))
 def test_resource_limits_numeric_overflow_and_malformed_precision_fail_closed(self):
  cases=[b'x'*(2*1024*1024+1),xml('<g:Assets contextRef="I" unitRef="USD">NaN</g:Assets>'),xml('<g:Assets contextRef="I" unitRef="USD" decimals="0" precision="2">100</g:Assets>'),xml().replace(b'2023-12-31',b'2023-02-31'),xml('<g:Assets contextRef="I" unitRef="USD">'+('9'*65)+'</g:Assets>')]
  for raw in cases:
   with self.subTest(length=len(raw)),self.assertRaises(ValueError):parsed(raw)
 def test_deterministic_parse_and_original_inputs_are_preserved(self):
  raw=xml();m=manifest(raw);spec=selected_concepts(NS);before=copy.deepcopy((m,spec));a=parse_instance(raw,m,spec);b=parse_instance(raw,m,spec);self.assertEqual(a,b);self.assertEqual((m,spec),before)

 def test_dimension_context_element_is_part_of_semantic_identity(self):
  segment='<x:segment><d:explicitMember dimension="ext:RegionAxis">ext:NorthMember</d:explicitMember></x:segment>'
  raw=xml(context_extra=segment);a=parsed(raw)['contexts']['I']
  changed=raw.replace(segment.encode(),b'').replace(b'<x:instant>2023-12-31</x:instant></x:period></x:context>',b'<x:instant>2023-12-31</x:instant></x:period>'+segment.replace('segment','scenario').encode()+b'</x:context>')
  b=parsed(changed)['contexts']['I'];self.assertNotEqual(a['semantic_sha256'],b['semantic_sha256']);self.assertEqual(a['dimensions'][0]['context_element'],'segment');self.assertEqual(b['dimensions'][0]['context_element'],'scenario')
 def test_duplicate_segment_scenario_and_mixed_typed_member_are_rejected(self):
  segment='<x:segment><d:typedMember dimension="ext:DeskAxis"><ext:Desk>A</ext:Desk></d:typedMember></x:segment>'
  raw=xml(context_extra=segment)
  for altered in (xml(context_extra=segment+segment.replace('DeskAxis','OtherAxis')),raw.replace(b'<x:instant>2023-12-31</x:instant></x:period></x:context>',b'<x:instant>2023-12-31</x:instant></x:period><x:scenario/><x:scenario/></x:context>'),raw.replace(b'><ext:Desk>',b'>unmodeled<ext:Desk>')):
   with self.assertRaises(XBRLError):parsed(altered)
 def test_significant_structural_context_text_cannot_become_consolidated_fact(self):
  for raw in (xml(context_extra='<x:segment>unmodeled context qualifier</x:segment>'),xml().replace(b'<x:instant>',b'unmodeled period<x:instant>',1),xml().replace(b'<x:entity>',b'unmodeled context<x:entity>',1)):
   with self.subTest(source_bytes=len(raw)),self.assertRaisesRegex(XBRLError,'structural_text'):parsed(raw)
 def test_significant_unit_container_text_cannot_be_discarded(self):
  for raw in (xml().replace(b'<x:measure>iso:USD',b'unmodeled unit<x:measure>iso:USD'),xml(unit_extra='<x:unit id="PER"><x:divide>qualifier<x:unitNumerator><x:measure>iso:USD</x:measure></x:unitNumerator><x:unitDenominator><x:measure>x:shares</x:measure></x:unitDenominator></x:divide></x:unit>')):
   with self.assertRaisesRegex(XBRLError,'structural_text'):parsed(raw)
