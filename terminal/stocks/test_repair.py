"""Repair regressions and independently authored provider responses,no actual observations."""
import asyncio,copy,json,unittest
from decimal import Decimal
from fractions import Fraction
from unittest.mock import patch
from starlette.testclient import TestClient
from .auth import credentials
from .service import StockWorkspace,AccessError
from .option_feed import snapshots
from .quote_analytics import analyze
from .test_workspace import SEC_ENV,ALPACA_ENV,submissions,facts,bars
from terminal.server.app import create_app

ENV={**SEC_ENV,**{k:v for k,v in ALPACA_ENV.items() if not k.startswith('APCA_')},'ALPACA_API_KEY_ID':'authored_key','ALPACA_API_SECRET_KEY':'authored_secret',**{'GIG_ALPACA_OPTIONS_'+k:'1' for k in ('ENABLED','PROTOCOL_REVIEWED','INDICATIVE_APPROVED')}}
def option_data(ticker='AAPL',price='100'):
    return {'snapshots':{ticker+'261120C00100000':{'latestQuote':{'t':'2026-10-25T12:00:00Z','bp':Decimal('2.50'),'ap':Decimal('2.75'),'bs':1,'as':2},'impliedVolatility':Decimal('.25'),'greeks':{'delta':Decimal('.55'),'theta':Decimal('-.02')}}},'next_page_token':None}

def authored_fetcher(url,headers,cap):
    async def run():
        ticker='NVDA' if '/NVDA' in url or '0001045810' in url else 'AAPL';cik=1045810 if ticker=='NVDA' else 320193
        if '/submissions/' in url:p=submissions();p['cik']=cik
        elif '/companyfacts/' in url:p=facts();p['cik']=cik
        elif '/options/' in url:p=option_data(ticker)
        elif '/bars?' in url:
            from urllib.parse import urlsplit,parse_qs
            import datetime
            p=bars();p['symbol']=ticker;start=datetime.date.fromisoformat(parse_qs(urlsplit(url).query)['start'][0][:10])
            for i,row in enumerate(p['bars']):row['t']=str(start+datetime.timedelta(days=i+1))+'T14:30:00Z'
        elif '/quotes/' in url:p={'symbol':ticker,'quote':{'t':'2026-10-25T12:00:00Z','bp':200 if ticker=='NVDA' else 100,'ap':201 if ticker=='NVDA' else 101,'bs':3,'as':1}}
        else:p={'symbol':ticker,'trade':{'t':'2026-10-25T12:00:00Z','p':200 if ticker=='NVDA' else 100,'s':1}}
        return json.dumps(p,default=str).encode()
    return run()

class Authentication(unittest.TestCase):
    def test_existing_alpaca_names_and_legacy_aliases(self):
        self.assertEqual(credentials(ENV),credentials(ALPACA_ENV));self.assertEqual(credentials({**ENV,'ALPACA_PAPER_BASE_URL':'https://paper-api.alpaca.markets'}),credentials(ENV))
    def test_partial_conflicting_or_invalid_pairs_reject(self):
        for change in ({'ALPACA_API_SECRET_KEY':''},{'APCA_API_KEY_ID':'different_key','APCA_API_SECRET_KEY':'different_secret'},{'ALPACA_API_KEY_ID':'newline\nkey'}):
            with self.assertRaises(ValueError):credentials({**ENV,**change})
    def test_safe_status_and_no_paper_endpoint(self):
        s=StockWorkspace(environment=ENV,fetcher=authored_fetcher);out=s.view('AAPL');self.assertTrue(out['configuration']['alpaca']['ready']);self.assertNotIn('authored_secret',json.dumps(out));self.assertFalse(out['configuration']['alpaca_credential_presence']['paper_base_url_used_for_market_data'])
    def test_options_separate_gate_no_opra_fallback(self):
        s=StockWorkspace(environment=ALPACA_ENV,fetcher=authored_fetcher)
        with self.assertRaisesRegex(AccessError,'indicative'):s.permission('options')
        self.assertFalse(s.view('AAPL')['capabilities']['options_quotes'])

