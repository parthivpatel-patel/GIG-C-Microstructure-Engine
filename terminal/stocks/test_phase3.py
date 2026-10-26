"""Independently authored Phase3 fixtures;never observed-company validation."""
import asyncio,copy,hashlib,json,os,random,unittest
from fractions import Fraction
from unittest.mock import patch
from .history import HistorySource,normalize,from_workspace


def bar(t='2024-01-02T14:30:00.000000001Z',close='100'):
    return dict(timestamp=t,open=close,high=close,low=close,close=close,volume='20')


def source(origin='HISTORICAL_SYNTHETIC'):
    return HistorySource('authored','single-venue','authored coverage','raw',origin,'fixture_only','2024-02-01T12:00:00Z')


def pages(rows):return [{'bars':rows,'sha256':'a'*64}]


class HistoricalIntegrity(unittest.TestCase):
    def test_exact_prices_time_scope_and_determinism(self):
        p=pages([bar()]);a=normalize('AAPL','1Min',p,source());b=normalize('AAPL','1Min',p,source())
        self.assertEqual(a,b);self.assertEqual(a['state'],'SIMULATED');self.assertEqual(a['bars'][0]['timestamp_ns'],'1704205800000000001')
        self.assertFalse(a['complete_history']);self.assertEqual(a['session']['status'],'UNVERIFIED')
        self.assertEqual(normalize('AAPL','1Min',p,source('OBSERVED_OFFICIAL_RESPONSE'))['state'],'HISTORICAL')
        # Canonical digest is independently reconstructed without production helper.
        digest=a.pop('canonical_sha256');self.assertEqual(digest,hashlib.sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest())
    def test_duplicate_and_decreasing_page_boundaries_fail_atomically(self):
        p=pages([bar()]);p.append(copy.deepcopy(p[0]));before=copy.deepcopy(p)
        with self.assertRaisesRegex(ValueError,'duplicate'):normalize('AAPL','1Min',p,source())
        self.assertEqual(before,p);p[1]['bars'][0]['timestamp']='2024-01-01T14:30:00Z'
        with self.assertRaisesRegex(ValueError,'out_of_order'):normalize('AAPL','1Min',p,source())
    def test_gap_candidate_not_missing_exchange_claim(self):
        p=pages([bar('2024-01-05T14:30:00Z'),bar('2024-01-08T14:30:00Z')]);x=normalize('AAPL','1Day',p,source(),has_more=True)
        self.assertEqual(x['gap_candidates'],[{'after_index':0,'elapsed_ns':str(3*86400*10**9)}]);self.assertTrue(x['has_more']);self.assertFalse(x['complete_history'])
    def test_numeric_timestamp_identity_and_shape_rejection(self):
        for key,value in [('close','NaN'),('volume','-1'),('open','0'),('high','99'),('timestamp','2024-01-01T00:00:00'),('close','1e999'),('volume',True),('unexpected','x')]:
            r=bar();r[key]=value
            with self.subTest(key=key,value=value),self.assertRaises((ValueError,TypeError)):normalize('AAPL','1Day',pages([r]),source())
        for ticker in ['aapl','AAPL/../','']:
            with self.assertRaises(ValueError):normalize(ticker,'1Day',pages([]),source())
        with self.assertRaises(ValueError):normalize('AAPL','1Tick',pages([]),source())
    def test_explicit_record_page_digest_and_numeric_budgets(self):
        for p in [pages([bar()]*257),pages([])*5,[],[{'bars':[],'sha256':'z'*64}],pages([{str(i):'x' for i in range(1000)}]),[{str(i):'x' for i in range(1000)}]]:
            with self.assertRaises(ValueError):normalize('AAPL','1Day',p,source())
        with self.assertRaises(ValueError):normalize('AAPL','1Day',pages([bar(close='1'*65)]),source())
    def test_reference_returns_and_drawdown_256_bars(self):
        from datetime import datetime,timedelta,timezone
        from .price_research import describe
        rng=random.Random(20261026);closes=[rng.randint(1,100000) for _ in range(256)];start=datetime(2024,1,1,tzinfo=timezone.utc)
        rows=[bar((start+timedelta(minutes=i)).isoformat().replace('+00:00','Z'),str(v)) for i,v in enumerate(closes)]
        x=normalize('AAPL','1Min',pages(rows),source());d=describe(x['bars']);wire=lambda m:Fraction(int(m['value']['numerator']),int(m['value']['denominator']))
        self.assertEqual(wire(d['total_return']),Fraction(closes[-1],closes[0])-1)
        self.assertEqual(wire(d['maximum_close_drawdown']),max(1-Fraction(v,max(closes[:i+1])) for i,v in enumerate(closes)))
        reference=sorted([1-Fraction(b,a) for a,b in zip(closes,closes[1:])],reverse=True);tail=13
        self.assertEqual(wire(d['historical_var_95']),reference[tail-1]);self.assertEqual(wire(d['historical_es_95']),sum(reference[:tail])/tail)
    def test_fixed_model_outputs_not_fitted_forecasts_and_causal_signal(self):
        from .research import analyze
        values=['0.01','-0.02']*20;x=analyze(values);y=analyze(values[:-1]+['0.03'])
        self.assertFalse(x['garch']['fitted']);self.assertFalse(x['hmm']['fitted'])
        self.assertEqual(x['garch']['one_step_variance'][0],.0001)
        self.assertAlmostEqual(x['garch']['one_step_variance'][1],1e-6+.08*.01**2+.90*.0001)
        self.assertEqual(x['strategy']['positions'],y['strategy']['positions']);self.assertEqual(x['hmm']['high_volatility_probability'][:-1],y['hmm']['high_volatility_probability'][:-1])
    def test_independent_realized_volatility_and_sample_variance(self):
        from .price_research import describe
        from decimal import Decimal,localcontext
        d=describe([bar(close=v) for v in ('100','110','99')])
        self.assertEqual(d['sample_return_variance']['value'],{'numerator':'1','denominator':'50'})
        with localcontext() as c:
            c.prec=80;expected=float((Decimal(1)/50).sqrt())
        self.assertAlmostEqual(d['realized_simple_return_volatility']['value'],expected,places=15)
        self.assertIsNone(describe([bar()])['sample_return_variance']['value'])
        self.assertIsNone(describe([bar()])['realized_simple_return_volatility']['value'])

    def test_cached_source_metadata_required_and_no_network(self):
        from .service import StockWorkspace
        w=StockWorkspace(environment={});self.assertEqual(from_workspace(w,'AAPL')['state'],'BLOCKED')
        self.assertEqual(len(w.cache),0)


