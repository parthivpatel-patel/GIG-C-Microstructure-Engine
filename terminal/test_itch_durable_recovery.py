"""Real native durable ITCH admission/private publication;no app or provider."""
import dataclasses,errno,hashlib,json,os,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,MAX_BYTES
from terminal.itch_recovery import save_new,load,ItchFileError
class DurableItch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.directory=tempfile.TemporaryDirectory();cls.root=Path(cls.directory.name)
  import gig_microstructure._native as native
  executable=Path(os.environ.get('GIG_ITCH_FIXTURE',str(Path(native.__file__).parents[2]/'gig_itch_durable_checkpoint_tests')))
  result=subprocess.run([str(executable),'--fixture',str(cls.root/'authored.bin')],capture_output=True,text=True,timeout=30,check=True)
  cls.meta=json.loads(result.stdout);cls.payload=(cls.root/'authored.bin').read_bytes();cls.admission=ItchAdmission(**{k:cls.meta[k]for k in('artifact_sha256','contract_sha256','implementation_sha256','capture','generation')})
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def restore(self,payload=None,admission=None,**kw):return ItchRecovery.restore(self.payload if payload is None else payload,self.admission if admission is None else admission,**kw)
 def resigned(self,b):
  b=bytearray(b);struct.pack_into('<Q',b,16,len(b)-56);b[24:56]=hashlib.sha256(b[56:]).digest();b=bytes(b)
  return b,dataclasses.replace(self.admission,artifact_sha256=hashlib.sha256(b).hexdigest())
 def test_full_context_both_books_and_deterministic_recapture(self):
  owner=self.restore();status=owner.status();self.assertEqual(int(status['source_records']),self.meta['records']);self.assertEqual(int(status['next_frame']),self.meta['next_frame']);self.assertEqual(owner.checkpoint(),self.payload);self.assertEqual(len(owner.canonical()),2)
  # A real partial cancellation from the published complete-frame boundary.
  p=bytearray(23);p[0]=ord('X');p[1:3]=(1).to_bytes(2,'big');p[5:11]=(1).to_bytes(6,'big');p[11:19]=(103).to_bytes(8,'big');p[19:23]=(1).to_bytes(4,'big')
  another=self.restore();a=owner.process(bytes(p),frame_offset=self.meta['next_frame'],ordinal=self.meta['records']);b=another.process(bytes(p),frame_offset=self.meta['next_frame'],ordinal=self.meta['records']);self.assertTrue(a['committed']);self.assertEqual(a,b);self.assertEqual(owner.canonical(),another.canonical());self.assertNotEqual(owner.checkpoint(),self.payload)
 def test_capture_generation_contract_code_and_hash_are_independent(self):
  for change in({'capture':'another'},{'generation':18},{'contract_sha256':'0'*64},{'implementation_sha256':'a'*64},{'artifact_sha256':'0'*64}):
   with self.subTest(change=change),self.assertRaises((ValueError,gig.EngineError)):self.restore(admission=dataclasses.replace(self.admission,**change))
 def test_corruption_truncation_unknown_versions_and_trailing_bytes(self):
  for data in(self.payload[:-1],b'bad',self.payload+b'x'):
   with self.subTest(length=len(data)),self.assertRaises((ValueError,gig.EngineError)):self.restore(data)
  for index in(0,8,16,24,56,100,len(self.payload)-1):
   b=bytearray(self.payload);b[index]^=255
   if index in(16,24):b=bytes(b);a=dataclasses.replace(self.admission,artifact_sha256=hashlib.sha256(b).hexdigest())
   else:b,a=self.resigned(b)
   with self.subTest(index=index),self.assertRaises(gig.EngineError):self.restore(b,a)
 def test_python_types_budgets_and_missing_trust_are_rejected(self):
  for generation in(True,-1,2**64):
   with self.assertRaises(ValueError):self.restore(admission=dataclasses.replace(self.admission,generation=generation))
  for p in(bytearray(self.payload),'string',b'x'*(MAX_BYTES+1)):
   with self.assertRaises(ValueError):self.restore(p)
  for budget in(True,0,256*1024*1024+1):
   with self.assertRaises(ValueError):self.restore(resource_budget_bytes=budget)
  with self.assertRaises(gig.EngineError):self.restore(resource_budget_bytes=1)
 def test_old_source_positions_do_not_reapply_prefix(self):
  owner=self.restore();before=owner.canonical();step=owner.process(b'not an ITCH record',frame_offset=0,ordinal=0);self.assertFalse(step['committed']);self.assertEqual(owner.canonical(),before)
  with self.assertRaises(gig.EngineError):owner.checkpoint()
 def test_private_immutable_revision_and_corrupt_file(self):
  with tempfile.TemporaryDirectory()as d:
   target=Path(d)/'state.bin';save_new(target,self.payload,self.admission);self.assertEqual(target.stat().st_mode&0o777,0o600);self.assertEqual(load(target,self.admission).checkpoint(),self.payload)
   with self.assertRaisesRegex(ItchFileError,'revision_exists'):save_new(target,self.payload,self.admission)
   target.write_bytes(self.payload[:-1])
   with self.assertRaises(ValueError):load(target,self.admission)
 def test_disk_full_and_directory_fsync_uncertainty(self):
  with tempfile.TemporaryDirectory()as d:
   target=Path(d)/'state.bin'
   def disk_full():raise OSError(errno.ENOSPC,'authored fault')
   with self.assertRaises(OSError):save_new(target,self.payload,self.admission,before_publish=disk_full)
   self.assertFalse(target.exists());self.assertEqual(list(Path(d).iterdir()),[])
   with self.assertRaisesRegex(ItchFileError,'uncertain_reopen'):save_new(target,self.payload,self.admission,after_publish=disk_full)
   self.assertEqual(load(target,self.admission).checkpoint(),self.payload)
 def test_cross_process_exit_after_publication_and_restart(self):
  with tempfile.TemporaryDirectory()as d:
   root=Path(d);source=root/'source';source.write_bytes(self.payload);target=root/'state'
   code="from terminal.itch_recovery import save_new;from gig_microstructure.itch_recovery import ItchAdmission;import os;save_new("+repr(str(target))+",open("+repr(str(source))+",'rb').read(),ItchAdmission(**"+repr(dataclasses.asdict(self.admission))+"),after_publish=lambda:os._exit(79))"
   run=subprocess.run([sys.executable,'-c',code],capture_output=True,timeout=30,cwd=Path(__file__).resolve().parents[1]);self.assertEqual(run.returncode,79,run.stderr.decode(errors='replace'));self.assertEqual(load(target,self.admission).checkpoint(),self.payload)
 def test_symlink_and_unsafe_permissions_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   target=Path(d)/'state';save_new(target,self.payload,self.admission);link=Path(d)/'link';link.symlink_to(target)
   with self.assertRaises(ValueError):load(link,self.admission)
   os.chmod(target,0o644)
   with self.assertRaisesRegex(ItchFileError,'private_file'):load(target,self.admission)
