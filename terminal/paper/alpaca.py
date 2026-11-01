"""Paper-only Alpaca protocol adapter. No startup network/account/credential access.

REST double-collection is NOT an exchange-atomic snapshot. Real admission requires
an explicit,expiring reviewed exclusive-account/reconciliation policy. No such
real policy/session is enabled by this assignment. All exercised traffic is fake.
"""
import asyncio
from dataclasses import dataclass
from decimal import Decimal,InvalidOperation
import hashlib,json,re,time,uuid
from urllib.parse import urlencode,urlsplit,parse_qs
from terminal.alpaca_wire import FixtureWire,HTTPWire,WireError,decode
from terminal.stocks.historical_v2 import ns,utc
from .contracts import PaperError,ExecutionGate,canonical,intent,integer,MAX_ORDERS,ACTIVE

HOST='https://paper-api.alpaca.markets'
MAX_FILLS=512

def exact_money(value,positive=False):
    if type(value)is not str or not re.fullmatch(r'(?:0|[1-9]\d{0,10})(?:\.\d{1,12})?',value):raise PaperError('paper_money_schema')
    number=Decimal(value)*100
    if number!=number.to_integral_value():raise PaperError('paper_subcent_account_value_unsupported')
    return integer(int(number),1 if positive else 0,10**12)

def shares(value):
    if type(value)is not str or not re.fullmatch(r'(?:0|[1-9]\d{0,4})(?:\.\d{1,12})?',value):raise PaperError('paper_quantity_schema')
    number=Decimal(value)
    if number!=number.to_integral_value():raise PaperError('paper_fractional_position_unsupported')
    return integer(int(number),0,10000)

def identifier(value):
    if type(value)is not str:
        raise PaperError('paper_provider_identity')
    try:
        if str(uuid.UUID(value))!=value:raise ValueError()
    except ValueError:raise PaperError('paper_provider_identity') from None
    return value

@dataclass(frozen=True)
class PaperAuthorization:
    execution:ExecutionGate=ExecutionGate()
    provider_enabled:bool=False
    cloud_reviewed:bool=False
    private_display:bool=False
    protocol_reviewed:bool=False
    audit_retention_reviewed:bool=False
    exclusive_account_reviewed:bool=False
    reconciliation_reviewed:bool=False
    no_cost:bool=False
    account_id:str=''
    session_start:str=''
    expires_ms:int=0
    risk_sha256:str=''
    def require(self,now_ms):
        self.execution.require()
        if not all(v is True for v in (self.provider_enabled,self.cloud_reviewed,self.private_display,self.protocol_reviewed,self.audit_retention_reviewed,self.exclusive_account_reviewed,self.reconciliation_reviewed,self.no_cost)):
            raise PaperError('paper_provider_specific_qualification_disabled')
        identifier(self.account_id)
        if type(self.risk_sha256)is not str or not re.fullmatch('[0-9a-f]{64}',self.risk_sha256):raise PaperError('paper_reviewed_risk_binding_required')
        try:start=ns(self.session_start)//10**6
        except ValueError:raise PaperError('paper_qualification_time') from None
        if type(now_ms)is not int or type(self.expires_ms)is not int or not start<=now_ms<self.expires_ms or self.expires_ms-start>15*60*1000:
            raise PaperError('paper_qualification_session_expired_or_invalid')
    def profile(self):
        identifier(self.account_id)
        try:start=ns(self.session_start)//10**6
        except ValueError:raise PaperError('paper_qualification_time') from None
        return 'alpaca-paper-v1:'+hashlib.sha256(self.account_id.encode()).hexdigest()+':'+str(start)


