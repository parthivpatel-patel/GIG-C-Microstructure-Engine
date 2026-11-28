"""Read-only Historical Replay view of an explicitly pinned completed ITCH source."""
import dataclasses
from gig_microstructure.itch_recovery import ItchAdmission,ItchCompletionAdmission,ItchRecovery,ItchSourceAdmission
from terminal.itch_product import ItchProduct,ItchProductError,digest,read_private
from terminal.verification.artifacts import decode

DATASET='itch-completed-v1'


class ItchCompletedProduct(ItchProduct):
    def __init__(self,owner,admission):
        self.owner=owner
        self.complete_admission=admission
        self.description=owner.describe()
        self.minimum=int(owner.status()['source_records'])
        self.records=()
        self.offset=0
        self.selected_book=0
        self.speed=1
        self.playing=False
        self.source_history=[]
        owner.book(self.selected_book,self.depth)

    def _view_status(self):
        checkpoint=self.complete_admission.checkpoint
        return {**self.owner.status(),'capture':checkpoint.capture,'generation':str(checkpoint.generation)}

    def seek(self,position,**_):
        if type(position)is not int or position!=self.minimum:
            raise ItchProductError('itch_completed_source_position_fixed')

    def step(self,**_):
        self.playing=False
        return False

    def capture(self):
        raise ItchProductError('itch_completed_source_checkpoint_unsupported')

    def control(self,action,value=None):
        if action in ('book','seek','restart','pause','step'):
            super().control(action,value)
        else:
            raise ItchProductError('itch_completed_source_read_only')

    def view(self,session):
        result=super().view(session)
        a=self.complete_admission
        result['feed'].update(state='COMPLETE',reason='End of the supplied authored ITCH container.',capture_complete=True)
        result['provenance'].update(dataset=DATASET,session_segment=a.capsule_sha256,
            completed_source={'capsule_sha256':a.capsule_sha256,'source_sha256':a.source.source_sha256,
                'checkpoint_sha256':a.checkpoint.artifact_sha256,'container':a.source.container,
                'source_records':str(self.minimum),'exchange_completeness':False})
        result['capabilities'].update(itch_checkpoint_available=False,itch_completion_available=True,itch_source_finished=True)
        return result


def load_completed(capsule_path,admission_path,expected_admission_sha256):
    if not all(type(v)is str and v for v in (capsule_path,admission_path,expected_admission_sha256)):
        raise ItchProductError('itch_completed_source_pinned_configuration_required')
    raw=read_private(admission_path,limit=8192)
    if digest(raw)!=expected_admission_sha256:
        raise ItchProductError('itch_completed_source_admission_digest')
    packet=decode(raw,numeric_policy='exact-integer')
    if type(packet)is not dict or set(packet)!={'capsule_sha256','checkpoint','source'}:
        raise ItchProductError('itch_completed_source_admission')
    def typed(cls,fields):
        if type(fields)is not dict or set(fields)!={field.name for field in dataclasses.fields(cls)}:
            raise ItchProductError('itch_completed_source_admission')
        return cls(**fields)
    admission=ItchCompletionAdmission(packet['capsule_sha256'],typed(ItchAdmission,packet['checkpoint']),
                                      typed(ItchSourceAdmission,packet['source']))
    admission.validate()
    owner=ItchRecovery.restore_completion_capsule_file(capsule_path,admission)
    return ItchCompletedProduct(owner,admission)
