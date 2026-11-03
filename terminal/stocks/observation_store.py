"""Opt-in private bounded SQLite observation ledger;never a hot/live book snapshot."""
import os,stat,sqlite3,json,hashlib,time,re,threading,math
from terminal.verification.artifacts import decode
from pathlib import Path
from contextlib import contextmanager
MAX_BYTES=16*1024*1024
MAX_RECORDS=10000
MAX_RECORD_BYTES=65536
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
   new=s.st_size==0
  finally:os.close(fd)
  with self.connect() as db:
   version=db.execute('PRAGMA user_version').fetchone()[0];app=db.execute('PRAGMA application_id').fetchone()[0];tables=db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
   if new:
    if version!=0 or app!=0 or tables:raise ValueError('observation_schema')
    db.execute('CREATE TABLE IF NOT EXISTS records(ordinal INTEGER PRIMARY KEY AUTOINCREMENT,capture TEXT,receipt INTEGER,created REAL,expires REAL,payload BLOB,previous TEXT,digest TEXT,UNIQUE(capture,receipt))')
    db.execute('CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT)');db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('anchor','0'*64));db.execute('INSERT OR IGNORE INTO meta VALUES(?,?)',('tail','0'*64));db.execute('PRAGMA user_version=1');db.execute('PRAGMA application_id=1195984719')
   elif version!=1 or app!=1195984719:raise ValueError('observation_schema')
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
 @staticmethod
 def _admit_rows(db,record_limit=MAX_RECORDS,byte_limit=MAX_BYTES):
  # COUNT is capped by a subquery before any BLOB is delivered to Python.
  count=db.execute('SELECT count(*) FROM (SELECT 1 FROM records LIMIT ?)',(record_limit+1,)).fetchone()[0]
  if count>record_limit:raise ValueError('observation_recovery_budget')
  total,largest,invalid=db.execute("SELECT coalesce(sum(length(payload)),0),coalesce(max(length(payload)),0),coalesce(sum(typeof(payload)!='blob'),0) FROM records").fetchone()
  if invalid or total>byte_limit or largest>MAX_RECORD_BYTES:raise ValueError('observation_recovery_payload_budget')
  invalid=db.execute("""SELECT count(*) FROM records WHERE
   typeof(capture)!='text' OR length(capture)!=32 OR
   typeof(receipt)!='integer' OR receipt<1 OR
   typeof(created) NOT IN ('real','integer') OR typeof(expires) NOT IN ('real','integer') OR
   typeof(previous)!='text' OR length(previous)!=64 OR
   typeof(digest)!='text' OR length(digest)!=64""").fetchone()[0]
  if invalid:raise ValueError('observation_record_contract')
  return count
 @staticmethod
 def _metadata(db):
  count=db.execute('SELECT count(*) FROM (SELECT 1 FROM meta LIMIT 5)').fetchone()[0]
  if count>4:
   raise ValueError('observation_metadata_budget')
  invalid=db.execute("SELECT count(*) FROM meta WHERE typeof(key)!='text' OR length(key)>7 OR typeof(value)!='text' OR length(value)>64").fetchone()[0]
  if invalid:raise ValueError('observation_metadata_contract')
  meta=dict(db.execute('SELECT key,value FROM meta LIMIT 4'))
  if len(meta)!=count:raise ValueError('observation_metadata_contract')
  if set(meta) not in ({'anchor','tail'},{'anchor','tail','capture','receipt'}):raise ValueError('observation_metadata_contract')
  if any(not re.fullmatch('[0-9a-f]{64}',meta[k])for k in ('anchor','tail')):raise ValueError('observation_metadata_contract')
  if 'capture' in meta:
   if not re.fullmatch('[0-9a-f]{32}',meta['capture']) or not re.fullmatch('[1-9][0-9]{0,18}',meta['receipt']) or int(meta['receipt'])>2**63-1:
    raise ValueError('observation_metadata_contract')
  return meta
 def _payload(self,raw,capture,receipt,created,expires):
  if type(raw)is not bytes or not 1<=len(raw)<=MAX_RECORD_BYTES:raise ValueError('observation_record_budget')
  value=decode(raw)
  if set(value)!={'schema','capture','created_seconds','expires_seconds','retention_policy','event'} or value['schema']!='gig.iex.observation.v1':raise ValueError('observation_corrupt_record')
  if (type(capture)is not str or not re.fullmatch('[0-9a-f]{32}',capture) or type(receipt)is not int or not 1<=receipt<=2**63-1
      or any(type(v)not in(int,float)or type(v)is float and not math.isfinite(v)for v in(created,expires,value['created_seconds'],value['expires_seconds']))):raise ValueError('observation_corrupt_record')
  policy=value['retention_policy'];event=value['event']
  if (type(policy)is not dict or set(policy)!={'seconds','observed_allowed','permission_reference_sha256'}
      or type(policy['seconds'])is not int or not 1<=policy['seconds']<=86400 or type(policy['observed_allowed'])is not bool):raise ValueError('observation_retention_policy')
  reference=policy['permission_reference_sha256']
  if (policy['observed_allowed'] and (type(reference)is not str or not re.fullmatch('[0-9a-f]{64}',reference))) or (not policy['observed_allowed'] and reference is not None):raise ValueError('observation_retention_policy')
  if (value['capture']!=capture or value['created_seconds']!=created or value['expires_seconds']!=expires
      or expires!=created+policy['seconds'] or type(event)is not dict or type(event.get('receipt_index'))is not int or event['receipt_index']!=receipt):raise ValueError('observation_corrupt_record')
  if event.get('origin')not in('HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'):raise ValueError('observation_origin')
  if event['origin']=='OBSERVED_OFFICIAL_RESPONSE' and (not self.allow_observed or not policy['observed_allowed']):raise ValueError('observation_retention_not_approved')
  return value
 def trim(self,db):
  self._admit_rows(db,MAX_RECORDS+128,MAX_BYTES+128*MAX_RECORD_BYTES)
  rows=list(db.execute('SELECT ordinal,expires,length(payload),digest FROM records ORDER BY ordinal LIMIT ?',(MAX_RECORDS+128,)));total=sum(r[2] for r in rows);count=len(rows);last=None
  now=self.clock();expired_through=max((r[0] for r in rows if r[1]<=now),default=0)
  for row in rows:
   if row[0]>expired_through and count<=MAX_RECORDS and total<=MAX_BYTES:break
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
   self._payload(raw,capture,receipt,created,created+self.ttl)
   rows.append((receipt,created,raw))
  with self.lock:
   with self.connect() as db:
    db.execute('BEGIN IMMEDIATE');meta=self._metadata(db)
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
   # One SQLite read snapshot covers preflight, metadata and streamed rows.
   db.execute('BEGIN')
   self._admit_rows(db);meta=self._metadata(db);previous=meta['anchor'];result=[]
   seen=set();last_capture=None;last_receipt=None
   for capture,receipt,created,expires,raw,parent,digest in db.execute('SELECT capture,receipt,created,expires,payload,previous,digest FROM records ORDER BY ordinal LIMIT ?',(MAX_RECORDS+1,)):
    if parent!=previous or type(digest)is not str or not re.fullmatch('[0-9a-f]{64}',digest) or self.digest(previous,raw)!=digest:raise ValueError('observation_corrupt_chain')
    value=self._payload(raw,capture,receipt,created,expires)
    if capture==last_capture:
     if receipt!=last_receipt+1:raise ValueError('observation_receipt_order')
    else:
     if capture in seen:raise ValueError('observation_retired_capture')
     seen.add(capture)
    last_capture,last_receipt=capture,receipt
    if expires>self.clock():result.append({**value,'classification':'RETAINED_HISTORICAL_NOT_CURRENT'})
    previous=digest
   if previous!=meta['tail']:raise ValueError('observation_truncated_tail')
   if last_capture is not None and (meta.get('capture')!=last_capture or meta.get('receipt')!=str(last_receipt)):raise ValueError('observation_metadata_tail_mismatch')
   return result
 def summary(self):
  with self.connect() as db:return self._summary(db)
 def _summary(self,db):
   count,size=db.execute('SELECT count(*),coalesce(sum(length(payload)),0) FROM records').fetchone();last=db.execute('SELECT digest FROM records ORDER BY ordinal DESC LIMIT 1').fetchone()
   return {'enabled':True,'records':count,'logical_payload_bytes':size,'last_digest':last[0] if last else None,'retention_seconds':self.ttl,'classification':'RETAINED_HISTORICAL_NOT_CURRENT','limits':'10000 records,16MiB payload,32MiB database;rollback journal may add32MiB','hot_live_recovery':False,'integrity':'Hash-chain consistency,not authenticated exchange completeness'}
