"""Authored full-depth books through the serviced coordinator and native aggregate."""
import asyncio
import copy
import hashlib
import json
import unittest
from unittest.mock import patch

from .kraken import (
    BOOK_DEPTH_SESSION_PROFILE, BOOK_LARGE_DEPTH_PROFILE, LARGE_BOOK_PAYLOAD,
    MAX_PAYLOAD, Permission, ProviderError, decode, live_messages, transport_subscriptions,
)
from .kraken_coordinator import PROFILE, KrakenSessionCoordinator
from .supervisor import FeedSupervisor
from .test_kraken_depth_session import wire
from .test_kraken_public_session import raw, status
from .test_supervisor import ENV
from .test_supervisor_joint import acknowledgment


def levels(depth):
    bids = [(str(2000-i), '1.00000000') for i in range(depth)]
    asks = [(str(6000+i), '2.00000000') for i in range(depth)]
    return bids, asks


def negotiated(depth=500):
    coordinator = KrakenSessionCoordinator(profile=PROFILE, book_profile=BOOK_LARGE_DEPTH_PROFILE,
                                            depth=depth, native_capacity=2*depth)
    token = coordinator.connect('authored-large-book')
    coordinator.feed(raw(status()), 0, token=token)
    for clock, request in enumerate(coordinator.subscription_requests(token), 1):
        coordinator.feed(acknowledgment(request), clock, token=token)
    return coordinator, token


