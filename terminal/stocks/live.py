"""Bounded IEX MessagePack stream,official alpaca-py protocol profile.
No network on construction/import. Explicit owner gates and lifecycle required.
"""
import asyncio,copy,datetime,hashlib,json,math,time
from decimal import Decimal
from .identity import instrument
from .prices import timestamp,decimal
from terminal.providers.kraken import timestamp_ns

ENDPOINT='wss://stream.data.alpaca.markets/v2/iex'
class ProtocolError(ValueError):pass

def unpack(raw):
    import msgpack
    if type(raw) is not bytes or not 1<=len(raw)<=32768:raise ProtocolError('binary_frame_budget')
    def pairs(rows):
        out={}
        for k,v in rows:
            if type(k) is not str or k in out:raise ProtocolError('duplicate_or_invalid_key')
            out[k]=v
        return out
    try:rows=msgpack.unpackb(raw,raw=False,strict_map_key=True,object_pairs_hook=pairs,max_array_len=128,max_map_len=32,max_str_len=512,max_bin_len=32768,max_ext_len=12)
    except (ValueError,TypeError,OverflowError) as exc:raise ProtocolError('invalid_messagepack') from None
    if type(rows) is not list or not 1<=len(rows)<=128 or any(type(r) is not dict for r in rows):raise ProtocolError('batch_budget')
    return rows

