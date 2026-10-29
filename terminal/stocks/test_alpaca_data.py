"""Independent authored asset/history contracts;no Alpaca account or market observations."""
import asyncio,copy,json,unittest,uuid
from unittest.mock import patch
from urllib.parse import parse_qs,urlsplit
from starlette.testclient import TestClient
import httpx
from .service import StockWorkspace
from .test_repair import ENV
from .alpaca_reference import parse
from .alpaca_history import acquire
from .alpaca_transport import validate_url,ASSETS,DATA


def asset(symbol='APLD',status='active',identity=1,**extra):
    return {'id':str(uuid.UUID(int=identity)),'symbol':symbol,'name':'Authored '+symbol,'exchange':'NASDAQ','class':'us_equity','status':status,'tradable':True,**extra}


def response(kind='bars',symbol='AAPL',stamp='2026-10-20T12:00:00.123456789Z',token=None):
    rows={'bars':{'t':stamp,'o':'100','h':'102','l':'99','c':'101','v':10,'vw':'100.25','n':2},
          'quotes':{'t':stamp,'bp':'100.25','ap':'100.75','bs':3,'as':1,'bx':'V','ax':'V','c':['R'],'z':'C'},
          'trades':{'t':stamp,'p':'100.50','s':2,'i':42,'x':'V','c':['@'],'z':'C'}}
    return {kind:{symbol:[rows[kind]]},'next_page_token':token}


class ReferenceContracts(unittest.TestCase):
    def test_exact_source_flags_and_inactive_identity_without_entitlement(self):
        c=parse([('active',[asset()]),('inactive',[asset('CRWV','inactive',2,tradable=False)])],'HISTORICAL_SYNTHETIC')
        self.assertEqual(c.rows['APLD']['asset_id'],str(uuid.UUID(int=1)))
        self.assertEqual(c.rows['CRWV']['listing_status'],'INACTIVE')
        self.assertFalse(c.rows['CRWV']['provider_flags']['tradable'])
        self.assertEqual(c.rows['APLD']['security_type'],'US_EQUITY_SUBTYPE_UNVERIFIED')
        self.assertNotIn('cik',c.rows['APLD'])
    def test_duplicate_ids_symbols_wrong_enums_and_unsafe_fields(self):
        for rows in [[asset(),asset(identity=2)],[asset(),asset('CRWV')],[asset(status='invalid')],[asset(tradable='yes')],[asset(id='bad')],[asset(name='bad\nname')]]:
            with self.assertRaises(ValueError):parse([('active',rows)],'HISTORICAL_SYNTHETIC')
    def test_unsupported_share_class_not_silently_converted(self):
        c=parse([('active',[asset('BRK.B'),asset('A/B',identity=2)])],'HISTORICAL_SYNTHETIC')
        self.assertEqual(list(c.rows),['BRK.B']);self.assertEqual(c.source['excluded']['unsupported_symbol'],1)
    def test_all_representative_symbols_keep_identity_independent_of_sec(self):
        from .discovery import search
        w=StockWorkspace(environment={});symbols=['AAPL','GOOGL','MSFT','NVDA','AMZN','APLD','CRWV']
        w.catalog=parse([('active',[asset(s,identity=i+1) for i,s in enumerate(symbols)])],'HISTORICAL_SYNTHETIC')
        for s in symbols:
            self.assertEqual(search(w,s)['results'][0]['symbol'],s)
            self.assertFalse(w.view(s)['capabilities']['iex_refresh'])
        self.assertIsNone(w.resolve('APLD')['cik']);self.assertIsNone(w.resolve('CRWV')['cik'])
    def test_filters_before_pagination_and_no_inferred_class(self):
        from .discovery import search
        w=StockWorkspace(environment={});w.catalog=parse([('active',[asset()]),('inactive',[asset('CRWV','inactive',2,exchange='OTC')])],'HISTORICAL_SYNTHETIC')
        self.assertEqual(search(w,'',filters={'listing_status':'INACTIVE'})['results'][0]['symbol'],'CRWV')
        self.assertEqual(search(w,'',filters={'exchange':'NASDAQ','security_type':'ETF'})['matches'],0)
        self.assertIn('OTC',search(w,'')['available_filters']['exchange'])
        with self.assertRaises(ValueError):search(w,'',filters={'arbitrary':'yes'})
    def test_read_only_allowlist_rejects_trading_or_credentials_destinations(self):
        allowed=[ASSETS+'?asset_class=us_equity&status=active',DATA+'quotes?symbols=AAPL&feed=iex',DATA+'AAPL/trades/latest?feed=iex']
        for url in allowed:self.assertIn(validate_url(url,'alpaca'),('array','object'))
        for url in ['https://paper-api.alpaca.markets/v2/orders','https://api.alpaca.markets/v2/assets','https://paper-api.alpaca.markets/v2/account','https://paper-api.alpaca.markets/v2/positions',DATA+'quotes?feed=sip',DATA+'quotes?feed=iex&feed=sip',DATA+'AAPL/../../orders?feed=iex','http://data.alpaca.markets/v2/stocks/bars?feed=iex',DATA+'bars?feed=iex#ignored','https://data.alpaca.markets.attacker.invalid/v2/stocks/bars?feed=iex']:
            with self.assertRaises(ValueError):validate_url(url,'alpaca')