class LargeDepth(unittest.TestCase):
    def test_full_official_depths_bind_subscriptions_native_and_raw_source(self):
        for depth in (500, 1000):
            with self.subTest(depth=depth):
                coordinator, token = negotiated(depth)
                self.assertEqual(coordinator.subscription_requests(token)[0]['params']['depth'], depth)
                body = wire(*levels(depth))
                if depth == 1000:
                    self.assertGreater(len(body), MAX_PAYLOAD)
                    with self.assertRaisesRegex(ProviderError, 'payload_limit'):
                        decode(body)
                receipt = coordinator.feed(body, 3, token=token)
                self.assertEqual(receipt['source_sha256'], hashlib.sha256(body.encode()).hexdigest())
                self.assertEqual(receipt['source_frame_bytes'], len(body.encode()))
                self.assertEqual(receipt['source_receipt']['retained_levels'], dict(bids=depth, asks=depth))
                self.assertEqual(receipt['book_session_profile'], BOOK_LARGE_DEPTH_PROFILE)
                self.assertEqual(receipt['checksum_depth'], 10)
                self.assertEqual(receipt['checksum_scope'], 'top_10_per_side_only')
                view = coordinator.view(3)
                self.assertEqual(len(view['book']['asks']), depth)
                self.assertEqual(view['book']['bids'][-1]['price_ticks'], str((2001-depth)*100))
                self.assertFalse(view['full_protocol_qualified'])
                self.assertIsNone(view['source_sequence'])

    def test_full_replacement_commits_one_native_revision_with_all_trim_deletions(self):
        depth = 1000
        coordinator, token = negotiated(depth)
        coordinator.feed(wire(*levels(depth)), 3, token=token)
        better_bids = [(str(4000-i), '3') for i in range(depth)]
        better_asks = [(str(4500+i), '4') for i in range(depth)]
        receipt = coordinator.feed(wire(better_bids, better_asks, kind='update'), 4, token=token)
        view = coordinator.view(4)
        for side in ('bids', 'asks'):
            self.assertEqual(len(receipt['native_event'][side]), 2000)
            self.assertEqual(sum(level['quantity'] == '0' for level in receipt['native_event'][side]), 1000)
            self.assertEqual(len(view['book'][side]), 1000)
        self.assertEqual(view['book']['revision'], '2')
        self.assertEqual(view['book']['asks'][-1]['price_ticks'], '549900')
        self.assertEqual(view['book']['bids'][-1]['price_ticks'], '300100')

    def test_deeper_update_preserves_exact_source_and_only_top_ten_crc_scope(self):
        coordinator, token = negotiated()
        bids, asks = levels(500)
        original = wire(bids, asks)
        coordinator.feed(original, 3, token=token)
        change = (bids[-1][0], '9.001')
        new = wire([change], [], kind='update', final=(bids[:-1]+[change], asks))
        self.assertEqual(json.loads(original)['data'][0]['checksum'], json.loads(new)['data'][0]['checksum'])
        receipt = coordinator.feed(new, 4, token=token)
        self.assertEqual(receipt['native_event']['bids'], [{'price_ticks': '150100', 'quantity': '900100000'}])
        self.assertEqual(receipt['native_book_source_sha256'], hashlib.sha256(new.encode()).hexdigest())

    def test_update_row_budget_is_separate_from_retained_depth(self):
        depth = 500
        coordinator, token = negotiated(depth)
        bids, asks = levels(depth)
        coordinator.feed(wire(bids, asks), 3, token=token)
        price = bids[0][0]
        ordered = [(price, '0'), (price, '3')] * depth
        final = ([(price, '3')] + bids[1:], asks)
        receipt = coordinator.feed(wire(ordered, [], kind='update', final=final), 4, token=token)
        self.assertEqual(receipt['native_event']['bids'],
                         [{'price_ticks': '200000', 'quantity': '300000000'}])
        self.assertEqual(receipt['source_receipt']['retained_levels'], dict(bids=depth, asks=depth))
        self.assertEqual(coordinator.view(4)['book']['revision'], '2')
        before = copy.deepcopy(coordinator._native_image)
        oversized = wire(ordered + [(price, '3')], [], kind='update', final=final)
        with self.assertRaisesRegex(ProviderError, 'update_budget'):
            coordinator.feed(oversized, 5, token=token)
        self.assertEqual(coordinator._native_image, before)
        self.assertIsNone(coordinator.view(5)['book'])

    def test_over_budget_or_bad_crc_fences_without_partial_native_publication(self):
        bids, asks = levels(500)
        valid = wire(bids, asks)
        cases = (
            (wire(bids+[('1','1')], asks), 'update_budget'),
            (wire(bids, asks, kind='update', checksum=0), 'checksum_mismatch'),
            (wire(bids, asks, kind='update') + ' ' * LARGE_BOOK_PAYLOAD, 'payload_limit'),
            (raw(status()) + ' ' * MAX_PAYLOAD, 'payload_limit'),
            (json.dumps({'channel':'book','padding':'☺' * 90000}, ensure_ascii=False), 'payload_limit'),
        )
        for frame, code in cases:
            with self.subTest(code=code, length=len(frame)):
                coordinator, token = negotiated()
                coordinator.feed(valid, 3, token=token)
                before = copy.deepcopy(coordinator._native_image)
                with self.assertRaisesRegex(ProviderError, code):
                    coordinator.feed(frame, 4, token=token)
                self.assertEqual(coordinator._native_image, before)
                self.assertIsNone(coordinator.view(5)['book'])

    def test_short_snapshot_keeps_only_original_levels(self):
        coordinator, token = negotiated(1000)
        receipt = coordinator.feed(wire([('10','1')], []), 3, token=token)
        self.assertEqual(receipt['source_receipt']['retained_levels'], dict(bids=1, asks=0))
        self.assertEqual(coordinator.view(3)['book']['asks'], [])

    def test_exclusive_depth_and_native_transaction_capacity_admission(self):
        for profile, depth, capacity in (
            (BOOK_LARGE_DEPTH_PROFILE, 100, 256),
            (BOOK_LARGE_DEPTH_PROFILE, 1000, 1999),
            (BOOK_LARGE_DEPTH_PROFILE, 1000, 2001),
            (BOOK_DEPTH_SESSION_PROFILE, 100, 1000),
            (BOOK_DEPTH_SESSION_PROFILE, 500, 256),
        ):
            with self.subTest(profile=profile, depth=depth, capacity=capacity), self.assertRaises(ProviderError):
                KrakenSessionCoordinator(profile=PROFILE, book_profile=profile, depth=depth, native_capacity=capacity)

    def test_subscription_intent_and_frame_budget_require_opt_in(self):
        coordinator, token = negotiated()
        requests = coordinator.subscription_requests(token)
        self.assertEqual(transport_subscriptions('BTC/USD',requests,book_profile=BOOK_LARGE_DEPTH_PROFILE), requests)
        for choices in ({'subscriptions': requests}, {'book_profile': BOOK_LARGE_DEPTH_PROFILE},
                        {'subscriptions': requests, 'book_profile': 'unknown'}):
            with self.subTest(choices=choices), self.assertRaises(ProviderError):
                transport_subscriptions('BTC/USD', **choices)


