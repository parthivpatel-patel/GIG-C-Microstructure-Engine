"""Private atomic native/source checkpoints for authored typed events only.

Not an IEX adapter,observed initialization authority or automatic network worker.
Hot restore loads full native state;historical events are not reapplied to the book.
"""
import copy,hashlib,json,os,re,sqlite3,stat,threading
from contextlib import contextmanager
from pathlib import Path
from functools import lru_cache
import gig_microstructure as gig
from terminal.verification.artifacts import decode

MAX_PAYLOAD=8*1024*1024
MAX_RECORD=65536
APP_ID=1195984721

class RecoveryError(ValueError):pass

def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def hashed(value):return hashlib.sha256(encoded(value)).hexdigest()
def hex64(v):return type(v)is str and bool(re.fullmatch('[a-f0-9]{64}',v))
def integer(v):return type(v)is int and 0<=v<2**53-1

@lru_cache(maxsize=1)
def native_binary_identity():
    path=Path(gig._native.__file__)
    if not 1<=path.stat().st_size<=256*1024*1024:raise RecoveryError('native_binary_identity_budget')
    digest=hashlib.sha256()
    with path.open('rb')as stream:
        while block:=stream.read(1024*1024):digest.update(block)
    return digest.hexdigest()


def authored_record(source,index,event,*,generation=None,capture_session=None):
    event=gig.validate_document(event).to_dict()
    return {'capture_index':index,'generation':source['generation']if generation is None else generation,'capture_session':source['capture_session']if capture_session is None else capture_session,'source_sha256':hashed(event),'event':event}

