"""Acceptance and original-DTS product binding, never presentation-based inference."""
import copy,unittest
from unittest.mock import patch
from .test_xbrl_calculation_report import inputs
from .test_xbrl_statement_v2 import extension
from .test_xbrl_statements import collection,ROLE,LATE,EARLY
from .service import StockWorkspace
from .xbrl_calculation_product import company_calculation_contract
from .xbrl_instance import XBRLError,digest
A='0000000123-24-000001';B='0000000123-24-000002'
def prepared():
 a=extension();b=extension(value='399',accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A)
 w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection(a,b));return w,{A:inputs(a)[1],B:inputs(b)[1]}
class CalculationProduct(unittest.TestCase):
 def test_cutoff_selects_original_then_amendment_with_bound_graph_and_lineage(self):
  w,g=prepared();before=copy.deepcopy(w.xbrl_collections['AAPL']._filings)
  a=company_calculation_contract(w,'AAPL',EARLY,g,role=ROLE);b=company_calculation_contract(w,'AAPL',LATE,g,role=ROLE)
  self.assertEqual(a['report']['source_filing']['accession'],A);self.assertEqual(b['report']['source_filing']['accession'],B);self.assertEqual(len(b['lineage']['sources']),2);self.assertEqual(a['status'],'AVAILABLE');self.assertIsNone(a['report']['selected_reported_value']);self.assertEqual(w.xbrl_collections['AAPL']._filings,before)
 def test_no_eligible_or_unknown_collection_is_unavailable_without_binding(self):
  w,g=prepared()
  for owner,cutoff in((w,'2024-01-01T00:00:00Z'),(StockWorkspace(environment={}),LATE)):
   with patch('terminal.stocks.xbrl_calculation_product.bind_calculation_report',side_effect=AssertionError('no binder')):
    r=company_calculation_contract(owner,'AAPL',cutoff,g,role=ROLE);self.assertEqual(r['status'],'UNAVAILABLE');self.assertIsNone(r['report'])
 def test_missing_current_graph_never_uses_an_older_filing_graph(self):
  w,g=prepared();r=company_calculation_contract(w,'AAPL',LATE,{A:g[A]},role=ROLE);self.assertEqual(r['reason'],'ORIGINAL_DTS_NOT_SUPPLIED');self.assertIsNone(r['report'])
  with self.assertRaises(XBRLError):company_calculation_contract(w,'AAPL',LATE,{B:g[A]},role=ROLE)
 def test_stale_collection_and_bounded_output_reject_without_mutation(self):
  w,g=prepared();before=w.xbrl_collections['AAPL'].page()
  with self.assertRaisesRegex(XBRLError,'stale_collection'):company_calculation_contract(w,'AAPL',LATE,g,role=ROLE,expected_collection_sha256='0'*64)
  with patch('terminal.stocks.xbrl_calculation_product.MAX_OUTPUT',100),self.assertRaisesRegex(XBRLError,'output_budget'):company_calculation_contract(w,'AAPL',LATE,g,role=ROLE)
  self.assertEqual(w.xbrl_collections['AAPL'].page(),before)
 def test_ambiguous_latest_sources_do_not_select_a_graph(self):
  a=extension(accepted_at=LATE);b=extension(accession=B,accepted_at=LATE);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection(a,b));r=company_calculation_contract(w,'AAPL',LATE,{},role=ROLE);self.assertEqual(r['reason'],'AMBIGUOUS_LATEST_FILING');self.assertIsNone(r['report'])
 def test_unresolved_ancestor_chain_does_not_claim_reconstruction(self):
  b=extension(accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A);w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',collection(b));r=company_calculation_contract(w,'AAPL',LATE,{B:inputs(b)[1]},role=ROLE);self.assertEqual(r['reason'],'EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED');self.assertFalse(r['complete_statements'])
 def test_both_modes_bind_and_packet_hash_is_deterministic(self):
  w,g=prepared()
  for mode in('round-to-nearest','truncation'):
   r=company_calculation_contract(w,'AAPL',EARLY,g,role=ROLE,rounding_mode=mode);self.assertEqual(r['report']['rounding_mode'],mode);self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));self.assertEqual(r,company_calculation_contract(w,'AAPL',EARLY,g,role=ROLE,rounding_mode=mode))
