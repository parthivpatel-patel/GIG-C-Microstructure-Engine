"""Read-only qualification primitives. Reports contain counts/hashes,never keys or prices."""
import asyncio,datetime,hashlib,json,os
from fractions import Fraction
from .sec_config import resolve


def nonretaining_environment(environment=None):
    effective,_=resolve(os.environ if environment is None else environment)
    result=dict(effective)
    # Restrict only this process;never save configuration or grant a permission.
    result.update(GIG_ALPACA_STORE_ENABLED='0',GIG_HISTORY_STORE_ENABLED='0',
                  GIG_ALPACA_ASSET_REFERENCE_ENABLED='0')
    return result


def history_status(result):
    if result.get('origin')!='OBSERVED_OFFICIAL_RESPONSE':return 'FIXTURE_NOT_PROVIDER_QUALIFICATION'
    if type(result.get('record_count')) is not int or not 0<=result['record_count']<=256:return 'REJECTED_HISTORICAL_COUNT'
    if not result['record_count']:return 'INCONCLUSIVE_EMPTY_SOURCE_RESPONSE'
    return 'PASS_BOUNDED_HISTORICAL_OBSERVATIONS'


def reference_summary(workspace):
    view=workspace.asset_reference.view()
    accepted=view['status']=='ACCEPTED' and view['accepted_count']>0
    observed=accepted and workspace.catalog.source.get('classification')=='OBSERVED_OFFICIAL_RESPONSE'
    rows=workspace.catalog.rows if accepted else {}
    return {'status':'PASS_OBSERVED_ACCOUNT_REFERENCE' if observed else 'FIXTURE_NOT_PROVIDER_QUALIFICATION' if accepted else 'INCONCLUSIVE_NO_ACCEPTED_ACCOUNT_REFERENCE',
            'accepted_identities':len(rows),'observed_identities':len(rows) if observed else 0,
            'active':sum(r['listing_status']=='ACTIVE' for r in rows.values()),
            'inactive':sum(r['listing_status']=='INACTIVE' for r in rows.values()),
            'representative_symbols':{s:s in rows for s in ('AAPL','MSFT','APLD','CRWV')},
            'sources':workspace.catalog.source.get('sources',[]) if accepted else [],
            'market_data_entitlement_verified':False,'coverage':'Paper-account asset reference;not complete current US exchange listings'}


def comparison_reference(histories):
    if not 2<=len(histories)<=4 or any(h['kind']!='bars' for h in histories):raise ValueError('comparison_input_profile')
    if len({h['symbol'] for h in histories})!=len(histories):raise ValueError('comparison_duplicate_symbol')
    if len({(h['origin'],h['provider'],h['feed']) for h in histories})!=1:raise ValueError('comparison_source_origin')
    scope=(histories[0]['timeframe'],histories[0]['requested_interval'])
    if any((h['timeframe'],h['requested_interval'])!=scope for h in histories):raise ValueError('comparison_scope')
    maps=[]
    for h in histories:
        rows={r['source_timestamp_ns']:r for r in h['records']}
        if len(rows)!=len(h['records']):raise ValueError('comparison_duplicate_timestamp')
        maps.append(rows)
    shared=sorted(set(maps[0]).intersection(*(set(m) for m in maps[1:])),key=int)
    series=[]
    for h,rows in zip(histories,maps):
        base=Fraction(rows[shared[0]]['close']) if shared else None
        if base is not None and base<=0:raise ValueError('comparison_nonpositive_baseline')
        values=[(Fraction(rows[k]['close'])/base-1)*100 for k in shared]
        series.append({'symbol':h['symbol'],'values':[{'numerator':str(v.numerator),'denominator':str(v.denominator)} for v in values]})
    return {'timestamps':[maps[0][k]['timestamp'] for k in shared], 'series':series,
            'exact_shared_timestamps':len(shared),'formula':'100*(raw close/first exactly common close-1);not total return'}


async def cadence(workspace):
    await asyncio.sleep(max(0,1.01-(workspace.clock()-workspace.last_request)))


