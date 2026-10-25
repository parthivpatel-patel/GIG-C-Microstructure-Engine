"""Real native-backed gateway contracts, security boundaries and exact independent references."""
from copy import deepcopy
from fractions import Fraction
import json
import unittest

from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from terminal.server.app import create_app
from terminal.server.engine import NativeSession, ControlError
from terminal.server.fixtures import EVENTS

ORIGIN = 'http://127.0.0.1:8787'


class NativeContracts(unittest.TestCase):
    def test_authored_initial_book_and_independent_metrics(self):
        s = NativeSession().state()
        self.assertEqual(s['position'], 20)
        for side in ('bids', 'asks'):
            for i, row in enumerate(s['book'][side]):
                self.assertEqual(row['price_ticks'], str(9900 - i if side == 'bids' else 9902 + i))
                self.assertEqual(row['quantity'], str(35 + i * 11))
        for name, expected in [('spread', 2), ('midprice', 9901), ('microprice', 9901),
                               ('imbalance', 0), ('bid_depth', 845), ('ask_depth', 845)]:
            self.assertEqual(Fraction(int(s['metrics'][name]['numerator']), int(s['metrics'][name]['denominator'])), expected)
        self.assertFalse(s['feed']['real_time'])
        self.assertIsNone(s['source_timestamp_ns'])
        self.assertEqual(s['origin'], 'HISTORICAL_SYNTHETIC')

    def test_all_events_restart_determinism_and_bounds(self):
        session = NativeSession()
        while session.step():
            pass
        first = session.replay.canonical()
        self.assertEqual(session.position, len(EVENTS))
        self.assertFalse(session.playing)
        session.restart()
        while session.step():
            pass
        self.assertEqual(first, session.replay.canonical())
        self.assertEqual(session.replay.status()['journal_size'], str(len(EVENTS)))
        self.assertLess(int(session.replay.status()['pmr_peak_bytes']), 33554432)

    def test_invalid_controls_do_not_mutate_native(self):
        session = NativeSession()
        before = session.replay.canonical()
        for action, value in [('unknown', None), ('speed', True), ('speed', 100), ('mode', 'real'), ('connect', 'unknown')]:
            with self.assertRaises(ControlError):
                session.control(action, value)
            self.assertEqual(session.replay.canonical(), before)

    def test_mode_isolation_and_blocked_live(self):
        session = NativeSession()
        session.control('connect', 'kraken')
        current = session.state()
        self.assertEqual(current['origin'], 'UNAVAILABLE')
        self.assertEqual(current['book'], {'bids': [], 'asks': []})
        self.assertTrue(all(value is None for value in current['metrics'].values()))
        self.assertIsNone(current['received_at_ns'])
        with self.assertRaises(ControlError):
            session.control('play')
        session.control('mode', 'SIMULATION')
        self.assertEqual(session.state()['book'], {'bids': [], 'asks': []})
        self.assertEqual(session.state()['origin'], 'SIMULATED')

    def test_nonbook_modes_keep_explicit_missing_metrics(self):
        session = NativeSession()
        for mode in ('LIVE', 'SIMULATION'):
            session.control('mode', mode)
            state = session.state()
            self.assertEqual(set(state['metrics']), {'spread', 'midprice', 'microprice', 'imbalance', 'top_imbalance', 'bid_depth', 'ask_depth'})
            self.assertTrue(all(v is None for v in state['metrics'].values()))

    def test_seek_reconstructs_source_without_inferred_seed(self):
        session = NativeSession()
        session.control('seek', 0)
        self.assertEqual(session.state()['book'], {'bids':[], 'asks':[]})
        session.control('seek', 21)
        expected = session.state()['book']
        session.restart(); session.step()
        self.assertEqual(session.state()['book'], expected)
        for value in (-1,261,True,1.5):
            with self.assertRaises(ControlError): session.control('seek',value)
            self.assertEqual(session.state()['book'], expected)

    def test_provider_shaped_fixture_uses_native_l2_without_l3_ids(self):
        s=NativeSession();s.control('dataset','kraken-authored-profile-v1')
        first=s.state();self.assertEqual(first['origin'],'HISTORICAL_SYNTHETIC')
        self.assertEqual(first['provider'],'authored-kraken-profile');self.assertEqual(first['feed_type'],'L2_AGGREGATE')
        self.assertEqual(first['quantity_scale'],'100000000');self.assertEqual(first['book']['bids'][0]['quantity'],'200000000')
        s.step();self.assertEqual(s.state()['book']['bids'][0]['quantity'],'400000000')
        prior=s.state()['book'];s.step();self.assertEqual(s.state()['book'],prior)
        s.step();self.assertEqual(s.state()['book']['bids'],[])
        self.assertIsNone(s.state()['metrics']['midprice']);s.step()
        self.assertEqual(s.state()['book']['bids'][0]['price_ticks'],'9900')
        s.restart();self.assertEqual(s.state()['book'],first['book'])
        s.control('seek',0);self.assertEqual(s.state()['book'],{'bids':[],'asks':[]})
        s.control('seek',2);self.assertEqual(s.state()['book']['bids'][0]['quantity'],'400000000')
        s.control('mode','LIVE');self.assertEqual(s.state()['book'],{'bids':[],'asks':[]})
        s.control('dataset','terminal-authored-v2');self.assertEqual(s.state()['position'],20)
        self.assertEqual(s.state()['instrument'],'SYNTH-USD')

    def test_restricted_dataset_selection_refused_before_state_change(self):
        s=NativeSession();before=s.state()['book']
        for source in ('lobster-aapl-private','nasdaq-itch-private','/private/input'):
            with self.assertRaises(ControlError):s.control('dataset',source)
            self.assertEqual(s.state()['book'],before)

    def test_shared_state_schema_matches_all_modes_and_sources(self):
        from pathlib import Path
        from jsonschema import Draft202012Validator
        schema=json.loads((Path(__file__).resolve().parents[1]/'contracts/state.schema.json').read_text())
        validator=Draft202012Validator(schema);session=NativeSession()
        for source in ('terminal-authored-v2','kraken-authored-profile-v1'):
            session.control('dataset',source)
            for mode in ('HISTORICAL_REPLAY','SIMULATION','LIVE'):
                session.control('mode',mode);validator.validate(session.state())

    def test_exact_plan_fills_and_tca(self):
        session = NativeSession()
        session.control('mode', 'SIMULATION')
        for algorithm in ('TWAP', 'VWAP', 'POV'):
            result = session.simulation(algorithm)
            self.assertEqual(result['origin'], 'SIMULATED')
            self.assertEqual(result, session.simulation(algorithm))
            fills = result['simulation']['data']['state']['exchange_fills']
            self.assertEqual(sum(int(f['quantity']) for f in fills), 100)
            self.assertTrue(all(f['price'] == '9903' for f in fills))
            cost = result['costs']['data']['result']['summary']
            self.assertEqual(cost['implementation_shortfall'], {'numerator': '200', 'denominator': '1'})
            self.assertEqual(cost['currency_shortfall'], {'numerator': '2', 'denominator': '1'})

    def test_simulation_budget_and_failure_atomicity(self):
        session = NativeSession()
        session.control('mode', 'SIMULATION')
        result = session.simulation('TWAP')
        for args in [('TWAP', '01', 5), ('TWAP', '0', 1), ('TWAP', '1000001', 5),
                     ('TWAP', '100', True), ('TWAP', '100', 17), ('INVALID', '100', 5)]:
            with self.assertRaises(ControlError):
                session.simulation(*args)
            self.assertEqual(result, session.last_simulation)


