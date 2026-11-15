"""Adversarial original-byte reconstruction; never provider or application access."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_dimensional_calculation import fixture,inputs,NS,rehash
from .test_xbrl_negative_dimensions import negative
from .test_xbrl_embedded import embedded
from .test_xbrl_dts import document
from .xbrl_instance import parse_instance,selected_concepts,digest,XBRLError
from .xbrl_dts import discover,EMBEDDED_PROFILE
from .xbrl_binding import bind_declarations
from .xbrl_dimensional_calculation import bind_dimensional_calculation_report
from .xbrl_dts_source_audit import audit_dts_sources

def audit(e=None,p=None,g=None,**kw):
 e=fixture()if e is None else e
 if p is None or g is None:
  original,graph=inputs(e);p=original if p is None else p;g=graph if g is None else g
 return audit_dts_sources(p,g,e['raw'],e['documents'],manifest=e['manifest'],concepts=e['concepts'],instance_uri=e['instance_uri'],**kw)

class DTSSourceAudit(unittest.TestCase):
 def test_exact_source_closure_binds_original_fact_context_unit_and_graph_ids(self):
  e=fixture();p,g=inputs(e);before=copy.deepcopy((e,p,g));r=audit(e,p,g)
  self.assertEqual(r['status'],'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION');self.assertEqual(r['parsed_sha256'],p['canonical_sha256']);self.assertEqual(r['dts_sha256'],g['canonical_sha256']);self.assertEqual(r['source_fact_ids'],[f['source_fact_id']for f in p['facts']]);self.assertEqual(r['source_context_sha256s'],{k:v['semantic_sha256']for k,v in sorted(p['contexts'].items())});self.assertEqual(r['source_unit_sha256s'],{k:v['semantic_sha256']for k,v in sorted(p['units'].items())});self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));self.assertEqual((e,p,g),before);self.assertFalse(r['provider_requested']);self.assertFalse(r['independent_source_authentication'])
 def test_rehashed_changed_global_default_rejects_against_unchanged_original_bytes(self):
  e=fixture(None,default=True);p,g=inputs(e);bad=copy.deepcopy(g)
  for a in bad['definition'][0]['arcs']:
   if a['kind']=='dimension-default':a['to']='{'+NS+'}North'
  rehash(bad)
  self.assertEqual(bind_dimensional_calculation_report(p,bad)['global_default_dimensions']['{'+NS+'}RegionAxis'],'{'+NS+'}North')
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(e,p,bad)
 def test_rehashed_changed_definition_or_effective_calculation_is_not_source_evidence(self):
  for kind in('definition','calculation','sourcehash','reference'):
   e=fixture();p,g=inputs(e);bad=copy.deepcopy(g)
   if kind=='definition':bad['definition'][0]['arcs'][0]['closed']=False
   elif kind=='calculation':
    network=next(n for n in bad['effective_relationships']['networks']if n['kind']=='calculation');network['arcs'][0]['weight']={'numerator':'-1','denominator':'1'};bad['effective_relationships']['sha256']=digest({k:v for k,v in bad['effective_relationships'].items()if k!='sha256'})
   elif kind=='sourcehash':bad['documents'][0]['sha256']='0'*64
   else:bad['schema_roots']=[]
   rehash(bad)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(e,p,bad)
 def test_rehashed_changed_declaration_or_type_metadata_is_not_source_evidence(self):
  for kind in('concept','type'):
   e=fixture();p,g=inputs(e);bad=copy.deepcopy(g)
   if kind=='concept':bad['concepts']['{'+NS+'}Assets']['declaration']['abstract']=True
   else:bad['type_declarations']={'{urn:invented}Type':{'declaration':{'base':None,'facets':[],'unsupported':[]},'source_documents':[]}}
   rehash(bad)
   with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(e,p,bad)
 def test_rehashed_fact_values_or_context_semantics_cannot_replace_original_parse(self):
  for kind in('value','context','unit','factid','refs'):
   e=fixture();p,g=inputs(e);bad=copy.deepcopy(p)
   if kind=='value':bad['facts'][0]['value']='9999'
   elif kind=='context':bad['contexts']['I']['period']['end']='2022-12-31'
   elif kind=='unit':bad['units']['USD']['numerator']=['{urn:invented}USD']
   elif kind=='factid':bad['facts'][0]['source_fact_id']='0'*64
   else:bad['schema_references']=[]
   rehash(bad)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'original_parsed_mismatch'):audit(e,bad,g)
 def test_raw_body_digest_mismatches_reject_before_artifact_reconstruction(self):
  e=fixture();p,g=inputs(e);bad=copy.deepcopy(e);bad['documents'][0]['raw']+=b' '
  with self.assertRaisesRegex(XBRLError,'document_digest'):audit(bad,p,g)
  bad=copy.deepcopy(e);bad['raw']+=b' '
  with self.assertRaisesRegex(XBRLError,'source_digest'):audit(bad,p,g)
 def test_changed_raw_document_and_matching_new_body_hash_still_fail_old_graph_binding(self):
  e=fixture();p,g=inputs(e);bad=copy.deepcopy(e);body=bad['documents'][-1]['raw'].replace(b'closed="true"',b'closed="false"');bad['documents'][-1]=document('dimensions.xml',body)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(bad,p,g)
 def test_complete_exact_original_coverage_rejects_missing_and_unreferenced_extras(self):
  e=fixture();p,g=inputs(e);missing=copy.deepcopy(e);missing['documents'].pop()
  with self.assertRaisesRegex(XBRLError,'original_closure_required'):audit(missing,p,g)
  extra=copy.deepcopy(e);extra['documents'].append(document('unreferenced.xsd',b'<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:unreferenced"/>'))
  with self.assertRaisesRegex(XBRLError,'original_document_coverage'):audit(extra,p,g)
 def test_duplicate_original_uris_reject_even_if_bytes_are_identical(self):
  e=fixture();p,g=inputs(e);e['documents'].append(copy.deepcopy(e['documents'][0]))
  with self.assertRaisesRegex(XBRLError,'duplicate_original_uri'):audit(e,p,g)
 def test_document_order_does_not_change_canonical_receipt(self):
  e=fixture();p,g=inputs(e);expected=audit(e,p,g);e['documents'].reverse();self.assertEqual(audit(e,p,g),expected)
 def test_processing_permission_failure_precedes_any_xml(self):
  e=fixture();p,g=inputs(e);e['manifest'].update(origin='OBSERVED_OFFICIAL_RESPONSE',source_url='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/instance.xml',permission_reference='authored private processing approval')
  with patch('terminal.stocks.xbrl_dts_source_audit.parse_instance',side_effect=AssertionError('NO_UNAPPROVED_PARSE'))as parser,patch('terminal.stocks.xbrl_dts_source_audit.discover',side_effect=AssertionError('NO_UNAPPROVED_DTS'))as discovery:
   with self.assertRaisesRegex(XBRLError,'not_approved'):audit(e,p,g)
   parser.assert_not_called();discovery.assert_not_called()
 def test_approved_observed_scope_matches_source_uri_and_keeps_reference_private(self):
  e=fixture();e['instance_uri']='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/instance.xml';e['manifest'].update(origin='OBSERVED_OFFICIAL_RESPONSE',source_url=e['instance_uri'],permission_reference='authored private processing approval');p=parse_instance(e['raw'],e['manifest'],e['concepts'],allow_observed=True)
  # All referenced raw documents remain supplied locally under actual resolved URIs.
  base=e['instance_uri'].rsplit('/',1)[0]+'/'
  for d in e['documents']:d['uri']=base+d['uri'].rsplit('/',1)[-1]
  g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],origin=e['manifest']['origin'],allow_observed=True,permission_reference=e['manifest']['permission_reference']);r=audit(e,p,g,allow_observed=True);self.assertEqual(r['origin'],'OBSERVED_OFFICIAL_RESPONSE');self.assertNotIn(e['manifest']['permission_reference'],str(r))
  e['instance_uri']=e['instance_uri'].replace('/instance.xml','/other.xml')
  with self.assertRaisesRegex(XBRLError,'original_uri_scope'):audit(e,p,g,allow_observed=True)
 def test_embedded_profile_is_explicit_and_cannot_be_substituted(self):
  e=embedded();p=parse_instance(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],embedded_profile=EMBEDDED_PROFILE)
  r=audit(e,p,g,embedded_profile=EMBEDDED_PROFILE);self.assertEqual(r['embedded_profile'],EMBEDDED_PROFILE)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(e,p,g)
 def test_unsupported_semantics_are_reconstructed_not_silently_removed(self):
  e=embedded();p=parse_instance(e['raw'],e['manifest'],e['concepts']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents']);self.assertTrue(g['unsupported_semantics']);audit(e,p,g);bad=copy.deepcopy(g);bad['unsupported_semantics']=[];rehash(bad)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(e,p,bad)
 def test_bound_or_derived_artifact_cannot_substitute_for_original(self):
  e=fixture();p,g=inputs(e)
  with self.assertRaisesRegex(XBRLError,'original_parsed_mismatch'):audit(e,bind_declarations(p,g),g)
  bad=copy.deepcopy(p);bad['schema']='gig.sec.xbrl.dimensional_instance.v4';rehash(bad)
  with self.assertRaisesRegex(XBRLError,'original_plain_artifact_required'):audit(e,bad,g)
 def test_explicit_concept_profile_is_not_inferred_from_retained_artifact(self):
  e=fixture();p,g=inputs(e);e['concepts']={}
  with self.assertRaisesRegex(XBRLError,'original_parsed_mismatch'):audit(e,p,g)
 def test_plain_original_contract_rejects_inline_document_sets(self):
  e=fixture();p,g=inputs(e);bad=copy.deepcopy(p);bad['schema']='gig.sec.xbrl.inline_set.v1';rehash(bad)
  with self.assertRaisesRegex(XBRLError,'original_plain_artifact_required'):audit(e,bad,g)
 def test_artifact_hashes_and_versions_reject_instead_of_repairing_input(self):
  for kind in('parsed','dts','version'):
   e=fixture();p,g=inputs(e)
   if kind=='parsed':p['canonical_sha256']='0'*64
   elif kind=='dts':g['canonical_sha256']='0'*64
   else:g['schema']='gig.sec.xbrl.dts.v99';rehash(g)
   with self.assertRaisesRegex(XBRLError,'artifact_identity|original_plain_artifact_required'):audit(e,p,g)
 def test_original_byte_and_artifact_output_limits_are_enforced(self):
  e=fixture();p,g=inputs(e)
  for key,limit,code in(('MAX_INSTANCE',1,'instance_budget'),('MAX_INPUT',1,'input_budget'),('MAX_PARSED',1,'artifact_budget'),('MAX_GRAPH',1,'artifact_budget'),('MAX_OUTPUT',1,'output_budget')):
   with patch('terminal.stocks.xbrl_dts_source_audit.'+key,limit),self.subTest(limit=key),self.assertRaisesRegex(XBRLError,code):audit(e,p,g)
  bad=copy.deepcopy(e);bad['documents']*=17
  with self.assertRaisesRegex(XBRLError,'document_budget'):audit(bad,p,g)
 def test_source_audit_is_not_a_claim_of_full_negative_drs_or_accounting_validation(self):
  e=negative();p,g=inputs(e);r=audit(e,p,g);self.assertEqual(r['status'],'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION');self.assertFalse(r['independent_source_authentication']);self.assertNotIn('complete_drs_validation',r);self.assertNotIn('selected_reported_value',r)
 def test_manifest_processing_reference_mismatch_rejects_before_xml(self):
  e=fixture();e['instance_uri']='https://www.sec.gov/Archives/edgar/data/320193/000000012324000001/instance.xml';e['manifest'].update(origin='OBSERVED_OFFICIAL_RESPONSE',source_url=e['instance_uri'],permission_reference='authored-first-processing-reference');base=e['instance_uri'].rsplit('/',1)[0]+'/'
  for d in e['documents']:d['uri']=base+d['uri'].rsplit('/',1)[-1]
  p=parse_instance(e['raw'],e['manifest'],e['concepts'],allow_observed=True);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'],origin=e['manifest']['origin'],allow_observed=True,permission_reference=e['manifest']['permission_reference']);e['manifest']['permission_reference']='authored-different-processing-reference'
  with patch('terminal.stocks.xbrl_dts_source_audit.parse_instance',side_effect=AssertionError('NO_MISMATCHED_PARSE'))as parser,patch('terminal.stocks.xbrl_dts_source_audit.discover',side_effect=AssertionError('NO_MISMATCHED_DTS'))as discovery:
   with self.assertRaisesRegex(XBRLError,'origin_scope'):audit(e,p,g,allow_observed=True)
   parser.assert_not_called();discovery.assert_not_called()
 def test_malformed_xml_entities_and_references_reject_original_source_processing(self):
  for body in(b'<s:schema>',b'<!DOCTYPE schema [<!ENTITY x SYSTEM "file:///etc/passwd">]><s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:bad"/>'):
   e=fixture();p,g=inputs(e);e['documents'][0]=document('authored.xsd',body)
   with self.assertRaises(XBRLError):audit(e,p,g)
 def test_no_socket_or_uri_fetch_is_used_by_source_reconstruction(self):
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')),patch('socket.socket.bind',side_effect=AssertionError('NO_SERVER')):
   self.assertFalse(audit()['provider_requested'])