class NativeSourceRecovery:
    """One serialized owner;CAS rejects concurrent/stale writers. No startup side effects outside a private SQLite file."""
    def __init__(self,directory,*,rules,config,limits,source,implementation_sha256,resource_budget_bytes='33554432',before_commit=None,after_commit=None):
        if not hasattr(gig._native,'restore_replay'):raise RecoveryError('native_hot_checkpoint_binding_required')
        if not hex64(implementation_sha256):raise RecoveryError('implementation_identity_required')
        if type(source)is not dict or set(source)!={'identity','capture_session','generation','first_capture','initialization','origin'}:raise RecoveryError('source_contract')
        if type(source['identity'])is not str or not re.fullmatch('[A-Za-z0-9._:-]{1,64}',source['identity'])or type(source['capture_session'])is not str or not re.fullmatch('[a-f0-9]{32}',source['capture_session']):raise RecoveryError('source_identity')
        if not integer(source['generation'])or not integer(source['first_capture'])or source['initialization']!='AUTHORED_COMPLETE_EMPTY'or source['origin']!='HISTORICAL_SYNTHETIC' or config.get('initial_state')!='1':raise RecoveryError('complete_authored_initialization_required')
        if type(resource_budget_bytes)is not str or not resource_budget_bytes.isdecimal()or not 1048576<=int(resource_budget_bytes)<=134217728:raise RecoveryError('native_resource_budget')
        self.contract=copy.deepcopy({'schema':'gig.native_source.contract.v1','rules':rules,'config':config,'limits':limits,'source':source,'implementation_sha256':implementation_sha256,'native_binary_sha256':native_binary_identity(),'resource_budget_bytes':resource_budget_bytes})
        self.contract_sha256=hashed(self.contract);self.lock=threading.RLock();self.before_commit=before_commit;self.after_commit=after_commit;self.uncertain=False;self.local_reason=None;self._digest=None
        root=Path(directory).absolute()
        if any(p.is_symlink()for p in (root,*root.parents)):raise RecoveryError('checkpoint_symlink')
        root.mkdir(parents=True,exist_ok=True,mode=0o700);info=root.stat()
        if info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:raise RecoveryError('checkpoint_private_directory')
        self.path=root/'native-source.sqlite3';fd=os.open(self.path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            info=os.fstat(fd);new=info.st_size==0
            if not stat.S_ISREG(info.st_mode)or info.st_nlink!=1 or info.st_uid!=os.getuid()or stat.S_IMODE(info.st_mode)&0o077:raise RecoveryError('checkpoint_private_file')
        finally:os.close(fd)
        with self._connect()as db:
            if new:
                db.execute('CREATE TABLE checkpoint(singleton INTEGER PRIMARY KEY CHECK(singleton=1),payload BLOB NOT NULL,digest TEXT NOT NULL)');db.execute('PRAGMA user_version=1');db.execute(f'PRAGMA application_id={APP_ID}');db.commit()
            elif db.execute('PRAGMA user_version').fetchone()[0]!=1 or db.execute('PRAGMA application_id').fetchone()[0]!=APP_ID:raise RecoveryError('checkpoint_database_contract')
            saved=self._read(db)
        if saved is None:
            if not new:raise RecoveryError('checkpoint_missing_committed_state')
            native=gig.Replay(rules,config,limits=limits,resource_budget_bytes=resource_budget_bytes)
            state={'schema':'gig.native_source.state.v1','contract_sha256':self.contract_sha256,'generation':source['generation'],'capture_session':source['capture_session'],'capture_index':None,'prefix_sha256':'0'*64,'recent':[],'state':'READY','diagnostic':None,'image':native.checkpoint(),'canonical':native.canonical()}
            self._publish(state,native,initial=True)
        else:
            state,digest=saved;native=self._restore(state);self._state=state;self._native=native;self._digest=digest
    @contextmanager
    def _connect(self):
        if self.path.stat().st_size>16*1024*1024:raise RecoveryError('checkpoint_disk_budget')
        db=sqlite3.connect(self.path,timeout=2)
        try:
            if db.execute('PRAGMA page_size').fetchone()[0]!=4096:raise RecoveryError('checkpoint_page_size')
            db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA secure_delete=ON');db.execute('PRAGMA max_page_count=4096')
            yield db
        except sqlite3.Error:raise RecoveryError('checkpoint_storage_failure')from None
        finally:db.close()
    def _read(self,db):
        n=db.execute('SELECT count(*) FROM (SELECT 1 FROM checkpoint LIMIT 2)').fetchone()[0]
        if n==0:return None
        if n!=1 or db.execute("SELECT count(*) FROM checkpoint WHERE typeof(singleton)!='integer' OR singleton!=1 OR typeof(payload)!='blob' OR length(payload)>? OR typeof(digest)!='text' OR length(digest)!=64",(MAX_PAYLOAD,)).fetchone()[0]:raise RecoveryError('checkpoint_payload_budget')
        raw,digest=db.execute('SELECT payload,digest FROM checkpoint WHERE singleton=1').fetchone()
        if not hex64(digest)or hashlib.sha256(raw).hexdigest()!=digest:raise RecoveryError('checkpoint_digest')
        value=decode(raw)
        if set(value)!={'schema','contract_sha256','generation','capture_session','capture_index','prefix_sha256','recent','state','diagnostic','image','canonical'}or value['schema']!='gig.native_source.state.v1'or value['contract_sha256']!=self.contract_sha256:raise RecoveryError('checkpoint_source_contract')
        if not integer(value['generation'])or type(value['capture_session'])is not str or not re.fullmatch('[a-f0-9]{32}',value['capture_session'])or value['capture_index']is not None and not integer(value['capture_index'])or not hex64(value['prefix_sha256']):raise RecoveryError('checkpoint_source_boundary')
        if value['state']not in ('READY','RECOVERY_REQUIRED')or value['diagnostic']is not None and (type(value['diagnostic'])is not str or not re.fullmatch('[A-Za-z0-9_.:-]{1,128}',value['diagnostic'])):raise RecoveryError('checkpoint_recovery_state')
        recent=value['recent']
        if type(recent)is not list or len(recent)>32:raise RecoveryError('checkpoint_dedup_budget')
        keys=set()
        for row in recent:
            if type(row)is not dict or set(row)!={'capture_session','generation','capture_index','sha256'}or type(row['capture_session'])is not str or not re.fullmatch('[a-f0-9]{32}',row['capture_session'])or not integer(row['generation'])or not integer(row['capture_index'])or not hex64(row['sha256']):raise RecoveryError('checkpoint_dedup_record')
            key=(row['capture_session'],row['generation'],row['capture_index'])
            if key in keys:raise RecoveryError('checkpoint_dedup_conflict')
            keys.add(key)
        if value['capture_index']is None:
            if recent or value['prefix_sha256']!='0'*64:raise RecoveryError('checkpoint_empty_boundary')
        elif not recent or (recent[-1]['capture_session'],recent[-1]['generation'],recent[-1]['capture_index'])!=(value['capture_session'],value['generation'],value['capture_index']):raise RecoveryError('checkpoint_recent_boundary')
        return value,digest
    def _restore(self,state):
        if type(state['canonical'])is not str or len(state['canonical'].encode())>MAX_PAYLOAD:raise RecoveryError('checkpoint_canonical_budget')
        c=self.contract
        return gig.Replay.restore_checkpoint(state['image'],c['rules'],c['config'],c['limits'],state['canonical'],resource_budget_bytes=c['resource_budget_bytes'])
    def _publish(self,state,native,*,initial=False):
        raw=encoded(state)
        if len(raw)>MAX_PAYLOAD:raise RecoveryError('checkpoint_payload_budget')
        digest=hashlib.sha256(raw).hexdigest();stage='prepare'
        with self._connect()as db:
            try:
                db.execute('BEGIN IMMEDIATE');prior=self._read(db)
                if (prior is not None if initial else prior is None or prior[1]!=self._digest):raise RecoveryError('checkpoint_stale_writer')
                db.execute('INSERT OR REPLACE INTO checkpoint VALUES(1,?,?)',(raw,digest))
                if self.before_commit:self.before_commit()
                stage='commit';db.commit();stage='published'
                if self.after_commit:self.after_commit()
            except BaseException as exc:
                if db.in_transaction:db.rollback()
                if stage in ('commit','published'):self.uncertain=True;self.local_reason='checkpoint_publication_uncertain'
                elif isinstance(exc,RecoveryError)and str(exc)=='checkpoint_stale_writer':self.uncertain=True;self.local_reason='stale_checkpoint_owner'
                raise
        # All fallible preparation and durable publication precede owner replacement.
        self._state,self._native,self._digest=state,native,digest
    def _admit(self,record):
        if type(record)is not dict or set(record)!={'capture_index','generation','capture_session','source_sha256','event'}:raise RecoveryError('typed_source_record')
        if not integer(record['capture_index'])or not integer(record['generation'])or type(record['capture_session'])is not str or not re.fullmatch('[a-f0-9]{32}',record['capture_session']):raise RecoveryError('typed_source_boundary')
        raw=encoded(record['event'])
        if len(raw)>MAX_RECORD or not hex64(record['source_sha256'])or hashlib.sha256(raw).hexdigest()!=record['source_sha256']:raise RecoveryError('typed_source_integrity')
        doc=gig.validate_document(record['event']).to_dict()
        if doc['schema']!='gig.event'or doc['data']['metadata']['provenance']['origin']!={'reason':'0','value':'0'}:raise RecoveryError('authored_native_profile_only')
        return doc,hashed(record)
    def _blocked(self,reason):
        state={**self._state,'state':'RECOVERY_REQUIRED','diagnostic':reason}
        try:self._publish(state,self._native)
        except BaseException:self.uncertain=True;self.local_reason='recovery_diagnostic_not_persisted';raise
        return {'status':'RECOVERY_REQUIRED','reason':reason,'committed':False}
    def _duplicate(self,record,digest):
        key=(record['capture_session'],record['generation'],record['capture_index'])
        for row in self._state['recent']:
            if (row['capture_session'],row['generation'],row['capture_index'])==key:return row['sha256']==digest
        return None
    def _commit_event(self,record,doc,digest,*,recovery=False):
        candidate=self._restore(self._state)
        try:
            if recovery:candidate.recover(doc)
            else:candidate.apply(doc)
        except gig.EngineError as exc:
            if exc.code_name in ('resource_exhausted','capacity'):raise
            return self._blocked('native:'+exc.code_name)
        state={**self._state,'generation':record['generation'],'capture_session':record['capture_session'],'capture_index':record['capture_index'],'prefix_sha256':hashlib.sha256(bytes.fromhex(self._state['prefix_sha256'])+bytes.fromhex(digest)).hexdigest(),'recent':(self._state['recent']+[{'capture_session':record['capture_session'],'generation':record['generation'],'capture_index':record['capture_index'],'sha256':digest}])[-32:],'state':'READY','diagnostic':None,'image':candidate.checkpoint(),'canonical':candidate.canonical()}
        self._publish(state,candidate)
        return {'status':'COMMITTED','committed':True,'capture_index':record['capture_index'],'checkpoint_sha256':self._digest}
    def apply(self,record):
        with self.lock:
            if self.uncertain:raise RecoveryError('checkpoint_publication_uncertain_reopen_required')
            doc,digest=self._admit(record)
            if record['generation']<self._state['generation']:return {'status':'STALE_GENERATION_REJECTED','committed':False}
            duplicate=self._duplicate(record,digest)
            if duplicate is True:return {'status':'DUPLICATE_SUPPRESSED','committed':False}
            if duplicate is False:return self._blocked('duplicate_conflict')
            if self._state['state']!='READY':raise RecoveryError('complete_resynchronization_required')
            if record['generation']!=self._state['generation']or record['capture_session']!=self._state['capture_session']:return self._blocked('generation_or_capture_transition_requires_snapshot')
            expected=self.contract['source']['first_capture']if self._state['capture_index']is None else self._state['capture_index']+1
            if record['capture_index']!=expected:return self._blocked('capture_gap_or_outside_dedup_window')
            return self._commit_event(record,doc,digest)
    def resynchronize(self,record):
        with self.lock:
            if self.uncertain:raise RecoveryError('checkpoint_publication_uncertain_reopen_required')
            doc,digest=self._admit(record);duplicate=self._duplicate(record,digest)
            if duplicate is True:return {'status':'DUPLICATE_SUPPRESSED','committed':False}
            if record['generation']<=self._state['generation']:raise RecoveryError('resynchronization_requires_new_generation')
            if doc['data']['payload']['tag']!='6':raise RecoveryError('complete_order_snapshot_required')
            return self._commit_event(record,doc,digest,recovery=True)
    def status(self):
        return {'schema':'gig.native_source.status.v1','state':'PUBLICATION_UNCERTAIN'if self.uncertain else self._state['state'],'needs_recovery':self.uncertain or self._state['state']!='READY','generation':self._state['generation'],'capture_index':self._state['capture_index'],'capture_session':self._state['capture_session'],'diagnostic':self.local_reason or self._state['diagnostic'],'checkpoint_sha256':self._digest,'prefix_sha256':self._state['prefix_sha256'],'native_journal_records':self._native.status()['journal_size'],'origin':'HISTORICAL_SYNTHETIC','source_profile':'AUTHORED_TYPED_NATIVE_V1','provider_connected':False,'order_submission':False,'hot_restore':'Full native state import,not historical book-event reapplication','limits':'8MiB payload,16MiB database,up to16MiB rollback journal,32dedup identities;source/authenticity not established by hashes'}
    def snapshot(self,depth='10'):
        if self.uncertain or self._state['state']!='READY':raise RecoveryError('unhealthy_source_snapshot_unavailable')
        return self._native.snapshot(depth).to_dict()
    def accepted_canonical(self):return self._state['canonical']
