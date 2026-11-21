"""Actual C++ verified container completion through optional SDK;no app/providers."""
import dataclasses,gzip,json,os,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchRecovery,ItchSourceCompletion,MAX_BYTES
from terminal import test_itch_source_product as fixtures

class SourceCompletion(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixtures.SourceProduct.setUpClass.__func__(cls)
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def complete(self,raw=None,**kwargs):
  raw=self.source+b'\0\0'if raw is None else raw
  admission=kwargs.pop('source_admission',dataclasses.replace(self.source_a,source_sha256=fixtures.digest(raw)if type(raw)is bytes else self.source_a.source_sha256))
  return ItchRecovery.complete_source(self.image,self.admission,raw,admission,**kwargs)
 def test_plain_and_single_gzip_finish_source_without_duplicate_prefix(self):
  for compressed in(False,True):
   raw=self.source+b'\0\0';raw=gzip.compress(raw,mtime=0)if compressed else raw;a=dataclasses.replace(self.source_a,source_sha256=fixtures.digest(raw),container='single_gzip'if compressed else'binary_file')
   owner=self.complete(raw,source_admission=a);self.assertIsInstance(owner,ItchSourceCompletion);self.assertEqual(owner.status()['source_records'],'10');self.assertTrue(owner.status()['finished']);self.assertTrue(owner.status()['input_complete']);self.assertTrue(owner.status()['session_incomplete']);self.assertEqual(owner.book(0)['snapshot']['data']['book']['bids'][0]['quantity'],'7');self.assertEqual(owner.original_admission,self.admission);self.assertEqual(owner.source_admission,a)
 def test_finished_owner_exposes_read_only_views_and_rejects_internal_writes(self):
  owner=self.complete();self.assertEqual(owner.describe()['source'],'p1g-native-synthetic');self.assertFalse(hasattr(owner,'process'));self.assertFalse(hasattr(owner,'checkpoint'));before=owner.canonical()
  with self.assertRaises(gig.EngineError):gig._checked(owner._owner.checkpoint())
  step=gig._checked(owner._owner.process(b'X','0','0'));self.assertFalse(step['committed']);self.assertEqual(owner.canonical(),before)
 def test_legacy_prefix_contract_rejects_terminal_unchanged(self):
  raw=self.source+b'\0\0';a=dataclasses.replace(self.source_a,source_sha256=fixtures.digest(raw))
  with self.assertRaises(gig.EngineError):ItchRecovery.resume_source(self.image,self.admission,raw,a)
  owner=ItchRecovery.resume_source(self.image,self.admission,self.source,self.source_a);self.assertEqual(owner.status()['source_records'],'10');self.assertIsInstance(owner.checkpoint(),bytes)
 def test_missing_terminal_partial_frame_or_trailing_data_fail_closed(self):
  for raw in(self.source,self.source[:-1],self.source+b'\0',self.source+b'\0\0x',self.source+b'\0\0\0\0'):
   with self.subTest(length=len(raw)),self.assertRaises(gig.EngineError):self.complete(raw)
 def test_single_gzip_crc_trailer_and_member_integrity(self):
  z=gzip.compress(self.source+b'\0\0',mtime=0);bad=bytearray(z);bad[-8]^=1
  for raw in(z[:-1],bytes(bad),z+z,z+b'x',gzip.compress(self.source,mtime=0)):
   a=dataclasses.replace(self.source_a,source_sha256=fixtures.digest(raw),container='single_gzip')
   with self.subTest(length=len(raw)),self.assertRaises(gig.EngineError):self.complete(raw,source_admission=a)
 def test_committed_prefix_semantics_cannot_be_replaced_by_rehash(self):
  raw=bytearray(self.source+b'\0\0');raw[20]^=1
  with self.assertRaises(gig.EngineError):self.complete(bytes(raw))
  with self.assertRaises(gig.EngineError):self.complete(self.source[-25:]+b'\0\0')
 def test_identity_generation_position_types_and_resource_bounds(self):
  for change in({'source_sha256':'0'*64},{'capture':'other'},{'generation':18},{'container':'unknown'},{'first_frame':True},{'first_ordinal':-1}):
   with self.subTest(change=change),self.assertRaises((ValueError,gig.EngineError)):self.complete(source_admission=dataclasses.replace(self.source_a,**change))
  for raw in(bytearray(self.source),'not bytes',b'x'*(MAX_BYTES+1)):
   with self.assertRaises(ValueError):self.complete(raw)
  with self.assertRaises(gig.EngineError):self.complete(resource_budget_bytes=1)
 def test_disabled_optional_source_sdk_has_no_fallback(self):
  with patch('gig_microstructure.itch_recovery._native',types.SimpleNamespace()):
   with self.assertRaisesRegex(ValueError,'sdk_streaming_disabled'):self.complete()
 def test_prior_checkpoint_owner_and_inputs_remain_immutable(self):
  prior=ItchRecovery.restore(self.image,self.admission);before=(prior.checkpoint(),prior.canonical(),prior.status());completed=self.complete();self.assertEqual((prior.checkpoint(),prior.canonical(),prior.status()),before);self.assertEqual(completed.canonical()[1],prior.canonical()[1]);self.assertEqual(self.admission.artifact_sha256,fixtures.digest(self.image))
 def test_book_argument_validation_retains_exact_native_constraints(self):
  completed=self.complete()
  for args in[(True,10),(2,10),(0,0),(0,4097)]:
   with self.assertRaises(ValueError):completed.book(*args)
 def test_actual_fresh_process_can_finish_from_retained_image_and_source(self):
  with tempfile.TemporaryDirectory()as directory:
   p=Path(directory);(p/'image').write_bytes(self.image);(p/'source').write_bytes(self.source+b'\0\0');(p/'metadata').write_text(json.dumps({'image':dataclasses.asdict(self.admission),'source':dataclasses.asdict(dataclasses.replace(self.source_a,source_sha256=fixtures.digest(self.source+b'\0\0')))}))
   script="""import json,socket,sys
from pathlib import Path
def no(*a,**k):raise AssertionError('NO_NETWORK_OR_SERVER')
socket.socket.bind=no;socket.socket.connect=no;socket.socket.connect_ex=no
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,ItchSourceAdmission
p=Path(sys.argv[1]);m=json.loads((p/'metadata').read_text());o=ItchRecovery.complete_source((p/'image').read_bytes(),ItchAdmission(**m['image']),(p/'source').read_bytes(),ItchSourceAdmission(**m['source']));print(json.dumps({'status':o.status(),'canonical':o.canonical()}))
"""
   result=subprocess.run([sys.executable,'-c',script,str(p)],env=os.environ.copy(),capture_output=True,text=True,timeout=30,check=True);out=json.loads(result.stdout);self.assertEqual(out['canonical'],self.complete().canonical());self.assertTrue(out['status']['finished']);self.assertEqual(out['status']['source_records'],'10')
