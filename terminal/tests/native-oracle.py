"""Independent terminal/native integration oracle on authored data only.

Expected books/ratios are derived here, without importing production fixture helpers.
Run from repository root with a Python environment containing the built native wheel.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from terminal.server.engine import NativeSession


def rational(value):
    return None if value is None else Fraction(int(value['numerator']), int(value['denominator']))


def run():
    checks = 0
    frames = []
    started = time.perf_counter_ns()
    session = NativeSession()
    quantities = [[35 + level * 11 for level in range(10)] for _ in range(2)]

    def verify(position):
        nonlocal checks
        state = session.state()
        assert state['position'] == position
        assert state['origin'] == 'HISTORICAL_SYNTHETIC'
        assert state['mode'] == 'HISTORICAL_REPLAY'
        checks += 3
        for side_index, side in enumerate(('bids', 'asks')):
            actual = state['book'][side]
            assert len(actual) == 10
            checks += 1
            for level, row in enumerate(actual):
                expected_price = 9900 - level if side_index == 0 else 9902 + level
                assert row['price_ticks'] == str(expected_price)
                assert row['quantity'] == str(quantities[side_index][level])
                assert row['order_count'] == '1'
                checks += 3
        bid, ask = sum(quantities[0]), sum(quantities[1])
        expected = {'spread': Fraction(2), 'midprice': Fraction(9901),
                    'microprice': Fraction(9902 * quantities[0][0] + 9900 * quantities[1][0], quantities[0][0] + quantities[1][0]),
                    'imbalance': Fraction(bid - ask, bid + ask), 'bid_depth': Fraction(bid), 'ask_depth': Fraction(ask)}
        for name, value in expected.items():
            assert rational(state['metrics'][name]) == value, (position, name)
            checks += 1
        frames.append({'position': position, 'book': state['book'], 'metrics': state['metrics']})

    verify(20)
    for cycle in range(12):
        for index in range(20):
            quantities[index // 10][index % 10] = 25 + (cycle * 17 + index * 13) % 125
            session.control('step')
            verify(21 + cycle * 20 + index)
    final = json.dumps(frames, sort_keys=True, separators=(',', ':')).encode()
    session.control('restart')
    assert session.state()['book'] == frames[0]['book']
    checks += 1
    session.control('mode', 'LIVE')
    unavailable = session.state()
    assert unavailable['origin'] == 'UNAVAILABLE'
    assert unavailable['book'] == {'bids': [], 'asks': []}
    assert unavailable['source_timestamp_ns'] is None
    assert not unavailable['playing']
    checks += 4
    session.control('mode', 'SIMULATION')
    simulated = []
    for algorithm in ('TWAP', 'VWAP', 'POV'):
        result = session.simulation(algorithm, '100', 5)
        assert result['origin'] == 'SIMULATED'
        plan = result['plan']['data']
        assert sum(int(c['order']['quantity']) for c in plan['children']) == 100
        fills = result['simulation']['data']['state']['exchange_fills']
        assert sum(int(fill['quantity']) for fill in fills) == 100
        assert all(fill['price'] == '9903' for fill in fills)
        costs = result['costs']['data']['result']['summary']
        assert costs['filled_lots'] == '100' and costs['unfilled_lots'] == '0'
        assert rational(costs['execution_vwap']['value']) == 9903
        assert rational(costs['implementation_shortfall']) == 200
        assert rational(costs['currency_shortfall']) == 2
        assert session.simulation(algorithm, '100', 5) == result
        checks += 9
        simulated.append({'algorithm': algorithm, 'sha256': result['sha256']})
    return {'schema': 'gig.terminal.native_oracle.v1', 'origin': 'HISTORICAL_SYNTHETIC',
            'architecture': platform.machine(), 'python': platform.python_version(),
            'states_compared': len(frames), 'independent_assertions': checks,
            'prefix_hash': hashlib.sha256(final).hexdigest(),
            'simulations': simulated, 'elapsed_ns': time.perf_counter_ns() - started,
            'failures': 0, 'skipped': 0,
            'scope': 'Author-written dictionary/price/quantity/Fraction oracle, not observed-market evidence'}


if __name__ == '__main__':
    evidence = run()
    if len(sys.argv) > 1:
        output = Path(sys.argv[1]); output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as f: json.dump(evidence, f, indent=2); f.write('\n')
    print(json.dumps(evidence, indent=2))
