"""Opt-in private bounded SQLite observation ledger;never a hot/live book snapshot."""
import os,stat,sqlite3,json,hashlib,time,re,threading
from pathlib import Path
from contextlib import contextmanager
MAX_BYTES=16*1024*1024
class ObservationStore:
 def __init__(self,directory,*,allow_observed=False,permission_reference=None,retention_seconds=3600,clock=time.time,before_commit=None):
  if type(allow_observed) is not bool or type(retention_seconds) is not int or not 1<=retention_seconds<=86400:raise ValueError('observation_policy')
  if allow_observed and (type(permission_reference) is not str or not 1<=len(permission_reference)<=256 or any(ord(c)<32 for c in permission_reference)):raise ValueError('observation_retention_permission')
  self.policy_hash=hashlib.sha256(permission_reference.encode()).hexdigest() if allow_observed else None
  self.lock=threading.RLock();self.allow_observed=allow_observed;self.ttl=retention_seconds;self.clock=clock;self.before_commit=before_commit
  root=Path(directory).absolute()
  if any(p.is_symlink() for p in (root,*root.parents)):raise ValueError('observation_symlink')
  root.mkdir(mode=0o700,parents=True,exist_ok=True)
  if root.stat().st_uid!=os.getuid() or stat.S_IMODE(root.stat().st_mode)&0o077:raise ValueError('observation_private_directory')
  self.path=root/'observations.sqlite3';fd=os.open(self.path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
  try:
   s=os.fstat(fd)
   if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)&0o077:raise ValueError('observation_private_file')
  finally:os.close(fd)
  with self.connect() as db:
   version=db.execute('PRAGMA user_version').fetchone()[0];app=db.execute('PRAGMA application_id').fetchone()[0];tables=db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
   if version not in (0,1) or app not in (0,1195984719) or app==0 and tables:raise ValueError('observation_schema')
   db.execute('CREATE TABLE IF NOT EXISTS records(ordinal INTEGER PRIMARY KEY AUTOINCREMENT,capture TEXT,receipt INTEGER,created REAL,expires REAL,payload BLOB,previous TEXT,digest TEXT,UNIQUE(capture,receipt))')
   db.execute('CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT)');db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('anchor','0'*64));db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('tail','0'*64));db.execute('PRAGMA user_version=1');db.execute('PRAGMA application_id=1195984719')
  self.recover();self.prune();self.cached=self.summary()
 @contextmanager
 def connect(self):
  with self.lock:
   with self._connect() as db:yield db
 @contextmanager
 def _connect(self):
  try:
   if self.path.stat().st_size>32*1024*1024:raise ValueError('observation_disk_budget')
   db=sqlite3.connect(self.path,timeout=2)
   try:
    if db.execute('PRAGMA page_size').fetchone()[0]!=4096:raise ValueError('observation_page_size')
    db.execute('PRAGMA journal_mode=DELETE');db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA secure_delete=ON');db.execute('PRAGMA max_page_count=8192')
    with db:yield db
   finally:db.close()
  except sqlite3.Error:raise ValueError('observation_storage_failure') from None
 @staticmethod
 def encode(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 @staticmethod
 def digest(previous,payload):return hashlib.sha256(bytes.fromhex(previous)+payload).hexdigest()
 def trim(self,db):
  rows=db.execute('SELECT ordinal,expires,length(payload),digest FROM records ORDER BY ordinal').fetchall();total=sum(r[2] for r in rows);count=len(rows);last=None
  now=self.clock();expired_through=max((r[0] for r in rows if r[1]<=now),default=0)
  for row in rows:
   if row[0]>expired_through and count<=10000 and total<=MAX_BYTES:break
   total-=row[2];count-=1;last=row
  if last:
   db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('anchor',last[3]));db.execute('DELETE FROM records WHERE ordinal<=?',(last[0],))
 def prune(self):
  with self.lock:
   with self.connect() as db:db.execute('BEGIN IMMEDIATE');self.trim(db);new_cached=self._summary(db)
   self.cached=new_cached
 def append(self,capture,events):
  if type(capture) is not str or not re.fullmatch('[0-9a-f]{32}',capture) or not 1<=len(events)<=128:raise ValueError('observation_batch')
  rows=[];prior=None
  for event in events:
   if event.get('origin') not in ('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE') or event['origin']!='HISTORICAL_SYNTHETIC' and not self.allow_observed:raise ValueError('observation_retention_not_approved')
   receipt=event['receipt_index']
   if type(receipt) is not int or receipt<1 or prior is not None and receipt!=prior+1:raise ValueError('observation_receipt_order')
   prior=receipt;core={k:v for k,v in event.items() if k!='received_monotonic'};created=self.clock();raw=self.encode({'schema':'gig.iex.observation.v1','capture':capture,'created_seconds':created,'expires_seconds':created+self.ttl,'retention_policy':{'permission_reference_sha256':self.policy_hash,'observed_allowed':self.allow_observed,'seconds':self.ttl},'event':core})
   if len(raw)>65536:raise ValueError('observation_record_budget')
   rows.append((receipt,created,raw))
  with self.lock:
   with self.connect() as db:
    db.execute('BEGIN IMMEDIATE');meta=dict(db.execute('SELECT key,value FROM meta'))
    if meta.get('capture')==capture:
     if rows[0][0]!=int(meta['receipt'])+1:raise ValueError('observation_receipt_order')
    elif db.execute('SELECT 1 FROM records WHERE capture=? LIMIT 1',(capture,)).fetchone():raise ValueError('observation_retired_capture')
    last=db.execute('SELECT digest FROM records ORDER BY ordinal DESC LIMIT 1').fetchone();previous=last[0] if last else meta['anchor']
    for receipt,created,raw in rows:
     digest=self.digest(previous,raw);db.execute('INSERT INTO records(capture,receipt,created,expires,payload,previous,digest) VALUES(?,?,?,?,?,?,?)',(capture,receipt,created,created+self.ttl,raw,previous,digest));previous=digest
    db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('capture',capture));db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('receipt',str(rows[-1][0])));self.trim(db);db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',('tail',previous));new_cached=self._summary(db)
    if self.before_commit:self.before_commit()
   self.cached=new_cached
 def recover(self):
  with self.connect() as db:
   previous=db.execute('SELECT value FROM meta WHERE key=?',('anchor',)).fetchone()[0];rows=db.execute('SELECT capture,receipt,created,expires,payload,previous,digest FROM records ORDER BY ordinal').fetchall();result=[]
   if len(rows)>10000 or sum(len(r[4]) for r in rows)>MAX_BYTES:raise ValueError('observation_recovery_budget')
   for capture,receipt,created,expires,raw,parent,digest in rows:
    if parent!=previous or self.digest(previous,raw)!=digest:raise ValueError('observation_corrupt_chain')
    value=json.loads(raw)
    if value['capture']!=capture or value['event']['receipt_index']!=receipt or value['created_seconds']!=created or value['expires_seconds']!=expires or value['schema']!='gig.iex.observation.v1':raise ValueError('observation_corrupt_record')
    if value['event']['origin']!='HISTORICAL_SYNTHETIC' and not self.allow_observed:raise ValueError('observation_retention_not_approved')
    if expires>self.clock():result.append({**value,'classification':'RETAINED_HISTORICAL_NOT_CURRENT'})
    previous=digest
   if previous!=db.execute('SELECT value FROM meta WHERE key=?',('tail',)).fetchone()[0]:raise ValueError('observation_truncated_tail')
   return result
 def summary(self):
  with self.connect() as db:return self._summary(db)
 def _summary(self,db):
   count,size=db.execute('SELECT count(*),coalesce(sum(length(payload)),0) FROM records').fetchone();last=db.execute('SELECT digest FROM records ORDER BY ordinal DESC LIMIT 1').fetchone()
   return {'enabled':True,'records':count,'logical_payload_bytes':size,'last_digest':last[0] if last else None,'retention_seconds':self.ttl,'classification':'RETAINED_HISTORICAL_NOT_CURRENT','limits':'10000 records,16MiB payload,32MiB database;rollback journal may add32MiB','hot_live_recovery':False,'integrity':'Hash-chain consistency,not authenticated exchange completeness'}