def validate_plan(method,url,body=None):
    u=urlsplit(url);q=parse_qs(u.query,keep_blank_values=True)
    if u.scheme!='https' or u.netloc!='paper-api.alpaca.markets' or u.fragment or any(len(v)!=1 for v in q.values()):raise PaperError('paper_live_or_dynamic_destination_rejected')
    if method=='GET' and body is None:
        if u.path in ('/v2/account','/v2/positions','/v2/clock') and not q:return
        if u.path=='/v2/orders' and q=={'status':['open'],'limit':['128'],'direction':['asc'],'nested':['false']}:return
        if u.path=='/v2/orders:by_client_order_id' and set(q)=={'client_order_id'} and re.fullmatch('gatlas-paper-[0-9a-f]{32}',q['client_order_id'][0]):return
        if re.fullmatch('/v2/assets/[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?',u.path) and not q:return
        if u.path=='/v2/account/activities/FILL' and set(q)<={'after','direction','page_size','page_token'} and q.get('direction')==['asc'] and q.get('page_size')==['100'] and 'after' in q:
            ns(q['after'][0]);return
    if method=='POST' and u.path=='/v2/orders' and not q and type(body)is dict:
        if set(body)=={'symbol','side','qty','limit_price','type','time_in_force','client_order_id','extended_hours'} and body['extended_hours'] is False and re.fullmatch('gatlas-paper-[0-9a-f]{32}',str(body['client_order_id'])):
            intent({'symbol':body['symbol'],'side':body['side'],'quantity':body['qty'],'limit_price':body['limit_price'],'type':body['type'],'time_in_force':body['time_in_force']});return
    if method=='DELETE' and body is None and not q and re.fullmatch('/v2/orders/[0-9a-f-]{36}',u.path):
        identifier(u.path.rsplit('/',1)[1]);return
    raise PaperError('paper_endpoint_or_order_profile_rejected')


