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
