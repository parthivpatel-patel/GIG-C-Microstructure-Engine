"""Actual C++ source coordinator through SDK/product/CLI;authored files only."""
import copy,dataclasses,gzip,json,os,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchAdmission,ItchSourceAdmission,ItchRecovery,MAX_BYTES
from terminal.itch_product import build_bundle,continue_source,digest,implementation_identity,ItchProduct,encoded,save_new,migrate
from terminal.server.engine import NativeSession

class SourceProduct(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.directory=tempfile.TemporaryDirectory();root=Path(cls.directory.name)
  import gig_microstructure._native as native
  fixture=Path(os.environ.get('GIG_ITCH_FIXTURE',str(Path(native.__file__).parents[2]/'gig_itch_durable_checkpoint_tests')))
  target=root/'image';run=subprocess.run([str(fixture),'--fixture-source',str(target)],capture_output=True,text=True,check=True,timeout=30);meta=json.loads(run.stdout)
  cls.image=target.read_bytes();cls.source=Path(str(target)+'.source').read_bytes();cls.admission=ItchAdmission(**{k:meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')})
  cls.source_a=ItchSourceAdmission(digest(cls.source),cls.admission.capture,cls.admission.generation,'binary_file',0,0)
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def resume(self,source=None,**kwargs):
  raw=self.source if source is None else source
  a=kwargs.pop('source_admission')if 'source_admission'in kwargs else dataclasses.replace(self.source_a,source_sha256=digest(raw)if isinstance(raw,(bytes,bytearray))else self.source_a.source_sha256)
  return ItchRecovery.resume_source(self.image,self.admission,raw,a,**kwargs)
 def bundle(self,*,tail=b''):
  image,a=ItchRecovery.migrate(self.image,self.admission,implementation_identity());return build_bundle(image,a,tail)
 def test_plain_and_crc_verified_gzip_only_apply_suffix_and_restart_idempotently(self):
  original=ItchRecovery.restore(self.image,self.admission);canonical=original.canonical()
  for container,source in [('binary_file',self.source),('single_gzip',gzip.compress(self.source,mtime=0))]:
   a=dataclasses.replace(self.source_a,source_sha256=digest(source),container=container);owner=self.resume(source,source_admission=a)
   self.assertEqual(owner.status()['source_records'],'10');self.assertEqual(owner.book(0)['snapshot']['data']['book']['bids'][0]['quantity'],'7');self.assertEqual(owner.canonical()[1],canonical[1]);self.assertEqual(owner.admission.artifact_sha256,digest(owner.checkpoint()))
   repeated=ItchRecovery.resume_source(owner.checkpoint(),owner.admission,source,a);self.assertEqual(repeated.checkpoint(),owner.checkpoint())
  self.assertEqual(original.canonical(),canonical);self.assertEqual(original.checkpoint(),self.image)
 def test_source_hash_scope_types_positions_and_resource_bounds_fail_closed(self):
  for change in({'source_sha256':'0'*64},{'capture':'other'},{'generation':18},{'first_frame':True},{'first_frame':2**64-2},{'first_ordinal':-1},{'container':'arbitrary'}):
   with self.subTest(change=change),self.assertRaises((ValueError,gig.EngineError)):self.resume(source_admission=dataclasses.replace(self.source_a,**change))
  for change in({'first_frame':2},{'first_ordinal':1}):
   with self.assertRaises(gig.EngineError):self.resume(source_admission=dataclasses.replace(self.source_a,**change))
  for source in(bytearray(self.source),'not bytes',b'x'*(MAX_BYTES+1)):
   with self.assertRaises(ValueError):self.resume(source)
  with self.assertRaises(gig.EngineError):self.resume(resource_budget_bytes=1)
 def test_crc_truncation_extra_members_terminal_and_partial_frames_reject(self):
  z=gzip.compress(self.source,mtime=0);corrupt=bytearray(z);corrupt[-8]^=1
  for raw in(z[:-1],bytes(corrupt),z+z):
   with self.assertRaises(gig.EngineError):self.resume(raw,source_admission=dataclasses.replace(self.source_a,source_sha256=digest(raw),container='single_gzip'))
  for raw in(self.source[:-1],self.source+b'\x00\x00',self.source+b'\x00'):
   with self.assertRaises(gig.EngineError):self.resume(raw)
 def test_committed_prefix_change_rejects_even_when_source_digest_is_recomputed(self):
  raw=bytearray(self.source);raw[20]^=1
  with self.assertRaises(gig.EngineError):self.resume(bytes(raw))
  with self.assertRaises(gig.EngineError):self.resume(self.source[-25:])
 def test_optional_sdk_build_fails_explicitly_without_fallback(self):
  with patch('gig_microstructure.itch_recovery._native',types.SimpleNamespace()):
   with self.assertRaisesRegex(ValueError,'sdk_streaming_disabled'):self.resume()
 def test_product_v2_preserves_source_evidence_paused_native_restore_and_selection(self):
  old=self.bundle();new=continue_source(old,digest(old),self.source,self.source_a);v=json.loads(new)
  self.assertEqual(v['version'],2);self.assertEqual(v['source_history'][0]['source_sha256'],digest(self.source));self.assertEqual(v['source_history'][0]['from_source_records'],9);self.assertEqual(v['source_history'][0]['to_source_records'],10)
  self.assertEqual(continue_source(new,digest(new),self.source,self.source_a),new)
  s=NativeSession.restore_checkpoint(new,digest(new),implementation_identity());self.assertFalse(s.playing);self.assertEqual(s.position,10);self.assertEqual(s.state()['book']['bids'][0]['quantity'],'7');self.assertEqual(s.state()['provenance']['source_recovery_history'],v['source_history']);self.assertEqual(s.checkpoint(implementation_identity()),new)
  s.control('speed',4);self.assertFalse(s.playing);s.control('book',1);self.assertEqual(s.state()['instrument'],'TWO')
 def test_pending_authored_continuation_cannot_be_silently_discarded(self):
  # Last source frame is a valid cancellation of reference103.
  offset=0;last=None
  while offset<len(self.source):
   size=int.from_bytes(self.source[offset:offset+2],'big');last=self.source[offset:offset+2+size];offset+=2+size
  old=self.bundle(tail=last)
  with self.assertRaisesRegex(ValueError,'pending_continuation'):continue_source(old,digest(old),self.source,self.source_a)
  self.assertEqual(ItchProduct.restore(old,digest(old)).position,9)
 def test_source_history_malformed_scope_cursor_and_budget_reject(self):
  old=self.bundle();new=continue_source(old,digest(old),self.source,self.source_a);v=json.loads(new)
  for change in({'to_source_records':11},{'from_source_records':11},{'generation':18},{'capture':'other'},{'first_frame':True},{'source_sha256':'bad'}):
   bad=copy.deepcopy(v);bad['source_history'][0].update(change);raw=encoded(bad)
   with self.subTest(change=change),self.assertRaises(ValueError):ItchProduct.restore(raw,digest(raw))
  bad=copy.deepcopy(v);bad['source_history']*=5;raw=encoded(bad)
  with self.assertRaisesRegex(ValueError,'history_budget'):ItchProduct.restore(raw,digest(raw))
  bad=copy.deepcopy(v);bad['version']=3;raw=encoded(bad)
  with self.assertRaisesRegex(ValueError,'schema'):ItchProduct.restore(raw,digest(raw))
 def test_explicit_code_migration_preserves_v2_source_lineage(self):
  old=self.bundle();new=continue_source(old,digest(old),self.source,self.source_a);v=json.loads(new);v['native_binary_sha256']='0'*64;trusted_old=encoded(v)
  converted=migrate(trusted_old,digest(trusted_old));new_v=json.loads(converted);self.assertEqual(new_v['source_history'],v['source_history']);self.assertEqual(new_v['version'],2);self.assertEqual(ItchProduct.restore(converted,digest(converted)).position,10)
 def test_private_cli_continue_and_separate_process_restore_never_launch_app(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);old=self.bundle();save_new(root/'bundle',old,digest(old));source=root/'source';source.write_bytes(self.source);source.chmod(0o600);target=root/'next'
   command=[sys.executable,'scripts/manage_itch_session.py','continue-source','--input',str(root/'bundle'),'--expected-sha256',digest(old),'--source',str(source),'--source-sha256',digest(self.source),'--container','binary_file','--first-frame','0','--first-ordinal','0','--output',str(target)]
   run=subprocess.run(command,capture_output=True,text=True,timeout=30);self.assertEqual(run.returncode,0,run.stdout+run.stderr);summary=json.loads(run.stdout);self.assertEqual(summary['status'],'SOURCE_CONTINUED');self.assertFalse(summary['provider_connected']);self.assertEqual(target.stat().st_mode&0o777,0o600)
   probe=subprocess.run([sys.executable,'scripts/manage_itch_session.py','inspect','--input',str(target),'--expected-sha256',summary['output_sha256']],capture_output=True,text=True,timeout=30);self.assertEqual(probe.returncode,0,probe.stderr);self.assertEqual(json.loads(probe.stdout)['source_records'],'10')
   again=subprocess.run(command,capture_output=True,text=True,timeout=30);self.assertEqual(again.returncode,1);self.assertEqual(digest(target.read_bytes()),summary['output_sha256'])