class OptionFeed(unittest.TestCase):
    def test_identity_model_values_and_indicative_scope(self):
        x=snapshots(option_data(),'AAPL');r=x['contracts'][0];self.assertEqual(r['right'],'call');self.assertEqual(r['expiration'],'2026-11-20');self.assertEqual(r['provider_greeks']['theta'],'-0.02');self.assertEqual(r['provider_implied_volatility'],'0.25');self.assertFalse(x['complete_chain']);self.assertIsNone(x['delay_seconds'])
    def test_wrong_underlying_malformed_code_and_budget(self):
        for p in (option_data('NVDA'),{'snapshots':{'invalid':{}}},{'snapshots':[]},{'snapshots':{str(i):{} for i in range(101)}}):
            with self.assertRaises(ValueError):snapshots(p,'AAPL')
    def test_missing_greeks_quotes_and_interest_not_invented(self):
        out=snapshots({'snapshots':{'AAPL261120P00100000':{}}},'AAPL');r=out['contracts'][0];self.assertIsNone(r['quote']);self.assertIsNone(r['provider_implied_volatility']);self.assertEqual(r['provider_greeks'],{});self.assertFalse(out['open_interest_available'])
    def test_invalid_numeric_and_timestamp_reject(self):
        for value in (True,Decimal('NaN'),Decimal('1e-999999')):
            p=option_data();next(iter(p['snapshots'].values()))['greeks']['delta']=value
            with self.assertRaises(ValueError):snapshots(p,'AAPL')

class NativeQuote(unittest.TestCase):
    def test_independent_spread_midpoint_microprice_and_units(self):
        q={'bid':'100','ask':'101','bid_size':'3','ask_size':'1'};x=analyze(q);self.assertEqual(x['engine'],'native_C++20_AggregateDepth')
        for key,expected in [('spread',Fraction(1)),('midpoint',Fraction(201,2)),('microprice',Fraction(403,4)),('depth_imbalance',Fraction(1,2))]:
            v=x['metrics'][key];self.assertEqual(Fraction(int(v['numerator']),int(v['denominator'])),expected)
    def test_unrepresentable_and_missing_liquidity_are_explicit(self):
        for q in ({'bid':'100','ask':'101','bid_size':'0','ask_size':'1'},{'bid':'100.000000001','ask':'101','bid_size':'1','ask_size':'1'}):self.assertEqual(analyze(q)['status'],'UNAVAILABLE')
    def test_crossed_and_locked_not_faked_into_normal_spread(self):
        for bid,ask,key in [('101','100','crossed'),('100','100','locked')]:self.assertTrue(analyze({'bid':bid,'ask':ask,'bid_size':'1','ask_size':'1'})[key])