def stamp(v):
    import msgpack
    if isinstance(v,msgpack.Timestamp):
        try:return datetime.datetime.fromtimestamp(v.seconds,datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')+f'.{v.nanoseconds:09d}Z'
        except (ValueError,OverflowError,OSError):raise ProtocolError('timestamp_range') from None
    timestamp(v);return v

def amount(v,positive=False):
    # Source MessagePack binary64 remains explicitly disclosed,not exchange tick exactness.
    if type(v) is float:
        if not math.isfinite(v):raise ProtocolError('nonfinite_price')
        v=repr(v)
    return decimal(v,positive)

class LiveIEX:
    def __init__(self,workspace,*,connector=None,clock=time.monotonic,wall=time.time):
        self.workspace=workspace;self.connector=connector;self.clock=clock;self.wall=wall
        self.task=None;self.stop_event=asyncio.Event();self.state='DISABLED';self.phase='DISCONNECTED';self.symbols=();self.latest={};self.seen=[];self.receipts=0;self.duplicates=0;self.generation=0;self.failures=0;self.reason=None;self.last_data=None
    def require(self):
        keys=self.workspace.permission('alpaca')
        if self.workspace.environment.get('GIG_ALPACA_LIVE_ENABLED')!='1':raise ValueError('live_explicit_enable_required')
        return keys
    def process(self,raw):
        candidate=copy.deepcopy((self.phase,self.latest,self.seen,self.receipts,self.duplicates,self.last_data))
        phase,latest,seen,count,dups,last=candidate;out=[];received=self.clock();wall_ns=int(self.wall()*10**9)
        for row in unpack(raw):
            t=row.get('T')
            if t=='error':raise ProtocolError('provider_error_'+str(row.get('code'))[:8] if type(row.get('code')) is int else 'provider_error')
            if t=='success':
                if phase=='CONNECTED_PENDING' and row.get('msg')=='connected':phase='AUTH_PENDING'
                elif phase=='AUTH_SENT' and row.get('msg')=='authenticated':phase='SUBSCRIBE_PENDING'
                else:raise ProtocolError('unexpected_success')
            elif t=='subscription':
                if phase!='SUBSCRIBE_SENT' or any(type(row.get(k)) is not list or len(row[k])!=len(self.symbols) or any(type(s) is not str for s in row[k]) or set(row[k])!=set(self.symbols) for k in ('quotes','trades')) or any(v for k,v in row.items() if k not in ('T','quotes','trades')):raise ProtocolError('subscription_mismatch')
                phase='SUBSCRIBED'
            elif t in ('q','t'):
                if phase!='SUBSCRIBED' or row.get('S') not in self.symbols:raise ProtocolError('unsubscribed_observation')
                source_time=stamp(row.get('t'));ns=int(timestamp_ns(source_time))
                if ns>wall_ns+5_000_000_000:raise ProtocolError('future_source_timestamp')
                ticker=row['S'];kind='quote' if t=='q' else 'trade'
                data=({'bid':amount(row['bp']),'ask':amount(row['ap']),'bid_size':amount(row['bs']),'ask_size':amount(row['as'])} if t=='q' else {'price':amount(row['p'],True),'size':amount(row['s'],True)})
                import msgpack
                identity=hashlib.sha256(msgpack.packb(row)).hexdigest()
                if identity in seen:dups+=1;continue
                seen=(seen+[identity])[-256:];count+=1;last=received
                event={'provider':'alpaca','feed':'iex','symbol':ticker,'kind':kind,'timestamp':source_time,'source_timestamp_ns':str(ns),'source_sha256':hashlib.sha256(raw).hexdigest(),'identity_sha256':identity,'receipt_index':count,'generation':self.generation,'origin':'HISTORICAL_SYNTHETIC' if self.connector else 'OBSERVED_OFFICIAL_RESPONSE','source_age_at_receipt_ns':str(max(0,wall_ns-ns)),'received_monotonic':received,'data':data,'numeric_policy':'MessagePack binary64 uses shortest roundtrip decimal;wire hex retained;not exact exchange ticks','wire_binary64':{k:v.hex() for k,v in row.items() if type(v) is float},'scope':'Single-venue IEX only;not SIP/NBBO/depth;no native book mutation','size_unit':'provider_reported_unverified_no_lot_conversion'}
                latest[ticker+':'+kind]=event;out.append(event)
            else:raise ProtocolError('unsupported_message_type')
        self.phase,self.latest,self.seen,self.receipts,self.duplicates,self.last_data=phase,latest,seen,count,dups,last
        return out
    def view(self):
        now=self.clock();rows=[]
        for event in self.latest.values():
            row={k:v for k,v in event.items() if k!='received_monotonic'};age=max(0,now-event['received_monotonic']);source_age=int(event['source_age_at_receipt_ns'])+int(age*10**9)
            row['receive_age_seconds']=age
            row['state']='UNAVAILABLE' if self.phase!='SUBSCRIBED' else 'STALE' if max(int(age*10**9),source_age)>30_000_000_000 else 'SIMULATED' if self.connector else 'LIVE';rows.append(row)
        return {'schema':'gig.alpaca.live.v1','state':self.state,'phase':self.phase,'symbols':list(self.symbols),'generation':self.generation,'accepted_observations':self.receipts,'duplicate_observations':self.duplicates,'consecutive_failures':self.failures,'reason':self.reason,'observations':rows,'authorization':'existing provider gates plus explicit live enable;not independent entitlement verification','limitations':['256-identity bounded dedup window;no global exactly-once claim','No exchange sequence invented;out-of-order source times preserved','Trade corrections/cancels and unknown message families fail explicitly','No observed acceptance from offline fixtures']}
    async def start(self,symbols):
        self.require()
        if type(symbols) is not list or not 1<=len(symbols)<=4 or len(set(symbols))!=len(symbols):raise ValueError('live_symbol_budget')
        for s in symbols:instrument(s)
        await self.close();self.symbols=tuple(sorted(symbols));self.stop_event=asyncio.Event();self.state='CONNECTING';self.reason=None;self.task=asyncio.create_task(self.run())
    async def close(self):
        self.stop_event.set()
        if self.task and not self.task.done():
            self.task.cancel()
            try:await self.task
            except asyncio.CancelledError:pass
        self.task=None;self.phase='DISCONNECTED';self.state='STOPPED'
    async def run(self):
        import msgpack
        from websockets.asyncio.client import connect
        class FixedEndpoint(connect):
            def process_redirect(self,error):return error
        connector=self.connector or FixedEndpoint
        try:
            while not self.stop_event.is_set():
                try:
                    keys=self.require();self.generation+=1;self.phase='CONNECTED_PENDING';self.latest={};self.state='CONNECTING';self.last_data=None
                    async with connector(ENDPOINT,additional_headers={'Content-Type':'application/msgpack'},open_timeout=10,close_timeout=3,ping_interval=20,ping_timeout=10,max_size=32768,max_queue=4) as ws:
                        subscribed_at=None
                        while not self.stop_event.is_set():
                            raw=await asyncio.wait_for(ws.recv(),15 if self.phase!='SUBSCRIBED' else 30)
                            if self.phase=='SUBSCRIBED' and self.clock()-(self.last_data if self.last_data is not None else subscribed_at)>30:raise TimeoutError('market_data_stale')
                            accepted=self.process(raw)
                            if accepted:self.failures=0
                            if self.phase=='AUTH_PENDING':
                                await ws.send(msgpack.packb({'action':'auth','key':keys['APCA-API-KEY-ID'],'secret':keys['APCA-API-SECRET-KEY']}));self.phase='AUTH_SENT'
                            elif self.phase=='SUBSCRIBE_PENDING':
                                await ws.send(msgpack.packb({'action':'subscribe','quotes':list(self.symbols),'trades':list(self.symbols)}));self.phase='SUBSCRIBE_SENT'
                            elif self.phase=='SUBSCRIBED':
                                if subscribed_at is None:subscribed_at=self.clock()
                                self.state='SUBSCRIBED'
                except ProtocolError as exc:
                    self.state='FAILED';self.reason=str(exc)[:64];self.phase='DISCONNECTED';return
                except (ValueError,KeyError,TypeError,OverflowError):
                    self.state='FAILED';self.reason='protocol_or_authorization_rejected';self.phase='DISCONNECTED';return
                except (OSError,TimeoutError,ConnectionError):
                    self.phase='DISCONNECTED';self.state='BACKOFF';self.failures+=1;self.reason='transport_or_data_timeout'
                except Exception:
                    # WebSocket closure/handshake failures never log exception text or keys.
                    self.phase='DISCONNECTED';self.state='BACKOFF';self.failures+=1;self.reason='transport_closed'
                if self.failures>=5:self.state='FAILED';self.reason='retry_budget_exhausted';return
                try:await asyncio.wait_for(self.stop_event.wait(),min(30,2**min(self.failures,5)))
                except asyncio.TimeoutError:pass
        finally:self.phase='DISCONNECTED'
