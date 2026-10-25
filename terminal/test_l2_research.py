"""Independent hand/integer/Fraction oracles and causal/adversarial controls."""
from fractions import Fraction
import random,unittest
from .l2_research import ResearchWindow,bounded

def book(bid=100,ask=102,bq=10,aq=30):
    return {'bids':[{'price_ticks':str(bid),'quantity':str(bq)}] if bid else [],
            'asks':[{'price_ticks':str(ask),'quantity':str(aq)}] if ask else []}
def quote(w,now,ordinal,**kwargs):w.observe({'kind':'snapshot' if ordinal==0 else 'update'},book(**kwargs),now,ordinal)
def trade(w,now,ordinal,side='buy',price=102,qty=2):
    w.observe({'kind':'trades','trades':[{'price_ticks':str(price),'quantity':str(qty),'side':side}]},None,now,ordinal)
def value(result,name):
    f=result['metrics'][name]['value'];return None if f is None else Fraction(int(f['numerator']),int(f['denominator']))

class Research(unittest.TestCase):
    def test_native_formula_equivalent_top_metrics(self):
        w=ResearchWindow();quote(w,0,0);r=w.view(0)
        for name,expected in [('spread',2),('relative_spread',Fraction(2,101)),('depth_imbalance',Fraction(-1,2)),('microprice',Fraction(201,2)),('weighted_midprice',Fraction(201,2)),('bid_top_concentration',1)]:
            self.assertEqual(value(r,name),expected,name)
    def test_ofi_and_matched_level_dynamics_hand_reference(self):
        w=ResearchWindow();quote(w,0,0);quote(w,1_000_000_000,1,bq=15,aq=25)
        r=w.view(1_000_000_000);self.assertEqual(value(r,'ofi'),10)
        self.assertEqual(value(r,'matched_level_replenishment'),5);self.assertEqual(value(r,'matched_level_depletion'),5)
        quote(w,2_000_000_000,2,bid=101,ask=103,bq=7,aq=9);r=w.view(2_000_000_000)
        self.assertEqual(value(r,'ofi'),42);self.assertEqual(value(r,'event_sampled_realized_variance'),Fraction(1,10201))
        self.assertEqual(value(r,'matched_level_replenishment'),5);self.assertEqual(value(r,'matched_level_depletion'),5)
    def test_trade_intensity_side_counts_and_unverified_effective_spread(self):
        w=ResearchWindow();quote(w,0,0);trade(w,1_000_000_000,1);trade(w,2_000_000_000,2,'sell',100,1)
        r=w.view(2_000_000_000);self.assertEqual(value(r,'trade_intensity_per_second'),1)
        self.assertEqual(value(r,'reported_side_net_quantity'),1);self.assertIsNone(value(r,'effective_spread'))
    def test_future_quote_cannot_reclassify_trade(self):
        w=ResearchWindow(aggressor_side_confirmed=True);quote(w,0,0);trade(w,1,1,price=102)
        quote(w,2,2,bid=200,ask=202);r=w.view(2)
        self.assertEqual(value(r,'effective_spread'),2)
        self.assertNotEqual(value(r,'effective_spread'),2*(102-201))
    def test_same_timestamp_uses_physical_capture_order(self):
        w=ResearchWindow(aggressor_side_confirmed=True);quote(w,0,0);trade(w,0,1);quote(w,0,2,bq=15,aq=25)
        self.assertEqual(value(w.view(0),'ofi'),10);self.assertEqual(value(w.view(0),'effective_spread'),2)
        self.assertIsNone(value(w.view(0),'trade_intensity_per_second'))
    def test_stale_missing_crossed_quotes_unavailable(self):
        w=ResearchWindow(aggressor_side_confirmed=True);quote(w,0,0);trade(w,10_000_000_001,1)
        self.assertIsNone(value(w.view(10_000_000_001),'effective_spread'))
        quote(w,10_000_000_002,2,bid=None);self.assertIsNone(value(w.view(10_000_000_002),'ofi'))
        quote(w,10_000_000_003,3,bid=103,ask=102);self.assertIsNone(value(w.view(10_000_000_003),'microprice'))
    def test_snapshot_resets_old_source_history(self):
        w=ResearchWindow();quote(w,0,0);trade(w,1,1)
        w.observe({'kind':'snapshot'},book(),2,2);r=w.view(3)
        self.assertEqual(r['trades'],0);self.assertIsNone(value(r,'ofi'));self.assertEqual(r['effective_start_receive_ns'],'2')
    def test_history_bound_signals_incomplete_rates(self):
        w=ResearchWindow();quote(w,0,0)
        for i in range(1,131):trade(w,i,i)
        r=w.view(131);self.assertEqual(r['trades'],128);self.assertFalse(r['trade_coverage_complete'])
        self.assertIsNone(value(r,'trade_intensity_per_second'));self.assertIsNone(value(r,'reported_side_net_quantity'))
    def test_ordering_and_inexact_inputs_reject(self):
        w=ResearchWindow();quote(w,5,0)
        with self.assertRaises(ValueError):quote(w,4,1)
        with self.assertRaises(ValueError):quote(w,5,0)
        with self.assertRaises(ValueError):w.view(4)
        bad=book();bad['bids'][0]['quantity']=1.5
        with self.assertRaises(ValueError):w.observe({'kind':'update'},bad,6,1)
        self.assertEqual(value(w.view(6),'depth_imbalance'),Fraction(-1,2))
    def test_numeric_capacity_and_missing_initial_state(self):
        with self.assertRaises(ArithmeticError):bounded(Fraction(1,1<<1025))
        w=ResearchWindow();self.assertEqual(w.view(1)['status'],'INSUFFICIENT');self.assertIsNone(value(w.view(1),'microprice'))
        quote(w,2,0,bid=2**63-2,ask=2**63-1,bq=2**64-1,aq=2**64-1)
        self.assertEqual(value(w.view(2),'microprice'),Fraction(2**64-3,2))
    def test_independent_integer_ofi_oracle_two_thousand_candidates(self):
        rng=random.Random(221);w=ResearchWindow();quote(w,0,0)
        old=(100,102,10,30);total=0
        for i in range(1,2001):
            if i%100==0:
                w=ResearchWindow();quote(w,i,0);old=(100,102,10,30);total=0
                continue
            new=(rng.randrange(90,100),rng.randrange(101,110),rng.randrange(1,100),rng.randrange(1,100))
            b,a,bq,aq=new;pb,pa,pbq,paq=old
            total+=(bq-pbq if b==pb else bq if b>pb else -pbq)
            total+=(-aq+paq if a==pa else -aq if a<pa else paq)
            quote(w,i,i, bid=b,ask=a,bq=bq,aq=aq)
            self.assertEqual(value(w.view(i),'ofi'),total);old=new
    def test_historical_trade_snapshot_not_counted_as_current_arrival(self):
        w=ResearchWindow();quote(w,0,0)
        w.observe({'kind':'trades','historical_snapshot':True,'trades':[{'price_ticks':'102','quantity':'1','side':'buy'}]},None,1,1)
        self.assertEqual(w.view(2)['trades'],0)

if __name__=='__main__':unittest.main()
