"""Direct offline product exports and original-receipt pre-XML admission."""
import copy,hashlib,unittest
from types import SimpleNamespace
from unittest.mock import patch
from .financial_intelligence_product import company_source_accounting,company_inline_audit
from .test_xbrl_accounting_statements import recipe,prepared,EARLY,LATE,A,B
from .test_inline_dts_source_audit import inputs
from .xbrl_collection import FilingCollection
from .inline_set import TRANSFORMATION_PROFILE
from .xbrl_instance import XBRLError,digest
from .service import StockWorkspace

MODULE='terminal.stocks.financial_intelligence_product.'
def inline(*,profile=None,observed=False):
 p,g,docs,tax,concepts,manifest=inputs(profile=profile,observed=observed)
 c=FilingCollection('0000320193',origin='OBSERVED_OFFICIAL_RESPONSE'if observed else'HISTORICAL_SYNTHETIC',allow_observed=observed)
 c.ingest_inline_set_batch([{'documents':docs,'concepts':concepts,'taxonomy_documents':tax}],transformation_profile=profile)
 w=StockWorkspace(environment={});w.admit_xbrl_collection('AAPL',c)
 entry={'documents':docs,'concepts':concepts,'taxonomy_documents':tax,'transformation_profile':profile,'embedded_profile':None,'acquisition_manifest':manifest,'expected_acquisition_manifest_sha256':digest(manifest)}
 return w,{p['source']['accession']:entry}
def audit(w,originals,**kw):return company_inline_audit(w,'AAPL',LATE,originals,**kw)
def selected(originals):return next(iter(originals.values()))

