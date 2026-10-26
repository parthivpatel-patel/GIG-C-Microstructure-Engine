"""Opt-in private SQLite snapshots:bounded immutable revisions,not an exchange archive."""
import hashlib,json,os,re,sqlite3,stat,time,threading
from pathlib import Path
from contextlib import contextmanager
from .history import HistorySource,normalize

MAX_SNAPSHOTS=32
MAX_PAYLOAD=512*1024
RETENTION_SECONDS=7*86400


def canonical(core):
    return json.dumps(core,sort_keys=True,separators=(',',':')).encode()


def verify(value):
    # Rebuild the exact canonical core;never trust a supplied digest/extra field.
    if type(value) is not dict:raise ValueError('history_storage_contract')
    if type(value.get('source')) is not dict or len(value['source'])!=9 or type(value.get('bars')) is not list or len(value['bars'])>256:raise ValueError('history_storage_budget')
    source=HistorySource(**value['source']);rows=[]
    for row in value['bars']:
        rows.append({k:row[k] for k in ('timestamp','open','high','low','close','volume')})
    if type(value.get('page_count')) is not int or not 1<=value['page_count']<=4 or type(value.get('source_sha256')) is not list or len(value['source_sha256'])!=value['page_count'] or any(type(v) is not str or not re.fullmatch('[0-9a-f]{64}',v) for v in value['source_sha256']):raise ValueError('history_storage_page_metadata')
    core=normalize(value['symbol'],value['timeframe'],[{'bars':rows,'sha256':value['source_sha256'][0]}],source,has_more=value['has_more'])
    core['page_count']=value['page_count'];core['source_sha256']=list(value['source_sha256'])
    del core['canonical_sha256'];core['canonical_sha256']=hashlib.sha256(canonical(core)).hexdigest()
    for key in core:
        if value.get(key)!=core[key]:raise ValueError('history_storage_integrity')
    return core


class HistoryStore:
    def __init__(self,directory,*,allow_observed=False,clock=time.time):
        if type(allow_observed) is not bool:raise ValueError('history_observed_retention_boolean_required')
        self.lock=threading.RLock()
        self.clock=clock;self.allow_observed=allow_observed
        root=Path(directory).absolute()
        if any(p.is_symlink() for p in (root,*root.parents)):raise ValueError('history_storage_symlink')
        root.mkdir(parents=True,exist_ok=True,mode=0o700)
        info=root.stat()
        if info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)&0o077:raise ValueError('history_storage_private_directory_required')
        self.path=root/'history.sqlite3'
        fd=os.open(self.path,os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
        try:
            s=os.fstat(fd)
            if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)&0o077:raise ValueError('history_storage_private_file_required')
        finally:os.close(fd)
        with self.connect() as db:
            db.execute('PRAGMA max_page_count=8192') # 32MiB at4096-byte pages
            db.execute('CREATE TABLE IF NOT EXISTS snapshots(revision TEXT PRIMARY KEY,symbol TEXT,timeframe TEXT,created REAL,payload BLOB)')
            version=db.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0,1):raise ValueError('history_storage_schema_version')
            db.execute('PRAGMA application_id=1195984712')
            db.execute('PRAGMA user_version=1')
            db.execute('DELETE FROM snapshots WHERE created<?',(self.clock()-RETENTION_SECONDS,))
    @contextmanager
    def connect(self):
        with self.lock:
            with self._connect() as db:yield db
    @contextmanager
    def _connect(self):
        if self.path.stat().st_size>32*1024*1024:raise ValueError('history_storage_disk_budget')
        db=sqlite3.connect(self.path,timeout=2)
        try:
            version=db.execute('PRAGMA user_version').fetchone()[0]
            app=db.execute('PRAGMA application_id').fetchone()[0]
            tables=db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
            if version not in (0,1) or app not in (0,1195984712) or (app==0 and tables) or db.execute('PRAGMA page_size').fetchone()[0]!=4096:raise ValueError('history_storage_schema_version')
            db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=FULL')
            db.execute('PRAGMA secure_delete=ON');db.execute('PRAGMA max_page_count=8192')
            with db:yield db
        finally:db.close()
    def save(self,value):
        core=verify(value)
        if core['source']['origin']!='HISTORICAL_SYNTHETIC' and not self.allow_observed:raise ValueError('history_observed_retention_not_approved')
        raw=canonical(core)
        if type(raw) is not bytes or len(raw)>MAX_PAYLOAD:raise ValueError('history_storage_payload_budget')
        revision=hashlib.sha256(raw).hexdigest();now=self.clock()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM snapshots WHERE created<?',(now-RETENTION_SECONDS,))
            existing=db.execute('SELECT payload FROM snapshots WHERE revision=?',(revision,)).fetchone()
            if existing is not None and existing[0]!=raw:raise ValueError('history_storage_revision_conflict')
            if existing is None:
                if db.execute('SELECT count(*) FROM snapshots').fetchone()[0]>=MAX_SNAPSHOTS:raise ValueError('history_storage_capacity_delete_explicitly')
                db.execute('INSERT INTO snapshots VALUES(?,?,?,?,?)',(revision,core['symbol'],core['timeframe'],now,raw))
        return {'revision':revision,'record_count':core['record_count'],'retention_seconds':RETENTION_SECONDS}
    def read(self,revision):
        self.key(revision)
        with self.connect() as db:
            row=db.execute('SELECT created,payload FROM snapshots WHERE revision=?',(revision,)).fetchone()
        if row is None or row[0]<self.clock()-RETENTION_SECONDS:raise ValueError('history_revision_missing_or_expired')
        raw=row[1]
        if type(raw) is not bytes or len(raw)>MAX_PAYLOAD or hashlib.sha256(raw).hexdigest()!=revision:raise ValueError('history_storage_digest')
        value=json.loads(raw);verify(value)
        if value['source']['origin']!='HISTORICAL_SYNTHETIC' and not self.allow_observed:raise ValueError('history_observed_retention_not_approved')
        return value
    def list(self):
        with self.connect() as db:
            rows=db.execute('SELECT revision,symbol,timeframe,created FROM snapshots WHERE created>=? ORDER BY created DESC,revision LIMIT 32',(self.clock()-RETENTION_SECONDS,)).fetchall()
        return [{'revision':r,'symbol':s,'timeframe':t,'retained_at_unix':c} for r,s,t,c in rows]
    def delete(self,revision):
        self.key(revision)
        with self.connect() as db:db.execute('DELETE FROM snapshots WHERE revision=?',(revision,))
    @staticmethod
    def key(value):
        if type(value) is not str or not re.fullmatch('[0-9a-f]{64}',value):raise ValueError('history_revision')


def configured(environment):
    if environment.get('GIG_HISTORY_STORE_ENABLED')!='1':return None
    directory=environment.get('GIG_HISTORY_STORE_DIRECTORY')
    if not directory:raise ValueError('history_storage_directory_required')
    return HistoryStore(directory,allow_observed=environment.get('GIG_HISTORY_OBSERVED_RETENTION_APPROVED')=='1')
