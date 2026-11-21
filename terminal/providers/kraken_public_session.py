"""Explicit offline Kraken-v2 trade/status subset; never opens a transport.

Official schemas are mapped to bounded local admission. Identifiers are not book
sequence/backfill guarantees and caller origin labels are not source authentication.
"""
from __future__ import annotations
from collections import deque
import datetime as dt
import hashlib
import re
from urllib.parse import urlsplit
from .kraken import ProviderError,decode,decimal_wire,bounded_integer,UINT64_MAX,PRICE_MAX,MAX_PAYLOAD

PROFILE='TRADE_STATUS_SESSION_V1'
SERVICES={'spot_ws','spot_rest','spot_fix','spot_trading','futures_ws','futures_rest','futures_fix','futures_trading','all','unspecified'}
SYSTEMS={'online','cancel_only','maintenance','post_only'}
PHASES={'announced','reminder_24h','approaching_30m','imminent_5m','final_warning_30s','unspecified'}
ACTIONS={'continue','reduce_activity','cancel_open_orders','stop_new_orders','disconnect_and_wait','unspecified'}
RFC3339=re.compile(r'(\d{4}-\d{2}-\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?([Zz]|[+-]\d{2}:\d{2})\Z')

def text(value,limit=256,*,empty=False):
 if type(value)is not str or len(value)>limit or not empty and not value or any(ord(c)<32 or ord(c)==127 for c in value):raise ProviderError('public_text')
 return value

def instant(value,*,utc=False):
 if type(value)is not str or len(value)>40:raise ProviderError('public_timestamp')
 m=RFC3339.fullmatch(value)
 if not m or m[6]=='-00:00':raise ProviderError('public_timestamp')
 try:
  day=dt.date.fromisoformat(m[1]);h,minute,second=map(int,m.group(2,3,4))
  if h>23 or minute>59 or second>59:raise ValueError()
  zone=m[6];offset=0
  if zone not in('Z','z'):
   zh,zm=map(int,zone[1:].split(':'))
   if zh>23 or zm>59:raise ValueError()
   offset=(zh*60+zm)*60*(1 if zone[0]=='+'else -1)
  if utc and offset:raise ValueError()
  seconds=(day-dt.date(1970,1,1)).days*86400+h*3600+minute*60+second-offset
  value=seconds*10**9+int((m[5]or'').ljust(9,'0'))
  if not 0<=value<=2**63-1:raise ValueError()
  return str(value)
 except ValueError as exc:raise ProviderError('public_timestamp')from exc

def url(value):
 text(value,512,empty=True)
 if not value:return value
 try:p=urlsplit(value);host=p.hostname;port=p.port
 except ValueError as exc:raise ProviderError('public_source_url')from exc
 if p.scheme not in('http','https')or not host or p.username or p.password or p.fragment or port==0 or any(c.isspace()for c in value):raise ProviderError('public_source_url')
 return value

def services(value):
 if type(value)is not list or len(value)>len(SERVICES)or any(type(v)is not str or v not in SERVICES for v in value)or len(set(value))!=len(value):raise ProviderError('public_services')
 return list(value)

def choices(value,allowed,code):
 if type(value)is not str or value not in allowed:raise ProviderError(code)
 return value

def _events(values,*,emergency):
 if type(values)is not list or len(values)>16:raise ProviderError('public_status_budget')
 out=[];ids=set()
 for v in values:
  expected={'event_id','title','incident_status','impact','affected_services','started_at_utc','next_steps','source_url'}if emergency else{'event_id','title','expected_start_utc','expected_end_utc','time_to_start_s','phase','affected_services','order_submission','recommended_action','cancel_before_utc','source_url'}
  if type(v)is not dict or set(v)!=expected:raise ProviderError('public_status_event_fields')
  identity=str(bounded_integer(v['event_id'],UINT64_MAX,'public_event_id'))
  if identity in ids:raise ProviderError('public_duplicate_event')
  ids.add(identity);row={'event_id':identity,'title':text(v['title']),'affected_services':services(v['affected_services']),'source_url':url(v['source_url'])}
  if emergency:
   row.update(incident_status=choices(v['incident_status'],{'investigating','identified','monitoring','unspecified'},'public_incident_status'),impact=choices(v['impact'],{'none','minor','major','critical','unspecified'},'public_incident_impact'),started_at_utc=v['started_at_utc'],started_at_ns=instant(v['started_at_utc'],utc=True))
   steps=v['next_steps']
   if type(steps)is not list or len(steps)>16:raise ProviderError('public_status_budget')
   row['next_steps']=[]
   for step in steps:
    if type(step)is not dict or set(step)!={'applies_to','type','expected_at_utc'}:raise ProviderError('public_next_step_fields')
    row['next_steps'].append({'applies_to':services(step['applies_to']),'type':choices(step['type'],{'expected_restart','expected_cancel_only','expected_post_only','expected_online','unspecified'},'public_next_step_type'),'expected_at_utc':step['expected_at_utc'],'expected_at_ns':instant(step['expected_at_utc'],utc=True)})
  else:
   start=instant(v['expected_start_utc'],utc=True);end=None if v['expected_end_utc']is None else instant(v['expected_end_utc'],utc=True);cancel=None if v['cancel_before_utc']is None else instant(v['cancel_before_utc'],utc=True)
   if end is not None and int(end)<int(start):raise ProviderError('public_maintenance_order')
   row.update(expected_start_utc=v['expected_start_utc'],expected_start_ns=start,expected_end_utc=v['expected_end_utc'],expected_end_ns=end,cancel_before_utc=v['cancel_before_utc'],cancel_before_ns=cancel,time_to_start_s=str(bounded_integer(v['time_to_start_s'],UINT64_MAX,'public_countdown')),phase=choices(v['phase'],PHASES,'public_phase'),order_submission=choices(v['order_submission'],{'allowed','discouraged','blocked','unspecified'},'public_order_submission'),recommended_action=choices(v['recommended_action'],ACTIONS,'public_recommended_action'))
  out.append(row)
 return out

