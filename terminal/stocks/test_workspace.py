"""Independently authored SEC/IEX-shaped inputs;no company/market observations."""
import asyncio,copy,datetime,json,math,unittest
from decimal import Decimal
from fractions import Fraction
from unittest.mock import patch
from starlette.testclient import TestClient
from .identity import search,instrument
from . import sec,prices,options,research
from .service import StockWorkspace,AccessError
from terminal.server.app import create_app

CIK='0000320193'
SEC_ENV={'GIG_SEC_ENABLED':'1','GIG_SEC_POLICY_REVIEWED':'1','GIG_SEC_USER_AGENT':'Authored Tests test@example.invalid'}
ALPACA_ENV={**{'GIG_ALPACA_'+k:'1' for k in ('ENABLED','PROTOCOL_REVIEWED','PRIVATE_DISPLAY_APPROVED','CLOUD_PROCESSING_APPROVED','NO_COST_CONFIRMED')},'GIG_ALPACA_PERMISSION_REFERENCE':'authored-not-a-license','APCA_API_KEY_ID':'authored_key','APCA_API_SECRET_KEY':'authored_secret'}

def submissions():return {'cik':320193,'filings':{'recent':{'accessionNumber':['0000000123-24-000001','0000000123-24-000002'],'form':['10-K','10-K/A'],'filingDate':['2024-02-01','2024-02-10'],'primaryDocument':['authored.htm','amendment.htm'],'acceptanceDateTime':['2024-02-01T12:00:00Z','2024-02-10T12:00:00Z'],'reportDate':['2023-12-31','2023-12-31']}}}
def fact(value=100,start='2023-01-01',end='2023-12-31',filed='2024-02-01',accn='0000000123-24-000001'):
    r={'val':value,'end':end,'filed':filed,'form':'10-K','accn':accn}
    if start:r['start']=start
    return r

def facts():return {'cik':320193,'facts':{'us-gaap':{'Revenues':{'units':{'USD':[fact(100)]}},'NetIncomeLoss':{'units':{'USD':[fact(20)]}},'Assets':{'units':{'USD':[fact(1000,None)]}},'Liabilities':{'units':{'USD':[fact(250,None)]}}}}}
def bars():return {'symbol':'AAPL','bars':[{'t':'2024-01-02T14:30:00Z','o':100,'h':102,'l':99,'c':101,'v':2,'vw':Decimal('100.5'),'n':3},{'t':'2024-01-03T14:30:00Z','o':101,'h':104,'l':100,'c':103,'v':3,'vw':Decimal('102.5'),'n':4}],'next_page_token':None}

class IdentityTests(unittest.TestCase):
    def test_required_tickers_and_name_search(self):
        self.assertEqual([r['symbol'] for r in search('nvidia')],['NVDA'])
        for ticker in ('AAPL','NVDA','TSLA','MSFT','AMZN','JPM'):self.assertEqual(len(instrument(ticker)['cik']),10)
    def test_no_arbitrary_instrument_or_injection(self):
        for value in ('../../keys','aapl','AAPL?key=secret','UNKNOWN'):
            with self.assertRaises(ValueError):instrument(value)
        with self.assertRaises(ValueError):search('x'*81)

