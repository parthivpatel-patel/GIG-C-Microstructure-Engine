"""Actual native capsule SDK file publication/read, syscall faults and process exits."""
import dataclasses,errno,gzip,json,os,stat,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import gig_microstructure as gig
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,ItchSourceAdmission,ItchCompletionAdmission,MAX_BYTES
from gig_microstructure import itch_capsule_store as store
from terminal import test_itch_source_product as fixtures


class CapsulePersistence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):fixtures.SourceProduct.setUpClass.__func__(cls)
 @classmethod
 def tearDownClass(cls):cls.directory.cleanup()
 def setUp(self):
  self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup);self.path=Path(self.temporary.name)/'completion.gig'
 def capsule(self,compressed=False):
  source=self.source+b'\0\0';source=gzip.compress(source,mtime=0)if compressed else source
  a=dataclasses.replace(self.source_a,source_sha256=fixtures.digest(source),container='single_gzip'if compressed else'binary_file')
  return ItchRecovery.create_completion_capsule(self.image,self.admission,source,a)
 def publish(self,raw,a,**kwargs):return ItchRecovery.persist_completion_capsule_file(self.path,raw,a,**kwargs)
 def read(self,a,**kwargs):return ItchRecovery.restore_completion_capsule_file(self.path,a,**kwargs)
 def test_plain_and_gzip_actual_sdk_persist_restore_preserve_original_native_state(self):
  for compressed in(False,True):
   raw,a=self.capsule(compressed);path=self.path.with_name('gzip.gig'if compressed else'plain.gig');receipt=ItchRecovery.persist_completion_capsule_file(path,raw,a);owner=ItchRecovery.restore_completion_capsule_file(path,a)
   self.assertEqual(path.read_bytes(),raw);self.assertEqual(receipt.profile,'POSIX_CREATE_ONLY_CAPSULE_V1');self.assertEqual(receipt.capsule_sha256,a.capsule_sha256);self.assertEqual(receipt.bytes,len(raw));self.assertTrue(receipt.file_fsync_completed);self.assertTrue(receipt.directory_fsync_completed);self.assertEqual(receipt.link_count,1);self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600);self.assertEqual(owner.canonical(),ItchRecovery.restore_completion_capsule(raw,a).canonical());self.assertTrue(owner.status()['finished']);self.assertEqual(owner.status()['source_records'],'10');self.assertEqual(owner.original_admission,a.checkpoint);self.assertEqual(owner.source_admission,a.source);self.assertFalse(hasattr(owner,'process'));self.assertFalse(owner.persistence_receipt.directory_fsync_completed)
 def test_existing_destination_is_never_overwritten_or_removed(self):
  raw,a=self.capsule();self.path.write_bytes(b'owner-original');before=self.path.stat()
  with self.assertRaises(store.ItchCapsulePersistenceError)as caught:self.publish(raw,a)
  error=caught.exception;self.assertIsInstance(error.primary_error,FileExistsError);self.assertFalse(error.published);self.assertFalse(error.durability_uncertain);self.assertEqual(self.path.read_bytes(),b'owner-original');self.assertEqual(self.path.stat().st_ino,before.st_ino);self.assertEqual(list(self.path.parent.iterdir()),[self.path]);self.assertEqual(error.cleanup_errors,())
 def test_native_admission_and_resource_failure_precede_all_filesystem_access(self):
  raw,a=self.capsule()
  with patch.object(store,'_parent',side_effect=AssertionError('NO_FILESYSTEM')):
   for payload,admission,budget in((raw[:-1],a,128*1024*1024),(raw,dataclasses.replace(a,checkpoint=dataclasses.replace(a.checkpoint,contract_sha256='0'*64)),128*1024*1024),(raw,a,1)):
    with self.subTest(budget=budget),self.assertRaises((ValueError,gig.EngineError)):self.publish(payload,admission,resource_budget_bytes=budget)
  self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_untrusted_nested_source_receipt_is_revalidated_on_file_restore(self):
  raw,a=self.capsule();self.publish(raw,a)
  bad=dataclasses.replace(a,source=dataclasses.replace(a.source,source_sha256='0'*64))
  with self.assertRaises(gig.EngineError):self.read(bad)
  with self.assertRaises(ValueError):self.read(dataclasses.replace(a,source=dataclasses.replace(a.source,generation=8)))
  self.assertEqual(self.path.read_bytes(),raw)
 def test_exact_admission_and_budget_validation_precede_file_read(self):
  raw,a=self.capsule()
  with patch.object(store,'_parent',side_effect=AssertionError('NO_FILESYSTEM')):
   for admission,budget in(({},128*1024*1024),(dataclasses.replace(a,capsule_sha256='bad'),128*1024*1024),(a,True),(a,0),(a,256*1024*1024+1)):
    with self.subTest(budget=budget),self.assertRaises(ValueError):self.read(admission,resource_budget_bytes=budget)
 def test_unsupported_sdk_never_reads_or_writes_files(self):
  raw,a=self.capsule()
  with patch('gig_microstructure.itch_recovery._native',types.SimpleNamespace()),patch.object(store,'_parent',side_effect=AssertionError('NO_FILESYSTEM')):
   with self.assertRaisesRegex(ValueError,'streaming_disabled'):self.publish(raw,a)
   with self.assertRaisesRegex(ValueError,'streaming_disabled'):self.read(a)
 def test_non_posix_store_explicitly_unsupported_without_fallback(self):
  raw,a=self.capsule()
  with patch.object(store.os,'name','nt'):
   with self.assertRaisesRegex(NotImplementedError,'posix_store_unsupported'):self.publish(raw,a)
   with self.assertRaisesRegex(NotImplementedError,'posix_store_unsupported'):self.read(a)
  self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_relative_traversal_empty_and_invalid_filename_paths_reject(self):
  raw,a=self.capsule();root=str(self.path.parent)
  for path in('relative.gig',root+'/../completion.gig',root+'/./completion.gig',root+'//completion.gig',root+'/',root+'/.hidden',root+'/bad\0name',b'/tmp/bytes.gig'):
   with self.subTest(path=path),self.assertRaises(ValueError):ItchRecovery.persist_completion_capsule_file(path,raw,a)
  self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_parent_symlink_is_not_followed(self):
  raw,a=self.capsule();target=self.path.parent/'real';target.mkdir();link=self.path.parent/'linked';link.symlink_to(target,target_is_directory=True)
  with self.assertRaises(store.ItchCapsulePersistenceError):ItchRecovery.persist_completion_capsule_file(link/'file.gig',raw,a)
  with self.assertRaises(store.ItchCapsulePersistenceError):ItchRecovery.restore_completion_capsule_file(link/'file.gig',a)
  self.assertEqual(list(target.iterdir()),[])
 def test_destination_symlink_cannot_be_used_for_read_or_publication(self):
  raw,a=self.capsule();target=self.path.parent/'original';target.write_bytes(raw);self.path.symlink_to(target)
  with self.assertRaises(store.ItchCapsulePersistenceError):self.publish(raw,a)
  with self.assertRaises(store.ItchCapsulePersistenceError):self.read(a)
  self.assertTrue(self.path.is_symlink());self.assertEqual(target.read_bytes(),raw);self.assertEqual(len(list(self.path.parent.iterdir())),2)
 def test_parent_and_file_writable_by_other_principals_reject(self):
  raw,a=self.capsule();self.path.parent.chmod(0o777)
  with self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertIn('parent_ownership_or_mode',str(error.exception.primary_error));self.path.parent.chmod(0o700);self.path.write_bytes(raw);self.path.chmod(0o666)
  with self.assertRaises(store.ItchCapsulePersistenceError)as error:self.read(a)
  self.assertIn('file_ownership_or_mode',str(error.exception.primary_error))
 def test_foreign_file_owner_rejects_before_reading(self):
  raw,a=self.capsule();self.path.write_bytes(raw);real=store.os.fstat
  def foreign(fd):
   value=real(fd)
   if stat.S_ISREG(value.st_mode):
    data=list(value);data[4]=os.geteuid()+1;return os.stat_result(data)
   return value
  with patch.object(store.os,'fstat',side_effect=foreign),patch.object(store.os,'read',side_effect=AssertionError('NO_READ')):
   with self.assertRaises(store.ItchCapsulePersistenceError)as error:self.read(a)
  self.assertIn('file_ownership_or_mode',str(error.exception.primary_error))
 def test_fifo_and_directory_cannot_block_or_supply_capsule_bytes(self):
  _,a=self.capsule()
  for kind in('fifo','directory'):
   if kind=='fifo':os.mkfifo(self.path,0o600)
   else:self.path.mkdir()
   with self.subTest(kind=kind),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.read(a)
   self.assertIn('file_ownership_or_mode',str(error.exception.primary_error))
   if kind=='fifo':self.path.unlink()
   else:self.path.rmdir()
 def test_sparse_oversized_and_short_files_reject_before_allocation(self):
  _,a=self.capsule()
  for size in(81,MAX_BYTES+1):
   with self.path.open('wb')as file:file.truncate(size)
   with patch.object(store.os,'read',side_effect=AssertionError('NO_READ')):
    with self.subTest(size=size),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.read(a)
   self.assertIn('byte_budget',str(error.exception.primary_error))
 def test_corrupted_and_trailing_file_bytes_never_reach_native_restore(self):
  raw,a=self.capsule()
  for payload in(raw[:-1],raw+b' ',raw[:24]+b'x'+raw[25:]):
   self.path.write_bytes(payload)
   with patch.object(ItchRecovery,'restore_completion_capsule',side_effect=AssertionError('NO_NATIVE')):
    with self.assertRaises(store.ItchCapsulePersistenceError):self.read(a)
 def test_partial_writes_complete_exactly_before_fsync_and_publication(self):
  raw,a=self.capsule();write=store.os.write;fsync=store.os.fsync;link=store.os.link;trace=[]
  def short(fd,data):trace.append('write');return write(fd,data[:7])
  def sync(fd):trace.append('directory_fsync'if stat.S_ISDIR(os.fstat(fd).st_mode)else'file_fsync');return fsync(fd)
  def publish(*args,**kwargs):trace.append('publish');return link(*args,**kwargs)
  with patch.object(store.os,'write',side_effect=short),patch.object(store.os,'fsync',side_effect=sync),patch.object(store.os,'link',side_effect=publish):receipt=self.publish(raw,a)
  self.assertGreater(trace.count('write'),1);self.assertLess(trace.index('file_fsync'),trace.index('publish'));self.assertLess(trace.index('publish'),trace.index('directory_fsync'));self.assertTrue(receipt.directory_fsync_completed);self.assertEqual(self.path.read_bytes(),raw)
 def test_zero_progress_write_never_publishes_and_cleans_only_staging(self):
  raw,a=self.capsule();sentinel=self.path.parent/'unrelated';sentinel.write_bytes(b'owner')
  with patch.object(store.os,'write',return_value=0),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertFalse(error.exception.published);self.assertEqual(error.exception.primary_error.errno,errno.EIO);self.assertEqual(list(self.path.parent.iterdir()),[sentinel]);self.assertEqual(sentinel.read_bytes(),b'owner')
 def test_corrupt_write_readback_prevents_publication(self):
  raw,a=self.capsule();write=store.os.write
  def corrupt(fd,data):return write(fd,b'x'*len(data))
  with patch.object(store.os,'write',side_effect=corrupt),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertIn('file_digest',str(error.exception.primary_error));self.assertFalse(error.exception.published);self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_file_fsync_failure_never_exposes_destination(self):
  raw,a=self.capsule();fsync=store.os.fsync
  def fail(fd):
   if stat.S_ISREG(os.fstat(fd).st_mode):raise OSError(errno.EIO,'file_sync_fault')
   return fsync(fd)
  with patch.object(store.os,'fsync',side_effect=fail),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertIn('file_sync_fault',str(error.exception.primary_error));self.assertFalse(error.exception.published);self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_link_failure_never_changes_existing_namespace(self):
  raw,a=self.capsule()
  with patch.object(store.os,'link',side_effect=OSError(errno.EIO,'link_fault')),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertFalse(error.exception.published);self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_directory_fsync_failure_is_explicit_post_publication_uncertainty(self):
  raw,a=self.capsule();fsync=store.os.fsync
  def fail(fd):
   if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError(errno.EIO,'directory_sync_fault')
   return fsync(fd)
  with patch.object(store.os,'fsync',side_effect=fail),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  failure=error.exception;self.assertTrue(failure.published);self.assertTrue(failure.file_fsync_completed);self.assertFalse(failure.directory_fsync_completed);self.assertTrue(failure.durability_uncertain);self.assertEqual(failure.code,'itch_capsule_publication_uncertain');self.assertEqual(self.path.read_bytes(),raw);self.assertTrue(self.read(a).status()['finished'])
 def test_primary_write_and_cleanup_failures_are_both_retained(self):
  raw,a=self.capsule()
  with patch.object(store.os,'write',side_effect=OSError(errno.ENOSPC,'primary_write_fault')),patch.object(store.os,'unlink',side_effect=OSError(errno.EACCES,'cleanup_fault')),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  failure=error.exception;self.assertEqual(failure.primary_error.errno,errno.ENOSPC);self.assertEqual(len(failure.cleanup_errors),1);self.assertEqual(failure.cleanup_errors[0].errno,errno.EACCES);self.assertFalse(failure.published);self.assertFalse(self.path.exists());self.assertEqual(len(list(self.path.parent.iterdir())),1)
 def test_interrupted_stage_cleanup_never_deletes_replaced_inode(self):
  raw,a=self.capsule();write=store.os.write;unlink=store.os.unlink
  def replace(fd,data):
   stage=next(self.path.parent.glob('.gig-capsule-*.pending'));unlink(stage);stage.write_bytes(b'unrelated-replacement');raise OSError(errno.EIO,'write_after_namespace_replacement')
  with patch.object(store.os,'write',side_effect=replace),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertEqual(len(error.exception.cleanup_errors),1);self.assertIn('staging_replaced',str(error.exception.cleanup_errors[0]));self.assertEqual(next(self.path.parent.iterdir()).read_bytes(),b'unrelated-replacement');self.assertFalse(self.path.exists())
 def test_growth_during_read_and_identity_change_are_rejected(self):
  raw,a=self.capsule();self.publish(raw,a);read=store.os.read;changed=False
  def grow(fd,size):
   nonlocal changed
   data=read(fd,size)
   if not changed:
    with self.path.open('ab')as file:file.write(b'x')
    changed=True
   return data
  with patch.object(store.os,'read',side_effect=grow),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.read(a)
  self.assertIn('file_changed',str(error.exception.primary_error))
 def test_staging_collisions_are_bounded_and_never_delete_existing_file(self):
  raw,a=self.capsule();stage=self.path.parent/('.gig-capsule-'+'a'*32+'.pending');stage.write_bytes(b'owner-original')
  with patch.object(store.secrets,'token_hex',return_value='a'*32),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.publish(raw,a)
  self.assertIsInstance(error.exception.primary_error,FileExistsError);self.assertEqual(stage.read_bytes(),b'owner-original');self.assertEqual(list(self.path.parent.iterdir()),[stage])
 def test_authenticated_hardlinked_capsule_is_not_misrepresented_as_immutable(self):
  raw,a=self.capsule();self.publish(raw,a);alias=self.path.parent/'same-original';os.link(self.path,alias);owner=self.read(a);self.assertEqual(owner.persistence_receipt.link_count,2);self.assertFalse(owner.persistence_receipt.file_fsync_completed);self.assertTrue(owner.status()['finished'])
 def child(self,raw,a,mode):
  files=self.path.parent/'inputs';files.mkdir();(files/'raw').write_bytes(raw);(files/'admission.json').write_text(json.dumps(dataclasses.asdict(a)))
  script='''import dataclasses,json,os,socket,stat,sys
from pathlib import Path
from gig_microstructure.itch_recovery import ItchRecovery,ItchAdmission,ItchSourceAdmission,ItchCompletionAdmission
from gig_microstructure import itch_capsule_store as store
def forbidden(*a,**k):raise AssertionError('NO_APPLICATION_OR_NETWORK')
socket.socket.bind=forbidden;socket.socket.connect=forbidden;socket.socket.connect_ex=forbidden
p=Path(sys.argv[1]);mode=sys.argv[2];raw=(p/'inputs/raw').read_bytes();v=json.loads((p/'inputs/admission.json').read_text());a=ItchCompletionAdmission(v['capsule_sha256'],ItchAdmission(**v['checkpoint']),ItchSourceAdmission(**v['source']))
if mode=='before_publish':
 def stop(*a,**k):os._exit(71)
 store.os.link=stop
elif mode=='after_publish':
 real=store.os.link
 def stop(*a,**k):real(*a,**k);os._exit(72)
 store.os.link=stop
if mode in('before_publish','after_publish'):ItchRecovery.persist_completion_capsule_file(p/'completion.gig',raw,a)
elif mode=='publish':
 receipt=ItchRecovery.persist_completion_capsule_file(p/'completion.gig',raw,a);print(json.dumps(dataclasses.asdict(receipt)))
else:
 owner=ItchRecovery.restore_completion_capsule_file(p/'completion.gig',a);print(json.dumps({'status':owner.status(),'canonical':owner.canonical(),'receipt':dataclasses.asdict(owner.persistence_receipt)}))
'''
  return subprocess.run([sys.executable,'-c',script,str(self.path.parent),mode],env=os.environ.copy(),capture_output=True,text=True,timeout=30)
 def test_actual_process_exit_before_publish_leaves_no_destination(self):
  raw,a=self.capsule();result=self.child(raw,a,'before_publish');self.assertEqual(result.returncode,71,result.stderr);self.assertFalse(self.path.exists());stages=list(self.path.parent.glob('.gig-capsule-*.pending'));self.assertEqual(len(stages),1);self.assertEqual(stages[0].read_bytes(),raw)
 def test_actual_process_exit_after_publish_restores_complete_two_link_inode(self):
  raw,a=self.capsule(True);result=self.child(raw,a,'after_publish');self.assertEqual(result.returncode,72,result.stderr);self.assertEqual(self.path.read_bytes(),raw);self.assertEqual(self.path.stat().st_nlink,2);owner=self.read(a);self.assertTrue(owner.status()['finished']);self.assertEqual(owner.persistence_receipt.link_count,2)
  # A distinct process restores the public file with independent admission; it
  # neither guesses/removes the unfinished staging alias nor invents fsync proof.
  script="import json,sys;from pathlib import Path;from gig_microstructure.itch_recovery import *;p=Path(sys.argv[1]);v=json.loads((p/'inputs/admission.json').read_text());a=ItchCompletionAdmission(v['capsule_sha256'],ItchAdmission(**v['checkpoint']),ItchSourceAdmission(**v['source']));o=ItchRecovery.restore_completion_capsule_file(p/'completion.gig',a);print(json.dumps({'status':o.status(),'links':o.persistence_receipt.link_count}))"
  restored=subprocess.run([sys.executable,'-c',script,str(self.path.parent)],env=os.environ.copy(),capture_output=True,text=True,timeout=30,check=True);value=json.loads(restored.stdout);self.assertTrue(value['status']['finished']);self.assertEqual(value['links'],2);self.assertEqual(len(list(self.path.parent.glob('.gig-capsule-*.pending'))),1)
 def test_actual_new_process_publishes_and_another_restores_native_owner(self):
  raw,a=self.capsule(True);result=self.child(raw,a,'publish');self.assertEqual(result.returncode,0,result.stderr);receipt=json.loads(result.stdout);self.assertTrue(receipt['directory_fsync_completed']);self.assertEqual(receipt['capsule_sha256'],a.capsule_sha256)
  # Reuse exact independent input files without rewriting/publishing source.
  script="import json,sys;from pathlib import Path;from gig_microstructure.itch_recovery import *;p=Path(sys.argv[1]);v=json.loads((p/'inputs/admission.json').read_text());a=ItchCompletionAdmission(v['capsule_sha256'],ItchAdmission(**v['checkpoint']),ItchSourceAdmission(**v['source']));o=ItchRecovery.restore_completion_capsule_file(p/'completion.gig',a);print(json.dumps({'status':o.status(),'canonical':o.canonical()}))"
  restored=subprocess.run([sys.executable,'-c',script,str(self.path.parent)],env=os.environ.copy(),capture_output=True,text=True,timeout=30,check=True);value=json.loads(restored.stdout);self.assertTrue(value['status']['finished']);self.assertEqual(value['canonical'],ItchRecovery.restore_completion_capsule(raw,a).canonical());self.assertEqual(self.path.read_bytes(),raw)
 def test_repeated_short_reads_restore_exact_source_without_chunk_count_authority(self):
  raw,a=self.capsule();self.publish(raw,a);read=store.os.read
  def short(fd,size):return read(fd,min(size,3))
  with patch.object(store.os,'read',side_effect=short):owner=self.read(a)
  self.assertEqual(owner.canonical(),ItchRecovery.restore_completion_capsule(raw,a).canonical());self.assertEqual(owner.persistence_receipt.bytes,len(raw))
 def test_pathname_replaced_after_open_cannot_claim_original_file_receipt(self):
  raw,a=self.capsule();self.publish(raw,a);open_=store.os.open;replaced=False;original=self.path.parent/'retained-original'
  def replace(name,flags,*args,**kwargs):
   nonlocal replaced
   fd=open_(name,flags,*args,**kwargs)
   if name==self.path.name and not replaced:
    self.path.rename(original);self.path.write_bytes(raw);replaced=True
   return fd
  with patch.object(store.os,'open',side_effect=replace),self.assertRaises(store.ItchCapsulePersistenceError)as error:self.read(a)
  self.assertIn('path_changed',str(error.exception.primary_error));self.assertEqual(original.read_bytes(),raw);self.assertEqual(self.path.read_bytes(),raw)
 def test_concurrent_create_only_publishers_cannot_overwrite_winner(self):
  import concurrent.futures,threading
  raw,a=self.capsule();compressed,b=self.capsule(True);link=store.os.link;ready=threading.Barrier(2)
  def together(*args,**kwargs):ready.wait(timeout=10);return link(*args,**kwargs)
  def publish(payload,admission):
   try:return self.publish(payload,admission)
   except store.ItchCapsulePersistenceError as error:return error
  with patch.object(store.os,'link',side_effect=together),concurrent.futures.ThreadPoolExecutor(max_workers=2)as workers:
   results=list(workers.map(lambda args:publish(*args),[(raw,a),(compressed,b)]))
  successes=[r for r in results if isinstance(r,store.ItchCapsuleFileReceipt)];errors=[r for r in results if isinstance(r,store.ItchCapsulePersistenceError)];self.assertEqual(len(successes),1);self.assertEqual(len(errors),1);self.assertIsInstance(errors[0].primary_error,FileExistsError);self.assertFalse(errors[0].published);self.assertEqual(list(self.path.parent.iterdir()),[self.path]);self.assertEqual(fixtures.digest(self.path.read_bytes()),successes[0].capsule_sha256);winner=a if successes[0].capsule_sha256==a.capsule_sha256 else b;self.assertTrue(self.read(winner).status()['finished'])
 def test_restrictive_creation_mask_cannot_make_published_capsule_unreadable(self):
  raw,a=self.capsule();open_=store.os.open
  def masked(path,flags,mode=0o777,**kwargs):return open_(path,flags,0 if flags&os.O_CREAT else mode,**kwargs)
  with patch.object(store.os,'open',side_effect=masked):receipt=self.publish(raw,a)
  self.assertEqual(stat.S_IMODE(self.path.stat().st_mode),0o600);self.assertTrue(receipt.directory_fsync_completed);self.assertTrue(self.read(a).status()['finished'])
 def test_private_mode_failure_prevents_any_public_destination(self):
  raw,a=self.capsule()
  with patch.object(store.os,'fchmod',side_effect=OSError(errno.EIO,'mode_fault')),self.assertRaises(store.ItchCapsulePersistenceError)as caught:self.publish(raw,a)
  self.assertEqual(caught.exception.primary_error.errno,errno.EIO);self.assertFalse(caught.exception.published);self.assertEqual(list(self.path.parent.iterdir()),[])
 def test_resigned_file_hash_cannot_replace_native_capsule_structure_validation(self):
  raw,a=self.capsule();malformed=b'NOTCAPS!'+raw[8:];self.path.write_bytes(malformed);replacement=dataclasses.replace(a,capsule_sha256=fixtures.digest(malformed))
  with self.assertRaises(gig.EngineError):self.read(replacement)
  self.assertEqual(self.path.read_bytes(),malformed)
 def test_preexisting_syscall_tracing_does_not_invent_platform_unsupported(self):
  script="import os;original=os.link;os.link=lambda *a,**k:original(*a,**k);from gig_microstructure.itch_capsule_store import _platform;_platform();print('POSIX_CAPABILITIES_RETAINED')"
  result=subprocess.run([sys.executable,'-c',script],env=os.environ.copy(),capture_output=True,text=True,timeout=30,check=True);self.assertEqual(result.stdout.strip(),'POSIX_CAPABILITIES_RETAINED')
 def test_legacy_interrupt_without_add_note_preserves_primary_and_cleanup(self):
  class LegacyInterrupt(KeyboardInterrupt):
   @property
   def add_note(self):raise AttributeError('add_note is unavailable')
  primary=LegacyInterrupt('operator stop');cleanup=OSError(errno.EACCES,'cleanup')
  with self.assertRaises(LegacyInterrupt)as raised:store._raise(primary,[cleanup],published=True,file_synced=True)
  self.assertIs(raised.exception,primary);self.assertEqual(primary.itch_capsule_cleanup_errors,(cleanup,));self.assertTrue(primary.itch_capsule_published);self.assertTrue(primary.itch_capsule_file_fsync_completed);self.assertFalse(primary.itch_capsule_directory_fsync_completed);self.assertTrue(primary.itch_capsule_durability_uncertain)
 def test_modern_interrupt_notes_and_publication_diagnostics_are_retained(self):
  primary=SystemExit(7);cleanup=OSError(errno.EIO,'cleanup')
  with self.assertRaises(SystemExit)as raised:store._raise(primary,[cleanup],published=True,file_synced=True,directory_synced=True)
  self.assertIs(raised.exception,primary);self.assertEqual(primary.code,7);self.assertEqual(primary.itch_capsule_cleanup_errors,(cleanup,));self.assertFalse(primary.itch_capsule_durability_uncertain)
  if callable(getattr(primary,'add_note',None)):self.assertTrue(any('Capsule cleanup failures'in n for n in primary.__notes__))
 def test_fallible_diagnostic_hook_never_masks_original_interrupt(self):
  class FallibleInterrupt(GeneratorExit):
   def add_note(self,_text):raise RuntimeError('diagnostic hook failure')
  primary=FallibleInterrupt('generator closed');cleanup=OSError(errno.EIO,'cleanup')
  with self.assertRaises(FallibleInterrupt)as raised:store._raise(primary,[cleanup])
  self.assertIs(raised.exception,primary);self.assertEqual(primary.itch_capsule_cleanup_errors,(cleanup,));self.assertFalse(primary.itch_capsule_published)
 def test_actual_write_interrupt_keeps_cleanup_error_without_add_note(self):
  class LegacyInterrupt(KeyboardInterrupt):add_note=None
  raw,a=self.capsule();primary=LegacyInterrupt('stop write')
  with patch.object(store.os,'write',side_effect=primary),patch.object(store.os,'unlink',side_effect=OSError(errno.EACCES,'cleanup')),self.assertRaises(LegacyInterrupt)as raised:self.publish(raw,a)
  self.assertIs(raised.exception,primary);self.assertFalse(primary.itch_capsule_published);self.assertIsInstance(primary.itch_capsule_cleanup_errors[0],OSError);self.assertFalse(self.path.exists())
