"""Versioned finite Kraken joint capture; exact supplied raw bytes, not a market tape.

The supervisor's admitted depth and a fresh single generation are bound to each
log. Original receipts are rederived before atomic publication and playback.
No live transport, exchange sequence, backfill or issuer/provider authentication.
"""
import copy,hashlib,re,time
from pathlib import Path
from .l2_recording import L2Writer,MAX_RECORDS,MAX_BYTES,MAX_AGE,optional_ns,JOINT_SCHEMA,JOINT_DEPTH_SCHEMA,JOINT_SCHEMAS
from .recording import canonical,root_path,safe_id
from .verification.artifacts import read_bytes,decode as decode_metadata
from .providers.kraken import (BOOK_SESSION_PROFILE,BOOK_DEPTH_SESSION_PROFILE,BOOK_LARGE_DEPTH_PROFILE,
 LARGE_DEPTHS,LARGE_BOOK_PAYLOAD,MAX_PAYLOAD,_decode_frame)
from .providers.kraken_coordinator import KrakenSessionCoordinator,PROFILE as JOINT_PROFILE

SCHEMA=JOINT_SCHEMA
PROFILE='ORIGINAL_RAW_JOINT_SESSION_RECORDING_V1'
DEPTH_PROFILE='ORIGINAL_RAW_JOINT_DEPTH_SESSION_RECORDING_V2'
RECORDING_DEPTHS=(10,25,100,*LARGE_DEPTHS)
MAX_CACHE_BYTES=8*1024*1024
SHA=re.compile('[0-9a-f]{64}')
INITIALIZATION='fresh_joint_status_book_trade_ack_and_L2_snapshot_required_not_L3'


class JointPublicationUncertain(ValueError):
 code='recording_joint_publication_uncertain'
 def __init__(self,identity):self.identity=identity;super().__init__(self.code)


def joint_object(raw):
 try:return decode_metadata(raw,numeric_policy='exact-integer')
 except ValueError as error:
  if getattr(error,'code',None)=='duplicate_json_field':
   from .providers.kraken import ProviderError
   raise ProviderError('duplicate_json_key')from None
  raise


def _sha(value):return hashlib.sha256(canonical(value)).hexdigest()


def _coordinator(symbol,origin,depth=10):
 if type(depth)is not int or depth not in RECORDING_DEPTHS:raise ValueError('recording_joint_depth')
 book_profile=BOOK_LARGE_DEPTH_PROFILE if depth in LARGE_DEPTHS else BOOK_DEPTH_SESSION_PROFILE if depth!=10 else BOOK_SESSION_PROFILE
 return KrakenSessionCoordinator(profile=JOINT_PROFILE,symbol=symbol,depth=depth,
  book_profile=book_profile,price_scale=100000000,quantity_scale=100000000,
  origin=origin,native_capacity=max(256,2*depth))


def _session(capture,symbol,origin,depth=10):
 c=_coordinator(symbol,origin,depth);token=c.connect(capture)
 return c,token,{'profile':JOINT_PROFILE,'capture':capture,'local_generation':'1',
  'book_session_profile':c._book.book_session_profile,'depth':depth,'trade_snapshot':False,
  'stale_ns':'10000000000','book_request_base':100,'trade_request_base':200,
  'native_capacity':c.native_capacity,'native_budget':c.native_budget,'subscriptions':c.subscription_requests(token)}


