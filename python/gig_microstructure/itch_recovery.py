"""Bounded version-1 full ITCH recovery. No providers,application startup or replay.

Admission metadata must be retained independently of an untrusted checkpoint.
A digest inside the checkpoint is not authentication. Automatic schema/code or
capture-generation migration is intentionally unsupported.
"""
import hashlib,re
from dataclasses import dataclass,replace
from . import _native,_checked

MAX_BYTES=32*1024*1024
@dataclass(frozen=True)
class ItchAdmission:
    artifact_sha256:str
    contract_sha256:str
    implementation_sha256:str
    capture:str
    generation:int
    def validate(self):
        if not all(type(v)is str and re.fullmatch('[0-9a-f]{64}',v) for v in (self.artifact_sha256,self.contract_sha256,self.implementation_sha256)):
            raise ValueError('itch_trusted_digest_required')
        if type(self.capture)is not str or not 1<=len(self.capture)<=128 or any(not 33<=ord(c)<=126 for c in self.capture):
            raise ValueError('itch_capture_identity')
        if type(self.generation)is not int or not 0<=self.generation<=2**64-1:raise ValueError('itch_generation')

SOURCE_CONTAINERS=('binary_file','single_gzip','gzip_members')


@dataclass(frozen=True)
class ItchSourceAdmission:
    source_sha256:str
    capture:str
    generation:int
    container:str
    first_frame:int
    first_ordinal:int
    def validate(self):
        ItchAdmission(self.source_sha256,self.source_sha256,self.source_sha256,self.capture,self.generation).validate()
        if type(self.container)is not str or self.container not in SOURCE_CONTAINERS:raise ValueError('itch_source_container')
        if type(self.first_frame)is not int or not 0<=self.first_frame<=2**64-3 or type(self.first_ordinal)is not int or not 0<=self.first_ordinal<=2**64-1:raise ValueError('itch_source_boundary')

@dataclass(frozen=True)
class ItchCompletionAdmission:
    """Independently retain this evidence;the capsule never supplies its own trust."""
    capsule_sha256:str
    checkpoint:ItchAdmission
    source:ItchSourceAdmission
    def validate(self):
        if type(self.capsule_sha256)is not str or not re.fullmatch('[0-9a-f]{64}',self.capsule_sha256):raise ValueError('itch_capsule_digest_required')
        if type(self.checkpoint)is not ItchAdmission or type(self.source)is not ItchSourceAdmission:raise ValueError('itch_capsule_admission')
        self.checkpoint.validate();self.source.validate()
        if(self.source.capture,self.source.generation)!=(self.checkpoint.capture,self.checkpoint.generation):raise ValueError('itch_source_scope')

def _validate_image(payload,admission,resource_budget_bytes):
    if type(admission)is not ItchAdmission:raise ValueError('itch_admission_required')
    admission.validate()
    if type(payload)is not bytes or not 56<=len(payload)<=MAX_BYTES:raise ValueError('itch_byte_budget')
    if type(resource_budget_bytes)is not int or not 0<resource_budget_bytes<=256*1024*1024:raise ValueError('itch_resource_budget')
    if hashlib.sha256(payload).hexdigest()!=admission.artifact_sha256:raise ValueError('itch_artifact_digest')

@dataclass(frozen=True)
class ItchPartialBinaryTail:
    source_sha256:str
    source_offset:int
    residual_bytes:int
    next_frame:int
    next_ordinal:int
    residual_sha256:str

@dataclass(frozen=True)
class ItchPartialGzipTail:
    source_sha256:str
    decompressed_offset:int
    residual_bytes:int
    next_frame:int
    next_ordinal:int
    residual_sha256:str
    decompressed_sha256:str


@dataclass(frozen=True)
class ItchSourceBoundary:
    decoded_bytes:int
    decoded_sha256:str


