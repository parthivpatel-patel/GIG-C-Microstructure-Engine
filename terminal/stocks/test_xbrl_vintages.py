"""Independent authored acceptance/amendment vintage expectations."""
import copy,unittest
from unittest.mock import patch
from .test_xbrl_statement_v2 import extension
from .test_xbrl_statements import collection,ROLE,LATE,EARLY
from .service import StockWorkspace
from .xbrl_vintages import company_vintages
from .xbrl_instance import XBRLError,digest

def workspace():
 w=StockWorkspace(environment={});original=extension();amendment=extension(value='399',accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001');w.admit_xbrl_collection('AAPL',collection(original,amendment));return w
CUTOFFS=['2024-01-01T00:00:00Z','2024-02-02T00:00:00Z',LATE]
class Vintages(unittest.TestCase):
 def test_independent_original_then_amendment_without_future_leakage(self):
  w=workspace();before=copy.deepcopy(w.xbrl_collections['AAPL']._filings);p=company_vintages(w,'AAPL',CUTOFFS,role=ROLE)
  self.assertEqual([e['transition']for e in p['entries']],['UNAVAILABLE','FIRST_AVAILABLE','SOURCE_CHANGED'])
  rows=[e['packet']['statement_view']for e in p['entries']];self.assertIsNone(rows[0]['source_filing']);self.assertEqual(rows[1]['periods'][0]['rows'][-1]['value'],'400');self.assertEqual(rows[2]['periods'][0]['rows'][-1]['value'],'399');self.assertIn('AMENDMENT_NOT_ADDITIVELY_MERGED',rows[2]['diagnostics']);self.assertEqual(w.xbrl_collections['AAPL']._filings,before)
 def test_duplicate_equivalent_or_reversed_cutoffs_reject_before_selection(self):
  w=workspace()
  for dates in([LATE,LATE],[LATE,'2024-01-01T00:00:00Z'],['2024-02-01T00:00:00Z','2024-01-31T19:00:00-05:00'],[],[LATE]*9):
   with patch('terminal.stocks.xbrl_vintages.company_contract',side_effect=AssertionError('selection must not run')):
    with self.assertRaises(ValueError):company_vintages(w,'AAPL',dates,role=ROLE)
 def test_stale_collection_and_output_limits_are_atomic(self):
  w=workspace();before=copy.deepcopy(w.xbrl_collections)
  with self.assertRaisesRegex(XBRLError,'stale_collection'):company_vintages(w,'AAPL',CUTOFFS,role=ROLE,expected_collection_sha256='0'*64)
  with patch('terminal.stocks.xbrl_vintages.MAX_BYTES',100),self.assertRaisesRegex(XBRLError,'output_budget'):company_vintages(w,'AAPL',CUTOFFS,role=ROLE)
  self.assertEqual(w.xbrl_collections['AAPL']._filings,before['AAPL']._filings)
 def test_unknown_collection_and_missing_roles_remain_unavailable(self):
  w=StockWorkspace(environment={});p=company_vintages(w,'AAPL',CUTOFFS);self.assertTrue(all(e['transition']=='UNAVAILABLE'for e in p['entries']));self.assertFalse(p['complete_history']);self.assertFalse(p['provider_requested'])
 def test_repeated_source_and_exact_digest_are_deterministic(self):
  w=workspace();p=company_vintages(w,'AAPL',['2024-02-02T00:00:00Z','2024-02-03T00:00:00Z'],role=ROLE);self.assertEqual(p['entries'][1]['transition'],'UNCHANGED_SOURCE');self.assertEqual(p,company_vintages(w,'AAPL',['2024-02-02T00:00:00Z','2024-02-03T00:00:00Z'],role=ROLE));self.assertEqual(p['sha256'],digest({k:v for k,v in p.items()if k!='sha256'}))
 def test_nanosecond_cutoffs_preserve_acceptance_boundary(self):
  w=workspace();p=company_vintages(w,'AAPL',['2024-02-10T12:00:00.000000000Z','2024-02-10T12:00:00.000000001Z'],role=ROLE);self.assertEqual(len(p['entries']),2);self.assertEqual(int(p['entries'][1]['cutoff_ns'])-int(p['entries'][0]['cutoff_ns']),1)
 def test_latest_missing_role_stays_unavailable_instead_of_using_older_statement(self):
  from .test_xbrl_dts import document
  w=StockWorkspace(environment={});new=extension(accession='0000000123-24-000002',filed='2024-02-10',accepted_at=LATE)
  new['documents'][1]=document('presentation.xml',new['documents'][1]['raw'].replace(ROLE.encode(),(ROLE+'/different').encode()))
  w.admit_xbrl_collection('AAPL',collection(extension(),new));p=company_vintages(w,'AAPL',CUTOFFS,role=ROLE);last=p['entries'][-1]['packet']['statement_view'];self.assertEqual(last['status'],'UNAVAILABLE');self.assertEqual(last['reason'],'ROLE_NOT_IN_LATEST_FILING');self.assertEqual(last['periods'],[])
 def test_same_acceptance_filings_remain_ambiguous(self):
  w=StockWorkspace(environment={});a=extension(accepted_at=LATE);b=extension(accession='0000000123-24-000002',accepted_at=LATE)
  w.admit_xbrl_collection('AAPL',collection(a,b));p=company_vintages(w,'AAPL',[LATE],role=ROLE);self.assertEqual(p['entries'][0]['transition'],'AMBIGUOUS');self.assertIsNone(p['entries'][0]['packet']['statement_view']['source_filing'])