class ApiContracts(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(), base_url=ORIGIN)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def post(self, path, value, headers=None):
        return self.client.post('/api/v1/' + path, json=value, headers={'origin': ORIGIN, **(headers or {})})

    def test_health_catalog_and_engine_ownership(self):
        self.assertTrue(self.client.get('/api/v1/health').json()['native'])
        state = self.client.get('/api/v1/state').json()
        self.assertTrue(state['engine']['native'])
        statuses = {d['id']: d['status'] for d in self.client.get('/api/v1/catalog').json()['datasets']}
        self.assertEqual(statuses['lobster-aapl-private'], 'BLOCKED_PERMISSION')
        self.assertEqual(statuses['itch-authored-fixtures'], 'CLI_AVAILABLE')

    def test_control_step_restart_and_invalid_fields(self):
        self.assertEqual(self.post('control', {'action': 'step'}).json()['position'], 21)
        self.assertEqual(self.post('control', {'action': 'restart'}).json()['position'], 20)
        for value in ({'action': 'step', 'path': '/private/data'}, [], {'action': 'speed', 'value': True}, {'action': 'unknown'}):
            self.assertEqual(self.post('control', value).status_code, 400)
        self.assertEqual(self.client.get('/api/v1/state').json()['position'], 20)

    def test_origin_and_host_boundaries(self):
        for origin in ('https://evil.example', 'null', ''):
            self.assertEqual(self.post('control', {'action': 'step'}, {'origin': origin}).status_code, 403)
        self.assertEqual(self.client.post('/api/v1/control', json={'action': 'step'}).status_code, 403)
        self.assertEqual(self.client.get('/api/v1/state', headers={'host': 'evil.example'}).status_code, 400)
        self.assertEqual(self.client.get('/api/v1/state').json()['position'], 20)

    def test_request_limits_and_duplicate_json(self):
        self.assertEqual(self.client.post('/api/v1/control', content='x' * 4097,
            headers={'origin': ORIGIN, 'content-type': 'application/json'}).status_code, 413)
        self.assertEqual(self.client.post('/api/v1/control', content='{"action":"step","action":"restart"}',
            headers={'origin': ORIGIN, 'content-type': 'application/json'}).status_code, 400)
        self.assertEqual(self.client.post('/api/v1/control', content='NaN',
            headers={'origin': ORIGIN, 'content-type': 'application/json'}).status_code, 400)
        self.assertEqual(self.client.post('/api/v1/control', content='{}', headers={'origin': ORIGIN}).status_code, 400)

    def test_simulation_endpoint_and_mode_gate(self):
        self.assertEqual(self.post('simulate', {}).status_code, 400)
        self.post('control', {'action': 'mode', 'value': 'SIMULATION'})
        result = self.post('simulate', {'algorithm': 'TWAP', 'quantity': '100', 'slices': 5})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['costs']['data']['result']['summary']['filled_lots'], '100')

    def test_websocket_exact_origin_and_owned_state(self):
        for origin in ('https://evil.example', ''):
            with self.assertRaises(WebSocketDisconnect):
                with self.client.websocket_connect('ws://127.0.0.1:8787/api/v1/stream', headers={'origin': origin}):
                    pass
        with self.client.websocket_connect('ws://127.0.0.1:8787/api/v1/stream', headers={'origin': ORIGIN}) as socket:
            state = socket.receive_json()
            self.assertEqual(state['position'], 20)
            self.assertEqual(state['diagnostics']['connected_clients'], 1)
            self.assertEqual(state['diagnostics']['queue_capacity'], 1)

    def test_security_headers_and_validation_allowlist(self):
        response = self.client.get('/api/v1/state')
        self.assertEqual(response.headers['x-content-type-options'], 'nosniff')
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertIn("frame-ancestors 'none'", response.headers['content-security-policy'])
        self.assertEqual(self.post('validate', {'profile': '../../private'}).status_code, 400)
        self.assertEqual(self.post('validate', {'profile': 'itch', 'path': '/private/input'}).status_code, 400)
        self.assertEqual(self.client.get('/api/v1/unknown').status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