class SECTests(unittest.TestCase):
    def test_filings_amendments_timeline_and_safe_links(self):
        out=sec.filings(submissions(),CIK);self.assertTrue(out['filings'][0]['amendment']);self.assertEqual(out['timeline'][0]['published_at'],'2024-02-10T12:00:00Z');self.assertIn('/320193/000000012324000002/amendment.htm',out['filings'][0]['url']);self.assertEqual(out['institutional_holdings']['status'],'UNAVAILABLE')
    def test_alignment_and_path_traversal(self):
        for change in ('columns','path','identity'):
            p=submissions()
            if change=='columns':p['filings']['recent']['form'].pop()
            elif change=='path':p['filings']['recent']['primaryDocument'][0]='../token'
            else:p['cik']=1
            with self.assertRaises(ValueError):sec.filings(p,CIK)
    def test_missing_optional_acceptance_not_invented(self):
        p=submissions();p['filings']['recent'].pop('acceptanceDateTime');self.assertIsNone(sec.filings(p,CIK)['filings'][0]['accepted_at'])
    def test_invalid_date_timezone_and_accession(self):
        for column,value in [('filingDate','2024-02-30'),('acceptanceDateTime','2024-02-01T12:00:00'),('accessionNumber','unsafe')]:
            p=submissions();p['filings']['recent'][column][0]=value
            with self.assertRaises(ValueError):sec.filings(p,CIK)
    def test_independent_exact_ratios(self):
        out=sec.facts(facts(),CIK,'2024-12-31')
        for name,reference in [('net_margin',Fraction(1,5)),('liabilities_to_assets',Fraction(1,4))]:
            v=out['ratios'][name]['value'];self.assertEqual(Fraction(int(v['numerator']),int(v['denominator'])),reference)
    def test_as_of_restatement_and_lookahead(self):
        p=facts();p['facts']['us-gaap']['Revenues']['units']['USD'].append(fact(200,filed='2024-03-01',accn='0000000123-24-000003'))
        self.assertEqual(sec.facts(p,CIK,'2024-02-20')['history']['revenue'][0]['value'],'100')
        self.assertEqual(sec.facts(p,CIK,'2024-04-01')['history']['revenue'][0]['value'],'200')
    def test_period_mismatch_and_missing_values(self):
        p=facts();p['facts']['us-gaap']['NetIncomeLoss']['units']['USD'][0]['start']='2023-10-01';out=sec.facts(p,CIK,'2024-12-31');self.assertIsNone(out['ratios']['net_margin']['value']);self.assertEqual(out['history']['cash'],[])
    def test_contradictory_same_filing_rejected(self):
        p=facts();p['facts']['us-gaap']['Revenues']['units']['USD'].append(fact(101))
        with self.assertRaisesRegex(ValueError,'contradictory'):sec.facts(p,CIK,'2024-12-31')
    def test_competing_concepts_not_silently_combined(self):
        p=facts();p['facts']['us-gaap']['SalesRevenueNet']={'units':{'USD':[fact(99)]}}
        self.assertEqual(sec.facts(p,CIK,'2024-12-31')['ratios']['net_margin']['reason'],'ambiguous_compatible_concepts')
    def test_decimal_and_exponent_resource_bounds(self):
        self.assertEqual(sec.exact(Decimal('12.123456789012')),'12.123456789012')
        for v in (True,Decimal('NaN'),Decimal('1e-99999999'),10**31):
            with self.assertRaises(ValueError):sec.exact(v)

class PriceTests(unittest.TestCase):
    def test_exact_vwap_ohlc_and_scope(self):
        out=prices.bars(bars(),'AAPL');v=out['vwap']['value'];self.assertEqual(Fraction(int(v['numerator']),int(v['denominator'])),Fraction(1017,10));self.assertFalse(out['complete_history']);self.assertEqual(out['feed'],'iex')
    def test_invalid_order_ohlc_identity_and_budget(self):
        for mode in ('order','ohlc','identity','budget'):
            p=bars()
            if mode=='order':p['bars'].reverse()
            elif mode=='ohlc':p['bars'][0]['h']=50
            elif mode=='identity':p['symbol']='NVDA'
            else:p['bars']*=129
            with self.assertRaises(ValueError):prices.bars(p,'AAPL')
    def test_missing_vwap_does_not_fabricate(self):
        p=bars();p['bars'][0].pop('vw');self.assertIsNone(prices.bars(p,'AAPL')['vwap']['value'])
    def test_source_nanoseconds_preserved_and_clock_scope(self):
        out=prices.quote({'symbol':'AAPL','quote':{'t':'2024-01-02T14:30:00.123456789Z','bp':100,'ap':101,'bs':1,'as':2}},'AAPL');self.assertTrue(out['timestamp'].endswith('123456789Z'));self.assertEqual(prices.market_window(out['timestamp'])['clock_window'],'REGULAR_CLOCK_WINDOW')
    def test_numeric_timestamp_and_expansion_bounds(self):
        for v in (True,'NaN','Infinity','-1','1e-99999999'):
            with self.assertRaises(ValueError):prices.decimal(v)
        with self.assertRaises(ValueError):prices.timestamp('2024-01-01')

