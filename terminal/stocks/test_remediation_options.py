"""Authored scenario-domain regressions;no network or observed market data."""
import json
import math
import unittest
from unittest.mock import patch

from starlette.testclient import TestClient
from terminal.server.app import create_app
from .options import price, scenario


class ScenarioDomain(unittest.TestCase):
    def config(self, spot=100.):
        return dict(spot=spot, strike=spot, years=1, volatility=.2)

    def test_boundaries_and_adjacent_inputs_preserve_base_metrics(self):
        for spot in (1e-6, math.nextafter(1e-6, math.inf),
                     math.nextafter(1e7, -math.inf), 1e7):
            with self.subTest(spot=spot):
                config=self.config(spot);out=scenario(config)
                self.assertEqual(out['metrics'], price(**config))
                self.assertEqual(sum(map(len,out['surface'])),153)
                unavailable=[p for row in out['surface'] for p in row if p['theoretical_price'] is None]
                self.assertTrue(unavailable)
                self.assertTrue(all(p['reason']=='derived_strike_outside_price_domain' for p in unavailable))
                self.assertEqual(out['surface_coverage']['unavailable'],len(unavailable))
                self.assertEqual(out['surface_coverage']['available']+len(unavailable),153)
                json.dumps(out,allow_nan=False)

    def test_ordinary_grid_preserves_all_153_original_cells(self):
        out=scenario(self.config())
        for i,row in enumerate(out['surface']):
            for j,point in enumerate(row):
                k=100*(.6+j*.05);t=.05+i*.11875
                self.assertEqual(point,dict(strike=k,years=t,volatility=.2,
                                           theoretical_price=price(100,k,t,.2)['price']))
        self.assertEqual(out['surface_coverage']['unavailable'],0)
        # Independent elementary price formula at the central point.
        expected=100*math.erf(.1/math.sqrt(2))
        self.assertAlmostEqual(out['metrics']['price'],expected,places=12)

    def test_invalid_nonfinite_and_huge_parameters_reject(self):
        for name,values in {'spot':(0,1e-7,1e7+1,math.inf,math.nan,10**1000,True),
                            'strike':(-1,0,math.nan),'years':(0,11,math.inf),
                            'volatility':(0,6,math.nan)}.items():
            for value in values:
                with self.subTest(name=name,value_type=type(value).__name__):
                    c={**self.config(),name:value}
                    with self.assertRaises(ValueError):scenario(c)

    def test_extreme_valid_cross_parameters_are_finite(self):
        for spot,strike in ((1e-6,1e7),(1e7,1e-6)):
            for right in ('call','put'):
                c=dict(spot=spot,strike=strike,years=10,volatility=5,rate=-.5,dividend=.5,right=right)
                self.assertTrue(all(math.isfinite(v) for v in scenario(c)['metrics'].values()))


class ScenarioHTTP(unittest.TestCase):
    def setUp(self):
        env={k:'0' for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED')}
        self.env=patch.dict('os.environ',env);self.env.start();self.addCleanup(self.env.stop)
        self.app=create_app();self.client=TestClient(self.app,base_url='http://127.0.0.1:8787')

    def test_boundary_http_success_without_native_mutation(self):
        before=self.app.state.native.replay.canonical()
        for s in (1e-6,math.nextafter(1e-6,math.inf),100.,math.nextafter(1e7,-math.inf),1e7):
            response=self.client.post('/api/v1/stocks/options',headers={'Origin':'http://127.0.0.1:8787'},
                                      json=dict(spot=s,strike=s,years=1,volatility=.2))
            self.assertEqual(response.status_code,200)
            self.assertTrue(math.isfinite(response.json()['metrics']['price']))
        self.assertEqual(before,self.app.state.native.replay.canonical())

    def test_invalid_inputs_still_fail_closed(self):
        for spot in (0,-1,1e7+1):
            r=self.client.post('/api/v1/stocks/options',headers={'Origin':'http://127.0.0.1:8787'},
                               json=dict(spot=spot,strike=100,years=1,volatility=.2))
            self.assertEqual(r.status_code,422)
        for token in ('NaN','Infinity','1e999'):
            body='{"spot":'+token+',"strike":100,"years":1,"volatility":0.2}'
            r=self.client.post('/api/v1/stocks/options',headers={'Origin':'http://127.0.0.1:8787','Content-Type':'application/json'},content=body)
            self.assertIn(r.status_code,(400,422))

    def test_unauthorized_origin_still_rejected(self):
        r=self.client.post('/api/v1/stocks/options',headers={'Origin':'https://attacker.invalid'},json={})
        self.assertEqual(r.status_code,403)
