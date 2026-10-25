"""Authored candidate status observations; neither official nor live evidence."""
import json,unittest
from .kraken import KrakenBookAdapter,ProviderError
from .test_kraken import book
STATUS={'channel':'status','type':'update','data':[{'api_version':'v2','connection_id':123,'system':'online','version':'2.0.8'}]}
class Admin(unittest.TestCase):
    def setUp(self):self.calls=[];self.a=KrakenBookAdapter(lambda **x:self.calls.append(x))
    def test_online_admin_preserves_wire_identity_without_book_mutation(self):
        self.a.connect();r=self.a.feed(json.dumps(STATUS),0)
        self.assertEqual(r['connection_id'],'123');self.assertEqual(self.calls,[])
        self.assertNotEqual(self.a.state,'LIVE');self.a.feed(book(),1)
        self.a.feed(json.dumps(STATUS),2);self.assertEqual(len(self.calls),1);self.assertEqual(self.a.state,'LIVE')
    def test_non_online_state_invalidates_trust_without_native_reset(self):
        self.a.feed(book(),0)
        p=json.loads(json.dumps(STATUS));p['data'][0]['system']='maintenance'
        with self.assertRaisesRegex(ProviderError,'not_online'):self.a.feed(json.dumps(p),1)
        self.assertEqual(len(self.calls),1);self.assertEqual(self.a.state,'GAP_DETECTED')
    def test_unknown_fields_and_invalid_identity_rejected(self):
        cases=[{**STATUS,'extra':1}, {**STATUS,'type':'snapshot'}]
        for identity in (True,-1,'123',2**64):
            p=json.loads(json.dumps(STATUS));p['data'][0]['connection_id']=identity;cases.append(p)
        for case in cases:
            with self.assertRaises(ProviderError):self.a.feed(json.dumps(case),0)
        self.assertEqual(self.calls,[])
    def test_status_observation_advances_receive_order_check(self):
        self.a.feed(json.dumps(STATUS),5)
        with self.assertRaisesRegex(ProviderError,'receive_clock_regression'):self.a.feed(book(),4)
    def test_trade_unknown_fields_and_order_type_are_explicit(self):
        t={'symbol':'BTC/USD','side':'buy','trade_id':1,'price':'101','qty':'1','timestamp':'2026-01-01T00:00:00Z'}
        for change in ({'undocumented':True},{'ord_type':'unreviewed'}):
            with self.assertRaises(ProviderError):self.a.feed(json.dumps({'channel':'trade','type':'update','data':[{**t,**change}]}),0)
        r=self.a.feed(json.dumps({'channel':'trade','type':'update','data':[{**t,'ord_type':'limit'}]}),1)
        self.assertEqual(r['trades'][0]['source_order_type'],'limit')
    def test_heartbeat_extra_semantics_are_not_silently_discarded(self):
        with self.assertRaisesRegex(ProviderError,'heartbeat_fields'):self.a.feed('{"channel":"heartbeat","book_reset":true}',0)

if __name__=='__main__':unittest.main()
