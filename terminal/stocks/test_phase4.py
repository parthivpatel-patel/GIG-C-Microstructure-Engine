"""Authored Phase4 correctness/negative controls;no empirical data evidence."""
import copy,hashlib,itertools,json,math,os,sqlite3,tempfile,unittest
from pathlib import Path
from fractions import Fraction
from unittest.mock import patch
from .test_phase3 import bar,pages,source
from .history import normalize
from .history_store import HistoryStore

class Persistence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)/'private';self.now=[1000000.];self.store=HistoryStore(self.root,clock=lambda:self.now[0]);self.core=normalize('AAPL','1Min',pages([bar()]),source())
    def test_restart_revision_exactness_and_idempotence(self):
        a=self.store.save(self.core);b=self.store.save(self.core);self.assertEqual(a,b);self.assertEqual(len(self.store.list()),1)
        restored=HistoryStore(self.root,clock=lambda:self.now[0]).read(a['revision']);self.assertEqual(restored['canonical_sha256'],self.core['canonical_sha256']);self.assertEqual(restored['bars'],self.core['bars'])
        import jsonschema
        jsonschema.validate(restored,json.loads((Path(__file__).resolve().parents[1]/'server/schemas/backend_history_v2.schema.json').read_text()))
    def test_multisymbol_timeframes_and_retention(self):
        a=self.store.save(self.core);other=normalize('NVDA','1Day',pages([bar()]),source());self.store.save(other);self.assertEqual({r['symbol'] for r in self.store.list()},{'AAPL','NVDA'})
        self.now[0]+=604801
        with self.assertRaises(ValueError):self.store.read(a['revision'])
        restarted=HistoryStore(self.root,clock=lambda:self.now[0]);self.assertEqual(restarted.list(),[])
    def test_tamper_and_invalid_snapshot_do_not_commit(self):
        a=self.store.save(self.core);bad=copy.deepcopy(self.core);bad['bars'][0]['close']='999'
        with self.assertRaises(ValueError):self.store.save(bad)
        self.assertEqual(len(self.store.list()),1)
        with sqlite3.connect(self.store.path) as db:db.execute('UPDATE snapshots SET payload=?',(b'{}',))
        with self.assertRaisesRegex(ValueError,'digest'):self.store.read(a['revision'])
        with self.assertRaisesRegex(ValueError,'revision_conflict'):self.store.save(self.core)
    def test_permission_paths_and_observed_retention(self):
        observed=normalize('AAPL','1Min',pages([bar()]),source('OBSERVED_OFFICIAL_RESPONSE'))
        with self.assertRaisesRegex(ValueError,'retention'):self.store.save(observed)
        bad=Path(self.temp.name)/'public';bad.mkdir(mode=0o755);bad.chmod(0o755)
        with self.assertRaises(ValueError):HistoryStore(bad)
        link=Path(self.temp.name)/'link';link.symlink_to(self.root)
        with self.assertRaises(ValueError):HistoryStore(link)
    def test_unknown_database_schema_is_refused(self):
        with sqlite3.connect(self.store.path) as db:db.execute('PRAGMA user_version=99')
        with self.assertRaisesRegex(ValueError,'schema_version'):HistoryStore(self.root)

    def test_observed_read_gate_is_rechecked_after_restart(self):
        observed=normalize('AAPL','1Min',pages([bar()]),source('OBSERVED_OFFICIAL_RESPONSE'))
        revision=HistoryStore(self.root,allow_observed=True).save(observed)['revision']
        with self.assertRaisesRegex(ValueError,'retention'):HistoryStore(self.root).read(revision)
        self.assertEqual(len(self.store.list()),1) # no destructive silent cleanup on permission change
        with self.assertRaises(ValueError):HistoryStore(self.root,allow_observed='false')

    def test_capacity_rejection_is_atomic_and_delete_explicit(self):
        for i in range(32):self.store.save(normalize('AAPL','1Min',pages([bar(close=str(100+i))]),source()))
        with self.assertRaisesRegex(ValueError,'capacity'):self.store.save(normalize('AAPL','1Min',pages([bar(close='999')]),source()))
        self.assertEqual(len(self.store.list()),32);r=self.store.list()[0]['revision'];self.store.delete(r);self.assertEqual(len(self.store.list()),31)

