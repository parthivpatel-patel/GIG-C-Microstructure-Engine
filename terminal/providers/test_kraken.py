"""Authored data only; reference CRC uses independent polynomial implementation."""
import json
import unittest
from copy import deepcopy
from decimal import Decimal
from .kraken import KrakenBookAdapter, ProviderError, Permission, decimal_wire, timestamp_ns


def crc_reference(text):
    crc = 0xffffffff
    for byte in text.encode('ascii'):
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xedb88320 if crc & 1 else 0)
    return crc ^ 0xffffffff


def book(bids=None, asks=None, kind='snapshot', checksum=None):
    bids = bids if bids is not None else [('100.00', '2.00000000')]
    asks = asks if asks is not None else [('101.00', '3.00000000')]
    if checksum is None:
        checksum = crc_reference(''.join(v.replace('.', '').lstrip('0') for side in (sorted(asks, key=lambda x: Decimal(x[0])), sorted(bids, key=lambda x: Decimal(x[0]), reverse=True)) for level in side for v in level))
    return json.dumps({'channel': 'book', 'type': kind, 'data': [{'symbol': 'BTC/USD', 'bids': [{'price': p, 'qty': q} for p, q in bids], 'asks': [{'price': p, 'qty': q} for p, q in asks], 'checksum': checksum}]})


