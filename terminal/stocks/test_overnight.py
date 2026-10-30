"""Authored numerical and cancellation regressions;no provider/network qualification."""
import asyncio,itertools,json,math,os,tempfile,threading,unittest
from decimal import Decimal,localcontext
from unittest.mock import patch
import httpx
from .advanced_models import missing_hmm
from .service import StockWorkspace
from .history_store import HistoryStore

ORIGIN='http://127.0.0.1:8787'


class AnalyticalRequests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        from terminal.server.app import create_app
        self.env=patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':ORIGIN,'GIG_SEC_ENABLED':'0','GIG_ALPACA_ENABLED':'0','GIG_LIVE_ENABLED':'0','GIG_COINBASE_ENABLED':'0'});self.env.start();self.addCleanup(self.env.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.app=create_app(stock_workspace=StockWorkspace(environment={},history_store=HistoryStore(self.temp.name)))
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url=ORIGIN,headers={'Origin':ORIGIN});self.addAsyncCleanup(self.client.aclose)

    async def cancellation(self,target,path,body,*,repeat=False,second='/api/v1/stocks/models'):
        started=threading.Event();release=threading.Event();calls=[]
        def calculate(*args,**kwargs):
            calls.append(1)
            if len(calls)==1:
                started.set()
                if not release.wait(5):raise AssertionError('authored worker release deadline')
            return {'fixture':True}
        with patch(target,calculate),patch('terminal.stocks.models.fit',calculate):
            task=asyncio.create_task(self.client.get(path)if body is None else self.client.post(path,json=body))
            try:
                self.assertTrue(await asyncio.to_thread(started.wait,2))
                task.cancel();await asyncio.sleep(.01)
                if repeat:task.cancel();await asyncio.sleep(.01)
                payload={'returns':['0.01']*20}if second.endswith('/models')else {'revisions':{},'weights':{}}
                with patch('terminal.stocks.datasets.analyze_revisions',calculate):
                    response=await self.client.post(second,json=payload)
                self.assertEqual(response.status_code,429,response.text)
                self.assertEqual(len(calls),1,'cancellation must not admit an overlapping physical worker')
            finally:
                release.set();await asyncio.gather(task,return_exceptions=True)
                # Await physical completion,not just request cancellation.
                for _ in range(100):
                    gate=getattr(self.app.state,'analysis',None)
                    if gate is None or not gate.busy:break
                    await asyncio.sleep(.001)
            self.assertFalse(getattr(self.app.state,'analysis',None)and self.app.state.analysis.busy)

    async def test_canceled_model_request_preserves_physical_worker_budget(self):
        await self.cancellation('terminal.stocks.models.fit','/api/v1/stocks/models',{'returns':['0.01']*20})

    async def test_repeated_cancellation_cannot_release_budget(self):
        await self.cancellation('terminal.stocks.models.fit','/api/v1/stocks/models',{'returns':['0.01']*20},repeat=True)

    async def test_garch_cancellation_preserves_shared_budget(self):
        await self.cancellation('terminal.stocks.advanced_models.optimize_garch','/api/v1/stocks/garch-optimization',{'returns':['0.01']*20})

    async def test_evaluation_cancellation_preserves_shared_budget(self):
        await self.cancellation('terminal.stocks.evaluation.evaluate','/api/v1/stocks/evaluation',{'returns':['0.01']*40,'train_end':20,'validation_end':30})

    async def test_ratio_history_cancellation_preserves_shared_budget(self):
        await self.cancellation('terminal.stocks.ratio_history.reported_history','/api/v2/companies/AAPL/ratio-history',None)

    async def test_dataset_analysis_cannot_bypass_busy_model(self):
        await self.cancellation('terminal.stocks.models.fit','/api/v1/stocks/models',{'returns':['0.01']*20},second='/api/v1/stocks/dataset-analysis')

    async def test_dataset_cancellation_preserves_shared_budget(self):
        await self.cancellation('terminal.stocks.datasets.analyze_revisions','/api/v1/stocks/dataset-analysis',{'revisions':{},'weights':{}})


class WorkerOwnership(unittest.IsolatedAsyncioTestCase):
    async def test_results_errors_and_reuse_are_preserved(self):
        from terminal.server.analysis import AnalysisGate
        gate=AnalysisGate();self.assertEqual(await gate.run(lambda:42),42)
        def invalid():raise ValueError('authored_failure')
        with self.assertRaisesRegex(ValueError,'authored_failure'):await gate.run(invalid)
        self.assertEqual(await gate.run(lambda:43),43);self.assertFalse(gate.busy)
        await gate.close()
        with self.assertRaisesRegex(ValueError,'analysis_closed'):await gate.run(lambda:44)

    async def test_shutdown_drains_canceled_request_worker_and_refuses_new_work(self):
        from terminal.server.analysis import AnalysisGate
        gate=AnalysisGate();started=threading.Event();release=threading.Event();finished=threading.Event()
        def work():started.set();release.wait(5);finished.set();return 1
        task=asyncio.create_task(gate.run(work));close=None
        try:
            self.assertTrue(await asyncio.to_thread(started.wait,2));task.cancel()
            await asyncio.gather(task,return_exceptions=True);self.assertTrue(gate.busy)
            with self.assertRaisesRegex(ValueError,'analysis_busy'):await gate.run(lambda:2)
            close=asyncio.create_task(gate.close());await asyncio.sleep(.01)
            self.assertFalse(close.done());self.assertFalse(finished.is_set())
            with self.assertRaisesRegex(ValueError,'analysis_closed'):await gate.run(lambda:3)
        finally:
            release.set();await asyncio.gather(task,*([]if close is None else [close]),return_exceptions=True)
        self.assertTrue(finished.is_set());self.assertFalse(gate.busy)

    async def test_canceled_worker_failure_is_observed_and_budget_recovers(self):
        from terminal.server.analysis import AnalysisGate
        gate=AnalysisGate();start=threading.Event();release=threading.Event();errors=[]
        loop=asyncio.get_running_loop();old=loop.get_exception_handler();loop.set_exception_handler(lambda *_:errors.append(True))
        def work():start.set();release.wait(5);raise ValueError('authored_private_error')
        task=asyncio.create_task(gate.run(work))
        try:
            self.assertTrue(await asyncio.to_thread(start.wait,2));task.cancel();await asyncio.gather(task,return_exceptions=True)
            release.set();await gate.close();await asyncio.sleep(0)
            self.assertFalse(gate.busy);self.assertFalse(errors)
        finally:release.set();loop.set_exception_handler(old)


