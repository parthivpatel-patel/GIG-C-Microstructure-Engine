"""Independent authored Alpaca wire/account/fill ledger,not provider qualification."""
import asyncio,copy,datetime,hashlib,json,tempfile,unittest
from dataclasses import replace
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from terminal.alpaca_wire import FixtureWire,WireResponse,WireError
from terminal.stocks.historical_v2 import ns,utc
from .alpaca import AlpacaPaperBroker,PaperAuthorization,exact_money,shares,validate_plan
from .contracts import ExecutionGate,RiskLimits,PaperError,canonical
from .engine import PaperEngine
from .store import IntentStore

ACCOUNT='00000000-0000-0000-0000-000000000001'
START='2024-01-02T14:30:00Z'
ORDER=dict(symbol='AAPL',side='buy',quantity='1',limit_price='100',type='limit',time_in_force='day')
LIMITS=RiskLimits(max_order_cents=50000,max_position_cents=200000,max_gross_cents=250000)
GATE=ExecutionGate(True,True,True,'AUTHORED_OFFLINE_TEST_NOT_OWNER_PERMISSION')

def money(c):return f'{c//100}.{c%100:02d}'
def response(v,status=200):return WireResponse(status,b'' if status==204 else json.dumps(v).encode())
class Clock:
 def __init__(self):self.ms=ns(START)//10**6;self.mono=1
 def now(self):return self.ms
 def monotonic(self):return self.mono
 async def sleep(self,s):self.ms+=round(s*1000);self.mono+=s

class Provider:
 """Independent exact integer account;raw average price is deliberately not an oracle."""
 def __init__(self,clock):self.clock=clock;self.cash=100000;self.positions={};self.orders={};self.activities=[];self.post_calls=0;self.failure=None;self.id=0;self.open=True;self.account_reads=0
 def raw_account(self):return dict(id=ACCOUNT,status='ACTIVE',currency='USD',account_blocked=False,trading_blocked=False,trade_suspended_by_user=False,cash=money(self.cash),equity=money(self.cash+sum(q*10000 for q in self.positions.values())),last_equity='1000.00',buying_power=money(self.cash-sum((int(o['qty'])-int(o['filled_qty']))*10000 for o in self.orders.values() if o['status']in('new','partially_filled','pending_cancel'))),non_marginable_buying_power=money(self.cash))
 def call(self,method,url,body):
  path=urlsplit(url).path;q=parse_qs(urlsplit(url).query)
  if self.failure=='429':return response({'message':'credential-redaction-sentinel'},429)
  if path=='/v2/account':
   v=self.raw_account();self.account_reads+=1
   if self.failure=='unstable':v['cash']=money(self.cash+self.account_reads)
   if self.failure=='blocked':v['trading_blocked']=True
   if self.failure=='wrong_account':v['id']='00000000-0000-0000-0000-000000000002'
   return response(v)
  if path=='/v2/positions':return response([dict(symbol=s,asset_class='us_equity',side='long',qty=str(n),qty_available=str(n))for s,n in self.positions.items() if n])
  if path.startswith('/v2/assets/'):
   return response(dict(symbol=path.rsplit('/',1)[1],asset_class='us_equity',status='inactive' if self.failure=='asset' else 'active',tradable=True))
  if path=='/v2/clock':return response(dict(timestamp=utc(self.clock.ms*10**6),is_open=self.open))
  if path=='/v2/account/activities/FILL':return response(self.activities)
  if path=='/v2/orders' and method=='GET':return response([v for v in self.orders.values() if v['status']in('new','partially_filled','pending_cancel')])
  if path=='/v2/orders' and method=='POST':
   self.post_calls+=1
   if self.failure=='post429':return response({},429)
   if self.failure=='before_post':raise WireError('wire_transport_unknown')
   if self.failure=='reject':return response({'message':'credential-redaction-sentinel'},422)
   self.id+=1;oid=f'00000000-0000-0000-0001-{self.id:012d}'
   o={**body,'id':oid,'asset_class':'us_equity','filled_qty':'0','status':'new','filled_avg_price':None};self.orders[body['client_order_id']]=o
   if self.failure=='after_post':raise WireError('wire_transport_unknown')
   return response(o)
  if path=='/v2/orders:by_client_order_id':return response(self.orders[q['client_order_id'][0]]) if q['client_order_id'][0]in self.orders else response({},404)
  if path.startswith('/v2/orders/') and method=='DELETE':
   o=next(v for v in self.orders.values() if v['id']==path.rsplit('/',1)[1])
   if self.failure=='cancel_lost':raise WireError('wire_transport_unknown')
   if self.failure=='fill_during_cancel':self.fill(o['client_order_id'],int(o['qty'])-int(o['filled_qty']),10000);return response(None,204)
   if self.failure=='cancel_pending':o['status']='new'
   elif o['status']!='filled':o['status']='canceled'
   return response(None,204)
  raise AssertionError((method,path))
 def fill(self,identity,qty,price):
  o=self.orders[identity];sign=1 if o['side']=='buy' else -1
  self.cash-=sign*qty*price;self.positions[o['symbol']]=self.positions.get(o['symbol'],0)+sign*qty
  o['filled_qty']=str(int(o['filled_qty'])+qty);o['status']='filled' if o['filled_qty']==o['qty'] else 'partially_filled'
  o['filled_avg_price']='99.666666667' #Deliberately rounded/irrelevant;use individual activities.
  self.activities.append(dict(activity_type='FILL',id='execution-'+str(len(self.activities)),order_id=o['id'],symbol=o['symbol'],side=o['side'],qty=str(qty),price=money(price),transaction_time=utc(self.clock.ms*10**6)))

