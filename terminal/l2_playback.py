"""Bounded native-validated prefix cache; no synthetic order identities or observed uploads."""
from copy import deepcopy
from itertools import islice
import json
import time
from pathlib import Path
import gig_microstructure as gig
from .l2_recording import load_l2,MAX_RECORDS,SCHEMA,SCHEMA2,bounded_entries
from .recording import canonical,root_path,safe_id
from .providers.kraken import KrakenBookAdapter,_pairs

MAX_CACHE_BYTES=8*1024*1024

def metadata(directory,identity):
    target=root_path(directory)/safe_id(identity)
    if target.is_symlink() or not target.is_dir():raise ValueError('recording_path')
    path=target/'manifest.json'
    if path.is_symlink():raise ValueError('recording_path')
    with path.open('rb') as stream:raw=stream.read(8193)
    if len(raw)>8192:raise ValueError('recording_manifest_budget')
    m=json.loads(raw,object_pairs_hook=_pairs)
    if type(m) is not dict or m.get('schema') not in (SCHEMA,SCHEMA2) or m.get('identity')!=identity or m.get('complete') is not True:
        raise ValueError('recording_manifest')
    return m


def discover(directory,*,allow_observed=False):
    root=root_path(directory);entries=bounded_entries(root,9)
    if len(entries)>8:raise ValueError('recording_dataset_budget')
    result=[];rejected=[]
    for path in sorted(entries):
        if path.name.startswith('.pending-'):continue
        try:
            m=metadata(root,path.name)
            origin=m.get('origin')
            if origin not in ('HISTORICAL_SYNTHETIC','LIVE_OBSERVED'):raise ValueError('recording_origin')
            result.append({'identity':path.name,'origin':'HISTORICAL_OBSERVED' if origin=='LIVE_OBSERVED' else origin,
                'instrument':m.get('symbol'),'venue':'Kraken','records':m.get('records'),'sha256':m.get('sha256'),
                'status':'AVAILABLE' if origin=='HISTORICAL_SYNTHETIC' or allow_observed else 'BLOCKED_PERMISSION',
                'market_session_complete':False})
        except (ValueError,OSError):
            rejected.append({'identity':path.name if path.name.isascii() and len(path.name)<=48 else '<invalid>','reason':'invalid_or_unreadable_manifest'})
    return {'sessions':result,'rejected':rejected,'maximum_sessions':8}


class RecordedSession:
    """Construct in a worker; native objects never cross threads. Public frames are owned copies."""
    def __init__(self,directory,identity,*,allow_observed=False):
        m=metadata(directory,identity)
        if m.get('origin')=='LIVE_OBSERVED' and not allow_observed:raise ValueError('observed_processing_permission_required')
        manifest,rows=load_l2(directory,identity)
        if not 0<len(rows)<=MAX_RECORDS:raise ValueError('empty_recording')
        book=gig._native.AggregateDepth(32,1048576)
        def apply(**e):gig._checked((book.snapshot if e['snapshot'] else book.update)(e['bids'],e['asks'],e['sequence']))
        adapter=KrakenBookAdapter(apply,symbol=manifest['symbol'],price_scale=manifest['price_scale'],
            quantity_scale=manifest['quantity_scale'],origin=manifest['origin'])
        self.frames=[];self.cache_bytes=0;self.identity=identity;self.manifest=manifest
        self.total_records=len(rows);self.expired=False
        from .l2_research import ResearchWindow
        research=ResearchWindow()
        last_exchange=None
        for position in range(len(rows)+1):
            row=rows[position-1] if position else None;receipt=None
            if row:
                receipt=adapter.feed(row['raw'],int(row['receive_monotonic_ns']))
                if 'normalized' in row and receipt!=row['normalized']:raise ValueError('recording_normalization_mismatch')
                if receipt['kind'] in ('snapshot','update'):last_exchange=receipt.get('source_timestamp_ns')
                if receipt['kind'] in ('snapshot','update','trades'):
                    observed={**receipt,'historical_snapshot':adapter.last_trade_snapshot} if receipt['kind']=='trades' else receipt
                    research.observe(observed,gig._checked(book.state()) if receipt['kind']!='trades' else None,int(row['receive_monotonic_ns']),position)
            native=gig._checked(book.state())
            frame={'research':research.view(int(row['receive_monotonic_ns']) if row else 0),'native':native,'last_event':receipt,'source_timestamp_ns':last_exchange,
                   'received_at_ns':row.get('receive_unix_ns') if row else None,
                   'replay_time_ns':str(int(row['receive_monotonic_ns'])-int(rows[0]['receive_monotonic_ns'])) if row else '0'}
            self.cache_bytes+=len(canonical(frame))
            if self.cache_bytes>MAX_CACHE_BYTES:raise ValueError('recording_prefix_cache_budget')
            self.frames.append(frame)
        if not adapter.snapshots:raise ValueError('recording_snapshot_required')
    def check_expiry(self):
        if time.time()>self.manifest['created_unix_seconds']+self.manifest['retention_seconds']:
            self.expired=True;self.frames.clear();self.cache_bytes=0
        return self.expired
    @property
    def event_count(self):return 0 if self.check_expiry() else self.total_records
    def view(self,position,playing,speed):
        if self.check_expiry():
            return {'mode':'HISTORICAL_REPLAY','origin':'UNAVAILABLE','instrument':self.manifest['symbol'],'provider':'kraken-recorded','venue':'Kraken',
                'book':{'bids':[],'asks':[]},'position':0,'event_count':0,'playing':False,'speed':speed,'revision':'0',
                'metrics':{k:None for k in ('spread','midprice','microprice','imbalance')},
                'feed':{'state':'ERROR','reason':'recording_retention_expired','real_time':False},
                'provenance':{'category':'UNAVAILABLE','dataset':self.identity,'session_segment':self.identity+':expired','complete_initialization':False}}
        if type(position) is not int or not 0<=position<=self.event_count:raise ValueError('replay_position')
        frame=deepcopy(self.frames[position]);native=frame.pop('native');m=self.manifest
        metrics={target:native['metrics'][source] for target,source in [('spread','spread'),('midprice','midpoint'),('microprice','microprice'),('imbalance','depth_imbalance'),('bid_depth','bid_depth'),('ask_depth','ask_depth')]}
        origin='HISTORICAL_OBSERVED' if m['origin']=='LIVE_OBSERVED' else 'HISTORICAL_SYNTHETIC'
        return {'mode':'HISTORICAL_REPLAY','origin':origin,'dataset':'recorded-l2','provider':'kraken-recorded','venue':'Kraken',
            'instrument':m['symbol'],'feed_type':'L2_AGGREGATE','price_scale':str(m['price_scale']),
            'quantity_scale':str(m['quantity_scale']),'position':position,'event_count':self.event_count,
            'playing':playing,'speed':speed,'book':{'bids':native['bids'],'asks':native['asks']},'revision':native['revision'],
            'metrics':metrics,**frame,'feed':{'state':'HISTORICAL_REPLAY','reason':'Native-validated recorded L2 prefix; not live or complete L3',
                'real_time':False,'stale':False,'capture_complete':True,'market_session_complete':False,'sequence_complete':False},
            'provenance':{'category':origin,'dataset':self.identity,'recording_sha256':m['sha256'],'session_segment':self.identity,
                'complete_initialization':False,'initialization_scope':'subscribed aggregate L2 only',
                'clock':'source:optional;receive:recorded;replay:relative_monotonic','recording_enabled':False,
                'playback':'immutable native-validated prefix cache','native_validated_prefixes':len(self.frames),
                'cache_encoded_bytes':self.cache_bytes,'exchange_sequence':None}}


