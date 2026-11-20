"""Offline official depth/CRC contracts; authored books and real native callbacks."""
import copy
import json
import unittest
from decimal import Decimal

import gig_microstructure as gig
from .kraken import (BOOK_DEPTH_SESSION_PROFILE, BOOK_SESSION_PROFILE,
                     KrakenBookAdapter, ProviderError)
from .test_kraken import crc_reference


def wire(bids, asks, *, kind='snapshot', final=None, checksum=None):
    """Independent polynomial CRC over final top ten, never all subscribed levels."""
    if checksum is None:
        final_bids, final_asks = (bids, asks) if final is None else final
        text = ''.join(value.replace('.', '').lstrip('0')
                       for side in (sorted(final_asks, key=lambda x: Decimal(x[0]))[:10],
                                    sorted(final_bids, key=lambda x: Decimal(x[0]), reverse=True)[:10])
                       for level in side for value in level)
        checksum = crc_reference(text)
    return json.dumps({'channel': 'book', 'type': kind, 'data': [{
        'symbol': 'BTC/USD', 'bids': [{'price': p, 'qty': q} for p, q in bids],
        'asks': [{'price': p, 'qty': q} for p, q in asks], 'checksum': checksum}]})


def levels(depth):
    return ([(str(1000-i), '1') for i in range(depth)],
            [(str(2000+i), '2') for i in range(depth)])