class FinancialIntelligenceProducts(unittest.TestCase):
 def test_accounting_exact_provenance_and_no_mutation_or_activation(self):
  w,i,b=prepared(recipe(exact=True));before=copy.deepcopy((i,b,w.xbrl_collections['AAPL']._filings))
  with patch('socket.socket.connect',side_effect=AssertionError('NO_PROVIDER')),patch('socket.socket.bind',side_effect=AssertionError('NO_SERVER')):
   p=company_source_accounting(w,'AAPL',LATE,i,b)
  self.assertEqual(p['status'],'AVAILABLE');self.assertFalse(p['source_confidence']['independent_issuer_authentication']);self.assertFalse(p['provider_requested']);self.assertTrue(p['read_only']);self.assertEqual(p['source']['canonical_sha256'],p['accounting']['original_parsed_sha256']);self.assertEqual(p['dts']['canonical_sha256'],p['accounting']['dts_sha256']);self.assertEqual(p['sha256'],digest({k:v for k,v in p.items()if k!='sha256'}));self.assertEqual((i,b,w.xbrl_collections['AAPL']._filings),before)
 def test_accounting_cutoff_amendment_and_latest_missing_original_never_fall_back(self):
  w,i,b=prepared(recipe(),recipe(alias=None,accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=A))
  old=company_source_accounting(w,'AAPL',EARLY,i,b);new=company_source_accounting(w,'AAPL',LATE,i,b)
  self.assertEqual(old['accounting']['source_filing']['accession'],A);self.assertEqual(new['accounting']['source_filing']['accession'],B);self.assertEqual(len(new['accounting']['lineage']['sources']),2)
  unavailable=company_source_accounting(w,'AAPL',LATE,{A:i[A]},b);self.assertEqual(unavailable['status'],'UNAVAILABLE');self.assertIsNone(unavailable['source']);self.assertIsNone(unavailable['dts']);self.assertEqual(unavailable['reason'],'SELECTED_ORIGINALS_OR_ROLE_BINDINGS_NOT_SUPPLIED')
 def test_accounting_stale_cutoff_corrupted_original_and_output_limits(self):
  w,i,b=prepared()
  with self.assertRaisesRegex(XBRLError,'stale'):company_source_accounting(w,'AAPL',LATE,i,b,expected_collection_sha256='0'*64)
  with self.assertRaises(ValueError):company_source_accounting(w,'AAPL','2024-02-31T00:00:00Z',i,b)
  i[A]['raw']+=b' '
  with self.assertRaisesRegex(XBRLError,'source_digest'):company_source_accounting(w,'AAPL',LATE,i,b)
  w,i,b=prepared()
  with patch(MODULE+'MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'export_budget'):company_source_accounting(w,'AAPL',LATE,i,b)
 def test_accounting_missing_conflicting_and_unsupported_rows_remain_explicit(self):
  for alias,state in[(None,'MISSING'),('101','CONFLICTING')]:
   w,i,b=prepared(recipe(alias=alias));p=company_source_accounting(w,'AAPL',LATE,i,b);row=p['accounting']['statements']['income_statement']['periods'][0]['rows'][-1];self.assertEqual(row['status'],state);self.assertIsNone(row['value'])
 def test_inline_valid_legacy_transformed_observed_and_detached_outputs(self):
  for profile,observed in[(None,False),(TRANSFORMATION_PROFILE,False),(None,True)]:
   w,o=inline(profile=profile,observed=observed);before=copy.deepcopy((o,w.xbrl_collections['AAPL']._filings))
   with patch('socket.socket.connect',side_effect=AssertionError('NO_PROVIDER')),patch('socket.socket.bind',side_effect=AssertionError('NO_SERVER')):p=audit(w,o)
   self.assertEqual(p['status'],'AVAILABLE');self.assertEqual(p['receipt']['transformation_profile'],profile);self.assertFalse(p['receipt']['independent_source_authentication']);self.assertNotIn('raw',p['receipt']);self.assertEqual((o,w.xbrl_collections['AAPL']._filings),before)
   p['receipt']['inline_documents'].clear();self.assertTrue(audit(w,o)['receipt']['inline_documents'])
 def test_inline_stale_invalid_cutoff_missing_selected_and_no_collection(self):
  w,o=inline()
  with self.assertRaisesRegex(XBRLError,'stale_collection'):audit(w,o,expected_collection_sha256='0'*64)
  with self.assertRaises(ValueError):company_inline_audit(w,'AAPL','2024-02-31T00:00:00Z',o)
  self.assertEqual(audit(w,{})['reason'],'SELECTED_INLINE_ORIGINALS_NOT_SUPPLIED')
  empty=company_inline_audit(StockWorkspace(environment={}),'AAPL',LATE,{})
  self.assertEqual(empty['status'],'UNAVAILABLE');self.assertIsNone(empty['receipt'])
 def test_inline_missing_or_unresolved_latest_amendment_never_uses_old_originals(self):
  w,o=inline();c=w.xbrl_collections['AAPL'];old=next(iter(c._filings.values()));new=copy.deepcopy(old);new['source'].update(accession=B,form='10-K/A',filed='2024-02-10',accepted_at=LATE,amends_accession=old['source']['accession']);new['canonical_sha256']=digest({k:v for k,v in new.items()if k!='canonical_sha256'});c._commit_parsed([new])
  self.assertEqual(audit(w,o)['reason'],'SELECTED_INLINE_ORIGINALS_NOT_SUPPLIED')
  new=copy.deepcopy(new);new['source']['amends_accession']=None;new['canonical_sha256']=digest({k:v for k,v in new.items()if k!='canonical_sha256'});c._filings[B]=new
  self.assertEqual(audit(w,o)['reason'],'EXPLICIT_AMENDMENT_CHAIN_UNRESOLVED')
 def test_inline_manifest_receipt_reference_and_uri_changes_reject_before_xml(self):
  for change in('receipt','reference','uri','source','body'):
   w,o=inline(observed=True);e=selected(o);doc=e['documents'][0]
   if change=='receipt':doc['manifest']['received_at']='2026-11-15T13:00:00Z'
   elif change=='reference':doc['manifest']['permission_reference']='changed-approved-reference'
   elif change=='uri':doc['uri']=doc['uri'].replace('primary.htm','other.htm')
   elif change=='source':doc['manifest']['accession']='0000000123-24-000099'
   else:doc['raw']+=b' ';doc['manifest']['source_sha256']=hashlib.sha256(doc['raw']).hexdigest()
   with self.subTest(change=change),patch(MODULE+'parse_document_set',side_effect=AssertionError('NO_XML'))as parser:
    with self.assertRaises(XBRLError):audit(w,o)
    parser.assert_not_called()
 def test_inline_permissions_profile_and_duplicate_documents_reject_before_xml(self):
  for change in('permission','future_profile','wrong_profile','duplicate'):
   w,o=inline(observed=True,profile=TRANSFORMATION_PROFILE);e=selected(o)
   if change=='permission':e['documents'][1]['manifest']['permission_reference']=None
   elif change=='future_profile':e['embedded_profile']='future'
   elif change=='wrong_profile':e['transformation_profile']=None
   else:e['documents'].append(copy.deepcopy(e['documents'][0]))
   with self.subTest(change=change),patch(MODULE+'parse_document_set',side_effect=AssertionError('NO_XML'))as parser:
    with self.assertRaises(XBRLError):audit(w,o)
    parser.assert_not_called()
 def test_inline_taxonomy_body_identity_membership_and_duplicates_reject_before_xml(self):
  for change in('body','identity','uri','duplicate','missing'):
   w,o=inline();e=selected(o);tax=e['taxonomy_documents']
   if change=='body':tax[0]['raw']+=b' '
   elif change=='identity':tax[0]['raw']+=b' ';tax[0]['sha256']=hashlib.sha256(tax[0]['raw']).hexdigest()
   elif change=='uri':tax[0]['uri']=tax[0]['uri'].replace('authored.xsd','other.xsd')
   elif change=='duplicate':tax.append(copy.deepcopy(tax[0]))
   else:tax.clear()
   with self.subTest(change=change),patch(MODULE+'parse_document_set',side_effect=AssertionError('NO_XML'))as parser:
    with self.assertRaises(XBRLError):audit(w,o)
    parser.assert_not_called()
 def test_inline_acquisition_order_hash_and_coordinator_lock_reject_before_xml(self):
  for change in('order','hash','missing','plan'):
   w,o=inline();e=selected(o)
   if change=='order':e['documents'].reverse()
   elif change=='hash':e['expected_acquisition_manifest_sha256']='0'*64
   elif change=='missing':e['acquisition_manifest']=None
   else:w.filing_ingestors['AAPL']=SimpleNamespace(plans={next(iter(o)):{'inline_manifest_sha256':'0'*64}},collection=w.xbrl_collections['AAPL'],status=lambda:{})
   with self.subTest(change=change),patch(MODULE+'parse_document_set',side_effect=AssertionError('NO_XML'))as parser:
    with self.assertRaises(XBRLError):audit(w,o)
    parser.assert_not_called()
 def test_inline_no_intent_preserves_nonsemantic_source_order_and_output_budget(self):
  w,o=inline();e=selected(o);e['acquisition_manifest']=None;e['expected_acquisition_manifest_sha256']=None;first=audit(w,o);e['documents'].reverse();second=audit(w,o)
  self.assertEqual(first['parsed_sha256'],second['parsed_sha256']);self.assertEqual(first['dts_sha256'],second['dts_sha256']);self.assertEqual(first['receipt']['supplied_document_order'],list(reversed(second['receipt']['supplied_document_order'])))
  before=copy.deepcopy((o,w.xbrl_collections['AAPL']._filings))
  with patch(MODULE+'MAX_OUTPUT',1),self.assertRaisesRegex(XBRLError,'export_budget'):audit(w,o)
  self.assertEqual((o,w.xbrl_collections['AAPL']._filings),before)

if __name__=='__main__':unittest.main()
