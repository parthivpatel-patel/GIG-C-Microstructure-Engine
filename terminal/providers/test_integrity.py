"""Independent authored regressions for trust/freshness boundaries."""
import json
import unittest
from .kraken import KrakenBookAdapter, ProviderError
from .test_kraken import book

class Integrity(unittest.TestCase):
    def setUp(self):
        self.calls=[];self.a=KrakenBookAdapter(lambda **x:self.calls.append(x),stale_ns=10)
    def test_heartbeats_do_not_extend_depth_freshness(self):
        self.a.feed(book(),1)
        self.a.feed('{"channel":"heartbeat"}',10)
        self.assertEqual(self.a.status(12)['state'],'STALE')
    def test_trades_do_not_extend_depth_freshness(self):
        self.a.feed(book(),1)
        trade={'channel':'trade','type':'update','data':[{'symbol':'BTC/USD','side':'buy','trade_id':1,'price':'101','qty':'1','timestamp':'2026-01-01T00:00:00Z'}]}
        self.a.feed(json.dumps(trade),10)
        self.assertEqual(self.a.status(12)['state'],'STALE')
    def test_crossed_candidate_never_commits_native(self):
        self.a.feed(book(),1)
        with self.assertRaisesRegex(ProviderError,'crossed_book'):self.a.feed(book([('102','1')],[('101','1')]),2)
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.a.state,'GAP_DETECTED')
    def test_invalid_receive_clock_invalidates_trust(self):
        self.a.feed(book(),5)
        with self.assertRaisesRegex(ProviderError,'receive_clock_regression'):self.a.feed(book(),4)
        self.assertEqual(self.a.state,'GAP_DETECTED')
    def test_extreme_numeric_exponent_is_structured_and_invalidates_trust(self):
        self.a.feed(book(),1)
        with self.assertRaisesRegex(ProviderError,'malformed_json'):
            self.a.feed('{"checksum":1e999999999999999999999999999999}',2)
        self.assertEqual(self.a.state,'GAP_DETECTED')

    def test_late_trade_ack_does_not_invalidate_a_valid_book(self):
        self.a.feed(book(),1)
        self.a.feed('{"method":"subscribe","success":true,"result":{"channel":"trade","symbol":"BTC/USD"}}',2)
        self.assertEqual(self.a.state,'LIVE')

    def test_eth_is_explicit_configuration_not_cross_symbol_merge(self):
        a=KrakenBookAdapter(lambda **_:None,symbol='ETH/USD')
        a.feed(book().replace('BTC/USD','ETH/USD'),1)
        with self.assertRaisesRegex(ProviderError,'symbol_mismatch'):a.feed(book(),2)

if __name__=='__main__':unittest.main()
