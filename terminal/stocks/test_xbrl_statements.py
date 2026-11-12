"""Source-authored statement graphs with independent exact expected numbers."""
import copy,unittest
from unittest.mock import patch
from .test_xbrl_instance import xml,manifest,NS
from .test_xbrl_dts import document,ROLE
from .test_xbrl_relationships import base,link,arc
from .xbrl_instance import selected_concepts,XBRLError,digest
from .xbrl_collection import FilingCollection
from .xbrl_binding import bind_declarations
from .xbrl_dts import discover
EARLY='2024-02-01T12:00:00.000000001Z';LATE='2024-02-10T12:00:00Z'

def entry(value='1000',cash='600',liabilities='400',*,extra_facts='',context_extra='',link_extra='',raw_patch=None,**metadata):
 facts=f'<g:Assets contextRef="I" unitRef="USD" decimals="0">{value}</g:Assets><g:CashAndCashEquivalentsAtCarryingValue contextRef="I" unitRef="USD">{cash}</g:CashAndCashEquivalentsAtCarryingValue><g:Liabilities contextRef="I" unitRef="USD">{liabilities}</g:Liabilities>'+extra_facts
 raw=xml(facts,context_extra=context_extra)
 if raw_patch:raw=raw_patch(raw)
 elements=''.join(f'<s:element name="{name}" id="{id_}" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="instant"/>'for name,id_ in [('Assets','assets'),('CashAndCashEquivalentsAtCarryingValue','cash'),('Liabilities','liabilities')])
 schema=f'<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:x="http://www.xbrl.org/2003/instance" xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" targetNamespace="{NS}">{elements}<s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="presentation.xml"/></s:appinfo></s:annotation></s:schema>'.encode()
 extra='<l:loc xl:type="locator" xl:label="b" xl:href="authored.xsd#liabilities"/>'
 present=link('presentation',arc()+arc(after='b',attrs='order="2"')+link_extra).replace('<l:presentationArc',extra+'<l:presentationArc',1)
 calc=link('calculation',arc(kind='calculation',attrs='weight="1"')+arc(kind='calculation',after='b',attrs='weight="1"')).replace('<l:calculationArc',extra+'<l:calculationArc',1)
 return {'raw':raw,'manifest':manifest(raw,**metadata),'concepts':selected_concepts(NS),'instance_uri':'https://authored.invalid/instance.xml','documents':[document('authored.xsd',schema),document('presentation.xml',base(present+calc))]}

def collection(*entries):
 c=FilingCollection('0000320193');c.ingest_dts_batch(list(entries)or[entry()]);return c

def view(c=None,at=LATE,**kw):return(c or collection()).statement_at(at,role=ROLE,**kw)

