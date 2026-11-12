"""Offline CLI tests use authored XML only;no listening application."""
import contextlib,io,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.inspect_xbrl_instances import inspect,main
from .test_xbrl_collection import entry,EARLY
from .test_xbrl_instance import NS
class XBRLTool(unittest.TestCase):
 def fixture(self,root):
  e=entry();(root/'instance.xml').write_bytes(e['raw']);doc={'schema':'gig.sec.xbrl.input_batch.v1','issuer_cik':'0000320193','origin':'HISTORICAL_SYNTHETIC','entries':[{'path':'instance.xml','manifest':e['manifest'],'gaap_namespace':NS}]};path=root/'batch.json';path.write_text(json.dumps(doc));return path,doc
 def test_summary_export_and_reproducible_result_do_not_fetch(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);path,_=self.fixture(root)
   with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):summary,result=inspect(path,EARLY)
   self.assertEqual(summary['selected_facts'],3);self.assertEqual(summary['status'],'OFFLINE_PROFILE_VALIDATED');self.assertFalse(summary['provider_requested']);self.assertNotIn('history',summary);self.assertEqual(inspect(path,EARLY)[1],result)
   stream=io.StringIO()
   with contextlib.redirect_stdout(stream):self.assertEqual(main(['--batch',str(path),'--as-of',EARLY,'--output',str(root/'private.json')]),0)
   self.assertEqual(json.loads((root/'private.json').read_text()),result);self.assertEqual((root/'private.json').stat().st_mode&0o777,0o600)
   with contextlib.redirect_stdout(stream):self.assertEqual(main(['--batch',str(path),'--as-of',EARLY,'--output',str(root/'private.json')]),2)
 def test_path_traversal_symlink_and_unknown_authority_fail_before_fetch(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);path,doc=self.fixture(root)
   for name in ('../instance.xml','/tmp/instance.xml'):
    doc['entries'][0]['path']=name;path.write_text(json.dumps(doc))
    with self.assertRaises(ValueError):inspect(path,EARLY)
   (root/'link.xml').symlink_to(root/'instance.xml');doc['entries'][0]['path']='link.xml';path.write_text(json.dumps(doc))
   with self.assertRaises(ValueError):inspect(path,EARLY)
   doc['url']='https://invalid.example';path.write_text(json.dumps(doc))
   with self.assertRaises(ValueError):inspect(path,EARLY)
 def test_observed_origin_not_implicitly_authorized_and_errors_do_not_echo_input(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);path,doc=self.fixture(root);doc['origin']='OBSERVED_OFFICIAL_RESPONSE';doc['entries'][0]['manifest']['permission_reference']='AUTHORED_PRIVATE_MARKER';path.write_text(json.dumps(doc));stream=io.StringIO()
   with contextlib.redirect_stdout(stream):self.assertEqual(main(['--batch',str(path),'--as-of',EARLY]),2)
   self.assertNotIn('AUTHORED_PRIVATE_MARKER',stream.getvalue());self.assertFalse(json.loads(stream.getvalue())['provider_requested'])
 def test_invalid_cutoff_and_duplicate_json_fields_are_explicit_rejections(self):
  with tempfile.TemporaryDirectory()as d:
   path,_=self.fixture(Path(d))
   with self.assertRaises(ValueError):inspect(path,'2024-02-30T00:00:00Z')
   path.write_text('{"schema":1,"schema":2}')
   with self.assertRaises(ValueError):inspect(path,EARLY)
 def dts_fixture(self,root):
  from .test_xbrl_types import sample,PROFILE
  e=sample();(root/'instance.xml').write_bytes(e['raw']);(root/'taxonomy.xsd').write_bytes(e['documents'][0]['raw'])
  doc={'schema':'gig.sec.xbrl.input_dts_batch.v1','issuer_cik':'0000320193','origin':'HISTORICAL_SYNTHETIC','numeric_profile':PROFILE,'entries':[{'path':'instance.xml','manifest':e['manifest'],'gaap_namespace':NS,'instance_uri':e['instance_uri'],'documents':[{'path':'taxonomy.xsd','uri':e['documents'][0]['uri'],'sha256':e['documents'][0]['sha256']}]}]};path=root/'batch.json';path.write_text(json.dumps(doc));return path,doc
 def test_dts_numeric_cli_joins_actual_supplied_documents_and_exports(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);path,doc=self.dts_fixture(root)
   with patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):summary,result=inspect(path,EARLY)
   self.assertEqual(summary['selected_facts'],1);self.assertEqual(result['history']['assets'][0]['value'],'123.4500');self.assertIn('numeric_value_validation',result['selected_input_coverage'][0]['xbrl_coverage']['dts_corroboration']);self.assertFalse(summary['provider_requested'])
   stream=io.StringIO()
   with contextlib.redirect_stdout(stream):self.assertEqual(main(['--batch',str(path),'--as-of',EARLY,'--output',str(root/'private.json')]),0)
   self.assertEqual(json.loads((root/'private.json').read_text()),result)
 def test_dts_cli_hash_path_symlink_and_profile_fail_closed(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);path,original=self.dts_fixture(root)
   import copy
   for mutation in('hash','traversal','symlink','profile'):
    doc=copy.deepcopy(original)
    if mutation=='hash':doc['entries'][0]['documents'][0]['sha256']='0'*64
    elif mutation=='traversal':doc['entries'][0]['documents'][0]['path']='../taxonomy.xsd'
    elif mutation=='symlink':
     (root/'link.xsd').symlink_to(root/'taxonomy.xsd');doc['entries'][0]['documents'][0]['path']='link.xsd'
    else:doc['numeric_profile']='guess'
    path.write_text(json.dumps(doc))
    with self.subTest(mutation=mutation),self.assertRaises(ValueError):inspect(path,EARLY)
 def test_dts_cli_does_not_retain_partial_export_on_invalid_types(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);path,doc=self.dts_fixture(root);doc['entries'][0]['documents'][0]['sha256']='0'*64;path.write_text(json.dumps(doc));stream=io.StringIO();output=root/'never.json'
   with contextlib.redirect_stdout(stream):self.assertEqual(main(['--batch',str(path),'--as-of',EARLY,'--output',str(output)]),2)
   self.assertFalse(output.exists());self.assertFalse(json.loads(stream.getvalue())['raw_source_retained']);self.assertNotIn('123.4500',stream.getvalue())
