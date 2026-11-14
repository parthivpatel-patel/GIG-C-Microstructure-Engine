"""Authored Registry3 numeric expectations; no provider or conformance-corpus claim."""
import unittest
from decimal import localcontext
from unittest.mock import patch
from .test_inline_set import doc,html,numeric
from .test_xbrl_instance import NS
from .inline_set import parse_document_set,TRANSFORMATION_PROFILE,ZERO_DASHES
from .xbrl_instance import selected_concepts,XBRLError
from .xbrl_collection import FilingCollection

def parse(text,format='ixt:numdotdecimal',attrs='',profile=TRANSFORMATION_PROFILE):
 return parse_document_set([doc('a.xhtml',html(numeric(text,format=format,attrs=attrs),resources=True))],selected_concepts(NS),transformation_profile=profile)

class RegistryNumeric(unittest.TestCase):
 def test_xml_collapse_and_space_nbsp_grouping_preserve_exact_output(self):
  for lexical,format in [(' 1\t234.50\n','ixt:numdotdecimal'),('1\u00a0234.50','ixt:numdotdecimal'),('1\t234,50','ixt:numcommadecimal'),('1\u00a0234,50','ixt:numcommadecimal')]:
   p=parse(lexical,format);self.assertEqual(p['facts'][0]['value'],'1234.50');self.assertEqual(p['document_set']['transformation_profile'],TRANSFORMATION_PROFILE)
 def test_indian_grouping_and_scale_are_exact_under_low_decimal_precision(self):
  with localcontext()as c:
   c.prec=2
   for lexical in('1,23,45,678.90','1 23 45 678.90','1\u00a023\u00a045\u00a0678.90','12345678.90'):
    self.assertEqual(parse(lexical,'ixt:numdotdecimalin',attrs=' scale="3" sign="-"')['facts'][0]['value'],'-12345678900')
 def test_supported_registered_dash_characters_and_only_reported_dash_become_zero(self):
  for char in ZERO_DASHES:self.assertEqual(parse(' \t'+char+'\n','ixt:zerodash')['facts'][0]['value'],'0')
  for text in('', '--', '−', '\u00a0-', 'N/A', '0'):
   with self.assertRaisesRegex(XBRLError,'lexical_subset'):parse(text,'ixt:zerodash')
 def test_original_text_format_and_raw_source_segments_are_retained(self):
  p=parse('<span>1</span> 23 456.70','ixt:numdotdecimalin');trace=p['document_set']['facts'][0]
  self.assertEqual(trace['extracted_text'],'1 23 456.70');self.assertEqual(trace['transformed_lexical'],'123456.70');self.assertEqual(trace['format'],'{http://www.xbrl.org/inlineXBRL/transformation/2015-02-26}numdotdecimalin');self.assertEqual(trace['segments'],p['facts'][0]['inline_source_segments'])
 def test_legacy_refuses_new_functions_and_new_group_separators(self):
  for text,format in [('-','ixt:zerodash'),('1,23,456','ixt:numdotdecimalin'),('1 234','ixt:numdotdecimal')]:
   with self.assertRaises(XBRLError):parse(text,format,profile=None)
  p=parse('1,234.50',profile=None);self.assertNotIn('transformation_profile',p['document_set'])
 def test_wrong_namespace_unknown_transform_and_profile_fail_closed(self):
  for format in('g:zerodash','ixt:invented'):
   with self.assertRaisesRegex(XBRLError,'transform_unsupported'):parse('-',format)
  for profile in('invented',True):
   with self.assertRaisesRegex(XBRLError,'profile_unsupported'):parse('1',profile=profile)
 def test_signed_exponent_unicode_digits_and_invalid_grouping_reject(self):
  for lexical,format in [('-1,234','ixt:numdotdecimal'),('+1,234','ixt:numdotdecimal'),('1e3','ixt:numdotdecimal'),('１２３','ixt:numdotdecimal'),('1,23.4','ixt:numdotdecimal'),('123,45,678','ixt:numdotdecimalin'),('1,2,345','ixt:numdotdecimalin'),('1 23','ixt:numdotdecimal'),('123.','ixt:numdotdecimal')]:
   with self.subTest(lexical=lexical),self.assertRaisesRegex(XBRLError,'lexical_subset'):parse(lexical,format)
 def test_nil_never_becomes_reported_zero_and_transform_is_disallowed(self):
  with self.assertRaisesRegex(XBRLError,'nil_transform'):parse('-','ixt:zerodash',attrs=' xsi:nil="true"')
  p=parse('',format='',attrs=' xsi:nil="true"');self.assertTrue(p['facts'][0]['nil']);self.assertIsNone(p['facts'][0]['value'])
 def test_mixed_registered_group_separators_are_not_sorted_or_reinterpreted(self):
  self.assertEqual(parse('1,234 567\u00a0890.10')['facts'][0]['value'],'1234567890.10')
  self.assertEqual(parse('12,34 567.80','ixt:numdotdecimalin')['facts'][0]['value'],'1234567.80')
 def test_source_and_output_limits_remain_enforced(self):
  with patch('terminal.stocks.inline_set.MAX_VALUE',4),self.assertRaisesRegex(XBRLError,'value_budget'):parse('1,234')
  with self.assertRaisesRegex(XBRLError,'inline_plain_numeric_profile'):parse('9'*65)
  with patch('terminal.stocks.inline_set.MAX_OUTPUT',32),self.assertRaises(XBRLError):parse('-',format='ixt:zerodash')
 def test_new_profile_keeps_existing_function_values_equal(self):
  for text,format in [('1,234.50','ixt:numdotdecimal'),('1.234,50','ixt:numcommadecimal'),('1234.50','')]:
   self.assertEqual(parse(text,format)['facts'][0]['value'],parse(text,format,profile=None)['facts'][0]['value'])

 def test_collection_propagates_profile_and_bad_later_set_is_atomic(self):
  c=FilingCollection('0000320193');entry={'documents':[doc('a.xhtml',html(numeric('1,23,456.70',format='ixt:numdotdecimalin'),resources=True))],'concepts':selected_concepts(NS),'taxonomy_documents':None}
  c.ingest_inline_set_batch([entry],transformation_profile=TRANSFORMATION_PROFILE)
  filing=next(iter(c._filings.values()));self.assertEqual(filing['facts'][0]['value'],'123456.70');before=c.page()
  bad={'documents':[doc('b.xhtml',html(numeric('--',format='ixt:zerodash'),resources=True))],'concepts':selected_concepts(NS),'taxonomy_documents':None}
  with self.assertRaises(XBRLError):c.ingest_inline_set_batch([entry,bad],transformation_profile=TRANSFORMATION_PROFILE)
  self.assertEqual(c.page(),before)
  with self.assertRaisesRegex(XBRLError,'profile_unsupported'):c.ingest_inline_set_batch([entry],transformation_profile='unknown')
