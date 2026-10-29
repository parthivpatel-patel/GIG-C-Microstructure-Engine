"""Bounded IEX historical reads, without enabling disk retention or a trading client."""
import asyncio
import datetime
import hashlib
import json
from urllib.parse import urlencode
from contextlib import asynccontextmanager
from .alpaca_transport import DATA
from .prices import bars, quote, trade, market_window
from .sec import date
from terminal.providers.kraken import timestamp_ns

def query_key(workspace, symbol, kind, start, end, timeframe, max_pages):
    workspace.market_identity(symbol)
    date(start)
    date(end)
    if kind not in ('bars','quotes','trades') or timeframe not in ('1Day','1Hour','1Min'):
        raise ValueError('market_history_profile')
    if type(max_pages) is not int or not 1 <= max_pages <= 4:
        raise ValueError('market_history_page_budget')
    span = (datetime.date.fromisoformat(end)-datetime.date.fromisoformat(start)).days
    maximum = {'1Day':365,'1Hour':30,'1Min':6}[timeframe] if kind == 'bars' else 1
    if not 0 <= span <= maximum:
        raise ValueError('market_history_interval')
    return symbol, kind, start, end, timeframe, max_pages

def metadata(row):
    """Preserve supported wire annotations without treating them as exchange sequences."""
    result = {}
    for key in ('x','bx','ax','z','i'):
        if key not in row:
            continue
        value = row[key]
        if type(value) is int and 0 <= value < 2**64:
            value = str(value)
        if type(value) is not str or not 1 <= len(value) <= 64 or any(not 32 < ord(c) < 127 for c in value):
            raise ValueError('market_history_annotation')
        result[key] = value
    if 'c' in row:
        value = row['c']
        if value is not None and (type(value) is not list or len(value) > 32 or any(type(v) is not str or not 1 <= len(v) <= 16 or any(not 32 < ord(c) < 127 for c in v) for v in value)):
            raise ValueError('market_history_conditions')
        result['conditions'] = value
    return result

@asynccontextmanager
async def transaction(workspace):
    # Queue only bounded local work;never retry a remote failure.
    if workspace.market_history_pending >= 4:
        raise ValueError('market_history_request_capacity')
    workspace.market_history_pending += 1
    try:
        async with asyncio.timeout(25):
            async with workspace.lock:
                yield
    finally:
        workspace.market_history_pending -= 1

