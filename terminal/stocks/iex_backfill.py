"""Explicit historical retrieval between retained IEX subscription generations."""
import hashlib
import re

from terminal.alpaca_wire import FixtureWire, HTTPWire, WireError
from .historical_v2 import canonical, ns, utc

MAX_GAP_NS = 2 * 86400 * 10**9
KINDS = {'quote': 'quotes', 'trade': 'trades'}


def retain_anchor(anchors, event, channel):
    if event['out_of_order'] or channel not in KINDS.values() or event['kind'] not in KINDS:
        return
    key = event['symbol'], channel
    point = {name: event[name] for name in
             ('timestamp', 'receipt_index', 'origin', 'source_session_id', 'generation')}
    previous, first, last = anchors.get(key, (None, None, None))
    if last is None or last['generation'] != point['generation']:
        previous, first = last, point
    anchors[key] = previous, first, point


def gaps(live):
    if live.phase != 'SUBSCRIBED' or live.pending or not live.current_observation_scope():
        return []
    previous, current = {}, {}
    if live.retention_current() and live.restored_backfill_endpoints:
        now = live.store.clock()
        previous.update((key, row) for key, row in live.restored_backfill_endpoints.items()
                        if row['expires_seconds'] > now and row['generation'] < live.generation
                        and key[0] in live.symbols and key[1] in live.channels)
    for row in live.history:
        kind = KINDS.get(row['kind'])
        if kind not in live.channels or row['symbol'] not in live.symbols or row['out_of_order']:
            continue
        key = (row['symbol'], kind)
        if row['generation'] < live.generation:
            previous[key] = row
        elif row['generation'] == live.generation:
            current.setdefault(key, row)

    # Endpoints outlive the display ring. Keep only two local generations per
    # active symbol/channel and derive the same gap identity before and after eviction.
    for key, (before, first, last) in live.backfill_anchors.items():
        if key[0] not in live.symbols or key[1] not in live.channels:
            continue
        if last['generation'] == live.generation:
            current[key] = first
        elif last['generation'] < live.generation:
            before = last
        if before is not None and before['generation'] < live.generation:
            other = previous.get(key)
            if other is None or (before['generation'], before['receipt_index']) >= (other['generation'], other['receipt_index']):
                previous[key] = before


    result = []
    for (symbol, kind), left in sorted(previous.items()):
        right = current.get((symbol, kind))
        if right is None or left['origin'] != right['origin']:
            continue
        try:
            start = ns(left['timestamp']) + 1
            end = ns(right['timestamp'])
        except WireError:
            continue  # This stream timestamp cannot bind an exact historical query.
        if not 0 < end - start <= MAX_GAP_NS:
            continue
        gap = {
            'symbol': symbol, 'kind': kind, 'start': utc(start), 'end': utc(end),
            'capture': live.source_session_id, 'generation': live.generation,
            'origin': left['origin'],
            'previous_receipt': left['receipt_index'], 'current_receipt': right['receipt_index'],
        }
        if left['source_session_id'] != live.source_session_id:
            gap['previous_capture'] = left['source_session_id']
        gap['gap_id'] = hashlib.sha256(canonical(gap)).hexdigest()
        result.append(gap)
    return result


async def backfill(live, historical, gap_id, max_pages=4, *, after_revision=None):
    if type(gap_id) is not str or not re.fullmatch('[0-9a-f]{64}', gap_id):
        raise WireError('iex_backfill_gap_identity')
    if type(max_pages) is not int or not 1 <= max_pages <= 4:
        raise WireError('iex_backfill_page_budget')
    keys=live.require()
    reference=live.permission_reference()
    gap = next((item for item in gaps(live) if item['gap_id'] == gap_id), None)
    if gap is None:
        raise WireError('iex_backfill_gap_unavailable')

    source_origin = {FixtureWire: 'HISTORICAL_SYNTHETIC', HTTPWire: 'OBSERVED_OFFICIAL_RESPONSE'}
    if historical.transport is not None and source_origin.get(type(historical.transport)) != gap['origin']:
        raise WireError('iex_backfill_source_mismatch')

    query = {key: gap[key] for key in ('symbol', 'kind', 'start', 'end')}
    query.update(feed='iex', timeframe='1Day', adjustment='raw', max_pages=max_pages)
    if hasattr(historical, 'acquire_backfill'):
        history, continuation = await historical.acquire_backfill(query, gap_id, after_revision)
    else:
        if after_revision is not None:
            raise WireError('iex_backfill_continuation_unavailable')
        history, continuation = await historical.acquire(query), None
    if live.require()!=keys or live.permission_reference()!=reference:
        raise WireError('iex_backfill_permission_changed')
    if not any(item == gap for item in gaps(live)):
        raise WireError('iex_backfill_gap_changed')
    if history['origin'] != gap['origin'] or history['query'] != query:
        raise WireError('iex_backfill_source_mismatch')

    result = {
        'schema': 'gig.iex.backfill.v1', 'gap': gap, 'history': history,
        'coverage': 'BOUNDED_PREFIX' if history['has_more'] else 'SOURCE_RESPONSE_EXHAUSTED',
        'observation_loss': 'UNKNOWN_NO_EXCHANGE_SEQUENCE', 'merged_into_live': False,
    }
    if continuation is not None:
        result['continuation'] = continuation
    return result
