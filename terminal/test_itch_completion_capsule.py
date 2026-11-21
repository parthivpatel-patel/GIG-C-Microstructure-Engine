"""Separate native finished-source replay capsule;authored immutable originals only."""
import dataclasses,gzip,json,os,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,ItchSourceAdmission,ItchCompletionAdmission,MAX_BYTES
from terminal import test_itch_source_product as fixtures

class CompletionCapsule(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixtures.SourceProduct.setUpClass.__func__(cls)
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def create(self,*,compressed=False,**kwargs):
  raw=self.source+b'\0\0';raw=gzip.compress(raw,mtime=0)if compressed else raw
  spec=dataclasses.replace(self.source_a,source_sha256=fixtures.digest(raw),container='single_gzip'if compressed else'binary_file')
  return ItchRecovery.create_completion_capsule(self.image,self.admission,raw,spec,**kwargs)
 def test_plain_and_gzip_reconstruct_exact_finished_state(self):
  for compressed in(False,True):
   capsule,admission=self.create(compressed=compressed);owner=ItchRecovery.restore_completion_capsule(capsule,admission)
   self.assertEqual(capsule[:8],b'GIGSCAP1');self.assertEqual(int.from_bytes(capsule[8:16],'little'),len(self.image));self.assertEqual(capsule[24:24+len(self.image)],self.image);self.assertEqual(admission.capsule_sha256,fixtures.digest(capsule));self.assertTrue(owner.status()['finished']);self.assertTrue(owner.status()['input_complete']);self.assertTrue(owner.status()['session_incomplete']);self.assertEqual(owner.status()['source_records'],'10');self.assertEqual(owner.book(0)['snapshot']['data']['book']['bids'][0]['quantity'],'7');self.assertEqual(owner.original_admission,self.admission);self.assertEqual(owner.source_admission,admission.source)
 def test_capsule_is_deterministic_and_original_owner_unchanged(self):
  prior=ItchRecovery.restore(self.image,self.admission);before=(prior.checkpoint(),prior.canonical());capsule,a=self.create();again,b=self.create();self.assertEqual((capsule,a),(again,b));left=ItchRecovery.restore_completion_capsule(capsule,a);right=ItchRecovery.restore_completion_capsule(capsule,a);self.assertEqual(left.canonical(),right.canonical());self.assertEqual((prior.checkpoint(),prior.canonical()),before);self.assertEqual(a.checkpoint.artifact_sha256,fixtures.digest(self.image))
 def test_corruption_rejects_before_trusting_internal_data(self):
  raw,a=self.create()
  for offset in(0,7,8,16,24,len(raw)-1):
   bad=bytearray(raw);bad[offset]^=1;bad=bytes(bad)
   with self.subTest(offset=offset),self.assertRaisesRegex(ValueError,'capsule_digest'):ItchRecovery.restore_completion_capsule(bad,a)
   forged=dataclasses.replace(a,capsule_sha256=fixtures.digest(bad))
   with self.subTest(rehashed=offset),self.assertRaises(gig.EngineError):ItchRecovery.restore_completion_capsule(bad,forged)
 def test_trailing_truncated_and_overflow_lengths_reject_after_rehash(self):
  raw,a=self.create();overflow=raw[:8]+(2**64-1).to_bytes(8,'little')+raw[16:]
  for bad in(raw[:-1],raw+b'x',overflow,raw[:16]+(2**64-1).to_bytes(8,'little')+raw[24:]):
   with self.assertRaises(gig.EngineError):ItchRecovery.restore_completion_capsule(bad,dataclasses.replace(a,capsule_sha256=fixtures.digest(bad)))
 def test_finished_owner_remains_read_only_and_active_codec_refuses_capsule(self):
  raw,a=self.create();owner=ItchRecovery.restore_completion_capsule(raw,a);self.assertFalse(hasattr(owner,'process'));self.assertFalse(hasattr(owner,'checkpoint'))
  with self.assertRaises(gig.EngineError):gig._checked(owner._owner.checkpoint())
  with self.assertRaises(gig.EngineError):ItchRecovery.restore(raw,dataclasses.replace(self.admission,artifact_sha256=fixtures.digest(raw)))
 def test_stale_nested_admission_and_generation_fail_closed(self):
  raw,a=self.create()
  with self.assertRaisesRegex(ValueError,'source_scope'):ItchRecovery.restore_completion_capsule(raw,dataclasses.replace(a,source=dataclasses.replace(a.source,generation=8)))
  stale=dataclasses.replace(a,checkpoint=dataclasses.replace(a.checkpoint,generation=8),source=dataclasses.replace(a.source,generation=8))
  with self.assertRaises(gig.EngineError):ItchRecovery.restore_completion_capsule(raw,stale)
  with self.assertRaises(gig.EngineError):ItchRecovery.restore_completion_capsule(raw,dataclasses.replace(a,checkpoint=dataclasses.replace(a.checkpoint,contract_sha256='0'*64)))
 def test_exact_types_bounds_and_nested_admission_required(self):
  raw,a=self.create()
  for value in(None,{},self.admission):
   with self.assertRaises(ValueError):ItchRecovery.restore_completion_capsule(raw,value)
  for value in(bytearray(raw),'bad',b'x'*81,b'x'*(MAX_BYTES+1)):
   with self.assertRaises(ValueError):ItchRecovery.restore_completion_capsule(value,a)
  for budget in(True,0,-1,2**63):
   with self.assertRaises(ValueError):ItchRecovery.restore_completion_capsule(raw,a,resource_budget_bytes=budget)
  for bad in(dataclasses.replace(a,capsule_sha256='bad'),dataclasses.replace(a,checkpoint={}),dataclasses.replace(a,source={})):
   with self.assertRaises(ValueError):ItchRecovery.restore_completion_capsule(raw,bad)
 def test_small_resource_budgets_do_not_publish_a_candidate(self):
  raw,a=self.create()
  with self.assertRaises(gig.EngineError):self.create(resource_budget_bytes=1)
  with self.assertRaises(gig.EngineError):ItchRecovery.restore_completion_capsule(raw,a,resource_budget_bytes=1)
 def test_encoder_requires_original_complete_source_and_original_hashes(self):
  for raw in(self.source,self.source+b'\0',self.source+b'\0\0x'):
   spec=dataclasses.replace(self.source_a,source_sha256=fixtures.digest(raw))
   with self.assertRaises(gig.EngineError):ItchRecovery.create_completion_capsule(self.image,self.admission,raw,spec)
  with self.assertRaises(ValueError):ItchRecovery.create_completion_capsule(self.image,self.admission,b'\0\0',self.source_a)
 def test_default_sdk_without_capability_never_falls_back(self):
  raw,a=self.create()
  with patch('gig_microstructure.itch_recovery._native',types.SimpleNamespace()):
   with self.assertRaisesRegex(ValueError,'sdk_streaming_disabled'):self.create()
   with self.assertRaisesRegex(ValueError,'sdk_streaming_disabled'):ItchRecovery.restore_completion_capsule(raw,a)
 def test_actual_new_process_restores_retained_capsule(self):
  raw,a=self.create(compressed=True)
  with tempfile.TemporaryDirectory()as directory:
   p=Path(directory);(p/'capsule').write_bytes(raw);(p/'admission').write_text(json.dumps(dataclasses.asdict(a)))
   script="""import json,socket,sys
from pathlib import Path
def no(*a,**k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=no;socket.socket.connect=no;socket.socket.connect_ex=no
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,ItchSourceAdmission,ItchCompletionAdmission
p=Path(sys.argv[1]);v=json.loads((p/'admission').read_text());a=ItchCompletionAdmission(v['capsule_sha256'],ItchAdmission(**v['checkpoint']),ItchSourceAdmission(**v['source']));o=ItchRecovery.restore_completion_capsule((p/'capsule').read_bytes(),a);print(json.dumps({'status':o.status(),'canonical':o.canonical()}))
"""
   out=subprocess.run([sys.executable,'-c',script,str(p)],env=os.environ.copy(),capture_output=True,text=True,check=True,timeout=30);value=json.loads(out.stdout);self.assertEqual(value['canonical'],ItchRecovery.restore_completion_capsule(raw,a).canonical());self.assertTrue(value['status']['finished']);self.assertEqual(value['status']['source_records'],'10')