class ItchRecovery:
    @classmethod
    def restore(cls,payload,admission,*,resource_budget_bytes=128*1024*1024):
        _validate_image(payload,admission,resource_budget_bytes)
        owner=_checked(_native.restore_itch_checkpoint(payload,admission.artifact_sha256,admission.contract_sha256,admission.implementation_sha256,admission.capture,str(admission.generation),str(resource_budget_bytes)))
        result=cls.__new__(cls);result._owner=owner;result.admission=admission;return result
    @classmethod
    def resume_source(cls,payload,admission,source,source_admission,*,resource_budget_bytes=128*1024*1024):
        owner=cls._source_owner(payload,admission,source,source_admission,resource_budget_bytes,'resume_itch_source')
        return cls._advanced_owner(owner,admission)

    @staticmethod
    def _source_owner(payload,admission,source,source_admission,resource_budget_bytes,method):
        _validate_image(payload,admission,resource_budget_bytes)
        if type(source_admission)is not ItchSourceAdmission:raise ValueError('itch_source_admission_required')
        source_admission.validate()
        if(source_admission.capture,source_admission.generation)!=(admission.capture,admission.generation):raise ValueError('itch_source_scope')
        if type(source)is not bytes or len(source)>MAX_BYTES:raise ValueError('itch_source_byte_budget')
        if hashlib.sha256(source).hexdigest()!=source_admission.source_sha256:raise ValueError('itch_source_digest')
        if not hasattr(_native,method):raise ValueError('itch_source_sdk_streaming_disabled')
        return _checked(getattr(_native,method)(payload,admission.artifact_sha256,admission.contract_sha256,admission.implementation_sha256,admission.capture,str(admission.generation),str(resource_budget_bytes),source,source_admission.source_sha256,str(SOURCE_CONTAINERS.index(source_admission.container)),str(source_admission.first_frame),str(source_admission.first_ordinal)))

    @classmethod
    def resume_bound_source(cls,payload,admission,source,source_admission,*,resource_budget_bytes=128*1024*1024):
        """Resume at a whole frame boundary and retain the exact decoded source receipt."""
        owner,size,sha256=cls._source_owner(payload,admission,source,source_admission,resource_budget_bytes,
                                          'resume_bound_itch_source')
        return cls._advanced_owner(owner,admission),ItchSourceBoundary(int(size),sha256)

    @classmethod
    def _advanced_owner(cls,owner,admission):
        result=cls.__new__(cls)
        result._owner=owner
        result.admission=replace(admission,artifact_sha256=hashlib.sha256(result.checkpoint()).hexdigest())
        return result

    @classmethod
    def resume_partial_binary_source(cls,payload,admission,source,source_admission,*,resource_budget_bytes=128*1024*1024):
        """Resume whole BinaryFile frames and return a receipt for the unfinished frame."""
        owner,receipt=cls._resume_partial_source(payload,admission,source,source_admission,
            resource_budget_bytes,'binary_file','resume_itch_partial_binary_source')
        tail=ItchPartialBinaryTail(source_admission.source_sha256,int(receipt['source_offset']),
            int(receipt['residual_bytes']),int(receipt['next_frame']),int(receipt['next_ordinal']),
            receipt['residual_sha256'])
        return owner,tail

    @classmethod
    def resume_partial_gzip_source(cls,payload,admission,source,source_admission,*,resource_budget_bytes=128*1024*1024):
        """Admit the selected gzip profile and report its unfinished BinaryFile frame."""
        multiple=type(source_admission)is ItchSourceAdmission and source_admission.container=='gzip_members'
        container,native_method=('gzip_members','resume_itch_partial_gzip_members') if multiple else (
            'single_gzip','resume_itch_partial_gzip_source')
        owner,receipt=cls._resume_partial_source(payload,admission,source,source_admission,
            resource_budget_bytes,container,native_method)
        tail=ItchPartialGzipTail(source_admission.source_sha256,int(receipt['decompressed_offset']),
            int(receipt['residual_bytes']),int(receipt['next_frame']),int(receipt['next_ordinal']),
            receipt['residual_sha256'],receipt['decompressed_sha256'])
        return owner,tail

    @classmethod
    def _resume_partial_source(cls,payload,admission,source,source_admission,resource_budget_bytes,
                               required_container,native_method):
        _validate_image(payload,admission,resource_budget_bytes)
        if type(source_admission)is not ItchSourceAdmission:raise ValueError('itch_source_admission_required')
        source_admission.validate()
        if(source_admission.capture,source_admission.generation)!=(admission.capture,admission.generation):
            raise ValueError('itch_source_scope')
        if source_admission.container!=required_container:
            raise ValueError('itch_partial_source_requires_'+required_container)
        if type(source)is not bytes or len(source)>MAX_BYTES:raise ValueError('itch_source_byte_budget')
        if hashlib.sha256(source).hexdigest()!=source_admission.source_sha256:
            raise ValueError('itch_source_digest')
        resume=getattr(_native,native_method,None)
        if resume is None:raise ValueError('itch_source_sdk_streaming_disabled')
        owner,receipt=_checked(resume(payload,admission.artifact_sha256,admission.contract_sha256,
            admission.implementation_sha256,admission.capture,str(admission.generation),
            str(resource_budget_bytes),source,source_admission.source_sha256,
            str(source_admission.first_frame),str(source_admission.first_ordinal)))
        result=cls.__new__(cls)
        result._owner=owner
        result.admission=replace(admission,artifact_sha256=hashlib.sha256(result.checkpoint()).hexdigest())
        return result,receipt

    @classmethod
    def complete_source(cls,payload,admission,source,source_admission,*,resource_budget_bytes=128*1024*1024):
        """Verify and finish one complete supplied container; no terminal V1 image."""
        _validate_image(payload,admission,resource_budget_bytes)
        if type(source_admission)is not ItchSourceAdmission:raise ValueError('itch_source_admission_required')
        source_admission.validate()
        if(source_admission.capture,source_admission.generation)!=(admission.capture,admission.generation):raise ValueError('itch_source_scope')
        if type(source)is not bytes or len(source)>MAX_BYTES:raise ValueError('itch_source_byte_budget')
        if hashlib.sha256(source).hexdigest()!=source_admission.source_sha256:raise ValueError('itch_source_digest')
        if not hasattr(_native,'complete_itch_source'):raise ValueError('itch_source_sdk_streaming_disabled')
        owner=_checked(_native.complete_itch_source(payload,admission.artifact_sha256,admission.contract_sha256,admission.implementation_sha256,admission.capture,str(admission.generation),str(resource_budget_bytes),source,source_admission.source_sha256,str(SOURCE_CONTAINERS.index(source_admission.container)),str(source_admission.first_frame),str(source_admission.first_ordinal)))
        result=ItchSourceCompletion.__new__(ItchSourceCompletion);result._owner=owner;result.original_admission=admission;result.source_admission=source_admission
        if result.status()['finished']is not True or result.status()['input_complete']is not True:raise ValueError('itch_source_incomplete')
        return result
    @classmethod
    def create_completion_capsule(cls,payload,admission,source,source_admission,*,resource_budget_bytes=128*1024*1024):
        _validate_image(payload,admission,resource_budget_bytes)
        if type(source_admission)is not ItchSourceAdmission:raise ValueError('itch_source_admission_required')
        source_admission.validate()
        if(source_admission.capture,source_admission.generation)!=(admission.capture,admission.generation):raise ValueError('itch_source_scope')
        if type(source)is not bytes or len(source)>MAX_BYTES or len(payload)+len(source)+24>MAX_BYTES:raise ValueError('itch_capsule_byte_budget')
        if hashlib.sha256(source).hexdigest()!=source_admission.source_sha256:raise ValueError('itch_source_digest')
        if not hasattr(_native,'encode_itch_completion_capsule'):raise ValueError('itch_source_sdk_streaming_disabled')
        raw=_checked(_native.encode_itch_completion_capsule(payload,admission.artifact_sha256,admission.contract_sha256,admission.implementation_sha256,admission.capture,str(admission.generation),str(resource_budget_bytes),source,source_admission.source_sha256,str(SOURCE_CONTAINERS.index(source_admission.container)),str(source_admission.first_frame),str(source_admission.first_ordinal)))
        return raw,ItchCompletionAdmission(hashlib.sha256(raw).hexdigest(),admission,source_admission)
    @classmethod
    def restore_completion_capsule(cls,payload,admission,*,resource_budget_bytes=128*1024*1024):
        if type(admission)is not ItchCompletionAdmission:raise ValueError('itch_capsule_admission')
        admission.validate()
        if type(payload)is not bytes or not 82<=len(payload)<=MAX_BYTES:raise ValueError('itch_capsule_byte_budget')
        if type(resource_budget_bytes)is not int or not 0<resource_budget_bytes<=256*1024*1024:raise ValueError('itch_resource_budget')
        if hashlib.sha256(payload).hexdigest()!=admission.capsule_sha256:raise ValueError('itch_capsule_digest')
        if not hasattr(_native,'restore_itch_completion_capsule'):raise ValueError('itch_source_sdk_streaming_disabled')
        a=admission.checkpoint;s=admission.source
        owner=_checked(_native.restore_itch_completion_capsule(payload,admission.capsule_sha256,a.artifact_sha256,a.contract_sha256,a.implementation_sha256,a.capture,str(a.generation),str(resource_budget_bytes),s.source_sha256,str(SOURCE_CONTAINERS.index(s.container)),str(s.first_frame),str(s.first_ordinal)))
        result=ItchSourceCompletion.__new__(ItchSourceCompletion);result._owner=owner;result.original_admission=a;result.source_admission=s
        return result
    @classmethod
    def persist_checkpoint_file(cls,path,payload,admission,*,resource_budget_bytes=128*1024*1024):
        """Publish native-admitted active checkpoint bytes to a new absolute POSIX path."""
        cls.restore(payload,admission,resource_budget_bytes=resource_budget_bytes)
        from .itch_capsule_store import _persist_verified_checkpoint
        return _persist_verified_checkpoint(path,payload,admission.artifact_sha256)

    @classmethod
    def restore_checkpoint_file(cls,path,admission,*,resource_budget_bytes=128*1024*1024):
        """Open a pinned active image and independently admit it through the native SDK."""
        if type(admission)is not ItchAdmission:raise ValueError('itch_admission_required')
        admission.validate()
        if type(resource_budget_bytes)is not int or not 0<resource_budget_bytes<=256*1024*1024:
            raise ValueError('itch_resource_budget')
        from .itch_capsule_store import _read_checkpoint
        payload,receipt=_read_checkpoint(path,admission.artifact_sha256)
        owner=cls.restore(payload,admission,resource_budget_bytes=resource_budget_bytes)
        owner.persistence_receipt=receipt
        return owner

    @classmethod
    def persist_completion_capsule_file(cls,path,payload,admission,*,resource_budget_bytes=128*1024*1024):
        """POSIX create-only publication after full independent native admission.

        No trust metadata is persisted or inferred from the destination. Returned
        fsync flags record completed syscalls, not physical hardware durability.
        """
        cls.restore_completion_capsule(payload,admission,resource_budget_bytes=resource_budget_bytes)
        from .itch_capsule_store import _persist_verified_capsule
        return _persist_verified_capsule(path,payload,admission.capsule_sha256)
    @classmethod
    def restore_completion_capsule_file(cls,path,admission,*,resource_budget_bytes=128*1024*1024):
        """Read bounded pinned-directory bytes, then revalidate native/source trust."""
        if type(admission)is not ItchCompletionAdmission:raise ValueError('itch_capsule_admission')
        admission.validate()
        if type(resource_budget_bytes)is not int or not 0<resource_budget_bytes<=256*1024*1024:raise ValueError('itch_resource_budget')
        if not hasattr(_native,'restore_itch_completion_capsule'):raise ValueError('itch_source_sdk_streaming_disabled')
        from .itch_capsule_store import _read_capsule
        payload,receipt=_read_capsule(path,admission.capsule_sha256)
        result=cls.restore_completion_capsule(payload,admission,resource_budget_bytes=resource_budget_bytes)
        result.persistence_receipt=receipt
        return result
    def describe(self):return _checked(self._owner.describe())
    def book(self,index,depth=10):
        if type(index)is not int or not 0<=index<2 or type(depth)is not int or not 1<=depth<=4096:raise ValueError('itch_book_depth')
        return _checked(self._owner.book(str(index),str(depth)))
    @classmethod
    def migrate(cls,payload,admission,target_implementation_sha256):
        # Explicitly validate old state with the current native implementation,
        # re-encode unchanged configuration/capture/generation under the target
        # code identity,then validate again. No unknown schema conversion or claim
        # of historical algorithm equivalence. The source payload stays unchanged.
        target=replace(admission,implementation_sha256=target_implementation_sha256);target.validate()
        source=cls.restore(payload,admission)
        raw=_checked(source._owner.rebind(target_implementation_sha256))
        target=replace(target,artifact_sha256=hashlib.sha256(raw).hexdigest())
        restored=cls.restore(raw,target)
        if restored.canonical()!=source.canonical()or restored.describe()!=source.describe()or restored.status()['source_records']!=source.status()['source_records']:
            raise ValueError('itch_migration_state_changed')
        return raw,target
    def status(self):return _checked(self._owner.status())
    def canonical(self):return _checked(self._owner.canonical())
    def checkpoint(self):return _checked(self._owner.checkpoint())
    def process(self,payload,*,frame_offset,ordinal):
        for v in(frame_offset,ordinal):
            if type(v)is not int or not 0<=v<=2**64-1:raise ValueError('itch_source_position')
        return _checked(self._owner.process(payload,str(frame_offset),str(ordinal)))

class ItchSourceCompletion:
    """Read-only completed reconstruction. Original checkpoint metadata stays separate.

    Supplied source/container completion is not independent exchange completeness.
    Finished-owner checkpoint serialization and further processing remain unsupported.
    """
    def status(self):return _checked(self._owner.completion())
    def describe(self):return _checked(self._owner.describe())
    def canonical(self):return _checked(self._owner.canonical())
    def book(self,index,depth=10):
        if type(index)is not int or not 0<=index<2 or type(depth)is not int or not 1<=depth<=4096:raise ValueError('itch_book_depth')
        return _checked(self._owner.book(str(index),str(depth)))