class JointL2Writer(L2Writer):
 """No native owner persists across asynchronous filesystem worker invocations."""
 def __init__(self,*args,**kwargs):
  if kwargs.pop('version',2)!=2:raise ValueError('recording_joint_version')
  self.recording_depth=kwargs.pop('depth',10)
  if type(self.recording_depth)is not int or self.recording_depth not in RECORDING_DEPTHS:raise ValueError('recording_joint_depth')
  self.joint_session=None
  super().__init__(*args,version=2,**kwargs)
 def _decode_source(self,raw):
  return _decode_frame(raw,LARGE_BOOK_PAYLOAD if self.recording_depth in LARGE_DEPTHS else MAX_PAYLOAD)
 def append(self,raw,receive_ns,*,receive_unix_ns=None,normalized=None):
  try:
   if type(normalized)is not dict or normalized.get('profile')!=JOINT_PROFILE or normalized.get('local_generation')!='1'or normalized.get('origin')!=self.origin or normalized.get('symbol')!=self.symbol:raise ValueError('recording_joint_receipt')
   if normalized.get('source_sha256')!=hashlib.sha256(raw.encode('utf-8')).hexdigest()or normalized.get('receive_monotonic_ns')!=str(receive_ns):raise ValueError('recording_joint_source_binding')
   capture=normalized.get('capture')
   if self.joint_session is None:
    _,_,self.joint_session=_session(capture,self.symbol,self.origin,self.recording_depth)
   elif self.joint_session['capture']!=capture:raise ValueError('recording_joint_generation_changed')
   if normalized.get('subscribed_depth')!=self.recording_depth or normalized.get('book_session_profile')!=self.joint_session['book_session_profile']:raise ValueError('recording_joint_depth')
   if self.recording_depth!=10:
    receipt_hash=normalized.get('sha256')
    if type(receipt_hash)is not str or not SHA.fullmatch(receipt_hash)or _sha({k:v for k,v in normalized.items()if k!='sha256'})!=receipt_hash:raise ValueError('recording_joint_receipt')
    normalized={'sha256':receipt_hash}
   super().append(raw,receive_ns,receive_unix_ns=receive_unix_ns,normalized=normalized)
  except BaseException:self.abort();raise
 def _manifest(self,reason):
  if self.joint_session is None:raise ValueError('recording_joint_initialization_missing')
  schema,profile=(SCHEMA,PROFILE)if self.recording_depth==10 else(JOINT_DEPTH_SCHEMA,DEPTH_PROFILE)
  m=super()._manifest(reason);m.update(schema=schema,profile=profile,initialization=INITIALIZATION,
   joint_session=copy.deepcopy(self.joint_session),source_sequence=None,gap_detection=False,
   complete_initialization=False,independent_source_authentication=False)
  m['manifest_sha256']=_sha(m);return m
 def _validate_finish(self,manifest):
  # All written bytes are flushed/fsynced before this hook. Reconstruct in this
  # worker only; no live native objects are transferred between threads.
  body=read_bytes(self.stage/'events.jsonl',MAX_BYTES)
  validate_log(self.identity,manifest,body,clock=self.clock)
 def finish(self,reason='operator_stopped'):
  if self.closed:raise ValueError('recording_closed')
  try:return super().finish(reason)
  except BaseException as error:
   self.abort()
   if self._published:raise JointPublicationUncertain(self.identity)from error
   raise


def _manifest(identity,m,clock):
 keys={'schema','identity','origin','provider','profile','symbol','records','bytes','sha256',
  'complete','created_unix_seconds','retention_seconds','price_scale','quantity_scale',
  'initialization','venue','interval_end_reason','market_session_complete','joint_session',
  'source_sequence','gap_detection','complete_initialization','independent_source_authentication','manifest_sha256'}
 if type(m)is not dict or set(m)!=keys or m['schema']not in JOINT_SCHEMAS or m['identity']!=safe_id(identity)or m['profile']!=(PROFILE if m['schema']==SCHEMA else DEPTH_PROFILE) or m['provider']!='kraken'or m['venue']!='Kraken'or m['origin']not in('HISTORICAL_SYNTHETIC','LIVE_OBSERVED')or m['symbol']not in('BTC/USD','ETH/USD')or m['complete']is not True:raise ValueError('recording_joint_manifest')
 if m['initialization']!=INITIALIZATION or any(m[k]is not False for k in('market_session_complete','gap_detection','complete_initialization','independent_source_authentication'))or m['source_sequence']is not None:raise ValueError('recording_joint_false_completeness')
 if any(type(m[k])is not int or m[k]!=100000000 for k in('price_scale','quantity_scale'))or m['interval_end_reason']not in('operator_stopped','fixture_complete','record_budget','disconnected'):raise ValueError('recording_joint_manifest')
 for key,minimum,maximum in(('records',1,MAX_RECORDS),('bytes',1,MAX_BYTES),('created_unix_seconds',0,2**63-1),('retention_seconds',1,MAX_AGE)):
  if type(m[key])is not int or not minimum<=m[key]<=maximum:raise ValueError('recording_joint_manifest')
 if any(type(m[k])is not str or not SHA.fullmatch(m[k])for k in('sha256','manifest_sha256'))or _sha({k:v for k,v in m.items()if k!='manifest_sha256'})!=m['manifest_sha256']:raise ValueError('recording_joint_manifest_digest')
 now=clock()
 if now<m['created_unix_seconds']or now>m['created_unix_seconds']+m['retention_seconds']:raise ValueError('recording_expired')
 session=m['joint_session']
 if type(session)is not dict:raise ValueError('recording_joint_session')
 depth=session.get('depth')
 if (m['schema']==SCHEMA)!=(depth==10):raise ValueError('recording_joint_depth')
 c,token,expected=_session(session.get('capture'),m['symbol'],m['origin'],depth)
 if canonical(session)!=canonical(expected):raise ValueError('recording_joint_session')
 return c,token


