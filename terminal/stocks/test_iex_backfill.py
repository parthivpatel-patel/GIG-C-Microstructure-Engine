import asyncio
import copy
import tempfile
import unittest
from types import SimpleNamespace
import msgpack
from urllib.parse import parse_qs, urlsplit

from terminal.alpaca_wire import FixtureWire, WireError
from .historical_v2 import HistoricalClient, HistoricalPermission, ns
from .iex_backfill import backfill, gaps
from .live import LiveIEX
from .observation_store import ObservationStore
from .test_sprint4_history import PERMISSION, response


def quote(timestamp):
    return {'T': 'q', 'S': 'AAPL', 't': timestamp, 'bp': 100, 'ap': 101, 'bs': 4, 'as': 5}


def fixture_live(store=None):
    workspace = SimpleNamespace(environment={'GIG_ALPACA_LIVE_ENABLED': '1'}, catalog=None,
                                permission=lambda _: {}, market_identity=lambda symbol: {'symbol': symbol})
    live = LiveIEX(workspace, connector=lambda: None, clock=lambda: 100., wall=lambda: 1704205801., store=store)
    live.phase = 'SUBSCRIBED'
    live.symbols = ('AAPL',)
    live.generation = 1
    return live


def observations():
    live = fixture_live()
    live.process(msgpack.packb([quote('2024-01-02T14:30:00.000000001Z')]))
    live.generation += 1
    live.latest = {}
    live.process(msgpack.packb([quote('2024-01-02T14:30:00.000000003Z')]))
    return live


def historical(wire, permission=PERMISSION):
    return HistoricalClient(wire, permission=permission, clock_ns=lambda: ns('2024-01-03T00:00:00Z'))


class Backfill(unittest.IsolatedAsyncioTestCase):
    async def test_exact_open_gap_uses_inclusive_wire_end_with_no_live_mutation(self):
        live = observations()
        retained = copy.deepcopy(live.view())
        gap, = gaps(live)
        self.assertEqual((gap['previous_receipt'], gap['current_receipt']), (1, 2))
        source_time = '2024-01-02T14:30:00.000000002Z'

        def handler(method, url, body):
            params = parse_qs(urlsplit(url).query)
            self.assertEqual((method, body), ('GET', None))
            self.assertEqual((params['start'], params['end'], params['feed']),
                             ([source_time], [source_time], ['iex']))
            return response({'quotes': {'AAPL': [quote(source_time)]},
                             'next_page_token': 'provider-page-two'})

        result = await backfill(live, historical(FixtureWire(handler)), gap['gap_id'], 1)
        self.assertEqual(result['coverage'], 'BOUNDED_PREFIX')
        self.assertEqual(result['history']['records'][0]['timestamp'], source_time)
        self.assertEqual(result['history']['query']['end'], gap['end'])
        self.assertFalse(result['merged_into_live'])
        self.assertEqual(result['observation_loss'], 'UNKNOWN_NO_EXCHANGE_SEQUENCE')
        self.assertEqual(live.view(), retained)

    async def test_stale_gap_or_unauthorized_history_never_reaches_wire(self):
        live = observations()
        gap, = gaps(live)
        wire = FixtureWire(lambda *_: self.fail('unexpected source request'))
        with self.assertRaisesRegex(WireError, 'specific_permissions'):
            await backfill(live, historical(wire, HistoricalPermission()), gap['gap_id'])
        live.pending = {'step': 'SUBSCRIBE_SENT'}
        with self.assertRaisesRegex(WireError, 'gap_unavailable'):
            await backfill(live, historical(wire), gap['gap_id'])
        self.assertEqual(wire.calls, [])

    async def test_restored_checkpoint_contributes_only_an_unexpired_previous_capture_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            now = [100.]
            previous = fixture_live(ObservationStore(directory, clock=lambda: now[0], retention_seconds=15))
            previous.process(msgpack.packb([quote('2024-01-02T14:30:00.000000001Z')]))
            current = fixture_live(ObservationStore(directory, clock=lambda: now[0], retention_seconds=30))
            current.restore_control()
            self.assertEqual((current.history, current.latest, current.receipts), ([], {}, 0))
            self.assertEqual(gaps(current), [])
            current.generation += 1
            current.phase = 'SUBSCRIBED'
            current.process(msgpack.packb([quote('2024-01-02T14:30:00.000000003Z')]))
            gap, = gaps(current)
            self.assertEqual(gap['previous_capture'], previous.source_session_id)
            self.assertEqual(gap['capture'], current.source_session_id)
            self.assertEqual((gap['previous_receipt'], gap['current_receipt']), (1, 1))
            self.assertEqual([r['source_session_id'] for r in current.history], [current.source_session_id])
            wire = FixtureWire(lambda *_:response({'quotes': {'AAPL': []}}))
            self.assertEqual((await backfill(current, historical(wire), gap['gap_id']))['coverage'],
                             'SOURCE_RESPONSE_EXHAUSTED')
            now[0] = 115.
            self.assertEqual(gaps(current), [])
            with self.assertRaisesRegex(WireError, 'gap_unavailable'):
                await backfill(current, historical(wire), gap['gap_id'])

    async def test_intent_only_restart_preserves_the_verified_old_observation_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ObservationStore(directory, clock=lambda: 100.)
            previous = fixture_live(store)
            previous.process(msgpack.packb([quote('2024-01-02T14:30:00.000000001Z')]))
            interrupted = fixture_live(store)
            interrupted.restore_control()
            interrupted.generation += 1
            interrupted.persist_control()  # A new intent with no accepted source frame.
            current = fixture_live(store)
            restored = current.restore_control()
            self.assertEqual(restored['previous_accepted_receipt'], 0)
            self.assertEqual(restored['observation_boundary']['capture'], previous.source_session_id)
            current.generation += 1
            current.phase = 'SUBSCRIBED'
            current.process(msgpack.packb([quote('2024-01-02T14:30:00.000000003Z')]))
            gap, = gaps(current)
            self.assertEqual(gap['previous_capture'], previous.source_session_id)
            self.assertEqual(gap['previous_receipt'], 1)

    async def test_generation_change_during_acquisition_rejects_result(self):
        live = observations()
        gap, = gaps(live)
        started = asyncio.Event()
        resumed = asyncio.Event()

        async def handler(*_):
            started.set()
            await resumed.wait()
            return response({'quotes': {'AAPL': []}})

        pending = asyncio.create_task(backfill(live, historical(FixtureWire(handler)), gap['gap_id']))
        await asyncio.wait_for(started.wait(), 1)
        live.generation += 1
        resumed.set()
        with self.assertRaisesRegex(WireError, 'gap_changed'):
            await pending