class Loading(unittest.IsolatedAsyncioTestCase):
    def workspace(self,fetcher=authored_fetcher):return StockWorkspace(environment=ENV,fetcher=fetcher,clock=lambda:100)
    async def fast(self,s,operation):
        async def sleep(_):s.last_request=-100;await original(0)
        original=asyncio.sleep
        with patch('terminal.stocks.service.asyncio.sleep',sleep):return await operation()
    async def test_select_load_fetches_sec_prices_options_and_native(self):
        s=self.workspace()
        async def run():await s.start_load('AAPL');await s.load_task
        await self.fast(s,run);v=s.view('AAPL');self.assertEqual(v['load']['status'],'FINISHED');self.assertEqual(v['classification'],'HISTORICAL_SYNTHETIC');self.assertEqual(v['prices']['native_analytics']['status'],'AVAILABLE');self.assertEqual(len(v['options_market']['contracts']),1);self.assertEqual(v['fundamentals']['status'],'AVAILABLE')
    async def test_quote_failure_does_not_hide_good_bars_or_trade(self):
        async def fetch(url,*args):
            if '/quotes/' in url:raise AccessError('upstream_http_403')
            return await authored_fetcher(url,*args)
        s=self.workspace(fetch)
        await self.fast(s,lambda:s.refresh('AAPL','alpaca',start='2024-01-01',end='2024-01-05'))
        v=s.view('AAPL')['prices'];self.assertEqual(v['status'],'PARTIAL');self.assertEqual(len(v['bars']),2);self.assertIn('trades',v);self.assertNotIn('quotes',v);self.assertEqual(v['components']['quotes']['reason'],'upstream_http_403')
    async def test_sec_failure_does_not_block_other_host(self):
        async def fetch(url,*args):
            if 'data.sec.gov' in url:raise AccessError('upstream_http_403')
            return await authored_fetcher(url,*args)
        s=self.workspace(fetch)
        async def run():await s.start_load('AAPL');await s.load_task
        await self.fast(s,run);v=s.view('AAPL');self.assertEqual(v['fundamentals']['status'],'UNAVAILABLE');self.assertEqual(v['prices']['status'],'AVAILABLE');self.assertEqual(v['options_market']['status'],'AVAILABLE')
    async def test_symbol_switch_cancels_pending_job_and_never_mixes_identity(self):
        started=asyncio.Event()
        async def fetch(url,*args):
            if '0000320193' in url:started.set();await asyncio.Event().wait()
            return await authored_fetcher(url,*args)
        s=self.workspace(fetch)
        async def run():
            await s.start_load('AAPL');await started.wait();await s.start_load('NVDA');await s.load_task
        await self.fast(s,run);self.assertEqual(s.view('NVDA')['prices']['quotes']['bid'],'200');self.assertNotIn('quotes',s.view('AAPL')['prices'])
    async def test_no_permission_never_calls_fetch_and_explains_next_action(self):
        async def fetch(*_):self.fail('blocked must not connect')
        s=StockWorkspace(environment={},fetcher=fetch);await s.start_load('AAPL');await s.load_task;v=s.view('AAPL');self.assertFalse(v['configuration']['alpaca']['ready']);self.assertIn('ALPACA_API_KEY_ID',v['configuration']['alpaca']['missing_configuration']);self.assertIn('Codespaces',v['configuration']['alpaca']['action'])
    async def test_indicative_fixed_endpoint_and_no_paid_feed(self):
        seen=[]
        async def fetch(url,*args):seen.append(url);return await authored_fetcher(url,*args)
        s=self.workspace(fetch);await s.refresh('AAPL','options');self.assertEqual(seen,['https://data.alpaca.markets/v1beta1/options/snapshots/AAPL?feed=indicative&limit=100']);self.assertNotIn('opra',seen[0])

class LoadSecurity(unittest.TestCase):
    def test_load_target_requires_origin_and_disallows_urls_or_keys(self):
        with TestClient(create_app(),base_url='http://127.0.0.1:8787') as c:
            self.assertEqual(c.post('/api/v1/stocks/load',json={'symbol':'AAPL'}).status_code,403)
            self.assertEqual(c.post('/api/v1/stocks/load',headers={'Origin':'http://127.0.0.1:8787'},json={'symbol':'AAPL','url':'https://attacker.invalid'}).status_code,400)
        with TestClient(create_app(stock_workspace=StockWorkspace(environment=ENV)),base_url='http://127.0.0.1:8787') as c:self.assertFalse(c.get('/api/v1/health').json()['fixture_tests_safe'])
    def test_load_registered_as_exact_proof_target(self):
        from terminal.server.request_proofs import TARGETS
        self.assertIn('/api/v1/stocks/load',TARGETS);self.assertNotIn('/api/v1/stocks/*',TARGETS)


