"""Authored explicit chains with no future-source disclosure or inferred edges."""
import copy,unittest
from .test_xbrl_statement_v2 import extension
from .test_xbrl_statements import collection,LATE
from .xbrl_lineage import filing_lineage
from .xbrl_instance import digest,XBRLError
A='0000000123-24-000001';B='0000000123-24-000002';C='0000000123-24-000003'
def chain(root=True):
 rows=[extension(accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A),extension(accession=C,form='10-K/A',filed='2024-02-11',accepted_at='2024-02-11T12:00:00Z',amends_accession=B)]
 return collection(*(([extension()]if root else[])+rows))
class Lineage(unittest.TestCase):
 def test_complete_supplied_chain_retains_originals_and_exact_hash(self):
  c=chain();before=copy.deepcopy(c._filings);p=filing_lineage(c,C,'2024-02-12T00:00:00Z');self.assertEqual(p['status'],'SUPPLIED_CHAIN_RESOLVED');self.assertEqual([r['source']['accession']for r in p['sources']],[C,B,A]);self.assertEqual(len(p['links']),2);self.assertFalse(p['complete_history']);self.assertEqual(c._filings,before);self.assertEqual(p['sha256'],digest({k:v for k,v in p.items()if k!='sha256'}))
 def test_missing_original_and_unknown_parent_are_explicit(self):
  p=filing_lineage(chain(False),C,'2024-02-12T00:00:00Z');self.assertEqual(p['reason'],'SOURCE_NOT_SUPPLIED');self.assertEqual([r['source']['accession']for r in p['sources']],[C,B])
  c=collection(extension(accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE));p=filing_lineage(c,B,LATE);self.assertEqual(p['reason'],'AMENDMENT_PARENT_NOT_DECLARED')
 def test_later_source_and_unknown_acceptance_are_not_disclosed(self):
  c=chain();p=filing_lineage(c,C,LATE);self.assertEqual(p['reason'],'SOURCE_AFTER_CUTOFF');self.assertEqual(p['sources'],[])
  c=collection(extension(accepted_at=None));p=filing_lineage(c,A,LATE);self.assertEqual(p['reason'],'ACCEPTANCE_UNKNOWN');self.assertEqual(p['sources'],[])
 def test_offset_equivalence_preserves_cutoff_membership(self):
  c=chain();a=filing_lineage(c,B,LATE);b=filing_lineage(c,B,'2024-02-10T07:00:00-05:00');self.assertEqual(a['sources'],b['sources']);self.assertEqual(a['cutoff_ns'],b['cutoff_ns'])
 def test_corrupted_source_identity_and_cycle_fail_closed(self):
  c=chain();c._filings[A]['source']['filed']='2024-02-02'
  with self.assertRaisesRegex(XBRLError,'source_identity'):filing_lineage(c,C,'2024-02-12T00:00:00Z')
  c=chain();p=c._filings[B];p['source']['amends_accession']=C;p.pop('canonical_sha256');p['canonical_sha256']=digest(p)
  with self.assertRaises(XBRLError):filing_lineage(c,C,'2024-02-12T00:00:00Z')
 def test_original_does_not_pick_another_filing_as_a_parent(self):
  c=chain();p=filing_lineage(c,A,'2024-02-12T00:00:00Z');self.assertEqual(p['status'],'SUPPLIED_CHAIN_RESOLVED');self.assertEqual(len(p['sources']),1);self.assertEqual(p['links'],[])
