"""No provider/network calls: exact risk, durable intents and independent fake ledger."""
import asyncio
import copy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from terminal.paper.contracts import (PaperError, ExecutionGate, RiskLimits, cents, intent,
                                      client_id, endpoint, lookup_endpoint, MAX_ORDERS)
from terminal.paper.store import IntentStore
from terminal.paper.fake import FakeBroker
from terminal.paper.engine import PaperEngine

ORDER = dict(symbol='AAPL', side='buy', quantity='1', limit_price='100', type='limit', time_in_force='day')


class Contracts(unittest.TestCase):
    def test_cent_reference(self):
        for s in ('0.01', '1', '7.96', '999999.99', '100.1'):
            self.assertEqual(cents(s), int(Decimal(s) * 100))
    def test_inexact_rejection(self):
        for x in ('1.001', '1e2', '-1', '0', 'NaN', 'Infinity', '01.0', ' 1', '', 1, None):
            with self.subTest(x=x), self.assertRaises(PaperError): cents(x)
    def test_intent_boundaries(self):
        for changes in ({'quantity':'0'}, {'quantity':1}, {'quantity':'1.5'}, {'quantity':'10001'}, {'symbol':'aapl'}, {'symbol':'AAPL/'}, {'type':'market'}, {'time_in_force':'gtc'}, {'side':'short'}, {'extra':1}):
            with self.subTest(changes=changes), self.assertRaises(PaperError): intent({**ORDER, **changes})
        self.assertEqual(intent(ORDER)['limit_price'], '100.00')
    def test_identity_exact_and_stable(self):
        d=intent(ORDER); x=client_id('fake-paper-v1','one',d)
        self.assertEqual(x,client_id('fake-paper-v1','one',d)); self.assertLessEqual(len(x),48)
        self.assertNotEqual(x,client_id('fake-paper-v1','two',d)); self.assertNotEqual(x,client_id('another','one',d))
    def test_endpoint_hosts(self):
        self.assertEqual(endpoint('POST','/v2/orders'),'https://paper-api.alpaca.markets/v2/orders')
        for host in ('https://api.alpaca.markets','http://paper-api.alpaca.markets','https://paper-api.alpaca.markets.evil','https://paper-api.alpaca.markets/'):
            with self.assertRaises(PaperError):endpoint('POST','/v2/orders',host)
        for path in ('//evil','/v2/account?secret=1','/v2/orders/../account'):
            with self.assertRaises(PaperError):endpoint('POST',path)
        self.assertIn('client_order_id=',lookup_endpoint(client_id('x','n',intent(ORDER))))
    def test_independent_gate(self):
        for env in ({},{'GIG_ALPACA_ENABLED':'1'}, {'GIG_PAPER_EXECUTION_ENABLED':'true'}, {'GIG_PAPER_EXECUTION_ENABLED':'1'}):
            with self.assertRaises(PaperError):ExecutionGate.configured(env).require()
        ExecutionGate(True,True,True,'synthetic-test-only').require()
    def test_example_limits_invalid(self):
        for changes in ({'max_open_orders':9},{'max_order_cents':0},{'max_daily_loss_cents':True},{'max_snapshot_age_ms':10001}):
            with self.assertRaises(PaperError):RiskLimits(**changes)