class Workflow(unittest.TestCase):
    def test_history_rejection_preserves_previously_accepted_cache(self):
        from .service import StockWorkspace,AccessError
        from .test_repair import ENV,authored_fetcher
        w=StockWorkspace(environment=ENV,fetcher=authored_fetcher)
        async def check():
            await w.refresh('AAPL','alpaca',start='2026-10-01',end='2026-10-26')
            before=copy.deepcopy(w.cache);w.last_request=-100
            with patch('terminal.stocks.history.normalize',side_effect=ValueError('authored_bad_page')):
                with self.assertRaises(AccessError):await w.refresh('AAPL','alpaca',start='2026-10-01',end='2026-10-26')
            self.assertEqual(w.cache,before)
        asyncio.run(check())

    def test_authored_aapl_search_load_financials_history_research_and_security(self):
        from starlette.testclient import TestClient
        from terminal.server.app import create_app
        from .service import StockWorkspace
        from .test_repair import ENV,authored_fetcher
        from terminal.server.backend_contract import company_contract
        w=StockWorkspace(environment=ENV,fetcher=authored_fetcher)
        async def load():
            await w.refresh('AAPL','sec');w.last_request=-100
            await w.refresh('AAPL','alpaca',start='2026-10-01',end='2026-10-26')
        asyncio.run(load())
        # Production source receipts are validated;no fixture provenance relabel.
        contract=company_contract(w,'AAPL');self.assertEqual(contract['instrument']['cik'],'0000320193');self.assertEqual(contract['data_origin'],'HISTORICAL_SYNTHETIC')
        with patch.dict(os.environ,{'GIG_TERMINAL_ALLOWED_ORIGINS':'http://127.0.0.1:8787','GIG_ALPACA_ENABLED':'0','GIG_SEC_ENABLED':'0'}):
            with TestClient(create_app(stock_workspace=w),base_url='http://127.0.0.1:8787') as c:
                before=c.get('/api/v1/state').json();x=c.get('/api/v2/companies/AAPL/historical');self.assertEqual(x.status_code,200,x.text);x=x.json()
                import jsonschema
                from pathlib import Path
                jsonschema.validate(x,json.loads((Path(__file__).resolve().parents[1]/'server/schemas/backend_history_v2.schema.json').read_text()))
                self.assertEqual(x['state'],'SIMULATED');self.assertEqual(x['research']['return_count'],1);self.assertEqual(x['source']['feed'],'iex')
                self.assertEqual(c.get('/api/v2/companies/AAPL/historical?url=evil').status_code,400)
                self.assertEqual(c.get('/api/v2/companies/INVALID/historical').status_code,400)
                self.assertEqual(c.get('/api/v1/state').json()['book'],before['book'])


class FeedHealth(unittest.TestCase):
    def test_heartbeat_never_qualifies_data_and_reconnect_needs_new_ack_and_observation(self):
        from .feed_health import ObservationMonitor
        m=ObservationMonitor(authorized=True,synthetic=True,stale_after_ns=100)
        g=m.connect(0);m.heartbeat(g,1);self.assertEqual(m.view('AAPL',1)['state'],'UNAVAILABLE')
        m.acknowledge('AAPL',g,2);m.observe('AAPL',g,3,'2024-01-01T00:00:00Z');self.assertEqual(m.view('AAPL',103)['state'],'SIMULATED')
        m.heartbeat(g,104);self.assertEqual(m.view('AAPL',104)['state'],'STALE')
        m.disconnect(105);self.assertEqual(m.view('AAPL',105)['state'],'UNAVAILABLE');g2=m.connect(106)
        with self.assertRaises(ValueError):m.observe('AAPL',g,107,'2024-01-01T00:00:00Z')
        self.assertEqual(m.view('AAPL',107)['state'],'UNAVAILABLE');self.assertGreater(g2,g)
    def test_authorization_delay_bounds_and_atomic_rejection(self):
        from .feed_health import ObservationMonitor
        m=ObservationMonitor();self.assertEqual(m.view('AAPL',0)['state'],'BLOCKED')
        with self.assertRaises(ValueError):m.connect(0)
        m=ObservationMonitor(authorized=True,delay_ns=10);g=m.connect(0);m.acknowledge('AAPL',g,1);m.observe('AAPL',g,2,'2024-01-01T00:00:00Z')
        self.assertEqual(m.view('AAPL',2)['state'],'DELAYED');before=copy.deepcopy(m.__dict__)
        with self.assertRaises(ValueError):m.observe('AAPL',g,1,'2024-01-01T00:00:00Z')
        self.assertEqual(before,m.__dict__)
        for ticker in ('NVDA','MSFT','GOOG','META','AMZN','TSLA','JPM'):m.acknowledge(ticker,g,3)
        with self.assertRaises(ValueError):m.acknowledge('XYZ',g,3)

if __name__=='__main__':unittest.main(verbosity=2)
