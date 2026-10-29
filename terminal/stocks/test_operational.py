"""Independent qualification regressions;no real credentials,provider data or network."""
import argparse,asyncio,contextlib,io,json,os,unittest
from types import SimpleNamespace
from unittest.mock import patch,AsyncMock

class OriginalDefects(unittest.IsolatedAsyncioTestCase):
    async def test_stream_qualification_cannot_inherit_disk_capture(self):
        from scripts import qualify_alpaca_live as q
        class ConstructorObserved(Exception):pass
        env={'GIG_ALPACA_STORE_ENABLED':'1','GIG_HISTORY_STORE_ENABLED':'1'}
        def workspace(**kwargs):return SimpleNamespace(environment=kwargs.get('environment',env))
        def live(w,**kwargs):
            self.assertEqual(kwargs.get('retry_budget'),1)
            self.assertEqual(w.environment.get('GIG_ALPACA_STORE_ENABLED'),'0')
            self.assertEqual(w.environment.get('GIG_HISTORY_STORE_ENABLED'),'0')
            raise ConstructorObserved()
        with patch.dict(os.environ,env,clear=True),patch.object(q,'StockWorkspace',side_effect=workspace),patch.object(q,'LiveIEX',side_effect=live):
            with self.assertRaises(ConstructorObserved):await q.qualify(SimpleNamespace(symbol='AAPL',seconds=5))
    async def test_empty_history_cannot_exit_as_successful_observed_qualification(self):
        from scripts import qualify_alpaca_market_history as q
        with patch('sys.argv',['qualify','--execute','--start','2026-10-01','--end','2026-10-02']),patch.object(q,'qualify',AsyncMock(return_value={'record_count':0,'origin':'OBSERVED_OFFICIAL_RESPONSE'})),contextlib.redirect_stdout(io.StringIO()):
            # main owns an event loop;execute it outside this async test loop.
            result=await asyncio.to_thread(q.main)
        self.assertNotEqual(result,0)

from pathlib import Path
import copy,subprocess
from .qualification import nonretaining_environment,history_status,reference_summary,comparison_reference,collect_stream,stage_error,qualify_sources
from .service import StockWorkspace
from .test_repair import ENV
from .test_alpaca_data import asset

ROOT=Path(__file__).resolve().parents[2]
def history(symbol='AAPL',prices=('100','110')):
    from terminal.providers.kraken import timestamp_ns
    records=[{'timestamp':f'2026-10-0{i+1}T00:00:00Z','source_timestamp_ns':timestamp_ns(f'2026-10-0{i+1}T00:00:00Z'),'source_record_sha256':'b'*64,'duplicate_record':False,'open':p,'high':p,'low':p,'close':p,'volume':'1'} for i,p in enumerate(prices)]
    return {'schema':'gig.alpaca.historical.v1','symbol':symbol,'kind':'bars','timeframe':'1Day','provider':'alpaca','feed':'iex','origin':'HISTORICAL_SYNTHETIC','freshness':'HISTORICAL_NOT_LIVE','availability':'AVAILABLE','records':records,'record_count':len(records),'pages':1,'has_more':False,'complete_market_history':False,'received_at':'2026-10-20T00:00:00Z','requested_interval':{'start':'2026-10-01T00:00:00Z','exclusive_end':'2026-10-20T00:00:00Z'},'source_records':[{'url':'https://data.alpaca.markets/v2/stocks/bars','sha256':'a'*64,'page':1,'records':len(records),'received_at':'2026-10-20T00:00:00Z'}]}

