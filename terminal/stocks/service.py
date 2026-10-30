"""Server-owned fixed-destination read-only data access. Disabled without review gates."""
import asyncio,datetime,hashlib,json,os,re,time
from collections import OrderedDict
from decimal import Decimal
import httpx
from .identity import instrument,search
from . import sec,prices
from .auth import credentials,presence

class AccessError(ValueError):pass

def failure_reason(exc,fallback):
    if isinstance(exc,AccessError):return str(exc)
    if isinstance(exc,httpx.ProxyError):return 'upstream_proxy_connection_failure'
    if isinstance(exc,httpx.TimeoutException):return 'upstream_timeout'
    if isinstance(exc,httpx.ConnectError):return 'upstream_connect_or_TLS_failure'
    return fallback


class StockWorkspace:
    def __init__(self,environment=None,fetcher=None,clock=time.monotonic,history_store=None):
        self.production_configuration=environment is None
        from .sec_config import resolve
        self.environment,self.sec_config = resolve(os.environ) if environment is None else (environment,{'source':'explicit_environment','error':None})
        from .market_catalog import MarketCatalog
        self.catalog=MarketCatalog.configured(self.environment)
        from .directory import DirectoryService
        self.directory=DirectoryService(self)
        self.issuers={};self.issuer_source=None;self.sec_identity_accepted=None;self.sec_accepted={};self.sec_refresh_state={}
        from .history_store import configured
        self.history_store=history_store if history_store is not None else configured(self.environment)
        self.fetcher=fetcher;self.origin='HISTORICAL_SYNTHETIC' if fetcher is not None else 'OBSERVED_OFFICIAL_RESPONSE'
        self.clock=clock;self.last_request=-100.;self.cooldown_until=0.;self.cooldowns={};self.cache=OrderedDict();self.lock=asyncio.Lock();self.last_error=None;self.load_lock=asyncio.Lock();self.load_task=None;self.load_state={};self.errors={}
        from .alpaca_reference import AssetReference
        self.asset_reference=AssetReference(self)
        self.market_history_cache=OrderedDict();self.market_history_pending=0
    def resolve(self,ticker):
        if type(ticker) is not str:raise ValueError('invalid_symbol')
        if ticker in self.issuers:
            row=self.issuers[ticker]
            exchange=self.catalog.rows.get(ticker,{}).get('exchange','UNVERIFIED')
            return {**row,'exchange':exchange,'currency':'USD','identity_source':'accepted_SEC_company_tickers_response','identity_as_of':self.issuer_source['received_at'],'identity_source_record':self.issuer_source}
        try:
            seed=instrument(ticker)
            if ticker in self.catalog.rows:
                row=self.catalog.rows[ticker];seed={**seed,'company_name':row['name'],'exchange':row['exchange'],'security_type':row.get('security_type','UNCLASSIFIED_SEED'),'listing_status':row.get('listing_status','UNVERIFIED_SEED')}
            return seed
        except ValueError:
            row=self.catalog.instrument(ticker)
            return {'symbol':ticker,'company_name':row['name'],'exchange':row['exchange'],'cik':None,'currency':'USD','security_type':row.get('security_type','UNCLASSIFIED'),'listing_status':row.get('listing_status','UNVERIFIED'),'identity_source':'market_catalog_not_SEC_issuer_verified','identity_as_of':self.catalog.source['as_of']}
    async def refresh_identities(self):
        from .sec_identity import parse_reference,URL
        from .identity import SEEDS
        headers=self.permission('sec')
        now=self.clock()
        if self.sec_identity_accepted is not None and 0<=now-self.sec_identity_accepted<60:
            self.directory.sec_status='CACHED_ACCEPTED_REFERENCE'
            return {'schema':'gig.sec.identity.v1','count':len(self.issuers),'source':self.issuer_source,'refresh':'CACHED_ACCEPTED_REFERENCE','next_refresh_seconds':60-(now-self.sec_identity_accepted)}
        if self.lock.locked():raise AccessError('upstream_refresh_busy')
        async with self.lock:
            async with asyncio.timeout(10):
                payload,digest=await self.fetch('sec',URL,headers);rows,integrity=parse_reference(payload)
                for ticker,_,_,cik in SEEDS:
                    if ticker in rows and rows[ticker]['cik']!=str(cik).zfill(10):raise AccessError('sec_directory_curated_identity_conflict')
                for ticker,row in self.issuers.items():
                    if ticker in self.cache and (ticker not in rows or rows[ticker]['cik']!=row['cik']):raise AccessError('sec_directory_cached_issuer_change')
                source={'url':URL,'sha256':digest,'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':self.origin,'integrity':integrity,'scope':'Current SEC ticker mapping,accepted routable subset with explicit exclusions;not historical listing identity or feed entitlement'}
                accepted=self.clock()
                self.issuers,self.issuer_source=rows,source
                self.sec_identity_accepted=accepted
                self.directory.sec_status='ACCEPTED'
        return {'schema':'gig.sec.identity.v1','count':len(rows),'source':source}
    def search(self,query):
        found=self.catalog.search(query);q=query.strip().casefold()
        symbols=[r['symbol'] for r in found['results']]
        extra=sorted(s for s,r in self.issuers.items() if q in s.casefold() or q in r['company_name'].casefold())
        symbols=list(dict.fromkeys(symbols+extra))[:20]
        return {'results':[self.resolve(s) for s in symbols],'scope':found['scope'],'directory':{k:found[k] for k in ('catalog_count','source','reason')},'sec_directory':{'count':len(self.issuers),'source':self.issuer_source}}
    def market_identity(self,ticker):
        try:return self.catalog.instrument(ticker)
        except ValueError:
            if type(ticker) is not str or ticker not in self.issuers:raise ValueError('unsupported_market_symbol') from None
            row=self.issuers[ticker]
            source={**self.issuer_source,'authority':'SEC_TICKER_IDENTITY_NOT_PROVIDER_ASSET_QUALIFICATION','as_of':None}
            if 'integrity' in source:
                # Source-level diagnostics live once in directory status,not in each
                # of256 retained market events. Preserve digest/counts and exact ID.
                source['integrity']={k:source['integrity'][k] for k in ('input_rows','accepted_rows','excluded_rows','coverage','normalization')}
            return {'symbol':ticker,'name':row['company_name'],'exchange':'UNVERIFIED','asset_id':None,'identity_source':source}
    def market_search(self,query):
        found=self.catalog.search(query);q=query.strip().casefold();symbols=[r['symbol'] for r in found['results']]
        matches=[s for s,r in self.issuers.items() if q in s.casefold() or q in r['company_name'].casefold()]
        chosen=list(dict.fromkeys(symbols+sorted(matches)))[:20]
        total=len({s for s in self.catalog.rows if q in s.casefold() or q in self.catalog.rows[s]['name'].casefold()}|set(matches))
        return {**found,'results':[self.market_identity(s) for s in chosen],'matches':total,'returned':len(chosen),'catalog_count':len(set(self.catalog.rows)|set(self.issuers)),'source':{**found['source'],'authority':'CONFIGURED_AND_ACCEPTED_SEC_IDENTITIES_NOT_ENTITLEMENT','as_of':None} if self.issuers else found['source'],'sec_identity_source':self.issuer_source,'scope':'Identity discovery only;not current provider asset support,SEC fact availability or streaming entitlement'}
    def permission(self,provider):
        e=self.environment
        if provider=='sec':
            from .sec_config import readiness
            status=readiness(e)
            if self.sec_config['error']:raise AccessError(self.sec_config['error'])
            if not status['ready']:raise AccessError(status['reason'])
            return {'User-Agent':e['GIG_SEC_USER_AGENT']}
        required=('ENABLED','PROTOCOL_REVIEWED','PRIVATE_DISPLAY_APPROVED','CLOUD_PROCESSING_APPROVED','NO_COST_CONFIRMED')
        if any(e.get('GIG_ALPACA_'+k)!='1' for k in required):raise AccessError('alpaca_disabled_pending_entitlement_protocol_and_usage_review')
        ref=e.get('GIG_ALPACA_PERMISSION_REFERENCE','')
        if not ref or len(ref)>256 or any(ord(c)<32 for c in ref):raise AccessError('alpaca_permission_reference')
        try:result=credentials(e)
        except ValueError as exc:raise AccessError(str(exc)) from None
        if provider=='options':
            if any(e.get('GIG_ALPACA_OPTIONS_'+k)!='1' for k in ('ENABLED','PROTOCOL_REVIEWED','INDICATIVE_APPROVED')):raise AccessError('indicative_options_explicit_review_required;no_paid_OPRA_fallback')
        return result
    def configuration(self):
        result={}
        for provider in ('sec','alpaca','options'):
            try:self.permission(provider);reason=None
            except AccessError as exc:reason=str(exc)
            missing=[]
            if provider=='sec':
                from .sec_config import readiness
                missing=readiness(self.environment)['missing_configuration']
            else:
                missing=['GIG_ALPACA_'+k for k in ('ENABLED','PROTOCOL_REVIEWED','PRIVATE_DISPLAY_APPROVED','CLOUD_PROCESSING_APPROVED','NO_COST_CONFIRMED') if self.environment.get('GIG_ALPACA_'+k)!='1']
                if not self.environment.get('GIG_ALPACA_PERMISSION_REFERENCE'):missing.append('GIG_ALPACA_PERMISSION_REFERENCE')
                if not any(presence(self.environment)[p+'_pair_present'] for p in ('ALPACA','APCA')):missing+=['ALPACA_API_KEY_ID','ALPACA_API_SECRET_KEY']
                if provider=='options':missing+=['GIG_ALPACA_OPTIONS_'+k for k in ('ENABLED','PROTOCOL_REVIEWED','INDICATIVE_APPROVED') if self.environment.get('GIG_ALPACA_OPTIONS_'+k)!='1']
            result[provider]={'ready':reason is None,'reason':reason,'missing_configuration':missing,'action':'Review current provider policy/entitlement,configure the listed server variables/Codespaces secrets,then restart and Load available data. Never paste keys in chat.','last_error':None}
        result['sec'].update({k:v for k,v in readiness(self.environment).items() if k not in ('ready','reason')})
        result['sec']['configuration_source']=self.sec_config['source']
        result['sec']['action']='Run .venv/bin/python scripts/configure_sec.py --check;configure Codespaces secrets or the private helper,then restart. Never paste the contact value in chat.'
        result['alpaca_credential_presence']=presence(self.environment)
        return result
    async def close(self):
        if self.load_task and not self.load_task.done():
            self.load_task.cancel()
            try:await self.load_task
            except asyncio.CancelledError:pass
    async def start_load(self,ticker,*,timeframe='1Day'):
        self.resolve(ticker)
        if timeframe not in ('1Day','1Hour','1Min'):raise AccessError('price_timeframe')
        async with self.load_lock:
            await self.close()
            self.load_state={'symbol':ticker,'status':'LOADING','sections':{}}
            self.load_task=asyncio.create_task(self._load(ticker,timeframe))
        return self.view(ticker)
    async def _load(self,ticker,timeframe):
        try:
            async with asyncio.timeout(60):
                for provider in ('sec','alpaca','options'):
                    try:
                        self.permission(provider)
                        await asyncio.sleep(max(0,1.01-(self.clock()-self.last_request)))
                        end=datetime.date.today();days={'1Day':90,'1Hour':14,'1Min':3}[timeframe]
                        await self.refresh(ticker,provider,start=str(end-datetime.timedelta(days=days)),end=str(end),timeframe=timeframe,allow_cached=provider=='sec')
                        self.load_state['sections'][provider]=self.cache.get(ticker,{}).get(provider,{}).get('status','UNAVAILABLE')
                    except (ValueError,TimeoutError):self.load_state['sections'][provider]='UNAVAILABLE;see_configuration_or_section_error'
            self.load_state['status']='FINISHED'
        except TimeoutError:self.load_state['status']='TIME_LIMIT;accepted_sections_preserved'
        except asyncio.CancelledError:raise
        except Exception:self.load_state['status']='FAILED;sanitized_provider_failure'
    async def fetch(self,provider,url,headers):
        shape='object'
        if provider!='sec':
            from .alpaca_transport import validate_url
            shape=validate_url(url,provider)
        domain='sec' if provider=='sec' else 'alpaca'
        if self.clock()<self.cooldowns.get(domain,0):raise AccessError('upstream_failure_cooldown')
        if self.clock()-self.last_request<1:raise AccessError('upstream_rate_limit_one_request_per_second')
        self.last_request=self.clock()
        cap=8*1024*1024 if provider=='sec' or shape=='array' else 512*1024
        if self.fetcher is not None:data=await self.fetcher(url,headers,cap)
        else:
            # No browser URL,redirect,automatic retry,compressed expansion or credential echo.
            async with httpx.AsyncClient(timeout=httpx.Timeout(8),follow_redirects=False,limits=httpx.Limits(max_connections=1),headers={'Accept-Encoding':'identity'}) as client:
                async with client.stream('GET',url,headers=headers) as response:
                    if response.status_code in (429,503):self.cooldowns[domain]=self.clock()+60
                    if response.status_code!=200:raise AccessError('upstream_http_'+str(response.status_code))
                    if response.headers.get('content-encoding','identity').lower() not in ('identity',''):raise AccessError('compressed_response_refused')
                    try:length=int(response.headers.get('content-length','0'))
                    except ValueError:raise AccessError('upstream_length') from None
                    if not 0<=length<=cap:raise AccessError('upstream_body_budget')
                    data=bytearray()
                    async for chunk in response.aiter_raw():
                        if len(data)+len(chunk)>cap:raise AccessError('upstream_body_budget')
                        data.extend(chunk)
                    data=bytes(data)
        if type(data) is not bytes or len(data)>cap:raise AccessError('upstream_body_budget')
        def pairs(items):
            result={}
            for k,v in items:
                if k in result:raise ValueError('duplicate_field')
                result[k]=v
            return result
        try:payload=json.loads(data,parse_float=Decimal,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('invalid_constant')),object_pairs_hook=pairs)
        except RecursionError:raise AccessError('upstream_json_nesting') from None
        if type(payload) is not (list if shape=='array' else dict):raise AccessError('upstream_expected_json_shape')
        return payload,hashlib.sha256(data).hexdigest()
    def view(self,ticker):
        company=self.resolve(ticker);cached=self.cache.get(ticker,{})
        out={'schema':'gig.stock.workspace.v1','instrument':company,'classification':self.origin if cached else 'UNAVAILABLE','fundamentals':cached.get('sec',{'status':'UNAVAILABLE','reason':'no_authorized_SEC_response_loaded'}),'prices':cached.get('alpaca',{'status':'UNAVAILABLE','reason':'no_authorized_IEX_response_loaded'}),'options_market':cached.get('options',{'status':'UNAVAILABLE','reason':'no_authorized_indicative_option_snapshots_loaded'}),'configuration':self.configuration(),'load':dict(self.load_state) if self.load_state.get('symbol')==ticker else {'status':'NOT_LOADING'},'capabilities':{'sec_refresh':False,'iex_refresh':False,'equities_depth':False,'options_quotes':False,'third_party_news':False}}
        for p,k in [('sec','sec_refresh'),('alpaca','iex_refresh'),('options','options_quotes')]:
            try:
                self.permission(p)
                out['capabilities'][k]=p!='sec' or company['cik'] is not None
            except AccessError:pass
        for provider in ('sec','alpaca','options'):out['configuration'][provider]['last_error']=self.errors.get((ticker,provider))
        for key in ('fundamentals','prices','options_market'):
            item=out[key]
            if 'received_at' in item:
                age=max(0,(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(item['received_at'])).total_seconds())
                out[key]={**item,'response_age_seconds':round(age,3),'freshness':'STALE_CACHE' if key=='fundamentals' and age>86400 else 'CACHED_RESPONSE_NOT_LIVE_STREAM','last_refresh_error':self.errors.get((ticker,{'fundamentals':'sec','prices':'alpaca','options_market':'options'}[key]))}
        if 'quotes' in out['prices']:
            for key in ('quotes','trades'):
                observed=out['prices'].get(key)
                if observed:
                    age=(datetime.datetime.now(datetime.timezone.utc)-prices.timestamp(observed['timestamp'])).total_seconds()
                    out['prices'][key]={**observed,'source_age_approximate_seconds':age,'clock_status':'FUTURE_SOURCE_CLOCK' if age<0 else 'SOURCE_TIMESTAMP_OBSERVED_NOT_STREAM_FRESHNESS'}
        out['sec_refresh']=dict(self.sec_refresh_state.get(ticker,{'status':'IDLE'}))
        return out
    async def refresh(self,ticker,provider,*,start=None,end=None,timeframe='1Day',allow_cached=False):
        company=self.resolve(ticker)
        if provider not in ('sec','alpaca','options'):raise AccessError('unsupported_provider')
        headers=self.permission(provider)
        if provider=='sec' and company['cik'] is None:raise AccessError('sec_issuer_identity_unavailable;market_discovery_is_not_SEC_mapping')
        if provider=='sec' and allow_cached and ticker in self.sec_accepted and 'sec' in self.cache.get(ticker,{}):
            age=self.clock()-self.sec_accepted[ticker]
            if 0<=age<60:
                self.sec_refresh_state[ticker]={'status':'CACHED_RECENT','cached_age_seconds':round(age,3),'next_refresh_seconds':round(60-age,3),'reason':'Recent accepted SEC response reused;no upstream request'}
                return self.view(ticker)
        if self.lock.locked():raise AccessError('upstream_refresh_busy')
        async with self.lock:
            if provider=='sec':self.sec_refresh_state[ticker]={'status':'RUNNING'}
            previous=self.cache.get(ticker,{})
            stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();hashes=[];urls=[];source_records=[]
            try:
                async with asyncio.timeout(25):
                    if provider=='sec':
                        cik=company['cik'];result={'components':{}}
                        requests=[('filings',f'https://data.sec.gov/submissions/CIK{cik}.json',lambda data:sec.filings(data,cik)),('financials',f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',lambda data:sec.facts(data,cik,stamp[:10]))]
                        for index,(kind,url,parse) in enumerate(requests):
                            if index:await asyncio.sleep(1.01)
                            try:
                                data,digest=await self.fetch(provider,url,headers);parsed=parse(data)
                                if kind=='filings':result.update(parsed)
                                else:
                                    from .financials import calculate
                                    parsed['analytics']=calculate(parsed);result['financials']=parsed
                                urls.append(url);hashes.append(digest);source_records.append({'component':kind,'url':url,'sha256':digest,'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});result['components'][kind]={'status':'AVAILABLE'}
                            except Exception as exc:result['components'][kind]={'status':'UNAVAILABLE','reason':failure_reason(exc,'upstream_parse_transport_or_validation_failure'),'action':'Review source policy,identity,schema and response budget;other accepted SEC section remains visible.'}
                        if hashes and result['components']['financials']['status']!='AVAILABLE' and previous.get('sec',{}).get('financials'):raise AccessError('SEC_companyfacts_failed_cached_financials_preserved')
                        if not hashes:raise AccessError('all_SEC_components_unavailable;'+','.join(k+'='+v['reason'] for k,v in result['components'].items()))
                        if any(c['status']!='AVAILABLE' for c in result['components'].values()):result['reason']='Partial SEC response;missing section: '+','.join(k+':'+v['reason'] for k,v in result['components'].items() if v['status']!='AVAILABLE')
                    elif provider=='options':
                        from .option_feed import snapshots
                        url=f'https://data.alpaca.markets/v1beta1/options/snapshots/{ticker}?feed=indicative&limit=100';urls.append(url)
                        data,digest=await self.fetch(provider,url,headers);hashes.append(digest);result=snapshots(data,ticker);source_records.append({'component':'option_snapshots','url':url,'sha256':digest,'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
                    else:
                        if not start or not end:raise AccessError('bounded_price_dates_required')
                        sec.date(start);sec.date(end)
                        if timeframe not in ('1Day','1Hour','1Min'):raise AccessError('price_timeframe')
                        maximum={'1Day':366,'1Hour':31,'1Min':7}[timeframe]
                        if not 0<(datetime.date.fromisoformat(end)-datetime.date.fromisoformat(start)).days<=maximum:raise AccessError('price_date_window')
                        from .quote_analytics import analyze
                        result={'feed':'iex','scope':'single-venue IEX only;not consolidated or full L2/3','components':{},'bars':[]}
                        exclusive_end=str(datetime.date.fromisoformat(end)+datetime.timedelta(days=1))
                        requests=[('bars',f'https://data.alpaca.markets/v2/stocks/{ticker}/bars?timeframe={timeframe}&start={start}T00:00:00Z&end={exclusive_end}T00:00:00Z&feed=iex&adjustment=raw&limit=256',prices.bars),('quotes',f'https://data.alpaca.markets/v2/stocks/{ticker}/quotes/latest?feed=iex',prices.quote),('trades',f'https://data.alpaca.markets/v2/stocks/{ticker}/trades/latest?feed=iex',prices.trade)]
                        for index,(kind,url,parse) in enumerate(requests):
                            if index:await asyncio.sleep(1.01)
                            try:
                                data,digest=await self.fetch(provider,url,headers);parsed=parse(data,ticker)
                                if kind=='bars':
                                    from terminal.providers.kraken import timestamp_ns
                                    lower=int(timestamp_ns(start+'T00:00:00Z'));upper=int(timestamp_ns(exclusive_end+'T00:00:00Z'))
                                    if any(not lower<=int(timestamp_ns(row['timestamp']))<upper for row in parsed['bars']):raise AccessError('bar_outside_requested_UTC_calendar_interval')
                                    result.update(parsed);result['timeframe']=timeframe;result['requested_interval']={'start':start+'T00:00:00Z','exclusive_end':exclusive_end+'T00:00:00Z','meaning':'user end date inclusive;latest bar completeness unknown'}
                                else:result[kind]=parsed
                                urls.append(url);hashes.append(digest);source_records.append({'component':kind,'url':url,'sha256':digest,'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat()});result['components'][kind]={'status':'AVAILABLE'}
                            except Exception as exc:
                                reason=failure_reason(exc,'invalid_or_unavailable_'+kind)
                                result['components'][kind]={'status':'UNAVAILABLE','reason':reason,'action':'Check entitlement/feed availability or retry after cooldown;other accepted sections remain visible.'}
                        if not hashes:raise AccessError('all_iex_components_unavailable;'+','.join(k+'='+v['reason'] for k,v in result['components'].items()))
                        if result['bars']:
                            from fractions import Fraction
                            first=Fraction(result['bars'][0]['close']);last=Fraction(result['bars'][-1]['close']);change=last-first;relative=change/first
                            from .price_research import describe
                            result['descriptive_research']=describe(result['bars'])
                            result['price_change']={'absolute':{'numerator':str(change.numerator),'denominator':str(change.denominator)},'relative':{'numerator':str(relative.numerator),'denominator':str(relative.denominator)},'scope':'first-to-last returned close,not necessarily prior-session change'}
                        if 'quotes' in result:
                            result['native_analytics']=analyze(result['quotes'])
                            history=list(previous.get('alpaca',{}).get('quote_history',[]))
                            quote=result['quotes']
                            if not history or quote!=history[-1]:history.append(quote)
                            result['quote_history']=history[-32:]
                    result.update(status='PARTIAL' if any(v['status']!='AVAILABLE' for v in result.get('components',{}).values()) else 'AVAILABLE',requested_at=stamp,received_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),origin=self.origin,source_urls=urls,response_sha256=hashes,source_records=source_records)
                    if provider=='alpaca' and result.get('bars'):
                        from .history import HistorySource,normalize
                        receipts=[r for r in source_records if r['component']=='bars']
                        if len(receipts)!=1:raise AccessError('history_unique_bar_receipt_required')
                        receipt=receipts[0]
                        history=normalize(ticker,timeframe,[{'bars':result['bars'],'sha256':receipt['sha256']}],HistorySource('alpaca','iex',result['scope'],'raw',self.origin,'fixture_only' if self.fetcher is not None else 'operator_review_not_independent_verification',receipt['received_at']),has_more=result.get('next_page_available',False))
                        result['history_integrity']={k:history[k] for k in ('schema','state','record_count','page_count','has_more','complete_history','source_sha256','session','canonical_sha256')}
                        result['history_integrity']['gap_candidate_count']=len(history['gap_candidates'])
                    encoded=json.dumps(result,separators=(',',':'))
                    if len(encoded)>2*1024*1024:raise AccessError('normalized_response_budget')
            except asyncio.CancelledError:
                if provider=='sec':self.sec_refresh_state[ticker]={'status':'CANCELLED','reason':'Refresh cancelled before publication;accepted cache unchanged','accepted_cache_preserved':bool(previous.get('sec'))}
                raise
            except Exception as exc:
                # Keep accepted cached result unchanged;never publish URL/key/error payload.
                domain='sec' if provider=='sec' else 'alpaca'
                self.cooldowns[domain]=max(self.cooldowns.get(domain,0),self.clock()+10)
                self.last_error=failure_reason(exc,'upstream_parse_transport_or_validation_failure')
                if provider=='sec':self.sec_refresh_state[ticker]={'status':'ERROR','reason':self.last_error,'accepted_cache_preserved':bool(previous.get('sec'))}
                self.errors[(ticker,provider)]=self.last_error
                raise AccessError(self.last_error) from None
            self.last_error=None;self.errors.pop((ticker,provider),None)
            self.cache[ticker]={**previous,provider:result};self.cache.move_to_end(ticker)
            if provider=='sec':
                self.sec_accepted[ticker]=self.clock();self.sec_refresh_state[ticker]={'status':'SUCCEEDED','next_refresh_seconds':60}
            while len(self.cache)>8:self.cache.popitem(last=False)
            return self.view(ticker)
