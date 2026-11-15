"""Additional source-role/vintage acceptance without changing product contracts."""
import copy,hashlib,unittest
from .test_xbrl_statement_set import authored,prepared,export,ROLES,KINDS,A,B,EARLY,LATE
from .test_xbrl_calculation_report import inputs
from .xbrl_collection import FilingCollection
from .xbrl_types import COMPLEX_PROFILE
from .xbrl_binding import bind_declarations
from .xbrl_statement_set import company_statement_history
from .xbrl_instance import digest,XBRLError
from .service import StockWorkspace

class StatementSetSourceAcceptance(unittest.TestCase):
 def test_original_admission_and_revalidated_child_are_distinct_explicit_identities(self):
  e=authored();c=FilingCollection('0000320193');c.ingest_dts_batch([e],numeric_profile=COMPLEX_PROFILE);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',c);graph=inputs(e)[1];before=copy.deepcopy(w.xbrl_collections['AAPL']._filings);packet=export(w,{A:graph},{A:ROLES});original=before[A];derived=bind_declarations(original,graph)
  self.assertNotEqual(original['canonical_sha256'],derived['canonical_sha256']);self.assertEqual(packet['parsed_sha256'],original['canonical_sha256']);self.assertEqual(packet['lineage']['sources'][0]['parsed_sha256'],original['canonical_sha256'])
  for row in packet['statements'].values():self.assertEqual(row['view']['selected_instance_sha256'],derived['canonical_sha256']);self.assertEqual(row['view']['source_filing'],original['source'])
  self.assertEqual(w.xbrl_collections['AAPL']._filings,before)
 def test_retained_role_graph_is_not_used_as_substitute_for_full_original_dts(self):
  w,g,r=prepared();p=w.xbrl_collections['AAPL']._filings[A];relations=p['dts_corroboration']['effective_relationships'];relations['networks'][0]['role']='urn:untrusted-retained-role';relations['sha256']=digest({k:v for k,v in relations.items()if k!='sha256'});p['canonical_sha256']=digest({k:v for k,v in p.items()if k!='canonical_sha256'});before=copy.deepcopy(p)
  packet=export(w,g,r);self.assertEqual(packet['status'],'AVAILABLE');self.assertEqual(packet['parsed_sha256'],before['canonical_sha256']);self.assertTrue(all(v['view']['role']==ROLES[k]for k,v in packet['statements'].items()));self.assertEqual(w.xbrl_collections['AAPL']._filings[A],before)
 def test_coherently_rehashed_changed_full_graph_still_cannot_replace_admitted_dts(self):
  w,g,r=prepared();g=copy.deepcopy(g);relations=g[A]['effective_relationships'];relations['networks'][0]['role']='urn:different-original-graph';relations['sha256']=digest({k:v for k,v in relations.items()if k!='sha256'});g[A]['canonical_sha256']=digest({k:v for k,v in g[A].items()if k!='canonical_sha256'})
  with self.assertRaisesRegex(XBRLError,'existing_dts_binding'):export(w,g,r)
 def test_whole_amendment_with_missing_line_does_not_fill_from_original(self):
  original=authored();amended=authored(income='99',accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A);amended['raw']=amended['raw'].replace(b'<ext:IncomeTotal contextRef="FD" unitRef="USD" decimals="0">99</ext:IncomeTotal>',b'');amended['manifest']['source_sha256']=hashlib.sha256(amended['raw']).hexdigest();w,g,r=prepared(original,amended)
  old=export(w,g,r,at=EARLY);new=export(w,g,r);self.assertEqual(old['statements']['income_statement']['view']['periods'][0]['rows'][0]['value'],'100');row=new['statements']['income_statement']['view']['periods'][0]['rows'][0];self.assertEqual(row['status'],'MISSING');self.assertIsNone(row['value']);self.assertEqual(row['facts'],[]);self.assertEqual(new['source_filing']['accession'],B)
 def test_exact_nanosecond_cutoffs_and_equivalent_clock_order(self):
  w,g,r=prepared();self.assertEqual(export(w,g,r,at='2024-02-01T12:00:00Z')['status'],'UNAVAILABLE');self.assertEqual(export(w,g,r,at=EARLY)['source_filing']['accession'],A)
  with self.assertRaisesRegex(XBRLError,'cutoff_order'):company_statement_history(w,'AAPL',[EARLY,'2024-02-01T07:00:00.000000001-05:00'],g,r)
 def test_role_designation_is_caller_intent_and_never_certified_classification(self):
  w,g,r=prepared();r=copy.deepcopy(r);r[A]['balance_sheet'],r[A]['income_statement']=r[A]['income_statement'],r[A]['balance_sheet'];packet=export(w,g,r);self.assertEqual(packet['status'],'AVAILABLE');self.assertEqual(packet['statements']['balance_sheet']['view']['periods'][0]['rows'][0]['value'],'100');self.assertFalse(packet['complete_statements']);self.assertIn('not inferred',packet['designation_policy']);self.assertTrue(all(row['statement_mapping']['accounting_metric']is None for v in packet['statements'].values()for period in v['view']['periods']for row in period['rows']))