def save_fixture(directory,identity='authored-l2-v2'):
    from .l2_recording import L2Writer
    from .providers.fixtures import EVENTS
    book=gig._native.AggregateDepth(32,1048576)
    def apply(**e):gig._checked((book.snapshot if e['snapshot'] else book.update)(e['bids'],e['asks'],e['sequence']))
    adapter=KrakenBookAdapter(apply,price_scale=100000000,quantity_scale=100000000)
    writer=L2Writer(directory,identity,enabled=True,version=2)
    try:
        for i,raw in enumerate(EVENTS):
            receipt=adapter.feed(raw,i*50_000_000)
            writer.append(raw,i*50_000_000,normalized=receipt)
        return writer.finish('fixture_complete')
    except BaseException:writer.abort();raise


def delete_session(directory,identity):
    import shutil
    target=root_path(directory)/safe_id(identity)
    metadata(directory,identity)  # Refuse symlinks and unknown/non-finalized trees.
    shutil.rmtree(target)
    from .l2_recording import sync_directory
    sync_directory(target.parent)
    return True


def prune_expired(directory,*,now=None,active_stage=None):
    """Delete only expired owned finalized logs; active pending writer is excluded."""
    import shutil
    from .l2_recording import sync_directory,MAX_AGE
    candidate=Path(directory)
    if candidate.is_symlink():raise ValueError('recording_root_symlink')
    if not candidate.exists():return {'deleted_count':0,'grace_seconds':60}
    root=root_path(directory);instant=time.time() if now is None else now
    entries=bounded_entries(root,9)
    if len(entries)>8:raise ValueError('recording_dataset_budget')
    deleted=[]
    for path in entries:
        if path.is_symlink() or not path.is_dir():continue
        if path.name.startswith('.pending-l2-'):
            deadline=None
            for name in ('pending.json','manifest.json'):
                candidate=path/name
                if candidate.is_symlink() or not candidate.is_file():continue
                try:
                    with candidate.open('rb') as stream:raw=stream.read(8193)
                    if len(raw)>8192:continue
                    m=json.loads(raw,object_pairs_hook=_pairs);created=m.get('created_unix_seconds');retention=m.get('retention_seconds')
                    if type(created) is int and type(retention) is int and 0<=created and 1<=retention<=MAX_AGE:deadline=created+retention;break
                except (OSError,ValueError,AttributeError):continue
            expired=path!=active_stage and (instant>deadline if deadline is not None else instant-path.stat().st_mtime>MAX_AGE)
        else:
            try:
                m=metadata(root,path.name);created=m.get('created_unix_seconds');retention=m.get('retention_seconds')
                expired=(type(created) is int and type(retention) is int and 0<=created and 1<=retention<=MAX_AGE and instant>created+retention)
            except (OSError,ValueError):continue
        if expired:shutil.rmtree(path);deleted.append(path.name)
    if deleted:sync_directory(root)
    return {'deleted_count':len(deleted),'grace_seconds':60}