async def collect_stream(stream,symbols,seconds):
    if type(seconds) is not int or not 5<=seconds<=60:raise ValueError('qualification_window')
    started=stream.clock()
    try:
        await stream.start(symbols)
        while stream.clock()-started<seconds:
            if stream.state=='FAILED' or stream.failures:break  # no qualification reconnect storm
            await asyncio.sleep(.1)
        state=stream.view()
        rows=[r for r in state['observations'] if r['state']=='LIVE' and r.get('origin')=='OBSERVED_OFFICIAL_RESPONSE']
        kinds={s:sorted({r['kind'] for r in rows if r['symbol']==s}) for s in symbols}
        ok=state['phase']=='SUBSCRIBED' and all({'quote','trade'}<=set(kinds[s]) for s in symbols)
        return {'status':'PASS_BOUNDED_LIVE_OBSERVATIONS' if ok else 'INCONCLUSIVE_OR_FAILED_STREAM_WINDOW',
                'feed':'iex','symbols':symbols,'phase':state['phase'],'state':state['state'],
                'elapsed_seconds':stream.clock()-started,'accepted_observations':state['accepted_observations'],
                'observed_kinds':kinds,'source_sha256':[r['source_sha256'] for r in rows],
                'source_timestamp_ns_range':[str(min(int(r['source_timestamp_ns']) for r in rows)),str(max(int(r['source_timestamp_ns']) for r in rows))] if rows else None,
                'maximum_receive_age_seconds':max((r['receive_age_seconds'] for r in rows),default=None),'clock_status':'SOURCE_RECEIVE_CLOCKS_UNSYNCHRONIZED_NOT_NETWORK_LATENCY',
                'connection_opens':state['connection_count'],'out_of_order_observations':state['out_of_order_observations'],
                'provider_error':state['reason'],'storage_enabled':bool(stream.store),
                'entitlement_scope':'Authentication/subscription/data-access observation only;not billing/legal or account-wide quota certification',
                'upstream_recovery':'NOT_FAULT_INJECTED;qualification stops on first transport failure',
                'session':'No exchange holiday/halt calendar inferred;quiet windows remain inconclusive'}
    finally:
        await stream.close()


def stage_error(error,stage='source_qualification'):
    # Never propagate transport exceptions,URLs,provider bodies or configuration values.
    from scripts.qualify_sec_sources import failure_result
    safe=failure_result(error,stage)
    return {'status':'BLOCKED_OR_REJECTED','error_type':safe['error_type'],
            'reason':safe['reason'],'diagnostic':safe['diagnostic'],
            'raw_data_retained':False}


