"""Explicit immutable private ITCH revisions. No startup/source/network activation.

Only native-admitted authored ITCH images are supported. The independently
retained admission includes capture/generation/config/code and the artifact hash.
No automatic migration,old-generation promotion or arbitrary gzip seek exists.
"""
import os,stat
from gig_microstructure.itch_recovery import ItchAdmission,ItchRecovery,MAX_BYTES
from terminal.session_recovery import _private_parent,_publish_revision
from terminal.verification.artifacts import read_bytes

class ItchFileError(ValueError):pass

def save_new(path,payload,admission,*,before_publish=None,after_publish=None):
    ItchRecovery.restore(payload,admission) # Complete native admission before filesystem mutation.
    publish_new(path,payload,before_publish=before_publish,after_publish=after_publish)
    return admission.artifact_sha256

def publish_new(path,payload,*,before_publish=None,after_publish=None):
    # Callers must complete their own admission before this shared immutable writer.
    _publish_revision(path,payload,maximum_size=64*1024*1024,exists='itch_revision_exists',
        uncertain='itch_publication_uncertain_reopen',error_type=ItchFileError,
        before_publish=before_publish,after_publish=after_publish)

def load(path,admission):
    path=_private_parent(path);info=path.stat()
    if not stat.S_ISREG(info.st_mode)or info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:
        raise ItchFileError('itch_private_file_required')
    # The existing bounded reader rejects symlinks,nonregular/changed files.
    return ItchRecovery.restore(read_bytes(path,MAX_BYTES),admission)
