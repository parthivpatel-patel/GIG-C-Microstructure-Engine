"""Native product-session restoration and immutable files;no ASGI/socket/provider."""
import copy,errno,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from terminal.server.engine import NativeSession
from terminal.session_recovery import capture,restore,digest,migrate,save_new,load,SessionRecoveryError
CODE='a'*64
class SessionRecovery(unittest.TestCase):
 def image(self):
  session=NativeSession();session.control('seek',55);session.control('speed',4);session.playing=True
  return session,session.checkpoint(CODE)
 def test_product_hot_restore_never_replays_default_startup_and_resumes_paused(self):
  original,image=self.image()
  with patch.object(gig.Replay,'apply',side_effect=AssertionError('No source replay during restore')):restored=NativeSession.restore_checkpoint(image,digest(image),CODE)
  self.assertEqual(restored.position,55);self.assertEqual(restored.speed,4);self.assertFalse(restored.playing);self.assertIsNone(restored.live_feed);self.assertEqual(restored.replay.canonical(),original.replay.canonical());self.assertEqual(restored.state()['book'],original.state()['book'])
  original.step();restored.step();self.assertEqual(restored.replay.canonical(),original.replay.canonical())
 def test_capture_modes_controls_and_unknown_schema_are_fail_closed(self):
  session,image=self.image();before=session.replay.canonical()
  for mode in('LIVE','SIMULATION'):
   session.mode=mode
   with self.assertRaises(SessionRecoveryError):capture(session,CODE)
  session.mode='HISTORICAL_REPLAY'
  for change in [{'version':0},{'version':True},{'position':True},{'position':999},{'speed':3},{'fixture_sha256':'b'*64},{'extra':1},{'native_binary_sha256':'b'*64}]:
   candidate={**image,**change}
   with self.subTest(change=change),self.assertRaises(ValueError):restore(candidate,digest(candidate),CODE)
  self.assertEqual(session.replay.canonical(),before)
 def test_digest_corruption_or_native_position_mismatch_cannot_publish_session(self):
  _,image=self.image();changed=copy.deepcopy(image);changed['position']=20
  with self.assertRaisesRegex(SessionRecoveryError,'native_position'):restore(changed,digest(changed),CODE)
  with self.assertRaisesRegex(SessionRecoveryError,'digest'):restore(changed,digest(image),CODE)
  changed=copy.deepcopy(image);changed['canonical']+='x'
  with self.assertRaises(gig.EngineError):restore(changed,digest(changed),CODE)
 def test_explicit_migration_validates_native_state_and_preserves_input(self):
  session,image=self.image();before=copy.deepcopy(image)
  new=migrate(image,digest(image),CODE,'b'*64);self.assertEqual(image,before);self.assertEqual(len(new['migration_history']),1);self.assertEqual(new['migration_history'][0]['from_checkpoint_sha256'],digest(image))
  restored=restore(new,digest(new),'b'*64);self.assertEqual(restored.replay.canonical(),session.replay.canonical())
  with self.assertRaisesRegex(SessionRecoveryError,'no_migration'):migrate(new,digest(new),'b'*64,'b'*64)
  for _ in range(3):new=migrate(new,digest(new),new['implementation_sha256'],'c'*64 if new['implementation_sha256']!='c'*64 else'b'*64)
  with self.assertRaisesRegex(SessionRecoveryError,'migration_budget'):migrate(new,digest(new),new['implementation_sha256'],'d'*64)
 def test_rebinding_changed_binary_requires_explicit_native_validation(self):
  _,image=self.image();old={**image,'native_binary_sha256':'b'*64}
  with self.assertRaisesRegex(SessionRecoveryError,'binary_migration'):restore(old,digest(old),CODE)
  migrated=migrate(old,digest(old),CODE,'c'*64);self.assertEqual(restore(migrated,digest(migrated),'c'*64).position,55)
  corrupt=copy.deepcopy(old);corrupt['canonical']+='x'
  with self.assertRaises(gig.EngineError):migrate(corrupt,digest(corrupt),CODE,'c'*64)
 def test_private_atomic_new_revision_does_not_overwrite_rollback(self):
  session,image=self.image()
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'old.json';save_new(path,image,digest(image),CODE);self.assertEqual(path.stat().st_mode&0o777,0o600);self.assertEqual(load(path,digest(image),CODE).replay.canonical(),session.replay.canonical());before=path.read_bytes()
   with self.assertRaisesRegex(SessionRecoveryError,'exists'):save_new(path,image,digest(image),CODE)
   migrated=migrate(image,digest(image),CODE,'b'*64);save_new(Path(directory)/'new.json',migrated,digest(migrated),'b'*64);self.assertEqual(path.read_bytes(),before)
 def test_faults_before_and_after_atomic_publication_are_distinguished(self):
  _,image=self.image()
  with tempfile.TemporaryDirectory()as directory:
   path=Path(directory)/'new.json'
   def fail():raise OSError(errno.ENOSPC,'authored disk full')
   with self.assertRaises(OSError):save_new(path,image,digest(image),CODE,before_publish=fail)
   self.assertFalse(path.exists());self.assertEqual(list(Path(directory).iterdir()),[])
   with self.assertRaisesRegex(SessionRecoveryError,'uncertain_reopen'):save_new(path,image,digest(image),CODE,after_publish=fail)
   self.assertEqual(load(path,digest(image),CODE).position,55)
 def test_process_exit_after_publish_leaves_a_complete_admissible_file(self):
  _,image=self.image()
  with tempfile.TemporaryDirectory()as directory:
   original=Path(directory)/'input.json';original.write_text(json.dumps(image));target=Path(directory)/'state.json'
   code="import json,os;from terminal.session_recovery import save_new,digest;v=json.load(open("+repr(str(original))+"));save_new("+repr(str(target))+",v,digest(v),'"+CODE+"',after_publish=lambda:os._exit(79))"
   result=subprocess.run([sys.executable,'-c',code],env=os.environ.copy(),timeout=30,capture_output=True);self.assertEqual(result.returncode,79);self.assertEqual(load(target,digest(image),CODE).position,55)
 def test_symlink_unsafe_permissions_and_oversized_input_are_rejected(self):
  _,image=self.image()
  with tempfile.TemporaryDirectory()as directory:
   parent=Path(directory);target=parent/'state.json';link=parent/'link.json';save_new(target,image,digest(image),CODE);link.symlink_to(target)
   with self.assertRaises(ValueError):load(link,digest(image),CODE)
   os.chmod(target,0o644)
   with self.assertRaisesRegex(SessionRecoveryError,'private_file'):load(target,digest(image),CODE)
  bad={**image,'canonical':'x'*(8*1024*1024)}
  with self.assertRaisesRegex(SessionRecoveryError,'byte_budget'):digest(bad)