class QualificationPrimitives(unittest.TestCase):
    def test_local_restrictions_do_not_mutate_or_grant_permissions(self):
        original={**ENV,'GIG_ALPACA_STORE_ENABLED':'1','GIG_HISTORY_STORE_ENABLED':'1','GIG_ALPACA_ENABLED':'0'};before=original.copy();restricted=nonretaining_environment(original)
        self.assertEqual(original,before);self.assertEqual(restricted['GIG_ALPACA_STORE_ENABLED'],'0');self.assertEqual(restricted['GIG_HISTORY_STORE_ENABLED'],'0');self.assertEqual(restricted['GIG_ALPACA_ENABLED'],'0')
        for k in ('PROTOCOL_REVIEWED','PRIVATE_DISPLAY_APPROVED','CLOUD_PROCESSING_APPROVED','NO_COST_CONFIRMED','PERMISSION_REFERENCE'):self.assertEqual(restricted.get('GIG_ALPACA_'+k),original.get('GIG_ALPACA_'+k))
    def test_empty_and_fixture_history_do_not_qualify_provider(self):
        self.assertEqual(history_status({'origin':'OBSERVED_OFFICIAL_RESPONSE','record_count':0}),'INCONCLUSIVE_EMPTY_SOURCE_RESPONSE')
        self.assertEqual(history_status({'origin':'HISTORICAL_SYNTHETIC','record_count':4}),'FIXTURE_NOT_PROVIDER_QUALIFICATION')
        self.assertTrue(history_status({'origin':'OBSERVED_OFFICIAL_RESPONSE','record_count':1}).startswith('PASS_'))
    def test_reference_requires_acquisition_not_fallback_count(self):
        w=StockWorkspace(environment={});r=reference_summary(w);self.assertEqual(r['accepted_identities'],0);self.assertFalse(r['status'].startswith('PASS_'))
    def test_synthetic_asset_reference_is_never_observed_qualification(self):
        from .alpaca_reference import parse
        w=StockWorkspace(environment=ENV,fetcher=lambda *_:None);w.catalog=parse([('active',[asset()])],'HISTORICAL_SYNTHETIC');w.asset_reference.status='ACCEPTED';r=reference_summary(w)
        self.assertEqual(r['accepted_identities'],1);self.assertEqual(r['observed_identities'],0);self.assertFalse(r['market_data_entitlement_verified']);self.assertFalse(r['status'].startswith('PASS_'))
    def test_comparison_exact_rational_reference(self):
        a,b=history(),history('MSFT',('50','60'));r=comparison_reference([a,b]);self.assertEqual(r['exact_shared_timestamps'],2);self.assertEqual(r['series'][0]['values'][1],{'numerator':'10','denominator':'1'});self.assertEqual(r['series'][1]['values'][1],{'numerator':'20','denominator':'1'})
    def test_comparison_never_fills_missing_timestamps(self):
        a,b=history(),history('MSFT');b['records']=b['records'][:1];r=comparison_reference([a,b]);self.assertEqual(r['exact_shared_timestamps'],1)
    def test_comparison_rejects_duplicate_scope_and_zero_baseline(self):
        for mutate in (lambda b:b.update(symbol='AAPL'),lambda b:b.update(timeframe='1Min'),lambda b:b['records'].append(b['records'][0]),lambda b:b['records'][0].update(close='0')):
            a,b=history(),history('MSFT');mutate(b)
            with self.assertRaises(ValueError):comparison_reference([a,b])
    def run_node(self,histories,expected):
        r=subprocess.run(['node','--experimental-strip-types',str(ROOT/'scripts/check_actual_comparison.mjs')],input=json.dumps({'histories':histories,'expected':expected}),text=True,capture_output=True,timeout=10)
        return r.returncode,json.loads(r.stdout)
    def test_actual_frontend_agrees_with_independent_fraction_reference(self):
        hs=[history(),history('MSFT',('50','60'))];code,r=self.run_node(hs,comparison_reference(hs));self.assertEqual(code,0);self.assertEqual(r['status'],'PASS');self.assertEqual(r['origin'],'FIXTURE_NOT_PROVIDER_QUALIFICATION');self.assertFalse({'records','prices','close','credentials'}&set(r))
    def test_frontend_negative_control_rejects_corrupt_reference(self):
        hs=[history(),history('MSFT')];expected=comparison_reference(hs);expected['series'][0]['values'][1]['numerator']='999';code,r=self.run_node(hs,expected);self.assertEqual(code,1);self.assertEqual(r['status'],'REJECTED')
    def test_frontend_negative_control_rejects_corrupt_source_clock(self):
        hs=[history(),history('MSFT')];expected=comparison_reference(hs);hs[0]['records'][0]['source_timestamp_ns']='1';self.assertEqual(self.run_node(hs,expected)[0],1)
    def test_errors_do_not_disclose_source_or_credentials(self):
        self.assertNotIn('AUTHORED_SECRET',json.dumps(stage_error(ValueError('AUTHORED_SECRET'))))
    def test_preflight_has_no_provider_request_or_permission_activation(self):
        from scripts.qualify_atlas import preflight
        with patch('socket.create_connection',side_effect=OSError):r=preflight(StockWorkspace(environment={}))
        self.assertEqual(r['network_provider_requests'],0);self.assertFalse(r['authorization_flags_changed']);self.assertFalse(r['gateway_port_8787_in_use'])
    def test_execute_refuses_active_gateway_without_source_calls(self):
        from scripts import qualify_atlas as q
        with patch('sys.argv',['qualify','--execute']),patch.object(q,'preflight',return_value={'gateway_port_8787_in_use':True}),patch.object(q,'qualify_sources',side_effect=AssertionError('must not execute')),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(q.main(),2)

