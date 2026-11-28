"""Explicit authored-native product-session images. No startup/network activation.

Stable schema/canonical checks before hot restoration. Versioned migration is an
explicit owner operation,not auto-relabeling old native/source evidence.
"""
import copy,hashlib,json,os,re,stat
from pathlib import Path
import gig_microstructure as gig
from terminal.native_recovery import native_binary_identity
from terminal.server.fixtures import rules,replay_config,EVENTS,FIXTURE_SHA256
from terminal.verification.artifacts import decode,read_bytes

LIMITS={'max_orders':'128','max_levels':'32','max_snapshot_depth':'20'}
MAX_BYTES=8*1024*1024
class SessionRecoveryError(ValueError):pass

def digest(v):return hashlib.sha256(encoded(v)).hexdigest()
def encoded(v):
 raw=json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 if len(raw)>MAX_BYTES:raise SessionRecoveryError('session_checkpoint_byte_budget')
 decode(raw);return raw
def key(v):return type(v)is str and bool(re.fullmatch('[0-9a-f]{64}',v))
def capture(session,implementation_sha256):
 if not key(implementation_sha256):raise SessionRecoveryError('session_implementation_identity')
 if session.mode!='HISTORICAL_REPLAY'or session.dataset!='terminal-authored-v2'or session.recorded_session is not None:raise SessionRecoveryError('authored_native_session_required')
 if type(session.position)is not int or not 0<=session.position<=len(EVENTS)or session.speed not in(1,2,4,8):raise SessionRecoveryError('session_control_state')
 if session.replay.status()['journal_size']!=str(session.position):raise SessionRecoveryError('session_native_position')
 value={'schema':'gig.authored_session.checkpoint','version':1,'fixture_sha256':FIXTURE_SHA256,'implementation_sha256':implementation_sha256,'native_binary_sha256':native_binary_identity(),'position':session.position,'speed':session.speed,'image':session.replay.checkpoint(),'canonical':session.replay.canonical(),'migration_history':[]}
 encoded(value);return value

def _admit(payload,expected_sha256,implementation_sha256,*,require_current_binary):
 if not key(expected_sha256)or not key(implementation_sha256):raise SessionRecoveryError('session_trusted_identity_required')
 raw=encoded(payload)
 if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise SessionRecoveryError('session_checkpoint_digest')
 value=decode(raw)
 if type(value.get('version'))is not int or value.get('version')!=1:raise SessionRecoveryError('session_migration_profile_required')
 fields={'schema','version','fixture_sha256','implementation_sha256','native_binary_sha256','position','speed','image','canonical','migration_history'}
 if set(value)!=fields or value['schema']!='gig.authored_session.checkpoint'or value['fixture_sha256']!=FIXTURE_SHA256 or value['implementation_sha256']!=implementation_sha256 or not key(value['native_binary_sha256']):raise SessionRecoveryError('session_source_contract')
 if require_current_binary and value['native_binary_sha256']!=native_binary_identity():raise SessionRecoveryError('session_explicit_binary_migration_required')
 if type(value['position'])is not int or not 0<=value['position']<=len(EVENTS)or type(value['speed'])is not int or value['speed']not in(1,2,4,8)or type(value['canonical'])is not str:raise SessionRecoveryError('session_control_state')
 history=value['migration_history']
 if type(history)is not list or len(history)>4:raise SessionRecoveryError('session_migration_budget')
 for entry in history:
  if type(entry)is not dict or set(entry)!={'from_checkpoint_sha256','from_implementation_sha256','from_native_binary_sha256'}or not all(key(x)for x in entry.values()):raise SessionRecoveryError('session_migration_lineage')
 return value

def _native(value):
 native=gig.Replay.restore_checkpoint(value['image'],rules(),replay_config(),LIMITS,value['canonical'],resource_budget_bytes='33554432')
 if native.status()['journal_size']!=str(value['position']):raise SessionRecoveryError('session_native_position')
 return native

