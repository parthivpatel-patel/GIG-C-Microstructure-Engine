"""Provisional Kraken-v2 shaped profile, independently authored fixtures only.

Current official docs/terms access is blocked. This implementation is NOT a verified
live protocol claim. Native callback owns financial state; cache here is bounded
wire-decimal text solely for candidate checksum validation. No inferred order IDs.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from collections import deque
import asyncio
import datetime as dt
import hashlib
import json
import re
import zlib
from typing import Callable, AsyncIterator

MAX_PAYLOAD = 65536
UINT64_MAX = 2**64 - 1
PRICE_MAX = 2**63 - 1
DECIMAL = re.compile(r'(?:0|[1-9][0-9]*)(?:\.[0-9]+)?\Z')
STAMP = re.compile(r'(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?Z\Z')


class ProviderError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class Permission:
    docs_reviewed: bool = False
    private_display_approved: bool = False
    cloud_processing_approved: bool = False
    recording_approved: bool = False
    evidence_reference: str = ''

    def require_live(self) -> None:
        if not (self.docs_reviewed and self.private_display_approved and self.cloud_processing_approved and self.evidence_reference):
            raise ProviderError('permission_or_current_protocol_unverified')


def _pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise ProviderError('duplicate_json_key')
        out[key] = value
    return out


def decode(raw: str) -> dict:
    if type(raw) is not str or len(raw) > MAX_PAYLOAD or len(raw.encode('utf-8')) > MAX_PAYLOAD:
        raise ProviderError('payload_limit')
    try:
        value = json.loads(raw, parse_float=Decimal, parse_int=Decimal,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProviderError('nonfinite_number')),
                           object_pairs_hook=_pairs)
    except (ValueError, RecursionError) as error:
        if isinstance(error, ProviderError):
            raise
        raise ProviderError('malformed_json') from error
    if type(value) is not dict:
        raise ProviderError('object_required')
    return value


def decimal_wire(value, *, maximum: int, scale: int) -> tuple[str, str]:
    if type(value) not in (str, Decimal, int) or type(value) is bool:
        raise ProviderError('decimal_required')
    text = str(value)
    if len(text) > 48 or not DECIMAL.fullmatch(text):
        raise ProviderError('decimal_grammar')
    try:
        x = Decimal(text)
        # Integer multiplication without Decimal's context-dependent rounding.
        sign, digits, exponent = x.as_tuple()
        coefficient = int(''.join(map(str, digits)))
        numerator = coefficient * scale * (10 ** max(exponent, 0))
        divisor = 10 ** max(-exponent, 0)
        result, remainder = divmod(numerator, divisor)
    except (InvalidOperation, ValueError) as error:
        raise ProviderError('decimal_invalid') from error
    if remainder:
        raise ProviderError('nonintegral_unit')
    if result > maximum:
        raise ProviderError('numeric_range')
    return str(result), text


def timestamp_ns(value: str) -> str:
    if type(value) is not str:
        raise ProviderError('timestamp_required')
    m = STAMP.fullmatch(value)
    if not m:
        raise ProviderError('timestamp_grammar')
    try:
        day = dt.date.fromisoformat(m[1])
        h, minute, second = map(int, m.group(2, 3, 4))
        if h > 23 or minute > 59 or second > 59:
            raise ValueError()
        seconds = (day - dt.date(1970, 1, 1)).days * 86400 + h * 3600 + minute * 60 + second
        ns = seconds * 10**9 + int((m[5] or '').ljust(9, '0'))
        if ns < 0 or ns > 2**63 - 1:
            raise ValueError()
        return str(ns)
    except ValueError as error:
        raise ProviderError('timestamp_range') from error


def bounded_integer(value, maximum, code):
    if type(value) not in (Decimal, int) or not 0 <= value <= maximum or value != int(value):
        raise ProviderError(code)
    return int(value)


def checksum(bids: dict[str, tuple[str, str]], asks: dict[str, tuple[str, str]]) -> int:
    # Candidate profile: asks ascending then bids descending, top ten each,
    # concatenated wire decimal digits stripped of '.' and leading zeros.
    def digits(text):
        return text.replace('.', '').lstrip('0')
    pieces = []
    for side, reverse in ((asks, False), (bids, True)):
        for key in sorted(side, key=int, reverse=reverse)[:10]:
            price, qty = side[key]
            pieces.extend((digits(price), digits(qty)))
    return zlib.crc32(''.join(pieces).encode('ascii')) & 0xffffffff


class KrakenBookAdapter:
    provider = 'kraken'
    capabilities = {
        'book_level': 'L2', 'order_ids': False, 'fifo': False,
        'exchange_sequence': False, 'candidate_crc32': True,
        'profile_verified': False, 'live_connectivity_verified': False,
        'recording': False, 'trades': True,
    }

    def __init__(self, apply_native: Callable, *, symbol='BTC/USD', price_scale=100,
                 quantity_scale=100000000, depth=10, stale_ns=10_000_000_000):
        if (type(depth) is not int or depth != 10 or type(price_scale) is not int or
                type(quantity_scale) is not int or not 1 <= price_scale <= 10**9 or
                not 1 <= quantity_scale <= 10**9 or type(stale_ns) is not int or
                not 1 <= stale_ns <= 60_000_000_000 or symbol != 'BTC/USD'):
            raise ProviderError('configuration')
        self.apply_native = apply_native
        self.symbol = symbol
        self.price_scale, self.quantity_scale = price_scale, quantity_scale
        self.depth, self.stale_ns = depth, stale_ns
        self.bids, self.asks = {}, {}
        self.state, self.reason = 'DISCONNECTED', 'not_connected'
        self.last_receive_ns = None
        self.last_digest = None
        self.rejected = self.duplicates = self.snapshots = self.updates = 0
        self.trades = deque(maxlen=256)
        self.trade_ids = set()
        self.backoff_attempt = 0

    def connect(self):
        self.state, self.reason = 'CONNECTING', 'awaiting_subscription'
        self.bids, self.asks = {}, {}
        self.last_digest, self.last_receive_ns = None, None

    def disconnected(self):
        self.state, self.reason = 'DISCONNECTED', 'transport_closed'
        self.bids, self.asks = {}, {}
        self.last_digest, self.last_receive_ns = None, None

    def recovery_delay(self) -> int:
        delay = min(30, 2 ** min(self.backoff_attempt, 5))
        self.backoff_attempt = min(self.backoff_attempt + 1, 6)
        return delay

    def status(self, now_ns: int) -> dict:
        if self.last_receive_ns is not None and now_ns - self.last_receive_ns > self.stale_ns and self.state == 'LIVE':
            self.state, self.reason = 'STALE', 'heartbeat_deadline'
        return {'state': self.state, 'reason': self.reason, 'provider': self.provider,
                'rejected': self.rejected, 'duplicates': self.duplicates,
                'snapshots': self.snapshots, 'updates': self.updates,
                'origin': 'HISTORICAL_SYNTHETIC', 'source_sequence': None, 'continuity': 'checksum_scoped_not_exchange_sequence',
                'capabilities': dict(self.capabilities)}

    def _level(self, item):
        if type(item) is not dict or set(item) - {'price', 'qty'} or set(item) != {'price', 'qty'}:
            raise ProviderError('level_fields')
        price, pt = decimal_wire(item['price'], maximum=PRICE_MAX, scale=self.price_scale)
        qty, qt = decimal_wire(item['qty'], maximum=UINT64_MAX, scale=self.quantity_scale)
        if price == '0':
            raise ProviderError('zero_price')
        return price, qty, pt, qt

    def feed(self, raw: str, now_ns: int) -> dict:
        if type(now_ns) is not int or now_ns < 0 or (self.last_receive_ns is not None and now_ns < self.last_receive_ns):
            raise ProviderError('receive_clock_regression')
        try:
            return self._feed(raw, now_ns)
        except (ProviderError, MemoryError):
            self.rejected += 1
            self.state, self.reason = 'GAP_DETECTED', 'invalid_or_uncommitted_payload'
            raise

    def _feed(self, raw: str, now_ns: int) -> dict:
        payload = decode(raw)
        if payload.get('method') == 'subscribe':
            if payload.get('success') is not True:
                raise ProviderError('subscription_rejected')
            result = payload.get('result')
            if type(result) is not dict or result.get('channel') not in ('book', 'trade') or result.get('symbol') != self.symbol:
                raise ProviderError('subscription_identity')
            self.state, self.reason = 'SYNCHRONIZING', 'awaiting_valid_snapshot'
            return {'kind': 'acknowledgment', 'source_sequence': None}
        if payload.get('channel') == 'heartbeat':
            self.last_receive_ns = now_ns
            return {'kind': 'heartbeat', 'source_sequence': None}
        if payload.get('channel') == 'trade':
            return self._trade(payload, now_ns)
        if payload.get('channel') != 'book' or payload.get('type') not in ('snapshot', 'update'):
            raise ProviderError('unsupported_message')
        if type(payload.get('data')) is not list or len(payload['data']) != 1:
            raise ProviderError('one_symbol_batch_required')
        data = payload['data'][0]
        if type(data) is not dict or data.get('symbol') != self.symbol:
            raise ProviderError('symbol_mismatch')
        snapshot = payload['type'] == 'snapshot'
        if not snapshot and self.state not in ('LIVE', 'STALE'):
            raise ProviderError('snapshot_required')
        if not {'bids', 'asks', 'checksum'} <= set(data) or set(data) - {'symbol', 'bids', 'asks', 'checksum', 'timestamp'}:
            raise ProviderError('book_fields')
        source_time = data.get('timestamp')
        source_ns = None if source_time is None else timestamp_ns(source_time)
        wire_checksum = bounded_integer(data['checksum'], 2**32-1, 'checksum_field')
        digest = hashlib.sha256(raw.encode()).hexdigest()
        if digest == self.last_digest and self.state == 'LIVE':
            self.duplicates += 1
            return {'kind': 'duplicate', 'source_sequence': None}
        candidate = [{}, {}] if snapshot else [self.bids.copy(), self.asks.copy()]
        normalized = []
        for cache, side in zip(candidate, ('bids', 'asks')):
            levels = data[side]
            if type(levels) is not list or len(levels) > 100:
                raise ProviderError('update_budget')
            if snapshot and len(levels) > self.depth:
                raise ProviderError('snapshot_depth')
            converted = []
            seen = set()
            for item in levels:
                price, qty, pt, qt = self._level(item)
                if price in seen:
                    raise ProviderError('duplicate_level')
                seen.add(price)
                if snapshot and qty == '0':
                    raise ProviderError('zero_snapshot_level')
                if qty == '0':
                    cache.pop(price, None)
                else:
                    cache[price] = (pt, qt)
                converted.append({'price_ticks': price, 'quantity': qty})
            # Candidate profile retains subscribed top10 only; no deeper completeness claim.
            retained = sorted(cache, key=int, reverse=side == 'bids')[:self.depth]
            cache_copy = {k: cache[k] for k in retained}
            cache.clear(); cache.update(cache_copy)
            normalized.append(converted)
        if checksum(*candidate) != wire_checksum:
            raise ProviderError('checksum_mismatch')
        # Project only the accepted bounded cache diff. Explicitly delete trimmed
        # old worst levels; never ask native to invent deeper liquidity.
        changes = []
        for before, after in zip((self.bids, self.asks), candidate):
            levels = [] if snapshot else [{'price_ticks': k, 'quantity': '0'} for k in before if k not in after]
            for k in after:
                qty, _ = decimal_wire(after[k][1], maximum=UINT64_MAX, scale=self.quantity_scale)
                if snapshot or before.get(k) != after[k]:
                    levels.append({'price_ticks': k, 'quantity': qty})
            changes.append(levels)
        # Prepare the owned receipt/counters before native commit: publication
        # allocation failure cannot strand native state ahead of accepted cache.
        receipt = {'kind': 'snapshot' if snapshot else 'update', 'source_timestamp': source_time,
                   'source_timestamp_ns': source_ns, 'source_sequence': None,
                   'receive_monotonic_ns': str(now_ns), 'origin': 'HISTORICAL_SYNTHETIC',
                   'integration_profile': 'unverified_kraken_v2_authored_v1'}
        next_snapshots, next_updates = self.snapshots + int(snapshot), self.updates + int(not snapshot)
        try:
            self.apply_native(snapshot=snapshot, bids=changes[0], asks=changes[1], sequence=None)
        except Exception as error:
            raise ProviderError('native_rejected') from error
        self.bids, self.asks = candidate
        self.last_digest, self.last_receive_ns = digest, now_ns
        self.state, self.reason = 'LIVE', 'authored_profile_validated_not_live_connectivity'
        self.backoff_attempt = 0
        self.snapshots, self.updates = next_snapshots, next_updates
        return receipt

    def _trade(self, payload, now_ns):
        if payload.get('type') not in ('snapshot', 'update') or type(payload.get('data')) is not list or len(payload['data']) > 100:
            raise ProviderError('trade_batch')
        pending = []
        ids = set()
        for item in payload['data']:
            if type(item) is not dict or item.get('symbol') != self.symbol or item.get('side') not in ('buy', 'sell'):
                raise ProviderError('trade_identity')
            tid = item.get('trade_id')
            key = str(bounded_integer(tid, UINT64_MAX, 'trade_id'))
            if key in ids:
                raise ProviderError('duplicate_trade_in_batch')
            ids.add(key)
            price, _ = decimal_wire(item.get('price'), maximum=PRICE_MAX, scale=self.price_scale)
            qty, _ = decimal_wire(item.get('qty'), maximum=UINT64_MAX, scale=self.quantity_scale)
            if price == '0' or qty == '0':
                raise ProviderError('zero_trade')
            ns = timestamp_ns(item.get('timestamp'))
            if key not in self.trade_ids:
                pending.append({'trade_id': key, 'price_ticks': price, 'quantity': qty,
                                'side': item['side'], 'source_timestamp': item['timestamp'],
                                'source_timestamp_ns': ns, 'origin': 'HISTORICAL_SYNTHETIC'})
        next_trades, next_ids = self.trades.copy(), self.trade_ids.copy()
        for trade in pending:
            if len(next_trades) == next_trades.maxlen:
                next_ids.remove(next_trades[0]['trade_id'])
            next_trades.append(trade); next_ids.add(trade['trade_id'])
        receipt = {'kind': 'trades', 'trades': pending, 'deduplication_window': '256', 'source_sequence': None}
        self.trades, self.trade_ids = next_trades, next_ids
        self.last_receive_ns = now_ns
        return receipt


async def live_messages(permission: Permission, *, stop: asyncio.Event) -> AsyncIterator[str]:
    """Explicit future opt-in transport; NEVER invoked by synthetic/default startup.

    Requires reviewed current protocol and legal evidence. Retains no market payload.
    No retries beyond caller-controlled lifecycle. ws client honors inherited proxy.
    """
    permission.require_live()
    import websockets.asyncio.client
    async with websockets.asyncio.client.connect(
            'wss://ws.kraken.com/v2', max_size=MAX_PAYLOAD, max_queue=4,
            open_timeout=10, close_timeout=3, ping_interval=20, ping_timeout=10) as ws:
        await ws.send(json.dumps({'method': 'subscribe', 'params': {'channel': 'book', 'symbol': ['BTC/USD'], 'depth': 10, 'snapshot': True}}))
        await ws.send(json.dumps({'method': 'subscribe', 'params': {'channel': 'trade', 'symbol': ['BTC/USD'], 'snapshot': False}}))
        while not stop.is_set():
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=1)
            except asyncio.TimeoutError:
                continue
            if type(raw) is not str:
                raise ProviderError('text_frame_required')
            yield raw