def _bounded_payload(value):
 """Apply the raw-frame resource boundary to lower-level decoded entry too."""
 from decimal import Decimal
 pending=[(value,0)];nodes=0;size=0
 while pending:
  value,depth=pending.pop();nodes+=1
  if nodes>8192 or depth>12:raise ProviderError('public_payload_budget')
  if type(value)is dict:
   if len(value)>32:raise ProviderError('public_payload_budget')
   for key,child in value.items():
    if type(key)is not str or len(key)>64:raise ProviderError('public_payload_fields')
    size+=len(key)+4;pending.append((child,depth+1))
  elif type(value)is list:
   if len(value)>100:raise ProviderError('public_payload_budget')
   size+=len(value)+2;pending.extend((child,depth+1)for child in value)
  elif type(value)is str:
   try:size+=len(value.encode('utf-8'))+2
   except UnicodeError as exc:raise ProviderError('public_payload_scalar')from exc
  elif type(value)is Decimal:
   if not value.is_finite()or len(value.as_tuple().digits)>64:raise ProviderError('public_payload_scalar')
   size+=len(str(value))
  elif type(value)is int:
   if value.bit_length()>128:raise ProviderError('public_payload_scalar')
   size+=len(str(value))
  elif value is None or type(value)is bool:size+=5
  else:raise ProviderError('public_payload_scalar')
  if size>MAX_PAYLOAD:raise ProviderError('public_payload_budget')

