"""Independently expected authored filing versions;no network,DB or application."""
import copy,unittest
from unittest.mock import patch
from .test_xbrl_instance import xml,manifest,NS
from .xbrl_instance import selected_concepts,XBRLError
from .xbrl_collection import FilingCollection

def entry(value='100.00',**metadata):
 raw=xml().replace(b'>100.00<',('>'+value+'<').encode())
 return {'raw':raw,'manifest':manifest(raw,**metadata),'concepts':selected_concepts(NS)}
def collection():return FilingCollection('0000320193')
EARLY='2024-02-01T12:00:00.000000001Z';LATE='2024-02-10T12:00:00Z'
def amendment(value='200'):
 return entry(value,accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001')
class XBRLCollection(unittest.TestCase):
 def test_exact_cutoff_and_amendment_replaces_same_period_without_addition(self):
  c=collection();c.ingest_batch([amendment(),entry()]);before=c.at_acceptance_time('2024-02-01T12:00:00Z');self.assertEqual(before['history']['revenue'],[])
  early=c.at_acceptance_time(EARLY);late=c.at_acceptance_time(LATE)
  self.assertEqual(early['history']['revenue'][0]['value'],'100.00');self.assertEqual(late['history']['revenue'][0]['value'],'200');self.assertTrue(late['superseded_source_fact_ids']);self.assertFalse(late['unresolved_amendment_filings'])
 def test_missing_acceptance_never_uses_filing_midnight_or_original_receipt(self):
  c=collection();c.ingest_batch([entry(accepted_at=None,received_at='2024-02-01T12:00:00Z')]);r=c.at_acceptance_time(LATE);self.assertEqual(r['history']['revenue'],[]);self.assertEqual(r['exclusions']['unknown_acceptance_filings'],1)
 def test_unknown_receipt_and_unresolved_amendment_are_preserved(self):
  c=collection();c.ingest_batch([amendment()]);r=c.at_acceptance_time(LATE);self.assertIsNone(r['source_filings'][0]['received_at']);self.assertEqual(r['unresolved_amendment_filings'],['0000000123-24-000002'])
 def test_conflicting_same_accession_is_atomic_and_identical_retry_is_idempotent(self):
  c=collection();receipt=c.ingest_batch([entry()]);self.assertEqual(c.ingest_batch([entry()]),receipt);before=c.at_acceptance_time(LATE)
  with self.assertRaisesRegex(XBRLError,'accession_content_conflict'):c.ingest_batch([amendment(),entry('999')])
  self.assertEqual(c.at_acceptance_time(LATE),before)
 def test_malformed_second_shard_does_not_publish_first(self):
  c=collection();bad=amendment();bad['raw']=b'<broken'
  with self.assertRaises(ValueError):c.ingest_batch([entry(),bad])
  self.assertEqual(c.page()['total'],0)
 def test_cross_issuer_origin_or_changed_source_contract_fail_closed(self):
  c=collection();bad=entry();bad['manifest']['issuer_cik']='0000000001'
  for item in [bad,entry(origin='OBSERVED_OFFICIAL_RESPONSE')]:
   with self.assertRaises(ValueError):c.ingest_batch([item])
  self.assertEqual(c.page()['total'],0)
 def test_amendment_cycles_or_future_predecessors_are_rejected_atomically(self):
  c=collection();a=entry(form='10-K/A',amends_accession='0000000123-24-000002');b=amendment()
  with self.assertRaises(ValueError):c.ingest_batch([a,b])
  self.assertEqual(c.page()['total'],0)
 def test_pagination_is_identity_bound_and_returned_metadata_does_not_alias_store(self):
  c=collection();c.ingest_batch([entry(),amendment()]);p=c.page(limit=1);p['records'][0]['filed']='1900-01-01';r=c.page(offset=1,expected_collection_sha256=p['collection_sha256']);self.assertEqual(r['total'],2)
  for args in [{'offset':1},{'offset':True},{'limit':9},{'offset':3},{'offset':1,'expected_collection_sha256':'0'*64}]:
   with self.assertRaises(ValueError):c.page(**args)
  self.assertNotEqual(c.page()['records'][0]['filed'],'1900-01-01')
 def test_same_acceptance_different_filings_are_ambiguous_not_arbitrarily_selected(self):
  c=collection();c.ingest_batch([entry(),entry('101',accession='0000000123-24-000003')]);r=c.at_acceptance_time(LATE);self.assertEqual(r['history']['revenue'],[]);self.assertGreater(r['exclusions']['ambiguous_same_time_facts'],0)
  # Different taxonomy namespaces are preserved,not assumed equivalent by local name.
  future=amendment('101');future['raw']=future['raw'].replace(b'us-gaap/2024',b'us-gaap/2025');future['manifest']=manifest(future['raw'],accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession='0000000123-24-000001');future['concepts']=selected_concepts(NS.replace('2024','2025'));d=collection();d.ingest_batch([entry(),future]);v=d.at_acceptance_time(LATE);self.assertEqual(len(v['history']['revenue']),2);self.assertEqual(len({r['source_xbrl_concept']for r in v['history']['revenue']}),2)
 def test_collection_and_input_budgets_fail_before_publication(self):
  c=collection()
  for entries in [[],[entry()]*9,[{**entry(),'raw':b'x'*(8*1024*1024+1)}]]:
   with self.assertRaises(ValueError):c.ingest_batch(entries)
  with patch('terminal.stocks.xbrl_collection.MAX_FILINGS',1),self.assertRaisesRegex(XBRLError,'filing_budget'):c.ingest_batch([entry(),amendment()])
  self.assertEqual(c.page()['total'],0)
 def test_order_independence_exact_units_provenance_and_unchanged_inputs(self):
  entries=[entry(),amendment()];before=copy.deepcopy(entries);a=collection();b=collection();a.ingest_batch(entries);b.ingest_batch(list(reversed(entries)));x=a.at_acceptance_time(LATE)
  self.assertEqual(x,b.at_acceptance_time(LATE));self.assertEqual(entries,before);self.assertEqual(x['history']['revenue'][0]['unit'],'USD');self.assertTrue(x['history']['revenue'][0]['source_xml_fact_ids']);self.assertIsNone(x['source_filings'][0]['received_at'])
 def test_dimensional_or_conflicting_values_do_not_leak_into_consolidated_selection(self):
  raw=xml('<g:Assets contextRef="I" unitRef="USD">100</g:Assets><g:Assets contextRef="I" unitRef="USD">200</g:Assets>');e={'raw':raw,'manifest':manifest(raw),'concepts':selected_concepts(NS)};c=collection();c.ingest_batch([e]);r=c.at_acceptance_time(LATE);self.assertEqual(r['history']['assets'],[]);self.assertEqual(r['selected_input_coverage'][0]['xbrl_coverage']['excluded']['unverified_or_conflicting'],2)
