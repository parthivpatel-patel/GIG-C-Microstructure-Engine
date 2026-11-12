"""Independent authored document-set/text/numeric/provenance expectations."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_instance import xml,manifest,NS
from .inline_set import parse_document_set,TRANSFORMS
from .xbrl_instance import selected_concepts,selected_financials,XBRLError
from .xbrl_collection import FilingCollection
from .test_xbrl_binding import declaration
BASE='https://authored.invalid/'
def html(facts,*,resources=False,reference=True):
 source=xml().decode();start=source.index('<x:context');end=source.index('<g:Revenues');res=source[start:end]if resources else''
 refs='<ix:references><l:schemaRef xl:type="simple" xl:href="authored.xsd"/></ix:references>'if resources and reference else''
 header='<ix:header>'+refs+('<ix:resources>'+res+'</ix:resources>'if resources else'')+'</ix:header>'
 return ('<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:x="http://www.xbrl.org/2003/instance" xmlns:g="'+NS+'" xmlns:iso="http://www.xbrl.org/2003/iso4217" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" xmlns:ixt="'+TRANSFORMS+'"><body>'+header+facts+'</body></html>').encode()
def doc(name,raw,**metadata):return {'uri':BASE+name,'raw':raw,'manifest':manifest(raw,**metadata)}
def numeric(text='1,234.50',*,format='ixt:numdotdecimal',attrs=''):
 return '<ix:nonFraction name="g:Revenues" contextRef="D" unitRef="USD" decimals="2"'+(' format="'+format+'"'if format else'')+attrs+'>'+text+'</ix:nonFraction>'
def documents():
 return [doc('a.xhtml',html(numeric('<span>1,234</span>.50')+'<ix:nonNumeric name="g:AuthoredText" contextRef="D" continuedAt="tail" id="narrative">A<b>B</b><ix:exclude>excluded</ix:exclude>C</ix:nonNumeric>',resources=True)),doc('b.xhtml',html('<ix:continuation id="tail">D<span>E</span></ix:continuation>'))]
def parse(docs=None):return parse_document_set(documents()if docs is None else docs,selected_concepts(NS))
def batch(docs=None):
 raw=declaration(period='duration',name='Revenues');return {'documents':documents()if docs is None else docs,'concepts':selected_concepts(NS),'taxonomy_documents':[{'uri':BASE+'authored.xsd','raw':raw,'sha256':hashlib.sha256(raw).hexdigest()}]}
class InlineSet(unittest.TestCase):
 def test_cross_document_chain_markup_exclusion_and_raw_provenance(self):
  docs=documents();before=copy.deepcopy(docs);p=parse(docs);self.assertEqual(p['schema'],'gig.sec.xbrl.inline_set.v1');self.assertEqual(p['facts'][0]['value'],'1234.50');self.assertEqual(p['facts'][1]['lexical_value'],'ABCDE');self.assertEqual(len(p['facts'][1]['inline_source_segments']),2);self.assertEqual(p['document_set']['documents'][0]['source']['source_sha256'],hashlib.sha256(docs[0]['raw']).hexdigest());self.assertIsNone(p['source']['received_at']);self.assertEqual(p['source']['source_hash_kind'],'DERIVED_DOCUMENT_SET_MANIFEST_V1');self.assertEqual(docs,before)
 def test_ordered_text_does_not_move_child_text_to_the_end(self):
  p=parse([doc('a.xhtml',html(numeric('<b>1</b>2<i>3</i>.40'),resources=True))]);self.assertEqual(p['facts'][0]['value'],'123.40')
 def test_supported_transforms_scale_sign_and_decimal_precision(self):
  from decimal import localcontext
  for text,format,expected in [('1,234.50','ixt:numdotdecimal','-1234500'),('1.234,50','ixt:numcommadecimal','-1234500')]:
   with localcontext()as c:
    c.prec=2;p=parse([doc('a.xhtml',html(numeric(text,format=format,attrs=' scale="3" sign="-"'),resources=True))]);self.assertEqual(p['facts'][0]['value'],expected)
 def test_unknown_transform_bad_grouping_and_numeric_exclude_reject(self):
  for fact in(numeric('1,23.4'),numeric('1',format='g:unknown'),numeric('<ix:exclude>1</ix:exclude>2'),numeric('1',attrs=' continuedAt="tail"')):
   with self.assertRaises(XBRLError):parse([doc('a.xhtml',html(fact,resources=True))])
 def test_missing_wrong_kind_cycle_reuse_and_orphan_continuations_reject(self):
  root='<ix:nonNumeric name="g:AuthoredText" contextRef="D" continuedAt="tail">A</ix:nonNumeric>'
  for suffix in('', '<div id="tail">B</div>','<ix:continuation id="tail" continuedAt="tail">B</ix:continuation>','<ix:continuation id="tail">B</ix:continuation>'+root,'<ix:continuation id="orphan">B</ix:continuation>'):
   with self.subTest(suffix=suffix[:30]),self.assertRaises(XBRLError):parse([doc('a.xhtml',html(root+suffix,resources=True))])
 def test_shared_resources_and_financial_attribution_are_exact(self):
  p=parse([doc('a.xhtml',html('',resources=True)),doc('b.xhtml',html(numeric()))]);f=selected_financials(p);row=f['history']['revenue'][0];self.assertEqual(row['value'],'1234.50');self.assertEqual(row['source_document_sha256s'],sorted(d['manifest']['source_sha256']for d in [doc('a.xhtml',html('',resources=True)),doc('b.xhtml',html(numeric()))]));self.assertIsNone(row['source_instance_sha256']);self.assertEqual(row['source_document_set_sha256'],p['document_set']['sha256']);self.assertTrue(row['source_xml_fact_ids'])
 def test_input_order_is_not_a_filing_chronology_and_output_is_deterministic(self):
  docs=documents();self.assertEqual(parse(docs),parse(list(reversed(docs))))
 def test_document_hash_scope_identity_and_duplicate_ids_reject(self):
  for kind in('hash','issuer','accession','duplicate_uri','duplicate_id'):
   docs=documents()
   if kind=='hash':docs[1]['manifest']['source_sha256']='0'*64
   elif kind=='issuer':docs[1]['manifest']['issuer_cik']='0000000001'
   elif kind=='accession':docs[1]['manifest']['accession']='0000000123-24-000002'
   elif kind=='duplicate_uri':docs[1]['uri']=docs[0]['uri']
   else:docs[1]=doc('b.xhtml',html('<div id="narrative"/>'))
   with self.subTest(kind=kind),self.assertRaises(ValueError):parse(docs)
 def test_permission_for_every_document_precedes_any_xml(self):
  docs=documents();docs[1]['manifest']['origin']='OBSERVED_OFFICIAL_RESPONSE'
  with patch('terminal.stocks.inline_set.parse_xml',side_effect=AssertionError('NO_UNAUTHORIZED_XML'))as parser:
   with self.assertRaisesRegex(XBRLError,'not_approved'):parse(docs)
   parser.assert_not_called()
 def test_nested_facts_active_markup_named_targets_and_escape_are_explicitly_unsupported(self):
  for fact in(numeric('<ix:nonFraction name="g:Revenues" contextRef="D" unitRef="USD">1</ix:nonFraction>'),numeric('<script>1</script>'),numeric('1',attrs=' target="other"'),'<ix:nonNumeric name="g:AuthoredText" contextRef="D" escape="true"><b>text</b></ix:nonNumeric>'):
   with self.assertRaises(XBRLError):parse([doc('a.xhtml',html(fact,resources=True))])
 def test_nil_and_fact_kind_conflicts_never_become_zero_or_numeric_facts(self):
  p=parse([doc('a.xhtml',html(numeric('',format='',attrs=' xsi:nil="true"'),resources=True))]);self.assertTrue(p['facts'][0]['nil']);self.assertFalse(selected_financials(p)['history']['revenue'])
  for fact in('<ix:nonNumeric name="g:Revenues" contextRef="D">100</ix:nonNumeric>',numeric().replace(' unitRef="USD"','')):
   with self.assertRaises(XBRLError):parse([doc('a.xhtml',html(fact,resources=True))])
 def test_document_node_value_chain_and_output_limits_fail_closed(self):
  with self.assertRaises(XBRLError):parse(documents()*5)
  for target,value,code in [('MAX_SET_BYTES',1,'byte_budget'),('MAX_NODES',1,'node_budget'),('MAX_VALUE',2,'value_budget'),('MAX_CHAIN',0,'chain_budget'),('MAX_OUTPUT',1,'trace_budget')]:
   with patch('terminal.stocks.inline_set.'+target,value),self.subTest(target=target),self.assertRaisesRegex(XBRLError,code):parse()
 def test_batch_dts_numeric_and_vintage_selection_work_without_network(self):
  from .xbrl_types import PROFILE
  c=FilingCollection('0000320193')
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):r=c.ingest_inline_set_batch([batch()],numeric_profile=PROFILE)
  self.assertEqual(r['filings'],1);view=c.at_acceptance_time('2024-02-02T00:00:00Z');self.assertEqual(view['history']['revenue'][0]['value'],'1234.50');proof=view['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration'];self.assertFalse(proof['schema_type_validation']);self.assertEqual(proof['numeric_value_validation']['facts'][0]['value_validation'],'VALIDATED_BOUNDED_NUMERIC_PROFILE')
 def test_invalid_later_filing_does_not_publish_partial_batch(self):
  c=FilingCollection('0000320193');first=batch();c.ingest_inline_set_batch([first]);before=c.page();bad=batch();bad['documents'][0]['raw']=b'<malformed'
  with self.assertRaises(ValueError):c.ingest_inline_set_batch([batch(),bad])
  self.assertEqual(c.page(),before)
 def test_amendment_vintage_uses_acceptance_not_collection_order(self):
  c=FilingCollection('0000320193');old=batch();new=batch()
  for document in new['documents']:document['manifest'].update(accession='0000000123-24-000002',form='10-K/A',filed='2024-02-10',accepted_at='2024-02-10T12:00:00Z',amends_accession='0000000123-24-000001')
  new['documents'][0]['raw']=new['documents'][0]['raw'].replace(b'1,234',b'2,234');new['documents'][0]['manifest']['source_sha256']=hashlib.sha256(new['documents'][0]['raw']).hexdigest();c.ingest_inline_set_batch([new,old]);self.assertEqual(c.at_acceptance_time('2024-02-02T00:00:00Z')['history']['revenue'][0]['value'],'1234.50');self.assertEqual(c.at_acceptance_time('2024-02-10T12:00:00Z')['history']['revenue'][0]['value'],'2234.50')
 def test_large_scale_is_explicit_bounded_and_independent_of_legacy_plain_profile(self):
  p=parse([doc('a.xhtml',html(numeric('1.25',format='',attrs=' scale="9"'),resources=True))]);self.assertEqual(p['facts'][0]['value'],'1250000000')
  with self.assertRaises(XBRLError):parse([doc('a.xhtml',html(numeric('1',format='',attrs=' scale="19"'),resources=True))])
 def test_dts_graph_cannot_bind_another_document_set_or_bypass_observed_gate(self):
  from .xbrl_dts import discover_inline_set
  from .xbrl_binding import bind_declarations
  from .xbrl_instance import digest
  p=parse();graph=discover_inline_set(p,batch()['taxonomy_documents']);bad=copy.deepcopy(graph);bad.pop('canonical_sha256');bad['document_set_sha256']='0'*64;bad['canonical_sha256']=digest(bad)
  with self.assertRaisesRegex(XBRLError,'source_scope'):bind_declarations(p,bad)
  q=copy.deepcopy(p);q.pop('canonical_sha256');q['origin']='OBSERVED_OFFICIAL_RESPONSE';q['source']['origin']=q['origin'];q['canonical_sha256']=digest(q)
  with patch('terminal.stocks.xbrl_dts._supplied_documents',side_effect=AssertionError('NO_UNAUTHORIZED_TAXONOMY'))as parser:
   with self.assertRaisesRegex(XBRLError,'not_approved'):discover_inline_set(q,batch()['taxonomy_documents'])
   parser.assert_not_called()
 def test_conflicting_values_keep_actual_source_fact_identifiers(self):
  p=parse([doc('a.xhtml',html(numeric('100')+numeric('101'),resources=True))]);self.assertEqual(set(p['conflicts'][0]['source_fact_ids']),{r['source_fact_id']for r in p['facts']});self.assertFalse(selected_financials(p)['history']['revenue'])
 def test_continuation_limit_applies_to_actual_chain_length(self):
  def chain(count):return '<ix:nonNumeric name="g:AuthoredText" contextRef="D" continuedAt="c0">A</ix:nonNumeric>'+''.join('<ix:continuation id="c'+str(i)+'"'+(' continuedAt="c'+str(i+1)+'"'if i+1<count else'')+'>B</ix:continuation>'for i in range(count))
  self.assertEqual(len(parse([doc('a.xhtml',html(chain(32),resources=True))])['facts'][0]['lexical_value']),33)
  with self.assertRaisesRegex(XBRLError,'chain_budget'):parse([doc('a.xhtml',html(chain(33),resources=True))])
 def test_numeric_profile_requires_explicit_dts_and_preflights_total_bytes(self):
  from .xbrl_types import PROFILE
  e=batch();e['taxonomy_documents']=None;c=FilingCollection('0000320193')
  with self.assertRaisesRegex(XBRLError,'requires_dts'):c.ingest_inline_set_batch([e],numeric_profile=PROFILE)
  with patch('terminal.stocks.xbrl_collection.MAX_BATCH_BYTES',1),patch('terminal.stocks.inline_set.parse_document_set',side_effect=AssertionError('NO_OVER_BUDGET_PARSING'))as parser:
   with self.assertRaisesRegex(XBRLError,'byte_budget'):c.ingest_inline_set_batch([batch()])
   parser.assert_not_called()
 def test_inline_set_accepts_explicit_simple_content_v2_without_promoting_schema_validity(self):
  from .xbrl_types import PROFILE,COMPLEX_PROFILE
  e=batch();document=e['taxonomy_documents'][0];raw=document['raw'].replace(b'<s:schema',('<s:schema xmlns:t="'+NS+'"').encode(),1).replace(b'type="x:monetaryItemType"',b'type="t:RevenueAmount"').replace(b'</s:schema>',b'<s:complexType name="RevenueAmount"><s:simpleContent><s:extension base="x:monetaryItemType"/></s:simpleContent></s:complexType></s:schema>');document.update(raw=raw,sha256=hashlib.sha256(raw).hexdigest())
  c=FilingCollection('0000320193')
  with self.assertRaisesRegex(XBRLError,'type_profile_unsupported'):c.ingest_inline_set_batch([e],numeric_profile=PROFILE)
  self.assertEqual(c.page()['total'],0);c.ingest_inline_set_batch([e],numeric_profile=COMPLEX_PROFILE);view=c.at_acceptance_time('2024-02-02T00:00:00Z');proof=view['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration'];self.assertFalse(proof['schema_type_validation']);self.assertEqual(proof['numeric_value_validation']['profile'],COMPLEX_PROFILE)
