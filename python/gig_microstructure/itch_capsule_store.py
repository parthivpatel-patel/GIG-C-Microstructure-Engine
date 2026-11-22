"""POSIX create-only persistence for independently admitted native capsules.

No trust metadata is loaded from disk. Exact capsule/source/native admission stays
with ItchRecovery; this module only handles bounded descriptor-relative bytes.
File/directory fsync completion describes syscalls, not physical crash durability.
"""
import errno,hashlib,os,re,secrets,stat
from dataclasses import dataclass

MAX_CAPSULE_BYTES=32*1024*1024
PROFILE='POSIX_CREATE_ONLY_CAPSULE_V1'
# Capability sets store original functions. Inspect their declared names so
# syscall tracing/fault wrappers do not turn a supported OS into an unsupported one.
_DIRFD_SUPPORTED=all(hasattr(os,n)for n in('open','link','stat','unlink','supports_dir_fd','supports_follow_symlinks'))and {'open','link','stat','unlink'}<={getattr(f,'__name__',None)for f in os.supports_dir_fd}and 'link'in{getattr(f,'__name__',None)for f in os.supports_follow_symlinks}


@dataclass(frozen=True)
class ItchCapsuleFileReceipt:
    profile:str
    file_name:str
    capsule_sha256:str
    bytes:int
    device:int
    inode:int
    link_count:int
    file_fsync_completed:bool
    directory_fsync_completed:bool
    action:str


class ItchCapsulePersistenceError(RuntimeError):
    """A failed operation never deletes/replaces the public destination.

    After an atomic link succeeds the complete artifact may remain. Inspect
    published/directory_fsync_completed; an exception is not proof of absence.
    Primary and cleanup failures are retained separately instead of masking one.
    """
    def __init__(self,primary_error,cleanup_errors,*,published=False,file_synced=False,directory_synced=False):
        self.primary_error=primary_error
        self.cleanup_errors=tuple(cleanup_errors)
        self.published=published
        self.file_fsync_completed=file_synced
        self.directory_fsync_completed=directory_synced
        self.durability_uncertain=published and not directory_synced
        self.code='itch_capsule_publication_uncertain'if self.durability_uncertain else'itch_capsule_store_failed'
        super().__init__(self.code)


def _platform():
    required=('O_NOFOLLOW','O_DIRECTORY','O_CLOEXEC','O_NONBLOCK','geteuid','fchmod')
    if os.name!='posix'or any(not hasattr(os,n)for n in required)or not _DIRFD_SUPPORTED:
        raise NotImplementedError('itch_capsule_posix_store_unsupported')


def _parent(path):
    _platform();value=os.fspath(path)
    if type(value)is not str or not value.startswith('/')or len(value)>4096 or '\0'in value:raise ValueError('itch_capsule_absolute_path_required')
    parts=value.split('/')[1:]
    if not parts or any(not p or p in('.','..')for p in parts)or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,127}',parts[-1]):raise ValueError('itch_capsule_path_components')
    flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
    fd=os.open('/',flags)
    try:
        for part in parts[:-1]:
            next_fd=os.open(part,flags,dir_fd=fd)
            old_fd=fd;fd=next_fd
            os.close(old_fd)
        info=os.fstat(fd)
        if not stat.S_ISDIR(info.st_mode)or info.st_uid!=os.geteuid()or info.st_mode&0o022 or info.st_nlink<1:raise ValueError('itch_capsule_parent_ownership_or_mode')
        return fd,parts[-1]
    except BaseException as primary:
        cleanup=[]
        try:os.close(fd)
        except BaseException as error:cleanup.append(error)
        _raise(primary,cleanup)


def _regular(info):
    if not stat.S_ISREG(info.st_mode)or info.st_uid!=os.geteuid()or info.st_mode&0o022 or info.st_nlink<1:raise ValueError('itch_capsule_file_ownership_or_mode')
    if not 82<=info.st_size<=MAX_CAPSULE_BYTES:raise ValueError('itch_capsule_file_byte_budget')


def _identity(info):
    return(info.st_dev,info.st_ino,info.st_size,info.st_uid,info.st_mode,info.st_nlink,info.st_mtime_ns,info.st_ctime_ns)


def _read_verified(fd,expected,*,collect=True):
    before=os.fstat(fd);_regular(before);os.lseek(fd,0,os.SEEK_SET)
    # A fixed buffer bounds retained memory even if every legal read is short.
    # Per-read chunk lists could otherwise add one Python object per source byte.
    total=0;output=bytearray(before.st_size)if collect else None;sha=hashlib.sha256()
    while True:
        raw=os.read(fd,min(65536,before.st_size-total+1))
        if not raw:break
        total+=len(raw)
        if total>before.st_size or total>MAX_CAPSULE_BYTES:raise ValueError('itch_capsule_file_changed')
        sha.update(raw)
        if collect:output[total-len(raw):total]=raw
    after=os.fstat(fd);_regular(after)
    if total!=before.st_size or _identity(before)!=_identity(after):raise ValueError('itch_capsule_file_changed')
    if sha.hexdigest()!=expected:raise ValueError('itch_capsule_file_digest')
    return bytes(output)if collect else None,after


def _receipt(leaf,expected,info,*,action,file_synced=False,directory_synced=False):
    return ItchCapsuleFileReceipt(PROFILE,leaf,expected,info.st_size,info.st_dev,info.st_ino,info.st_nlink,file_synced,directory_synced,action)