class ModelTests(unittest.TestCase):
    def test_black_scholes_known_reference_and_parity(self):
        call=options.price(100,100,1,.2,.05);put=options.price(100,100,1,.2,.05,right='put')
        self.assertAlmostEqual(call['price'],10.450583572185565,places=11);self.assertAlmostEqual(call['price']-put['price'],100-100*math.exp(-.05),places=11)
    def test_greeks_independent_finite_differences(self):
        h=.001;f=lambda s:options.price(s,110,.7,.3,.02)['price'];g=options.price(100,110,.7,.3,.02)
        self.assertAlmostEqual(g['delta'],(f(100+h)-f(100-h))/(2*h),places=7);self.assertAlmostEqual(g['gamma'],(f(100+h)-2*f(100)+f(100-h))/h**2,places=6)
        v=lambda x:options.price(100,110,.7,x,.02)['price'];self.assertAlmostEqual(g['vega'],(v(.300001)-v(.299999))/.000002,places=6)
        r=lambda x:options.price(100,110,.7,.3,x)['price'];t=lambda x:options.price(100,110,x,.3,.02)['price']
        self.assertAlmostEqual(g['rho'],(r(.020001)-r(.019999))/.000002,places=6)
        self.assertAlmostEqual(g['theta_per_year'],-(t(.700001)-t(.699999))/.000002,places=6)
    def test_iv_roundtrip_and_unidentifiable_price(self):
        for v in (.05,.2,.8):self.assertAlmostEqual(options.implied(options.price(100,100,1,v)['price'],100,100,1),v,places=8)
        with self.assertRaises(ValueError):options.implied(1000,100,100,1)
    def test_model_bounds_and_occ_identity(self):
        for v in (True,float('nan'),-1,6):
            with self.assertRaises(ValueError):options.price(100,100,1,v)
        c=options.contract('AAPL  261120C00100000');self.assertEqual(c['strike_millis'],'100000');self.assertEqual(c['expiration'],'2026-11-20')
        with self.assertRaises(ValueError):options.contract('AAPL\n261120C00100000')
    def test_surface_is_explicitly_theoretical_and_bounded(self):
        out=options.scenario({'spot':100,'strike':100,'years':1,'volatility':.2});self.assertEqual(out['classification'],'THEORETICAL_SCENARIO');self.assertEqual(sum(map(len,out['surface'])),153);self.assertTrue(all(p['volatility']==.2 for row in out['surface'] for p in row))
    def test_empirical_risk_independent_sorted_reference(self):
        data=[str(Decimal(i)/1000) for i in range(-20,20)];out=research.analyze(data);risk=out['historical_risk'];self.assertEqual(Fraction(int(risk['var']['numerator']),int(risk['var']['denominator'])),Fraction(19,1000));self.assertEqual(Fraction(int(risk['expected_shortfall']['numerator']),int(risk['expected_shortfall']['denominator'])),Fraction(39,2000))
    def test_no_future_leak_in_filters_or_strategy(self):
        first=['0.01']*40;other=first[:20]+['-0.01']*20;a=research.analyze(first);b=research.analyze(other)
        self.assertEqual(a['kalman']['filtered_mean'][:20],b['kalman']['filtered_mean'][:20]);self.assertEqual(a['hmm']['high_volatility_probability'][:20],b['hmm']['high_volatility_probability'][:20]);self.assertEqual(a['garch']['one_step_variance'][:21],b['garch']['one_step_variance'][:21]);self.assertEqual(a['strategy']['positions'][:21],b['strategy']['positions'][:21])
    def test_strategy_cost_and_model_reference(self):
        out=research.analyze(['0.01']*20);self.assertEqual(out['strategy']['positions'][:6],[0,0,0,0,0,1]);self.assertEqual(out['strategy']['turnover_units'],1);self.assertEqual(out['garch']['one_step_variance'][1],1e-6+.08*.01**2+.9*.0001)
        wealth=out['strategy']['terminal_wealth'];self.assertEqual(Fraction(int(wealth['numerator']),int(wealth['denominator'])),Fraction(10099,10000)*Fraction(101,100)**14)
        self.assertAlmostEqual(out['kalman']['filtered_mean'][0],(1.00001/1.00101)*.01,places=14)
        self.assertAlmostEqual(research.analyze(['0']*20)['hmm']['high_volatility_probability'][0],1/6,places=14)
    def test_research_expansion_and_sample_bounds(self):
        for values in (['0.1']*19,['1e-99999999']*20,['NaN']*20,['2']*20):
            with self.assertRaises(ValueError):research.analyze(values)

class ServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_gate_before_any_network_and_no_credentials_in_view(self):
        async def fetch(*_):self.fail('no network')
        s=StockWorkspace(environment={},fetcher=fetch)
        with self.assertRaises(AccessError):await s.refresh('AAPL','sec')
        s.environment=ALPACA_ENV;self.assertNotIn('authored_secret',json.dumps(s.view('AAPL')))
    async def test_sec_atomic_refresh_fixture_provenance_and_hashes(self):
        async def fetch(url,headers,cap):return json.dumps(submissions() if '/submissions/' in url else facts()).encode()
        s=StockWorkspace(environment=SEC_ENV,fetcher=fetch,clock=lambda:100)
        async def sleep(_):s.last_request=-100
        with patch('terminal.stocks.service.asyncio.sleep',sleep):out=await s.refresh('AAPL','sec')
        self.assertEqual(out['classification'],'HISTORICAL_SYNTHETIC');self.assertEqual(len(out['fundamentals']['response_sha256']),2);before=copy.deepcopy(s.cache)
        async def broken(*_):raise RuntimeError('secret_token')
        s.fetcher=broken;s.last_request=-100
        with self.assertRaisesRegex(AccessError,'validation_failure'):await s.refresh('AAPL','sec')
        self.assertEqual(s.cache,before);self.assertNotIn('secret_token',json.dumps(s.view('AAPL')))
    async def test_alpaca_fixed_read_only_paths_and_single_venue(self):
        urls=[]
        async def fetch(url,headers,cap):
            urls.append(url);self.assertEqual(headers['APCA-API-SECRET-KEY'],'authored_secret')
            if '/bars?' in url:return json.dumps(bars(),default=str).encode()
            if '/quotes/latest' in url:return json.dumps({'symbol':'AAPL','quote':{'t':'2024-01-02T14:30:00Z','bp':100,'ap':101,'bs':1,'as':2}}).encode()
            return json.dumps({'symbol':'AAPL','trade':{'t':'2024-01-02T14:30:00Z','p':100,'s':1}}).encode()
        s=StockWorkspace(environment=ALPACA_ENV,fetcher=fetch,clock=lambda:100)
        async def sleep(_):s.last_request=-100
        with patch('terminal.stocks.service.asyncio.sleep',sleep):out=await s.refresh('AAPL','alpaca',start='2024-01-01',end='2024-01-05')
        self.assertEqual(len(urls),3);self.assertTrue(all(url.startswith('https://data.alpaca.markets/v2/stocks/AAPL/') and 'feed=iex' in url for url in urls));self.assertEqual(out['prices']['feed'],'iex');self.assertNotIn('authored_secret',json.dumps(out))
    async def test_duplicate_json_and_body_budget_fail_without_commit(self):
        for raw in (b'{"cik":1,"cik":2}',b'x'*(8*1024*1024+1)):
            async def fetch(*_):return raw
            s=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
            with self.assertRaises(AccessError):await s.refresh('AAPL','sec')
            self.assertEqual(len(s.cache),0)
    async def test_rate_budget_rejects_before_fetch_and_cache_bound(self):
        async def fetch(*_):self.fail('rate-limited')
        s=StockWorkspace(environment=SEC_ENV,fetcher=fetch,clock=lambda:1);s.last_request=1
        with self.assertRaisesRegex(AccessError,'rate_limit'):await s.refresh('AAPL','sec')
        self.assertEqual(s.cache,{})