class Models(unittest.TestCase):
    def test_forward_likelihood_matches_independent_path_enumeration(self):
        from .models import hmm_filter
        x=[.01,-.02,.03,-.01];means=[0.,.01];v=[.001,.002];a=[[.8,.2],[.3,.7]];prior=[.4,.6];total=0.
        for path in itertools.product(range(2),repeat=4):
            probability=prior[path[0]]
            for i,state in enumerate(path):
                probability*=math.exp(-(x[i]-means[state])**2/(2*v[state]))/math.sqrt(2*math.pi*v[state])
                if i:probability*=a[path[i-1]][state]
            total+=probability
        ll,p,_,_=hmm_filter(x,means,v,a,prior);self.assertAlmostEqual(ll,math.log(total),places=12)
        self.assertTrue(all(abs(sum(row)-1)<1e-12 for row in p))
    def test_fits_deterministic_monotone_and_constraint_valid(self):
        from .models import fit
        values=['0.001','-0.002','0.003','-0.004']*10;x=fit(values);self.assertEqual(x,fit(values));h=x['hmm'];self.assertTrue(h['fitted']);self.assertTrue(all(b>=a-1e-8 for a,b in zip(h['likelihood_trace'],h['likelihood_trace'][1:])))
        self.assertTrue(all(v>0 for v in h['variances']));g=x['garch'];self.assertGreater(g['omega'],0);self.assertLess(g['alpha']+g['beta'],1);self.assertGreaterEqual(g['log_likelihood'],g['constant_variance_log_likelihood'])
        constant=fit(['0.01']*20);self.assertFalse(constant['hmm']['fitted']);self.assertFalse(constant['garch']['fitted'])
    def test_garch_reference_and_kalman_missing_covariance(self):
        from .models import garch_likelihood,kalman
        x=[.01,-.02];ll,path,nextv=garch_likelihood(x,0,1e-6,.08,.9,.0001);v1=1e-6+.08*.01**2+.9*.0001
        self.assertEqual(path,[.0001,v1]);self.assertAlmostEqual(nextv,1e-6+.08*.02**2+.9*v1)
        independent=sum(-.5*(math.log(2*math.pi*v)+r*r/v) for r,v in zip(x,[.0001,v1]));self.assertAlmostEqual(ll,independent)
        rows=kalman([.01,None,.02])['states'];self.assertEqual(rows[1]['estimate'],rows[0]['estimate']);self.assertGreater(rows[1]['variance'],rows[0]['variance']);self.assertTrue(all(v['variance']>0 for v in rows))
    def test_hmm_extreme_emissions_are_log_stable(self):
        from .models import hmm_filter
        ll,prob,_,_=hmm_filter([1.,-1.],[0.,.01],[1e-12,1e-12],[[.9,.1],[.1,.9]],[.5,.5])
        self.assertTrue(math.isfinite(ll));self.assertTrue(all(abs(sum(row)-1)<1e-9 for row in prob))

    def test_extreme_equal_likelihood_states_remain_normalized(self):
        from .models import hmm_filter
        _,prob,_,_=hmm_filter([1.,-1.],[0.,0.],[1e-12,1e-12],[[.5,.5],[.5,.5]],[.5,.5])
        self.assertEqual(prob,[[.5,.5],[.5,.5]])

    def test_bad_model_and_scenario_inputs_fail_bounded(self):
        from .models import fit
        from .risk import scenarios
        for x in [[],['NaN']*20,['1e999999999999']*20,['0']*257]:
            with self.assertRaises(ValueError):fit(x)
        for q in ['1e999999999999','1/0','NaN']:
            with self.assertRaises(ValueError):scenarios(q,'100',['0.1'])

class RiskAndFinancials(unittest.TestCase):
    def test_independent_risk_tail_parametric_and_linear_exposure(self):
        from .risk import analyze,scenarios
        rows=[bar(close=str(100+i)) for i in range(25)];x=analyze(rows);returns=[Fraction(1,100+i) for i in range(24)];losses=sorted([-v for v in returns],reverse=True)
        wire=lambda r:Fraction(int(r['numerator']),int(r['denominator']))
        mean=sum(returns)/24;variance=sum((v-mean)**2 for v in returns)/23
        reference_normal=-float(mean)+1.6448536269514722*math.sqrt(float(variance))
        self.assertAlmostEqual(x['normal_parametric_var'],reference_normal,places=14)
        self.assertEqual(wire(x['historical_var']),losses[1]);self.assertEqual(wire(x['historical_expected_shortfall']),sum(losses[:2])/2);self.assertEqual(len(x['rolling20']),5)
        self.assertEqual(wire(scenarios('-2','100',['-0.1'])['cases'][0]['linear_pnl']),20)
        self.assertEqual(analyze(rows[:10])['status'],'UNAVAILABLE')
        from decimal import Decimal,localcontext
        tiny=analyze([bar(close=str(10**15-24+i)) for i in range(25)])['log_returns_approximate'][0]
        with localcontext() as c:c.prec=80;expected=float((Decimal(10**15-23)/Decimal(10**15-24)).ln())
        self.assertLessEqual(abs(tiny-expected),abs(expected)*1e-12)
    def test_actual_period_alignment_missingness_and_ambiguity(self):
        from .statements import aligned
        from .test_backend import FinancialMetrics
        n=FinancialMetrics().normalized();x=aligned(n,'income','annual');self.assertEqual(x['periods'][0]['fields']['revenue']['value'],'100');self.assertFalse(aligned(n,'income','quarter')['periods'])
        n['history']['revenue'].append({**n['history']['revenue'][0],'concept':'CompetingRevenue'});self.assertEqual(aligned(n)['periods'][0]['fields']['revenue']['status'],'AMBIGUOUS')
        self.assertEqual(aligned(n,'cash','quarter')['coverage'],'SELECTED_REPORTED_FACTS_NOT_COMPLETE_STATEMENTS')

