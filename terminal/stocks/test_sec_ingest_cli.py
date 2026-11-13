"""Owner tool gates and fixture mode;no owner config or network reads."""
import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scripts.qualify_sec_filing_ingestion import main
class IngestCLI(unittest.TestCase):
 def run_cli(self,args,environment=None):
  output=io.StringIO()
  with contextlib.redirect_stdout(output):code=main(args,environment=environment)
  return code,json.loads(output.getvalue())
 def test_fixture_runs_without_configuration_provider_or_app(self):
  with patch('terminal.stocks.sec_config.resolve',side_effect=AssertionError('NO_OWNER_CONFIG')),patch('socket.socket.connect',side_effect=AssertionError('NO_NETWORK')):
   code,r=self.run_cli(['--fixture']);self.assertEqual(code,0);self.assertEqual(r['status'],'OFFLINE_FIXTURE_PASS');self.assertEqual(r['origin'],'HISTORICAL_SYNTHETIC');self.assertFalse(r['provider_requested']);self.assertFalse(r['trading_enabled'])
 def test_fetch_requires_separate_gate_before_transport(self):
  with patch('terminal.stocks.sec_read_wire.SECReadWire.open',side_effect=AssertionError('NO_PROVIDER')):
   for e in[{}, {'GIG_SEC_XBRL_INGEST_ENABLED':'1'}]:
    code,r=self.run_cli(['--fetch','--accession','0000000123-24-000001','--as-of','2024-02-10T12:00:00Z'],e);self.assertEqual(code,2);self.assertEqual(r['status'],'BLOCKED_OR_INVALID');self.assertFalse(r['contact_disclosed'])
 def test_private_derived_export_and_checkpoint_are_explicit(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);out=root/'view.json';code,r=self.run_cli(['--fixture','--output',str(out),'--checkpoint-root',directory]);self.assertEqual(code,0);self.assertTrue(r['checkpoint_sha256']);self.assertEqual(out.stat().st_mode&0o777,0o600);self.assertEqual(json.loads(out.read_text())['schema'],'gig.backend.company_xbrl.v2')
 def test_fixture_never_masquerades_as_a_different_observed_issuer(self):
  code,r=self.run_cli(['--fixture','--symbol','MSFT']);self.assertEqual(code,2);self.assertEqual(r['status'],'BLOCKED_OR_INVALID')
 def test_output_collision_is_non_destructive(self):
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'existing.json';path.write_text('KEEP');code,r=self.run_cli(['--fixture','--output',str(path)]);self.assertEqual(code,2);self.assertEqual(path.read_text(),'KEEP')