class Acquisition(unittest.IsolatedAsyncioTestCase):
    async def fast(self,w,op):
        original=asyncio.sleep
        async def sleep(_):w.last_request=-100;await original(0)
        with patch('terminal.stocks.alpaca_history.asyncio.sleep',sleep):return await op()
    def workspace(self,fetch):
        self.ticks=[100]
        return StockWorkspace(environment=ENV,fetcher=fetch,clock=lambda:self.ticks[0])
    async def test_bounded_pagination_preserves_nanos_and_provenance(self):
        calls=[]
        async def fetch(url,*_):
            q=parse_qs(urlsplit(url).query);calls.append(q)
            return json.dumps(response('quotes',stamp='2026-10-20T12:00:0'+str(len(calls))+'.123456789Z',token='PRIVATE_PAGE_TOKEN' if len(calls)==1 else None)).encode()
        w=self.workspace(fetch);r=await self.fast(w,lambda:acquire(w,'AAPL','quotes','2026-10-20','2026-10-20'))
        self.assertEqual(r['record_count'],2);self.assertEqual(r['pages'],2);self.assertEqual(r['records'][0]['source_timestamp_ns'],'1792497601123456789')
        self.assertEqual(r['records'][0]['wire_metadata']['bx'],'V');self.assertEqual(r['origin'],'HISTORICAL_SYNTHETIC')
        self.assertFalse(r['complete_market_history']);self.assertNotIn('PRIVATE_PAGE_TOKEN',json.dumps(r));self.assertNotIn('authored_secret',json.dumps(r))
        self.assertEqual(calls[1]['page_token'],['PRIVATE_PAGE_TOKEN']);self.assertEqual(calls[0]['feed'],['iex'])
    async def test_all_historical_families_and_exact_decimal_values(self):
        for kind in ['bars','quotes','trades']:
            async def fetch(*_):return json.dumps(response(kind)).encode()
            w=self.workspace(fetch);r=await self.fast(w,lambda:acquire(w,'AAPL',kind,'2026-10-20','2026-10-20'))
            self.assertEqual(r['record_count'],1);self.assertEqual(r['records'][0]['close' if kind=='bars' else 'bid' if kind=='quotes' else 'price'],'101' if kind=='bars' else '100.25' if kind=='quotes' else '100.50')
            self.assertEqual(r['freshness'],'HISTORICAL_NOT_LIVE')
    async def test_page_limit_and_duplicates_are_explicit(self):
        async def fetch(*_):return json.dumps(response('trades',token='more')).encode()
        w=self.workspace(fetch);r=await self.fast(w,lambda:acquire(w,'AAPL','trades','2026-10-20','2026-10-20',max_pages=1))
        self.assertTrue(r['has_more']);self.assertEqual(r['record_count'],1)
        self.ticks[0]+=61
        pages=[response('trades',token='two'),response('trades')]
        async def dupe(*_):return json.dumps(pages.pop(0)).encode()
        w.fetcher=dupe;r=await self.fast(w,lambda:acquire(w,'AAPL','trades','2026-10-20','2026-10-20'))
        self.assertEqual(r['duplicate_source_records'],1);self.assertEqual(r['record_count'],2)
    async def test_invalid_second_page_failure_preserves_accepted_cache(self):
        pages=[]
        async def fetch(*_):return json.dumps(pages.pop(0) if pages else response()).encode()
        w=self.workspace(fetch);old=await self.fast(w,lambda:acquire(w,'AAPL','bars','2026-10-20','2026-10-20'))
        self.ticks[0]+=61;pages.extend([response(token='next'),response(stamp='2026-10-19T00:00:00Z')])
        with self.assertRaises(ValueError):await self.fast(w,lambda:acquire(w,'AAPL','bars','2026-10-20','2026-10-20'))
        self.assertIs(next(iter(w.market_history_cache.values()))[1],old)
    async def test_wrong_symbol_interval_order_bad_token_and_ohlc(self):
        malformed=[response(symbol='NVDA'),response(stamp='2026-10-21T00:00:00Z'),response(token='bad\n'),{'bars':{'AAPL':[response()['bars']['AAPL'][0]]*65}},response()]
        malformed[-1]['bars']['AAPL'][0]['h']='90'
        for p in malformed:
            async def fetch(*_):return json.dumps(p).encode()
            w=self.workspace(fetch)
            with self.assertRaises(ValueError):await self.fast(w,lambda:acquire(w,'AAPL','bars','2026-10-20','2026-10-20'))
            self.assertFalse(w.market_history_cache)
    async def test_token_cycle_and_out_of_order_rejected(self):
        for rows in [[response('quotes',token='cycle'),response('quotes',token='cycle')],[response(token='next'),response(stamp='2026-10-20T10:00:00Z')]]:
            async def fetch(*_):return json.dumps(rows.pop(0)).encode()
            w=self.workspace(fetch)
            with self.assertRaises(ValueError):await self.fast(w,lambda:acquire(w,'AAPL','quotes' if len(rows[0].get('quotes',{})) else 'bars','2026-10-20','2026-10-20'))
            self.assertFalse(w.market_history_cache)
    async def test_cache_reuses_source_receipt_but_permission_rechecked(self):
        calls=[]
        async def fetch(*_):calls.append(1);return json.dumps(response()).encode()
        w=self.workspace(fetch);a=await self.fast(w,lambda:acquire(w,'AAPL','bars','2026-10-20','2026-10-20'));b=await acquire(w,'AAPL','bars','2026-10-20','2026-10-20')
        self.assertEqual(len(calls),1);self.assertEqual(a['received_at'],b['received_at']);self.assertEqual(b['cache_status'],'ACCEPTED_REFERENCE_REUSED')
        w.environment={}
        with self.assertRaises(ValueError):await acquire(w,'AAPL','bars','2026-10-20','2026-10-20')
    async def test_cancellation_and_resource_error_never_publish(self):
        entered=asyncio.Event()
        async def fetch(*_):entered.set();await asyncio.Event().wait()
        w=self.workspace(fetch);task=asyncio.create_task(acquire(w,'AAPL','bars','2026-10-20','2026-10-20'));await entered.wait();task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        self.assertFalse(w.market_history_cache);self.assertFalse(w.lock.locked())
        async def over(*_):return b'x'*(512*1024+1)
        w.fetcher=over;w.last_request=-100
        with self.assertRaises(ValueError):await acquire(w,'AAPL','bars','2026-10-20','2026-10-20')
        self.assertFalse(w.market_history_cache)
    async def test_no_permission_or_invalid_request_never_fetches(self):
        async def fetch(*_):self.fail('unexpected request')
        w=StockWorkspace(environment={},fetcher=fetch)
        with self.assertRaises(ValueError):await acquire(w,'AAPL','bars','2026-10-20','2026-10-20')
        w=self.workspace(fetch)
        for args in [('quotes','2026-10-01','2026-10-20',1),('bars','bad','2026-10-20',1),('bars','2026-10-20','2026-10-20',True)]:
            with self.assertRaises(ValueError):await acquire(w,'AAPL',args[0],args[1],args[2],max_pages=args[3])
    async def test_asset_initialization_atomic_failure_and_cooldown(self):
        calls=[]
        async def fetch(url,*_):
            calls.append(url);status=parse_qs(urlsplit(url).query)['status'][0]
            return json.dumps([asset('APLD' if status=='active' else 'CRWV',status,1 if status=='active' else 2)]).encode()
        w=self.workspace(fetch);r=await self.fast(w,w.asset_reference.refresh);old=w.catalog
        self.assertEqual(r['accepted_count'],2);self.assertEqual(r['observed_provider_count'],0)
        self.assertEqual(len(calls),2);self.assertFalse(w.resolve('APLD')['cik'])
        with self.assertRaises(ValueError):await w.asset_reference.refresh()
        self.ticks[0]+=301
        async def fail(*_):return b'not json'
        w.fetcher=fail
        with self.assertRaises(ValueError):await self.fast(w,w.asset_reference.refresh)
        self.assertIs(w.catalog,old)
    async def test_real_transport_429_no_retries_and_cooldown(self):
        calls=[]
        def transport(request):calls.append(request);return httpx.Response(429)
        original=httpx.AsyncClient
        w=StockWorkspace(environment=ENV)
        with patch('terminal.stocks.service.httpx.AsyncClient',lambda **kw:original(transport=httpx.MockTransport(transport),**kw)):
            for _ in range(2):
                with self.assertRaises(ValueError):await self.fast(w,lambda:acquire(w,'AAPL','bars','2026-10-20','2026-10-20'))
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0].method,'GET');self.assertEqual(calls[0].url.host,'data.alpaca.markets')
    async def test_asset_worker_default_gates_and_cancel(self):
        async def fetch(*_):self.fail('injected context must not acquire implicitly')
        w=self.workspace(fetch);self.assertFalse(w.asset_reference.enabled())
        task=asyncio.create_task(w.asset_reference.run());await asyncio.sleep(0);task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        w.production_configuration=True;self.assertTrue(w.asset_reference.enabled());w.environment['GIG_ALPACA_ASSET_REFERENCE_ENABLED']='0';self.assertFalse(w.asset_reference.enabled())

    async def test_account_paths_rejected_before_credentials_reach_transport(self):
        calls=[]
        async def fetch(url,*_):calls.append(url);return b'{}'
        w=self.workspace(fetch)
        for path in ('orders','account','positions','assets/attacker'):
            with self.assertRaises(ValueError):await w.fetch('alpaca','https://paper-api.alpaca.markets/v2/'+path,w.permission('alpaca'))
        self.assertEqual(calls,[])

    async def test_history_cache_has_explicit_sixteen_query_limit(self):
        async def fetch(url,*_):
            day=parse_qs(urlsplit(url).query)['start'][0][:10]
            return json.dumps(response(stamp=day+'T12:00:00Z')).encode()
        w=self.workspace(fetch)
        for i in range(1,18):
            day=f'2026-10-{i:02}'
            await self.fast(w,lambda:acquire(w,'AAPL','bars',day,day))
        self.assertEqual(len(w.market_history_cache),16)
        self.assertNotIn('2026-10-01',[key[2] for key in w.market_history_cache])

    async def test_asset_parse_allocation_failure_retains_previous_snapshot(self):
        async def fetch(url,*_):
            status=parse_qs(urlsplit(url).query)['status'][0]
            return json.dumps([asset(status=status)] if status=='active' else []).encode()
        w=self.workspace(fetch);old=w.catalog
        with patch('terminal.stocks.alpaca_reference.parse',side_effect=MemoryError('authored allocation failure')):
            with self.assertRaises(ValueError):await self.fast(w,w.asset_reference.refresh)
        self.assertIs(w.catalog,old);self.assertFalse(w.lock.locked())