class SupervisedLargeDepth(unittest.IsolatedAsyncioTestCase):
    async def test_product_projects_ten_levels_and_preserves_metric_depth_and_source(self):
        for depth in (25, 100, 500, 1000):
            with self.subTest(depth=depth):
                book = wire(*levels(depth))
                requests = []
                async def source(permission, *, stop, symbol, subscriptions, book_profile=None):
                    requests.extend(transport_subscriptions(symbol, subscriptions, book_profile=book_profile))
                    yield raw(status())
                    for request in subscriptions:
                        yield acknowledgment(request)
                    yield book
                    await stop.wait()

                env = {**ENV, 'GIG_LIVE_KRAKEN_SESSION_PROFILE':PROFILE,'GIG_LIVE_KRAKEN_BOOK_DEPTH':str(depth)}
                feed = FeedSupervisor(environment=env, transport=source)
                try:
                    await feed.start()
                    for _ in range(150):
                        if feed.messages == 4:
                            break
                        await asyncio.sleep(.001)
                    self.assertEqual(feed.messages, 4, feed.reason)
                    view = feed.view()
                    self.assertEqual(len(view['book']['bids']), 10)
                    self.assertEqual(view['feed']['native_depth_counts'], dict(asks=depth, bids=depth))
                    self.assertEqual(view['feed']['joint_session']['subscribed_depth'], depth)
                    self.assertEqual(view['metrics']['bid_depth']['numerator'], str(depth * 100000000))
                    self.assertEqual(view['provenance']['joint_source_receipts']['book']['source_sha256'],
                                     hashlib.sha256(book.encode()).hexdigest())
                    self.assertEqual(requests[0]['params']['depth'], depth)
                    self.assertEqual(view['origin'], 'HISTORICAL_SYNTHETIC')
                    self.assertFalse(view['capabilities']['recording'])
                    with self.assertRaisesRegex(ProviderError,'recording_profile_unavailable'):
                        feed.recording_writer_type()
                finally:
                    await feed.close()

    async def test_bad_configuration_rejects_before_source_worker(self):
        for token, profile in [('0500', PROFILE), ('1000', None), (500, PROFILE), ('250', PROFILE)]:
            with self.subTest(token=token, profile=profile):
                env={**ENV,'GIG_LIVE_KRAKEN_BOOK_DEPTH':token}
                if profile:
                    env['GIG_LIVE_KRAKEN_SESSION_PROFILE']=profile
                feed=FeedSupervisor(environment=env, transport=lambda **kw:self.fail('invalid depth reached transport'))
                with self.assertRaisesRegex(ProviderError,'depth_configuration'):
                    await feed.start()
                self.assertIsNone(feed.task)
                self.assertIsNone(feed.coordinator)

    async def test_large_frame_transport_limit_applies_only_to_explicit_request(self):
        coordinator, token = negotiated(1000)
        requests = coordinator.subscription_requests(token)
        calls = []
        class AuthoredConnect:
            def __init__(self, *args, **kwargs):
                calls.append(kwargs)
            async def __aenter__(self):
                return self
            async def __aexit__(self, *args):
                pass
            async def send(self, data):
                pass
            async def recv(self):
                return '{"channel":"heartbeat"}'
        with patch('websockets.asyncio.client.connect', AuthoredConnect):
            stream = live_messages(Permission(True, True, True, False, 'authored'), stop=asyncio.Event(),
                                   subscriptions=requests, book_profile=BOOK_LARGE_DEPTH_PROFILE)
            try:
                self.assertEqual(await anext(stream), '{"channel":"heartbeat"}')
                self.assertEqual(calls[0]['max_size'], LARGE_BOOK_PAYLOAD)
                self.assertEqual(calls[0]['max_queue'], 4)
            finally:
                await stream.aclose()
