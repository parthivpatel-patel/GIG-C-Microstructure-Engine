"""Independent authored Phase5 data/recovery fixtures;no external data acquisition."""
import asyncio,copy,json,tempfile,unittest,sqlite3
from pathlib import Path
from unittest.mock import patch
from .history_store import HistoryStore
from .history import normalize
from .test_phase3 import bar,pages,source
from .test_repair import ENV
from .service import StockWorkspace

class Historical(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.store=HistoryStore(Path(self.temp.name)/'private')
    def test_multipage_core_stays_versioned_and_old_single_page_compatible(self):
        p=pages([bar('2024-01-02T14:30:00Z')]);p+=pages([bar('2024-01-03T14:30:00Z')]);p[1]['sha256']='b'*64
        core=normalize('AAPL','1Day',p,source());r=self.store.save(core);loaded=self.store.read(r['revision']);self.assertEqual(core,loaded);self.assertEqual(loaded['page_count'],2)
        single=normalize('NVDA','1Min',pages([bar()]),source());self.assertEqual(single,self.store.read(self.store.save(single)['revision']))
    def test_bounded_pagination_and_pinned_data_not_current_cache(self):
        calls=[]
        async def fetch(url,headers,cap):
            calls.append(url);i=len(calls);return json.dumps({'symbol':'AAPL','bars':[{'t':f'2024-01-0{i+1}T14:30:00Z','o':100,'h':101,'l':99,'c':100,'v':1}],'next_page_token':'opaque+cursor==' if i==1 else None}).encode()
        w=StockWorkspace(environment=ENV,fetcher=fetch,history_store=self.store)
        from .acquisition import ingest
        result=asyncio.run(ingest(w,'AAPL','2024-01-01','2024-01-10'));self.assertEqual(result['pages'],2);self.assertFalse(result['has_more']);self.assertNotIn('AAPL',w.cache)
        self.assertIn('page_token=opaque%2Bcursor%3D%3D',calls[1]);self.assertEqual(self.store.read(result['revision'])['state'],'SIMULATED')
    def test_later_page_rejection_publishes_nothing(self):
        async def fetch(url,headers,cap):
            return json.dumps({'symbol':'AAPL','bars':[{'t':'2024-01-02T14:30:00Z','o':100,'h':101,'l':99,'c':100,'v':1}],'next_page_token':'loop'}).encode()
        w=StockWorkspace(environment=ENV,fetcher=fetch,history_store=self.store)
        from .acquisition import ingest
        with self.assertRaises(ValueError):asyncio.run(ingest(w,'AAPL','2024-01-01','2024-01-10'))
        self.assertEqual(self.store.list(),[])
    def test_disabled_provider_rejects_before_fetch(self):
        from .acquisition import ingest
        async def forbidden(*args):self.fail('network attempted')
        w=StockWorkspace(environment={},fetcher=forbidden,history_store=self.store)
        with self.assertRaises(ValueError):asyncio.run(ingest(w,'AAPL','2024-01-01','2024-01-10'))
    def test_backup_restore_restart_and_corrupt_backup_atomicity(self):
        from .history_backup import backup,restore,delete_backup
        core=normalize('AAPL','1Min',pages([bar()]),source());revision=self.store.save(core)['revision'];record=backup(self.store);self.assertEqual(record['revisions'],1)
        with self.assertRaises(ValueError):backup(self.store)
        self.store.delete(revision);self.assertEqual(self.store.list(),[]);self.assertEqual(restore(self.store)['restored_revisions'],1)
        self.assertEqual(HistoryStore(self.store.path.parent).read(revision),core)
        file=self.store.path.parent/'history.backup.sqlite3';file.write_bytes(b'bad')
        with self.assertRaises(ValueError):restore(self.store)
        self.assertEqual(self.store.read(revision),core);delete_backup(self.store)
    def test_restore_fault_before_publication_preserves_database(self):
        from .history_backup import backup,restore
        core=normalize('AAPL','1Min',pages([bar()]),source());revision=self.store.save(core)['revision'];backup(self.store)
        with patch('terminal.stocks.history_backup._copy',side_effect=OSError('authored fault')):
            with self.assertRaises(OSError):restore(self.store)
        self.assertEqual(self.store.read(revision),core)

class PortfolioAndEvaluation(unittest.TestCase):
    def test_independent_covariance_risk_and_shocks(self):
        import math
        from fractions import Fraction
        from .portfolio import analyze
        a=['0.01','-0.02']*10;b=['-0.01','0.02']*10
        x=analyze({'assets':{'ASSET_A':a,'ASSET_B':b},'weights':{'ASSET_A':'0.5','ASSET_B':'0.5'},'shocks':[{'ASSET_A':'-0.1','ASSET_B':'0.2'}]})
        value=lambda f:Fraction(int(f['numerator']),int(f['denominator']))
        self.assertTrue(all(value(v)==0 for v in x['portfolio_returns']));self.assertEqual(x['gaussian_var'],0);self.assertEqual(x['gaussian_es'],0)
        self.assertAlmostEqual(x['correlation_approximate'][0][1],-1)
        self.assertEqual(value(x['scenarios'][0]['weighted_return']),Fraction(1,20))
        mean=sum(map(Fraction,a))/20;var=sum((Fraction(v)-mean)**2 for v in a)/19
        self.assertEqual(value(x['sample_covariance'][0][0]),var);self.assertEqual(value(x['sample_covariance'][0][1]),-var)
    def test_missing_alignment_zero_variance_and_weights(self):
        from .portfolio import analyze
        x={'assets':{'ASSET_A':['0.01']*20},'weights':{'ASSET_A':'1'}};self.assertIsNone(analyze(x)['correlation_approximate'][0][0])
        for patch_value in [{'weights':{'ASSET_A':'0.5'}},{'assets':{'ASSET_A':['NaN']*20}},{'assets':{'ASSET_A':['0.01']*20,'ASSET_B':['0.02']*21},'weights':{'ASSET_A':'0.5','ASSET_B':'0.5'}}]:
            with self.assertRaises(ValueError):analyze({**x,**patch_value})
    def test_heldout_mutation_cannot_change_training_or_validation(self):
        from .evaluation import evaluate
        x=['0.001','-0.002','0.003','-0.004']*15;a=evaluate(x,30,45);y=x[:45]+['0.02','-0.03','0.01']*5;b=evaluate(y,30,45)
        self.assertEqual(a['parameters'],b['parameters']);self.assertEqual(a['training_sha256'],b['training_sha256']);self.assertEqual(a['validation_log_likelihood'],b['validation_log_likelihood']);self.assertNotEqual(a['dataset_sha256'],b['dataset_sha256'])
        with self.assertRaises(ValueError):evaluate(x,50,40)
    def test_accounting_missingness_and_exact_residual(self):
        from .accounting import checks
        from .test_backend import FinancialMetrics
        n=FinancialMetrics().normalized();x=checks(n);self.assertEqual(x['checks']['balance'][0]['status'],'SELECTED_COMPONENT_RESIDUAL');self.assertIsNone(x['checks']['cash_change'][0]['residual'])
        n['history']['liabilities']=[{**n['history']['assets'][0],'concept':'Liabilities','value':'600'}];n['history']['equity'][0]['value']='400';self.assertEqual(checks(n)['checks']['balance'][0]['status'],'SELECTED_COMPONENTS_EQUAL')
        from .test_workspace import facts as raw_facts,fact,CIK
        from .sec import facts
        p=raw_facts();g=p['facts']['us-gaap']
        for tag,value,instant in [('StockholdersEquity',750,True),('GrossProfit',60,False),('CostOfRevenue',40,False),('NetCashProvidedByUsedInOperatingActivities',30,False),('NetCashProvidedByUsedInInvestingActivities',-10,False),('NetCashProvidedByUsedInFinancingActivities',-5,False),('EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents',2,False),('CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',17,False)]:
            g[tag]={'units':{'USD':[fact(value,None) if instant else fact(value)]}}
        verified=checks(facts(p,CIK,'2024-12-31'))
        for name in ('balance','gross_profit','cash_change'):self.assertEqual(verified['checks'][name][0]['status'],'SELECTED_COMPONENTS_EQUAL')

    def test_new_taxonomy_preserves_share_units(self):
        from .sec import facts
        from .test_workspace import facts as fixture,fact,CIK
        p=fixture();p['facts']['us-gaap']['WeightedAverageNumberOfDilutedSharesOutstanding']={'units':{'shares':[fact(20)]}};n=facts(p,CIK,'2024-12-31');self.assertEqual(n['history']['diluted_shares'][0]['unit'],'shares')

class StorageFailure(unittest.TestCase):
    def test_completed_copy_is_not_reported_failed_by_late_deadline(self):
        from .history_backup import _copy
        class Completed:
            def backup(self,target,**kwargs):kwargs['progress'](101,0,2)
        with patch('terminal.stocks.history_backup.time.monotonic',side_effect=[0,10]):_copy(Completed(),None)
        class Busy:
            def backup(self,target,**kwargs):kwargs['progress'](sqlite3.SQLITE_BUSY,0,0)
        with patch('terminal.stocks.history_backup.time.monotonic',side_effect=[0,10]):
            with self.assertRaises(ValueError):_copy(Busy(),None)

    def test_sqlite_partial_restore_copy_rolls_back_destination(self):
        from . import history_backup as module
        with tempfile.TemporaryDirectory() as root:
            s=HistoryStore(root);a=normalize('AAPL','1Min',pages([bar()]),source());old=s.save(a)['revision'];module.backup(s);s.delete(old)
            b=normalize('AAPL','1Min',pages([bar(close='101')]),source());current=s.save(b)['revision'];original=module._copy;calls=[0]
            def fault(src,dst):
                calls[0]+=1
                if calls[0]==1:return original(src,dst)
                def progress(status,left,total):
                    if left:raise OSError('authored partial-copy failure')
                src.backup(dst,pages=1,progress=progress)
            with patch('terminal.stocks.history_backup._copy',side_effect=fault):
                with self.assertRaises(OSError):module.restore(s)
            self.assertEqual(s.read(current),b)
            with self.assertRaises(ValueError):s.read(old)

class Chronology(unittest.TestCase):
    def test_future_changes_leave_prior_walk_forward_fold_identical(self):
        from .evaluation import walk_forward
        x=['0.001','-0.002','0.003','-0.004']*15;a=walk_forward(x);y=x[:35]+['0.05']*25;b=walk_forward(y)
        self.assertEqual(a['folds'][0],b['folds'][0]);self.assertEqual(len(a['folds']),4);self.assertEqual(a['unused_suffix_observations'],15)
    def test_rate_limit_fixture_stops_without_retry_or_partial_store(self):
        import httpx
        from .acquisition import ingest
        original=httpx.AsyncClient;calls=[]
        def handler(request):calls.append(str(request.url));return httpx.Response(429,headers={'Retry-After':'60'})
        with tempfile.TemporaryDirectory() as root:
            s=HistoryStore(root,allow_observed=True);w=StockWorkspace(environment=ENV,history_store=s)
            with patch('httpx.AsyncClient',side_effect=lambda **kw:original(transport=httpx.MockTransport(handler),**kw)):
                with self.assertRaises(ValueError):asyncio.run(ingest(w,'AAPL','2024-01-01','2024-01-10'))
            self.assertEqual(len(calls),1);self.assertEqual(s.list(),[]);self.assertGreater(w.cooldowns['alpaca'],w.clock())

class IndependentReferences(unittest.TestCase):
    def test_state_label_permutation_and_missing_policy(self):
        from .models import hmm_filter
        from .evaluation import evaluate
        x=[.01,-.02,.03];a=[[.9,.1],[.2,.8]]
        ll,p,_,_=hmm_filter(x,[0,.01],[.0001,.001],a,[.6,.4]);other,q,_,_=hmm_filter(x,[.01,0],[.001,.0001],[[.8,.2],[.1,.9]],[.4,.6])
        self.assertAlmostEqual(ll,other,places=12)
        for r,s in zip(p,q):self.assertAlmostEqual(r[0],s[1],places=12)
        with self.assertRaises(ValueError):evaluate(['0.01']*20+[None]*10,20,25)
    def test_nonzero_gaussian_tail_reference(self):
        from .portfolio import analyze
        from fractions import Fraction
        import math
        x=analyze({'assets':{'ASSET_A':['0.01','-0.02']*10},'weights':{'ASSET_A':'1'}})
        sd=math.sqrt(float(Fraction(9,40000)*20/19))
        self.assertAlmostEqual(x['gaussian_var'],.005+sd*1.6448536269514722,places=14)
        self.assertAlmostEqual(x['gaussian_es'],.005+sd*2.0627128075074257,places=14)
    def test_declared_calendar_reports_missing_without_exchange_claim(self):
        from .acquisition import coverage_against_declared_schedule
        core=normalize('AAPL','1Min',pages([bar('2024-01-02T14:30:00Z'),bar('2024-01-02T14:32:00Z')]),source())
        x=coverage_against_declared_schedule(core,['2024-01-02T14:30:00Z','2024-01-02T14:31:00Z','2024-01-02T14:32:00Z'])
        self.assertEqual(len(x['missing_timestamp_ns']),1);self.assertIn('caller',x['authority'])
    def test_new_endpoint_proofs_and_api_unavailable(self):
        import os
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        with patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787','GIG_HISTORY_STORE_ENABLED':'0','GIG_SEC_ENABLED':'0','GIG_ALPACA_ENABLED':'0'}):
            with TestClient(create_app(),base_url='http://127.0.0.1:8787') as c:
                for target in ('portfolio','evaluation','history-ingest'):
                    p=c.get('/api/v1/request-proof',headers={'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':'http://127.0.0.1:8787','X-GIG-Target':'/api/v1/stocks/'+target,'Sec-Fetch-Site':'same-origin'});self.assertEqual(p.status_code,200)
                    self.assertEqual(c.post('/api/v1/stocks/'+target,json={},headers={'Origin':'https://evil.invalid'}).status_code,403)
                self.assertEqual(c.get('/api/v2/companies/AAPL/accounting-checks').json()['issuer_check'],'UNAVAILABLE')

class ProcessRecovery(unittest.TestCase):
    def test_actual_process_exit_before_and_after_sqlite_commit(self):
        import subprocess,sys,time,hashlib
        from .history_store import canonical
        child="""import sys,json,sqlite3,os
p=json.loads(sys.stdin.read());db=sqlite3.connect(sys.argv[1]);db.execute('PRAGMA synchronous=FULL');db.execute('BEGIN IMMEDIATE');db.execute('INSERT INTO snapshots VALUES(?,?,?,?,?)',(p['revision'],'AAPL','1Min',p['created'],p['raw'].encode()))
if sys.argv[2]=='after':db.commit()
os._exit(23)
"""
        with tempfile.TemporaryDirectory() as root:
            store=HistoryStore(root);old=normalize('AAPL','1Min',pages([bar()]),source());old_rev=store.save(old)['revision'];new=normalize('AAPL','1Min',pages([bar(close='102')]),source());raw=canonical(new);revision=hashlib.sha256(raw).hexdigest();payload=json.dumps({'revision':revision,'created':time.time(),'raw':raw.decode()})
            for mode in ('before','after'):
                result=subprocess.run([sys.executable,'-c',child,str(store.path),mode],input=payload,text=True,capture_output=True,timeout=10);self.assertEqual(result.returncode,23,result.stderr)
                reopened=HistoryStore(root);self.assertEqual(reopened.read(old_rev),old)
                if mode=='before':
                    with self.assertRaises(ValueError):reopened.read(revision)
                else:self.assertEqual(reopened.read(revision),new)