class FixedHMMStability(unittest.TestCase):
    def test_large_finite_variance_has_independent_finite_density(self):
        result=missing_hmm(['0'],[0,0],[1e308,1e308],[[.5,.5],[.5,.5]],[.5,.5])
        self.assertEqual(result['states'][0]['probabilities'],[.5,.5])
        expected=-.5*math.log(2*math.pi)-154*math.log(10)
        self.assertAlmostEqual(result['observed_log_likelihood'],expected,places=12)
        json.dumps(result,allow_nan=False)

    def test_unrepresentable_likelihood_fails_explicitly_without_NaN(self):
        for means,variances in [([1e308,1e308],[.01,.01]),([1e154,1e154],[.01,.01])]:
            with self.assertRaisesRegex(ValueError,'hmm_likelihood_capacity'):
                missing_hmm(['0']*256,means,variances,[[.5,.5],[.5,.5]],[.5,.5])

    def test_one_negligible_state_does_not_poison_finite_state(self):
        result=missing_hmm(['0',None,'0'],[1e308,0],[.01,.01],[[.8,.2],[.3,.7]],[.6,.4])
        self.assertEqual(result['states'][0]['probabilities'],[0,1])
        self.assertEqual(result['states'][1]['probabilities'],[.3,.7])
        self.assertEqual(result['states'][2]['probabilities'],[0,1])
        self.assertTrue(math.isfinite(result['observed_log_likelihood']));json.dumps(result,allow_nan=False)

    def test_parameter_shapes_types_and_probabilities_fail_as_ValueError(self):
        valid=[['0'],[0,0],[.01,.04],[[.8,.2],[.3,.7]],[.6,.4]]
        for index,value in [(1,None),(1,'ab'),(2,{}),(3,[None,None]),(3,[[1],[1]]),(4,None),
                            (1,[True,0]),(1,[10**1000,0]),(2,[float('inf'),1]),(2,[0,1]),
                            (3,[[1,0],[.3,.7]]),(4,[.1,.1])]:
            args=list(valid);args[index]=value
            with self.subTest(index=index,value_type=type(value).__name__),self.assertRaises(ValueError):missing_hmm(*args)

    def test_independent_path_enumeration_missing_emissions_and_prefix_causality(self):
        values=['0.02',None,'-0.01'];means=[0,.1];variance=[.01,.04];transition=[[.8,.2],[.3,.7]];prior=[.6,.4]
        result=missing_hmm(values,means,variance,transition,prior)
        with localcontext()as ctx:
            ctx.prec=70;D=lambda v:Decimal(str(v));pi=D('3.141592653589793238462643383279502884197169399375105820974944592307816')
            for n in range(1,len(values)+1):
                marginal=[Decimal(0),Decimal(0)]
                for path in itertools.product(range(2),repeat=n):
                    weight=D(prior[path[0]])
                    for i,state in enumerate(path):
                        if i:weight*=D(transition[path[i-1]][state])
                        if values[i]is not None:weight*=(-(D(values[i])-D(means[state]))**2/(2*D(variance[state]))).exp()/(2*pi*D(variance[state])).sqrt()
                    marginal[path[-1]]+=weight
                total=sum(marginal)
                for j in range(2):self.assertAlmostEqual(result['states'][n-1]['probabilities'][j],float(marginal[j]/total),places=13)
                prefix=missing_hmm(values[:n],means,variance,transition,prior)
                self.assertEqual(prefix['states'],result['states'][:n])
            self.assertAlmostEqual(result['observed_log_likelihood'],float(total.ln()),places=13)

    def test_missing_only_boundaries_and_invalid_observations(self):
        result=missing_hmm([None]*256,[0,.1],[.01,.04],[[.8,.2],[.3,.7]],[.6,.4])
        self.assertEqual(result['observed_log_likelihood'],0);self.assertEqual(len(result['states']),256)
        for bad in ([],[None]*257,['NaN'],[True],['2']):
            with self.assertRaises(ValueError):missing_hmm(bad,[0,.1],[.01,.04],[[.8,.2],[.3,.7]],[.6,.4])
