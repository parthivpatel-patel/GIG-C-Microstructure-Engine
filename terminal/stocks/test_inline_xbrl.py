"""Authored XHTML only;independent exact numeric and provenance expectations."""
import hashlib,unittest
from .test_xbrl_instance import xml,manifest,NS
from .xbrl_instance import parse_instance,selected_financials,selected_concepts,XBRLError
from .inline_xbrl import parse_inline
from .xbrl_collection import FilingCollection

def html(fact=None):
 source=xml().decode();start=source.index('<x:context');end=source.index('<g:Revenues');resources=source[start:end]
 fact=fact or'<ix:nonFraction name="g:Revenues" contextRef="D" unitRef="USD" decimals="INF" scale="3" sign="-" id="reported">123.4500</ix:nonFraction>'
 return ('<html xmlns="http://www.w3.org/1999/xhtml" xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:x="http://www.xbrl.org/2003/instance" xmlns:g="'+NS+'" xmlns:iso="http://www.xbrl.org/2003/iso4217" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><head/><body><ix:header><ix:resources>'+resources+'</ix:resources></ix:header>'+fact+'</body></html>').encode()
class InlineXBRL(unittest.TestCase):
 def test_observed_permission_fails_before_xml_processing(self):
  from unittest.mock import patch
  from .inline_xbrl import parse_filing
  raw=html();m=manifest(raw,origin='OBSERVED_OFFICIAL_RESPONSE')
  for parser in(parse_inline,parse_filing):
   with patch('terminal.stocks.inline_xbrl.parse_xml',side_effect=AssertionError('must not inspect unauthorized XML'))as xml_parser:
    with self.assertRaisesRegex(XBRLError,'not_approved'):parser(raw,m,selected_concepts(NS))
    xml_parser.assert_not_called()
 def parse(self,raw):return parse_inline(raw,manifest(raw),selected_concepts(NS))
 def test_exact_scale_sign_units_source_context_and_original_receipt(self):
  raw=html();p=self.parse(raw);r=selected_financials(p)['history']['revenue'][0];self.assertEqual(r['value'],'-123450.0');self.assertEqual(p['inline_profile']['facts'][0]['original_lexical'],'123.4500');self.assertEqual(p['source']['source_sha256'],hashlib.sha256(raw).hexdigest());self.assertIsNone(p['source']['received_at']);self.assertEqual(r['source_xbrl_concept'],'{'+NS+'}Revenues')
 def test_small_decimal_scale_does_not_depend_on_decimal_precision(self):
  from decimal import localcontext
  with localcontext()as c:
   c.prec=2;p=self.parse(html('<ix:nonFraction name="g:Revenues" contextRef="D" unitRef="USD" scale="-6">123456789.123456789</ix:nonFraction>'))
  self.assertEqual(p['facts'][0]['value'],'123.456789123456789')
 def test_nil_remains_missing_and_nonnumeric_unknown_remains_unselected(self):
  p=self.parse(html('<ix:nonFraction name="g:Revenues" contextRef="D" unitRef="USD" xsi:nil="true"/><ix:nonNumeric name="g:AuthoredText" contextRef="D">Unavailable</ix:nonNumeric>'));self.assertEqual(selected_financials(p)['history']['revenue'],[]);self.assertEqual(p['facts'][1]['lexical_value'],'Unavailable')
 def test_transforms_continuations_nested_markup_tuples_and_named_targets_reject(self):
  base='<ix:nonFraction name="g:Revenues" contextRef="D" unitRef="USD"{}>1</ix:nonFraction>'
  cases=[html(base.format(' format="g:unreviewed"')),html(base.format(' continuedAt="later"')),html(base.format(' target="other"')),html(base.format(' tupleRef="tuple"')),html(base.format('')).replace(b'>1</ix:',b'><span>1</span></ix:'),html().replace(b'<ix:nonFraction',b'<ix:fraction').replace(b'</ix:nonFraction',b'</ix:fraction')]
  for raw in cases:
   with self.subTest(length=len(raw)),self.assertRaises(XBRLError):self.parse(raw)
 def test_source_hash_duplicate_ids_unsafe_entities_and_invalid_scale_reject(self):
  cases=[html().replace(b'scale="3"',b'scale="999"'),html().replace(b'contextRef="D"',b'contextRef="missing"'),html().replace(b'123.4500',b'1,234'),html().replace(b'<html',b'<!DOCTYPE html [<!ENTITY a SYSTEM "file:///etc/passwd">]><html',1)]
  for raw in cases:
   with self.assertRaises(ValueError):self.parse(raw)
  raw=html()
  with self.assertRaises(XBRLError):parse_inline(raw,manifest(raw,source_sha256='0'*64),selected_concepts(NS))
  from unittest.mock import patch
  with patch('terminal.stocks.inline_xbrl.MAX_FACTS',0),self.assertRaisesRegex(XBRLError,'inline_fact_budget'):self.parse(raw)
  with patch('terminal.stocks.inline_xbrl.MAX_OUTPUT_BYTES',1),self.assertRaisesRegex(XBRLError,'inline_output_budget'):self.parse(raw)
 def test_atomic_collection_accepts_inline_without_changing_strict_instance_api(self):
  raw=html();c=FilingCollection('0000320193');receipt=c.ingest_batch([{'raw':raw,'manifest':manifest(raw),'concepts':selected_concepts(NS)}]);self.assertEqual(receipt['filings'],1);value=c.at_acceptance_time('2024-02-10T00:00:00Z');self.assertEqual(value['history']['revenue'][0]['value'],'-123450.0')
  with self.assertRaises(XBRLError):parse_instance(raw,manifest(raw),selected_concepts(NS))
  self.assertEqual(self.parse(raw),self.parse(raw))
