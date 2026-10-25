"""Bounded permission-aware L2 source log and deterministic replay, private only.

No web input paths. Uncommitted directories are explicitly incomplete. No observed
log is ever created unless operator permission and recording are separately enabled.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from .providers.kraken import Permission,ProviderError,decode,_pairs
from .recording import canonical,root_path,safe_id

MAX_RECORDS=512
MAX_BYTES=2*1024*1024
MAX_AGE=86400
SCHEMA='gig.terminal.l2_log.v1'
SCHEMA2='gig.terminal.l2_log.v2'

def sync_directory(path):
    descriptor=os.open(path,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)

def optional_ns(value):
    if value is None:return
    if type(value) is not str or len(value)>19 or not value.isascii() or not value.isdecimal() or str(int(value))!=value or int(value)>2**63-1:
        raise ValueError('recording_timestamp')

class L2Writer:
    def __init__(self,directory,identity,*,symbol='BTC/USD',origin='HISTORICAL_SYNTHETIC',
                 enabled=False,permission=None,retention_seconds=MAX_AGE,clock=time.time,version=1):
        if enabled is not True:raise ValueError('recording_disabled')
        if type(version) is not int or version not in (1,2):raise ValueError('recording_version')
        self.version=version
        if origin not in ('HISTORICAL_SYNTHETIC','LIVE_OBSERVED'):raise ValueError('recording_origin')
        if origin=='LIVE_OBSERVED':
            if not isinstance(permission,Permission):raise ValueError('recording_permission')
            permission.require_live()
            if not permission.recording_approved:raise ValueError('retention_permission_unverified')
        if symbol not in ('BTC/USD','ETH/USD') or type(retention_seconds) is not int or not 1<=retention_seconds<=MAX_AGE:
            raise ValueError('recording_configuration')
        root=root_path(directory);self.identity=safe_id(identity);self.target=root/self.identity
        if self.target.exists() or self.target.is_symlink():raise ValueError('recording_exists')
        if len(list(root.iterdir()))>=8:raise ValueError('recording_dataset_budget')
        self.stage=Path(tempfile.mkdtemp(prefix='.pending-l2-',dir=root))
        try:
            fd=os.open(self.stage/'events.jsonl',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            self.stream=os.fdopen(fd,'wb')
        except BaseException:shutil.rmtree(self.stage,ignore_errors=True);raise
        self.origin,self.symbol,self.clock=origin,symbol,clock
        self.retention=retention_seconds;self.count=self.size=0;self.previous=None
        self.digest=hashlib.sha256();self.closed=False
    def append(self,raw,receive_ns,*,receive_unix_ns=None,normalized=None):
        if self.closed:raise ValueError('recording_closed')
        try:
            decode(raw)  # Preserve exact source string, but reject malformed/unbounded JSON.
            if type(receive_ns) is not int or not 0<=receive_ns<=2**63-1 or (self.previous is not None and receive_ns<self.previous):
                raise ValueError('recording_receive_clock')
            value={'ordinal':self.count,'receive_monotonic_ns':str(receive_ns),'raw':raw}
            if self.version==2:
                optional_ns(receive_unix_ns)
                if type(normalized) is not dict or len(canonical(normalized))>65536:raise ValueError('recording_normalized')
                value.update(receive_unix_ns=receive_unix_ns,normalized=normalized)
            elif normalized is not None or receive_unix_ns is not None:raise ValueError('recording_version')
            row=canonical(value)+b'\n'
            if self.count>=MAX_RECORDS or self.size+len(row)>MAX_BYTES:raise ValueError('recording_budget')
            written=self.stream.write(row)
            if written!=len(row):raise OSError('short_recording_write')
            self.digest.update(row);self.count+=1;self.size+=len(row);self.previous=receive_ns
        except BaseException:
            self.abort();raise
    def finish(self,reason='operator_stopped'):
        if self.closed:raise ValueError('recording_closed')
        if reason not in ('operator_stopped','fixture_complete','record_budget','disconnected'):raise ValueError('recording_end_reason')
        manifest={'schema':SCHEMA if self.version==1 else SCHEMA2,'identity':self.identity,'origin':self.origin,'provider':'kraken',
            'profile':'provisional_kraken_v2','symbol':self.symbol,'records':self.count,'bytes':self.size,
            'sha256':self.digest.hexdigest(),'complete':True,'created_unix_seconds':int(self.clock()),
            'retention_seconds':self.retention,'price_scale':100000000,'quantity_scale':100000000,
            'initialization':'first_valid_subscribed_L2_snapshot_required_not_L3'}
        if self.version==2:manifest.update(venue='Kraken',interval_end_reason=reason,market_session_complete=False)
        try:
            self.stream.flush();os.fsync(self.stream.fileno());self.stream.close()
            fd=os.open(self.stage/'manifest.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            with os.fdopen(fd,'wb') as stream:stream.write(canonical(manifest));stream.flush();os.fsync(stream.fileno())
            if self.target.exists():raise ValueError('recording_exists')
            sync_directory(self.stage)
            self.stage.rename(self.target);self.closed=True
            sync_directory(self.target.parent)
            return manifest
        except BaseException:self.abort();raise
    def abort(self):
        if not self.closed:
            self.closed=True;self.stream.close();shutil.rmtree(self.stage,ignore_errors=True)


def load_l2(directory,identity,*,clock=time.time):
    root=root_path(directory);target=root/safe_id(identity)
    if target.is_symlink() or not target.is_dir():raise ValueError('recording_path')
    content=[]
    for name,limit in [('manifest.json',8192),('events.jsonl',MAX_BYTES)]:
        path=target/name
        if path.is_symlink():raise ValueError('recording_path')
        with path.open('rb') as stream:value=stream.read(limit+1)
        if len(value)>limit:raise ValueError('recording_budget')
        content.append(value)
    m=json.loads(content[0],object_pairs_hook=_pairs)
    if type(m) is not dict:raise ValueError('recording_manifest')
    if (m.get('schema') not in (SCHEMA,SCHEMA2) or m.get('identity')!=identity or m.get('complete') is not True
            or m.get('origin') not in ('HISTORICAL_SYNTHETIC','LIVE_OBSERVED') or m.get('provider')!='kraken'
            or m.get('profile')!='provisional_kraken_v2' or m.get('symbol') not in ('BTC/USD','ETH/USD')
            or m.get('price_scale')!=100000000 or m.get('quantity_scale')!=100000000):raise ValueError('recording_manifest')
    if m.get('initialization')!='first_valid_subscribed_L2_snapshot_required_not_L3' or m.get('market_session_complete',False) is not False or m.get('complete_initialization',False) is not False:
        raise ValueError('recording_false_completeness')
    if m['schema']==SCHEMA2 and (m.get('venue')!='Kraken' or m.get('interval_end_reason') not in ('operator_stopped','fixture_complete','record_budget','disconnected')):
        raise ValueError('recording_manifest')
    for key,minimum,maximum in [('created_unix_seconds',0,2**63-1),('retention_seconds',1,MAX_AGE),('records',0,MAX_RECORDS),('bytes',0,MAX_BYTES)]:
        if type(m.get(key)) is not int or not minimum<=m[key]<=maximum:raise ValueError('recording_manifest')
    if clock()<m['created_unix_seconds'] or clock()-m['created_unix_seconds']>m['retention_seconds']:raise ValueError('recording_expired')
    if len(content[1])!=m['bytes'] or hashlib.sha256(content[1]).hexdigest()!=m['sha256']:raise ValueError('recording_digest')
    if content[1] and not content[1].endswith(b'\n'):raise ValueError('recording_truncated')
    rows=[];previous=None
    for i,line in enumerate(content[1].splitlines()):
        row=json.loads(line,object_pairs_hook=_pairs)
        keys={'ordinal','receive_monotonic_ns','raw'}
        if m['schema']==SCHEMA2:keys|={'receive_unix_ns','normalized'}
        if type(row) is not dict or set(row)!=keys or type(row['ordinal']) is not int or row['ordinal']!=i:
            raise ValueError('recording_ordinal')
        ns=row['receive_monotonic_ns']
        if type(ns) is not str or not ns.isascii() or not ns.isdecimal() or str(int(ns))!=ns or not 0<=int(ns)<=2**63-1:
            raise ValueError('recording_receive_clock')
        if previous is not None and int(ns)<previous:raise ValueError('recording_receive_clock')
        if m['schema']==SCHEMA2:
            optional_ns(row['receive_unix_ns'])
            if type(row['normalized']) is not dict or len(canonical(row['normalized']))>65536:raise ValueError('recording_normalized')
        decode(row['raw']);previous=int(ns);rows.append(row)
        if len(rows)>MAX_RECORDS:raise ValueError('recording_budget')
    if len(rows)!=m['records']:raise ValueError('recording_count')
    return m,rows


def replay_l2(manifest,rows,position=None):
    """Fresh native state at every seek. No source order, timestamp or L3 inference."""
    import gig_microstructure as gig
    from .providers.kraken import KrakenBookAdapter
    if position is None:position=len(rows)
    if type(position) is not int or not 0<=position<=len(rows)<=MAX_RECORDS:raise ValueError('replay_position')
    book=gig._native.AggregateDepth(32,1048576)
    def apply(**e):gig._checked((book.snapshot if e['snapshot'] else book.update)(e['bids'],e['asks'],e['sequence']))
    origin='HISTORICAL_SYNTHETIC' if manifest['origin']=='HISTORICAL_SYNTHETIC' else 'LIVE_OBSERVED'
    adapter=KrakenBookAdapter(apply,symbol=manifest['symbol'],price_scale=manifest['price_scale'],quantity_scale=manifest['quantity_scale'],origin=origin)
    for row in rows[:position]:
        receipt=adapter.feed(row['raw'],int(row['receive_monotonic_ns']))
        if 'normalized' in row and receipt!=row['normalized']:raise ValueError('recording_normalization_mismatch')
    state=gig._checked(book.state())
    return {'schema_version':'1','mode':'HISTORICAL_REPLAY','origin':'HISTORICAL_SYNTHETIC' if origin=='HISTORICAL_SYNTHETIC' else 'HISTORICAL_OBSERVED',
        'position':position,'event_count':len(rows),'native':state,'source_sha256':manifest['sha256'],
        'complete_initialization':False,'initialization_scope':'aggregate_subscribed_L2_only',
        'trades':list(adapter.trades),'exchange_sequence':None}
