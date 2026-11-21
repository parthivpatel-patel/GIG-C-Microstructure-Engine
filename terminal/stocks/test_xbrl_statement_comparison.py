"""Adjacent original-byte filing comparisons; no source values are synthesized."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_accounting_statements import recipe,prepared,A,B,EARLY,LATE,ACCOUNTING
from .test_xbrl_statement_set import KINDS,EXT
from .test_xbrl_dts import document
from .xbrl_accounting_relationships import REQUIRES
from .xbrl_instance import canonical,digest,XBRLError
from .xbrl_statement_comparison import company_statement_vintage_comparison
from .service import StockWorkspace

MODULE='terminal.stocks.xbrl_statement_comparison.'
C='0000000123-24-000003';LATEST='2024-03-01T12:00:00Z'
BEFORE='2024-01-01T00:00:00Z'

def amendment(**kw):return recipe(accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A,**kw)
def raw_edit(e,old,new):
 e['raw']=e['raw'].replace(old,new);e['manifest']['source_sha256']=hashlib.sha256(e['raw']).hexdigest();return e
def source_doc(e,index,raw):
 old=e['documents'][index];e['documents'][index]={**old,'raw':raw,'sha256':hashlib.sha256(raw).hexdigest()}
 return e

def compare(*entries,cutoffs=None,inputs=None,bindings=None,**kw):
 w,i,b=prepared(*(entries or(recipe(),amendment())))
 return company_statement_vintage_comparison(w,'AAPL',cutoffs or[EARLY,LATE],i if inputs is None else inputs,b if bindings is None else bindings,**kw)
def changes(result,kind='income_statement',transition=0):return result['comparisons'][transition]['statements'][kind]['rows']
def change(result,concept='IssuerProfit',kind='income_statement',transition=0):
 return next(r for r in changes(result,kind,transition)if r['concept']=='{'+EXT+'}'+concept)
def requires(e):
 d=e['documents'][-1];addition=f'<l:loc xl:type="locator" xl:label="c" xl:href="extension.xsd#CashFlowTotal"/><l:definitionArc xl:type="arc" xl:arcrole="{REQUIRES}" xl:from="b" xl:to="c"/>'
 return source_doc(e,len(e['documents'])-1,d['raw'].replace(b'</l:definitionLink>',(addition+'</l:definitionLink>').encode()))

class StatementVintageComparison(unittest.TestCase):
 def test_original_amendment_vintages_preserve_every_source_identity(self):
  r=compare(recipe(),amendment(income='101',alias='101'));row=change(r)
  self.assertEqual(r['schema'],'gig.backend.statement_vintage_comparison.v1');self.assertEqual(row['status'],'REPORTED_NUMERIC_VALUE_CHANGED');self.assertTrue(row['reported_values_comparable']);self.assertEqual(row['previous']['reported_value'],'100');self.assertEqual(row['current']['reported_value'],'101');self.assertFalse(row['underlying_value_equality_established']);self.assertFalse(row['restatement_established']);self.assertEqual(r['comparisons'][0]['source_relation'],'EXPLICIT_SUPPLIED_AMENDMENT_CHAIN')
  for side,index in[('previous',0),('current',1)]:
   value=row[side];packet=r['entries'][index];self.assertEqual(value['source_packet_sha256'],packet['sha256']);self.assertEqual(value['source_sha256'],packet['accounting']['source_filing']['source_sha256']);self.assertEqual(value['original_parsed_sha256'],packet['source']['canonical_sha256']);self.assertEqual(value['dts_sha256'],packet['dts']['canonical_sha256']);self.assertTrue(value['source_facts']);self.assertEqual(value['numeric_facts'][0]['original_lexical_value'],value['source_facts'][0]['lexical_value'])
  self.assertEqual(len(r['entries'][1]['accounting']['lineage']['sources']),2);self.assertFalse(r['complete_statements']);self.assertFalse(r['complete_history']);self.assertFalse(r['values_filled']);self.assertFalse(r['gaap_aliases_inferred']);self.assertIsNone(r['selected_reported_value']);self.assertFalse(r['provider_requested']);self.assertTrue(r['read_only'])
 def test_same_selected_filing_is_stable_without_reapplying_history(self):
  r=compare(recipe(),amendment(),cutoffs=[EARLY,'2024-02-05T00:00:00Z']);self.assertEqual(r['comparisons'][0]['source_relation'],'SAME_SELECTED_FILING');self.assertTrue(all(v['status']=='REPORTED_NUMERIC_VALUE_UNCHANGED'for v in changes(r)));self.assertEqual(r['entries'][0]['source']['canonical_sha256'],r['entries'][1]['source']['canonical_sha256'])
 def test_equal_lexical_variants_and_signed_zero_are_not_numeric_changes(self):
  old=raw_edit(recipe(),b'>100</ext:IssuerProfit>',b'>+00100.00</ext:IssuerProfit>');r=compare(old,amendment());row=change(r);self.assertEqual(row['status'],'REPORTED_NUMERIC_VALUE_UNCHANGED');self.assertEqual(row['previous']['source_facts'][0]['lexical_value'],'+00100.00');self.assertEqual(row['current']['source_facts'][0]['lexical_value'],'100')
  old=raw_edit(recipe(),b'>30</ext:CashFlowTotal>',b'>-0</ext:CashFlowTotal>');new=raw_edit(amendment(),b'>30</ext:CashFlowTotal>',b'>0.0</ext:CashFlowTotal>')
  # Keep source calculation compatible instead of erasing its diagnostic.
  for e in(old,new):raw_edit(e,b'>50</ext:OperatingCash>',b'>20</ext:OperatingCash>')
  self.assertEqual(change(compare(old,new),'CashFlowTotal','cash_flow_statement')['status'],'REPORTED_NUMERIC_VALUE_UNCHANGED')
 def test_missing_nil_and_conflicting_rows_remain_unselected(self):
  for new,expected in[(amendment(alias=None),'CURRENT_SOURCE_ROW_MISSING'),(amendment(alias='101'),'CONFLICTING_SOURCE_ROW'),(amendment(alias=None,extra='<ext:IssuerProfit contextRef="FD" unitRef="USD" xsi:nil="true"/>'),'CURRENT_SOURCE_ROW_MISSING')]:
   row=change(compare(recipe(),new));self.assertEqual(row['status'],expected);self.assertFalse(row['reported_values_comparable']);self.assertIsNone(row['current']['reported_value']);self.assertEqual(row['previous']['reported_value'],'100')
 def test_both_missing_and_previously_missing_do_not_invent_values(self):
  self.assertEqual(change(compare(recipe(alias=None),amendment(alias=None)))['status'],'BOTH_SOURCE_ROWS_MISSING');row=change(compare(recipe(alias=None),amendment()));self.assertEqual(row['status'],'PREVIOUS_SOURCE_ROW_MISSING');self.assertIsNone(row['previous']['reported_value'])
 def test_unsupported_numeric_declaration_remains_explicit(self):
  new=amendment();d=new['documents'][2];source_doc(new,2,d['raw'].replace(b'id="CashFlowTotal" name="CashFlowTotal" type="x:monetaryItemType"',b'id="CashFlowTotal" name="CashFlowTotal" type="x:stringItemType"'));row=change(compare(recipe(),new),'CashFlowTotal','cash_flow_statement');self.assertEqual(row['status'],'UNSUPPORTED_SOURCE_ROW');self.assertIsNone(row['current']['reported_value'])
 def test_exact_units_are_required_even_when_numeric_values_agree(self):
  new=raw_edit(amendment(),b'>iso:USD<',b'>iso:EUR<');row=change(compare(recipe(),new));self.assertEqual(row['status'],'INCOMPATIBLE_SOURCE_UNIT');self.assertFalse(row['reported_values_comparable']);self.assertEqual(row['previous']['reported_value'],row['current']['reported_value'])
 def test_entity_identifier_lexical_and_dimensional_aspects_do_not_cross_join(self):
  new=raw_edit(amendment(),b'>0000320193<',b'>320193<');row=change(compare(recipe(),new));self.assertEqual(row['status'],'INCOMPATIBLE_SOURCE_CONTEXT')
  new=raw_edit(amendment(),b'<x:period><x:startDate>2023-01-01',b'<x:segment><d:explicitMember dimension="ext:Region">ext:North</d:explicitMember></x:segment><x:period><x:startDate>2023-01-01');row=change(compare(recipe(),new));self.assertEqual(row['status'],'UNSUPPORTED_SOURCE_ROW');self.assertTrue(row['current']['source_facts'])
 def test_multiple_lexical_entity_contexts_are_not_one_data_point(self):
  new=amendment();raw=new['raw'];start=raw.index(b'<x:context id="FD">');end=raw.index(b'</x:context>',start)+len(b'</x:context>');other=raw[start:end].replace(b'id="FD"',b'id="FD2"').replace(b'>0000320193<',b'>320193<');raw_edit(new,b'</x:xbrl>',other+b'<ext:ExpenseReported contextRef="FD2" unitRef="USD" decimals="0">50</ext:ExpenseReported></x:xbrl>');row=change(compare(recipe(),new),'ExpenseReported');self.assertEqual(row['status'],'AMBIGUOUS_SOURCE_ASPECTS');self.assertEqual(len(row['current']['source_facts']),2)
 def test_exact_periods_are_never_joined_to_different_historical_periods(self):
  new=amendment();raw_edit(new,b'<x:startDate>2023-01-01',b'<x:startDate>2022-01-01');raw_edit(new,b'<x:endDate>2023-12-31',b'<x:endDate>2022-12-31');rows=changes(compare(recipe(),new));self.assertEqual({r['status']for r in rows},{'ROW_NOT_IN_PREVIOUS_VIEW','ROW_NOT_IN_CURRENT_VIEW'});self.assertTrue(all(not r['reported_values_comparable']for r in rows));self.assertEqual({r['period']['end']for r in rows},{'2023-12-31','2022-12-31'})
 def test_concept_names_are_not_used_as_cross_filing_aliases(self):
  new=amendment();raw_edit(new,b'IssuerProfit',b'IssuerProfitOther');d=new['documents'][2];source_doc(new,2,d['raw'].replace(b'name="IssuerProfit"',b'name="IssuerProfitOther"'));r=compare(recipe(),new);old=change(r);fresh=change(r,'IssuerProfitOther');self.assertEqual(old['status'],'ROW_NOT_IN_CURRENT_VIEW');self.assertEqual(fresh['status'],'ROW_NOT_IN_PREVIOUS_VIEW');self.assertFalse(old['reported_values_comparable']);self.assertFalse(fresh['reported_values_comparable'])
 def test_declaration_changes_are_not_hidden_by_equal_reported_numbers(self):
  new=amendment();d=new['documents'][2];source_doc(new,2,d['raw'].replace(b'id="ExpenseReported" name="ExpenseReported"',b'id="ExpenseReported" name="ExpenseReported" x:balance="debit"'));row=change(compare(recipe(),new),'ExpenseReported');self.assertEqual(row['status'],'SOURCE_DECLARATION_CHANGED')
 def test_same_named_numeric_type_requires_same_original_restriction_path(self):
  old=recipe();new=amendment()
  for e,maximum in[(old,'100'),(new,'200')]:
   d=e['documents'][2];raw=d['raw'];declaration='<s:complexType name="ExpenseType"><s:simpleContent><s:restriction base="x:monetaryItemType"><s:maxInclusive value="'+maximum+'"/></s:restriction></s:simpleContent></s:complexType>'
   raw=raw.replace(b'<s:schema ',('<s:schema xmlns:vintage="'+EXT+'" ').encode(),1).replace(b'id="ExpenseReported" name="ExpenseReported" type="x:monetaryItemType"',b'id="ExpenseReported" name="ExpenseReported" type="vintage:ExpenseType"').replace(b'</s:schema>',(declaration+'</s:schema>').encode());source_doc(e,2,raw)
  row=change(compare(old,new),'ExpenseReported');self.assertEqual(row['status'],'SOURCE_DECLARATION_CHANGED');self.assertEqual(row['previous']['reported_value'],row['current']['reported_value'])
 def test_collection_identity_change_between_queries_cannot_publish_mixed_history(self):
  from . import xbrl_statement_comparison as comparison
  w,i,b=prepared(recipe(),amendment());actual=comparison.company_source_accounting;calls=[]
  def changing(*a,**kw):
   result=actual(*a,**kw);calls.append(result)
   if len(calls)==1:
    third=recipe(accession=C,filed='2024-03-01',accepted_at=LATEST);w.xbrl_collections['AAPL'].ingest_dts_batch([third])
   return result
  with patch(MODULE+'company_source_accounting',side_effect=changing),self.assertRaisesRegex(XBRLError,'stale'):
   company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
  self.assertEqual(len(calls),1)
 def test_changed_source_relationship_does_not_create_an_equivalence(self):
  new=amendment();d=new['documents'][-1];source_doc(new,len(new['documents'])-1,d['raw'].replace(b'xl:from="a" xl:to="b"',b'xl:from="b" xl:to="a"'));row=change(compare(recipe(),new));self.assertEqual(row['status'],'ACCOUNTING_RELATIONSHIP_CHANGED');self.assertFalse(row['reported_values_comparable'])
 def test_unmet_requires_element_is_not_repaired_from_previous_filing(self):
  old=requires(recipe());new=requires(amendment());raw_edit(new,b'<ext:CashFlowTotal contextRef="FD" unitRef="USD" decimals="0">30</ext:CashFlowTotal>',b'');row=change(compare(old,new));self.assertEqual(row['status'],'ACCOUNTING_REQUIREMENT_UNSATISFIED');self.assertEqual(row['current']['reported_value'],'100');self.assertFalse(row['reported_values_comparable'])
 def test_source_calculation_inconsistency_blocks_compatible_change_claim(self):
  new=raw_edit(amendment(),b'>30</ext:CashFlowTotal>',b'>80</ext:CashFlowTotal>');row=change(compare(recipe(),new),'CashFlowTotal','cash_flow_statement');self.assertEqual(row['status'],'CALCULATION_INCONSISTENT');self.assertEqual(row['current_calculations'][0]['calculation']['status'],'DEFINITELY_INCONSISTENT');self.assertFalse(row['reported_values_comparable'])
 def test_incomplete_calculation_stays_visible_without_zero_filling(self):
  old=raw_edit(recipe(),b'<ext:InvestingCash contextRef="FD" unitRef="USD" decimals="0">20</ext:InvestingCash>',b'');new=amendment();row=change(compare(old,new),'CashFlowTotal','cash_flow_statement');self.assertEqual(row['status'],'REPORTED_NUMERIC_VALUE_UNCHANGED');self.assertEqual(row['previous_calculations'][0]['calculation']['status'],'INCOMPLETE');self.assertIsNone(row['previous_calculations'][0]['calculation']['weighted_sum_interval'])
 def test_changed_explicit_role_bindings_are_not_semantically_inferred(self):
  w,i,b=prepared(recipe(),amendment());b[B]['income_statement']['accounting_role']=None;r=company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b);self.assertEqual({v['status']for v in changes(r)},{'ROLE_BINDING_CHANGED'});self.assertTrue(all(not v['reported_values_comparable']for v in changes(r)))
 def test_unknown_or_missing_latest_originals_never_fall_back_to_older_source(self):
  w,i,b=prepared(recipe(),amendment());r=company_statement_vintage_comparison(w,'AAPL',[BEFORE,EARLY,LATE],{A:i[A]},b);self.assertEqual(r['entries'][2]['reason'],'SELECTED_ORIGINALS_OR_ROLE_BINDINGS_NOT_SUPPLIED');self.assertEqual(r['comparisons'][1]['statements']['income_statement']['status'],'UNAVAILABLE_ADJACENT_VIEW');self.assertEqual(r['comparisons'][1]['statements']['income_statement']['rows'],[]);self.assertEqual(r['comparisons'][1]['source_relation'],'SELECTED_ORIGINAL_SOURCE_UNAVAILABLE')
 def test_unavailable_gap_is_not_skipped_when_later_source_appears(self):
  third=recipe(accession=C,filed='2024-03-01',accepted_at=LATEST);w,i,b=prepared(recipe(),amendment(),third);i.pop(B);r=company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE,LATEST],i,b);self.assertEqual(r['comparisons'][1]['previous_entry_index'],1);self.assertEqual(r['comparisons'][1]['statements']['income_statement']['rows'],[]);self.assertEqual(r['entries'][0]['accounting']['source_filing']['accession'],A);self.assertEqual(r['entries'][2]['accounting']['source_filing']['accession'],C)
 def test_independent_filing_change_does_not_claim_amendment_or_restatement(self):
  r=compare(recipe(),recipe(accession=B,filed='2024-02-10',accepted_at=LATE));self.assertEqual(r['comparisons'][0]['source_relation'],'INDEPENDENT_SELECTED_FILINGS');self.assertFalse(r['restatements_inferred']);self.assertFalse(r['comparisons'][0]['restatement_established'])
 def test_invalid_cutoffs_stale_identity_and_original_corruption_fail_closed(self):
  w,i,b=prepared(recipe(),amendment())
  for cutoffs in([], [LATE,EARLY], [EARLY,EARLY], [EARLY]*9, ['2024-02-31T00:00:00Z']):
   with self.subTest(cutoffs=cutoffs),self.assertRaises(ValueError):company_statement_vintage_comparison(w,'AAPL',cutoffs,i,b)
  with self.assertRaisesRegex(XBRLError,'stale'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b,expected_collection_sha256='0'*64)
  i[B]['raw']+=b' '
  with self.assertRaisesRegex(XBRLError,'source_digest'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
 def test_rehashed_altered_original_and_taxonomy_cannot_replace_admitted_source(self):
  w,i,b=prepared(recipe(),amendment());raw_edit(i[B],b'>100</ext:IssuerProfit>',b'>101</ext:IssuerProfit>')
  with self.assertRaisesRegex(XBRLError,'admitted_source_mismatch'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
  w,i,b=prepared(recipe(),amendment());d=i[B]['documents'][2];source_doc(i[B],2,d['raw']+b' ')
  with self.assertRaisesRegex(XBRLError,'admitted_dts_mismatch'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
 def test_observed_permissions_still_gate_original_processing(self):
  w,i,b=prepared(recipe(),amendment());i[B]['manifest']['origin']='OBSERVED_OFFICIAL_RESPONSE'
  with self.assertRaisesRegex(XBRLError,'not_approved'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
 def test_boundaries_and_no_input_or_shared_collection_mutation(self):
  w,i,b=prepared(recipe(),amendment());before=copy.deepcopy((i,b,w.xbrl_collections['AAPL']._filings))
  with patch('socket.socket.bind',side_effect=AssertionError('NO_SERVER')),patch('socket.socket.connect',side_effect=AssertionError('NO_PROVIDER')):r=company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
  self.assertEqual((i,b,w.xbrl_collections['AAPL']._filings),before);self.assertEqual(r,company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b));self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));r['entries'][0]['accounting']['statements'].clear();self.assertTrue(company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)['entries'][0]['accounting']['statements'])
  with patch(MODULE+'MAX_ROWS',0),self.assertRaisesRegex(XBRLError,'row_budget'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
  with patch(MODULE+'MAX_OUTPUT',1024),self.assertRaisesRegex(XBRLError,'output_budget'):company_statement_vintage_comparison(w,'AAPL',[EARLY,LATE],i,b)
 def test_eight_exact_cutoffs_preserve_adjacent_order_and_one_collection(self):
  cutoffs=['2024-02-01T12:00:00.00000000'+str(n)+'Z'for n in range(1,9)];r=compare(recipe(),cutoffs=cutoffs);self.assertEqual([p['as_of']for p in r['entries']],cutoffs);self.assertEqual(len(r['comparisons']),7);self.assertTrue(all(p['collection_sha256']==r['collection_sha256']for p in r['entries']));self.assertEqual([(p['previous_entry_index'],p['current_entry_index'])for p in r['comparisons']],[(n,n+1)for n in range(7)])
 def test_single_cutoff_empty_workspace_and_deterministic_canonical_output(self):
  r=compare(recipe(),cutoffs=[EARLY]);self.assertEqual(r['comparisons'],[]);empty=company_statement_vintage_comparison(StockWorkspace(environment={}),'AAPL',[EARLY,LATE],{},{});self.assertEqual(empty['entries'][0]['status'],'UNAVAILABLE');self.assertEqual(empty['comparisons'][0]['statements']['balance_sheet']['rows'],[]);self.assertEqual(canonical(empty),canonical(company_statement_vintage_comparison(StockWorkspace(environment={}),'AAPL',[EARLY,LATE],{},{})))

if __name__=='__main__':unittest.main()
