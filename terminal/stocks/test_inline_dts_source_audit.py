"""Exact inline originals,acquisition intent and source-processing gates;offline."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_sec_multidoc import fixture
from .test_sec_transform_profile import transformed_fixture
from .test_sec_filing_ingest import PREFIX
from .test_xbrl_instance import manifest,NS
from .test_inline_set import html
from .test_xbrl_binding import declaration
from .inline_set import parse_document_set,TRANSFORMATION_PROFILE
from .xbrl_instance import selected_concepts,digest,XBRLError
from .xbrl_dts import discover_inline_set,EMBEDDED_PROFILE
from .xbrl_binding import bind_declarations
from .xbrl_dts_source_audit import audit_inline_dts_sources


def inputs(*,profile=None,observed=False,count=2):
 data,intent=fixture()if profile is None else transformed_fixture();docs=[]
 if count==1:
  # Keep the continuation in its original primary byte stream for one-source audit.
  primary=data[PREFIX+'primary.htm'];tail='<ix:continuation id="tail">C<i>D</i></ix:continuation>'.encode();primary=primary.replace(b'</body>',tail+b'</body>');data[PREFIX+'primary.htm']=primary;intent['documents']=intent['documents'][:1];intent['documents'][0]['sha256']=hashlib.sha256(primary).hexdigest()
 for i,d in enumerate(intent['documents']):
  name=d['name'];raw=data[PREFIX+name];meta=manifest(raw,source_url=PREFIX+name,received_at=f'2026-11-15T12:00:0{i}Z')
  if observed:meta.update(origin='OBSERVED_OFFICIAL_RESPONSE',permission_reference='authored-private-reference-'+str(i))
  docs.append({'uri':PREFIX+name,'raw':raw,'manifest':meta})
 for i in range(count-len(docs)):
  name=f'part-{i}.xhtml';raw=html('');meta=manifest(raw,source_url=PREFIX+name,received_at='2026-11-15T12:00:10Z')
  if observed:meta.update(origin='OBSERVED_OFFICIAL_RESPONSE',permission_reference='authored-private-extra-'+str(i))
  docs.append({'uri':PREFIX+name,'raw':raw,'manifest':meta});intent['documents'].append({'name':name,'sha256':hashlib.sha256(raw).hexdigest()})
 raw=data[PREFIX+'authored.xsd'];tax=[{'uri':PREFIX+'authored.xsd','raw':raw,'sha256':hashlib.sha256(raw).hexdigest()}];concepts=selected_concepts(NS)
 p=parse_document_set(docs,concepts,allow_observed=observed,transformation_profile=profile);references=[d['manifest']['permission_reference']for d in sorted(docs,key=lambda d:d['uri'])];g=discover_inline_set(p,tax,allow_observed=observed,permission_references=references)
 return p,g,docs,tax,concepts,intent

def audit(bundle=None,*,intent=False,**kw):
 p,g,docs,tax,concepts,m=inputs()if bundle is None else bundle
 if intent:kw.update(acquisition_manifest=m,expected_acquisition_manifest_sha256=digest(m))
 return audit_inline_dts_sources(p,g,docs,tax,concepts=concepts,**kw)

def rehash(value):value['canonical_sha256']=digest({k:v for k,v in value.items()if k!='canonical_sha256'});return value

class InlineOriginalAudit(unittest.TestCase):
 def test_original_text_continuations_raw_hashes_and_receipts_reconstruct_exactly(self):
  b=inputs();before=copy.deepcopy(b);p,g,docs,tax,_,m=b;r=audit(b,intent=True)
  self.assertEqual(r['status'],'VERIFIED_ORIGINAL_SOURCE_RECONSTRUCTION');self.assertEqual(r['parsed_sha256'],p['canonical_sha256']);self.assertEqual(r['dts_sha256'],g['canonical_sha256']);self.assertEqual(r['document_set_sha256'],p['document_set']['sha256']);self.assertEqual(r['source_fact_ids'],[f['source_fact_id']for f in p['facts']]);self.assertEqual(r['acquisition_manifest_sha256'],digest(m));self.assertEqual(r['supplied_document_order'],[d['uri']for d in docs]);self.assertEqual(r['parsed_document_order'],sorted(r['supplied_document_order']));self.assertEqual({d['received_at']for d in r['inline_documents']},{'2026-11-15T12:00:00Z','2026-11-15T12:00:01Z'});self.assertEqual(r['sha256'],digest({k:v for k,v in r.items()if k!='sha256'}));self.assertEqual(b,before);self.assertNotIn('ABCD',str(r));self.assertFalse(r['provider_requested']);self.assertFalse(r['independent_source_authentication'])
 def test_selected_registry_profile_is_explicit_immutable_interpretation(self):
  b=inputs(profile=TRANSFORMATION_PROFILE);r=audit(b,intent=True,transformation_profile=TRANSFORMATION_PROFILE);self.assertEqual(r['transformation_profile'],TRANSFORMATION_PROFILE);self.assertEqual(b[0]['facts'][0]['value'],'123456.70')
  with patch('terminal.stocks.xbrl_dts_source_audit.parse_document_set',side_effect=AssertionError('NO_WRONG_PROFILE_PARSE'))as parser:
   with self.assertRaisesRegex(XBRLError,'profile_scope'):audit(b)
   parser.assert_not_called()
 def test_legacy_profile_and_source_order_are_not_silently_rewritten(self):
  b=inputs();expected=audit(b);b[2].reverse();r=audit(b);self.assertEqual(r['parsed_sha256'],expected['parsed_sha256']);self.assertEqual(r['dts_sha256'],expected['dts_sha256']);self.assertEqual(r['supplied_document_order'],list(reversed(expected['supplied_document_order'])));self.assertIsNone(r['transformation_profile'])
 def test_accepted_acquisition_order_requires_retained_expected_manifest_identity(self):
  b=inputs();m=b[-1]
  with self.assertRaisesRegex(XBRLError,'acquisition_identity'):audit_inline_dts_sources(b[0],b[1],b[2],b[3],concepts=b[4],acquisition_manifest=m)
  reversed_bundle=copy.deepcopy(b);reversed_bundle[2].reverse()
  with self.assertRaisesRegex(XBRLError,'order_or_members'):audit(reversed_bundle,intent=True)
  changed=copy.deepcopy(m);changed['documents'].reverse()
  with self.assertRaisesRegex(XBRLError,'acquisition_identity'):audit_inline_dts_sources(b[0],b[1],list(reversed(b[2])),b[3],concepts=b[4],acquisition_manifest=changed,expected_acquisition_manifest_sha256=digest(m))
 def test_every_permission_is_checked_before_any_original_or_taxonomy_xml(self):
  b=inputs(observed=True)
  with patch('terminal.stocks.xbrl_dts_source_audit.parse_document_set',side_effect=AssertionError('NO_UNAPPROVED_XML'))as parser,patch('terminal.stocks.xbrl_dts_source_audit.discover_inline_set',side_effect=AssertionError('NO_UNAPPROVED_DTS'))as discovery:
   with self.assertRaisesRegex(XBRLError,'not_approved'):audit(b)
   parser.assert_not_called();discovery.assert_not_called()
  b[2][1]['manifest']['permission_reference']=None
  with patch('terminal.stocks.xbrl_dts_source_audit.parse_document_set',side_effect=AssertionError('NO_SECOND_DOCUMENT_PERMISSION'))as parser:
   with self.assertRaisesRegex(XBRLError,'not_approved'):audit(b,allow_observed=True)
   parser.assert_not_called()
 def test_observed_per_document_reference_order_and_privacy_are_preserved(self):
  b=inputs(observed=True);r=audit(b,intent=True,allow_observed=True);self.assertEqual(r['origin'],'OBSERVED_OFFICIAL_RESPONSE');self.assertTrue(all(d['permission_reference_sha256']for d in r['inline_documents']));self.assertNotIn('authored-private-reference',str(r));b[2].reverse();self.assertEqual(audit(b,allow_observed=True)['parsed_sha256'],r['parsed_sha256'])
 def test_processing_reference_or_receipt_change_is_rejected_before_xml(self):
  for kind in('reference','receipt','acceptance'):
   b=inputs(observed=True)
   if kind=='reference':b[2][1]['manifest']['permission_reference']='different-approved-reference'
   elif kind=='receipt':b[2][1]['manifest']['received_at']='2026-11-15T13:00:00Z'
   else:b[2][1]['manifest']['accepted_at']='2024-02-01T12:00:00.000000002Z'
   with patch('terminal.stocks.xbrl_dts_source_audit.parse_document_set',side_effect=AssertionError('NO_MISMATCHED_METADATA_XML'))as parser:
    with self.assertRaisesRegex(XBRLError,'metadata_scope|filing_scope'):audit(b,allow_observed=True)
    parser.assert_not_called()
 def test_raw_original_and_taxonomy_digest_mismatch_rejects_preparse(self):
  for kind in('inline','taxonomy'):
   b=inputs();b[2 if kind=='inline'else 3][0]['raw']+=b' '
   with patch('terminal.stocks.xbrl_dts_source_audit.parse_document_set',side_effect=AssertionError('NO_CORRUPTED_XML'))as parser:
    with self.assertRaisesRegex(XBRLError,'source_digest|document_digest'):audit(b)
    parser.assert_not_called()
 def test_changed_original_bytes_and_updated_manifest_hash_cannot_replace_retained_set(self):
  b=inputs();doc=b[2][0];doc['raw']=doc['raw'].replace(b'>A<b>B',b'>Q<b>B');doc['manifest']['source_sha256']=hashlib.sha256(doc['raw']).hexdigest()
  with self.assertRaisesRegex(XBRLError,'metadata_scope'):audit(b)
 def test_rehashed_fact_context_unit_and_transform_traces_cannot_replace_original_parse(self):
  for kind in('value','context','unit','trace','segments'):
   b=inputs();p=b[0]
   if kind=='value':p['facts'][0]['value']='999999'
   elif kind=='context':p['contexts']['D']['period']['start']='2022-01-01'
   elif kind=='unit':p['units']['USD']['numerator']=['{urn:invented}USD']
   elif kind=='trace':p['document_set']['facts'][1]['transformed_lexical']='invented narrative'
   else:p['facts'][1]['inline_source_segments'].reverse()
   rehash(p)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'original_parsed_mismatch'):audit(b)
 def test_rehashed_graph_concepts_types_and_source_hashes_must_reconstruct(self):
  for kind in('concept','type','original','reference'):
   b=inputs();g=b[1]
   if kind=='concept':next(iter(g['concepts'].values()))['declaration']['abstract']=True
   elif kind=='type':g['type_declarations']={'{urn:invented}Amount':{'declaration':{'base':None,'facets':[],'unsupported':[]},'source_documents':[]}}
   elif kind=='original':g['original_inline_documents'][0]['source_sha256']='0'*64
   else:g['schema_roots']=[]
   rehash(g)
   with self.subTest(kind=kind),self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(b)
 def test_missing_and_unreferenced_taxonomy_bodies_never_claim_exact_closure(self):
  b=inputs();b[3].clear()
  with self.assertRaisesRegex(XBRLError,'taxonomy_document_budget'):audit(b)
  b=inputs();b[3].append({'uri':PREFIX+'unused.xsd','raw':declaration(),'sha256':hashlib.sha256(declaration()).hexdigest()})
  with self.assertRaisesRegex(XBRLError,'document_coverage'):audit(b)
  b=inputs();b[3][0]['uri']=PREFIX+'wrong.xsd'
  with self.assertRaisesRegex(XBRLError,'closure_required'):audit(b)
 def test_duplicate_original_and_taxonomy_uris_or_role_overlap_reject(self):
  b=inputs();b[2].append(copy.deepcopy(b[2][0]))
  with self.assertRaisesRegex(XBRLError,'duplicate_original_uri'):audit(b)
  b=inputs();b[3].append(copy.deepcopy(b[3][0]))
  with self.assertRaisesRegex(XBRLError,'duplicate_taxonomy_uri'):audit(b)
  b=inputs();b[3][0]['uri']=b[2][0]['uri']
  with self.assertRaisesRegex(XBRLError,'taxonomy_overlap'):audit(b)
 def test_foreign_filing_primary_uri_and_acquisition_hash_mismatch_reject(self):
  b=inputs();b[2][1]['manifest']['accession']='0000000123-24-000002';b[2][1]['manifest']['source_url']=b[2][1]['uri'].replace('000000012324000001','000000012324000002')
  with self.assertRaisesRegex(XBRLError,'original_uri_scope'):audit(b)
  b=inputs();b[-1]['documents'][1]['sha256']='0'*64
  with self.assertRaisesRegex(XBRLError,'source_binding'):audit(b,intent=True)
  b=inputs()
  with self.assertRaisesRegex(XBRLError,'manifest_required'):audit_inline_dts_sources(b[0],b[1],b[2],b[3],concepts=b[4],expected_acquisition_manifest_sha256=digest(b[-1]))
 def test_concept_profile_is_supplied_not_inferred_from_retained_numeric_values(self):
  b=inputs()
  with self.assertRaisesRegex(XBRLError,'original_parsed_mismatch'):audit_inline_dts_sources(b[0],b[1],b[2],b[3],concepts={})
 def test_bound_derived_or_plain_artifact_cannot_replace_original_set(self):
  b=inputs();bound=bind_declarations(b[0],b[1])
  with self.assertRaisesRegex(XBRLError,'original_parsed_mismatch'):audit_inline_dts_sources(bound,b[1],b[2],b[3],concepts=b[4])
  b=inputs();b[0]['schema']='gig.sec.xbrl.instance.v1';rehash(b[0])
  with self.assertRaisesRegex(XBRLError,'original_set_artifact_required'):audit(b)
 def test_one_and_eight_originals_keep_source_budgets_and_identity(self):
  for count in(1,8):
   b=inputs(count=count);r=audit(b,intent=True);self.assertEqual(len(r['inline_documents']),count);self.assertEqual(r['source_fact_ids'],[f['source_fact_id']for f in b[0]['facts']])
  b=inputs();b[2].extend(copy.deepcopy(b[2])*4)
  with self.assertRaisesRegex(XBRLError,'document_budget'):audit(b)
 def test_artifact_and_original_byte_output_limits_reject_without_truncation(self):
  b=inputs()
  for key,code in(('MAX_INSTANCE','original_contract'),('MAX_INPUT','input_budget'),('MAX_PARSED','artifact_budget'),('MAX_GRAPH','artifact_budget'),('MAX_OUTPUT','output_budget')):
   with patch('terminal.stocks.xbrl_dts_source_audit.'+key,1),self.subTest(key=key),self.assertRaisesRegex(XBRLError,code):audit(b)
 def test_selectors_and_stale_manifest_identity_are_rejected_preparse(self):
  b=inputs()
  for opts,code in[({'transformation_profile':'future'},'transformation_profile'),({'embedded_profile':'future'},'embedded_profile'),({'acquisition_manifest':b[-1],'expected_acquisition_manifest_sha256':'0'*64},'acquisition_identity')]:
   with patch('terminal.stocks.xbrl_dts_source_audit.parse_document_set',side_effect=AssertionError('NO_BAD_SELECTOR_XML'))as parser:
    with self.assertRaisesRegex(XBRLError,code):audit_inline_dts_sources(b[0],b[1],b[2],b[3],concepts=b[4],**opts)
    parser.assert_not_called()
 def test_no_socket_or_server_is_used_and_no_raw_source_text_is_exported(self):
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')),patch('socket.socket.bind',side_effect=AssertionError('NO_SERVER')):
   r=audit();self.assertFalse(r['provider_requested']);self.assertFalse(r['independent_source_authentication']);self.assertNotIn('raw',r);self.assertNotIn('facts',r)
 def test_coherent_forged_metadata_does_not_hide_invalid_original_continuations_or_xml(self):
  from .xbrl_instance import validate_manifest
  for wire in(html(''),html('<ix:continuation id="tail" continuedAt="tail">C</ix:continuation>'),html('<ix:continuation id="tail">C</ix:continuation><div id="tail"/>'),b'<!DOCTYPE html [<!ENTITY secret SYSTEM "file:///etc/passwd">]><html/>'):
   b=inputs();p,g,docs,*_=b;doc=docs[1];doc['raw']=wire;doc['manifest']['source_sha256']=hashlib.sha256(wire).hexdigest();sources=copy.deepcopy(p['document_set']['documents'])
   next(d for d in sources if d['uri']==doc['uri'])['source']=validate_manifest(wire,doc['manifest'],False);p['document_set']['documents']=sources;p['document_set']['sha256']=digest(sources);p['source']['source_sha256']=digest(sources);rehash(p)
   g['document_set_sha256']=digest(sources);g['original_inline_documents']=[{'uri':d['uri'],'source_sha256':d['source']['source_sha256']}for d in sources];rehash(g)
   with self.assertRaises(XBRLError):audit(b)
 def test_embedded_graph_profile_is_explicit_and_unsupported_diagnostics_are_preserved(self):
  from .test_xbrl_embedded import embedded
  e=embedded();b=inputs();p,_,docs,_,concepts,m=b;tax=[{'uri':PREFIX+d['uri'].rsplit('/',1)[-1],'raw':d['raw'],'sha256':d['sha256']}for d in e['documents']];g=discover_inline_set(p,tax,embedded_profile=EMBEDDED_PROFILE);bundle=(p,g,docs,tax,concepts,m);self.assertEqual(audit(bundle,embedded_profile=EMBEDDED_PROFILE)['embedded_profile'],EMBEDDED_PROFILE)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(bundle)
  legacy=discover_inline_set(p,tax);self.assertTrue(legacy['unsupported_semantics']);bundle=(p,legacy,docs,tax,concepts,m);audit(bundle);legacy['unsupported_semantics']=[];rehash(legacy)
  with self.assertRaisesRegex(XBRLError,'reconstructed_graph_mismatch'):audit(bundle)