class DepthSession(unittest.TestCase):
    def adapter(self, depth=25, *, native_limit=256):
        native = gig._native.AggregateDepth(native_limit, 1048576)
        calls = []
        def apply(**event):
            gig._checked((native.snapshot if event['snapshot'] else native.update)(
                event['bids'], event['asks'], event['sequence']))
            calls.append(copy.deepcopy(event))
        adapter = KrakenBookAdapter(apply, depth=depth, ordered_updates=True,
            book_session_profile=BOOK_DEPTH_SESSION_PROFILE, book_request_id=100)
        adapter.connect()
        return adapter, native, calls

    def ack(self, adapter, now=1, **result_changes):
        result = {'channel': 'book', 'symbol': adapter.symbol,
                  'depth': adapter.depth, 'snapshot': True}
        result.update(result_changes)
        return adapter.feed(json.dumps({'method': 'subscribe', 'success': True,
            'req_id': adapter.book_subscription_request()['req_id'], 'result': result}), now)

    def native_state(self, native):
        return gig._checked(native.state())

    def test_depths_are_opt_in_and_defaults_and_v1_remain_ten(self):
        for profile in (None, BOOK_SESSION_PROFILE):
            for depth in (25, 100):
                with self.subTest(profile=profile, depth=depth), self.assertRaises(ProviderError):
                    KrakenBookAdapter(lambda **_: None, depth=depth,
                        book_session_profile=profile, book_request_id=100 if profile else None)
        for depth in (10, 25, 100):
            a, _, _ = self.adapter(depth)
            self.assertEqual(a.book_subscription_request()['params']['depth'], depth)
            self.assertFalse(a.capabilities['profile_verified'])
        legacy = KrakenBookAdapter(lambda **_: None)
        self.assertEqual(legacy.depth, 10)
        self.assertFalse(legacy.ordered_updates)
        self.assertIsNone(legacy.book_session_profile)

    def test_configuration_rejects_unimplemented_depths_and_unordered_profile(self):
        for depth in (True, 25.0, '25', 0, 11, 500, 1000):
            with self.subTest(depth=depth), self.assertRaises(ProviderError):
                self.adapter(depth)
        with self.assertRaisesRegex(ProviderError, 'ordered_updates_required'):
            KrakenBookAdapter(lambda **_: None, depth=25,
                book_session_profile=BOOK_DEPTH_SESSION_PROFILE, book_request_id=100)

    def test_ack_binds_exact_depth_and_no_snapshot_is_inferred(self):
        a, native, calls = self.adapter(100)
        with self.assertRaisesRegex(ProviderError, 'book_ack_options'):
            self.ack(a, depth=25)
        self.assertFalse(self.native_state(native)['initialized'])
        self.assertEqual(calls, [])
        a.connect()
        receipt = self.ack(a, 2)
        self.assertEqual(receipt['depth'], 100)
        self.assertEqual(receipt['book_session_profile'], BOOK_DEPTH_SESSION_PROFILE)
        self.assertEqual(a.state, 'SYNCHRONIZING')
        self.assertFalse(self.native_state(native)['initialized'])

    def test_deep_snapshot_preserves_all_native_levels_and_top_ten_crc_scope(self):
        for depth in (25, 100):
            a, native, calls = self.adapter(depth)
            self.ack(a)
            bids, asks = levels(depth)
            r = a.feed(wire(bids, asks), 2)
            state = self.native_state(native)
            self.assertEqual(len(state['bids']), depth)
            self.assertEqual(len(state['asks']), depth)
            self.assertEqual(state['bids'], [{'price_ticks': str(int(p)*100),
                'quantity': '100000000'} for p, _ in bids])
            self.assertEqual(r['subscribed_depth'], depth)
            self.assertEqual(r['checksum_depth'], 10)
            self.assertEqual(r['checksum_scope'], 'top_10_per_side_only')
            self.assertEqual(r['retained_levels'], {'bids': depth, 'asks': depth})
            self.assertIsNone(r['source_sequence'])
            self.assertEqual(len(calls), 1)

    def test_worst_case_depth_hundred_diff_commits_two_hundred_native_changes(self):
        a, native, calls = self.adapter(100)
        self.ack(a)
        bids, asks = levels(100)
        a.feed(wire(bids, asks), 2)
        better = [(str(1200-i), '3') for i in range(100)]
        better_asks = [(str(1800+i), '4') for i in range(100)]
        a.feed(wire(better, better_asks, kind='update', final=(better, better_asks)), 3)
        for side in ('bids', 'asks'):
            self.assertEqual(len(calls[-1][side]), 200)
            self.assertEqual(sum(x['quantity']=='0' for x in calls[-1][side]), 100)
            self.assertEqual(len(self.native_state(native)[side]), 100)
        self.assertEqual(len(a.bids), 100)
        self.assertEqual(self.native_state(native)['bids'][0],
                         {'price_ticks': '120000', 'quantity': '300000000'})
        self.assertEqual(self.native_state(native)['asks'][0],
                         {'price_ticks': '180000', 'quantity': '400000000'})

    def test_truncation_explicitly_deletes_old_worst_levels_on_both_sides(self):
        a, native, calls = self.adapter()
        self.ack(a)
        bids, asks = levels(25)
        a.feed(wire(bids, asks), 2)
        final = ([('1001', '4')]+bids[:-1], [('1999', '5')]+asks[:-1])
        a.feed(wire([('1001', '4')], [('1999', '5')], kind='update', final=final), 3)
        for side, old in (('bids', bids[-1]), ('asks', asks[-1])):
            self.assertIn({'price_ticks': str(int(old[0])*100), 'quantity': '0'}, calls[-1][side])
            self.assertEqual(len(self.native_state(native)[side]), 25)

    def test_repeated_updates_resolve_in_wire_order_before_depth_truncation(self):
        a, native, calls = self.adapter()
        self.ack(a)
        bids, asks = levels(25)
        a.feed(wire(bids, asks), 2)
        updates = [('1001', '1'), ('1001.00', '0'), ('1001', '7')]
        final = ([('1001', '7')]+bids[:-1], asks)
        a.feed(wire(updates, [], kind='update', final=final), 3)
        self.assertEqual(a.bids['100100'][1], '7')
        self.assertEqual(self.native_state(native)['bids'][0]['quantity'], '700000000')
        self.assertEqual(len(calls), 2)

    def test_deeper_changes_are_retained_but_not_promoted_into_crc_coverage(self):
        a, native, _ = self.adapter()
        self.ack(a)
        bids, asks = levels(25)
        first = wire(bids, asks)
        a.feed(first, 2)
        changed = bids[:-1]+[(bids[-1][0], '9')]
        message = wire([changed[-1]], [], kind='update', final=(changed, asks))
        self.assertEqual(json.loads(first)['data'][0]['checksum'],
                         json.loads(message)['data'][0]['checksum'])
        r = a.feed(message, 3)
        self.assertEqual(self.native_state(native)['bids'][-1]['quantity'], '900000000')
        self.assertEqual(r['checksum_scope'], 'top_10_per_side_only')
        self.assertFalse(a.capabilities['exchange_sequence'])

    def test_checksum_rejection_preserves_entire_deep_native_book_and_invalidates_ack(self):
        a, native, calls = self.adapter(100)
        self.ack(a)
        bids, asks = levels(100)
        a.feed(wire(bids, asks), 2)
        before = self.native_state(native), copy.deepcopy((a.bids, a.asks))
        with self.assertRaisesRegex(ProviderError, 'checksum_mismatch'):
            a.feed(wire([('1000', '9')], [], kind='update', checksum=0), 3)
        self.assertEqual((self.native_state(native), (a.bids, a.asks)), before)
        self.assertEqual(len(calls), 1)
        self.assertFalse(a._book_acknowledged)

    def test_snapshot_depth_and_message_update_budget_remain_bounded(self):
        for depth, count, kind, reason in ((25, 26, 'snapshot', 'snapshot_depth'),
                                          (100, 101, 'update', 'update_budget')):
            a, native, calls = self.adapter(depth)
            self.ack(a)
            bids, asks = levels(depth)
            a.feed(wire(bids, asks), 2)
            before = self.native_state(native)
            with self.subTest(depth=depth), self.assertRaisesRegex(ProviderError, reason):
                a.feed(wire(levels(count)[0], [], kind=kind), 3)
            self.assertEqual(self.native_state(native), before)
            self.assertEqual(len(calls), 1)

    def test_native_capacity_failure_preserves_native_and_python_state(self):
        a, native, calls = self.adapter(100, native_limit=100)
        self.ack(a)
        bids, asks = levels(100)
        a.feed(wire(bids, asks), 2)
        before = self.native_state(native), copy.deepcopy((a.bids, a.asks))
        better = [(str(1200-i), '3') for i in range(100)]
        with self.assertRaisesRegex(ProviderError, 'native_rejected'):
            a.feed(wire(better, [], kind='update', final=(better, asks)), 3)
        self.assertEqual((self.native_state(native), (a.bids, a.asks)), before)
        self.assertEqual(len(calls), 1)
        self.assertFalse(a._book_acknowledged)

    def test_reconnect_stale_ack_cannot_authorize_deep_book(self):
        a, native, calls = self.adapter()
        request = a.book_subscription_request()['req_id']
        self.ack(a)
        a.feed(wire(*levels(25)), 2)
        before = self.native_state(native)
        a.disconnected()
        a.connect()
        stale = {'method': 'subscribe', 'success': True, 'req_id': request,
                 'result': {'channel': 'book', 'symbol': a.symbol, 'depth': 25, 'snapshot': True}}
        with self.assertRaisesRegex(ProviderError, 'request_id'):
            a.feed(json.dumps(stale), 3)
        with self.assertRaisesRegex(ProviderError, 'acknowledgment_required'):
            a.feed(wire(*levels(25)), 4)
        self.assertEqual(self.native_state(native), before)
        self.assertEqual(len(calls), 1)

    def test_short_snapshot_never_synthesizes_missing_subscribed_levels(self):
        a, native, _ = self.adapter(100)
        self.ack(a)
        r = a.feed(wire([('1000', '1')], [('2000', '2')]), 2)
        self.assertEqual(r['retained_levels'], {'bids': 1, 'asks': 1})
        self.assertEqual(len(self.native_state(native)['bids']), 1)
        self.assertEqual(r['subscribed_depth'], 100)

    def test_documented_checksum_vector_is_unchanged_at_deeper_subscription(self):
        # Kraken's public checksum-guide example is documentation, not captured data.
        bids = list(zip(('45283.5','45283.4','45282.1','45281.0','45280.3',
                         '45279.0','45277.6','45277.5','45277.3','45276.6'),
                        ('0.10000000','1.54582015','0.10000000','0.10000000','1.54592586',
                         '0.07990000','0.03310103','0.30000000','1.54602737','0.15445238')))
        asks = list(zip(('45285.2','45286.4','45286.6','45289.6','45290.2',
                         '45291.8','45294.7','45296.1','45297.5','45299.5'),
                        ('0.00100000','1.54571953','1.54571109','1.54560911','0.15890660',
                         '1.54553491','0.04454749','0.35380000','0.09945542','0.18772827')))
        raw = wire(bids, asks)
        self.assertEqual(json.loads(raw)['data'][0]['checksum'], 3310070434)
        a, native, calls = self.adapter()
        self.ack(a)
        r = a.feed(raw, 2)
        self.assertEqual(r['retained_levels'], {'bids': 10, 'asks': 10})
        self.assertEqual(len(self.native_state(native)['asks']), 10)
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
