"""Owner-private bounded SQLite backup/restore. No caller file paths,overwrite or network."""
import hashlib,json,os,sqlite3,tempfile,time,shutil,stat,math
from pathlib import Path
from .history_store import MAX_PAYLOAD,MAX_SNAPSHOTS,RETENTION_SECONDS,verify


def _private(path):
    s=path.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_uid!=os.getuid() or s.st_mode&0o077 or s.st_size>32*1024*1024:raise ValueError('history_backup_private_file')


def _copy(source,target):
    deadline=time.monotonic()+5
    def progress(status,left,total):
        if (status!=sqlite3.SQLITE_DONE and time.monotonic()>deadline) or total>8192:raise ValueError('history_backup_copy_budget')
    source.backup(target,pages=64,progress=progress,sleep=.05)


def _validate(db,store):
    if db.execute('PRAGMA page_size').fetchone()!=(4096,) or db.execute('PRAGMA quick_check').fetchone()!=('ok',) or db.execute('PRAGMA user_version').fetchone()!=(1,) or db.execute('PRAGMA application_id').fetchone()!=(1195984712,):raise ValueError('history_backup_database')
    if db.execute('SELECT count(*) FROM snapshots').fetchone()[0]>MAX_SNAPSHOTS or db.execute('SELECT count(*) FROM snapshots WHERE length(payload)>?',(MAX_PAYLOAD,)).fetchone()[0]:raise ValueError('history_backup_payload_budget')
    rows=db.execute('SELECT revision,symbol,timeframe,created,payload FROM snapshots').fetchall()
    for revision,symbol,timeframe,created,raw in rows:
        if type(raw) is not bytes or hashlib.sha256(raw).hexdigest()!=revision:raise ValueError('history_backup_revision')
        core=verify(json.loads(raw))
        if (symbol,timeframe)!=(core['symbol'],core['timeframe']) or type(created) not in (int,float) or not math.isfinite(created) or not 0<=created<=store.clock()+1:raise ValueError('history_backup_index_metadata')
        if core['source']['origin']!='HISTORICAL_SYNTHETIC' and not store.allow_observed:raise ValueError('history_observed_retention_not_approved')
    return len(rows)


def _staging(store):
    if shutil.disk_usage(store.path.parent).free<128*1024*1024:raise ValueError('history_backup_free_disk_budget')
    fd,name=tempfile.mkstemp(prefix='.history-stage-',suffix='.sqlite3',dir=store.path.parent);os.close(fd)
    return Path(name)


def backup(store):
    with store.lock:
        final=store.path.parent/'history.backup.sqlite3';manifest=store.path.parent/'history.backup.json'
        if final.exists() or manifest.exists():raise ValueError('history_backup_exists_delete_explicitly')
        stage=_staging(store)
        try:
            with store.connect() as source:
                count=_validate(source,store)
                target=sqlite3.connect(stage)
                try:
                    _copy(source,target);count=_validate(target,store)
                finally:target.close()
            _private(stage);raw=stage.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            # link is atomic no-replace;an existing backup is never overwritten.
            os.link(stage,final);stage.unlink()
            record={'schema':'gig.history.backup.v1','sha256':digest,'bytes':len(raw),'revisions':count,'database_version':1}
            fd=os.open(manifest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'w') as f:json.dump(record,f,sort_keys=True);f.flush();os.fsync(f.fileno())
            return record
        finally:
            if stage.exists():stage.unlink()


def restore(store):
    with store.lock:
        source_path=store.path.parent/'history.backup.sqlite3';manifest=store.path.parent/'history.backup.json'
        _private(source_path);_private(manifest)
        if manifest.stat().st_size>4096:raise ValueError('history_backup_manifest_budget')
        record=json.loads(manifest.read_bytes());raw=source_path.read_bytes()
        if record.get('schema')!='gig.history.backup.v1' or record.get('sha256')!=hashlib.sha256(raw).hexdigest() or record.get('bytes')!=len(raw):raise ValueError('history_backup_digest')
        stage=_staging(store)
        try:
            original=sqlite3.connect(source_path.as_uri()+'?mode=ro',uri=True);candidate=sqlite3.connect(stage)
            try:
                _validate(original,store);_copy(original,candidate)
                candidate.execute('PRAGMA secure_delete=ON');candidate.execute('DELETE FROM snapshots WHERE created<?',(store.clock()-RETENTION_SECONDS,));candidate.commit()
                count=_validate(candidate,store)
                # SQLite backup publication uses its destination write transaction;
                # no path replacement of a live database/connection is performed.
                with store.connect() as destination:_copy(candidate,destination)
            finally:original.close();candidate.close()
            return {'schema':'gig.history.restore.v1','restored_revisions':count,'source_backup_sha256':record['sha256'],'policy':'expired rows excluded;observed retention gates rechecked'}
        finally:
            if stage.exists():stage.unlink()


def delete_backup(store):
    with store.lock:
        for name in ('history.backup.json','history.backup.sqlite3'):
            path=store.path.parent/name
            if path.exists():_private(path);path.unlink()
        return {'schema':'gig.history.backup.v1','deleted':True}