def restore(payload,expected_sha256,implementation_sha256,*,session_type=None):
 value=_admit(payload,expected_sha256,implementation_sha256,require_current_binary=True);native=_native(value)
 if session_type is None:
  from terminal.server.engine import NativeSession
  session_type=NativeSession
 session=session_type.__new__(session_type);session._initialize();session.replay=native;session.position=value['position'];session.speed=value['speed']
 # Network/feed handles,client counters,simulation and running playback stay fresh.
 return session

def migrate(payload,source_sha256,source_implementation_sha256,target_implementation_sha256):
 if not key(target_implementation_sha256):raise SessionRecoveryError('session_implementation_identity')
 value=_admit(payload,source_sha256,source_implementation_sha256,require_current_binary=False)
 if value['implementation_sha256']==target_implementation_sha256 and value['native_binary_sha256']==native_binary_identity():raise SessionRecoveryError('session_no_migration_needed')
 if len(value['migration_history'])>=4:raise SessionRecoveryError('session_migration_budget')
 native=_native(value) # Actual new native schema/config/canonical admission,not metadata-only rebinding.
 lineage={'from_checkpoint_sha256':source_sha256,'from_implementation_sha256':source_implementation_sha256,'from_native_binary_sha256':value['native_binary_sha256']}
 result={**value,'implementation_sha256':target_implementation_sha256,'native_binary_sha256':native_binary_identity(),'image':native.checkpoint(),'migration_history':value['migration_history']+[lineage]}
 encoded(result);return result

def _private_parent(path):
 path=Path(path).absolute();parent=path.parent
 if any(p.is_symlink()for p in(path,*path.parents)):raise SessionRecoveryError('session_checkpoint_symlink')
 parent.mkdir(parents=True,exist_ok=True,mode=0o700);info=parent.stat()
 if info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:raise SessionRecoveryError('session_private_directory_required')
 return path

def _publish_revision(path,raw,*,maximum_size,exists,uncertain,error_type,before_publish=None,after_publish=None):
 from gig_microstructure.itch_capsule_store import _parent,_persist_verified_capsule,ItchCapsulePersistenceError
 path=_private_parent(path)
 def open_private(value):
  return _parent(value,strict_leaf=False,private_directory=True)
 try:
  _persist_verified_capsule(path,raw,hashlib.sha256(raw).hexdigest(),minimum_size=1,maximum_size=maximum_size,
      parent_opener=open_private,before_publish=before_publish,after_publish=after_publish)
 except ItchCapsulePersistenceError as exc:
  if exc.published or exc.publication_unknown:raise error_type(uncertain)from exc
  if isinstance(exc.primary_error,FileExistsError):raise error_type(exists)from exc
  if exc.primary_error is not None and not exc.cleanup_errors:raise exc.primary_error from None
  raise

def save_new(path,payload,expected_sha256,implementation_sha256,*,before_publish=None,after_publish=None):
 # Exclusive immutable revisions:upgrade writes a different file,never overwrites rollback input.
 value=_admit(payload,expected_sha256,implementation_sha256,require_current_binary=True);_native(value);raw=encoded(value)
 _publish_revision(path,raw,maximum_size=MAX_BYTES,exists='session_checkpoint_exists',
     uncertain='session_publication_uncertain_reopen',error_type=SessionRecoveryError,
     before_publish=before_publish,after_publish=after_publish)
 return expected_sha256

def load(path,expected_sha256,implementation_sha256):
 path=_private_parent(path);info=path.stat()
 if not stat.S_ISREG(info.st_mode)or info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:raise SessionRecoveryError('session_private_file_required')
 # A crash after atomic link can leave an extra private temp hardlink. Admission
 # relies on verified bytes/private ownership,not a single-link-count assumption.
 value=decode(read_bytes(path,MAX_BYTES));return restore(value,expected_sha256,implementation_sha256)