class LoadProof(unittest.TestCase):
    def test_codespaces_exact_rewrite_can_load_but_cannot_reuse_proof(self):
        import os
        origin='https://authored-load-8787.app.github.dev';raw={'Origin':'http://localhost:8787','Host':'localhost:8787','X-Forwarded-Host':'authored-load-8787.app.github.dev','X-Forwarded-Proto':'https'}
        with patch.dict(os.environ,{'CODESPACES':'true','CODESPACE_NAME':'authored-load','GIG_TERMINAL_ALLOWED_ORIGINS':origin}),TestClient(create_app(stock_workspace=StockWorkspace(environment={},fetcher=authored_fetcher)),base_url='http://localhost:8787') as c:
            read=c.get('/api/v1/request-proof',headers={**raw,'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':origin,'X-GIG-Target':'/api/v1/stocks/load','Sec-Fetch-Site':'same-origin'});self.assertEqual(read.status_code,200)
            headers={**raw,'X-GIG-Request-Proof':read.json()['proof']}
            self.assertEqual(c.post('/api/v1/stocks/load',headers=headers,json={'symbol':'AAPL'}).status_code,200);self.assertEqual(c.post('/api/v1/stocks/load',headers=headers,json={'symbol':'AAPL'}).status_code,403)
    def test_credential_configuration_never_uses_paper_or_arbitrary_host(self):
        e={**ENV,'ALPACA_PAPER_BASE_URL':'https://attacker.invalid/?token=private'};s=StockWorkspace(environment=e,fetcher=authored_fetcher)
        self.assertNotIn('attacker.invalid',json.dumps(s.view('AAPL')));self.assertNotIn('private',json.dumps(s.configuration()['alpaca_credential_presence']))
    def test_native_price_exactness_not_rounded_into_ticks(self):
        self.assertEqual(analyze({'bid':'100.000000000001','ask':'101','bid_size':'3','ask_size':'1'})['status'],'UNAVAILABLE')



class PriceReferences(unittest.TestCase):
    def test_exact_return_drawdown_and_insufficient_risk_sample(self):
        from .price_research import describe
        rows=[{'close':str(p),'timestamp':str(i)} for i,p in enumerate([100,80,120,60])];r=describe(rows)
        self.assertEqual(r['maximum_close_drawdown']['value'],{'numerator':'1','denominator':'2'});self.assertIsNone(r['historical_var_95']['value'])
    def test_sorted_empirical_tail_independent_reference(self):
        from .price_research import describe
        r=describe([{'close':str(100+i),'timestamp':str(i)} for i in range(21)]);self.assertEqual(r['historical_var_95']['value'],{'numerator':'-1','denominator':'119'});self.assertEqual(r['total_return']['value'],{'numerator':'1','denominator':'5'})
    def test_record_budget(self):
        from .price_research import describe
        with self.assertRaises(ValueError):describe([{'close':'100','timestamp':'authored'}]*257)



class ConfigurationDiagnostic(unittest.TestCase):
    def test_diagnostic_is_no_network_and_credential_free(self):
        import importlib.util
        from pathlib import Path
        spec=importlib.util.spec_from_file_location('config_diag',Path(__file__).resolve().parents[2]/'scripts/check_stock_configuration.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        r=m.report(ENV);self.assertEqual(r['network_requests'],0);self.assertNotIn('authored_secret',json.dumps(r));self.assertNotIn('authored_key',json.dumps(r))
    def test_transport_failure_categories_do_not_copy_exception_strings(self):
        import httpx
        from .service import failure_reason
        for exc,expected in [(httpx.ProxyError('secret'),'upstream_proxy_connection_failure'),(httpx.ReadTimeout('secret'),'upstream_timeout'),(httpx.ConnectError('secret'),'upstream_connect_or_TLS_failure')]:self.assertEqual(failure_reason(exc,'fallback'),expected)



class SECPartialValidation(unittest.IsolatedAsyncioTestCase):
    async def exercise(self,failed):
        async def fetch(url,*args):
            if failed in url:raise AccessError('upstream_http_403')
            return await authored_fetcher(url,*args)
        s=StockWorkspace(environment=ENV,fetcher=fetch,clock=lambda:100)
        original=asyncio.sleep
        async def sleep(_):s.last_request=-100;await original(0)
        with patch('terminal.stocks.service.asyncio.sleep',sleep):await s.refresh('AAPL','sec')
        return s.view('AAPL')['fundamentals']
    async def test_good_filings_survive_unavailable_companyfacts(self):
        r=await self.exercise('companyfacts');self.assertEqual(r['status'],'PARTIAL');self.assertTrue(r['filings']);self.assertNotIn('financials',r)
    async def test_good_companyfacts_survive_unavailable_submissions(self):
        r=await self.exercise('submissions');self.assertEqual(r['status'],'PARTIAL');self.assertTrue(r['financials']['history']['revenue']);self.assertNotIn('filings',r)

if __name__=='__main__':unittest.main(verbosity=2)
