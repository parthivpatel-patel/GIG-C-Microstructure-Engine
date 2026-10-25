"""Independent arbitrary-precision check of actual installed native aggregate binding."""
from fractions import Fraction
import random
import unittest
import gig_microstructure as gig
from terminal.providers.kraken import KrakenBookAdapter, ProviderError
from terminal.providers.test_kraken import book, crc_reference


def checked(value):return gig._checked(value)
def pair(value):return Fraction(int(value['numerator']),int(value['denominator']))

class NativeDepth(unittest.TestCase):
    def test_precision_rollback_and_exact_boundaries(self):
        b=gig._native.AggregateDepth(32,1048576)
        self.assertIsNone(checked(b.snapshot([{'price_ticks':'100','quantity':'30'}],[{'price_ticks':'101','quantity':'10'}],None)))
        self.assertEqual(pair(checked(b.state())['metrics']['microprice']),Fraction(403,4))
        prior=checked(b.state())
        for qty in ('1.0','01','-0','18446744073709551616'):
            with self.assertRaises(gig.EngineError):checked(b.update([{'price_ticks':'100','quantity':qty}],[],None))
            self.assertEqual(checked(b.state()),prior)
        n='18446744073709551615'
        checked(b.snapshot([{'price_ticks':'9223372036854775806','quantity':n}],[{'price_ticks':'9223372036854775807','quantity':n}],None))
        self.assertEqual(pair(checked(b.state())['metrics']['microprice']),Fraction(18446744073709551613,2))
        checked(b.snapshot([],[], '7'));before=checked(b.state())
        with self.assertRaises(gig.EngineError) as failure:checked(b.update([],[], '6'))
        self.assertEqual(failure.exception.code_name,'sequence_regression');self.assertEqual(checked(b.state()),before)

    def test_seeded_independent_level_map(self):
        rng=random.Random(911);b=gig._native.AggregateDepth(32,1048576);checked(b.snapshot([],[], '0'));reference=[{},{}]
        for sequence in range(1,1001):
            side=rng.randrange(2);p=(100-rng.randrange(20)) if side==0 else (101+rng.randrange(20));q=rng.randrange(100)
            update={'price_ticks':str(p),'quantity':str(q)}
            checked(b.update([update] if side==0 else [],[update] if side==1 else [],str(sequence)))
            if q:reference[side][p]=q
            else:reference[side].pop(p,None)
            value=checked(b.state())
            for i,key in enumerate(('bids','asks')):
                expected=[{'price_ticks':str(p),'quantity':str(q)} for p,q in sorted(reference[i].items(),reverse=i==0)]
                self.assertEqual(value[key],expected)
            bids,asks=map(lambda x:sum(x.values()),reference)
            self.assertEqual(pair(value['metrics']['bid_depth']),bids)
            self.assertEqual(pair(value['metrics']['ask_depth']),asks)
            if bids+asks:self.assertEqual(pair(value['metrics']['depth_imbalance']),Fraction(bids-asks,bids+asks))

    def test_authored_provider_native_integration(self):
        b=gig._native.AggregateDepth(32,1048576)
        def apply(snapshot,bids,asks,sequence):checked((b.snapshot if snapshot else b.update)(bids,asks,sequence))
        provider=KrakenBookAdapter(apply)
        provider.feed(book(),1)
        self.assertEqual(checked(b.state())['bids'],[{'price_ticks':'10000','quantity':'200000000'}])
        provider.feed(book([('100.00','4.00000000')],[('101.00','0.00000000')],'update',crc_reference('10000400000000')),2)
        self.assertEqual(checked(b.state())['asks'],[])
        before=checked(b.state())
        with self.assertRaises(ProviderError):provider.feed(book(checksum=0),3)
        self.assertEqual(checked(b.state()),before)

if __name__=='__main__':unittest.main()
