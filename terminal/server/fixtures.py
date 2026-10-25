"""Authored deterministic fixtures. No restricted observations or exchange order IDs."""
from copy import deepcopy
import hashlib
import json


def known(value):
    return {'reason': '0', 'value': value}


def missing():
    return {'reason': '3', 'value': None}


def rules():
    return {'instrument': '1', 'venue': '1', 'minimum_price': '1',
            'maximum_price': '9223372036854775807', 'maximum_quantity': '18446744073709551615',
            'tick_size': {'numerator': '1', 'denominator': '100'},
            'lot_size': {'numerator': '1', 'denominator': '1'}}


def scope():
    return {'stream': '1', 'session': 'terminal-authored-v2', 'epoch': '0', 'unit': '0'}


def replay_config():
    return {'run_id': 'terminal-authored-replay-v2', 'session': {'session': 'terminal-authored-v2', 'epoch': '0'},
            'streams': [{'venue': '1', 'scope': scope(), 'dataset': 'terminal-authored-v2',
                         'dataset_version': '2', 'first_sequence': '0', 'rank': '0'}],
            'ordering': '0', 'timestamp_clock': missing(), 'additional_instruments': [],
            'max_journal_records': '512', 'initial_state': '1'}


def event(sequence, tag, payload):
    return {'schema': 'gig.event', 'version': '1.0', 'data': {
        'metadata': {'schema_version': '1', 'instrument': known('1'), 'venue': known('1'),
                     'scope': known(scope()), 'sequence': known(str(sequence)), 'subevent_index': '0',
                     'subevent_count': '1', 'event_time': missing(),  # Replay clock is separate from exchange EventTimestamp.
                     'receive_time': missing(), 'source_record': known(f'authored:{sequence}'),
                     'capture_ordinal': known(str(sequence)), 'provenance': {
                         'dataset': known({'identity': 'terminal-authored-v2', 'version': known('2'),
                            'license_reference': known('independently-authored:no-external-data'), 'sha256': missing()}),
                         'origin': known('0'), 'source': known('0'), 'generator_seed': known('0'),
                         'lineage': [{'kind': '0', 'operation': 'terminal-fixed-scenario-v2', 'version': '2'}], 'parents': []}},
        'payload': {'tag': str(tag), 'value': payload}}}


def make_events():
    result = []
    for side in ('0', '1'):
        for level in range(10):
            identifier = 1 + level + (10 if side == '1' else 0)
            result.append(event(len(result), '0', {'order_id': str(identifier), 'side': side,
                'price_ticks': str(9900 - level if side == '0' else 9902 + level),
                'quantity': str(35 + level * 11)}))
    # Price-preserving replacements are authored queue-priority resets, not real market events.
    for cycle in range(12):
        for index in range(20):
            side = '0' if index < 10 else '1'
            level = index % 10
            quantity = 25 + ((cycle * 17 + index * 13) % 125)
            result.append(event(len(result), '2', {'old_order_id': str(index + 1),
                'new_order_id': str(index + 1), 'side': side,
                'price_ticks': str(9900 - level if side == '0' else 9902 + level),
                'quantity': str(quantity), 'priority': '0'}))
    return result


EVENTS = tuple(make_events())
FIXTURE_SHA256 = hashlib.sha256(json.dumps(EVENTS, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def sim_config():
    zero = {'base': '0', 'jitter': '0'}
    return {'run_id': 'terminal-simulation-v1', 'rules': rules(), 'seed': '1729',
            'arrival': deepcopy(zero), 'cancel': deepcopy(zero), 'acknowledgment': deepcopy(zero),
            'execution': {'base': '5', 'jitter': '0'}, 'max_orders': '128', 'max_events': '1024',
            'max_fills': '512', 'max_commands': '512', 'max_reports': '1024'}


def plan_config(quantity, slices):
    return {'run_id': 'terminal-simulation-v1', 'assumptions_id': 'authored-limit-liquidity-v1',
            'rules': rules(), 'side': '0', 'limit': '9905', 'target': quantity,
            'inventory_limit': quantity, 'max_child': quantity, 'start': '0', 'end': '1000000000',
            'bins': str(slices), 'first_child_id': '1000', 'tif': '1', 'post_only': False}


def benchmark(price, time='0'):
    return {'midpoint': {'numerator': str(price), 'denominator': '1'},
            'available_at': time, 'source_artifact': 'authored-benchmark-v1'}