class StatementSelection(unittest.TestCase):
 def test_exact_statement_numbers_order_and_computation_have_original_lineage(self):
  r=view();self.assertEqual(r['status'],'AVAILABLE');p=r['periods'][0];self.assertEqual([v['value']for v in p['rows']],['1000','600','400']);self.assertEqual(p['calculations'][0]['status'],'EXACT_MATCH');self.assertEqual(p['calculations'][0]['residual'],{'numerator':'0','denominator':'1'});self.assertEqual(p['rows'][0]['facts'][0]['lexical_value'],'1000');self.assertIsNone(r['source_filing']['received_at']);self.assertFalse(r['complete_statements']);self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}))
 def test_exact_high_precision_uses_no_float_or_decimal_context_rounding(self):
  r=view(collection(entry(value='0.30000000000000000001',cash='0.1',liabilities='0.20000000000000000001')));self.assertEqual(r['periods'][0]['calculations'][0]['status'],'EXACT_MATCH');self.assertEqual(r['periods'][0]['rows'][0]['value'],'0.30000000000000000001')
 def test_difference_is_diagnostic_not_fabricated_balancing_value(self):
  r=view(collection(entry(value='999')));p=r['periods'][0];self.assertEqual(p['rows'][0]['value'],'999');self.assertEqual(p['calculations'][0]['status'],'EXACT_DIFFERENCE');self.assertEqual(p['calculations'][0]['residual']['numerator'],'-1')
 def test_missing_and_conflicting_facts_do_not_produce_total_or_fake_zero(self):
  r=view(collection(entry(raw_patch=lambda b:b.replace(b'>400<',b'>0<'))));self.assertEqual(r['periods'][0]['rows'][2]['value'],'0')
  e=entry();e['raw']=e['raw'].replace(b'<g:Liabilities contextRef="I" unitRef="USD">400</g:Liabilities>',b'');e['manifest']=manifest(e['raw']);r=view(collection(e));self.assertEqual(r['periods'][0]['rows'][2]['status'],'MISSING');self.assertIsNone(r['periods'][0]['rows'][2]['value']);self.assertEqual(r['periods'][0]['calculations'][0]['status'],'INCOMPLETE')
  r=view(collection(entry(extra_facts='<g:Assets contextRef="I" unitRef="USD">1001</g:Assets>')));self.assertEqual(r['periods'][0]['rows'][0]['status'],'CONFLICT');self.assertIsNone(r['periods'][0]['rows'][0]['value'])
 def test_consistent_duplicates_retain_all_source_fact_ids(self):
  r=view(collection(entry(extra_facts='<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>')));f=r['periods'][0]['rows'][0];self.assertEqual(f['status'],'REPORTED');self.assertEqual(len(f['facts']),2)
 def test_dimensional_contexts_do_not_leak_as_consolidated_rows(self):
  r=view(collection(entry(context_extra='<x:segment><d:explicitMember dimension="ext:RegionAxis">ext:NorthMember</d:explicitMember></x:segment>')));self.assertEqual(r['periods'],[]);self.assertEqual(r['fact_exclusions']['dimensioned_or_opaque'],3)
 def test_units_and_periods_are_not_merged(self):
  extra='<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit><g:Assets contextRef="I" unitRef="EUR">1000</g:Assets>'
  r=view(collection(entry(extra_facts=extra)));self.assertEqual(r['periods'][0]['rows'][0]['status'],'AMBIGUOUS_UNITS');self.assertEqual(r['periods'][0]['calculations'][0]['status'],'INCOMPLETE')
  extra='<x:context id="OLD"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier></x:entity><x:period><x:instant>2022-12-31</x:instant></x:period></x:context><g:Assets contextRef="OLD" unitRef="USD">500</g:Assets>'
  r=view(collection(entry(extra_facts=extra)));self.assertEqual(len(r['periods']),2);self.assertEqual(r['periods'][1]['rows'][0]['value'],'500');self.assertEqual(r['periods'][1]['rows'][1]['status'],'MISSING')
 def test_acceptance_cutoff_is_exact_and_timezone_equivalent(self):
  c=collection();self.assertEqual(view(c,at='2024-02-01T12:00:00Z')['status'],'UNAVAILABLE');a=view(c,at=EARLY);b=view(c,at='2024-02-01T07:00:00.000000001-05:00');self.assertEqual(a['periods'],b['periods']);self.assertEqual(a['status'],'AVAILABLE')
 def test_unknown_acceptance_never_uses_receipt_as_filing_time(self):
  r=view(collection(entry(accepted_at=None,received_at=LATE)));self.assertEqual(r['status'],'UNAVAILABLE');self.assertEqual(r['exclusions']['unknown_acceptance'],1)
 def test_amendment_is_selected_as_whole_source_without_addition(self):
  amended=entry(value='1100',accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001');c=collection(amended,entry());self.assertEqual(view(c,at=EARLY)['periods'][0]['rows'][0]['value'],'1000');r=view(c);self.assertEqual(r['periods'][0]['rows'][0]['value'],'1100');self.assertEqual(r['source_filing']['amends_accession'],'0000000123-24-000001');self.assertIn('AMENDMENT_NOT_ADDITIVELY_MERGED',r['diagnostics'])
 def test_unresolved_amendment_is_not_accepted_as_complete_restatement(self):
  r=view(collection(entry(form='10-K/A')));self.assertEqual(r['reason'],'AMENDMENT_LINEAGE_UNRESOLVED');self.assertEqual(r['periods'],[])
 def test_same_time_filings_are_ambiguous_not_accession_sort_tiebreak(self):
  r=view(collection(entry(),entry(value='1001',accession='0000000123-24-000002')));self.assertEqual(r['status'],'AMBIGUOUS');self.assertEqual(r['periods'],[])
 def test_missing_latest_role_does_not_fall_back_to_older_filing(self):
  e=entry(value='1001',accession='0000000123-24-000002',filed='2024-02-10',accepted_at=LATE);e['documents'][1]=document('presentation.xml',e['documents'][1]['raw'].replace(ROLE.encode(),(ROLE+'/new').encode()));r=view(collection(entry(),e));self.assertEqual(r['reason'],'ROLE_NOT_IN_LATEST_FILING')
 def test_unsupported_network_or_open_dts_remains_unavailable(self):
  r=view(collection(entry(link_extra=arc(attrs='custom="unsupported"'))));self.assertEqual(r['reason'],'PRESENTATION_UNSUPPORTED')
  e=entry();e['documents']=e['documents'][:1];r=view(collection(e));self.assertEqual(r['reason'],'SUPPLIED_CLOSED_DTS_REQUIRED')
 def test_explicit_form_family_and_role_required(self):
  c=collection();r=c.statement_at(LATE);self.assertIn(ROLE,r['available_roles']);self.assertEqual(r['reason'],'EXPLICIT_PRESENTATION_ROLE_REQUIRED');self.assertEqual(view(c,form='10-Q')['status'],'UNAVAILABLE')
  for kw in({'role':''},{'role':[]},{'form':'8-K'}):
   with self.assertRaises(XBRLError):c.statement_at(LATE,**kw)
 def test_corruption_and_lineage_resource_limits_fail_closed(self):
  c=collection();c._filings[next(iter(c._filings))]['facts'][0]['value']='999'
  with self.assertRaisesRegex(XBRLError,'input_identity'):view(c)
  with patch('terminal.stocks.xbrl_statements.MAX_CONCEPTS',2),self.assertRaisesRegex(XBRLError,'concept_budget'):view()
  with patch('terminal.stocks.xbrl_statements.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):view()
  from .xbrl_statements import _result
  from .xbrl_instance import canonical
  body={'example':'bounded'}
  with patch('terminal.stocks.xbrl_statements.MAX_OUTPUT',len(canonical(body))+1),self.assertRaisesRegex(XBRLError,'output_budget'):_result(body)
 def test_determinism_no_input_mutation_and_return_isolation(self):
  c=collection();before=copy.deepcopy(c._filings);a=view(c);b=view(c);self.assertEqual(a,b);a['periods'][0]['rows'][0]['facts'][0]['value']='999';self.assertEqual(view(c),b);self.assertEqual(c._filings,before)
 def test_original_instance_without_dts_does_not_claim_statements(self):
  e=entry();c=FilingCollection('0000320193');c.ingest_batch([{k:e[k]for k in('raw','manifest','concepts')}]);self.assertEqual(view(c)['reason'],'SUPPLIED_CLOSED_DTS_REQUIRED')
 def test_amendment_without_known_parent_acceptance_is_unresolved(self):
  original=entry(accepted_at=None);amended=entry(accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001');self.assertEqual(view(collection(original,amended))['reason'],'AMENDMENT_LINEAGE_UNRESOLVED')
 def test_numeric_nil_remains_missing_and_incomplete(self):
  e=entry();e['raw']=e['raw'].replace(b'<g:Assets contextRef="I" unitRef="USD" decimals="0">1000</g:Assets>',b'<g:Assets contextRef="I" unitRef="USD" xsi:nil="true"/>');e['manifest']=manifest(e['raw']);d=e['documents'][0];e['documents'][0]=document('authored.xsd',d['raw'].replace(b'name="Assets"',b'name="Assets" nillable="true"'));r=view(collection(e));self.assertEqual(r['periods'][0]['rows'][0]['status'],'MISSING');self.assertEqual(r['periods'][0]['calculations'][0]['status'],'INCOMPLETE')
