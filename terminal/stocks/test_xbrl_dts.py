"""Authored taxonomy graphs and independent presentation expectations;no requests."""
import copy,hashlib,unittest
from unittest.mock import patch
from .test_xbrl_instance import xml
from .xbrl_dts import discover,XBRLError
BASE='https://authored.invalid/';NS='https://authored.invalid/gaap';ROLE='https://authored.invalid/role/balance'

def schema(extra=''):
 return ('<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" xmlns:x="http://www.xbrl.org/2003/instance" xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink" targetNamespace="'+NS+'"><s:element id="assets" name="Assets" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="instant" x:balance="debit"/><s:element id="cash" name="Cash" type="x:monetaryItemType" substitutionGroup="x:item" x:periodType="instant"/><s:annotation><s:appinfo><l:linkbaseRef xl:type="simple" xl:href="presentation.xml"/></s:appinfo></s:annotation>'+extra+'</s:schema>').encode()
def presentation(*,order='1.10',extra='',attrs=''):
 return ('<l:linkbase xmlns:l="http://www.xbrl.org/2003/linkbase" xmlns:xl="http://www.w3.org/1999/xlink"><l:presentationLink xl:type="extended" xl:role="'+ROLE+'"><l:loc xl:type="locator" xl:label="a" xl:href="authored.xsd#assets"/><l:loc xl:type="locator" xl:label="c" xl:href="authored.xsd#cash"/><l:presentationArc xl:type="arc" xl:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xl:from="a" xl:to="c" order="'+order+'" '+attrs+'/>'+extra+'</l:presentationLink></l:linkbase>').encode()
def document(name,raw):return {'uri':BASE+name,'raw':raw,'sha256':hashlib.sha256(raw).hexdigest()}
def evaluate(docs=None,**kwargs):
 raw=xml();docs=docs if docs is not None else[document('authored.xsd',schema()),document('presentation.xml',presentation())]
 return discover(raw,BASE+'instance.xml',hashlib.sha256(raw).hexdigest(),docs,**kwargs)
class DTS(unittest.TestCase):
 def test_structural_closure_retains_exact_concepts_roles_order_and_provenance(self):
  x=evaluate();self.assertTrue(x['structural_closure']);self.assertFalse(x['schema_type_validation']);self.assertFalse(x['complete_statements']);self.assertEqual(x['schema_roots'],[BASE+'authored.xsd']);self.assertEqual(x['presentation'][0]['roots'],['{'+NS+'}Assets']);self.assertEqual(x['presentation'][0]['arcs'][0]['order'],'1.10');self.assertIsNone(x['documents'][0]['received_at']);self.assertFalse(x['provider_requested'])
 def test_unprovided_references_are_explicit_without_fetch_or_guessed_types(self):
  with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):x=evaluate([])
  self.assertFalse(x['structural_closure']);self.assertEqual(x['unresolved'][0]['uri'],BASE+'authored.xsd');self.assertEqual(x['concepts'],{})
 def test_supplied_import_namespace_conflict_and_duplicate_schema_ids_reject(self):
  imported=b'<s:schema xmlns:s="http://www.w3.org/2001/XMLSchema" targetNamespace="https://wrong.invalid"/>'
  for docs in [[document('authored.xsd',schema('<s:import namespace="https://expected.invalid" schemaLocation="import.xsd"/>')),document('import.xsd',imported)],[document('authored.xsd',schema('<s:element id="assets" name="Other"/>'))]]:
   with self.assertRaises(XBRLError):evaluate(docs)
  with self.assertRaises(XBRLError):evaluate([document('authored.xsd',schema('<s:import namespace="https://expected.invalid" schemaLocation="import.xsd"/>')),document('import.xsd',presentation())])
 def test_digest_and_conflicting_supplied_content_do_not_publish_partial_graph(self):
  doc=document('authored.xsd',schema());wrong={**doc,'sha256':'0'*64}
  with self.assertRaisesRegex(XBRLError,'digest'):evaluate([wrong])
  with self.assertRaisesRegex(XBRLError,'conflict'):evaluate([doc,document('authored.xsd',schema('<s:element name="Extra"/>'))])
 def test_unresolved_locator_and_unsupported_prohibition_are_not_renderable(self):
  for raw in[presentation().replace(b'#cash',b'#missing'),presentation(attrs='use="prohibited"'),presentation(attrs='priority="1"')]:
   x=evaluate([document('authored.xsd',schema()),document('presentation.xml',raw)]);self.assertFalse(x['presentation'][0]['usable']);self.assertTrue(x['presentation'][0]['issues'])
 def test_presentation_cycle_is_reported_without_recursive_traversal(self):
  reverse='<l:presentationArc xl:type="arc" xl:arcrole="http://www.xbrl.org/2003/arcrole/parent-child" xl:from="c" xl:to="a"/>'
  x=evaluate([document('authored.xsd',schema()),document('presentation.xml',presentation(extra=reverse))]);self.assertFalse(x['presentation'][0]['usable']);self.assertIn('DIRECTED_PRESENTATION_CYCLE',x['presentation'][0]['issues'])
 def test_external_entities_xml_base_bad_uri_and_large_bundles_fail_closed(self):
  for raw in[schema().replace(b'<s:schema',b'<!DOCTYPE schema [<!ENTITY x SYSTEM "file:///etc/passwd">]><s:schema',1),schema().replace(b'targetNamespace=',b'xml:base="https://other.invalid/" targetNamespace=',1)]:
   with self.assertRaises(XBRLError):evaluate([document('authored.xsd',raw)])
  with self.assertRaises(XBRLError):evaluate([document('authored.xsd',schema())]*17)
  raw=xml()
  with self.assertRaises(ValueError):discover(raw,'file:///tmp/instance.xml',hashlib.sha256(raw).hexdigest(),[])
 def test_custom_types_remain_unvalidated_and_input_order_does_not_change_result(self):
  docs=[document('authored.xsd',schema('<s:complexType name="ExtensionType"/>')),document('presentation.xml',presentation())];before=copy.deepcopy(docs);x=evaluate(docs);self.assertTrue(x['unsupported_semantics']);self.assertEqual(x,evaluate(list(reversed(docs))));self.assertEqual(docs,before)
  first=presentation();link=first[first.index(b'<l:presentationLink'):first.index(b'</l:presentationLink>')+len(b'</l:presentationLink>')];both=first.replace(b'</l:linkbase>',link+b'</l:linkbase>');x=evaluate([document('authored.xsd',schema()),document('presentation.xml',both)]);self.assertEqual(len(x['presentation']),2);self.assertTrue(all(not n['usable']for n in x['presentation']))
 def test_observed_permission_fails_before_any_xml_processing(self):
  with patch('terminal.stocks.xbrl_dts.parse_xml',side_effect=AssertionError('NO_UNAUTHORIZED_PROCESSING'))as parser:
   with self.assertRaisesRegex(XBRLError,'not_approved'):evaluate(origin='OBSERVED_OFFICIAL_RESPONSE')
   parser.assert_not_called()
