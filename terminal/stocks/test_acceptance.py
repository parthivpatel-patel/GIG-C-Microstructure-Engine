import copy,unittest
from .sec import facts
from .vintages import at_acceptance_time
from .test_workspace import facts as source_facts
class Acceptance(unittest.TestCase):
 def input(self):
  p=source_facts();f=facts(p,'0000320193','2024-12-31');return f
 def test_unknown_acceptance_is_not_replaced_by_filing_midnight(self):
  f=self.input();r=at_acceptance_time(f,[],'2024-12-31T12:00:00Z');self.assertTrue(all(not v for v in r['history'].values()));self.assertGreater(r['exclusions']['unknown_or_ambiguous_acceptance'],0)
 def test_exact_boundary_and_no_current_filing_substitution(self):
  f=self.input();allrows=[r for v in f['history'].values() for r in v];accessions={r['accession'] for r in allrows};filings=[{'accession':a,'accepted_at':'2024-12-30T12:00:00.000000001Z'} for a in accessions];before=copy.deepcopy(f)
  a=at_acceptance_time(f,filings,'2024-12-30T12:00:00Z');self.assertTrue(all(not v for v in a['history'].values()));b=at_acceptance_time(f,filings,'2024-12-30T12:00:00.000000001Z');self.assertTrue(any(b['history'].values()));self.assertEqual(f,before)
 def test_timezone_equivalence_conflicts_and_truncated_coverage(self):
  f=self.input();a=next(r for rows in f['history'].values() for r in rows)['accession'];filings=[{'accession':a,'accepted_at':'2024-12-30T12:00:00Z'}];x=at_acceptance_time(f,filings,'2024-12-30T07:00:00-05:00');y=at_acceptance_time(f,filings,'2024-12-30T12:00:00Z');self.assertEqual(x['history'],y['history']);filings.append({'accession':a,'accepted_at':'2024-12-30T13:00:00Z'});z=at_acceptance_time(f,filings,'2024-12-31T00:00:00Z');self.assertGreater(z['exclusions']['unknown_or_ambiguous_acceptance'],0)
