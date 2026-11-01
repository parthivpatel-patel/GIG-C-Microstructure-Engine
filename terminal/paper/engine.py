"""Fail-closed intent admission/reconciliation;no default broker/network transport."""
import asyncio
import copy
import time
from .contracts import (PaperError, ExecutionGate, RiskLimits, ACTIVE, TERMINAL,
                        STATES, MAX_ORDERS, cents, intent, nonce, client_id, integer)
from .fake import FakeBroker


class PaperEngine:
    def __init__(self, store, broker=None, *, gate=ExecutionGate(), limits=RiskLimits(), clock=None):
        self.store, self.broker, self.gate, self.limits = store, broker, gate, limits
        self.clock = clock or (lambda: time.time_ns() // 1_000_000)
        self.lock = asyncio.Lock(); self.account = None

    def _transport(self):
        if not isinstance(self.broker, FakeBroker):
            self.gate.require()
            # A future separately qualified adapter must establish account/order
            # coherence. No credentials or network factory exists in this sprint.
            raise PaperError('paper_network_transport_not_qualified')

    def _now(self):
        return integer(self.clock(), 0, 2**63 - 1)

    async def _call(self, method, *args):
        self._transport()
        try:
            return await asyncio.wait_for(method(*args), 2)
        except asyncio.CancelledError:
            raise
        except PaperError:
            raise
        except Exception:
            raise PaperError('paper_transport_unknown_requires_reconciliation') from None

    def _record(self, local, remote):
        if type(remote) is not dict or remote.get('client_id') != local['client_id'] or remote.get('intent') != local['intent'] or remote.get('state') not in STATES:
            raise PaperError('paper_broker_order_identity_or_state')
        filled = integer(remote.get('filled_qty'), local['filled_qty'], int(local['intent']['quantity']))
        value = integer(remote.get('filled_notional_cents'), local['filled_notional_cents'])
        state = remote['state']
        if (state == 'FILLED' and filled != int(local['intent']['quantity'])) or (state == 'PARTIALLY_FILLED' and not 0 < filled < int(local['intent']['quantity'])) or (state == 'REJECTED' and filled):
            raise PaperError('paper_broker_fill_state')
        total = int(local['intent']['quantity'])
        if (filled == total and state != 'FILLED') or (state in ('ACCEPTED', 'SUBMITTED', 'REJECTED') and filled):
            raise PaperError('paper_broker_fill_state')
        delta_quantity = filled - local['filled_qty']
        delta_value = value - local['filled_notional_cents']
        limit = cents(local['intent']['limit_price'])
        if (delta_quantity == 0 and delta_value != 0) or (delta_quantity and (delta_value <= 0 or (local['intent']['side'] == 'buy' and delta_value > limit * delta_quantity) or (local['intent']['side'] == 'sell' and delta_value < limit * delta_quantity))):
            raise PaperError('paper_broker_incremental_fill_price')
        if local['state'] in TERMINAL and (state != local['state'] or filled != local['filled_qty'] or value != local['filled_notional_cents']):
            raise PaperError('paper_terminal_state_regression')
        if local['broker_id'] is not None and remote.get('broker_id') != local['broker_id']:
            raise PaperError('paper_broker_identity_changed')
        if type(remote.get('broker_id')) is not str or not 1 <= len(remote['broker_id']) <= 100 or any(ord(c) < 33 or ord(c) > 126 for c in remote['broker_id']):
            raise PaperError('paper_broker_identity')
        limit = cents(local['intent']['limit_price'])
        if (not filled and value) or (filled and (value <= 0 or (local['intent']['side'] == 'buy' and value > limit * filled) or (local['intent']['side'] == 'sell' and value < limit * filled))):
            raise PaperError('paper_broker_fill_price')
        return {**local, 'state': state, 'filled_qty': filled, 'filled_notional_cents': value,
                'broker_id': remote['broker_id'], 'uncertain': state in ('UNKNOWN', 'SUBMITTED', 'CANCEL_REQUESTED')}

    def _snapshot(self, value, now):
        if type(value) is not dict or value.get('classification') != 'HISTORICAL_SYNTHETIC' or value.get('paper') is not True or value.get('verified') is not True or value.get('coherent') is not True or value.get('account_id') != 'AUTHORED-FAKE-PAPER':
            raise PaperError('paper_unknown_or_nonpaper_account')
        age = now - integer(value.get('at_ms'), 0, 2**63 - 1)
        if not 0 <= age <= self.limits.max_snapshot_age_ms:
            raise PaperError('paper_account_stale')
        integer(value.get('revision')); integer(value.get('equity_cents')); integer(value.get('opening_equity_cents'))
        integer(value.get('buying_power_cents'))
        if value.get('session') not in ('OPEN', 'CLOSED', 'UNKNOWN'):
            raise PaperError('paper_session_unknown')
        if type(value.get('orders')) is not dict or len(value['orders']) > MAX_ORDERS or type(value.get('positions')) is not dict or len(value['positions']) > 32 or type(value.get('marks')) is not dict or len(value['marks']) > 32:
            raise PaperError('paper_account_resource_boundary')
        for symbol, mark in value['marks'].items():
            if type(symbol) is not str or not symbol.isascii() or len(symbol) > 14:
                raise PaperError('paper_account_symbol')
            integer(mark, 1, 100000000)
        for symbol, quantity in value['positions'].items():
            integer(quantity, 0, 10000)
            if symbol not in value['marks']:
                raise PaperError('paper_position_mark_unknown')
        return value

    async def _refresh(self):
        self._transport(); self.account = None
        raw = await self._call(self.broker.snapshot)
        now = self._now(); value = self._snapshot(raw, now)
        def apply(state):
            if now < state['clock_ms'] or value['revision'] < state['snapshot_revision']:
                raise PaperError('paper_snapshot_or_clock_regression')
            known = {r['client_id']: (key, r) for key, r in state['orders'].items()}
            if any(identity not in known for identity in value['orders']):
                raise PaperError('paper_external_order_requires_reconciliation')
            for identity, (key, record) in known.items():
                remote = value['orders'].get(identity)
                if remote is None:
                    if record['state'] in ACTIVE:
                        state['orders'][key] = {**record, 'state': 'UNKNOWN', 'uncertain': True}
                else:
                    state['orders'][key] = self._record(record, remote)
            state['clock_ms'] = now; state['snapshot_revision'] = value['revision']
            if value['opening_equity_cents'] - value['equity_cents'] >= self.limits.max_daily_loss_cents:
                state['kill'] = True
        self.store.mutate('RECONCILED', apply)
        self.account = copy.deepcopy(value)
        return value

    async def refresh(self):
        async with self.lock:
            try:
                await self._refresh()
            except BaseException:
                self.account = None
                raise
            return self.view()

    def _risk(self, state, account, definition):
        if account['opening_equity_cents'] - account['equity_cents'] >= self.limits.max_daily_loss_cents:
            raise PaperError('paper_daily_loss_limit')
        if state['kill']:
            raise PaperError('paper_kill_switch_active')
        if any(r['uncertain'] for r in state['orders'].values()):
            raise PaperError('paper_unknown_order_blocks_admission')
        if account['session'] != 'OPEN':
            raise PaperError('paper_session_not_verified_open')
        for record in state['orders'].values():
            represented = account['orders'].get(record['client_id'], {}).get('filled_qty', 0)
            if record['filled_qty'] > represented:
                raise PaperError('paper_account_revision_requires_refresh')
        symbol = definition['symbol']; q = int(definition['quantity']); p = cents(definition['limit_price'])
        if symbol not in account['marks']:
            raise PaperError('paper_instrument_not_eligible')
        mark = account['marks'][symbol]
        if abs(p - mark) * 10000 > mark * self.limits.max_price_distance_bps:
            raise PaperError('paper_limit_far_from_reference')
        if q * p > self.limits.max_order_cents:
            raise PaperError('paper_order_notional_limit')
        active = [r for r in state['orders'].values() if r['state'] in ACTIVE]
        if len(active) >= self.limits.max_open_orders:
            raise PaperError('paper_open_order_limit')
        buys = {}; sells = {}; unreported_buy_reserve = 0
        for r in active:
            d = r['intent']; left = int(d['quantity']) - r['filled_qty']
            if d['side'] == 'buy':
                buys[d['symbol']] = buys.get(d['symbol'], 0) + left * cents(d['limit_price'])
                if r['client_id'] not in account['orders']:
                    unreported_buy_reserve += left * cents(d['limit_price'])
            else:
                sells[d['symbol']] = sells.get(d['symbol'], 0) + left
        position = account['positions'].get(symbol, 0)
        if definition['side'] == 'sell':
            if q > position - sells.get(symbol, 0):
                raise PaperError('paper_short_or_reserved_position')
        else:
            if q * p > account['buying_power_cents'] - unreported_buy_reserve:
                raise PaperError('paper_buying_power')
            if position * mark + buys.get(symbol, 0) + q * p > self.limits.max_position_cents:
                raise PaperError('paper_position_exposure_limit')
            gross = sum(n * account['marks'][s] for s, n in account['positions'].items()) + sum(buys.values())
            if gross + q * p > self.limits.max_gross_cents:
                raise PaperError('paper_gross_exposure_limit')

    async def submit(self, request_id, definition):
        self._transport(); request_id = nonce(request_id); definition = intent(definition)
        async with self.lock:
            existing = self.store.read()['orders'].get(request_id)
            if existing is not None:
                if existing['intent'] != definition:
                    raise PaperError('paper_idempotency_conflict')
                return copy.deepcopy(existing)  # No repeat create,even after unknown acknowledgment.
            account = await self._refresh(); now = self._now()
            def reserve(state):
                if now < state['clock_ms'] or now - account['at_ms'] > self.limits.max_snapshot_age_ms or account['revision'] < state['snapshot_revision']:
                    raise PaperError('paper_account_stale')
                if len(state['orders']) >= MAX_ORDERS:
                    raise PaperError('paper_intent_capacity')
                if request_id in state['orders']:
                    raise PaperError('paper_concurrent_request_identity')
                self._risk(state, account, definition)
                r = {'client_id': client_id(state['profile'], request_id, definition), 'intent': definition,
                     'state': 'SUBMITTED', 'filled_qty': 0, 'filled_notional_cents': 0,
                     'broker_id': None, 'uncertain': True}
                state['orders'][request_id] = r; state['clock_ms'] = now
                return copy.deepcopy(r)
            record = self.store.mutate('INTENT_DURABLE_BEFORE_SEND', reserve)
            self.account = None
            try:
                remote = await self._call(self.broker.place, definition, record['client_id'])
                accepted = self._record(record, remote)
                self.store.mutate('BROKER_ACKNOWLEDGED', lambda s: s['orders'].__setitem__(request_id, accepted))
                return copy.deepcopy(accepted)
            except BaseException:
                self.account = None
                # If this commit itself fails,the prior durable SUBMITTED/uncertain
                # intent still reserves exposure and blocks unsafe readmission.
                self.store.mutate('ACK_UNKNOWN', lambda s: s['orders'].__setitem__(request_id, {**record, 'state': 'UNKNOWN'}))
                raise

    def kill(self):
        self.store.mutate('KILL_ADMISSION', lambda s: s.__setitem__('kill', True))

    async def arm_demo(self, acknowledge_example_limits):
        self._transport()
        if acknowledge_example_limits is not True:
            raise PaperError('paper_example_limits_ack_required')
        async with self.lock:
            await self._refresh()
            def arm(state):
                if any(r['uncertain'] for r in state['orders'].values()):
                    raise PaperError('paper_unknown_order_blocks_admission')
                if self.account['opening_equity_cents'] - self.account['equity_cents'] >= self.limits.max_daily_loss_cents:
                    raise PaperError('paper_daily_loss_limit')
                state['kill'] = False
            self.store.mutate('FAKE_EXAMPLE_LIMITS_ACKNOWLEDGED', arm)
            return self.view()

    async def cancel(self, request_id):
        self._transport(); request_id = nonce(request_id)
        async with self.lock:
            record = self.store.read()['orders'].get(request_id)
            if record is None:
                raise PaperError('paper_unknown_intent')
            if record['state'] not in ACTIVE:
                return copy.deepcopy(record)
            pending = {**record, 'state': 'CANCEL_REQUESTED', 'uncertain': True}
            self.store.mutate('CANCEL_DURABLE_BEFORE_SEND', lambda s: s['orders'].__setitem__(request_id, pending))
            self.account = None
            try:
                remote = await self._call(self.broker.cancel, record['client_id'])
                accepted = self._record(pending, remote)
                self.store.mutate('CANCEL_OBSERVED', lambda s: s['orders'].__setitem__(request_id, accepted))
                return accepted
            except BaseException:
                self.account = None
                self.store.mutate('CANCEL_UNKNOWN', lambda s: s['orders'].__setitem__(request_id, {**pending, 'state': 'UNKNOWN'}))
                raise

    async def kill_and_cancel(self):
        self.kill()  # Admission closes before any fallible broker operation.
        for key, record in self.store.read()['orders'].items():
            if record['state'] in ACTIVE:
                try:
                    await self.cancel(key)
                except PaperError:
                    pass  # Unknown remains reserved;final reconciliation is explicit.
        await self.refresh()
        return self.view()

    def view(self):
        state = self.store.read()
        return {'schema': 'gig.paper.sandbox.v1', 'classification': 'HISTORICAL_SYNTHETIC',
                'mode': 'FAKE_BROKER_NOT_ALPACA', 'external_execution_enabled': False,
                'account': copy.deepcopy(self.account), 'kill_switch': state['kill'],
                'orders': [{'request_id': k, **r} for k, r in state['orders'].items()],
                'requires_reconciliation': any(r['uncertain'] for r in state['orders'].values()),
                'risk_limits': self.limits.view(), 'audit': self.store.audit_receipt(),
                'limitations': ['Fake balances,eligibility,marks,session and fills are authored.',
                                'No Alpaca access,account authentication or order submission.',
                                'Snapshot revision is local fake consistency metadata,not an exchange sequence.',
                                'Real transport/account/permission/risk qualification remains blocked.']}
