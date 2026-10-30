"""Independent supplied-depth research oracles;not observed market validation."""
import copy
import itertools
import unittest
from decimal import Decimal,localcontext
from fractions import Fraction
from unittest.mock import patch
from starlette.testclient import TestClient
from terminal.server.concentration import calculate
from terminal.server.app import create_app


def authored(bids=(),asks=()):
    return {'origin':'HISTORICAL_SYNTHETIC','provider':'authored','instrument':'DEMO',
            'revision':'1','position':7,'provenance':{'dataset':'independent-concentration-test'},
            'book':{'bids':[dict(price_ticks=str(100-i),quantity=str(q)) for i,q in enumerate(bids)],
                    'asks':[dict(price_ticks=str(101+i),quantity=str(q)) for i,q in enumerate(asks)]}}


def exact(wire):return Fraction(int(wire['numerator']),int(wire['denominator']))


class Concentration(unittest.TestCase):
    def test_equal_and_concentrated_independent_hand_values(self):
        for q,h,n in (([1,1,1,1],Fraction(1,4),Fraction(0)),([1],Fraction(1),Fraction(1)),
                      ([3,1],Fraction(5,8),Fraction(1,4)),([9,1],Fraction(41,50),Fraction(16,25))):
            value=calculate(authored(q),side='bid')
            self.assertEqual(exact(value['hhi']),h);self.assertEqual(exact(value['normalized_hhi']),n)

    def test_asymmetric_side_selection_and_partial_depth(self):
        state=authored([1,3],[2]);both=calculate(state,depth=1)
        self.assertEqual(exact(both['hhi']),Fraction(5,9))
        self.assertEqual(exact(calculate(state,'ask')['hhi']),1)
        self.assertEqual(exact(calculate(state,'bid')['hhi']),Fraction(5,8))
        self.assertFalse(calculate(state)['requested_depth_populated'])
        self.assertEqual(both['available_levels'],{'bids':2,'asks':1})
        self.assertIn('Supplied selected levels only',both['coverage'])

    def test_bounded_exhaustive_decimal_oracle(self):
        # Independent Decimal probability calculation,not production output as oracle.
        with localcontext() as context:
            context.prec=60
            for quantities in itertools.product(range(1,5),repeat=4):
                state=authored(quantities[:2],quantities[2:]);before=copy.deepcopy(state)
                value=calculate(state)
                probabilities=[Decimal(q)/sum(quantities) for q in quantities]
                expected=sum(p*p for p in probabilities)
                fraction=exact(value['hhi']);actual=Decimal(fraction.numerator)/fraction.denominator
                self.assertLess(abs(actual-expected),Decimal('1e-58'))
                self.assertEqual(state,before)
                self.assertGreaterEqual(fraction,Fraction(1,4));self.assertLessEqual(fraction,1)

    def test_empty_zero_denominator_and_zero_level_are_distinct(self):
        for state,reason in ((authored(),'no_supplied_levels'),(authored([0,0]),'zero_quantity_denominator'),
                             (authored([0,1]),'zero_quantity_level')):
            out=calculate(state);self.assertEqual(out['reason'],reason);self.assertIsNone(out['hhi'])

    def test_extreme_quantities_are_exact_without_overflow(self):
        q=2**64-1
        self.assertEqual(exact(calculate(authored([q]*20,[q]*20),depth=20)['hhi']),Fraction(1,40))
        out=calculate(authored([q,1]),'bid')
        self.assertEqual(exact(out['hhi']),Fraction(q*q+1,(q+1)**2))
        self.assertIsNone(calculate(authored([q+1]))['hhi'])

    def test_malformed_levels_and_budgets_fail_closed(self):
        for q in ('1\n','-1','01','1.0',True,None,'9'*100):
            s=authored([1]);s['book']['bids'][0]['quantity']=q
            self.assertEqual(calculate(s)['reason'],'invalid_supplied_levels')
        for s in (authored([1]*21),authored([1,2])):
            if len(s['book']['bids'])==2:s['book']['bids'][1]['price_ticks']='100'
            self.assertIsNone(calculate(s)['hhi'])
        for side,depth in (('sell',1),('both',0),('both',21),('both',True)):
            with self.assertRaises(ValueError):calculate(authored([1]),side,depth)

    def test_provenance_and_unavailable_source_never_upgraded(self):
        s=authored([1]);out=calculate(s)
        self.assertEqual(out['source']['parents']['dataset'],'independent-concentration-test')
        self.assertEqual(out['source']['origin'],'HISTORICAL_SYNTHETIC')
        self.assertIn('NOT_ORIGINAL_REQUIREMENT_ACCEPTANCE',out['contract_status'])
        s['origin']='UNAVAILABLE';out=calculate(s)
        self.assertEqual(out['reason'],'source_unavailable');self.assertIsNone(out['hhi'])


class ConcentrationAPI(unittest.TestCase):
    def setUp(self):
        self.env=patch.dict('os.environ',{k:'0' for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED')});self.env.start();self.addCleanup(self.env.stop)
        self.app=create_app();self.c=TestClient(self.app,base_url='http://127.0.0.1:8787')

    def test_versioned_readonly_endpoint_and_state_are_consistent(self):
        before=self.app.state.native.replay.canonical()
        state=self.c.get('/api/v1/state').json()
        out=self.c.get('/api/v2/research/concentration').json()
        self.assertEqual(out,state['research_metrics']['concentration'])
        self.assertEqual(out['schema'],'gig.research.supplied_depth_concentration.v1')
        self.assertEqual(before,self.app.state.native.replay.canonical())

    def test_query_contract_and_duplicate_keys(self):
        for query in ('side=other','depth=0','depth=21','depth=x','side=bid&side=ask','unknown=1'):
            self.assertEqual(self.c.get('/api/v2/research/concentration?'+query).status_code,400)
        self.assertEqual(self.c.get('/api/v2/research/concentration?side=bid&depth=1').status_code,200)

    def test_gated_live_mode_does_not_fabricate_depth(self):
        self.app.state.native.control('mode','LIVE')
        out=self.c.get('/api/v2/research/concentration').json()
        self.assertEqual(out['status'],'UNAVAILABLE');self.assertIsNone(out['hhi'])
