"""Gated bounded IEX historical REST acquisition;no live/SIP or automatic retries."""
import asyncio,datetime,hashlib
from urllib.parse import urlencode
from .service import AccessError
from .sec import date
from .prices import bars
from .history import HistorySource,normalize

async def ingest(workspace,ticker,start,end,timeframe='1Day',max_pages=4):
    workspace.market_identity(ticker);date(start);date(end)
    if timeframe not in ('1Day','1Hour','1Min') or type(max_pages) is not int or not 1<=max_pages<=4:raise AccessError('history_acquisition_budget')
    if not 0<(datetime.date.fromisoformat(end)-datetime.date.fromisoformat(start)).days<={'1Day':366,'1Hour':31,'1Min':7}[timeframe]:raise AccessError('history_acquisition_interval')
    store=workspace.history_store
    if store is None:raise AccessError('history_private_storage_required')
    headers=workspace.permission('alpaca')
    if workspace.fetcher is None and not store.allow_observed:raise AccessError('history_observed_retention_not_approved')
    if workspace.lock.locked():raise AccessError('upstream_refresh_busy')
    async with workspace.lock:
        pages=[];seen=set();token=None;has_more=False;receipt=None
        exclusive=str(datetime.date.fromisoformat(end)+datetime.timedelta(days=1))
        lower=start+'T00:00:00Z';upper=exclusive+'T00:00:00Z'
        from terminal.providers.kraken import timestamp_ns
        for index in range(max_pages):
            await asyncio.sleep(max(0,1.01-(workspace.clock()-workspace.last_request)))
            query={'timeframe':timeframe,'start':lower,'end':upper,'feed':'iex','adjustment':'raw','limit':64}
            if token is not None:query['page_token']=token
            url='https://data.alpaca.markets/v2/stocks/'+ticker+'/bars?'+urlencode(query)
            payload,digest=await workspace.fetch('alpaca',url,headers);parsed=bars(payload,ticker)
            if len(parsed['bars'])>64:raise AccessError('history_page_record_budget')
            if any(not int(timestamp_ns(lower))<=int(timestamp_ns(r['timestamp']))<int(timestamp_ns(upper)) for r in parsed['bars']):raise AccessError('history_bar_outside_interval')
            pages.append({'bars':parsed['bars'],'sha256':digest})
            receipt=datetime.datetime.now(datetime.timezone.utc).isoformat()
            token=payload.get('next_page_token');has_more=token not in (None,'')
            if not has_more:break
            if type(token) is not str or not 1<=len(token)<=512 or any(ord(c)<33 or ord(c)>126 for c in token):raise AccessError('history_page_token')
            if token in seen or not parsed['bars']:raise AccessError('history_pagination_no_progress')
            seen.add(token)
        core=normalize(ticker,timeframe,pages,HistorySource('alpaca','iex',f'IEX only;not SIP/NBBO/depth;requested UTC[{lower},{upper});limit64;max_pages{max_pages};receipt is last-page receipt','raw',workspace.origin,'fixture_only' if workspace.fetcher is not None else 'operator_review_not_independent_entitlement_verification',receipt),has_more=has_more)
        result=await asyncio.to_thread(store.save,core)
        return {'schema':'gig.history.acquisition.v1','status':'STORED_BOUNDED_INTERVAL','symbol':ticker,'timeframe':timeframe,**result,'pages':len(pages),'has_more':has_more,'complete_history':False,'next_token_sha256':hashlib.sha256(token.encode()).hexdigest() if has_more else None,'source_sha256':core['source_sha256'],'state':core['state'],'cache_policy':'immutable revision stored;current stock quote/bar cache is not silently replaced','session_policy':'calendar not supplied;gaps are candidates,not verified missing exchange bars'}


def coverage_against_declared_schedule(core,expected_utc):
    from terminal.providers.kraken import timestamp_ns
    if type(expected_utc) is not list or len(expected_utc)>256:raise ValueError('history_schedule_budget')
    expected=[int(timestamp_ns(v)) for v in expected_utc]
    if any(b<=a for a,b in zip(expected,expected[1:])):raise ValueError('history_schedule_order')
    observed={int(r['timestamp_ns']) for r in core['bars']}
    return {'status':'COMPARISON_TO_CALLER_SUPPLIED_SCHEDULE','missing_timestamp_ns':[str(v) for v in expected if v not in observed],'unexpected_timestamp_ns':[str(v) for v in sorted(observed-set(expected))],'authority':'caller-declared expected timestamps;not an independently verified exchange calendar/holiday/halts schedule'}