class API(unittest.TestCase):
    def test_new_mutations_require_explicit_endpoint_scoped_proofs(self):
        from terminal.server.request_proofs import RequestProofs,bootstrap_context,authorize_mutation
        origin='https://authored-8787.app.github.dev';origins=(origin,)
        for target in ('/api/v1/stocks/models','/api/v1/stocks/scenarios','/api/v1/stocks/history-store'):
            h={'x-gig-bootstrap':'same-origin-v1','x-gig-browser-origin':origin,'x-gig-target':target,'sec-fetch-site':'same-origin'}
            context,_=bootstrap_context(h,origins,origin);self.assertEqual(context['target'],target)
            p=RequestProofs();token=p.issue(origin,target)
            headers={'origin':'http://localhost:8787','host':'localhost:8787','x-gig-request-proof':token}
            self.assertEqual(authorize_mutation(headers,target,origins,origin,p)[0],origin)
            self.assertIsNone(authorize_mutation(headers,target,origins,origin,p)[0])
            token=p.issue(origin,target);headers['x-gig-request-proof']=token
            self.assertIsNone(authorize_mutation(headers,'/api/v1/control',origins,origin,p)[0])
            self.assertIsNone(bootstrap_context({**h,'x-gig-target':'/api/v1/admin'},origins,origin)[0])
            self.assertIsNone(bootstrap_context({**h,'x-gig-browser-origin':'https://evil.invalid'},origins,origin)[0])

    def test_owner_private_storage_route_is_protected_and_restores_revision(self):
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        from .service import StockWorkspace
        from .test_repair import ENV,authored_fetcher
        import asyncio
        with tempfile.TemporaryDirectory() as directory:
            store=HistoryStore(Path(directory)/'private');w=StockWorkspace(environment=ENV,fetcher=authored_fetcher,history_store=store)
            asyncio.run(w.refresh('AAPL','alpaca',start='2026-10-01',end='2026-10-26'))
            with patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787','GIG_ALPACA_ENABLED':'0','GIG_SEC_ENABLED':'0'}):
                with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
                    url='/api/v1/stocks/history-store';body={'action':'save','symbol':'AAPL'}
                    self.assertEqual(c.post(url,json=body,headers={'Origin':'https://evil.invalid'}).status_code,403)
                    x=c.post(url,json=body,headers={'Origin':'http://127.0.0.1:8787'});self.assertEqual(x.status_code,200,x.text)
                    revision=x.json()['revision'];self.assertEqual(c.get(url+'?revision='+revision).json()['snapshot']['record_count'],2)
                    self.assertEqual(len(c.get(url).json()['revisions']),1)

    def test_origin_guard_cache_only_queries_models_and_risk(self):
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        with patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787','GIG_SEC_ENABLED':'0','GIG_ALPACA_ENABLED':'0','GIG_HISTORY_STORE_ENABLED':'0'}):
            with TestClient(create_app(),base_url='http://127.0.0.1:8787') as c:
                before=c.get('/api/v1/state').json();self.assertEqual(c.post('/api/v1/stocks/models',json={'returns':['0.01']*20},headers={'Origin':'https://evil.invalid'}).status_code,403)
                good={'Origin':'http://127.0.0.1:8787'};self.assertEqual(c.post('/api/v1/stocks/models',json={'returns':['0.01']*20},headers=good).status_code,200)
                self.assertEqual(c.get('/api/v2/companies/AAPL/risk').json()['risk']['status'],'UNAVAILABLE');self.assertEqual(c.get('/api/v2/companies/AAPL/statements?period=quarter').status_code,200)
                self.assertEqual(c.get('/api/v2/companies/AAPL/statements?period=bad').status_code,400);self.assertEqual(c.get('/api/v1/stocks/history-store').status_code,422)
                self.assertEqual(before['book'],c.get('/api/v1/state').json()['book'])
