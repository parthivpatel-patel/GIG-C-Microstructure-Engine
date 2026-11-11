"""Bounded version-1 full ITCH recovery. No providers,application startup or replay.

Admission metadata must be retained independently of an untrusted checkpoint.
A digest inside the checkpoint is not authentication. Automatic schema/code or
capture-generation migration is intentionally unsupported.
"""
import hashlib,re
from dataclasses import dataclass
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

class ItchRecovery:
    @classmethod
    def restore(cls,payload,admission,*,resource_budget_bytes=128*1024*1024):
        if type(admission)is not ItchAdmission:raise ValueError('itch_admission_required')
        admission.validate()
        if type(payload)is not bytes or not 56<=len(payload)<=MAX_BYTES:raise ValueError('itch_byte_budget')
        if type(resource_budget_bytes)is not int or not 0<resource_budget_bytes<=256*1024*1024:raise ValueError('itch_resource_budget')
        if hashlib.sha256(payload).hexdigest()!=admission.artifact_sha256:raise ValueError('itch_artifact_digest')
        owner=_checked(_native.restore_itch_checkpoint(payload,admission.artifact_sha256,admission.contract_sha256,admission.implementation_sha256,admission.capture,str(admission.generation),str(resource_budget_bytes)))
        result=cls.__new__(cls);result._owner=owner;result.admission=admission;return result
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
        from dataclasses import replace
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
