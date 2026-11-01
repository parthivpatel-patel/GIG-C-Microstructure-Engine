"""Exact-time explicit-feed historical reads. No automatic startup acquisition.

API/profile assumptions are explicit;HTTPWire is only supplied at an approved
future server integration boundary. FixtureWire is the sole transport used here.
"""
import asyncio
from collections import OrderedDict
import datetime as dt
from dataclasses import dataclass
import hashlib
import json
import re
import time
from urllib.parse import urlencode, urlsplit, parse_qs
from fractions import Fraction
from decimal import Decimal
from terminal.alpaca_wire import WireError, FixtureWire, HTTPWire, decode
from .identity import symbol
from .prices import bars,quote,trade,market_window
from .alpaca_history import metadata
from .session_schedule import SessionSchedule

UTC=dt.timezone.utc
BASE='https://data.alpaca.markets/v2/stocks/'
MAX_NS=2**63-1

def ns(value):
    # RFC3339 with explicit offset;exact nanoseconds retained independently of datetime.
    if type(value) is not str or len(value)>40:raise WireError('history_timestamp')
    m=re.fullmatch(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?(Z|[+-]\d\d:\d\d)',value)
    if not m or m[3]=='-00:00':raise WireError('history_timestamp')
    try:
        if m[3]!='Z' and (int(m[3][1:3])>23 or int(m[3][4:])>59):raise ValueError()
        base=dt.datetime.fromisoformat(m[1]+('+00:00' if m[3]=='Z' else m[3]))
        epoch=dt.datetime(1970,1,1,tzinfo=UTC);delta=base.astimezone(UTC)-epoch
        result=(delta.days*86400+delta.seconds)*10**9+int((m[2] or '').ljust(9,'0') or '0')
    except ValueError:raise WireError('history_timestamp') from None
    if not 0<=result<=MAX_NS:raise WireError('history_timestamp_boundary')
    return result

def utc(value):
    value=ns(value) if type(value) is str else value
    if type(value) is not int or not 0<=value<=MAX_NS:raise WireError('history_timestamp_boundary')
    s,n=divmod(value,10**9)
    return (dt.datetime(1970,1,1,tzinfo=UTC)+dt.timedelta(seconds=s)).strftime('%Y-%m-%dT%H:%M:%S')+(f'.{n:09d}' if n else '')+'Z'

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

@dataclass(frozen=True)
class HistoricalPermission:
    enabled:bool=False
    cloud:bool=False
    private_display:bool=False
    protocol_reviewed:bool=False
    no_cost:bool=False
    reference:str=''
    feeds:tuple=()
    def require(self,feed):
        if not all(v is True for v in (self.enabled,self.cloud,self.private_display,self.protocol_reviewed,self.no_cost)) or type(self.reference) is not str or not 1<=len(self.reference)<=256 or any(ord(c)<32 or ord(c)>126 for c in self.reference):
            raise WireError('historical_provider_disabled_pending_specific_permissions')
        if feed not in self.feeds or feed not in ('iex','sip'):raise WireError('historical_feed_not_authorized')
    @classmethod
    def configured(cls,e):
        return cls(*(e.get('GIG_ALPACA_HISTORY_'+k)=='1' for k in ('ENABLED','CLOUD_APPROVED','PRIVATE_DISPLAY_APPROVED','PROTOCOL_REVIEWED','NO_COST_CONFIRMED')),e.get('GIG_ALPACA_HISTORY_PERMISSION_REFERENCE',''),tuple(f for f in ('iex','sip') if e.get('GIG_ALPACA_HISTORY_'+f.upper()+'_APPROVED')=='1'))


def validate_query(q,now_ns):
    if type(q) is not dict or set(q)!={'symbol','kind','feed','start','end','timeframe','adjustment','max_pages'}:raise WireError('history_query_fields')
    try:symbol(q['symbol'])
    except (ValueError,TypeError):raise WireError('history_symbol') from None
    if q['kind'] not in ('bars','quotes','trades') or q['feed'] not in ('iex','sip') or q['timeframe'] not in ('1Day','1Hour','1Min') or q['adjustment'] not in ('raw','split','dividend','all') or (q['kind']!='bars' and q['adjustment']!='raw'):
        raise WireError('history_query_profile')
    if type(q['max_pages']) is not int or not 1<=q['max_pages']<=4:raise WireError('history_page_budget')
    lo,hi=ns(q['start']),ns(q['end'])
    maximum=({'1Day':366,'1Hour':31,'1Min':7}[q['timeframe']] if q['kind']=='bars' else 2)*86400*10**9
    if not lo<hi or hi-lo>maximum or hi>now_ns:raise WireError('history_interval')
    if q['feed']=='sip' and hi>now_ns-900*10**9:raise WireError('history_sip_minimum_delay_900_seconds')
    return {**q,'start':utc(lo),'end':utc(hi)}


def validate_plan(method,url,body=None):
    u=urlsplit(url);query=parse_qs(u.query,keep_blank_values=True)
    if method!='GET' or body is not None or u.scheme!='https' or u.netloc!='data.alpaca.markets' or u.path not in ('/v2/stocks/bars','/v2/stocks/quotes','/v2/stocks/trades') or u.fragment or any(len(v)!=1 for v in query.values()):raise WireError('history_fixed_destination')
    allowed={'symbols','start','end','feed','limit','sort','page_token'}|({'timeframe','adjustment'} if u.path.endswith('bars') else set())
    if set(query)-allowed or query.get('limit')!=['64'] or query.get('sort')!=['asc'] or query.get('feed') not in (['iex'],['sip']):raise WireError('history_wire_query')


class HistoricalClient:
    def __init__(self,transport=None,*,permission=HistoricalPermission(),clock=time.time,monotonic=time.monotonic,sleep=asyncio.sleep,identity=None,schedule=None,clock_ns=None):
        if transport is not None and type(transport) not in (FixtureWire,HTTPWire):raise WireError('history_transport_boundary')
        self.transport,self.permission=transport,permission
        self.clock,self.monotonic,self.sleep=clock,monotonic,sleep
        self.now_ns=clock_ns or (time.time_ns if clock is time.time else lambda:int(Decimal(str(clock()))*10**9))
        self.identity=identity or (lambda s:{'symbol':s,'identity_authority':'REQUESTED_IDENTIFIER_NOT_LISTING_VERIFICATION'})
        self.schedule=schedule or SessionSchedule()
        self.lock=asyncio.Lock();self.cache=OrderedDict();self.last_request=None;self.failures=0
    def readiness(self):
        feeds=[];reasons=[]
        for f in ('iex','sip'):
            try:self.permission.require(f);feeds.append(f)
            except WireError as e:reasons.append(e.code)
        return {'schema':'gig.history.readiness.v2','ready':bool(feeds and self.transport),'feeds':feeds,'provider_access_enabled':bool(feeds and self.transport),'transport':'AUTHORED_FIXTURE' if type(self.transport)is FixtureWire else 'DISABLED' if self.transport is None else 'CONFIGURED_HTTP_NOT_QUALIFIED','reason':None if feeds and self.transport else reasons[0] if reasons else 'explicit_server_transport_required','cache_entries':len(self.cache),'cache_limit':16,'ttl_seconds':60,'observed_disk_retention_enabled':False,'licensing':'General personal-use permission does not establish private-cloud/display/historical-feed permission.'}
    def prune(self):
        now=self.monotonic()
        for key,(accepted,_) in list(self.cache.items()):
            if not 0<=now-accepted<60:del self.cache[key]
    def delete(self,identity=None):
        if identity is not None and (type(identity)is not str or not re.fullmatch('[0-9a-f]{64}',identity)):raise WireError('history_cache_identity')
        keys=[k for k,(_,v) in self.cache.items() if identity is None or v['canonical_sha256']==identity]
        for k in keys:del self.cache[k]
        return {'deleted':len(keys),'scope':'in_process_only_no_provider_request'}
    def accepted(self,identity):
        self.prune()
        for _,v in self.cache.values():
            if v['canonical_sha256']==identity:
                self.permission.require(v['feed'])
                return json.loads(canonical(v))
        raise WireError('history_accepted_revision_unavailable_or_expired')
    async def _fetch(self,url):
        for attempt in range(3):
            now=self.monotonic()
            if self.last_request is not None:
                if now<self.last_request:raise WireError('history_clock_regression')
                await self.sleep(max(0,1.01-(now-self.last_request)))
            self.last_request=self.monotonic()
            response=await self.transport.send('GET',url)
            try:return decode(response)
            except WireError as e:
                if e.status!=429 or attempt==2:raise
                if e.retry_after is not None and e.retry_after>5:raise WireError('history_rate_limit_retry_budget',status=429)
                await self.sleep(max(1, e.retry_after or 2**attempt))
        raise WireError('history_retry_budget')
    async def acquire(self,query):
        now_ns=self.now_ns();q=validate_query(query,now_ns);self.permission.require(q['feed'])
        if self.transport is None:raise WireError('history_provider_transport_disabled')
        self.identity(q['symbol'])
        if self.lock.locked():raise WireError('history_busy')
        self.prune();key=hashlib.sha256(canonical(q)).hexdigest()
        if key in self.cache:return {**json.loads(canonical(self.cache[key][1])),'cache_status':'ACCEPTED_MEMORY_REFERENCE'}
        async with self.lock:
            async with asyncio.timeout(30):
                records=[];receipts=[];seen_tokens=set();seen={};trade_ids={};prior=None;token=None;duplicates=0
                for page in range(q['max_pages']):
                    # Delay is checked again before every request;never change feed.
                    self.permission.require(q['feed']);validate_query(q,self.now_ns())
                    params={'symbols':q['symbol'],'start':q['start'],'end':q['end'],'feed':q['feed'],'limit':64,'sort':'asc'}
                    if q['kind']=='bars':params.update(timeframe=q['timeframe'],adjustment=q['adjustment'])
                    if token:params['page_token']=token
                    url=BASE+q['kind']+'?'+urlencode(params);validate_plan('GET',url)
                    payload,digest=await self._fetch(url)
                    if type(payload)is not dict or type(payload.get(q['kind']))is not dict or set(payload[q['kind']])-{q['symbol']} or type(payload[q['kind']].get(q['symbol'],[]))is not list or len(payload[q['kind']].get(q['symbol'],[]))>64:raise WireError('history_page_identity_or_budget')
                    rows=payload[q['kind']].get(q['symbol'],[])
                    for raw in rows:
                        if type(raw)is not dict:raise WireError('history_row_schema')
                        try:
                            exact=ns(raw.get('t'));wire={**raw,'t':utc(exact)}
                            if q['kind']=='bars':r=bars({'symbol':q['symbol'],'bars':[wire]},q['symbol'])['bars'][0]
                            else:r=(quote if q['kind']=='quotes' else trade)({'symbol':q['symbol'],'quote' if q['kind']=='quotes' else 'trade':wire},q['symbol'])
                            annotations={} if q['kind']=='bars' else metadata(raw)
                        except (ValueError,TypeError,KeyError,OverflowError):raise WireError('history_row_schema') from None
                        if not ns(q['start'])<=exact<ns(q['end']):raise WireError('history_record_outside_interval')
                        digest_row=hashlib.sha256(canonical({**r,'annotations':annotations})).hexdigest()
                        if q['kind']=='trades' and 'i' in annotations:
                            trade_key=(annotations.get('x'),annotations['i'],exact)
                            if trade_key in trade_ids and trade_ids[trade_key]!=digest_row:raise WireError('history_conflicting_trade_identity')
                            trade_ids[trade_key]=digest_row
                        if digest_row in seen:duplicates+=1;continue
                        if prior is not None and (exact<prior or q['kind']=='bars' and exact==prior):raise WireError('history_out_of_order_or_conflicting_bar')
                        prior=exact;seen[digest_row]=True
                        records.append({**r,'timestamp':utc(exact),'source_timestamp_ns':str(exact),'source_record_sha256':digest_row,'source_timestamp_text':raw['t'],'record_hash_scope':'normalized_observation_and_supported_annotations','wire_metadata':annotations})
                    receipt_time=utc(self.now_ns())
                    receipts.append({'endpoint':BASE+q['kind'],'page':page+1,'records':len(rows),'sha256':digest,'received_at':receipt_time})
                    token=payload.get('next_page_token')
                    if token in (None,''):break
                    if type(token)is not str or not 1<=len(token)<=512 or any(not 32<ord(c)<127 for c in token) or token in seen_tokens or not rows:raise WireError('history_cursor_loop_or_no_progress')
                    seen_tokens.add(token)
                origin='HISTORICAL_SYNTHETIC' if type(self.transport)is FixtureWire else 'OBSERVED_OFFICIAL_RESPONSE'
                result={'schema':'gig.alpaca.history.v2','query':q,'symbol':q['symbol'],'kind':q['kind'],'feed':q['feed'],'origin':origin,'records':records,'record_count':len(records),'duplicate_records_removed':duplicates,'deduplication_policy':'Identical normalized records collapsed;source receipts retain physical counts;not an exactly-once tape','source_records':receipts,'received_at':receipts[-1]['received_at'],'has_more':token not in (None,''),'complete_history':False,'freshness':'HISTORICAL_NOT_LIVE','adjustment':q['adjustment'],'instrument':self.identity(q['symbol']),'session':self.schedule.at(q['symbol'],records[-1]['timestamp'] if records else None),'clock_window':market_window(records[-1]['timestamp']) if records else None,'coverage':'IEX venue-limited observations' if q['feed']=='iex' else 'Historical SIP requested with minimum900second delay;not real-time entitlement','cache_policy':'16in-process queries,60secondTTL,explicit deletion;no disk retention enabled','limitations':['No full-session/holiday/halt completeness inferred.','Raw prices may contain split/dividend jumps;provider adjustment selection is disclosed,not independently verified.','Quote sizes retain provider units;no depth,queue or aggressor direction inferred.','Source symbols do not independently prove historical security identity.']}
                result['canonical_sha256']=hashlib.sha256(canonical(result)).hexdigest()
                if len(canonical(result))>512*1024:raise WireError('history_result_budget')
                self.cache[key]=(self.monotonic(),result)
                while len(self.cache)>16:self.cache.popitem(last=False)
                return json.loads(canonical(result))