def validate_log(identity,manifest,body,*,clock=time.time,include_frames=False):
 c,token=_manifest(identity,manifest,clock)
 if type(body)is not bytes or len(body)!=manifest['bytes']or hashlib.sha256(body).hexdigest()!=manifest['sha256']:raise ValueError('recording_digest')
 if not body.endswith(b'\n'):raise ValueError('recording_truncated')
 rows=[];previous=None
 for i,line in enumerate(body.split(b'\n')[:-1]):
  row=joint_object(line)
  if line!=canonical(row):raise ValueError('recording_joint_noncanonical_envelope')
  if type(row)is not dict or set(row)!={'ordinal','receive_monotonic_ns','receive_unix_ns','raw','normalized'}or type(row['ordinal'])is not int or row['ordinal']!=i:raise ValueError('recording_ordinal')
  ns=row['receive_monotonic_ns'];optional_ns(ns);optional_ns(row['receive_unix_ns'])
  if ns is None or previous is not None and int(ns)<previous:raise ValueError('recording_receive_clock')
  if type(row['normalized'])is not dict or len(canonical(row['normalized']))>65536:raise ValueError('recording_normalized')
  if manifest['schema']==JOINT_DEPTH_SCHEMA:
   witness=row['normalized']
   if set(witness)!={'sha256'}or type(witness['sha256'])is not str or not SHA.fullmatch(witness['sha256']):raise ValueError('recording_joint_receipt')
  previous=int(ns);rows.append(row)
  if len(rows)>MAX_RECORDS:raise ValueError('recording_budget')
 if len(rows)!=manifest['records']:raise ValueError('recording_count')
 frames,size=_derive_frames(c,token,rows,digest_receipts=manifest['schema']==JOINT_DEPTH_SCHEMA)
 if not frames[-1]['eligible']:raise ValueError('recording_joint_initialization_or_fence')
 if include_frames:return manifest,rows,frames,size
 return manifest,rows