class ApiBoundary(unittest.TestCase):
    def test_new_proof_targets_no_urls_keys_or_cross_origin(self):
        from terminal.server.app import create_app
        from terminal.server.request_proofs import TARGETS
        w=StockWorkspace(environment={})
        with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
            for path in ['/api/v1/stocks/assets-refresh','/api/v1/stocks/market-history']:
                self.assertIn(path,TARGETS);self.assertEqual(c.post(path,json={}).status_code,403)
                self.assertEqual(c.post(path,json={'url':'https://attacker.invalid','api_key':'SECRET'},headers={'Origin':'http://127.0.0.1:8787'}).status_code,422)
            for path in ['/api/v1/stocks/orders','/api/v1/stocks/account','/api/v1/stocks/positions']:
                self.assertEqual(c.post(path,json={},headers={'Origin':'http://127.0.0.1:8787'}).status_code,405)
            self.assertEqual(c.get('/api/v2/securities?exchange=NASDAQ&exchange=NYSE').status_code,422)
    def test_source_errors_do_not_expose_credentials_or_mutate_native_book(self):
        from terminal.server.app import create_app
        async def fetch(*_):raise httpx.ConnectError('authored_secret leaked by an upstream')
        w=StockWorkspace(environment=ENV,fetcher=fetch)
        with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
            before=c.get('/api/v1/state').json()['book']
            r=c.post('/api/v1/stocks/market-history',json={'symbol':'AAPL','kind':'bars','start':'2026-10-20','end':'2026-10-20'},headers={'Origin':'http://127.0.0.1:8787'})
            self.assertEqual(r.status_code,422);self.assertNotIn('authored_secret',r.text);self.assertEqual(c.get('/api/v1/state').json()['book'],before)
