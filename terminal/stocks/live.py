"""Bounded IEX MessagePack stream,official alpaca-py protocol profile.
No network on construction/import. Explicit owner gates and lifecycle required.
"""
import asyncio,datetime,hashlib,json,math,time
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
        if v<0 or v>10**15 or (positive and v==0):raise ProtocolError('price_numeric')
        return repr(v)
    return decimal(v,positive)

class LiveIEX:
    def __init__(self,workspace,*,connector=None,clock=time.monotonic,wall=time.time):
        self.workspace=workspace;self.connector=connector;self.clock=clock;self.wall=wall
        self.task=None;self.stop_event=asyncio.Event();self.state='DISABLED';self.phase='DISCONNECTED';self.symbols=();self.latest={};self.seen=[];self.receipts=0;self.duplicates=0;self.generation=0;self.failures=0;self.reason=None;self.last_data=None;self.channels=('quotes','trades');self.history=[];self.out_of_order=0;self.evicted=0
    def symbol_limit(self):
        value=self.workspace.environment.get('GIG_ALPACA_LIVE_MAX_SYMBOLS','4')
        if value not in ('1','2','3','4'):raise ValueError('live_invalid_symbol_limit')
        return int(value)
    def require(self):
        self.symbol_limit()
        keys=self.workspace.permission('alpaca')
        if self.workspace.environment.get('GIG_ALPACA_LIVE_ENABLED')!='1':raise ValueError('live_explicit_enable_required')
        return keys
    def process(self,raw):
        # Accepted event dictionaries are never edited by process();copy containers only.
        # All new rows/counters are staged until the complete frame validates.
        candidate=(self.phase,dict(self.latest),list(self.seen),self.receipts,self.duplicates,self.last_data,list(self.history),self.out_of_order,self.evicted)
        phase,latest,seen,count,dups,last,history,late_count,evicted=candidate;out=[];received=self.clock();wall_ns=int(self.wall()*10**9)
        for row in unpack(raw):
            t=row.get('T')
            if t=='error':raise ProtocolError('provider_error_'+str(row.get('code'))[:8] if type(row.get('code')) is int else 'provider_error')
            if t=='success':
                if phase=='CONNECTED_PENDING' and row.get('msg')=='connected':phase='AUTH_PENDING'
                elif phase=='AUTH_SENT' and row.get('msg')=='authenticated':phase='SUBSCRIBE_PENDING'
                else:raise ProtocolError('unexpected_success')
            elif t=='subscription':
                if phase!='SUBSCRIBE_SENT' or any(type(row.get(k)) is not list or len(row[k])!=len(self.symbols) or any(type(s) is not str for s in row[k]) or set(row[k])!=set(self.symbols) for k in self.channels) or any(v for k,v in row.items() if k not in ('T',*self.channels)):raise ProtocolError('subscription_mismatch')
                phase='SUBSCRIBED'
            elif t in ('q','t','b','c','x'):
                if phase!='SUBSCRIBED' or row.get('S') not in self.symbols:raise ProtocolError('unsubscribed_observation')
                source_time=stamp(row.get('t'));ns=int(timestamp_ns(source_time))
                if ns>wall_ns+5_000_000_000:raise ProtocolError('future_source_timestamp')
                ticker=row['S'];kind={'q':'quote','t':'trade','b':'bar','c':'correction','x':'cancel'}[t]
                channel={'q':'quotes','t':'trades','b':'bars','c':'trades','x':'trades'}[t]
                if channel not in self.channels:raise ProtocolError('unrequested_channel')
                def reference(v):
                    if type(v) is int and 0<=v<2**64:return str(v)
                    if type(v) is str and 1<=len(v)<=64 and all(32<ord(c)<127 for c in v):return v
                    raise ProtocolError('invalid_trade_reference')
                if t=='q':data={'bid':amount(row['bp']),'ask':amount(row['ap']),'bid_size':amount(row['bs']),'ask_size':amount(row['as'])}
                elif t=='t':data={'price':amount(row['p'],True),'size':amount(row['s'],True)}
                elif t=='b':
                    data={k:amount(row[f],True) for k,f in [('open','o'),('high','h'),('low','l'),('close','c')]};data['volume']=amount(row['v'])
                    if not Decimal(data['low'])<=min(Decimal(data['open']),Decimal(data['close']))<=max(Decimal(data['open']),Decimal(data['close']))<=Decimal(data['high']):raise ProtocolError('invalid_bar_ohlc')
                elif t=='c':data={'original_id':reference(row['oi']),'corrected_id':reference(row['ci']),'original_price':amount(row['op'],True),'corrected_price':amount(row['cp'],True),'original_size':amount(row['os'],True),'corrected_size':amount(row['cs'],True),'policy':'correction observation only;no automatic tape/book rewrite'}
                else:data={'trade_id':reference(row['i']),'price':amount(row['p'],True),'size':amount(row['s'],True),'action':reference(row['a']),'policy':'cancel/error observation only;no automatic liquidity restoration'}
                conditions={}
                for name in (('oc','cc') if t=='c' else ('c',) if t in ('q','t') else ()):
                    if name not in row:continue
                    value=row[name]
                    if value is not None and (type(value) is not list or len(value)>32 or any(type(v) is not str or not 1<=len(v)<=16 or any(ord(ch)<32 or ord(ch)>126 for ch in v) for v in value)):raise ProtocolError('invalid_conditions')
                    conditions[name]=value
                import msgpack
                identity=hashlib.sha256(msgpack.packb(row)).hexdigest()
                if identity in seen:dups+=1;continue
                seen=(seen+[identity])[-256:];count+=1;last=received
                previous=latest.get(ticker+':'+kind);late=bool(previous and ns<int(previous['source_timestamp_ns']));late_count+=int(late)
                event={'provider':'alpaca','feed':'iex','symbol':ticker,'kind':kind,'timestamp':source_time,'source_timestamp_ns':str(ns),'source_sha256':hashlib.sha256(raw).hexdigest(),'identity_sha256':identity,'receipt_index':count,'generation':self.generation,'out_of_order':late,'received_at':datetime.datetime.fromtimestamp(self.wall(),datetime.timezone.utc).isoformat(),'exchange_codes':{k:reference(row[k]) for k in ('x','bx','ax') if k in row},'conditions':conditions,'tape_code':reference(row['z']) if 'z' in row else None,'trade_id':reference(row['i']) if t=='t' and 'i' in row else None,'clock_quality':'SOURCE_AHEAD_WITHIN_TOLERANCE' if ns>wall_ns else 'UNSYNCHRONIZED_SOURCE_RECEIVE_CLOCKS','origin':'HISTORICAL_SYNTHETIC' if self.connector else 'OBSERVED_OFFICIAL_RESPONSE','source_age_at_receipt_ns':str(max(0,wall_ns-ns)),'received_monotonic':received,'data':data,'numeric_policy':'MessagePack binary64 uses shortest roundtrip decimal;wire hex retained;not exact exchange ticks','wire_binary64':{k:v.hex() for k,v in row.items() if type(v) is float},'scope':'Single-venue IEX only;not SIP/NBBO/depth;no native book mutation','size_unit':'provider_reported_unverified_no_lot_conversion'}
                if not late:latest[ticker+':'+kind]=event
                history.append(event)
                if len(history)>256:history.pop(0);evicted+=1
                out.append(event)
            else:raise ProtocolError('unsupported_message_type')
        self.phase,self.latest,self.seen,self.receipts,self.duplicates,self.last_data,self.history,self.out_of_order,self.evicted=phase,latest,seen,count,dups,last,history,late_count,evicted
        return out
    def view(self):
        from .live_metrics import metrics
        from .prices import market_window
        now=self.clock()
        def present(event):
            row={k:v for k,v in event.items() if k!='received_monotonic'};age=max(0,now-event['received_monotonic']);source_age=int(event['source_age_at_receipt_ns'])+int(age*10**9)
            row['receive_age_seconds']=age
            row['state']='UNAVAILABLE' if self.phase!='SUBSCRIBED' or event['generation']!=self.generation else 'STALE' if max(int(age*10**9),source_age)>(120_000_000_000 if event['kind']=='bar' else 30_000_000_000) else 'SIMULATED' if self.connector else 'LIVE'
            return row
        try:self.require();ready={'ready':True,'reason':None,'symbol_limit':self.symbol_limit()}
        except ValueError as exc:ready={'ready':False,'reason':str(exc)[:128],'symbol_limit':None}
        rows=[present(e) for e in self.latest.values()];history=[present(e) for e in self.history if e['symbol'] in self.symbols]
        return {'schema':'gig.alpaca.live.v1','state':self.state,'phase':self.phase,'symbols':list(self.symbols),'channels':list(self.channels),'generation':self.generation,'accepted_observations':self.receipts,'duplicate_observations':self.duplicates,'out_of_order_observations':self.out_of_order,'retained_history_limit':256,'retention_evictions':self.evicted,'history':history,'readiness':ready,'metrics':{s:metrics(self.history,s,self.generation) for s in self.symbols},'sessions':{s:market_window(next(r['timestamp'] for r in reversed(history) if r['symbol']==s)) if any(r['symbol']==s for r in history) else {'authority':'No source observations;market open/closed unavailable'} for s in self.symbols},'consecutive_failures':self.failures,'reason':self.reason,'observations':rows,'authorization':'existing provider gates plus explicit live enable;not independent entitlement verification','backpressure':{'websocket_frame_capacity':4,'frame_bytes_limit':32768,'queue_depth':'NOT_INSTRUMENTED','missing_source_observations':'UNKNOWN_NO_EXCHANGE_SEQUENCE'},'limitations':['256-identity dedup and256-event retention,not complete tape/exactly-once','No exchange sequence or market-open/calendar authority inferred','Corrections/cancels are observations;trade-derived volume not reconciled','Dynamic symbol changes replace one shared upstream connection;no in-place delta subscriptions','No observed acceptance from offline fixtures']}
    async def start(self,symbols,channels=None):
        self.require()
        if type(symbols) is not list or not 1<=len(symbols)<=self.symbol_limit() or len(set(symbols))!=len(symbols):raise ValueError('live_symbol_budget')
        for s in symbols:instrument(s)
        channels=('quotes','trades') if channels is None else channels
        if type(channels) not in (list,tuple) or not channels or len(channels)>3 or any(c not in ('quotes','trades','bars') for c in channels) or len(set(channels))!=len(channels):raise ValueError('live_channel_budget')
        selected=tuple(sorted(symbols));chosen=tuple(sorted(channels))
        if self.task and not self.task.done() and self.symbols==selected and tuple(sorted(self.channels))==chosen:return
        await self.close();self.latest={};self.symbols=selected;self.channels=chosen;self.stop_event=asyncio.Event();self.state='CONNECTING';self.reason=None;self.task=asyncio.create_task(self.run())
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
                                await ws.send(msgpack.packb({'action':'subscribe',**{c:list(self.symbols) for c in self.channels}}));self.phase='SUBSCRIBE_SENT'
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