def _derive_frames(c,token,rows,*,digest_receipts=False):
 from .l2_research import ResearchWindow
 research=ResearchWindow();frames=[];size=0;research_ready=False;last_exchange=None;last_book_receive=None;sources={}
 for position in range(len(rows)+1):
  row=rows[position-1]if position else None;receipt=None;now=int(row['receive_monotonic_ns'])if row else 0
  if row:
   receipt=c.feed(row['raw'],now,token=token)
   expected={'sha256':receipt['sha256']}if digest_receipts else receipt
   if canonical(expected)!=canonical(row['normalized']):raise ValueError('recording_joint_normalization_mismatch')
   observed=receipt['source_receipt'];kind=observed['kind']
   channel='book'if kind in('snapshot','update')else'trade'if kind=='trades'else('book_subscription'if'book_session_profile'in observed else'trade_subscription')if kind=='acknowledgment'else kind
   sources[channel]={k:receipt[k]for k in('sha256','source_sha256','capture','local_generation','connection_id','receive_monotonic_ns','kind','origin')}
   if kind in('snapshot','update'):
    last_exchange=observed.get('source_timestamp_ns');last_book_receive=row['receive_unix_ns']
  joint=c.view(now);eligible=joint['book_eligible'];native=joint.pop('book')
  if receipt and eligible:
   observed=receipt['source_receipt'];kind=observed['kind']
   if kind=='snapshot':research_ready=True
   if research_ready and kind in('snapshot','update','trades'):
    event={**observed,'historical_snapshot':observed.get('type')=='snapshot'}if kind=='trades'else observed
    research.observe(event,native if kind!='trades'else None,now,position)
  frame={'native':native,'eligible':eligible,'joint_session':joint,'last_event':receipt,
   'source_timestamp_ns':last_exchange,'received_at_ns':last_book_receive,
   'replay_time_ns':str(now-int(rows[0]['receive_monotonic_ns']))if row else'0',
   'research':research.view(now)if eligible and research_ready else{'status':'UNAVAILABLE','reason':'awaiting_jointly_eligible_book_snapshot'},
   'trades':copy.deepcopy(list(c._public.trades))if eligible else[],
   'source_receipts':copy.deepcopy(sources)}
  size+=len(canonical(frame))
  if size>MAX_CACHE_BYTES:raise ValueError('recording_prefix_cache_budget')
  frames.append(frame)
 return frames,size


def replay_joint(manifest,rows,position=None):
 if type(rows)is not list or not 0<len(rows)<=MAX_RECORDS:raise ValueError('replay_position')
 if position is None:position=len(rows)
 if type(position)is not int or not 0<=position<=len(rows):raise ValueError('replay_position')
 body=b''.join(canonical(row)+b'\n'for row in rows)
 _,_,frames,_=validate_log(manifest.get('identity'),manifest,body,include_frames=True)
 frame=copy.deepcopy(frames[position])
 return {'schema':'gig.kraken.joint_replay.v1','mode':'HISTORICAL_REPLAY',
  'origin':'HISTORICAL_OBSERVED'if manifest['origin']=='LIVE_OBSERVED'else'HISTORICAL_SYNTHETIC',
  'position':position,'event_count':len(rows),'source_sha256':manifest['sha256'],
  'manifest_sha256':manifest['manifest_sha256'],'complete_initialization':False,
  'exchange_sequence':None,**frame}