class Paper(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)/'private'
        self.time=1000; self.clock=lambda:self.time
        self.store=IntentStore(self.root); self.broker=FakeBroker(self.store,self.clock)
        self.limits=RiskLimits(max_order_cents=50000,max_position_cents=200000,max_gross_cents=250000)
        self.engine=PaperEngine(self.store,self.broker,limits=self.limits,clock=self.clock)
    def tearDown(self): self.temp.cleanup()
    async def arm(self): await self.engine.arm_demo(True)
    async def order(self, key='one', **values): return await self.engine.submit(key,{**ORDER,**values})
    async def test_default_killed(self):
        with self.assertRaisesRegex(PaperError,'kill_switch'): await self.order()
        self.assertEqual(self.broker.place_calls,0)
    async def test_acknowledgment_required(self):
        with self.assertRaises(PaperError):await self.engine.arm_demo(False)
    async def test_no_real_transport_even_all_gates(self):
        for gate in (ExecutionGate(),ExecutionGate(True,True,True,'fake-permission')):
            e=PaperEngine(self.store,gate=gate,clock=self.clock)
            with self.assertRaises(PaperError):await e.refresh()
    async def test_idempotent_submission(self):
        await self.arm(); a=await self.order(); b=await self.order()
        self.assertEqual(a,b); self.assertEqual(self.broker.place_calls,1)
        with self.assertRaisesRegex(PaperError,'idempotency'):await self.order(quantity='2')
    async def test_partial_full_and_ledger_reference(self):
        await self.arm(); o=await self.order(quantity='3')
        self.broker.event(o['client_id'],'fill',1,'99.00'); await self.engine.refresh()
        s=self.engine.view(); self.assertEqual(s['orders'][0]['state'],'PARTIALLY_FILLED')
        self.assertEqual(s['account']['buying_power_cents'],100000-9900-20000)
        self.broker.event(o['client_id'],'fill',2,'100'); await self.engine.refresh()
        s=self.engine.view(); self.assertEqual(s['orders'][0]['filled_notional_cents'],int(Decimal('299')*100))
        self.assertEqual(s['orders'][0]['state'],'FILLED'); self.assertEqual(s['account']['positions'],{'AAPL':3})
    async def test_overfill_atomic(self):
        await self.arm(); o=await self.order(); before=await self.broker.snapshot()
        for q,p in ((2,'100'),(1,'100.01'),(0,'100'),(1,'100.001')):
            with self.assertRaises(PaperError):self.broker.event(o['client_id'],'fill',q,p)
            self.assertEqual(await self.broker.snapshot(),before)
    async def test_cancel_and_expire_reject(self):
        await self.arm()
        for i,action in enumerate(('cancel','reject','expire')):
            o=await self.order(str(i))
            if action=='cancel':await self.engine.cancel(str(i))
            else:self.broker.event(o['client_id'],action)
            await self.engine.refresh(); self.assertEqual(self.engine.view()['orders'][i]['state'],{'cancel':'CANCELED','reject':'REJECTED','expire':'EXPIRED'}[action])
    async def test_ack_loss_reconcile_no_resend(self):
        await self.arm(); self.broker.failure='after_place'
        with self.assertRaises(PaperError):await self.order()
        self.assertEqual(self.engine.view()['orders'][0]['state'],'UNKNOWN')
        await self.order(); self.assertEqual(self.broker.place_calls,1)
        self.broker.failure=None; await self.engine.refresh()
        self.assertEqual(self.engine.view()['orders'][0]['state'],'ACCEPTED'); self.assertFalse(self.engine.view()['requires_reconciliation'])
    async def test_missing_ack_stays_unknown(self):
        await self.arm(); self.broker.failure='before_place'
        with self.assertRaises(PaperError):await self.order()
        self.broker.failure=None; await self.engine.refresh()
        with self.assertRaisesRegex(PaperError,'unknown_order'):await self.order('two')
        self.assertEqual(self.broker.place_calls,1)
    async def test_cancel_failure_reserves_and_kills(self):
        await self.arm(); await self.order(); self.broker.failure='cancel_timeout'
        with self.assertRaises(PaperError):await self.engine.cancel('one')
        self.assertTrue(self.engine.view()['requires_reconciliation'])
        self.broker.failure=None; await self.engine.kill_and_cancel()
        s=self.engine.view(); self.assertTrue(s['kill_switch']); self.assertEqual(s['orders'][0]['state'],'CANCELED')
    async def test_cancel_rejection_explicit_outstanding(self):
        await self.arm(); await self.order(); self.broker.failure='cancel_reject'
        await self.engine.kill_and_cancel();s=self.engine.view()
        self.assertTrue(s['kill_switch']); self.assertEqual(s['orders'][0]['state'],'CANCEL_REJECTED')
    async def test_closed_unknown_session(self):
        await self.arm()
        for state in ('CLOSED','UNKNOWN'):
            self.broker.scenario(session=state)
            with self.assertRaisesRegex(PaperError,'session_not_verified'):await self.order(state)
    async def test_buying_power(self):
        await self.arm(); self.broker.scenario(cash_cents=5000)
        # Keep daily-loss separate to exercise buying-power guard.
        self.engine.limits=replace(self.limits,max_daily_loss_cents=1000000)
        with self.assertRaisesRegex(PaperError,'buying_power'):await self.order()
    async def test_daily_loss_trips_durable_kill(self):
        await self.arm(); self.broker.scenario(cash_cents=90000)
        await self.engine.refresh(); self.assertTrue(self.store.read()['kill'])
        with self.assertRaisesRegex(PaperError,'daily_loss'):await self.engine.arm_demo(True)
    async def test_notional_eligibility_distance(self):
        await self.arm()
        for expected, values in (('notional',{'quantity':'6'}),('eligible',{'symbol':'ZZZZ'}),('far_from',{'limit_price':'110'})):
            with self.assertRaisesRegex(PaperError,expected):await self.order(expected,**values)
    async def test_position_and_gross_reservations(self):
        await self.arm(); self.engine.limits=replace(self.limits,max_position_cents=15000)
        await self.order()
        with self.assertRaisesRegex(PaperError,'position_exposure'):await self.order('two')
        self.engine.limits=replace(self.limits,max_gross_cents=20000)
        with self.assertRaisesRegex(PaperError,'gross_exposure'):await self.order('three',symbol='NVDA',limit_price='150')
    async def test_sell_requires_unreserved_position(self):
        await self.arm()
        with self.assertRaisesRegex(PaperError,'short_or_reserved'):await self.order(side='sell')
        o=await self.order();self.broker.event(o['client_id'],'fill',1,'100');await self.engine.refresh()
        await self.order('sell',side='sell')
        with self.assertRaisesRegex(PaperError,'short_or_reserved'):await self.order('again',side='sell')
    async def test_open_order_limit(self):
        await self.arm();self.engine.limits=replace(self.limits,max_open_orders=2)
        await self.order('1');await self.order('2')
        with self.assertRaisesRegex(PaperError,'open_order_limit'):await self.order('3')
    async def test_clock_regression(self):
        await self.arm();self.time-=1
        with self.assertRaisesRegex(PaperError,'clock_regression'):await self.order()
    async def test_snapshot_boundaries(self):
        good=await self.broker.snapshot()
        for changes in ({'at_ms':-1},{'at_ms':999999},{'at_ms':-5001},{'verified':False},{'paper':False},{'account_id':'LIVE'},{'positions':{'UNKNOWN':1}},{'buying_power_cents':-1}):
            with self.subTest(changes=changes),self.assertRaises(PaperError):self.engine._snapshot({**good,**changes},self.time)
    async def test_snapshot_failure_clears_account(self):
        await self.arm();self.broker.failure='snapshot'
        with self.assertRaises(PaperError):await self.engine.refresh()
        self.assertIsNone(self.engine.view()['account'])
    async def test_unknown_external_order_rejected(self):
        await self.arm();await self.broker.place(intent(ORDER),client_id('foreign','x',intent(ORDER)))
        with self.assertRaisesRegex(PaperError,'external_order'):await self.engine.refresh()
    async def test_terminal_and_identity_regressions(self):
        await self.arm();r=await self.order();self.broker.event(r['client_id'],'fill',1,'100');await self.engine.refresh()
        local=self.store.read()['orders']['one'];remote=(await self.broker.snapshot())['orders'][r['client_id']]
        for changes in ({'state':'ACCEPTED'},{'filled_notional_cents':10001},{'broker_id':'different'},{'intent':{**remote['intent'],'symbol':'MSFT'}}):
            with self.assertRaises(PaperError):self.engine._record(local,{**remote,**changes})
    async def test_each_fill_increment_preserves_limit(self):
        await self.arm();r=await self.order(quantity='2');self.broker.event(r['client_id'],'fill',1,'50');await self.engine.refresh()
        local=self.store.read()['orders']['one'];remote=(await self.broker.snapshot())['orders'][r['client_id']]
        # Aggregate average100 disguises an invalid150 second execution;must reject.
        with self.assertRaisesRegex(PaperError,'incremental_fill_price'):
            self.engine._record(local,{**remote,'state':'FILLED','filled_qty':2,'filled_notional_cents':20000})
        with self.assertRaises(PaperError):self.engine._record(local,{**remote,'filled_notional_cents':5001})
    async def test_contradictory_accepted_fill_rejected(self):
        await self.arm();r=await self.order(quantity='2');local=self.store.read()['orders']['one']
        remote=(await self.broker.snapshot())['orders'][r['client_id']]
        with self.assertRaisesRegex(PaperError,'fill_state'):
            self.engine._record(local,{**remote,'state':'ACCEPTED','filled_qty':1,'filled_notional_cents':10000})
    async def test_commit_failure_prevents_send(self):
        await self.arm();before=self.store.read();counter=0
        def fail():
            nonlocal counter
            counter+=1
            if counter==2:raise MemoryError('authored allocation failure')
        self.store.before_commit=fail
        with self.assertRaises(MemoryError):await self.order()
        self.store.before_commit=None
        self.assertEqual(self.broker.place_calls,0);self.assertEqual(self.store.read()['orders'],before['orders'])
    async def test_ack_commit_failure_retains_unknown(self):
        await self.arm();count=0
        def fail():
            nonlocal count
            count+=1
            if count==3:raise MemoryError('authored post-send failure')
        self.store.before_commit=fail
        with self.assertRaises(MemoryError):await self.order()
        self.store.before_commit=None
        self.assertEqual(self.broker.place_calls,1);self.assertTrue(self.engine.view()['requires_reconciliation'])
        await self.engine.refresh();self.assertEqual(self.engine.view()['orders'][0]['state'],'ACCEPTED')
    async def test_task_cancellation_durable_unknown(self):
        await self.arm();original=self.broker.place
        async def wait(*a):await asyncio.sleep(10)
        self.broker.place=wait;task=asyncio.create_task(self.order())
        for _ in range(100):
            await asyncio.sleep(.001)
            if self.store.read()['orders']:break
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        self.broker.place=original;self.assertTrue(self.engine.view()['requires_reconciliation'])
    async def test_durable_restart_and_backup(self):
        await self.arm();o=await self.order();self.broker.event(o['client_id'],'fill',1,'99.50')
        backup=Path(self.temp.name)/'backup';backup.mkdir(mode=0o700)
        with self.store.connection() as source,sqlite3.connect(backup/'paper-demo.sqlite3') as dest:source.backup(dest)
        os.chmod(backup/'paper-demo.sqlite3',0o600)
        for root in (self.root,backup):
            store=IntentStore(root);fake=FakeBroker(store,self.clock);e=PaperEngine(store,fake,limits=self.limits,clock=self.clock)
            await e.refresh();self.assertEqual(e.view()['orders'][0]['filled_notional_cents'],9950)
            self.assertEqual(e.view()['account']['positions'],{'AAPL':1})
    async def test_corrupt_state_hash_and_missing_fake(self):
        await self.arm();await self.order()
        with self.store.connection() as db:db.execute("UPDATE state SET payload=? WHERE id=1",(b'{}',))
        with self.assertRaises(PaperError):self.store.read()
    async def test_corrupt_fake_contract_safe(self):
        with self.store.connection() as db:
            raw=b'{invalid';db.execute('UPDATE fake SET payload=?,digest=? WHERE id=1',(raw,hashlib.sha256(raw).hexdigest()))
        with self.assertRaisesRegex(PaperError,'fake_contract'):await self.engine.refresh()
        self.assertIsNone(self.engine.account)
    async def test_audit_overflow_rejected_bounded(self):
        # Corrupted/overfull input is read with a2049-row limit,not an unbounded fetch.
        import terminal.paper.store as store_module
        from unittest.mock import patch
        with patch.object(store_module,'MAX_AUDIT',3):
            self.store.mutate('ONE',lambda s:None);self.store.mutate('TWO',lambda s:None)
            before=self.store.read()
            with self.assertRaisesRegex(PaperError,'audit_capacity'):
                self.store.mutate('THREE',lambda s:s.__setitem__('kill',False))
            self.assertEqual(self.store.read(),before)
    async def test_mutation_contract_rollback(self):
        before=self.store.read()
        with self.assertRaises(PaperError):self.store.mutate('BAD',lambda s:s.__setitem__('kill','no'))
        self.assertEqual(self.store.read(),before)
    async def test_real_process_interruption_rolls_back(self):
        before=self.store.read()
        code="from terminal.paper.store import IntentStore; import os,sys; s=IntentStore(sys.argv[1],before_commit=lambda:os._exit(23)); s.mutate('AUTHORED_CRASH',lambda x:x.__setitem__('kill',False))"
        r=subprocess.run([sys.executable,'-c',code,str(self.root)],timeout=5,check=False)
        self.assertEqual(r.returncode,23);self.assertEqual(self.store.read(),before)
    async def test_file_permissions_and_symlinks(self):
        self.assertEqual(self.store.path.stat().st_mode&0o777,0o600)
        link=Path(self.temp.name)/'link';link.symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(PaperError):IntentStore(link)
        os.chmod(self.root,0o755)
        with self.assertRaises(PaperError):IntentStore(self.root)
    async def test_capacity_rejection(self):
        # Bounded maximum,without sending128 orders merely to test a dictionary boundary.
        state=self.store.read();record={'client_id':'','intent':intent(ORDER),'state':'SUBMITTED','filled_qty':0,'filled_notional_cents':0,'broker_id':None,'uncertain':True}
        for i in range(MAX_ORDERS+1):
            key=str(i);state['orders'][key]={**record,'client_id':client_id(state['profile'],key,intent(ORDER))}
        with self.assertRaises(PaperError):self.store.mutate('CAPACITY',lambda s:s.update(state))
        self.assertEqual(len(self.store.read()['orders']),0)


if __name__=='__main__':unittest.main()
