"""Bounded stream-control intent, not credentials, market data or a native L3 snapshot.

The caller writes this record inside the observation-ledger transaction. Its tail
binding detects inconsistent local publication; a hash is not source authenticity.
"""
import hashlib,json,re
from terminal.verification.artifacts import decode

MAX_BYTES=4096
PHASES={'DISCONNECTED','CONNECTED_PENDING','AUTH_PENDING','AUTH_SENT','SUBSCRIBE_PENDING','SUBSCRIBE_SENT','SUBSCRIBED'}

def validate(value):
    fields={'schema','source_session_id','symbols','channels','generation','accepted_receipt','failures','retry_budget','connection_count','active','phase'}
    if type(value)is not dict or set(value)!=fields or value['schema']!='gig.iex.control.v1':raise ValueError('live_checkpoint_schema')
    if type(value['source_session_id'])is not str or not re.fullmatch('[a-f0-9]{32}',value['source_session_id']):raise ValueError('live_checkpoint_capture')
    symbols=value['symbols'];channels=value['channels']
    if type(symbols)is not list or len(symbols)>4 or any(type(s)is not str or not re.fullmatch(r'[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?',s)for s in symbols) or symbols!=sorted(set(symbols)):raise ValueError('live_checkpoint_symbols')
    if type(channels)is not list or not 1<=len(channels)<=3 or any(type(c)is not str or c not in ('quotes','trades','bars')for c in channels) or channels!=sorted(set(channels)) or not any(c in channels for c in ('quotes','trades')):raise ValueError('live_checkpoint_channels')
    for name in ('generation','accepted_receipt','connection_count'):
        if type(value[name])is not int or not 0<=value[name]<2**53-1:raise ValueError('live_checkpoint_counter')
    if type(value['failures'])is not int or not 0<=value['failures']<=5 or type(value['retry_budget'])is not int or not 1<=value['retry_budget']<=5:raise ValueError('live_checkpoint_retries')
    if type(value['active'])is not bool or value['active']and not symbols or type(value['phase'])is not str or value['phase']not in PHASES:raise ValueError('live_checkpoint_phase')
    return value

def exists(db):return bool(db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='live_checkpoint'").fetchone())

def write(db,value,meta):
    validate(value)
    if value['accepted_receipt'] and (meta.get('capture')!=value['source_session_id'] or meta.get('receipt')!=str(value['accepted_receipt'])):raise ValueError('live_checkpoint_receipt')
    core={'schema':'gig.iex.control.envelope.v1','control':value,'observation_tail':meta['tail'],'capture':meta.get('capture'),'receipt':meta.get('receipt')}
    raw=json.dumps(core,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    if len(raw)>MAX_BYTES:raise ValueError('live_checkpoint_budget')
    db.execute('CREATE TABLE IF NOT EXISTS live_checkpoint(singleton INTEGER PRIMARY KEY CHECK(singleton=1),payload BLOB NOT NULL,digest TEXT NOT NULL)')
    db.execute('INSERT OR REPLACE INTO live_checkpoint VALUES(1,?,?)',(raw,hashlib.sha256(raw).hexdigest()))

def read(db,meta):
    if not exists(db):return None
    count=db.execute('SELECT count(*) FROM (SELECT 1 FROM live_checkpoint LIMIT 2)').fetchone()[0]
    if count==0:return None
    if count!=1 or db.execute("SELECT count(*) FROM live_checkpoint WHERE typeof(singleton)!='integer' OR singleton!=1 OR typeof(payload)!='blob' OR length(payload)>? OR typeof(digest)!='text' OR length(digest)!=64",(MAX_BYTES,)).fetchone()[0]:raise ValueError('live_checkpoint_budget')
    raw,digest=db.execute('SELECT payload,digest FROM live_checkpoint WHERE singleton=1').fetchone()
    if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('live_checkpoint_digest')
    value=decode(raw)
    if set(value)!={'schema','control','observation_tail','capture','receipt'} or value['schema']!='gig.iex.control.envelope.v1':raise ValueError('live_checkpoint_schema')
    validate(value['control'])
    if any(value[k]!=meta.get(m)for k,m in [('observation_tail','tail'),('capture','capture'),('receipt','receipt')]):raise ValueError('live_checkpoint_tail')
    c=value['control']
    if c['accepted_receipt']and(value['capture']!=c['source_session_id']or value['receipt']!=str(c['accepted_receipt'])):raise ValueError('live_checkpoint_receipt')
    return {**value,'checkpoint_sha256':digest}
