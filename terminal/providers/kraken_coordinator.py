"""Opt-in raw-frame Kraken joint-session admission into an owned native L2 book.

No transport, permission change, trading, receipt import, or provider qualification.
"""
from __future__ import annotations
import copy
from dataclasses import dataclass
import hashlib
import json
import re
import gig_microstructure as gig
from .kraken import (BOOK_SESSION_PROFILE,BOOK_DEPTH_SESSION_PROFILE,BOOK_LARGE_DEPTH_PROFILE,KrakenBookAdapter,
                     ProviderError,_decode_frame,bounded_integer,UINT64_MAX)
from .kraken_public_session import KrakenPublicSession,PROFILE as PUBLIC_PROFILE

PROFILE='NATIVE_JOINT_SESSION_V1'

def _digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

@dataclass(frozen=True)
class KrakenSessionToken:
 """Caller-supplied connection capture label plus local, nonexchange generation."""
 capture:str
 generation:int
 symbol:str

class KrakenSessionCoordinator:
 """Conservative joint book/trade/status eligibility on one supplied connection.

 Both subscriptions and any requested trade snapshot must be admitted. Every frame
 requires the current capture token. Bad frames fence all financial eligibility;
 reconnect requires fresh status, acknowledgments and book snapshot. Native owner
 replacement occurs only after parsing, native validation and receipt allocation.
 """
 def __init__(self,*,profile,symbol='BTC/USD',depth=10,book_profile=BOOK_SESSION_PROFILE,
              book_request_id=100,trade_request_id=200,trade_snapshot=False,
              price_scale=100,quantity_scale=100000000,stale_ns=10000000000,
              origin='HISTORICAL_SYNTHETIC',native_capacity=256,native_budget=1048576):
  if profile!=PROFILE or book_profile not in(BOOK_SESSION_PROFILE,BOOK_DEPTH_SESSION_PROFILE,BOOK_LARGE_DEPTH_PROFILE):raise ProviderError('coordinator_profile')
  if type(book_request_id)is not int or type(trade_request_id)is not int or not 0<=book_request_id<trade_request_id<=UINT64_MAX-2:raise ProviderError('coordinator_request_ids')
  capacity_limit = 2000 if book_profile == BOOK_LARGE_DEPTH_PROFILE else 256
  if type(native_capacity)is not int or not 1<=native_capacity<=capacity_limit or type(native_budget)is not int or not 1<=native_budget<=67108864:raise ProviderError('coordinator_native_budget')
  if not all(hasattr(gig._native,name)for name in('AggregateDepth','restore_aggregate')):raise ProviderError('coordinator_native_unsupported')
  self._book=KrakenBookAdapter(lambda **_:None,symbol=symbol,depth=depth,
   ordered_updates=True,book_session_profile=book_profile,book_request_id=book_request_id,
   price_scale=price_scale,quantity_scale=quantity_scale,stale_ns=stale_ns,origin=origin)
  if book_profile == BOOK_LARGE_DEPTH_PROFILE and native_capacity < 2 * depth:
   raise ProviderError('coordinator_native_budget')
  self._public=KrakenPublicSession(symbol=symbol,price_scale=price_scale,
   quantity_scale=quantity_scale,request_id=trade_request_id,snapshot=trade_snapshot,origin=origin)
  self.symbol=symbol;self.origin=origin;self.native_capacity=native_capacity;self.native_budget=native_budget
  self._generation=0;self._token=None;self._last_clock=None;self._native=None;self._native_image=None
  self._native_source=None;self._last_receipt_sha256=None;self._eligible=False;self._reconnect_required=False;self._reason='not_connected'
 def _fence(self,reason):
  self._eligible=False;self._reconnect_required=True;self._reason=reason
  self._public.invalidate();self._book._book_acknowledged=False
  self._book.state='GAP_DETECTED';self._book.reason='coordinated_session_fenced'
 def _current(self,token):
  if type(token)is not KrakenSessionToken or token is not self._token or self._token is None or not self._public.connected:raise ProviderError('coordinator_capture_token')
 def _clock(self,now_ns):
  if type(now_ns)is not int or not 0<=now_ns<=UINT64_MAX or self._last_clock is not None and now_ns<self._last_clock:raise ProviderError('coordinator_receive_clock')
  if self._book.last_book_receive_ns is not None and now_ns-self._book.last_book_receive_ns>self._book.stale_ns:raise ProviderError('coordinator_book_stale')
 def connect(self,capture):
  try:
   if type(capture)is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}',capture):raise ProviderError('coordinator_capture_label')
   self._public.check_connect()
   if self._book.book_request_id+self._book._book_generation+1>UINT64_MAX:raise ProviderError('coordinator_request_id_exhausted')
   book=copy.deepcopy(self._book);public=copy.deepcopy(self._public);book.connect();public.connect()
   generation=self._generation+1
   if public.generation!=generation or book._book_generation!=generation:raise ProviderError('coordinator_generation')
   token=KrakenSessionToken(capture,generation,self.symbol)
  except (ProviderError,MemoryError):self._fence('connect_rejected');raise
  self._book=book;self._public=public;self._generation=generation;self._token=token
  self._last_clock=None;self._native=None;self._native_image=None;self._native_source=None
  self._last_receipt_sha256=None;self._eligible=False;self._reconnect_required=False;self._reason='awaiting_status_and_subscriptions'
  return token
 def disconnected(self):
  self._book.disconnected();self._public.disconnected();self._token=None
  self._native=None;self._native_image=None;self._native_source=None;self._eligible=False
  self._reconnect_required=True;self._reason='transport_closed'
 def subscription_requests(self,token):
  self._current(token)
  try:
   if self._reconnect_required:raise ProviderError('coordinator_reconnect_required')
   return [self._book.book_subscription_request(),self._public.subscription_request()]
  except (ProviderError,MemoryError):self._fence('request_rejected');raise
 def trade_unsubscription_request(self,token):
  self._current(token)
  try:
   if self._reconnect_required:raise ProviderError('coordinator_reconnect_required')
   public=copy.deepcopy(self._public);request=public.unsubscription_request()
  except (ProviderError,MemoryError):self._fence('request_rejected');raise
  self._public=public;self._eligible=False;self._reason='joint_trade_unsubscription_pending'
  return request
 def _native_candidate(self,event):
  try:
   if self._native_image is None:native=gig._native.AggregateDepth(self.native_capacity,self.native_budget)
   else:native=gig._checked(gig._native.restore_aggregate(self._native_image,str(self.native_capacity),str(self.native_budget)))
   gig._checked((native.snapshot if event['snapshot']else native.update)(event['bids'],event['asks'],event['sequence']))
   image=gig._checked(native.checkpoint())
   return native,image
  except (gig.EngineError,ValueError,RuntimeError,MemoryError)as exc:raise ProviderError('coordinator_native_rejected')from exc
 def _make_receipt(self,source_receipt,source,token,now_ns,public,book,image,event,eligible,reconnect,source_size):
  result={'schema':'gig.kraken.coordinated_session.v1','profile':PROFILE,'symbol':self.symbol,
   'capture':token.capture,'local_generation':str(token.generation),'connection_id':public.connection_id,
   'receive_monotonic_ns':str(now_ns),'source_sha256':source,'source_hash_basis':'HASHED_RAW_FRAME','source_frame_bytes':source_size,
   'book_session_profile':book.book_session_profile,'public_session_profile':PUBLIC_PROFILE,
   'generation_scope':'COORDINATOR_INSTANCE_ONLY','ordering_scope':'SUPPLIED_WIRE_ORDER_AND_MONOTONIC_RECEIVE_CLOCK',
   'stale_detection':'LOCAL_GENERATION_AND_BOOK_RECEIVE_DEADLINE_ONLY','subscribed_depth':book.depth,
   'checksum_depth':10,'checksum_scope':'top_10_per_side_only',
   'kind':source_receipt['kind'],'source_receipt':copy.deepcopy(source_receipt),
   'native_event':copy.deepcopy(event),'native_book_sha256':None if image is None else _digest(image),
   'native_book_revision':None if image is None else image['revision'],
   'native_book_source_sha256':source if event is not None else self._native_source,
   'book_eligible':eligible,'reconnect_required':reconnect,'book_level':'L2',
   'trade_observation_level':'EXECUTED_TRADES_NOT_L3_ORDERS','source_sequence':None,
   'gap_detection':False,'complete_history':False,'origin':self.origin,
   'provider_requested':False,'independent_source_authentication':False,'full_protocol_qualified':False}
  result['sha256']=_digest(result);return result
 def feed(self,raw,now_ns,*,token):
  # Frames rejected at the capture boundary must leave the active generation intact.
  self._current(token)
  try:
   self._clock(now_ns)
   if type(raw)is not str or len(raw)>self._book.frame_limit:raise ProviderError('payload_limit')
   try:body=raw.encode('utf-8')
   except UnicodeError as exc:raise ProviderError('malformed_json')from exc
   payload=_decode_frame(raw,self._book.frame_limit);source=hashlib.sha256(body).hexdigest()
   is_status=payload.get('channel')=='status'
   if self._reconnect_required and not is_status:raise ProviderError('coordinator_reconnect_required')
   book=copy.deepcopy(self._book);public=copy.deepcopy(self._public);events=[]
   def stage(**event):
    if events:raise ProviderError('coordinator_multiple_native_events')
    events.append(copy.deepcopy(event))
   book.apply_native=stage
   if is_status:
    receipt=public.feed(raw,now_ns)
   else:
    if public.system!='online'or public.connection_id is None or public.reconnect_required:raise ProviderError('coordinator_online_status_required')
    if payload.get('channel')=='trade':receipt=public.feed(raw,now_ns)
    elif payload.get('channel')in('book','heartbeat'):
     if public.phase in('UNSUBSCRIBE_PENDING','UNSUBSCRIBED'):raise ProviderError('coordinator_joint_trade_closed')
     receipt=book.feed(raw,now_ns)
    elif payload.get('method')in('subscribe','unsubscribe'):
     req=bounded_integer(payload.get('req_id'),UINT64_MAX,'coordinator_ack_request_id')
     if req==book.book_subscription_request()['req_id']:
      if payload['method']!='subscribe':raise ProviderError('coordinator_book_unsubscribe_unsupported')
      receipt=book.feed(raw,now_ns)
     elif req==public.current_request_id(payload['method']):receipt=public.feed(raw,now_ns)
     else:raise ProviderError('coordinator_ack_request_id')
    else:raise ProviderError('coordinator_message_unsupported')
   if 'public_session_profile'in receipt:
    if receipt['source_hash_basis']!='HASHED_RAW_FRAME'or receipt['source_sha256']!=source or receipt['local_generation']!=str(token.generation)or receipt['connection_id']!=public.connection_id:raise ProviderError('coordinator_public_receipt_binding')
   event=events[0]if events else None
   if event is not None:
    if receipt.get('native_event')!=event or receipt['kind']not in('snapshot','update')or event.get('sequence')is not None:raise ProviderError('coordinator_native_receipt_binding')
    native,image=self._native_candidate(event)
   else:
    if 'native_event'in receipt:raise ProviderError('coordinator_native_receipt_binding')
    native,image=self._native,self._native_image
   reconnect=self._reconnect_required or public.reconnect_required or public.phase=='UNSUBSCRIBED'
   eligible=(not reconnect and public.system=='online'and public.phase=='ACTIVE'and
     (not public.snapshot or public.snapshot_seen)and book._book_acknowledged and book.state=='LIVE'and image is not None)
   result=self._make_receipt(receipt,source,token,now_ns,public,book,image,event,eligible,reconnect,len(body))
   last_sha=result['sha256'];native_source=source if event is not None else self._native_source
  except (ProviderError,MemoryError)as exc:
   self._fence(exc.code if isinstance(exc,ProviderError)else'allocation_failed');raise
  self._book=book;self._public=public;self._native=native;self._native_image=image
  self._native_source=native_source;self._last_receipt_sha256=last_sha;self._last_clock=now_ns
  self._eligible=bool(eligible);self._reconnect_required=bool(reconnect)
  if reconnect:
   self._book._book_acknowledged=False;self._book.state='GAP_DETECTED';self._book.reason='coordinated_session_fenced'
   self._reason='explicit_reconnect_required'
  else:self._reason='joint_session_eligible'if eligible else'awaiting_joint_snapshots_and_acknowledgments'
  return result
 def view(self,now_ns):
  try:self._clock(now_ns)
  except ProviderError as exc:
   self._fence(exc.code)
   if exc.code!='coordinator_book_stale':raise
  eligible=self._eligible and self._native is not None and not self._reconnect_required
  # Read native state before publishing the local view; never expose retained
  # financial data when source eligibility has been fenced.
  try:book=gig._checked(self._native.state())if eligible else None
  except (gig.EngineError,MemoryError)as exc:
   self._fence('coordinator_native_view_unavailable');raise ProviderError('coordinator_native_view_unavailable')from exc
  result={'schema':'gig.kraken.coordinated_view.v1','profile':PROFILE,'symbol':self.symbol,
   'capture':None if self._token is None else self._token.capture,'local_generation':str(self._generation),
   'connection_id':self._public.connection_id,'system':self._public.system,'book_eligible':bool(eligible),
   'book':book,'reconnect_required':self._reconnect_required,'reason':self._reason,
   'native_book_sha256':None if self._native_image is None else _digest(self._native_image),
   'native_book_source_sha256':self._native_source,'last_frame_receipt_sha256':self._last_receipt_sha256,
   'source_sequence':None,'book_level':'L2','trade_observation_level':'EXECUTED_TRADES_NOT_L3_ORDERS',
   'generation_scope':'COORDINATOR_INSTANCE_ONLY','stale_detection':'LOCAL_GENERATION_AND_BOOK_RECEIVE_DEADLINE_ONLY',
   'subscribed_depth':self._book.depth,'checksum_depth':10,'checksum_scope':'top_10_per_side_only',
   'origin':self.origin,'independent_source_authentication':False,'full_protocol_qualified':False}
  self._last_clock=now_ns
  return result
