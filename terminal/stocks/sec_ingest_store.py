"""Explicit permission-gated private immutable source revisions. No auto retention.

Uses the existing native/source immutable writer,not a new journal algorithm.
Quotas include orphan temp files;publication uncertainty requires explicit reopen.
"""
import fcntl,hashlib,os,re,stat
from pathlib import Path
from contextlib import contextmanager
from terminal.verification.artifacts import read_bytes
from .sec_filing_ingest import MAX_IMAGE,IngestError
class FilingCheckpointStore:
 def __init__(self,root,*,enabled=False,retention_approved=False,max_revisions=16,max_bytes=64*1024*1024,before_publish=None,after_publish=None):
  if enabled is not True or retention_approved is not True:raise IngestError('sec_ingest_retention_disabled')
  if type(max_revisions)is not int or not 1<=max_revisions<=16 or type(max_bytes)is not int or not 1<=max_bytes<=64*1024*1024:raise IngestError('sec_ingest_store_budget')
  self.root=Path(root).absolute();self.max_revisions=max_revisions;self.max_bytes=max_bytes;self.before=before_publish;self.after=after_publish
  self._private(self.root,True)
 def _private(self,path,folder=False):
  if any(p.is_symlink()for p in(path,*path.parents)):raise IngestError('sec_ingest_store_symlink')
  info=path.stat()
  if info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077 or not(stat.S_ISDIR(info.st_mode)if folder else stat.S_ISREG(info.st_mode)):raise IngestError('sec_ingest_store_private_required')
 @contextmanager
 def _lock(self):
  self._private(self.root,True);fd=os.open(self.root/'.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
  try:
   info=os.fstat(fd)
   if not stat.S_ISREG(info.st_mode)or info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:raise IngestError('sec_ingest_store_lock')
   try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:raise IngestError('sec_ingest_store_busy')from None
   yield
  finally:os.close(fd)
 def save(self,raw):
  if type(raw)is not bytes or not 1<=len(raw)<=MAX_IMAGE:raise IngestError('sec_ingest_store_payload')
  sha=hashlib.sha256(raw).hexdigest();path=self.root/(sha+'.json')
  with self._lock():
   if path.exists():
    self._private(path)
    if read_bytes(path,MAX_IMAGE)!=raw:raise IngestError('sec_ingest_store_existing_corrupt')
    return sha
   count=total=0
   with os.scandir(self.root)as entries:
    for entry in entries:
     if entry.name=='.lock':continue
     count+=1
     if count>self.max_revisions:raise IngestError('sec_ingest_store_revisions')
     self._private(Path(entry.path));total+=entry.stat(follow_symlinks=False).st_size
     if total+len(raw)>self.max_bytes:raise IngestError('sec_ingest_store_bytes')
   if count>=self.max_revisions or len(raw)>self.max_bytes:raise IngestError('sec_ingest_store_exhausted')
   from terminal.itch_recovery import publish_new
   publish_new(path,raw,before_publish=self.before,after_publish=self.after)
  return sha
 def load(self,sha):
  if type(sha)is not str or not re.fullmatch('[0-9a-f]{64}',sha):raise IngestError('sec_ingest_store_identity')
  path=self.root/(sha+'.json');self._private(path);raw=read_bytes(path,MAX_IMAGE)
  if hashlib.sha256(raw).hexdigest()!=sha:raise IngestError('sec_ingest_store_integrity')
  return raw
