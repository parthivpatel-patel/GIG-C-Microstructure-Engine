"""Authored declarations and filing batches;independent contradiction expectations."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_instance import xml,manifest,NS,parsed
from .xbrl_instance import selected_concepts,selected_financials,XBRLError
from .xbrl_dts import discover
from .xbrl_binding import bind_declarations
from .xbrl_collection import FilingCollection
BASE='https://authored.invalid/'
def declaration(*,period='instant',abstract='false',nillable='false',name='Assets'):
 return ('<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:x="http://www.xbrl.org/2003/instance" targetNamespace="'+NS+'"><s:element id="assets" name="'+name+'" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="'+period+'" abstract="'+abstract+'" nillable="'+nillable+'"/></s:schema>').encode()
def entry(raw=None,document=None,**manifest_patch):
 raw=xml('<g:Assets contextRef="I" unitRef="USD">1000</g:Assets>')if raw is None else raw;document=declaration()if document is None else document
 return {'raw':raw,'manifest':manifest(raw,**manifest_patch),'concepts':selected_concepts(NS),'instance_uri':BASE+'instance.xml','documents':[{'uri':BASE+'authored.xsd','raw':document,'sha256':hashlib.sha256(document).hexdigest()}]}
class Binding(unittest.TestCase):
 def test_exact_source_and_expanded_declaration_bind_into_vintage_export(self):
  e=entry();before=copy.deepcopy(e);collection=FilingCollection('0000320193');r=collection.ingest_dts_batch([e]);self.assertEqual(r['filings'],1);out=collection.at_acceptance_time('2024-02-02T00:00:00Z');self.assertEqual(out['history']['assets'][0]['value'],'1000');proof=out['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration'];self.assertFalse(proof['schema_type_validation']);self.assertFalse(proof['complete_statements']);self.assertEqual(proof['selected_facts'][0]['concept'],'{'+NS+'}Assets');self.assertEqual(proof['documents'][0]['sha256'],e['documents'][0]['sha256']);self.assertIsNone(proof['documents'][0]['received_at']);self.assertEqual(e,before)
 def test_declared_period_abstract_nil_or_missing_concept_are_not_ignored(self):
  bad=[entry(document=declaration(period='duration')),entry(document=declaration(abstract='true')),entry(document=declaration(name='Other')),entry(xml('<g:Assets contextRef="I" unitRef="USD" xsi:nil="true"/>'))]
  for e in bad:
   with self.subTest(document=e['documents'][0]['sha256']),self.assertRaises(XBRLError):FilingCollection('0000320193').ingest_dts_batch([e])
 def test_bad_second_filing_preserves_entire_accepted_collection(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([entry()]);before=c.page()
  good=entry(accession='0000000123-24-000002');bad=entry(document=declaration(period='duration'),accession='0000000123-24-000003')
  with self.assertRaises(XBRLError):c.ingest_dts_batch([good,bad])
  self.assertEqual(c.page(),before)
 def test_graph_and_instance_hash_or_origin_mismatch_are_rejected(self):
  e=entry();p=parsed(e['raw']);g=discover(e['raw'],e['instance_uri'],e['manifest']['source_sha256'],e['documents'])
  for component,key in [(p,'origin'),(g,'instance_sha256')]:
   q=copy.deepcopy(component);q[key]='tampered'
   with self.assertRaises(XBRLError):bind_declarations(q,g)if component is p else bind_declarations(p,q)
  from .xbrl_instance import digest
  changed=copy.deepcopy(g);changed.pop('canonical_sha256');changed['instance_sha256']='0'*64;changed['canonical_sha256']=digest(changed)
  with self.assertRaisesRegex(XBRLError,'source_scope'):bind_declarations(p,changed)
  self.assertEqual(selected_financials(bind_declarations(p,g))['history']['assets'][0]['source_xml_fact_ids'],selected_financials(p)['history']['assets'][0]['source_xml_fact_ids'])
 def test_unknown_concepts_remain_unverified_not_given_financial_mapping(self):
  e=entry(xml('<ext:OpaqueMetric contextRef="I">unverified</ext:OpaqueMetric>'));c=FilingCollection('0000320193');c.ingest_dts_batch([e]);out=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertEqual(out['history']['assets'],[]);proof=out['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration'];self.assertEqual(proof['unverified_facts'],1)
 def test_observed_permission_gate_precedes_any_source_parsing(self):
  e=entry(origin='OBSERVED_OFFICIAL_RESPONSE')
  with patch('terminal.stocks.inline_xbrl.parse_xml',side_effect=AssertionError('NO_UNAUTHORIZED_XML'))as parse:
   with self.assertRaisesRegex(XBRLError,'not_approved'):FilingCollection('0000320193').ingest_dts_batch([e])
   parse.assert_not_called()
 def test_budget_and_original_batch_contract_remain_strict(self):
  c=FilingCollection('0000320193');e=entry()
  with self.assertRaises(XBRLError):c.ingest_batch([e])
  with patch('terminal.stocks.xbrl_collection.MAX_BATCH_BYTES',1),patch('terminal.stocks.xbrl_collection.parse_filing',side_effect=AssertionError('No parsing over budget'))as parser:
   with self.assertRaisesRegex(XBRLError,'byte_budget'):c.ingest_dts_batch([e])
   parser.assert_not_called()
  reduced={k:v for k,v in e.items()if k in('raw','manifest','concepts')};self.assertEqual(c.ingest_batch([reduced])['filings'],1)
 def test_nil_is_admitted_only_when_declared_and_stays_missing(self):
  c=FilingCollection('0000320193');c.ingest_dts_batch([entry(xml('<g:Assets contextRef="I" unitRef="USD" xsi:nil="true"/>'),declaration(nillable='true'))]);out=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertEqual(out['history']['assets'],[])
