"""Single-owner native research session. All financial calculations remain in C++."""
from collections import deque
from copy import deepcopy
import hashlib
import json
import time

import gig_microstructure as gig

from .fixtures import EVENTS, FIXTURE_SHA256, benchmark, plan_config, replay_config, rules, sim_config


class ControlError(ValueError):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def exact_quantity(value):
    if type(value) is not str or not value.isascii() or not value.isdecimal() or value.startswith('0') or len(value) > 7:
        raise ControlError('INVALID_QUANTITY', 'quantity must be a canonical decimal string between 1 and 1000000')
    if not 1 <= int(value) <= 1_000_000:
        raise ControlError('INVALID_QUANTITY', 'quantity exceeds simulation budget')
    return value


class NativeSession:
    """Mutated only on the ASGI event loop, never shared with a background thread."""
    def __init__(self):
        self.live_feed = None
        self.mode = 'HISTORICAL_REPLAY'
        self.dataset = 'terminal-authored-v2'
        self.aggregate = None
        self.adapter = None
        self.playing = False
        self.speed = 1
        self.position = 0
        self.notifications = deque(maxlen=16)
        self.started = time.monotonic()
        self.clients = 0
        self.rejected = 0
        self.stream_timeouts = 0
        self.last_simulation = None
        self.replay = None
        self.restart()

    def reset_aggregate(self):
        from terminal.providers.kraken import KrakenBookAdapter
        aggregate = gig._native.AggregateDepth(32, 1048576)
        def apply(snapshot, bids, asks, sequence):
            return gig._checked((aggregate.snapshot if snapshot else aggregate.update)(bids, asks, sequence))
        self.aggregate = aggregate
        self.adapter = KrakenBookAdapter(apply)
        self.position = 0

    @property
    def source_events(self):
        if self.dataset == 'kraken-authored-profile-v1':
            from terminal.providers.fixtures import EVENTS as profile_events
            return profile_events
        return EVENTS

    def restart(self):
        self.playing = False
        if self.dataset == 'kraken-authored-profile-v1':
            self.reset_aggregate()
            self.step()
            return
        self.replay = gig.Replay(rules(), replay_config(), limits={
            'max_orders': '128', 'max_levels': '32', 'max_snapshot_depth': '20'},
            resource_budget_bytes='33554432')
        self.position = 0
        for _ in range(20):
            self.step()

    def step(self):
        if self.position >= len(self.source_events):
            self.playing = False
            return False
        if self.dataset == 'kraken-authored-profile-v1':
            self.adapter.feed(self.source_events[self.position], self.position * 50_000_000)
        else:
            self.replay.apply(EVENTS[self.position])
        self.position += 1
        return True

    def control(self, action, value=None):
        if action == 'mode':
            if value not in ('HISTORICAL_REPLAY', 'SIMULATION', 'LIVE'):
                raise ControlError('INVALID_MODE', 'unknown operating mode')
            self.playing = False
            self.mode = value
        elif action == 'dataset':
            if value not in ('terminal-authored-v2', 'kraken-authored-profile-v1'):
                raise ControlError('DATASET_UNAVAILABLE', 'only authored native or provider-shaped fixtures may be selected')
            if value == 'kraken-authored-profile-v1' and not hasattr(gig._native, 'AggregateDepth'):
                raise ControlError('NATIVE_CAPABILITY_UNAVAILABLE', 'rebuild the native package with aggregate depth support')
            # Stage the new source before replacing the accepted session.
            candidate = NativeSession()
            candidate.dataset = value
            if value != 'terminal-authored-v2': candidate.restart()
            self.dataset, self.mode, self.playing = value, 'HISTORICAL_REPLAY', False
            self.replay, self.aggregate, self.adapter = candidate.replay, candidate.aggregate, candidate.adapter
            self.position = candidate.position
        elif action == 'speed':
            if type(value) is not int or value not in (1, 2, 4, 8):
                raise ControlError('INVALID_SPEED', 'speed must be one of 1, 2, 4, 8')
            self.speed = value
        elif action == 'seek':
            if self.mode != 'HISTORICAL_REPLAY' or type(value) is not int or not 0 <= value <= len(self.source_events):
                raise ControlError('INVALID_SEEK', 'seek requires authored replay position within the source boundary')
            if self.dataset == 'kraken-authored-profile-v1':
                self.reset_aggregate()
                for _ in range(value): self.step()
                self.playing = False
                return
            candidate = gig.Replay(rules(), replay_config(), limits={
                'max_orders':'128', 'max_levels':'32', 'max_snapshot_depth':'20'}, resource_budget_bytes='33554432')
            candidate.run(EVENTS[:value])
            self.replay, self.position, self.playing = candidate, value, False
        elif action in ('play', 'pause', 'step', 'restart'):
            if self.mode != 'HISTORICAL_REPLAY':
                raise ControlError('MODE_RESTRICTION', 'replay controls require Historical Replay mode')
            if action == 'play':
                self.playing = self.position < len(self.source_events)
            elif action == 'pause':
                self.playing = False
            elif action == 'step':
                self.playing = False
                self.step()
            else:
                self.restart()
        elif action == 'connect':
            if value not in (None, 'kraken'):
                raise ControlError('UNSUPPORTED_PROVIDER', 'only the provisional Kraken profile is available')
            self.mode = 'LIVE'
            self.playing = False
            self.notifications.append({'code': 'LIVE_BLOCKED', 'message': 'Live transport is disabled: official documentation and terms could not be verified through the environment proxy.'})
        else:
            raise ControlError('UNKNOWN_ACTION', 'unknown control action')

    def state(self):
        live = self.mode == 'LIVE'
        simulation = self.mode == 'SIMULATION'
        origin = 'UNAVAILABLE' if live else 'SIMULATED' if simulation else 'HISTORICAL_SYNTHETIC'
        book = self.replay.snapshot('10')['data']['book'] if not live and not simulation else {'bids': [], 'asks': [], 'revision': '0'}
        profile = self.dataset == 'kraken-authored-profile-v1'
        metrics = {name: None for name in ('spread', 'midprice', 'microprice', 'imbalance', 'top_imbalance', 'bid_depth', 'ask_depth')}
        aggregate = gig._checked(self.aggregate.state()) if profile else None
        if profile and not live and not simulation:
            book = {'bids':aggregate['bids'], 'asks':aggregate['asks'], 'revision':aggregate['revision']}
            for target, source in [('spread','spread'),('midprice','midpoint'),('microprice','microprice'),('imbalance','depth_imbalance'),('bid_depth','bid_depth'),('ask_depth','ask_depth')]:
                metrics[target] = aggregate['metrics'][source]
        elif not live and not simulation:
            native = self.replay.metrics('10')['data']['result']['metrics']
            for target, source in [('spread', 'spread'), ('midprice', 'midpoint'), ('microprice', 'microprice'),
                                   ('imbalance', 'depth_imbalance'), ('top_imbalance', 'top_imbalance'),
                                   ('bid_depth', 'bid_depth'), ('ask_depth', 'ask_depth')]:
                metrics[target] = native[source]['value']
        from terminal.providers.fixtures import SHA256 as profile_sha
        result = {
            'schema_version': '1', 'mode': self.mode, 'origin': origin,
            'instrument': 'BTC/USD' if live or profile else 'SYNTH-USD', 'provider': 'kraken' if live else 'authored-kraken-profile' if profile else 'authored',
            'venue': 'Kraken' if live else 'AUTHORED', 'feed_type': 'L2_AGGREGATE' if live or profile else 'L3_AUTHORED',
            'price_scale': '100', 'quantity_scale': '100000000' if profile else '1',
            'book': {'bids': book['bids'], 'asks': book['asks']}, 'revision': book['revision'],
            'metrics': metrics, 'position': self.position if not live else 0, 'event_count': len(self.source_events) if not live else 0,
            'playing': self.playing, 'speed': self.speed,
            'source_timestamp_ns': None,
            'replay_time_ns': str((self.position - 1) * 50_000_000) if not live and not simulation else None,
            'received_at_ns': None,
            'feed': {'state': 'ERROR' if live else 'PAUSED' if not self.playing else 'REPLAYING',
                     'reason': 'Blocked: provider documentation, terms and connectivity unverified; no live data received.' if live else
                               'Independently authored provider-shaped L2 snapshot; current provider protocol is unverified.' if profile else 'Independently authored complete empty starting state; not historical observations.',
                     'real_time': False, 'sequence_complete': not live and not profile, 'capture_complete': not live, 'stale': live, 'gaps': 0},
            'provenance': {'category': origin, 'dataset': None if live else self.dataset,
                           'fixture_sha256': None if live else profile_sha if profile else FIXTURE_SHA256, 'generator_seed': None if live else '0',
                           'clock': None if live else 'simulation:authored-logical-clock', 'complete_initialization': not live and not profile, 'initialization_scope': 'authored subscribed L2 only' if profile else 'authored order-level empty boundary',
                           'recording_enabled': False, 'permission': 'unverified' if live else 'independently-authored'},
            'capabilities': {'live': False, 'native_replay': True, 'aggregate_l2': hasattr(gig._native, 'AggregateDepth'),
                             'simulation': True, 'twap': True, 'vwap': True, 'pov': True, 'tca': True,
                             'recording': False, 'observed_lobster': False, 'observed_itch': False},
            'engine': {'native': True, **gig.native_build_info()},
            'diagnostics': {'connected_clients': self.clients, 'queue_capacity': 1, 'queue_occupancy': 0,
                            'stream_timeouts': self.stream_timeouts, 'rejected_requests': self.rejected,
                            'native_status': aggregate if profile else self.replay.status(), 'uptime_seconds': round(time.monotonic() - self.started, 3)},
            'notifications': list(self.notifications), 'simulation': deepcopy(self.last_simulation) if simulation else None,
        }

        if live and self.live_feed is not None:
            view=self.live_feed.view()
            # Fixture-injected transports cannot be displayed as live observations.
            if view['origin']=='HISTORICAL_SYNTHETIC':
                view['origin']='UNAVAILABLE';view['book']={'bids':[],'asks':[]}
                view['metrics']={k:None for k in metrics};view['provenance']['category']='UNAVAILABLE'
                view['flow']={'trades':[],'classification':'UNAVAILABLE'}
            result.update(view)
        return result

    def simulation(self, algorithm, quantity='100', slices=5):
        if self.mode != 'SIMULATION':
            raise ControlError('MODE_RESTRICTION', 'simulation requires Simulation mode')
        if algorithm not in ('TWAP', 'VWAP', 'POV'):
            raise ControlError('INVALID_ALGORITHM', 'algorithm must be TWAP, VWAP or POV')
        quantity = exact_quantity(quantity)
        if type(slices) is not int or not 1 <= slices <= 16 or slices > int(quantity):
            raise ControlError('INVALID_SLICES', 'slices must be between 1 and 16 and no greater than quantity')
        config = plan_config(quantity, slices)
        if algorithm == 'TWAP':
            schedule = gig.twap(config)
        elif algorithm == 'VWAP':
            schedule = gig.vwap(config, [str(i + 1) for i in range(slices)], 'authored-volume-profile-v1', '0')
        else:
            # These are authored causal volume observations, not observed market volume.
            observations = [{'available_at': str(i * 1_000_000_000 // slices), 'lots': str(int(quantity) * 10),
                             'source_artifact': 'authored-volume-v1', 'ordinal': str(i + 1)} for i in range(slices)]
            schedule = gig.pov(config, observations, '1', '10')
        liquidity = [{'id': '1', 'side': '1', 'limit': '9903', 'quantity': quantity,
                      'tif': '0', 'post_only': False}]
        run = gig.simulate_plan(schedule, sim_config(), liquidity, '1000000005')
        simulation = run.simulation.to_dict()
        plan = run.plan.to_dict()
        children = {child['order']['id']: child for child in plan['data']['children']}
        cost_fills = []
        for fill in simulation['data']['state']['exchange_fills']:
            child = children[fill['taker']]
            decision_time = child['decision_time']
            cost_fills.append({'fill': fill, 'child': fill['taker'], 'decision_time': decision_time,
                               'decision_benchmark': benchmark(9901, decision_time),
                               'fee_ticks_per_lot': {'numerator': '0', 'denominator': '1'}})
        costs = gig.transaction_costs({'run_id': 'terminal-tca-v1', 'simulation_run_id': 'terminal-simulation-v1',
            'rules': rules(), 'side': '0', 'target': quantity, 'arrival': benchmark(9901),
            'terminal': benchmark(9901, '1000000005'), 'as_of': '1000000005'}, cost_fills).to_dict()
        result = {'schema_version': '1', 'origin': 'SIMULATED', 'algorithm': algorithm,
                  'plan': plan, 'simulation': simulation, 'costs': costs,
                  'provenance': {'category': 'SIMULATED', 'scenario': 'authored-fixed-liquidity-v1',
                    'seed': '1729', 'provider': 'authored', 'benchmark': 'authored-benchmark-v1',
                    'assumptions': 'No observed market data; zero fees; fixed supplied liquidity; execution-report delay 5 logical ns.'}}
        canonical = json.dumps(result, sort_keys=True, separators=(',', ':'))
        result['sha256'] = hashlib.sha256(canonical.encode()).hexdigest()
        self.last_simulation = result
        return deepcopy(result)

    @staticmethod
    def catalog():
        return {'schema_version': '1', 'datasets': [
            {'id': 'terminal-authored-v2', 'origin': 'HISTORICAL_SYNTHETIC', 'instrument': 'SYNTH-USD',
             'status': 'AVAILABLE', 'records': len(EVENTS), 'sha256': FIXTURE_SHA256,
             'initialization': 'authored complete empty state', 'format': 'gig.event/1.0'},
            {'id':'kraken-authored-profile-v1','origin':'HISTORICAL_SYNTHETIC','status':'AVAILABLE','format':'provisional provider-shaped L2;not observed','records':5},
            {'id': 'lobster-authored-fixtures', 'origin': 'HISTORICAL_SYNTHETIC', 'status': 'CLI_AVAILABLE',
             'format': 'LOBSTER 6/20-column authored CSV', 'reason': 'Validated offline adapter; not loaded into browser replay.'},
            {'id': 'itch-authored-fixtures', 'origin': 'HISTORICAL_SYNTHETIC', 'status': 'CLI_AVAILABLE',
             'format': 'BinaryFile/ITCH5.0', 'reason': 'Validated offline decoder/reconstruction; browser import not implemented.'},
            {'id': 'lobster-aapl-private', 'origin': 'HISTORICAL_OBSERVED', 'status': 'BLOCKED_PERMISSION',
             'reason': 'Third-party cloud processing not authorized; no file is opened.'},
            {'id': 'nasdaq-itch-private', 'origin': 'HISTORICAL_OBSERVED', 'status': 'BLOCKED_ACQUISITION',
             'reason': 'Separate bounded resource/acquisition authorization required.'}],
            'providers': [{'id': 'kraken', 'instrument': 'BTC/USD', 'capabilities': ['L2_AGGREGATE', 'TRADES'],
                           'status': 'BLOCKED_UNVERIFIED', 'live_connected': False,
                           'reason': 'Official docs/legal access blocked by environment proxy; no live transport enabled.'}],
            'recording': {'enabled': False, 'observed_permission': False}}