async def acquire(workspace, symbol, kind, start, end, timeframe='1Day', max_pages=4):
    key = query_key(workspace,symbol,kind,start,end,timeframe,max_pages)
    headers = workspace.permission('alpaca')
    cached = workspace.market_history_cache.get(key)
    if cached and 0 <= workspace.clock()-cached[0] < 60:
        return {**cached[1], 'cache_status':'ACCEPTED_REFERENCE_REUSED'}
    lower = start+'T00:00:00Z'
    upper = str(datetime.date.fromisoformat(end)+datetime.timedelta(days=1))+'T00:00:00Z'
    lo, hi = int(timestamp_ns(lower)), int(timestamp_ns(upper))
    rows, receipts, seen_tokens, identities = [], [], set(), set()
    token = None
    prior = None
    duplicates = 0
    has_more = False
    async with transaction(workspace):
        headers = workspace.permission('alpaca')
        instrument = workspace.market_identity(symbol)
        # A prior queued request may have published this exact interval.
        cached = workspace.market_history_cache.get(key)
        if cached and 0 <= workspace.clock()-cached[0] < 60:
            return {**cached[1], 'cache_status':'ACCEPTED_REFERENCE_REUSED'}
        for page in range(max_pages):
            await asyncio.sleep(max(0,1.01-(workspace.clock()-workspace.last_request)))
            params = {'symbols':symbol,'start':lower,'end':upper,'feed':'iex','limit':64,'sort':'asc'}
            if kind == 'bars':
                params.update(timeframe=timeframe,adjustment='raw')
            if token:
                params['page_token'] = token
            payload, digest = await workspace.fetch('alpaca', DATA+kind+'?'+urlencode(params), headers)
            group = payload.get(kind)
            if type(group) is not dict or set(group)-{symbol} or type(group.get(symbol,[])) is not list or len(group.get(symbol,[])) > 64:
                raise ValueError('market_history_identity_or_page_budget')
            source_rows = group.get(symbol,[])
            if kind == 'bars':
                parsed = bars({'symbol':symbol,'bars':source_rows},symbol)['bars']
            else:
                parser, label = (quote,'quote') if kind == 'quotes' else (trade,'trade')
                parsed = [{**parser({'symbol':symbol,label:r},symbol),'wire_metadata':metadata(r)} for r in source_rows]
            for raw, row in zip(source_rows,parsed):
                stamp = int(timestamp_ns(row['timestamp']))
                if not lo <= stamp < hi or prior is not None and (stamp < prior or kind == 'bars' and stamp == prior):
                    raise ValueError('market_history_time_boundary_or_order')
                prior = stamp
                identity = hashlib.sha256(json.dumps(raw,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()
                duplicate = identity in identities
                duplicates += int(duplicate)
                identities.add(identity)
                rows.append({**row,'source_timestamp_ns':str(stamp),'source_record_sha256':identity,'duplicate_record':duplicate})
            # Never expose provider pagination tokens in diagnostics or source URLs.
            receipts.append({'url':DATA+kind,'page':page+1,'sha256':digest,'records':len(source_rows),
                'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
            token = payload.get('next_page_token')
            has_more = token not in (None,'')
            if not has_more:
                break
            if type(token) is not str or not 1 <= len(token) <= 512 or any(not 32 < ord(c) < 127 for c in token) or token in seen_tokens or not source_rows:
                raise ValueError('market_history_pagination_no_progress')
            seen_tokens.add(token)
        result = {'schema':'gig.alpaca.historical.v1','symbol':symbol,'kind':kind,
            'instrument_metadata':instrument,
            'timeframe':timeframe if kind == 'bars' else None,'provider':'alpaca','feed':'iex',
            'origin':workspace.origin,'availability':'AVAILABLE' if rows else 'EMPTY_SOURCE_RESPONSE',
            'freshness':'HISTORICAL_NOT_LIVE','adjustment':'raw' if kind == 'bars' else None,
            'requested_interval':{'start':lower,'exclusive_end':upper,'clock':'UTC calendar bounds,not exchange-session boundaries'},
            'records':rows,'record_count':len(rows),'pages':len(receipts),'max_pages':max_pages,
            'source_records':receipts,'has_more':has_more,'complete_market_history':False,
            'pagination_state':'BOUNDED_PREFIX_MORE_ADVERTISED' if has_more else 'SOURCE_NO_FURTHER_PAGE_ADVERTISED_NOT_COMPLETENESS_PROOF',
            'duplicate_source_records':duplicates,'duplicate_policy':'Retained and marked;no sequence/exactly-once inference',
            'session':market_window(rows[-1]['timestamp']) if rows else None,
            'received_at':receipts[-1]['received_at'],'cache_status':'ACQUIRED',
            'scope':'Single-venue IEX,not SIP/NBBO or full-market tape;no L2/L3 inference',
            'retention':'At most16 bounded queries in process memory;no disk storage enabled',
            'limitations':['No authoritative holiday/halt/session completeness','Quotes/trades are unreconciled source observations,not a corrected tape','Current provider symbol mapping does not prove historical security identity','Provider timestamps preserved;no clock-latency qualification']}
        accepted = workspace.clock()
        workspace.market_history_cache[key] = (accepted,result)
        workspace.market_history_cache.move_to_end(key)
        while len(workspace.market_history_cache) > 16:
            workspace.market_history_cache.popitem(last=False)
        return result
