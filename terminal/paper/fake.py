"""Durable deterministic fake broker. No HTTP/socket/client credential code.

All balances,marks,eligibility,session and fills are AUTHORED,not Alpaca values.
"""
import hashlib
import json
from .contracts import PaperError, ACTIVE, STATES, MAX_ORDERS, canonical, cents, intent, integer


class FakeBroker:
    synthetic = True
    def __init__(self, store, clock):
        self.store, self.clock = store, clock
        self.failure = None
        self.place_calls = 0
        self.cancel_calls = 0
        with store.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT count(*) FROM fake').fetchone()[0] == 0:
                if store._load(db)['orders']:
                    raise PaperError('paper_fake_history_missing')
                self._save(db, {'revision': 1, 'cash_cents': 100000, 'opening_equity_cents': 100000,
                                'positions': {}, 'orders': {}, 'session': 'OPEN',
                                'marks': {'AAPL': 10000, 'MSFT': 20000, 'NVDA': 15000}})

    def _load(self, db):
        row = db.execute('SELECT payload,digest FROM fake WHERE id=1').fetchone()
        if row is None or type(row[0]) is not bytes or len(row[0]) > 256 * 1024 or hashlib.sha256(row[0]).hexdigest() != row[1]:
            raise PaperError('paper_fake_integrity')
        try:
            value = json.loads(row[0])
            if type(value) is not dict or set(value) != {'revision','cash_cents','opening_equity_cents','positions','orders','session','marks'} or value['session'] not in ('OPEN','CLOSED','UNKNOWN'):
                raise PaperError('paper_fake_contract')
            for k in ('revision','cash_cents','opening_equity_cents'):
                integer(value[k])
            if type(value['positions']) is not dict or len(value['positions']) > 32 or type(value['marks']) is not dict or not 1 <= len(value['marks']) <= 32 or type(value['orders']) is not dict or len(value['orders']) > MAX_ORDERS:
                raise PaperError('paper_fake_contract')
            for symbol, mark in value['marks'].items():
                intent({'symbol':symbol,'side':'buy','quantity':'1','limit_price':'1','type':'limit','time_in_force':'day'})
                integer(mark,1,100000000)
            for symbol, q in value['positions'].items():
                if symbol not in value['marks']:
                    raise PaperError('paper_fake_contract')
                integer(q,0,10000)
            for identity, record in value['orders'].items():
                if type(record) is not dict or set(record) != {'client_id','broker_id','intent','state','filled_qty','filled_notional_cents'} or record['client_id'] != identity or record['broker_id'] != 'fake-' + identity or record['intent'] != intent(record['intent']) or record['state'] not in STATES:
                    raise PaperError('paper_fake_contract')
                integer(record['filled_qty'],0,int(record['intent']['quantity']))
                integer(record['filled_notional_cents'])
        except (ValueError, TypeError, KeyError, UnicodeError):
            raise PaperError('paper_fake_contract') from None
        return value

    def _save(self, db, value):
        raw = canonical(value)
        if len(raw) > 256 * 1024:
            raise PaperError('paper_fake_capacity')
        db.execute('INSERT OR REPLACE INTO fake VALUES(1,?,?)', (raw, hashlib.sha256(raw).hexdigest()))

    async def snapshot(self):
        if self.failure == 'snapshot':
            raise TimeoutError()
        with self.store.connection() as db:
            db.execute('BEGIN')
            v = self._load(db)
        reserved = sum((int(o['intent']['quantity']) - o['filled_qty']) * cents(o['intent']['limit_price'])
                       for o in v['orders'].values() if o['state'] in ACTIVE and o['intent']['side'] == 'buy')
        equity = v['cash_cents'] + sum(q * v['marks'][s] for s, q in v['positions'].items())
        return {'classification': 'HISTORICAL_SYNTHETIC', 'account_id': 'AUTHORED-FAKE-PAPER',
                'paper': True, 'verified': True, 'coherent': True, 'revision': v['revision'],
                'at_ms': self.clock(), 'session': v['session'], 'equity_cents': equity,
                'opening_equity_cents': v['opening_equity_cents'],
                'buying_power_cents': max(0, v['cash_cents'] - reserved),
                'positions': v['positions'], 'marks': v['marks'], 'orders': v['orders'],
                'limits': 'EXAMPLE fake cash/marks only;not a genuine broker account or live prices'}

    async def place(self, definition, identity):
        self.place_calls += 1
        if self.failure == 'before_place':
            raise TimeoutError()
        definition = intent(definition)
        with self.store.connection() as db:
            db.execute('BEGIN IMMEDIATE'); v = self._load(db)
            if identity in v['orders']:
                if v['orders'][identity]['intent'] != definition:
                    raise PaperError('paper_fake_client_id_conflict')
                return dict(v['orders'][identity])
            if len(v['orders']) >= MAX_ORDERS:
                raise PaperError('paper_fake_capacity')
            record = {'client_id': identity, 'broker_id': 'fake-' + identity,
                      'intent': definition, 'state': 'ACCEPTED', 'filled_qty': 0,
                      'filled_notional_cents': 0}
            v['orders'][identity] = record; v['revision'] += 1; self._save(db, v)
        if self.failure == 'after_place':
            raise TimeoutError()  # Committed fake order,ambiguous delivery to caller.
        return record

    async def cancel(self, identity):
        self.cancel_calls += 1
        if self.failure == 'cancel_timeout':
            raise TimeoutError()
        with self.store.connection() as db:
            db.execute('BEGIN IMMEDIATE'); v = self._load(db)
            if identity not in v['orders']:
                raise PaperError('paper_fake_unknown_order')
            o = v['orders'][identity]
            if o['state'] in ACTIVE:
                o['state'] = 'CANCEL_REJECTED' if self.failure == 'cancel_reject' else 'CANCELED'
                v['revision'] += 1; self._save(db, v)
            return dict(o)

    def event(self, identity, action, quantity=None, price=None):
        """Explicit authored event,not an automatically simulated market fill."""
        with self.store.connection() as db:
            db.execute('BEGIN IMMEDIATE'); v = self._load(db)
            if identity not in v['orders']:
                raise PaperError('paper_fake_unknown_order')
            o = v['orders'][identity]
            if o['state'] not in ACTIVE:
                raise PaperError('paper_fake_terminal_order')
            if action == 'fill':
                q = integer(quantity, 1, int(o['intent']['quantity']) - o['filled_qty'])
                p = cents(price)
                limit = cents(o['intent']['limit_price']); side = o['intent']['side']; symbol = o['intent']['symbol']
                if (side == 'buy' and p > limit) or (side == 'sell' and p < limit):
                    raise PaperError('paper_fake_fill_outside_limit')
                sign = 1 if side == 'buy' else -1
                position = v['positions'].get(symbol, 0) + sign * q
                if position < 0 or v['cash_cents'] - sign * q * p < 0:
                    raise PaperError('paper_fake_account_boundary')
                v['positions'][symbol] = position; v['cash_cents'] -= sign * q * p
                o['filled_qty'] += q; o['filled_notional_cents'] += q * p
                o['state'] = 'FILLED' if o['filled_qty'] == int(o['intent']['quantity']) else 'PARTIALLY_FILLED'
            elif action in ('reject', 'expire'):
                if action == 'reject' and o['filled_qty']:
                    raise PaperError('paper_reject_after_fill')
                o['state'] = 'REJECTED' if action == 'reject' else 'EXPIRED'
            else:
                raise PaperError('paper_fake_event')
            v['revision'] += 1; self._save(db, v)

    def scenario(self, *, session=None, cash_cents=None):
        with self.store.connection() as db:
            db.execute('BEGIN IMMEDIATE'); v = self._load(db)
            if session is not None:
                if session not in ('OPEN', 'CLOSED', 'UNKNOWN'):
                    raise PaperError('paper_fake_session')
                v['session'] = session
            if cash_cents is not None:
                v['cash_cents'] = integer(cash_cents)
            v['revision'] += 1; self._save(db, v)
