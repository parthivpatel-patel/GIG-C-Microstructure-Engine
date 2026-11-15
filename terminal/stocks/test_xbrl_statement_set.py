"""Three authored issuer roles; exact periods, source changes and unavailable cells."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_statement_v2 import extension,EXT
from .test_xbrl_statements import collection,ROLE,EARLY,LATE
from .test_xbrl_dts import document
from .test_xbrl_calculation_report import inputs
from .service import StockWorkspace
from .xbrl_instance import XBRLError,digest
from .xbrl_statement_set import company_statement_set,company_statement_history,KINDS
A='0000000123-24-000001';B='0000000123-24-000002'
ROLES=dict(zip(KINDS,(ROLE,ROLE+'/income',ROLE+'/cash-flow')))
NAMES=('IncomeTotal','RevenueReported','ExpenseReported','CashFlowTotal','OperatingCash','InvestingCash')

def authored(*,income='100',extra='',**metadata):
 e=extension(**metadata)
 context='<x:context id="FD"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier></x:entity><x:period><x:startDate>2023-01-01</x:startDate><x:endDate>2023-12-31</x:endDate></x:period></x:context>'
 facts=''.join(f'<ext:{name} contextRef="FD" unitRef="USD" decimals="0">{value}</ext:{name}>'for name,value in zip(NAMES,(income,'150','50','30','50','20')))
 e['raw']=e['raw'].replace(b'</x:xbrl>',(context+facts+extra+'</x:xbrl>').encode());e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest()
 old=e['documents'][2]['raw'];elements=''.join(f'<s:element id="{name}" name="{name}" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="duration" nillable="true"/>'for name in NAMES)
 e['documents'][2]=document('extension.xsd',old.replace(b'</s:schema>',(elements+'</s:schema>').encode()))
 links=''
 for kind,names in zip(KINDS[1:],(NAMES[:3],NAMES[3:])):
  for link in('presentation','calculation'):
   locs=''.join(f'<l:loc xl:type="locator" xl:label="{n}" xl:href="extension.xsd#{n}"/>'for n in names)
   arcs=''.join(f'<l:{link}Arc xl:type="arc" xl:arcrole="http://www.xbrl.org/2003/arcrole/{"parent-child"if link=="presentation"else"summation-item"}" xl:from="{names[0]}" xl:to="{n}" order="{i}"'+(''if link=='presentation'else f' weight="{1 if i==1 else -1}"')+'/>'for i,n in enumerate(names[1:],1))
   links+=f'<l:{link}Link xl:type="extended" xl:role="{ROLES[kind]}">{locs}{arcs}</l:{link}Link>'
 e['documents'][1]=document('presentation.xml',e['documents'][1]['raw'].replace(b'</l:linkbase>',(links+'</l:linkbase>').encode()))
 return e

def prepared(*entries):
 entries=entries or(authored(),);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection(*entries))
 return w,{e['manifest']['accession']:inputs(e)[1]for e in entries},{e['manifest']['accession']:copy.deepcopy(ROLES)for e in entries}

def export(w=None,g=None,r=None,at=LATE,**kw):
 if w is None:w,g,r=prepared()
 return company_statement_set(w,'AAPL',at,g,r,**kw)

class StatementSet(unittest.TestCase):
 def test_three_source_roles_preserve_exact_values_and_signed_relationships(self):
  r=export();self.assertEqual(r['status'],'AVAILABLE');self.assertFalse(r['complete_statements']);self.assertFalse(r['provider_requested'])
  for kind,expected in zip(KINDS,(['1000','600','400'],['100','150','50'],['30','50','20'])):
   view=r['statements'][kind]['view'];self.assertEqual([row['value']for row in view['periods'][0]['rows']],expected);self.assertEqual(view['periods'][0]['calculations'][0]['exact_diagnostic']['status'],'EXACT_MATCH');self.assertTrue(view['relationships'][0]['provenance'])
   for row in view['periods'][0]['rows']:self.assertIsNone(row['statement_mapping']['accounting_metric'])
 def test_periods_units_and_original_numeric_source_ids_remain_bound(self):
  r=export();balance=r['statements'][KINDS[0]]['view']['periods'][0];income=r['statements'][KINDS[1]]['view']['periods'][0]
  self.assertIsNone(balance['start']);self.assertEqual(income['start'],'2023-01-01');self.assertEqual(income['end'],'2023-12-31');row=income['rows'][0];self.assertIsNone(row['facts'][0]['value']);self.assertEqual(row['numeric_facts'][0]['value'],'100');self.assertEqual(row['numeric_facts'][0]['source_fact_id'],row['facts'][0]['source_fact_id']);self.assertEqual(row['unit']['numerator'],['{http://www.xbrl.org/2003/iso4217}USD'])
 def test_historical_comparative_is_separate_and_does_not_fill_missing_rows(self):
  ctx='<x:context id="OLD"><x:entity><x:identifier scheme="http://www.sec.gov/CIK">0000320193</x:identifier></x:entity><x:period><x:startDate>2022-01-01</x:startDate><x:endDate>2022-12-31</x:endDate></x:period></x:context>'
  w,g,r=prepared(authored(extra=ctx+'<ext:RevenueReported contextRef="OLD" unitRef="USD" decimals="0">125</ext:RevenueReported>'));periods=export(w,g,r)['statements'][KINDS[1]]['view']['periods'];self.assertEqual(len(periods),2);self.assertEqual([row['status']for row in periods[1]['rows']],['MISSING','REPORTED_EXTENSION','MISSING']);self.assertEqual(periods[1]['rows'][1]['value'],'125')
 def test_conflicting_duplicates_are_not_selected(self):
  w,g,r=prepared(authored(extra='<ext:IncomeTotal contextRef="FD" unitRef="USD" decimals="0">101</ext:IncomeTotal>'));row=export(w,g,r)['statements'][KINDS[1]]['view']['periods'][0]['rows'][0];self.assertEqual(row['status'],'CONFLICT');self.assertIsNone(row['value']);self.assertEqual(len(row['facts']),2)
 def test_nil_missing_and_zero_are_distinct(self):
  e=authored(income='0');w,g,r=prepared(e);self.assertEqual(export(w,g,r)['statements'][KINDS[1]]['view']['periods'][0]['rows'][0]['value'],'0')
  e['raw']=e['raw'].replace(b'<ext:IncomeTotal contextRef="FD" unitRef="USD" decimals="0">0</ext:IncomeTotal>',b'<ext:IncomeTotal contextRef="FD" unitRef="USD" xsi:nil="true"/>');e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();w,g,r=prepared(e);row=export(w,g,r)['statements'][KINDS[1]]['view']['periods'][0]['rows'][0];self.assertEqual(row['status'],'MISSING');self.assertIsNone(row['value']);self.assertTrue(row['facts'][0]['nil'])
 def test_unit_conflict_stays_ambiguous(self):
  extra='<x:unit id="EUR"><x:measure>iso:EUR</x:measure></x:unit><ext:IncomeTotal contextRef="FD" unitRef="EUR" decimals="0">100</ext:IncomeTotal>'
  w,g,r=prepared(authored(extra=extra));row=export(w,g,r)['statements'][KINDS[1]]['view']['periods'][0]['rows'][0];self.assertEqual(row['status'],'AMBIGUOUS_UNITS');self.assertIsNone(row['value'])
 def test_cutoff_original_and_amendment_are_whole_independent_sources(self):
  w,g,r=prepared(authored(),authored(income='99',accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A));old=export(w,g,r,at=EARLY);new=export(w,g,r);self.assertEqual(old['source_filing']['accession'],A);self.assertEqual(new['source_filing']['accession'],B);self.assertEqual(new['statements'][KINDS[1]]['view']['periods'][0]['rows'][0]['value'],'99');self.assertEqual(len(new['lineage']['sources']),2)
 def test_missing_latest_graph_or_bindings_never_substitutes_old_source(self):
  w,g,r=prepared(authored(),authored(income='99',accession=B,filed='2024-02-10',accepted_at=LATE))
  self.assertEqual(export(w,{A:g[A]},r)['reason'],'ORIGINAL_DTS_NOT_SUPPLIED');self.assertEqual(export(w,g,{A:r[A]})['reason'],'ROLE_BINDINGS_NOT_SUPPLIED')
  with self.assertRaises(XBRLError):export(w,{B:g[A]},r)
 def test_missing_role_partial_and_explicit_undesignated_stays_missing(self):
  w,g,r=prepared();r[A]['income_statement']=ROLE+'/unknown';r[A]['cash_flow_statement']=None;packet=export(w,g,r);self.assertEqual(packet['status'],'PARTIAL');self.assertEqual(packet['statements']['income_statement']['reason'],'ROLE_NOT_IN_LATEST_FILING');self.assertEqual(packet['statements']['cash_flow_statement']['reason'],'ROLE_NOT_DESIGNATED')
 def test_ambiguous_latest_and_unresolved_ancestry_stay_unavailable(self):
  w,g,r=prepared(authored(),authored(accession=B));self.assertEqual(export(w,g,r)['reason'],'AMBIGUOUS_LATEST_FILING')
  w,g,r=prepared(authored(form='10-K/A'));self.assertEqual(export(w,g,r)['reason'],'EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED')
 def test_unknown_or_future_acceptance_is_not_admitted(self):
  for entry in(authored(accepted_at=None),authored(accepted_at='2025-01-01T00:00:00Z')):
   w,g,r=prepared(entry);self.assertEqual(export(w,g,r)['status'],'UNAVAILABLE')
 def test_invalid_query_and_stale_collection_reject(self):
  w,g,r=prepared()
  for invalid in([],{}, {A:{**ROLES,'extra':ROLE}}, {A:{k:ROLE for k in KINDS}}, {A:{**ROLES,'balance_sheet':False}}):
   if invalid=={}:continue
   with self.assertRaises(XBRLError):export(w,g,invalid)
  with self.assertRaisesRegex(XBRLError,'stale_collection'):export(w,g,r,expected_collection_sha256='0'*64)
  with self.assertRaises(XBRLError):export(w,g,r,form='8-K')
 def test_corrupted_source_context_or_arc_provenance_rejects(self):
  w,g,r=prepared();bad=copy.deepcopy(g);bad[A]['effective_relationships']['networks'][0]['arcs'][0]['provenance'][0]['source_sha256']='0'*64
  with self.assertRaises(XBRLError):export(w,bad,r)
  p=w.xbrl_collections['AAPL']._filings[A];p['contexts']['FD']['period']['start']='2022-01-01';p['canonical_sha256']=digest({k:v for k,v in p.items()if k!='canonical_sha256'})
  with self.assertRaises(XBRLError):export(w,g,r)
 def test_output_and_period_budgets_reject(self):
  with patch('terminal.stocks.xbrl_statement_set.MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'output_budget'):export()
  with patch('terminal.stocks.xbrl_statements.MAX_PERIODS',0),self.assertRaisesRegex(XBRLError,'period_budget'):export()
 def test_determinism_isolation_and_legacy_defaults(self):
  w,g,r=prepared();before=copy.deepcopy(w.xbrl_collections['AAPL']._filings);legacy=w.xbrl_collections['AAPL'].statement_at(LATE,role=ROLE);a=export(w,g,r);self.assertEqual(a,export(w,g,r));a['source_filing']['form']='bad';self.assertEqual(before,w.xbrl_collections['AAPL']._filings);self.assertEqual(legacy,w.xbrl_collections['AAPL'].statement_at(LATE,role=ROLE))
 def test_history_exact_order_transitions_and_no_cross_vintage_fill(self):
  w,g,r=prepared(authored(),authored(income='99',accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A));h=company_statement_history(w,'AAPL',['2024-01-01T00:00:00Z',EARLY,LATE],g,r);self.assertEqual([row['transition']for row in h['entries']],['UNAVAILABLE','FIRST_AVAILABLE','SOURCE_CHANGED']);self.assertFalse(h['complete_history']);self.assertEqual(h['entries'][2]['previous_accession'],A)
  for cutoffs in([], [LATE,EARLY], [EARLY,EARLY], [EARLY]*9):
   with self.assertRaises(XBRLError):company_statement_history(w,'AAPL',cutoffs,g,r)
  with patch('terminal.stocks.xbrl_statement_set.MAX_HISTORY',1),self.assertRaises(XBRLError):company_statement_history(w,'AAPL',[EARLY],g,r)

if __name__=='__main__':unittest.main()