class ProviderContracts(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.a = KrakenBookAdapter(lambda **kw: self.calls.append(kw))

    def refuse(self, raw, code=None, now=2):
        old_b, old_a, n = deepcopy(self.a.bids), deepcopy(self.a.asks), len(self.calls)
        with self.assertRaises(ProviderError) as c:
            self.a.feed(raw, now)
        if code:
            self.assertEqual(c.exception.code, code)
        self.assertEqual((self.a.bids, self.a.asks, len(self.calls)), (old_b, old_a, n))

    def test_exact_units(self):
        self.assertEqual(decimal_wire('100.01', maximum=2**63-1, scale=100), ('10001', '100.01'))
        self.assertEqual(decimal_wire('0.00000001', maximum=2**64-1, scale=10**8)[0], '1')
        for value in ['1.001', '-0', 'NaN', '1e5', '00.1']:
            with self.assertRaises(ProviderError): decimal_wire(value, maximum=2**63-1, scale=100)
        with self.assertRaises(ProviderError): decimal_wire('92233720368547758.08', maximum=2**63-1, scale=100)
        self.assertEqual(decimal_wire('184467440737.09551615', maximum=2**64-1, scale=10**8)[0], str(2**64-1))

    def test_snapshot_native_and_origin(self):
        result = self.a.feed(book(), 1)
        self.assertEqual(result['origin'], 'HISTORICAL_SYNTHETIC')
        self.assertIsNone(result['source_sequence'])
        self.assertEqual(self.calls[0], {'snapshot': True, 'bids': [{'price_ticks': '10000', 'quantity': '200000000'}], 'asks': [{'price_ticks': '10100', 'quantity': '300000000'}], 'sequence': None})

    def test_absolute_update_and_delete(self):
        self.a.feed(book(), 1)
        # Candidate state has a changed bid quantity and no ask.
        checksum = crc_reference('10000'+'400000000')
        result = self.a.feed(book([('100.00','4.00000000')], [('101.00','0.00000000')], 'update', checksum), 2)
        self.assertEqual(result['kind'], 'update')
        self.assertEqual(self.a.asks, {})
        self.assertEqual(self.calls[-1]['asks'], [{'price_ticks':'10100','quantity':'0'}])

    def test_replacement_snapshot_has_no_zero_deletes(self):
        self.a.feed(book(), 1)
        self.a.feed(book([('99','1')], [('102','1')]), 2)
        self.assertTrue(self.calls[-1]['snapshot'])
        self.assertTrue(all(x['quantity'] != '0' for side in ('bids','asks') for x in self.calls[-1][side]))

    def test_snapshot_required(self):
        self.refuse(book(kind='update'), 'snapshot_required')

    def test_crc_failure_state_atomic(self):
        self.a.feed(book(), 1)
        self.refuse(book(checksum=123), 'checksum_mismatch')
        self.assertEqual(self.a.state, 'GAP_DETECTED')
        self.refuse(book(kind='update'), 'snapshot_required', 3)
        self.a.feed(book(), 4)
        self.assertEqual(self.a.state, 'LIVE')

    def test_native_failure_atomic(self):
        self.a.apply_native = lambda **_: (_ for _ in ()).throw(MemoryError())
        self.refuse(book(), 'native_rejected')

    def test_duplicate_is_explicit(self):
        raw = book(); self.a.feed(raw, 1)
        self.assertEqual(self.a.feed(raw, 2)['kind'], 'duplicate')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.a.last_receive_ns, 1)

    def test_unknown_symbol(self):
        self.refuse(book().replace('BTC/USD','ETH/USD'), 'symbol_mismatch')

    def test_duplicate_levels(self):
        self.refuse(book([('100','2'),('100.00','2')]), 'duplicate_level')

    def test_zero_negative_snapshot(self):
        self.refuse(book([('100','0')]), 'zero_snapshot_level')
        self.refuse(book([('100','-1')]), 'decimal_grammar')
        self.refuse(book([('0','1')]), 'zero_price')

    def test_limits_and_unsupported(self):
        self.refuse('x'*65537, 'payload_limit')
        self.refuse('[]', 'object_required')
        self.refuse('{"a":1,"a":2}', 'duplicate_json_key')
        self.refuse('{"channel":"ticker"}', 'unsupported_message')
        self.refuse(book([('100','1')]*101), 'update_budget')

    def test_large_checksum_exponent_rejected_before_int(self):
        self.refuse(book().replace('"checksum": ', '"checksum": 1e99999, "discard": '), 'book_fields')
        raw = json.loads(book()); raw['data'][0]['checksum'] = 'oversize'
        self.refuse(json.dumps(raw), 'checksum_field')
        self.refuse(book().replace(str(json.loads(book())['data'][0]['checksum']), '1e99999'), 'checksum_field')

    def test_subscription_and_heartbeat(self):
        self.a.connect()
        self.assertEqual(self.a.state,'CONNECTING')
        ack = '{"method":"subscribe","success":true,"result":{"channel":"book","symbol":"BTC/USD"}}'
        self.a.feed(ack,1); self.assertEqual(self.a.state,'SYNCHRONIZING')
        self.a.feed(book(),2)
        self.assertEqual(self.a.status(10_000_000_003)['state'],'STALE')
        self.a.feed('{"channel":"heartbeat"}',10_000_000_004)
        # A heartbeat alone cannot restore stale book publication.
        self.assertEqual(self.a.state,'STALE')

    def test_disconnect_requires_new_snapshot(self):
        self.a.feed(book(),1);self.a.disconnected()
        self.assertEqual(self.a.bids,{})
        self.refuse(book(kind='update'),'snapshot_required')
        self.assertEqual([self.a.recovery_delay() for _ in range(8)], [1,2,4,8,16,30,30,30])

    def test_timestamp_exact_and_invalid(self):
        self.assertEqual(timestamp_ns('1970-01-01T00:00:00.000000001Z'),'1')
        self.assertEqual(timestamp_ns('2000-02-29T12:00:00.123456789Z'),'951825600123456789')
        for value in ['2019-02-29T00:00:00Z','2020-01-01T24:00:00Z','2020-01-01T00:00:60Z','2020-01-01T00:00:00.1234567890Z','bad']:
            with self.assertRaises(ProviderError):timestamp_ns(value)

    def test_clock_regression(self):
        self.a.feed(book(),5)
        self.refuse(book(), 'receive_clock_regression',4)

    def test_trade_precision_dedup_and_batch_atomicity(self):
        trade={'symbol':'BTC/USD','side':'buy','price':'100.01','qty':'0.00000001','trade_id':1,'timestamp':'2026-10-25T12:34:56.123456789Z'}
        raw=json.dumps({'channel':'trade','type':'update','data':[trade]})
        out=self.a.feed(raw,1)
        self.assertEqual(out['trades'][0]['quantity'],'1')
        self.assertEqual(self.a.feed(raw,2)['trades'],[])
        bad=dict(trade);bad['trade_id']=2;bad['qty']='0'
        old=list(self.a.trades)
        self.refuse(json.dumps({'channel':'trade','type':'update','data':[dict(trade,trade_id=3),bad]}),'zero_trade',3)
        self.assertEqual(list(self.a.trades),old)

    def test_depth_trim_explicit_native_deletion(self):
        bids=[(str(100-i),'1') for i in range(10)]
        self.a.feed(book(bids,[]),1)
        after=[('101','1')]+bids[:9]
        crc=crc_reference(''.join(p+q for p,q in after))
        self.a.feed(book([('101','1')],[],'update',crc),2)
        self.assertIn({'price_ticks':'9100','quantity':'0'},self.calls[-1]['bids'])
        self.assertEqual(len(self.a.bids),10)

    def test_permission_gate(self):
        with self.assertRaises(ProviderError):Permission().require_live()
        with self.assertRaises(ProviderError):Permission(docs_reviewed=True,private_display_approved=True,cloud_processing_approved=True).require_live()
        Permission(True,True,True,False,'externally-reviewed-reference').require_live()


if __name__=='__main__':unittest.main()
