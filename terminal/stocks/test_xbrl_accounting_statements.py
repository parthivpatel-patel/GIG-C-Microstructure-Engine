"""Authored source relationships and complete three-role bounded row outcomes."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_statement_set import authored,A,B,ROLES,KINDS,EXT,EARLY,LATE
from .test_xbrl_statements import collection
from .test_xbrl_dts import document
from .service import StockWorkspace
from .xbrl_instance import XBRLError,digest
from .xbrl_accounting_relationships import ESSENCE,REQUIRES
from .xbrl_accounting_statements import company_accounting_statements,company_accounting_history
ACCOUNTING='https://authored.invalid/accounting/issuer-reported'

def recipe(*,alias='100',exact=False,extra='',**metadata):
 e=authored(extra=extra,**metadata)
 fact=''if alias is None else f'<ext:IssuerProfit contextRef="FD" unitRef="USD" decimals="0">{alias}</ext:IssuerProfit>'
 e['raw']=e['raw'].replace(b'</x:xbrl>',(fact+'</x:xbrl>').encode())
 if exact:e['raw']=e['raw'].replace(b'decimals="0"',b'decimals="INF"')
 e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
 xsd=e['documents'][2]['raw'].replace(b'<s:schema ',b'<s:schema xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" ',1)
 element='<s:element id="profit" name="IssuerProfit" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="duration" nillable="true"/>'
 e['documents'][2]=document('extension.xsd',xsd.replace(b'</s:schema>',(element+'<s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="accounting.xml"/></s:appinfo></s:annotation></s:schema>').encode()))
 link=f'<l:definitionLink xl:type="extended" xl:role="{ACCOUNTING}"><l:loc xl:type="locator" xl:label="a" xl:href="extension.xsd#IncomeTotal"/><l:loc xl:type="locator" xl:label="b" xl:href="extension.xsd#profit"/><l:definitionArc xl:type="arc" xl:arcrole="{ESSENCE}" xl:from="a" xl:to="b"/></l:definitionLink>'
 e['documents'].append(document('accounting.xml',('<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink">'+link+'</l:linkbase>').encode()))
 raw=e['documents'][1]['raw'];start=raw.index((f'<l:presentationLink xl:type="extended" xl:role="{ROLES[KINDS[1]]}"').encode());end=raw.index(b'</l:presentationLink>',start)
 addition=b'<l:loc xl:type="locator" xl:label="profit" xl:href="extension.xsd#profit"/><l:presentationArc xl:type="arc" xl:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xl:from="IncomeTotal" xl:to="profit" order="3"/>'
 e['documents'][1]=document('presentation.xml',raw[:end]+addition+raw[end:]);return e

def prepared(*entries):
 entries=entries or(recipe(),);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection(*entries))
 originals={e['manifest']['accession']:copy.deepcopy(e)for e in entries};roles={e['manifest']['accession']:{k:{'presentation_role':ROLES[k],'accounting_role':ACCOUNTING}for k in KINDS}for e in entries};return w,originals,roles
def export(w=None,inputs=None,roles=None,at=LATE,**kw):
 if w is None:w,inputs,roles=prepared()
 return company_accounting_statements(w,'AAPL',at,inputs,roles,**kw)
def aliasrow(packet):return packet['statements'][KINDS[1]]['periods'][0]['rows'][-1]

class AccountingStatements(unittest.TestCase):
 def test_accounting_history_cutoffs_and_whole_source_transitions(self):
  w,i,b=prepared(recipe(),recipe(alias=None,accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A));r=company_accounting_history(w,'AAPL',['2024-01-01T00:00:00Z',EARLY,LATE],i,b);self.assertEqual([e['transition']for e in r['entries']],['UNAVAILABLE','FIRST_AVAILABLE','SOURCE_CHANGED']);self.assertEqual(aliasrow(r['entries'][2]['packet'])['status'],'MISSING');self.assertEqual(r['entries'][2]['previous_accession'],A);self.assertFalse(r['complete_history'])
  for cutoffs in([], [LATE,EARLY], [EARLY,EARLY], [EARLY]*9):
   with self.assertRaises(XBRLError):company_accounting_history(w,'AAPL',cutoffs,i,b)
 def test_source_supported_three_roles_classification_and_exact_calculation(self):
  r=export();self.assertEqual(r['status'],'AVAILABLE');self.assertFalse(r['complete_statements']);row=aliasrow(r);self.assertEqual(row['status'],'SUPPORTED');self.assertEqual(row['value'],'100');self.assertEqual(row['essence_concept'],'{'+EXT+'}IncomeTotal');self.assertIsNone(row['classification']['accounting_metric']);self.assertEqual(row['classification']['period_type'],'duration');self.assertEqual(row['equivalence_status'],'SOURCE_RELATIONSHIP_REPORTED_EQUAL');self.assertTrue(row['classification']['declaration_documents']);self.assertTrue(row['accounting_relationships'][0]['provenance']);self.assertEqual(r['statements'][KINDS[1]]['periods'][0]['calculations'][0]['calculation']['status'],'CALCULATION_COMPATIBLE')
 def test_exact_INF_allows_explicit_equivalence_with_original_source_receipts(self):
  w,i,b=prepared(recipe(exact=True));r=export(w,i,b);self.assertEqual(aliasrow(r)['equivalence_status'],'SOURCE_EQUIVALENCE_VERIFIED');self.assertEqual(r['accounting_report']['source_audit']['status'],'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION');self.assertNotEqual(r['admitted_parsed_sha256'],r['original_parsed_sha256'])
 def test_missing_alias_is_not_filled_from_reported_essence(self):
  w,i,b=prepared(recipe(alias=None));row=aliasrow(export(w,i,b));self.assertEqual(row['status'],'MISSING');self.assertIsNone(row['value']);self.assertEqual(row['facts'],[]);self.assertEqual(row['equivalence_status'],'MISSING_COUNTERPART')
 def test_conflicting_alias_retains_both_source_values_without_projected_value(self):
  w,i,b=prepared(recipe(alias='101'));row=aliasrow(export(w,i,b));self.assertEqual(row['status'],'CONFLICTING');self.assertIsNone(row['value']);check=row['accounting_relationships'][0]['checks'][0];self.assertEqual(check['essence_facts'][0]['reported_value'],'100');self.assertEqual(check['alias_facts'][0]['reported_value'],'101')
 def test_duplicate_conflicts_and_nil_cannot_be_reported_as_values(self):
  extra='<ext:IssuerProfit contextRef="FD" unitRef="USD" decimals="0">99</ext:IssuerProfit>';w,i,b=prepared(recipe(extra=extra));self.assertEqual(aliasrow(export(w,i,b))['status'],'CONFLICTING')
  e=recipe(alias=None,extra='<ext:IssuerProfit contextRef="FD" unitRef="USD" xsi:nil="true"/>');w,i,b=prepared(e);row=aliasrow(export(w,i,b));self.assertEqual(row['status'],'MISSING');self.assertTrue(row['facts'][0]['nil'])
 def test_dimensioned_rows_stay_unsupported(self):
  e=recipe();e['raw']=e['raw'].replace(b'<x:period><x:startDate>2023-01-01',b'<x:segment><d:explicitMember dimension="ext:Region">ext:North</d:explicitMember></x:segment><x:period><x:startDate>2023-01-01');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();w,i,b=prepared(e);row=aliasrow(export(w,i,b));self.assertEqual(row['status'],'UNSUPPORTED');self.assertIsNone(row['value']);self.assertEqual(row['equivalence_status'],'UNSUPPORTED_ASPECTS')
 def test_period_unit_and_context_incompatibility_never_cross_join(self):
  e=recipe();e['raw']=e['raw'].replace(b'</x:xbrl>',b'<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit></x:xbrl>').replace(b'<ext:IssuerProfit contextRef="FD" unitRef="USD"',b'<ext:IssuerProfit contextRef="FD" unitRef="EUR"');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();w,i,b=prepared(e);row=aliasrow(export(w,i,b));self.assertEqual(row['equivalence_status'],'UNSUPPORTED_ASPECTS');self.assertEqual(row['unit']['numerator'],['{http://www.xbrl.org/2003/iso4217}EUR'])
 def test_unknown_numeric_type_stays_unsupported(self):
  e=recipe();d=e['documents'][2];raw=d['raw'].replace(b'id="profit" name="IssuerProfit" type="x:monetaryItemType"',b'id="profit" name="IssuerProfit" type="x:stringItemType"');e['documents'][2]=document('extension.xsd',raw);w,i,b=prepared(e)
  with self.assertRaisesRegex(XBRLError,'type_conflict'):export(w,i,b)
 def test_source_acceptance_amendment_and_missing_original_never_use_old_filing(self):
  w,i,b=prepared(recipe(),recipe(income='99',alias=None,accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A));old=export(w,i,b,at=EARLY);new=export(w,i,b);self.assertEqual(aliasrow(old)['value'],'100');self.assertEqual(aliasrow(new)['status'],'MISSING');self.assertEqual(new['source_filing']['accession'],B);self.assertEqual(len(new['lineage']['sources']),2);self.assertEqual(export(w,{A:i[A]},b)['reason'],'SELECTED_ORIGINALS_OR_ROLE_BINDINGS_NOT_SUPPLIED')
 def test_same_time_ambiguity_and_unresolved_ancestry_are_unavailable(self):
  w,i,b=prepared(recipe(),recipe(accession=B));self.assertEqual(export(w,i,b)['reason'],'AMBIGUOUS_LATEST_FILING')
  w,i,b=prepared(recipe(form='10-K/A'));self.assertEqual(export(w,i,b)['reason'],'EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED')
 def test_wrong_originals_and_altered_raw_hashes_reject(self):
  w,i,b=prepared();i[A]['raw']=i[A]['raw'].replace(b'>100</ext:IssuerProfit>',b'>101</ext:IssuerProfit>')
  with self.assertRaises(XBRLError):export(w,i,b)
  i[A]['manifest']['source_sha256']=hashlib.sha256(i[A]['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'admitted_source_mismatch'):export(w,i,b)
 def test_explicit_role_missing_or_not_designated_is_not_inferred(self):
  w,i,b=prepared();b[A]['income_statement']['accounting_role']='https://unknown.invalid';r=export(w,i,b);self.assertEqual(r['status'],'PARTIAL');self.assertEqual(r['statements']['income_statement']['reason'],'ACCOUNTING_ROLE_NOT_IN_SELECTED_FILING');b[A]['income_statement']['accounting_role']=None;r=export(w,i,b);self.assertEqual(aliasrow(r)['equivalence_status'],'NO_SOURCE_EQUIVALENCE')
  b[A]['income_statement']['presentation_role']=b[A]['balance_sheet']['presentation_role']
  with self.assertRaisesRegex(XBRLError,'ambiguous_presentation_roles'):export(w,i,b)
 def test_stale_query_and_budgets_reject_without_mutation(self):
  w,i,b=prepared();before=copy.deepcopy(w.xbrl_collections['AAPL']._filings)
  with self.assertRaisesRegex(XBRLError,'stale'):export(w,i,b,expected_collection_sha256='0'*64)
  with patch('terminal.stocks.xbrl_accounting_statements.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):export(w,i,b)
  with patch('terminal.stocks.xbrl_accounting_statements.MAX_PERIODS',0),self.assertRaisesRegex(XBRLError,'period_budget'):export(w,i,b)
  self.assertEqual(before,w.xbrl_collections['AAPL']._filings)
 def test_deterministic_detached_result_and_legacy_views_unchanged(self):
  w,i,b=prepared();before=copy.deepcopy((i,b,w.xbrl_collections['AAPL']._filings));r=export(w,i,b);self.assertEqual(r,export(w,i,b));r['statements'].clear();self.assertEqual((i,b,w.xbrl_collections['AAPL']._filings),before);self.assertEqual(export(w,i,b)['sha256'],digest({k:v for k,v in export(w,i,b).items()if k!='sha256'}))
 def test_one_source_exposes_supported_conflicting_missing_and_unsupported_rows(self):
  e=recipe(alias='101');e['raw']=e['raw'].replace(b'<ext:RevenueReported contextRef="FD" unitRef="USD" decimals="0">150</ext:RevenueReported>',b'');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();d=e['documents'][2];e['documents'][2]=document('extension.xsd',d['raw'].replace(b'id="CashFlowTotal" name="CashFlowTotal" type="x:monetaryItemType"',b'id="CashFlowTotal" name="CashFlowTotal" type="x:stringItemType"'));w,i,b=prepared(e);r=export(w,i,b);states={row['status']for section in r['statements'].values()for period in section['periods']for row in period['rows']};self.assertEqual(states,{'SUPPORTED','CONFLICTING','MISSING','UNSUPPORTED'});self.assertEqual(r['statements'][KINDS[1]]['periods'][0]['calculations'][0]['calculation']['status'],'INCOMPLETE')
 def test_calculation_does_not_join_normalized_CIK_with_different_identifier_lexicals(self):
  e=recipe();raw=e['raw'];start=raw.index(b'<x:context id="FD">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="FD"',b'id="FD2"').replace(b'>0000320193<',b'>320193<');e['raw']=raw.replace(b'</x:xbrl>',other+b'</x:xbrl>').replace(b'<ext:ExpenseReported contextRef="FD"',b'<ext:ExpenseReported contextRef="FD2"');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();w,i,b=prepared(e);checks=export(w,i,b)['statements'][KINDS[1]]['periods'][0]['calculations'];self.assertEqual(len(checks),2);self.assertTrue(all(c['calculation']['status']=='INCOMPLETE'for c in checks));self.assertEqual({c['identifier_lexical']for c in checks},{'0000320193','320193'})
 def test_requires_element_missing_occurrence_is_visible_without_cross_filing_fill(self):
  e=recipe();d=e['documents'][-1];e['documents'][-1]=document('accounting.xml',d['raw'].replace(b'</l:definitionLink>',(f'<l:loc xl:type="locator" xl:label="c" xl:href="extension.xsd#CashFlowTotal"/><l:definitionArc xl:type="arc" xl:arcrole="{REQUIRES}" xl:from="b" xl:to="c"/></l:definitionLink>').encode()));e['raw']=e['raw'].replace(b'<ext:CashFlowTotal contextRef="FD" unitRef="USD" decimals="0">30</ext:CashFlowTotal>',b'');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();w,i,b=prepared(e);r=export(w,i,b);relations=aliasrow(r)['accounting_relationships'];check=next(a for a in relations if a['kind']=='requires-element')['checks'][0];self.assertEqual(check['status'],'REQUIRED_ELEMENT_MISSING');self.assertEqual(r['statements'][KINDS[2]]['periods'][0]['rows'][0]['status'],'MISSING')

if __name__=='__main__':unittest.main()