class KrakenPublicSession:
 """Per-symbol, local-generation trade/status admission with bounded retained IDs.

 Explicit reconnect is required after protocol failure, a changed connection ID or
 non-online status. This local conservative fence does not infer engine continuity.
 """
 def __init__(self,*,symbol='BTC/USD',price_scale=100,quantity_scale=100000000,request_id=200,snapshot=False,origin='HISTORICAL_SYNTHETIC'):
  if symbol not in('BTC/USD','ETH/USD')or type(request_id)is not int or not 0<=request_id<=UINT64_MAX-2 or type(snapshot)is not bool or origin not in('HISTORICAL_SYNTHETIC','LIVE_OBSERVED')or any(type(v)is not int or not 1<=v<=10**9 for v in(price_scale,quantity_scale)):raise ProviderError('public_configuration')
  self.symbol=symbol;self.price_scale=price_scale;self.quantity_scale=quantity_scale;self.request_id=request_id;self.snapshot=snapshot;self.origin=origin
  self.generation=0;self.connected=False;self.reconnect_required=False;self.phase='DISCONNECTED';self.connection_id=None;self.system=None;self.last_receive_ns=None;self.snapshot_seen=False;self.trades=deque(maxlen=256);self.identities={}
 def check_connect(self):
  if self.request_id+2*(self.generation+1)>UINT64_MAX:raise ProviderError('public_request_id_exhausted')
 def connect(self):
  self.check_connect();self.generation+=1;self.connected=True;self.reconnect_required=False;self.phase='AWAITING_ACK';self.connection_id=None;self.system=None;self.last_receive_ns=None;self.snapshot_seen=False;self.trades.clear();self.identities.clear()
 def disconnected(self):
  self.connected=False;self.phase='DISCONNECTED';self.connection_id=None;self.system=None;self.last_receive_ns=None;self.snapshot_seen=False;self.trades.clear();self.identities.clear()
 def invalidate(self):self.reconnect_required=True;self.phase='RECONNECT_REQUIRED'
 def current_request_id(self,method='subscribe'):
  return self.request_id+2*self.generation-(1 if method=='subscribe'else 0)
 def subscription_request(self):
  if not self.connected:raise ProviderError('public_not_connected')
  return {'method':'subscribe','params':{'channel':'trade','symbol':[self.symbol],'snapshot':self.snapshot},'req_id':self.current_request_id()}
 def unsubscription_request(self):
  self._online()
  if self.phase!='ACTIVE':raise ProviderError('trade_not_subscribed')
  request={'method':'unsubscribe','params':{'channel':'trade','symbol':[self.symbol]},'req_id':self.current_request_id('unsubscribe')};self.phase='UNSUBSCRIBE_PENDING';return request
 def _online(self):
  if not self.connected or self.reconnect_required or self.system!='online'or self.connection_id is None:raise ProviderError('public_online_connection_required')
 def feed(self,raw,now_ns):
  try:
   if type(raw)is not str or len(raw)>MAX_PAYLOAD:raise ProviderError('payload_limit')
   try:body=raw.encode('utf-8')
   except UnicodeError as exc:raise ProviderError('malformed_json')from exc
   receipt=self.accept_payload(decode(raw),now_ns,hashlib.sha256(body).hexdigest());receipt['source_hash_basis']='HASHED_RAW_FRAME';return receipt
  except (ProviderError,MemoryError):self.invalidate();raise
 def accept_payload(self,payload,now_ns,source_sha256):
  try:return self._accept_payload(payload,now_ns,source_sha256)
  except (ProviderError,MemoryError):self.invalidate();raise
 def _accept_payload(self,payload,now_ns,source_sha256):
  if type(payload)is not dict or type(source_sha256)is not str or not re.fullmatch('[0-9a-f]{64}',source_sha256):raise ProviderError('public_source_identity')
  _bounded_payload(payload)
  if type(now_ns)is not int or not 0<=now_ns<=UINT64_MAX or self.last_receive_ns is not None and now_ns<self.last_receive_ns:raise ProviderError('public_receive_clock')
  if not self.connected:raise ProviderError('public_not_connected')
  if payload.get('channel')=='status':receipt=self._status(payload)
  elif payload.get('method')in('subscribe','unsubscribe'):receipt=self._ack(payload)
  elif payload.get('channel')=='trade':receipt=self._trade(payload)
  else:raise ProviderError('public_message_unsupported')
  self.last_receive_ns=now_ns;receipt.update(public_session_profile=PROFILE,local_generation=str(self.generation),connection_id=self.connection_id,receive_monotonic_ns=str(now_ns),source_sha256=source_sha256,source_hash_basis='CALLER_SUPPLIED_DIGEST',source_sequence=None,origin=self.origin,independent_source_authentication=False,full_protocol_qualified=False)
  return receipt
 def _status(self,p):
  if set(p)!={'channel','type','data'}or p['type']!='update'or type(p['data'])is not list or len(p['data'])!=1:raise ProviderError('public_status_fields')
  v=p['data'][0];base={'system','api_version','connection_id','version'}
  if type(v)is not dict or set(v)not in(base,base|{'upcoming_maintenance','emergency'})or v['api_version']!='v2':raise ProviderError('public_status_fields')
  identity=str(bounded_integer(v['connection_id'],UINT64_MAX,'public_connection_id'));version=text(v['version'],128);system=choices(v['system'],SYSTEMS,'public_system')
  if self.connection_id is not None and identity!=self.connection_id:raise ProviderError('public_connection_changed')
  receipt={'kind':'status','api_version':'v2','version':version,'system':system,'book_reset_required':system!='online'}
  if 'upcoming_maintenance'in v:receipt.update(upcoming_maintenance=_events(v['upcoming_maintenance'],emergency=False),emergency=_events(v['emergency'],emergency=True))
  self.connection_id=identity;self.system=system
  if system!='online':self.invalidate()
  receipt['reconnect_required']=self.reconnect_required
  return receipt
 def _ack(self,p):
  self._online();method=p['method'];expected='AWAITING_ACK'if method=='subscribe'else'UNSUBSCRIBE_PENDING'
  if self.phase!=expected:raise ProviderError('public_ack_phase')
  if set(p)-{'method','success','result','req_id','time_in','time_out','error'}or type(p.get('success'))is not bool:raise ProviderError('public_ack_fields')
  request=bounded_integer(p.get('req_id'),UINT64_MAX,'public_ack_request_id')
  if request!=self.current_request_id(method):raise ProviderError('public_ack_request_id')
  times={name:instant(p[name])for name in('time_in','time_out')if name in p}
  if len(times)==2 and int(times['time_out'])<int(times['time_in']):raise ProviderError('public_ack_time_order')
  if not p['success']:
   if 'result'in p:raise ProviderError('public_ack_fields')
   error=text(p.get('error'),512);self.invalidate();return {'kind':'request_rejected','method':method,'request_id':str(request),'error':error,'source_times_ns':times,'reconnect_required':True}
  if 'error'in p:raise ProviderError('public_ack_fields')
  result=p.get('result');keys={'channel','symbol','snapshot'}if method=='subscribe'else{'channel','symbol'}
  if type(result)is not dict or not keys<=set(result)or set(result)-keys-{'warnings'}or result['channel']!='trade'or result['symbol']!=self.symbol:raise ProviderError('public_ack_identity')
  if method=='subscribe'and result['snapshot']is not self.snapshot:raise ProviderError('public_ack_snapshot')
  warnings=result.get('warnings',[])
  if type(warnings)is not list or len(warnings)>16:raise ProviderError('public_ack_warnings')
  warnings=[text(v)for v in warnings]
  receipt={'kind':'acknowledgment','method':method,'channel':'trade','request_id':str(request),'warnings':warnings,'source_times_ns':times}
  if method=='subscribe':receipt['snapshot']=self.snapshot;self.phase='ACTIVE'
  else:self.phase='UNSUBSCRIBED'
  return receipt
 def _trade(self,p):
  self._online()
  if self.phase!='ACTIVE':raise ProviderError('trade_acknowledgment_required')
  if set(p)!={'channel','type','data'}or p['type']not in('snapshot','update')or type(p['data'])is not list:raise ProviderError('public_trade_fields')
  snapshot=p['type']=='snapshot'
  if snapshot and(not self.snapshot or self.snapshot_seen):raise ProviderError('public_trade_snapshot_unrequested')
  if not snapshot and self.snapshot and not self.snapshot_seen:raise ProviderError('public_trade_snapshot_required')
  if len(p['data'])>(50 if snapshot else 100):raise ProviderError('public_trade_budget')
  pending=[];identities=set();duplicates=[]
  for item in p['data']:
   if type(item)is not dict or set(item)!={'symbol','side','price','qty','trade_id','timestamp','ord_type'}:raise ProviderError('public_trade_fields')
   if item['symbol']!=self.symbol or item['side']not in('buy','sell')or item['ord_type']not in('limit','market'):raise ProviderError('public_trade_identity')
   key=str(bounded_integer(item['trade_id'],UINT64_MAX,'public_trade_id'))
   if key in identities:raise ProviderError('public_duplicate_trade_in_batch')
   identities.add(key)
   # Official price/qty are JSON numbers; strings and Python floats are refused.
   from decimal import Decimal
   if any(type(item[k])not in(int,Decimal)for k in('price','qty')):raise ProviderError('public_trade_number')
   price,pt=decimal_wire(item['price'],maximum=PRICE_MAX,scale=self.price_scale);qty,qt=decimal_wire(item['qty'],maximum=UINT64_MAX,scale=self.quantity_scale)
   if price=='0'or qty=='0':raise ProviderError('public_zero_trade')
   stamp=instant(item['timestamp']);identity=(price,qty,item['side'],item['ord_type'],stamp)
   if key in self.identities:
    if self.identities[key]!=identity:raise ProviderError('public_conflicting_trade_identity')
    duplicates.append(key);continue
   pending.append((key,identity,{'trade_id':key,'symbol':self.symbol,'side':item['side'],'price_ticks':price,'quantity':qty,'price_decimal_text':pt,'quantity_decimal_text':qt,'source_order_type':item['ord_type'],'source_timestamp':item['timestamp'],'source_timestamp_ns':stamp,'origin':self.origin}))
  trades=self.trades.copy();known=self.identities.copy()
  for key,identity,trade in pending:
   if len(trades)==trades.maxlen:known.pop(trades[0]['trade_id'])
   trades.append(trade);known[key]=identity
  receipt={'kind':'trades','type':p['type'],'trades':[dict(t)for _,_,t in pending],'duplicate_trade_ids':duplicates,'deduplication_window':'256','identifier_scope':'unique_per_book_not_L2_sequence','gap_detection':False,'complete_history':False,'snapshot_trade_limit':50,'side_semantics':'taker_order_side'}
  self.trades=trades;self.identities=known;self.snapshot_seen=self.snapshot_seen or snapshot
  return receipt
