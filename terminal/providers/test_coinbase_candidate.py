"""Authored protocol assumptions only; independent native expected levels, no network."""
import json,unittest
import gig_microstructure as gig
from .coinbase_candidate import CoinbaseCandidate
from .kraken import ProviderError

SNAP={'type':'snapshot','product_id':'BTC-USD','bids':[['100.00','2.00000000']],'asks':[['101.00','3.00000000']]}
UPDATE={'type':'l2update','product_id':'BTC-USD','time':'2026-01-01T00:00:00.000000001Z','changes':[['buy','100.00','4.00000000']]}
class Candidate(unittest.TestCase):
    def setUp(self):
        self.book=gig._native.AggregateDepth(256,1048576)
        def apply(**e):gig._checked((self.book.snapshot if e['snapshot'] else self.book.update)(e['bids'],e['asks'],e['sequence']))
        self.adapter=CoinbaseCandidate(apply)
    def feed(self,p,n=1):return self.adapter.feed(json.dumps(p),n)
    def test_snapshot_and_absolute_native_update(self):
        self.feed(SNAP);r=self.feed(UPDATE,2)
        self.assertIsNone(r['native_event']['sequence']);self.assertEqual(gig._checked(self.book.state())['bids'],[{'price_ticks':'10000000000','quantity':'400000000'}])
    def test_global_sequence_not_assumed_contiguous_l2(self):
        self.feed(SNAP);r=self.feed({**UPDATE,'sequence':1000000},2);self.assertEqual(r['source_sequence'],'1000000')
        self.assertEqual(self.adapter.status(2)['sequence_continuity'],'unverified_global_scope_not_a_contiguous_L2_sequence')
    def test_missing_snapshot_and_wrong_venue_product(self):
        for p in (UPDATE,{**SNAP,'product_id':'ETH-USD'}):
            with self.assertRaises(ProviderError):self.feed(p)
        self.assertFalse(gig._checked(self.book.state())['initialized'])
    def test_cancel_is_absolute_level_deletion_not_order_identity(self):
        self.feed(SNAP);self.feed({**UPDATE,'changes':[['buy','100','0']]},2)
        self.assertEqual(gig._checked(self.book.state())['bids'],[])
    def test_duplicate_price_and_crossing_fail_atomically(self):
        self.feed(SNAP)
        for i,(changes,code) in enumerate((([['buy','100','1'],['buy','100.00','2']],'duplicate_level'),([['buy','102','1']],'crossed'))):
            old=gig._checked(self.book.state())
            with self.assertRaisesRegex(ProviderError,code):self.feed({**UPDATE,'changes':changes},2+i*2)
            self.assertEqual(gig._checked(self.book.state()),old)
            self.feed(SNAP,3+i*2)
    def test_native_failure_has_no_candidate_commit(self):
        self.adapter.apply=lambda **_:(_ for _ in ()).throw(MemoryError())
        with self.assertRaisesRegex(ProviderError,'native_rejected'):self.feed(SNAP)
        self.assertEqual(self.adapter.bids,{})
    def test_maker_side_is_not_aggressor_side(self):
        p={'type':'match','product_id':'BTC-USD','side':'sell','trade_id':1,'price':'101','size':'1','time':'2026-01-01T00:00:00Z'}
        r=self.feed(p);self.assertIsNone(r['trade']['aggressor_side']);self.assertEqual(r['trade']['reported_side_role'],'maker_candidate_unverified')
        self.assertTrue(self.feed(p,2)['duplicate'])
    def test_heartbeat_cannot_keep_book_fresh(self):
        self.feed(SNAP);self.feed({'type':'heartbeat','product_id':'BTC-USD'},10_000_000_001)
        self.assertEqual(self.adapter.status(10_000_000_002)['state'],'STALE')
        with self.assertRaises(ProviderError):self.feed(UPDATE,10_000_000_003)
    def test_limits_precision_unknowns_and_explicit_resync(self):
        for p in ({**SNAP,'bids':[['100.000000001','1']]},{**SNAP,'asks':[['101','18446744073709551616']]},{'type':'arbitrary','product_id':'BTC-USD'}):
            with self.assertRaises(ProviderError):self.feed(p)
        self.feed(SNAP,2);self.adapter.disconnected()
        with self.assertRaises(ProviderError):self.feed(UPDATE,3)
    def test_unknown_fields_and_malformed_payload_do_not_commit(self):
        self.feed(SNAP);before=gig._checked(self.book.state())
        with self.assertRaisesRegex(ProviderError,'unknown_fields'):self.feed({**UPDATE,'undocumented_state':'x'},2)
        self.assertEqual(gig._checked(self.book.state()),before)
        with self.assertRaises(ProviderError):self.adapter.feed('x'*65537,3)
        with self.assertRaisesRegex(ProviderError,'unsupported'):self.feed({'type':[]},4)
    def test_heartbeat_reference_preserved_and_invalid_reference_rejected(self):
        r=self.feed({'type':'heartbeat','product_id':'BTC-USD','last_trade_id':123,'sequence':9})
        self.assertEqual(r['last_trade_id'],'123');self.assertEqual(r['source_sequence'],'9')
        with self.assertRaises(ProviderError):self.feed({'type':'heartbeat','product_id':'BTC-USD','last_trade_id':True},2)
    def test_eth_is_separate_configured_native_book(self):
        a=CoinbaseCandidate(lambda **_:None,symbol='ETH-USD');a.feed(json.dumps({**SNAP,'product_id':'ETH-USD'}),1)
        self.assertEqual(self.adapter.bids,{})
        self.assertFalse(a.status(1)['live_verified'])

if __name__=='__main__':unittest.main()
