"""Server-owned fixed-destination read-only data access. Disabled without review gates."""
import asyncio,datetime,hashlib,json,os,re,time
from collections import OrderedDict
from decimal import Decimal
import httpx
from .identity import instrument,search
from . import sec,prices

class AccessError(ValueError):pass

class StockWorkspace:
    def __init__(self,environment=None,fetcher=None,clock=time.monotonic):
        self.environment=os.environ if environment is None else environment
        self.fetcher=fetcher;self.origin='HISTORICAL_SYNTHETIC' if fetcher is not None else 'OBSERVED_OFFICIAL_RESPONSE'
        self.clock=clock;self.last_request=-100.;self.cooldown_until=0.;self.cache=OrderedDict();self.lock=asyncio.Lock();self.last_error=None
    def permission(self,provider):
        e=self.environment
        if provider=='sec':
            if e.get('GIG_SEC_ENABLED')!='1' or e.get('GIG_SEC_POLICY_REVIEWED')!='1':raise AccessError('sec_disabled_pending_fair_access_review')
            agent=e.get('GIG_SEC_USER_AGENT','')
            if not re.fullmatch(r'[ -~]{8,160}',agent) or '@' not in agent:raise AccessError('sec_identifying_user_agent_required')
            return {'User-Agent':agent}
        required=('ENABLED','PROTOCOL_REVIEWED','PRIVATE_DISPLAY_APPROVED','CLOUD_PROCESSING_APPROVED','NO_COST_CONFIRMED')
        if any(e.get('GIG_ALPACA_'+k)!='1' for k in required):raise AccessError('alpaca_disabled_pending_entitlement_protocol_and_usage_review')
        ref=e.get('GIG_ALPACA_PERMISSION_REFERENCE','')
        if not ref or len(ref)>256 or any(ord(c)<32 for c in ref):raise AccessError('alpaca_permission_reference')
        keys=[e.get(k,'') for k in ('APCA_API_KEY_ID','APCA_API_SECRET_KEY')]
        if any(not re.fullmatch(r'[A-Za-z0-9_-]{8,256}',k) for k in keys):raise AccessError('alpaca_server_credentials_required')
        return dict(zip(('APCA-API-KEY-ID','APCA-API-SECRET-KEY'),keys))
    async def fetch(self,provider,url,headers):
        if self.clock()<self.cooldown_until:raise AccessError('upstream_failure_cooldown')
        if self.clock()-self.last_request<1:raise AccessError('upstream_rate_limit_one_request_per_second')
        self.last_request=self.clock()
        cap=8*1024*1024 if provider=='sec' else 512*1024
        if self.fetcher is not None:data=await self.fetcher(url,headers,cap)
        else:
            # No browser URL,redirect,automatic retry,compressed expansion or credential echo.
            async with httpx.AsyncClient(timeout=httpx.Timeout(8),follow_redirects=False,limits=httpx.Limits(max_connections=1),headers={'Accept-Encoding':'identity'}) as client:
                async with client.stream('GET',url,headers=headers) as response:
                    if response.status_code in (429,503):self.cooldown_until=self.clock()+60
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
        payload=json.loads(data,parse_float=Decimal,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('invalid_constant')),object_pairs_hook=pairs)
        if type(payload) is not dict:raise AccessError('upstream_object_required')
        return payload,hashlib.sha256(data).hexdigest()
    def view(self,ticker):
        company=instrument(ticker);cached=self.cache.get(ticker,{})
        out={'schema':'gig.stock.workspace.v1','instrument':company,'classification':self.origin if cached else 'UNAVAILABLE','fundamentals':cached.get('sec',{'status':'UNAVAILABLE','reason':'no_authorized_SEC_response_loaded'}),'prices':cached.get('alpaca',{'status':'UNAVAILABLE','reason':'no_authorized_IEX_response_loaded'}),'capabilities':{'sec_refresh':False,'iex_refresh':False,'equities_depth':False,'options_quotes':False,'third_party_news':False}}
        for p,k in [('sec','sec_refresh'),('alpaca','iex_refresh')]:
            try:self.permission(p);out['capabilities'][k]=True
            except AccessError:pass
        for key in ('fundamentals','prices'):
            item=out[key]
            if 'received_at' in item:
                age=max(0,(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(item['received_at'])).total_seconds())
                out[key]={**item,'response_age_seconds':round(age,3),'freshness':'CACHED_RESPONSE_NOT_LIVE_STREAM','last_refresh_error':self.last_error}
        if 'quotes' in out['prices']:
            for key in ('quotes','trades'):
                observed=out['prices'].get(key)
                if observed:
                    age=(datetime.datetime.now(datetime.timezone.utc)-prices.timestamp(observed['timestamp'])).total_seconds()
                    out['prices'][key]={**observed,'source_age_approximate_seconds':age,'clock_status':'FUTURE_SOURCE_CLOCK' if age<0 else 'SOURCE_TIMESTAMP_OBSERVED_NOT_STREAM_FRESHNESS'}
        return out
    async def refresh(self,ticker,provider,*,start=None,end=None,timeframe='1Day'):
        company=instrument(ticker)
        if provider not in ('sec','alpaca'):raise AccessError('unsupported_provider')
        headers=self.permission(provider)
        if self.lock.locked():raise AccessError('upstream_refresh_busy')
        async with self.lock:
            previous=self.cache.get(ticker,{})
            stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();hashes=[];urls=[]
            try:
                async with asyncio.timeout(25):
                    if provider=='sec':
                        cik=company['cik'];url=f'https://data.sec.gov/submissions/CIK{cik}.json';urls.append(url)
                        data,digest=await self.fetch(provider,url,headers);hashes.append(digest);result=sec.filings(data,cik)
                        await asyncio.sleep(1.01)
                        url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json';urls.append(url)
                        data,digest=await self.fetch(provider,url,headers);hashes.append(digest)
                        result['financials']=sec.facts(data,cik,stamp[:10])
                    else:
                        if not start or not end:raise AccessError('bounded_price_dates_required')
                        sec.date(start);sec.date(end)
                        if timeframe not in ('1Day','1Hour','1Min'):raise AccessError('price_timeframe')
                        maximum={'1Day':366,'1Hour':31,'1Min':7}[timeframe]
                        if not 0<(datetime.date.fromisoformat(end)-datetime.date.fromisoformat(start)).days<=maximum:raise AccessError('price_date_window')
                        url=f'https://data.alpaca.markets/v2/stocks/{ticker}/bars?timeframe={timeframe}&start={start}T00:00:00Z&end={end}T00:00:00Z&feed=iex&adjustment=raw&limit=256';urls.append(url)
                        data,digest=await self.fetch(provider,url,headers);hashes.append(digest);result=prices.bars(data,ticker);result['timeframe']=timeframe
                        for endpoint,parse in [('quotes/latest',prices.quote),('trades/latest',prices.trade)]:
                            await asyncio.sleep(1.01)
                            url=f'https://data.alpaca.markets/v2/stocks/{ticker}/{endpoint}?feed=iex';urls.append(url)
                            data,digest=await self.fetch(provider,url,headers);hashes.append(digest);result[endpoint.split('/')[0]]=parse(data,ticker)
                    result.update(status='AVAILABLE',received_at=stamp,origin=self.origin,source_urls=urls,response_sha256=hashes)
                    encoded=json.dumps(result,separators=(',',':'))
                    if len(encoded)>2*1024*1024:raise AccessError('normalized_response_budget')
            except Exception as exc:
                # Keep accepted cached result unchanged;never publish URL/key/error payload.
                self.cooldown_until=max(self.cooldown_until,self.clock()+10)
                self.last_error=str(exc) if isinstance(exc,AccessError) else 'upstream_parse_transport_or_validation_failure'
                raise AccessError(self.last_error) from None
            self.last_error=None
            self.cache[ticker]={**previous,provider:result};self.cache.move_to_end(ticker)
            while len(self.cache)>8:self.cache.popitem(last=False)
            return self.view(ticker)