class AlpacaPaperBroker:
    def __init__(self,store,transport=None,*,authorization=PaperAuthorization(),clock=None,monotonic=time.monotonic,sleep=asyncio.sleep,reference=None):
        if transport is not None and type(transport) not in (FixtureWire,HTTPWire):raise PaperError('paper_transport_boundary')
        self.store,self.transport,self.authorization=store,transport,authorization
        self.clock=clock or (lambda:time.time_ns()//10**6);self.monotonic,self.sleep=monotonic,sleep
        self.reference=reference;self.symbols=set();self.last_request=None;self.revision=store.read()['snapshot_revision'];self.notifications=[]
        if store.read()['profile']!=authorization.profile():raise PaperError('paper_account_session_store_binding')
        with store.connection() as db:
            db.execute('CREATE TABLE IF NOT EXISTS executions(id TEXT PRIMARY KEY,order_id TEXT NOT NULL,payload BLOB NOT NULL,digest TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS baseline(id INTEGER PRIMARY KEY CHECK(id=1),payload BLOB NOT NULL,digest TEXT NOT NULL)')
    def require(self):
        self.authorization.require(self.clock())
        if self.transport is None:raise PaperError('paper_provider_transport_disabled')
    async def _request(self,method,path,body=None):
        self.require();url=HOST+path;validate_plan(method,url,body)
        now=self.monotonic()
        if self.last_request is not None:
            if now<self.last_request:raise PaperError('paper_monotonic_clock_regression')
            await self.sleep(max(0,.36-(now-self.last_request)))
        self.last_request=self.monotonic()
        try:
            response=await self.transport.send(method,url,body)
            return decode(response)
        except WireError as e:
            # Never retry create/cancel,including429/5xx/ambiguous transport errors.
            raise PaperError(e.code) from None
    async def prepare_symbol(self,symbol):
        self.require();intent({'symbol':symbol,'side':'buy','quantity':'1','limit_price':'1','type':'limit','time_in_force':'day'})
        if len(self.symbols)>=32 and symbol not in self.symbols:raise PaperError('paper_symbol_budget')
        raw,_=await self._request('GET','/v2/assets/'+symbol)
        if type(raw)is not dict or raw.get('symbol')!=symbol or raw.get('asset_class')!='us_equity' or raw.get('status')!='active' or raw.get('tradable') is not True:raise PaperError('paper_instrument_not_eligible')
        self.symbols.add(symbol)
    def _account(self,v):
        if type(v)is not dict or v.get('id')!=self.authorization.account_id or v.get('status')!='ACTIVE' or v.get('currency')!='USD' or any(v.get(k)is not False for k in ('account_blocked','trading_blocked','trade_suspended_by_user')):
            raise PaperError('paper_account_identity_status_or_blocked')
        return {k:exact_money(v.get(k)) for k in ('cash','equity','last_equity','buying_power','non_marginable_buying_power')}
    def _positions(self,v):
        if type(v)is not list or len(v)>32:raise PaperError('paper_positions_budget')
        result={}
        for p in v:
            if type(p)is not dict or p.get('asset_class')!='us_equity' or p.get('side')!='long':raise PaperError('paper_position_profile')
            s=p.get('symbol');intent({'symbol':s,'side':'buy','quantity':'1','limit_price':'1','type':'limit','time_in_force':'day'})
            if s in result:raise PaperError('paper_duplicate_position')
            q=shares(p.get('qty'));available=shares(p.get('qty_available'))
            if available>q:raise PaperError('paper_position_availability')
            result[s]=q
        return result
    def _definition(self,v):
        if type(v)is not dict or v.get('asset_class')!='us_equity' or v.get('extended_hours') is not False:raise PaperError('paper_order_profile')
        q=shares(v.get('qty'));p=exact_money(v.get('limit_price'),True)
        return intent({'symbol':v.get('symbol'),'side':v.get('side'),'quantity':str(q),'limit_price':f'{p//100}.{p%100:02d}','type':v.get('type'),'time_in_force':v.get('time_in_force')})
    def _fills(self,order_id):
        q=value=0
        with self.store.connection() as db:
            rows=db.execute('SELECT payload,digest FROM executions WHERE order_id=? LIMIT ?',(order_id,MAX_FILLS+1)).fetchall()
        if len(rows)>MAX_FILLS:raise PaperError('paper_fill_budget')
        for raw,digest in rows:
            if type(raw)is not bytes or len(raw)>2048 or hashlib.sha256(raw).hexdigest()!=digest:raise PaperError('paper_fill_integrity')
            v=json.loads(raw);q+=v['qty'];value+=v['price_cents']*v['qty']
        return q,value
    def _normalize(self,v):
        definition=self._definition(v);order_id=identifier(v.get('id'));identity=v.get('client_order_id')
        if type(identity)is not str or not re.fullmatch('gatlas-paper-[0-9a-f]{32}',identity):raise PaperError('paper_unowned_order')
        qty=shares(v.get('filled_qty'));q,value=self._fills(order_id)
        if qty!=q:raise PaperError('paper_exact_fill_activities_required')
        mapping={'new':'ACCEPTED','accepted':'ACCEPTED','pending_new':'SUBMITTED','partially_filled':'PARTIALLY_FILLED','filled':'FILLED','canceled':'CANCELED','expired':'EXPIRED','rejected':'REJECTED','pending_cancel':'CANCEL_REQUESTED'}
        state=mapping.get(v.get('status'))
        if state is None:raise PaperError('paper_unsupported_broker_order_state')
        local=next((r for r in self.store.read()['orders'].values() if r['client_id']==identity),None)
        if local and local['state'] in ('CANCEL_REQUESTED','UNKNOWN') and local['broker_id'] and state in ('ACCEPTED','PARTIALLY_FILLED','SUBMITTED'):
            rejected=any(n['event']=='order_cancel_rejected' and n['client_id']==identity for n in self.notifications)
            state='CANCEL_REJECTED' if rejected else 'CANCEL_REQUESTED'
        return {'client_id':identity,'broker_id':order_id,'intent':definition,'state':state,'filled_qty':q,'filled_notional_cents':value}
    async def _activities(self,known):
        token=None;seen=set();pending=[]
        for _ in range(3):
            params={'after':self.authorization.session_start,'direction':'asc','page_size':100}
            if token:params['page_token']=token
            rows,_=await self._request('GET','/v2/account/activities/FILL?'+urlencode(params))
            if type(rows)is not list or len(rows)>100:raise PaperError('paper_activity_page_budget')
            for r in rows:
                if type(r)is not dict or r.get('activity_type')!='FILL':raise PaperError('paper_activity_profile')
                oid=identifier(r.get('order_id'));identity=r.get('id')
                if oid not in known:raise PaperError('paper_unowned_fill_activity')
                if type(identity)is not str or not 1<=len(identity)<=128 or any(not 32<ord(c)<127 for c in identity):raise PaperError('paper_execution_identity')
                stamp=r.get('transaction_time')
                if not ns(self.authorization.session_start)<=ns(stamp)<=self.clock()*10**6:raise PaperError('paper_activity_time')
                qty=shares(r.get('qty'));price=exact_money(r.get('price'),True)
                if not qty or r.get('side')!=known[oid]['side'] or r.get('symbol')!=known[oid]['symbol']:raise PaperError('paper_activity_order_disagreement')
                record={'id':identity,'order_id':oid,'symbol':r['symbol'],'side':r['side'],'qty':qty,'price_cents':price,'source_time':stamp}
                pending.append(record)
            if len(rows)<100:break
            token=rows[-1]['id']
            if token in seen:raise PaperError('paper_activity_cursor_loop')
            seen.add(token)
        else:raise PaperError('paper_activity_incomplete_prefix')
        def apply(db,state):
            for r in pending:
                raw=canonical(r);digest=hashlib.sha256(raw).hexdigest();old=db.execute('SELECT payload,digest FROM executions WHERE id=?',(r['id'],)).fetchone()
                if old:
                    if old!=(raw,digest):raise PaperError('paper_conflicting_execution_identity')
                    continue
                if db.execute('SELECT count(*) FROM executions').fetchone()[0]>=MAX_FILLS:raise PaperError('paper_fill_budget')
                db.execute('INSERT INTO executions VALUES(?,?,?,?)',(r['id'],r['order_id'],raw,digest))
        self.store.transact('EXECUTION_ACTIVITIES_RECONCILED',apply)
    async def _collect(self):
        a,_=await self._request('GET','/v2/account');p,_=await self._request('GET','/v2/positions');o,_=await self._request('GET','/v2/orders?'+urlencode({'status':'open','limit':128,'direction':'asc','nested':'false'}))
        account=self._account(a);positions=self._positions(p)
        if type(o)is not list or len(o)>=128:raise PaperError('paper_open_orders_incomplete_or_budget')
        identities=[identifier(r.get('id')) for r in o if type(r)is dict]
        if len(identities)!=len(o) or len(set(identities))!=len(o):raise PaperError('paper_duplicate_or_invalid_order')
        return account,positions,sorted(o,key=lambda r:r['id'])
    async def snapshot(self):
        self.require();first=await self._collect();second=await self._collect()
        if first!=second:raise PaperError('paper_unstable_rest_snapshot')
        account,positions,raw_orders=second;local=self.store.read()['orders']
        by_client={r['client_id']:r for r in local.values()};known={}
        for raw in raw_orders:
            if raw.get('client_order_id') not in by_client:raise PaperError('paper_external_open_order')
            known[identifier(raw.get('id'))]=self._definition(raw)
        for r in local.values():
            if r['state'] in ACTIVE and not any(v.get('client_order_id')==r['client_id'] for v in raw_orders):
                try:raw,_=await self._request('GET','/v2/orders:by_client_order_id?'+urlencode({'client_order_id':r['client_id']}))
                except PaperError as e:
                    if e.code=='provider_http_404':continue # Unknown stays unknown,no blind resend.
                    raise
                raw_orders.append(raw);known[identifier(raw.get('id'))]=self._definition(raw)
            elif r['broker_id']:
                known[r['broker_id']]=r['intent']
        await self._activities(known)
        orders={}
        for r in raw_orders:
            normalized=self._normalize(r)
            if normalized['client_id'] in orders:raise PaperError('paper_duplicate_order')
            orders[normalized['client_id']]=normalized
        clock,_=await self._request('GET','/v2/clock')
        if type(clock)is not dict or type(clock.get('is_open'))is not bool or abs(ns(clock.get('timestamp'))//10**6-self.clock())>5000:raise PaperError('paper_clock_unknown_or_stale')
        marks={}
        for symbol in sorted(self.symbols|set(positions)):
            if self.reference is None:raise PaperError('paper_authorized_price_reference_unavailable')
            ref=self.reference(symbol)
            if type(ref)is not dict or ref.get('symbol')!=symbol or ref.get('feed')!='iex' or ref.get('origin')!=('HISTORICAL_SYNTHETIC' if type(self.transport)is FixtureWire else 'OBSERVED_OFFICIAL_RESPONSE') or type(ref.get('at_ms'))is not int or not 0<=self.clock()-ref['at_ms']<=5000:
                raise PaperError('paper_price_reference_unverified_or_stale')
            marks[symbol]=integer(ref.get('price_cents'),1,100000000)
        def baseline(db,state):
            row=db.execute('SELECT payload,digest FROM baseline WHERE id=1').fetchone()
            if row is None:
                if local or raw_orders:raise PaperError('paper_initial_account_baseline_missing')
                value={'positions':positions,'cash_cents':account['cash'],'account_sha256':hashlib.sha256(self.authorization.account_id.encode()).hexdigest()}
                raw=canonical(value);db.execute('INSERT INTO baseline VALUES(1,?,?)',(raw,hashlib.sha256(raw).hexdigest()))
                return
            raw,digest=row
            if type(raw)is not bytes or len(raw)>16384 or hashlib.sha256(raw).hexdigest()!=digest:raise PaperError('paper_account_baseline_integrity')
            expected=json.loads(raw);p=dict(expected['positions']);cash=expected['cash_cents']
            fills=db.execute('SELECT payload,digest FROM executions LIMIT ?',(MAX_FILLS+1,)).fetchall()
            if len(fills)>MAX_FILLS:raise PaperError('paper_fill_budget')
            for raw,digest in fills:
                if hashlib.sha256(raw).hexdigest()!=digest:raise PaperError('paper_fill_integrity')
                f=json.loads(raw);sign=1 if f['side']=='buy' else -1;p[f['symbol']]=p.get(f['symbol'],0)+sign*f['qty'];cash-=sign*f['qty']*f['price_cents']
            if {s:q for s,q in p.items() if q}!={s:q for s,q in positions.items() if q}:raise PaperError('paper_position_reconciliation')
            if cash!=account['cash']:raise PaperError('paper_cash_unexplained_fee_or_movement')
        self.store.transact('ACCOUNT_BASELINE_OR_RECONCILIATION',baseline)
        self.revision=max(self.revision,self.store.read()['snapshot_revision'])+1
        return {'classification':'HISTORICAL_SYNTHETIC' if type(self.transport)is FixtureWire else 'OBSERVED_PAPER_RESPONSE','account_id':self.authorization.account_id,'paper':True,'verified':True,'coherent':True,'coherence_authority':'EXPLICIT_EXCLUSIVE_ACCOUNT_POLICY_AND_STABLE_DOUBLE_READ_NOT_EXCHANGE_ATOMIC','revision':self.revision,'at_ms':self.clock(),'session':'OPEN' if clock['is_open'] else 'CLOSED','equity_cents':account['equity'],'opening_equity_cents':account['last_equity'],'buying_power_cents':min(account['buying_power'],account['non_marginable_buying_power'],account['cash']),'positions':positions,'marks':marks,'orders':orders,'limits':'Whole-share USD exact-cent long-only profile;no unexplained cash movements or fractional/subcent accounting'}
    async def place(self,definition,identity):
        self.require();definition=intent(definition)
        if self.store.read()['profile']!=self.authorization.profile():raise PaperError('paper_store_account_binding')
        body={**definition,'qty':definition['quantity'],'client_order_id':identity,'extended_hours':False};del body['quantity']
        raw,_=await self._request('POST','/v2/orders',body)
        # An immediate fill without independently reconciled activities remains
        # ambiguous to the caller;durable intent must be reconciled,not resent.
        return self._normalize(raw)
    async def cancel(self,identity):
        self.require();raw,_=await self._request('GET','/v2/orders:by_client_order_id?'+urlencode({'client_order_id':identity}))
        oid=identifier(raw.get('id'));await self._request('DELETE','/v2/orders/'+oid)
        raw,_=await self._request('GET','/v2/orders:by_client_order_id?'+urlencode({'client_order_id':identity}))
        return self._normalize(raw) #204is request acknowledgment,not proof of cancellation.
    def observe_update(self,raw):
        self.require()
        if type(raw)is not dict or raw.get('event') not in ('new','partial_fill','fill','canceled','expired','rejected','pending_cancel','order_cancel_rejected') or type(raw.get('order'))is not dict:raise PaperError('paper_trade_update_unsupported')
        identity=raw['order'].get('client_order_id')
        if not any(r['client_id']==identity for r in self.store.read()['orders'].values()):raise PaperError('paper_unowned_trade_update')
        digest=hashlib.sha256(canonical(raw)).hexdigest()
        if not any(v['sha256']==digest for v in self.notifications):self.notifications.append({'event':raw['event'],'client_id':identity,'sha256':digest,'classification':'RECONCILIATION_HINT_NOT_FILL_ACCOUNTING'})
        self.notifications=self.notifications[-32:]
        return {'reconciliation_required':True,'event':raw['event'],'sha256':digest}