class APITests(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict('os.environ',{'GIG_SEC_ENABLED':'0','GIG_ALPACA_ENABLED':'0','GIG_LIVE_ENABLED':'0','GIG_COINBASE_ENABLED':'0'});self.env.start();self.addCleanup(self.env.stop);self.app=create_app();self.c=TestClient(self.app,base_url="http://127.0.0.1:8787")
    def test_search_company_and_unavailable_no_fake_observations(self):
        self.assertEqual(self.c.get('/api/v1/stocks/search?q=Apple').json()['results'][0]['symbol'],'AAPL');out=self.c.get('/api/v1/stocks/company?symbol=AAPL').json();self.assertEqual(out['classification'],'UNAVAILABLE');self.assertNotIn('bars',out['prices'])
    def test_refresh_cannot_send_keys_urls_or_mutate_native(self):
        before=self.app.state.native.replay.canonical()
        r=self.c.post('/api/v1/stocks/refresh',headers={'Origin':'http://127.0.0.1:8787'},json={'symbol':'AAPL','provider':'sec','url':'https://attacker.invalid','key':'secret'});self.assertEqual(r.status_code,400);self.assertEqual(before,self.app.state.native.replay.canonical())
    def test_new_mutations_preserve_origin_boundary(self):
        for path,payload in [('refresh',{'symbol':'AAPL','provider':'sec'}),('options',{'spot':100,'strike':100,'years':1,'volatility':.2}),('research',{'returns':['0.01']*20})]:
            r=self.c.post('/api/v1/stocks/'+path,headers={'Origin':'https://attacker.invalid','X-Forwarded-Host':'localhost:8787'},json=payload);self.assertEqual(r.status_code,403)
    def test_option_research_and_disabled_refresh(self):
        headers={'Origin':'http://127.0.0.1:8787'};self.assertEqual(self.c.post('/api/v1/stocks/options',headers=headers,json={'spot':100,'strike':100,'years':1,'volatility':.2}).status_code,200)
        self.assertEqual(self.c.post('/api/v1/stocks/research',headers=headers,json={'returns':['0.01']*20}).status_code,200)
        self.assertEqual(self.c.post('/api/v1/stocks/refresh',headers=headers,json={'symbol':'AAPL','provider':'sec'}).status_code,422)


class DisclosureTests(unittest.TestCase):
    def xml(self):return b'<informationTable xmlns="urn:authored"><infoTable><nameOfIssuer>Authored Only</nameOfIssuer><cusip>000000000</cusip><value>12</value><shrsOrPrnAmt><sshPrnamt>34</sshPrnamt><sshPrnamtType>SH</sshPrnamtType></shrsOrPrnAmt></infoTable></informationTable>'
    def parse(self,raw,**kwargs):
        from .disclosures import holdings
        return holdings(raw,report_date='2024-03-31',filing_date='2024-05-15',accession='0000000123-24-000001',value_unit=kwargs.get('unit','USD_THOUSANDS'),amendment=kwargs.get('amendment',False))
    def test_explicit_historical_units_and_delayed_amendment(self):
        out=self.parse(self.xml(),amendment=True);self.assertEqual(out['holdings'][0]['value_usd'],'12000');self.assertTrue(out['amendment']);self.assertEqual(self.parse(self.xml(),unit='USD')['holdings'][0]['value_usd'],'12')
    def test_dtd_entity_and_encoding_rejected(self):
        for raw in (b'<!DOCTYPE x [<!ENTITY y "bad">]>'+self.xml(),self.xml().decode().encode('utf-16'),b'<broken>'):
            with self.assertRaises(ValueError):self.parse(raw)
    def test_units_duplicates_and_resource_limits(self):
        with self.assertRaises(ValueError):self.parse(self.xml(),unit='UNKNOWN')
        with self.assertRaises(ValueError):self.parse(self.xml().replace(b'<value>12</value>',b'<value>12</value><value>13</value>'))
        with self.assertRaises(ValueError):self.parse(b'x'*(1024*1024+1))

class SubscriptionTests(unittest.IsolatedAsyncioTestCase):
    def module(self):
        import importlib.util
        from pathlib import Path
        spec=importlib.util.spec_from_file_location('bounded_subscription',Path(__file__).resolve().parents[2]/'scripts/qualify_provider_subscription.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    async def test_explicit_owner_gate_before_transport(self):
        async def transport(*args,**kwargs):self.fail('must not subscribe');yield ''
        from terminal.providers.test_supervisor import ENV
        with self.assertRaisesRegex(ValueError,'approval_required'):await self.module().qualify('kraken','BTC/USD',1,environment=ENV,transport=transport)
    async def test_bounded_authored_native_validation_no_payload_output(self):
        from terminal.providers.test_supervisor import ENV
        from terminal.providers.test_kraken import book
        async def transport(*args,**kwargs):
            for _ in range(300):yield book()
        r=await self.module().qualify('kraken','BTC/USD',1,environment={**ENV,'GIG_PROVIDER_SUBSCRIPTION_TEST_APPROVED':'1'},transport=transport)
        self.assertEqual(r['classification'],'HISTORICAL_SYNTHETIC');self.assertEqual(r['native_book_transactions'],1);self.assertEqual(sum(r['message_kinds'].values()),256);self.assertEqual(r['native_revision'],'1');self.assertFalse(r['raw_payloads_retained']);self.assertFalse(r['recording']);self.assertNotIn('price_ticks',json.dumps(r))

class TransportBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_no_redirect_or_credential_echo(self):
        import httpx
        calls=[];actual=httpx.AsyncClient
        def handler(request):calls.append(request.url);return httpx.Response(302,headers={'location':'https://attacker.invalid/?token=secret'})
        with patch('terminal.stocks.service.httpx.AsyncClient',lambda **kw:actual(transport=httpx.MockTransport(handler),**kw)):
            s=StockWorkspace(environment=SEC_ENV)
            with self.assertRaisesRegex(AccessError,'upstream_http_302'):await s.fetch('sec','https://data.sec.gov/submissions/CIK0000320193.json',s.permission('sec'))
        self.assertEqual(len(calls),1)
    async def test_compressed_and_oversized_headers_refused(self):
        import httpx
        actual=httpx.AsyncClient
        for headers in ({'Content-Encoding':'gzip'},{'Content-Length':str(8*1024*1024+1)}):
            def handler(request):return httpx.Response(200,headers=headers,stream=httpx.ByteStream(b'not-read'))
            with patch('terminal.stocks.service.httpx.AsyncClient',lambda **kw:actual(transport=httpx.MockTransport(handler),**kw)):
                s=StockWorkspace(environment=SEC_ENV)
                with self.assertRaises(AccessError):await s.fetch('sec','https://data.sec.gov/submissions/CIK0000320193.json',s.permission('sec'))



class StockProofTests(unittest.TestCase):
    def setUp(self):
        import os
        self.origin='https://authored-stock-8787.app.github.dev';self.raw={'Origin':'http://localhost:8787','Host':'localhost:8787','X-Forwarded-Host':'authored-stock-8787.app.github.dev','X-Forwarded-Proto':'https'}
        env=patch.dict(os.environ,{'CODESPACES':'true','CODESPACE_NAME':'authored-stock','GIG_TERMINAL_ALLOWED_ORIGINS':self.origin,'GIG_SEC_ENABLED':'0','GIG_ALPACA_ENABLED':'0'});env.start();self.addCleanup(env.stop);self.c=TestClient(create_app(),base_url='http://localhost:8787')
    def proof(self,target,**changes):
        return self.c.get('/api/v1/request-proof',headers={**self.raw,'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':self.origin,'X-GIG-Target':target,'Sec-Fetch-Site':'same-origin',**changes})
    def test_three_exact_stock_targets_support_codespaces_rewrite(self):
        for path,body,status in [('options',{'spot':100,'strike':100,'years':1,'volatility':.2},200),('research',{'returns':['0.01']*20},200),('refresh',{'symbol':'AAPL','provider':'sec'},422)]:
            target='/api/v1/stocks/'+path;token=self.proof(target).json()['proof'];r=self.c.post(target,headers={**self.raw,'X-GIG-Request-Proof':token},json=body);self.assertEqual(r.status_code,status)
    def test_stock_proof_cannot_authorize_another_target_or_reuse(self):
        target='/api/v1/stocks/options';token=self.proof(target).json()['proof'];headers={**self.raw,'X-GIG-Request-Proof':token}
        self.assertEqual(self.c.post('/api/v1/control',headers=headers,json={'action':'step'}).status_code,403)
        self.assertEqual(self.c.post(target,headers=headers,json={'spot':100,'strike':100,'years':1,'volatility':.2}).status_code,403)
    def test_forged_headers_foreign_site_and_unknown_targets_denied(self):
        self.assertEqual(self.proof('/api/v1/stocks/options',**{'Sec-Fetch-Site':'cross-site'}).status_code,403)
        self.assertEqual(self.proof('/api/v1/stocks/arbitrary').status_code,403)
        self.assertEqual(self.c.post('/api/v1/stocks/options',headers=self.raw,json={}).status_code,403)



class IntradayTests(unittest.IsolatedAsyncioTestCase):
    def test_submicrosecond_order_is_not_silently_truncated(self):
        p=bars();p['bars'][0]['t']='2024-01-02T14:30:00.123456780Z';p['bars'][1]['t']='2024-01-02T14:30:00.123456789Z'
        self.assertEqual(len(prices.bars(p,'AAPL')['bars']),2)
        p['bars'].reverse()
        with self.assertRaises(ValueError):prices.bars(p,'AAPL')
    async def test_intraday_window_and_timeframe_rejected_before_network(self):
        async def fetch(*_):self.fail('invalid parameters must not fetch')
        for frame,end in [('1Min','2024-02-01'),('unknown','2024-01-03')]:
            s=StockWorkspace(environment=ALPACA_ENV,fetcher=fetch)
            with self.assertRaises(AccessError):await s.refresh('AAPL','alpaca',start='2024-01-01',end=end,timeframe=frame)



class StartupRetentionTests(unittest.TestCase):
    def test_first_authored_save_is_not_preempted_by_background_cleanup(self):
        import os,tempfile,threading
        entered=threading.Event();release=threading.Event()
        def cleanup(*args,**kwargs):entered.set();release.wait(5)
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'GIG_TERMINAL_L2_RECORDINGS':directory,'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787'}),patch('terminal.l2_playback.prune_expired',cleanup):
            try:
                with TestClient(create_app(),base_url='http://127.0.0.1:8787') as client:
                    entered.wait(.1)
                    response=client.post('/api/v1/recording',headers={'Origin':'http://127.0.0.1:8787'},json={'action':'save_l2_fixture'})
                    self.assertEqual(response.status_code,200,response.text)
                    self.assertFalse(entered.is_set())
            finally:release.set()

if __name__=='__main__':unittest.main(verbosity=2)