class JointRecordedSession:
 """Actual NativeSession consumer of immutable fully validated prefix frames."""
 def __init__(self,directory,identity,*,allow_observed=False,expected_manifest=None):
  from .l2_playback import metadata
  m=metadata(directory,identity)if expected_manifest is None else expected_manifest
  if m.get('origin')=='LIVE_OBSERVED'and not allow_observed:raise ValueError('observed_processing_permission_required')
  target=root_path(directory)/safe_id(identity);path=target/'events.jsonl'
  if target.is_symlink()or path.is_symlink():raise ValueError('recording_path')
  manifest,rows,frames,size=validate_log(identity,m,read_bytes(path,MAX_BYTES),include_frames=True)
  self.manifest=copy.deepcopy(manifest);self.frames=frames;self.cache_bytes=size
  self.identity=identity;self.total_records=len(rows);self.expired=False
 def check_expiry(self):
  now=time.time()
  if now<self.manifest['created_unix_seconds']or now>self.manifest['created_unix_seconds']+self.manifest['retention_seconds']:
   self.expired=True;self.frames.clear();self.cache_bytes=0
  return self.expired
 @property
 def event_count(self):return 0 if self.check_expiry()else self.total_records
 def view(self,position,playing,speed):
  expired=self.check_expiry()
  if not expired and(type(position)is not int or not 0<=position<=self.total_records):raise ValueError('replay_position')
  frame=None if expired else copy.deepcopy(self.frames[position]);native=frame.pop('native')if frame else None
  origin='HISTORICAL_OBSERVED'if self.manifest['origin']=='LIVE_OBSERVED'else'HISTORICAL_SYNTHETIC'
  metrics={k:None for k in('spread','midprice','microprice','imbalance','bid_depth','ask_depth')}
  if native:
   for k,s in(('spread','spread'),('midprice','midpoint'),('microprice','microprice'),('imbalance','depth_imbalance'),('bid_depth','bid_depth'),('ask_depth','ask_depth')):metrics[k]=native['metrics'][s]
  depth=self.manifest['joint_session']['depth']
  return {'mode':'HISTORICAL_REPLAY','origin':origin if native else'UNAVAILABLE','dataset':'recorded-l2',
   'subscribed_depth':depth,'checksum_depth':10,'checksum_scope':'top_10_per_side_only',
   'provider':'kraken-recorded','venue':'Kraken','instrument':self.manifest['symbol'],'feed_type':'L2_AGGREGATE',
   'price_scale':str(self.manifest['price_scale']),'quantity_scale':str(self.manifest['quantity_scale']),
   'position':0 if expired else position,'event_count':0 if expired else self.total_records,
   'playing':playing if not expired else False,'speed':speed,'book':{k:native[k][:10]if native else[]for k in('bids','asks')},
   'revision':native['revision']if native else'0','metrics':metrics,**(frame or{}),
   'research':frame['research']if frame else{'status':'UNAVAILABLE','reason':'recording_retention_expired'},
   'flow':{'trades':frame['trades']if frame else[],'classification':'provider_reported_side_not_inferred_cancellations'},
   'feed':{'state':'ERROR'if expired else'HISTORICAL_REPLAY'if native else'SYNCHRONIZING',
    'reason':'recording_retention_expired'if expired else'Exact raw joint-session prefix;not live or complete L3',
    'real_time':False,'stale':False,'capture_complete':not expired,
    'depth':10,'native_depth_counts':{k:len(native[k])if native else 0 for k in('bids','asks')},'market_session_complete':False,'sequence_complete':False},
   'provenance':{'category':origin if native else'UNAVAILABLE','recording_origin':origin,'dataset':self.identity,
    'profile':self.manifest['profile'],'recording_sha256':self.manifest['sha256'],'manifest_sha256':self.manifest['manifest_sha256'],
    'session_segment':self.identity,'complete_initialization':False,'initialization_scope':'subscribed aggregate L2 only',
    'native_metrics_scope':'all admitted native levels;display is top 10',
    'exchange_sequence':None,'recording_enabled':False,'independent_source_authentication':False,
    'playback':'immutable joint-native-validated prefix cache','native_validated_prefixes':len(self.frames),
    'cache_encoded_bytes':self.cache_bytes,'joint_source_receipts':frame['source_receipts']if frame else{}}}


def authored_joint_frames(subscriptions):
 """Explicit synthetic wire fixture; never an inferred observed trade field."""
 from .providers.fixtures import EVENTS
 def raw(value):return canonical(value).decode()
 frames=[raw({'channel':'status','type':'update','data':[{'system':'online','api_version':'v2','connection_id':42,'version':'2.0.8'}]})]
 for request in subscriptions:
  params=request['params'];result={'channel':params['channel'],'symbol':'BTC/USD','snapshot':params['snapshot']}
  if params['channel']=='book':result['depth']=params['depth']
  frames.append(raw({'method':'subscribe','success':True,'req_id':request['req_id'],'result':result}))
 synthetic_trade=raw({'channel':'trade','type':'update','data':[{'symbol':'BTC/USD','side':'buy','trade_id':7,
  'price':101,'qty':0.25,'timestamp':'2026-01-01T00:00:00.000000001Z','ord_type':'limit'}]})
 return (*frames,EVENTS[0],EVENTS[1],synthetic_trade,EVENTS[3],EVENTS[4])


def save_joint_fixture(directory,identity='authored-joint-l2-v1'):
 """Explicit offline production diagnostic; no provider or application startup."""
 c,token,_=_session('authored-joint-session','BTC/USD','HISTORICAL_SYNTHETIC')
 writer=JointL2Writer(directory,identity,enabled=True)
 try:
  for i,raw in enumerate(authored_joint_frames(c.subscription_requests(token))):
   now=i*50000000;receipt=c.feed(raw,now,token=token)
   writer.append(raw,now,normalized=receipt)
  return writer.finish('fixture_complete')
 except BaseException:writer.abort();raise
