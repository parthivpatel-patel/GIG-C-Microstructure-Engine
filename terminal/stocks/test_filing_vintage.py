"""Independent authored filing-vintage admission; no SEC requests or application."""
import copy,unittest
from .sec import facts,filings
from .vintages import at_acceptance_time as retained_acceptance

def at_acceptance_time(*args):return retained_acceptance(*args,strict_filing_metadata=True)
from .test_workspace import facts as raw_facts,submissions,CIK

class FilingVintage(unittest.TestCase):
 def inputs(self):return facts(raw_facts(),CIK,'2024-12-31'),filings(submissions(),CIK)['filings']
 def test_fact_and_filing_form_mismatch_cannot_acquire_acceptance_authority(self):
  financials,source=self.inputs();source[-1]['form']='10-Q'
  r=at_acceptance_time(financials,source,'2024-02-11T00:00:00Z')
  self.assertEqual(r['history']['revenue'],[]);self.assertGreater(r['exclusions']['filing_metadata_mismatch'],0)
 def test_same_accession_conflicting_filing_metadata_fails_atomically(self):
  financials,source=self.inputs();source.append({**source[0],'filed':'2024-02-02'});before=copy.deepcopy((financials,source))
  with self.assertRaisesRegex(ValueError,'contradictory_filing'):at_acceptance_time(financials,source,'2024-02-11T00:00:00Z')
  self.assertEqual((financials,source),before)
 def test_same_fact_id_with_changed_retained_content_is_not_last_write_wins(self):
  financials,source=self.inputs();row=copy.deepcopy(financials['history']['revenue'][0]);row['value']='999';financials['revision_history']['revenue'].append(row)
  with self.assertRaisesRegex(ValueError,'contradictory_fact'):at_acceptance_time(financials,source,'2024-02-11T00:00:00Z')
 def test_amendment_cutoff_lineage_and_reproducible_selection_hash(self):
  p=raw_facts();records=p['facts']['us-gaap']['Revenues']['units']['USD'];row=copy.deepcopy(records[0]);records.append({**row,'val':200,'filed':'2024-02-10','accn':'0000000123-24-000002','form':'10-K/A'})
  financials=facts(p,CIK,'2024-12-31');source=filings(submissions(),CIK)['filings']
  early=at_acceptance_time(financials,source,'2024-02-05T00:00:00Z');late=at_acceptance_time(financials,source,'2024-02-11T00:00:00Z')
  self.assertEqual(early['history']['revenue'][0]['value'],'100');self.assertEqual(late['history']['revenue'][0]['value'],'200')
  self.assertTrue(late['filing_lineage']['superseded_source_fact_ids']);self.assertFalse(early['filing_lineage']['superseded_source_fact_ids'])
  self.assertEqual(late['selection_sha256'],at_acceptance_time(copy.deepcopy(financials),list(reversed(source)),'2024-02-11T00:00:00Z')['selection_sha256'])
 def test_missing_and_future_acceptance_do_not_become_midnight_or_prior_vintage(self):
  financials,source=self.inputs();source[-1]['accepted_at']=None
  r=at_acceptance_time(financials,source,'2024-02-11T00:00:00Z');self.assertEqual(r['history']['revenue'],[])
  self.assertGreater(r['exclusions']['unknown_or_ambiguous_acceptance'],0);self.assertFalse(r['filing_lineage']['matched_filings'])
 def test_eligible_cache_date_is_not_an_original_receipt_claim(self):
  financials,source=self.inputs();r=at_acceptance_time(financials,source,'2024-02-11T00:00:00Z')
  self.assertIsNone(r['filing_lineage']['original_response_received_at']);self.assertIn('not',r['filing_lineage']['authority'])
  self.assertTrue(all(x['source_fact_id']for x in r['history']['revenue']))
 def test_filing_date_mismatch_is_explicitly_excluded(self):
  financials,source=self.inputs();source[-1]['filed']='2024-02-02'
  r=at_acceptance_time(financials,source,'2024-02-11T00:00:00Z');self.assertEqual(r['history']['revenue'],[]);self.assertGreater(r['exclusions']['filing_metadata_mismatch'],0)
 def test_duplicates_identical_content_preserve_selection_and_cutoff_nanoseconds(self):
  financials,source=self.inputs();a=at_acceptance_time(financials,source,'2024-02-11T00:00:00.000000001Z');b=at_acceptance_time(financials,source+[copy.deepcopy(source[0])],'2024-02-11T00:00:00.000000001Z')
  self.assertEqual(a['selection_sha256'],b['selection_sha256']);self.assertTrue(a['cutoff_ns'].endswith('000000001'))

 def test_strict_profile_never_infers_legacy_missing_form_and_filing_date(self):
  financials,source=self.inputs();legacy=[{'accession':r['accession'],'accepted_at':r['accepted_at']}for r in source]
  old=retained_acceptance(financials,legacy,'2024-02-11T00:00:00Z');self.assertTrue(old['history']['revenue']);self.assertEqual(old['admission_profile'],'LEGACY_ACCESSION_TIME_V1')
  with self.assertRaises(ValueError):at_acceptance_time(financials,legacy,'2024-02-11T00:00:00Z')