class StreamAndStages(unittest.IsolatedAsyncioTestCase):
    async def test_one_shot_stream_stops_on_first_open_failure(self):
        from .live import LiveIEX
        calls=[]
        class Socket:
            async def __aenter__(self):calls.append(1);raise OSError('authored disconnect')
            async def __aexit__(self,*_):pass
        w=StockWorkspace(environment={**ENV,'GIG_ALPACA_LIVE_ENABLED':'1'},fetcher=lambda *_:None)
        s=LiveIEX(w,connector=lambda *_a,**_k:Socket(),retry_budget=1)
        try:
            await s.start(['AAPL']);await asyncio.wait_for(s.task,1);self.assertEqual(calls,[1]);self.assertEqual(s.state,'FAILED');self.assertEqual(s.reason,'retry_budget_exhausted')
        finally:await s.close()
    async def test_retry_budget_invalid_values_reject(self):
        from .live import LiveIEX
        for n in (0,6,True,'1'):
            with self.assertRaises(ValueError):LiveIEX(StockWorkspace(environment={}),retry_budget=n)
    async def test_default_stream_retry_contract_preserved(self):
        from .live import LiveIEX
        self.assertEqual(LiveIEX(StockWorkspace(environment={})).retry_budget,5)
    async def test_stream_finally_closes_on_rejection(self):
        class Stream:
            clock=lambda s:0
            closed=False
            async def start(self,_):raise ValueError('authored failure')
            async def close(self):self.closed=True
        s=Stream()
        with self.assertRaises(ValueError):await collect_stream(s,['AAPL'],5)
        self.assertTrue(s.closed)
    async def test_invalid_stream_duration_cannot_start(self):
        with self.assertRaises(ValueError):await collect_stream(None,['AAPL'],61)
    async def test_missing_permissions_make_no_source_requests(self):
        async def denied(*_):self.fail('no source request permitted')
        w=StockWorkspace(environment={},fetcher=denied);r=await qualify_sources(w,end='2026-10-28')
        self.assertFalse(r['observed_provider_qualification']);self.assertEqual(r['stages']['live']['new_connections'],0);self.assertEqual(r['stages']['sec_sources']['status'],'BLOCKED_CONFIGURATION');self.assertEqual(r['identity_coverage']['count_status'],'UNQUALIFIED_PROCESS_IDENTITY_COUNT');self.assertEqual(r['identity_coverage']['accepted_provider_assets'],0)
    async def test_sec_can_run_independently_with_market_data_blocked(self):
        from .test_workspace import SEC_ENV,submissions,facts
        facts_raw=json.dumps(facts()).encode()
        async def fetch(url,*_):
            if 'company_tickers' in url:return json.dumps({'0':{'cik_str':320193,'ticker':'AAPL','title':'Authored Apple'},'1':{'cik_str':42,'ticker':'APLD','title':'FICTIONAL CIK42'},'2':{'cik_str':43,'ticker':'CRWV','title':'FICTIONAL CIK43'}}).encode()
            return json.dumps(submissions()).encode() if '/submissions/' in url else facts_raw
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch)
        with patch('scripts.qualify_sec_sources.official_fetch',return_value=(facts_raw,'https://data.sec.gov/fixture-not-executed')):
            r=await qualify_sources(w,end='2026-10-28')
        self.assertEqual(r['stages']['sec_financials']['mismatch_count'],0);self.assertEqual(r['stages']['sec_identity']['status'],'FIXTURE_NOT_PROVIDER_QUALIFICATION');self.assertEqual(r['stages']['alpaca_reads']['status'],'BLOCKED_CONFIGURATION_OR_PERMISSION');self.assertFalse(r['observed_provider_qualification'])
    async def test_cancelled_campaign_closes_workspace(self):
        w=StockWorkspace(environment=ENV,fetcher=lambda *_:None);w.close=AsyncMock()
        async def wait():await asyncio.Event().wait()
        w.asset_reference.refresh=wait
        with self.assertRaises(TimeoutError):await asyncio.wait_for(qualify_sources(w,end='2026-10-28'),.02)
        w.close.assert_awaited_once()