def _raise(primary,cleanup,*,published=False,file_synced=False,directory_synced=False):
    if isinstance(primary,(KeyboardInterrupt,SystemExit,GeneratorExit)):
        if cleanup:primary.add_note('Capsule cleanup failures: '+','.join(type(e).__name__ for e in cleanup))
        raise primary
    error=ItchCapsulePersistenceError(primary,cleanup,published=published,file_synced=file_synced,directory_synced=directory_synced)
    if primary is None:raise error
    raise error from primary


def _persist_verified_capsule(path,payload,expected):
    """Caller must have natively admitted the exact immutable bytes first.

    Complete-write, readback SHA, file fsync, atomic no-overwrite link, unlink only
    this operation's staging inode, then directory fsync. No destination rollback.
    """
    if type(payload)is not bytes or not 82<=len(payload)<=MAX_CAPSULE_BYTES or type(expected)is not str or not re.fullmatch('[0-9a-f]{64}',expected)or hashlib.sha256(payload).hexdigest()!=expected:raise ValueError('itch_capsule_verified_bytes_required')
    directory,leaf=_parent(path);fd=None;stage=None;created=False;original=None;published=False;file_synced=False;directory_synced=False;primary=None;cleanup=[];receipt=None
    try:
        for _ in range(8):
            name='.gig-capsule-'+secrets.token_hex(16)+'.pending'
            try:fd=os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
            except FileExistsError:continue
            stage=name;created=True;break
        if fd is None:raise FileExistsError(errno.EEXIST,'itch_capsule_staging_collision')
        original=os.fstat(fd)
        if original.st_uid!=os.geteuid()or not stat.S_ISREG(original.st_mode)or original.st_nlink!=1 or original.st_mode&0o077:raise ValueError('itch_capsule_staging_identity')
        # umask may remove owner permissions from the requested creation mode.
        # Pin exact private readable/writable mode before persisting any bytes.
        os.fchmod(fd,0o600)
        original=os.fstat(fd)
        if stat.S_IMODE(original.st_mode)!=0o600:raise ValueError('itch_capsule_staging_mode')
        view=memoryview(payload);done=0
        while done<len(view):
            n=os.write(fd,view[done:])
            if type(n)is not int or not 0<n<=len(view)-done:raise OSError(errno.EIO,'itch_capsule_short_write')
            done+=n
        os.fsync(fd);file_synced=True
        _,verified=_read_verified(fd,expected,collect=False)
        if(verified.st_dev,verified.st_ino)!=(original.st_dev,original.st_ino)or verified.st_nlink!=1:raise ValueError('itch_capsule_staging_identity')
        closing=fd;fd=None;os.close(closing)
        os.link(stage,leaf,src_dir_fd=directory,dst_dir_fd=directory,follow_symlinks=False);published=True
        final=os.stat(leaf,dir_fd=directory,follow_symlinks=False);_regular(final)
        if(final.st_dev,final.st_ino)!=(original.st_dev,original.st_ino):raise ValueError('itch_capsule_publication_identity')
        os.unlink(stage,dir_fd=directory);created=False
        os.fsync(directory);directory_synced=True
        final=os.stat(leaf,dir_fd=directory,follow_symlinks=False);_regular(final)
        if(final.st_dev,final.st_ino)!=(original.st_dev,original.st_ino)or final.st_size!=len(payload):raise ValueError('itch_capsule_publication_identity')
        receipt=_receipt(leaf,expected,final,action='PUBLISHED_CREATE_ONLY',file_synced=True,directory_synced=True)
    except BaseException as error:primary=error
    finally:
        if fd is not None:
            try:os.close(fd)
            except BaseException as error:cleanup.append(error)
        if created:
            try:
                info=os.stat(stage,dir_fd=directory,follow_symlinks=False)
                if original is None or(info.st_dev,info.st_ino)!=(original.st_dev,original.st_ino):raise ValueError('itch_capsule_staging_replaced')
                os.unlink(stage,dir_fd=directory)
                os.fsync(directory)
            except BaseException as error:cleanup.append(error)
        try:os.close(directory)
        except BaseException as error:cleanup.append(error)
    if primary is not None or cleanup:_raise(primary,cleanup,published=published,file_synced=file_synced,directory_synced=directory_synced)
    return receipt


def _read_capsule(path,expected):
    """Bound before allocation; O_NONBLOCK avoids opening a FIFO as a byte source.

    Stable positive link counts are allowed: a process may stop after the atomic
    publish link, before removing its private staging alias. This authenticates
    current read bytes, not inode immutability or a hostile concurrent namespace.
    """
    if type(expected)is not str or not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('itch_capsule_digest_required')
    directory,leaf=_parent(path);fd=None;primary=None;cleanup=[];out=None
    try:
        fd=os.open(leaf,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=directory)
        payload,info=_read_verified(fd,expected)
        named=os.stat(leaf,dir_fd=directory,follow_symlinks=False);_regular(named)
        if _identity(named)!=_identity(info):raise ValueError('itch_capsule_path_changed')
        out=payload,_receipt(leaf,expected,info,action='READ_VERIFIED_BYTES')
    except BaseException as error:primary=error
    finally:
        if fd is not None:
            try:os.close(fd)
            except BaseException as error:cleanup.append(error)
        try:os.close(directory)
        except BaseException as error:cleanup.append(error)
    if primary is not None or cleanup:_raise(primary,cleanup)
    return out
