"""Exact metadata ingress, duplicate source keys and untouched Decimal observations."""
import asyncio,contextlib,hashlib,io,json,tempfile,unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from terminal.verification.artifacts import decode,EvidenceError
from .test_sec_filing_ingest import client,resources,ACC,PREFIX
from .xbrl_instance import canonical

class ExactMetadataJSON(unittest.TestCase):
 def test_explicit_policy_preserves_big_integer_and_integral_exponents_exactly(self):
  cases={'18446744073709551615':2**64-1,'9007199254740993':9007199254740993,'1e3':1000,'100000e-5':1,'900719925474099100e-2':9007199254740991,'0e-128':0,'-1e2':-100}
  for token,expected in cases.items():
   with self.subTest(token=token):
    value=decode(('{"n":'+token+'}').encode(),numeric_policy='exact-integer')['n'];self.assertIs(type(value),int);self.assertEqual(value,expected)
 def test_fractional_underflow_negative_zero_and_number_budgets_reject(self):
  tokens=('1.0000000000000001','9007199254740991.1','1e-999','1e-128','-0','-0.0','-0e-128','0e129','1e128','1'*129)
  for token in tokens:
   with self.subTest(token=token),self.assertRaises(EvidenceError):decode(('{"n":'+token+'}').encode(),numeric_policy='exact-integer')
 def test_duplicate_decoded_keys_and_bad_utf8_remain_rejected_in_both_policies(self):
  for policy in('finite-float','exact-integer'):
   for raw in(b'{"issuer_cik":"wrong","issuer_\\u0063ik":"right"}',b'{"source":{"sha256":"wrong","sha256":"right"}}',b'{"x":"\xff"}',b'{"x":NaN}'):
    with self.subTest(policy=policy,raw=raw),self.assertRaises(EvidenceError):decode(raw,numeric_policy=policy)
 def test_default_finite_float_evidence_policy_remains_compatible(self):
  value=decode(b'{"timing":1.25,"legacy_tiny":1e-999}');self.assertIs(type(value['timing']),float);self.assertEqual(value['timing'],1.25);self.assertEqual(value['legacy_tiny'],0.0)
  with self.assertRaisesRegex(EvidenceError,'json_numeric_policy'):decode(b'{}',numeric_policy='invented')
 def test_real_xbrl_batch_cli_refuses_aliases_before_xml_and_retains_no_output(self):
  from .test_xbrl_tool import XBRLTool
  from .test_xbrl_collection import EARLY
  from scripts.inspect_xbrl_instances import main
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);path,batch=XBRLTool().fixture(root);valid=json.dumps(batch)
   for prefix in('"schema":"contradictory",','"\\u0073chema":"contradictory",','"untrusted_metadata":1.0000000000000001,','"untrusted_metadata":-0,'):
    path.write_text('{'+prefix+valid[1:]);output=root/'must-not-exist.json';stream=io.StringIO()
    with patch('terminal.stocks.inline_xbrl.parse_xml',side_effect=AssertionError('NO_AMBIGUOUS_XML_PARSE')),contextlib.redirect_stdout(stream):result=main(['--batch',str(path),'--as-of',EARLY,'--output',str(output)])
    self.assertEqual(result,2);self.assertFalse(output.exists());self.assertNotIn('contradictory',stream.getvalue())
   path.write_text(valid)
   with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(main(['--batch',str(path),'--as-of',EARLY,'--output',str(root/'accepted.json')]),0)
   self.assertTrue((root/'accepted.json').exists())

class SECExactIngress(unittest.IsolatedAsyncioTestCase):
 async def test_exact_exponent_directory_sizes_preserve_actual_accepted_facts(self):
  original=resources();data=resources();index=json.loads(data[PREFIX+'index.json']);size=int(index['directory']['item'][0]['size']);index['directory']['item'][0]['size']='EXPONENT_MARKER';data[PREFIX+'index.json']=json.dumps(index).replace('"EXPONENT_MARKER"',str(size)+'e0').encode()
  a,_,_=client(original);b,_,_=client(data);await a.ingest(ACC);await b.ingest(ACC);self.assertEqual(a.collection.page(),b.collection.page())
 async def test_source_directory_negative_zero_and_escaped_duplicate_reject_atomically(self):
  for raw in(b'{"directory":null,"\\u0064irectory":{}}',b'{"directory":{"name":"authored","item":[]},"ignored":-0}',b'{"ignored":1e-999}'):
   data=resources();data[PREFIX+'index.json']=raw;c,_,_=client(data)
   with self.assertRaises(EvidenceError):await c.ingest(ACC)
   self.assertEqual(c.plans,{});self.assertEqual(c.sources,{})
 async def test_checkpoint_boolean_numeric_alias_is_not_a_source_metadata_match(self):
  c,_,_=client();await c.ingest(ACC);before=c.checkpoint();image=json.loads(before);self.assertIs(image['plans'][ACC]['metadata']['amendment'],False)
  for replacement in(0,0.0):
   image['plans'][ACC]['metadata']['amendment']=replacement;raw=canonical(image)
   with self.assertRaisesRegex(ValueError,'metadata_binding'):c.restore(raw,hashlib.sha256(raw).hexdigest())
   self.assertEqual(c.checkpoint(),before)
 async def test_checkpoint_lexical_errors_fail_before_any_state_or_transport_change(self):
  c,_,_=client();await c.ingest(ACC);before=c.checkpoint()
  for prefix in(b'"issuer_cik":"wrong",',b'"issuer_\\u0063ik":"wrong",',b'"ignored":1.0000000000000001,',b'"ignored":-0,'):
   raw=b'{'+prefix+before[1:]
   with self.assertRaises(EvidenceError):c.restore(raw,hashlib.sha256(raw).hexdigest())
   self.assertEqual(c.checkpoint(),before)
 async def test_authored_provider_json_keeps_exact_decimal_observations(self):
  from .service import StockWorkspace
  async def authored(*_args):return b'{"observed_decimal":1.0000000000000001}'
  workspace=StockWorkspace(environment={},fetcher=authored);payload,_=await workspace.fetch('sec','https://data.sec.gov/authored-fixture',{})
  self.assertIs(type(payload['observed_decimal']),Decimal);self.assertEqual(str(payload['observed_decimal']),'1.0000000000000001')

if __name__=='__main__':unittest.main(verbosity=2)
