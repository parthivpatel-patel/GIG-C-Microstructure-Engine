"""Explicit immutable private ITCH revisions. No startup/source/network activation.

Only native-admitted authored ITCH images are supported. The independently
retained admission includes capture/generation/config/code and the artifact hash.
No automatic migration,old-generation promotion or arbitrary gzip seek exists.
"""
import os,tempfile,stat
from gig_microstructure.itch_recovery import ItchAdmission,ItchRecovery,MAX_BYTES
from terminal.session_recovery import _private_parent
from terminal.verification.artifacts import read_bytes

class ItchFileError(ValueError):pass

def save_new(path,payload,admission,*,before_publish=None,after_publish=None):
    ItchRecovery.restore(payload,admission) # Complete native admission before filesystem mutation.
    path=_private_parent(path)
    fd,temporary=tempfile.mkstemp(prefix='.gig-itch-',dir=path.parent);published=False
    try:
        with os.fdopen(fd,'wb')as stream:
            if stream.write(payload)!=len(payload):raise ItchFileError('itch_short_write')
            stream.flush();os.fsync(stream.fileno())
        if before_publish:before_publish()
        os.link(temporary,path,follow_symlinks=False);published=True
        if after_publish:after_publish()
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory)
        finally:os.close(directory)
    except FileExistsError:raise ItchFileError('itch_revision_exists')from None
    except BaseException:
        if published:raise ItchFileError('itch_publication_uncertain_reopen')from None
        raise
    finally:os.unlink(temporary)
    return admission.artifact_sha256

def load(path,admission):
    path=_private_parent(path);info=path.stat()
    if not stat.S_ISREG(info.st_mode)or info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:
        raise ItchFileError('itch_private_file_required')
    # The existing bounded reader rejects symlinks,nonregular/changed files.
    return ItchRecovery.restore(read_bytes(path,MAX_BYTES),admission)