async def qualify_sources(workspace,*,end,seconds=30,exclusive_stream_window=False,compare=None,stream_factory=None):
    from .alpaca_history import acquire
    from .live import LiveIEX
    from scripts.qualify_sec_sources import official_fetch,reconcile
    from . import sec
    sec.date(end)
    start=str(datetime.date.fromisoformat(end)-datetime.timedelta(days=13))
    config=workspace.configuration()
    result={'schema':'gig.atlas.operational.sources.v1','readiness':config,'stages':{},
            'milestone_2':'NOT_VERIFIED_TARGET_UI_PRIVACY_AND_FINAL_OWNER_ACCEPTANCE_REQUIRED',
            'persistent_observed_storage':False,'trading_operations':False,
            'legal_and_plan_verification':'Existing operator permission records required;configured flags are not independent vendor/billing evidence'}
    stages=result['stages'];histories=[]
    try:
        if config['alpaca']['ready']:
            source_stage='asset_reference'
            try:
                await workspace.asset_reference.refresh();stages['assets']=reference_summary(workspace)
                for symbol in ('AAPL','MSFT'):
                    source_stage='history_'+symbol
                    h=await acquire(workspace,symbol,'bars',start,end,'1Day',1)
                    histories.append(h)
                    stages['history_'+symbol]={'status':history_status(h),'symbol':symbol,'record_count':h['record_count'],'origin':h['origin'],
                        'requested_interval':h['requested_interval'],'source_records':h['source_records'],'has_more':h['has_more'],'complete_market_history':False}
                source_stage='historical_comparison';expected=comparison_reference(histories)
                stages['comparison']={'status':'PASS_EXACT_COMMON_TIMESTAMP_REFERENCE' if expected['exact_shared_timestamps']>=2 else 'INCONCLUSIVE_SHARED_COVERAGE',
                    'shared_timestamps':expected['exact_shared_timestamps'],
                    'calculation_sha256':hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
                if compare and expected['exact_shared_timestamps']>=2:stages['comparison']['frontend_agreement']=await compare(histories,expected)
            except Exception as exc:stages['alpaca_reads']=stage_error(exc,source_stage)
        else:stages['alpaca_reads']={'status':'BLOCKED_CONFIGURATION_OR_PERMISSION','missing':config['alpaca']['missing_configuration']}
        # SEC is independent of market-data authorization,so still attempt when eligible.
        if config['sec']['ready']:
            source_stage='sec_identity'
            try:
                await cadence(workspace);await workspace.refresh_identities(requested_symbol='AAPL')
                stages['sec_identity']={'status':'PASS_OBSERVED_IDENTITY_REFERENCE' if workspace.origin=='OBSERVED_OFFICIAL_RESPONSE' else 'FIXTURE_NOT_PROVIDER_QUALIFICATION',
                    'count':len(workspace.issuers),'symbols':{s:workspace.issuers.get(s,{}).get('cik') for s in ('AAPL','APLD','CRWV')},'source':workspace.issuer_source}
                if 'AAPL' not in workspace.issuers:raise ValueError('SEC_exact_AAPL_identity_unavailable')
                source_stage='sec_financials';await cadence(workspace);await workspace.refresh('AAPL','sec')
                accepted=workspace.cache['AAPL']['sec'];financials=accepted.get('financials')
                await cadence(workspace)
                source_stage='sec_reconciliation';raw,_=await asyncio.to_thread(official_fetch,workspace.resolve('AAPL')['cik'],workspace.environment)
                check=reconcile(raw,financials,financials['as_of_filing_date'])
                stages['sec_financials']={**check,'component_status':accepted['components'],
                    'scope':'Selected public SEC facts/filings;not complete statements or intraday PIT archive'}
            except Exception as exc:stages['sec_sources']=stage_error(exc,source_stage)
        else:stages['sec_sources']={'status':'BLOCKED_CONFIGURATION','missing':config['sec']['missing_configuration']}
        if config['alpaca']['ready'] and workspace.environment.get('GIG_ALPACA_LIVE_ENABLED')=='1':
            if not exclusive_stream_window:stages['live']={'status':'BLOCKED_SHARED_ACCOUNT_WINDOW_NOT_CONFIRMED','new_connections':0}
            else:
                try:
                    stream=(stream_factory or LiveIEX)(workspace,retry_budget=1)
                    symbols=['AAPL','MSFT'][:stream.symbol_limit()]
                    stages['live']=await collect_stream(stream,symbols,seconds)
                except Exception as exc:stages['live']=stage_error(exc,'live_stream')
        else:stages['live']={'status':'BLOCKED_EXISTING_LIVE_GATE','new_connections':0}
        required=('assets','history_AAPL','history_MSFT','comparison','sec_identity','sec_financials','live')
        passed=all(stages.get(k,{}).get('status','').startswith('PASS_') or k=='sec_financials' and stages.get(k,{}).get('status')=='AGREEMENT_WITHIN_SELECTED_RECORD_SCOPE' for k in required)
        if stages.get('sec_financials',{}).get('component_status') and any(v['status']!='AVAILABLE' for v in stages['sec_financials']['component_status'].values()):passed=False
        if compare and stages.get('comparison',{}).get('frontend_agreement',{}).get('status')!='PASS':passed=False
        # Injected transports never qualify observed-provider operations,even if fixtures say otherwise.
        observed=workspace.fetcher is None and workspace.origin=='OBSERVED_OFFICIAL_RESPONSE' and stream_factory is None
        result['status']='PASS_BOUNDED_SOURCE_PROBES_ONLY' if passed and observed else 'INCOMPLETE_OR_BLOCKED_SOURCE_QUALIFICATION'
        result['observed_provider_qualification']=passed and observed
        result['identity_coverage']={'runtime_searchable_identity_count':len(set(workspace.catalog.rows)|set(workspace.issuers)),
            'accepted_provider_assets':stages.get('assets',{}).get('observed_identities',0),
            'accepted_SEC_ticker_mappings':len(workspace.issuers) if workspace.origin=='OBSERVED_OFFICIAL_RESPONSE' else 0,
            'count_status':'OBSERVED_REFERENCE_IDENTITIES_NOT_COMPLETE_US_LISTINGS' if observed and stages.get('assets',{}).get('observed_identities',0)>0 else 'UNQUALIFIED_PROCESS_IDENTITY_COUNT',
            'representative_symbols':{s:{'catalog_identity':s in workspace.catalog.rows,'official_SEC_cik':workspace.issuers.get(s,{}).get('cik') if workspace.origin=='OBSERVED_OFFICIAL_RESPONSE' else None}for s in ('AAPL','APLD','CRWV')},
            'scope':'Search namespace may combine provider assets,SEC registrants and curated fallbacks;not a count of all current exchange-listed stocks'}
        return result
    finally:await workspace.close()