class StandaloneStreamAdmission(unittest.TestCase):
    def test_standalone_requires_explicit_account_window_without_connection(self):
        from scripts import qualify_alpaca_live as q
        with patch('sys.argv',['live','--execute']),patch.object(q,'qualify',side_effect=AssertionError('no source')),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit)as e:q.main()
        self.assertEqual(e.exception.code,2)
    def test_standalone_refuses_existing_gateway(self):
        from scripts import qualify_alpaca_live as q
        with patch('sys.argv',['live','--execute','--exclusive-stream-window']),patch('socket.create_connection')as connection,patch.object(q,'qualify',side_effect=AssertionError('no source')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(q.main(),2)
    def test_browser_cohort_summary_accepts_exact_legacy_and_json_formats(self):
        from scripts.qualify_atlas_offline import summary
        self.assertEqual(summary('PASS ratio-history browser 14')['passed'],14)
        self.assertEqual(summary('PASS landscape checks=5')['passed'],5)
        self.assertEqual(summary('PASS 3/3 AAPL,APLD,CRWV browser discovery')['passed'],3)
        with self.assertRaises(ValueError):summary('PASS 2/3 incomplete')
        self.assertEqual(summary('prefix\n{"summary":{"passed":21,"failed":0}}')['passed'],21)
        self.assertEqual(summary('{"passed":1,"failed":1}')['failed'],1)
        with self.assertRaises(ValueError):summary('no completed result')

class FinalQualificationBoundaries(unittest.IsolatedAsyncioTestCase):
    async def test_live_contract_interpreter_and_cleanup_without_actual_provider(self):
        # Authored literals exercise the observed-wire branch;this is NOT provider evidence.
        class AuthoredContract:
            failures=0;state='SUBSCRIBED';store=None;t=0;closed=False
            def clock(self):self.t+=1;return self.t
            async def start(self,_):pass
            async def close(self):self.closed=True
            def view(self):return {'phase':'SUBSCRIBED','state':'SUBSCRIBED','observations':[{'symbol':'AAPL','kind':k,'state':'LIVE','origin':'OBSERVED_OFFICIAL_RESPONSE','source_sha256':'a'*64,'source_timestamp_ns':'1000000000','receive_age_seconds':.1}for k in ('quote','trade')],'accepted_observations':2,'connection_count':1,'out_of_order_observations':0,'reason':None}
        s=AuthoredContract();r=await collect_stream(s,['AAPL'],5);self.assertTrue(r['status'].startswith('PASS_'));self.assertTrue(s.closed);self.assertEqual(r['source_timestamp_ns_range'],['1000000000','1000000000']);self.assertFalse(r['storage_enabled'])
    async def test_synthetic_stream_cannot_pass_observed_interpreter(self):
        class AuthoredContract:
            failures=0;state='SUBSCRIBED';store=None;t=0
            def clock(self):self.t+=1;return self.t
            async def start(self,_):pass
            async def close(self):pass
            def view(self):return {'phase':'SUBSCRIBED','state':'SUBSCRIBED','observations':[{'symbol':'AAPL','kind':k,'state':'SIMULATED','origin':'HISTORICAL_SYNTHETIC'}for k in ('quote','trade')],'accepted_observations':2,'connection_count':1,'out_of_order_observations':0,'reason':None}
        self.assertFalse((await collect_stream(AuthoredContract(),['AAPL'],5))['status'].startswith('PASS_'))
    async def test_missing_official_AAPL_mapping_cannot_fall_back_to_curated_identity(self):
        from .test_workspace import SEC_ENV
        calls=[]
        async def fetch(url,*_):
            calls.append(url);return json.dumps({'0':{'cik_str':42,'ticker':'APLD','title':'FICTIONAL CIK42'}}).encode()
        w=StockWorkspace(environment=SEC_ENV,fetcher=fetch);r=await qualify_sources(w,end='2026-10-28');self.assertEqual(len(calls),1);self.assertEqual(r['stages']['sec_sources']['status'],'BLOCKED_OR_REJECTED');self.assertFalse(r['observed_provider_qualification'])
    async def test_mixed_origin_comparison_and_invalid_counts_are_rejected(self):
        a,b=history(),history('MSFT');b['origin']='OBSERVED_OFFICIAL_RESPONSE'
        with self.assertRaises(ValueError):comparison_reference([a,b])
        for value in (-1,257,True,'1'):self.assertEqual(history_status({'origin':'OBSERVED_OFFICIAL_RESPONSE','record_count':value}),'REJECTED_HISTORICAL_COUNT')

class ChildProcessBoundary(unittest.IsolatedAsyncioTestCase):
    async def test_comparison_process_receives_no_provider_credentials(self):
        from scripts.qualify_atlas import frontend_comparison
        process=SimpleNamespace(returncode=0,communicate=AsyncMock(return_value=(b'{"status":"PASS"}',b'')))
        with patch.dict(os.environ,{'ALPACA_API_SECRET_KEY':'AUTHORED_SECRET_NOT_REAL','GIG_SEC_USER_AGENT':'AUTHORED_CONTACT_NOT_REAL'}),patch('asyncio.create_subprocess_exec',AsyncMock(return_value=process))as launch:
            self.assertEqual((await frontend_comparison([],{}))['status'],'PASS')
        self.assertEqual(set(launch.call_args.kwargs['env']),{'PATH','LANG'})
        self.assertNotIn('AUTHORED_SECRET_NOT_REAL',json.dumps(launch.call_args.kwargs['env']))

class ReconciliationDeadline(unittest.TestCase):
    def test_official_SEC_reconciliation_has_a_total_body_deadline(self):
        from scripts.qualify_sec_sources import official_fetch
        from .test_workspace import SEC_ENV
        from unittest.mock import MagicMock
        response=MagicMock(status_code=200,headers={});response.iter_raw.return_value=iter([b'{}'])
        client=MagicMock();client.__enter__.return_value=client;client.stream.return_value.__enter__.return_value=response
        with patch('httpx.Client',return_value=client),patch('scripts.qualify_sec_sources.time.monotonic',side_effect=[0,30]):
            with self.assertRaisesRegex(ValueError,'SEC_total_deadline'):official_fetch('0000320193',SEC_ENV)