class Contracts(unittest.TestCase):
 def test_exact_units(self):
  self.assertEqual(exact_money('123.4500'),12345);self.assertEqual(shares('2.000'),2)
  for v in ('0.001','-1','NaN',1,None):
   with self.assertRaises(PaperError):exact_money(v)
  for v in ('1.5','10001',1):
   with self.assertRaises(PaperError):shares(v)
 def test_live_host_rejected(self):
  for url in ('https://api.alpaca.markets/v2/account','https://paper-api.alpaca.markets.evil/v2/account','http://paper-api.alpaca.markets/v2/account','https://paper-api.alpaca.markets/v2/account?x=1'):
   with self.assertRaises(PaperError):validate_plan('GET',url)
 def test_no_market_extended_order(self):
  from .contracts import client_id,intent
  body={**ORDER,'qty':'1','client_order_id':client_id('p','x',intent(ORDER)),'extended_hours':False};del body['quantity']
  validate_plan('POST','https://paper-api.alpaca.markets/v2/orders',body)
  for change in ({'type':'market'},{'extended_hours':True},{'qty':'1.5'},{'limit_price':'100.001'}):
   with self.assertRaises(PaperError):validate_plan('POST','https://paper-api.alpaca.markets/v2/orders',{**body,**change})
 def test_default_authorization_closed(self):
  with self.assertRaises(PaperError):PaperAuthorization().require(ns(START)//10**6)

class Integration(unittest.IsolatedAsyncioTestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.clock=Clock();self.provider=Provider(self.clock);self.wire=FixtureWire(self.provider.call)
  self.authorization=PaperAuthorization(GATE,True,True,True,True,True,True,True,True,ACCOUNT,START,self.clock.ms+900000,hashlib.sha256(canonical(LIMITS.view())).hexdigest())
  self.root=Path(self.temp.name)/'private';self.store=IntentStore(self.root,profile=self.authorization.profile())
  self.broker=self.make_broker();self.engine=PaperEngine(self.store,self.broker,gate=GATE,limits=LIMITS,clock=self.clock.now)
 def tearDown(self):self.temp.cleanup()
 def make_broker(self):return AlpacaPaperBroker(self.store,self.wire,authorization=self.authorization,clock=self.clock.now,monotonic=self.clock.monotonic,sleep=self.clock.sleep,reference=lambda s:dict(symbol=s,feed='iex',origin='HISTORICAL_SYNTHETIC',at_ms=self.clock.ms,price_cents=10000))
 async def arm(self):await self.engine.arm_demo(True)
 async def order(self,key='one',**changes):return await self.engine.submit(key,{**ORDER,**changes})
 async def test_default_engine_gate_never_calls_transport(self):
  e=PaperEngine(self.store,self.broker,clock=self.clock.now)
  with self.assertRaises(PaperError):await e.refresh()
  self.assertEqual(self.wire.calls,[])
 async def test_missing_transport_view_is_disabled(self):
  e=PaperEngine(self.store,clock=self.clock.now);v=e.view()
  self.assertEqual(v['mode'],'DISABLED');self.assertEqual(v['classification'],'UNAVAILABLE');self.assertFalse(v['external_execution_enabled'])
 async def test_submit_identity_and_profile(self):
  await self.arm();a=await self.order();b=await self.order()
  self.assertEqual(a,b);self.assertEqual(self.provider.post_calls,1)
  self.assertEqual(a['state'],'ACCEPTED');self.assertEqual(self.engine.view()['classification'],'UNAVAILABLE') #Account invalidated by send until reconcile.
  await self.engine.refresh();self.assertEqual(self.engine.view()['classification'],'HISTORICAL_SYNTHETIC');self.assertFalse(self.engine.view()['external_execution_enabled'])
 async def test_fill_uses_activities_not_rounded_average(self):
  await self.arm();r=await self.order(quantity='3');self.provider.fill(r['client_id'],1,9900);await self.engine.refresh()
  self.assertEqual(self.store.read()['orders']['one']['state'],'PARTIALLY_FILLED')
  self.provider.fill(r['client_id'],2,10000);await self.engine.refresh();v=self.engine.view()
  self.assertEqual(v['orders'][0]['filled_notional_cents'],29900);self.assertEqual(v['account']['positions'],{'AAPL':3})
 async def test_lost_ack_reconcile_without_resend(self):
  await self.arm();self.provider.failure='after_post'
  with self.assertRaises(PaperError):await self.order()
  self.assertTrue(self.engine.view()['requires_reconciliation']);await self.order();self.assertEqual(self.provider.post_calls,1)
  self.provider.failure=None;await self.engine.refresh();self.assertEqual(self.engine.view()['orders'][0]['state'],'ACCEPTED')
 async def test_unknown_absence_not_resubmitted(self):
  await self.arm();self.provider.failure='before_post'
  with self.assertRaises(PaperError):await self.order()
  self.provider.failure=None;await self.engine.refresh();await self.order()
  self.assertEqual(self.provider.post_calls,1);self.assertTrue(self.engine.view()['requires_reconciliation'])
 async def test_partial_cancel_and_race(self):
  await self.arm();r=await self.order(quantity='2');self.provider.fill(r['client_id'],1,10000);await self.engine.refresh();await self.engine.cancel('one');await self.engine.refresh()
  v=self.engine.view();self.assertEqual(v['orders'][0]['state'],'CANCELED');self.assertEqual(v['account']['positions'],{'AAPL':1})
 async def test_cancel_ack_not_terminal(self):
  await self.arm();await self.order();self.provider.failure='cancel_pending';await self.engine.cancel('one');await self.engine.refresh()
  self.assertEqual(self.engine.view()['orders'][0]['state'],'CANCEL_REQUESTED');self.assertTrue(self.engine.view()['requires_reconciliation'])
 async def test_cancel_timeout_and_kill(self):
  await self.arm();await self.order();self.provider.failure='cancel_lost'
  with self.assertRaises(PaperError):await self.engine.cancel('one')
  self.engine.kill();self.assertTrue(self.store.read()['kill']);self.assertTrue(self.engine.view()['requires_reconciliation'])
 async def test_restart_preserves_fills_and_exposure(self):
  await self.arm();r=await self.order();self.provider.fill(r['client_id'],1,9900);await self.engine.refresh()
  self.store=IntentStore(self.root,profile=self.authorization.profile());self.broker=self.make_broker();e=PaperEngine(self.store,self.broker,gate=GATE,limits=LIMITS,clock=self.clock.now);e.kill();await e.refresh()
  self.assertTrue(e.view()['kill_switch']);self.assertEqual(e.view()['account']['positions'],{'AAPL':1});self.assertEqual(e.view()['orders'][0]['filled_notional_cents'],9900)
 async def test_duplicate_activity_idempotent_and_conflict_atomic(self):
  await self.arm();r=await self.order();self.provider.fill(r['client_id'],1,10000);self.provider.activities.append(copy.deepcopy(self.provider.activities[0]));await self.engine.refresh()
  self.assertEqual(self.engine.view()['orders'][0]['filled_qty'],1)
  self.provider.activities[-1]['price']='99.00'
  with self.assertRaisesRegex(PaperError,'conflicting_execution'):await self.engine.refresh()
 async def test_unknown_account_and_blocked(self):
  for state in ('wrong_account','blocked'):
   self.provider.failure=state
   with self.assertRaises(PaperError):await self.arm()
  self.assertEqual(self.provider.post_calls,0)
 async def test_session_closed_prevents_order(self):
  await self.arm();self.provider.open=False
  with self.assertRaisesRegex(PaperError,'session_not_verified'):await self.order()
  self.assertEqual(self.provider.post_calls,0)
 async def test_expired_session_no_credential_or_wire(self):
  self.clock.ms=self.authorization.expires_ms
  with self.assertRaises(PaperError):await self.arm()
  self.assertEqual(self.wire.calls,[])
 async def test_risk_review_hash_binding(self):
  self.engine.limits=replace(LIMITS,max_order_cents=50001)
  with self.assertRaisesRegex(PaperError,'risk_binding'):await self.arm()
  self.assertEqual(self.wire.calls,[])
 async def test_asset_ineligible(self):
  await self.arm();self.provider.failure='asset'
  with self.assertRaises(PaperError):await self.order()
  self.assertEqual(self.provider.post_calls,0)
 async def test_unknown_mark_and_stale(self):
  await self.arm();self.broker.reference=None
  with self.assertRaisesRegex(PaperError,'price_reference'):await self.order()
  self.broker.reference=lambda s:dict(symbol=s,feed='iex',origin='HISTORICAL_SYNTHETIC',at_ms=0,price_cents=10000)
  with self.assertRaisesRegex(PaperError,'stale'):await self.order()
 async def test_unexplained_cash_fails_closed(self):
  await self.arm();self.provider.cash-=1
  with self.assertRaisesRegex(PaperError,'cash_unexplained'):await self.engine.refresh()
  self.assertIsNone(self.engine.account)
 async def test_position_mismatch(self):
  await self.arm();self.provider.positions['AAPL']=1
  with self.assertRaisesRegex(PaperError,'position_reconciliation'):await self.engine.refresh()
 async def test_external_order_rejected(self):
  await self.arm();fake={**ORDER,'qty':'1','client_order_id':'foreign','extended_hours':False};del fake['quantity'];self.provider.call('POST','https://paper-api.alpaca.markets/v2/orders',fake)
  with self.assertRaisesRegex(PaperError,'external_open_order'):await self.engine.refresh()
 async def test_rate_limit_never_retries_creation(self):
  await self.arm();self.provider.failure='post429'
  with self.assertRaisesRegex(PaperError,'429'):await self.order()
  self.assertEqual(self.provider.post_calls,1);await self.order();self.assertEqual(self.provider.post_calls,1)
  self.assertTrue(self.engine.view()['requires_reconciliation'])
 async def test_cancel_fill_race_requires_execution_reconciliation(self):
  await self.arm();await self.order();self.provider.failure='fill_during_cancel'
  with self.assertRaisesRegex(PaperError,'activities_required'):await self.engine.cancel('one')
  self.assertTrue(self.engine.view()['requires_reconciliation']);self.provider.failure=None;await self.engine.refresh()
  self.assertEqual(self.engine.view()['orders'][0]['state'],'FILLED');self.assertEqual(self.engine.view()['account']['positions'],{'AAPL':1})
 async def test_rejected_and_expired_are_explicit_terminal_states(self):
  await self.arm()
  for index,state in enumerate(('rejected','expired')):
   r=await self.order(str(index));self.provider.orders[r['client_id']]['status']=state;await self.engine.refresh()
   self.assertEqual(self.store.read()['orders'][str(index)]['state'],state.upper())
 async def test_unsupported_replacement_state_not_lossily_mapped(self):
  await self.arm();r=await self.order();self.provider.orders[r['client_id']]['status']='replaced'
  with self.assertRaisesRegex(PaperError,'unsupported_broker_order_state'):await self.engine.refresh()
  self.assertIsNone(self.engine.account)
 async def test_unstable_rest_boundary_rejected(self):
  self.provider.failure='unstable'
  with self.assertRaisesRegex(PaperError,'unstable_rest'):await self.arm()
  self.assertEqual(self.store.read()['orders'],{})
 async def test_missing_execution_history_never_invents_notional(self):
  await self.arm();r=await self.order();self.provider.fill(r['client_id'],1,10000);self.provider.activities=[]
  with self.assertRaisesRegex(PaperError,'activities_required'):await self.engine.refresh()
  self.assertEqual(self.store.read()['orders']['one']['filled_qty'],0)
 async def test_execution_commit_allocation_failure_rolls_back(self):
  await self.arm();r=await self.order();self.provider.fill(r['client_id'],1,10000)
  self.store.before_commit=lambda:(_ for _ in ()).throw(MemoryError('authored fault'))
  with self.assertRaises(PaperError):await self.engine.refresh()
  self.store.before_commit=None
  with self.store.connection() as db:self.assertEqual(db.execute('SELECT count(*) FROM executions').fetchone()[0],0)
  await self.engine.refresh();self.assertEqual(self.engine.view()['orders'][0]['filled_qty'],1)
 async def test_duplicate_trade_updates_are_only_hints(self):
  await self.arm();r=await self.order();raw={'event':'fill','order':{'client_order_id':r['client_id']}}
  self.broker.observe_update(raw);self.broker.observe_update(raw)
  self.assertEqual(len(self.broker.notifications),1);self.assertEqual(self.store.read()['orders']['one']['filled_qty'],0)
 async def test_store_account_binding(self):
  with self.assertRaises(PaperError):IntentStore(self.root,profile=self.authorization.profile().replace('1704205800000','1704205800001'))

if __name__=='__main__':unittest.main()
