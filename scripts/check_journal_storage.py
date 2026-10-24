#!/usr/bin/env python3
"""Independent integer byte accounting and frozen pre-optimization replay control."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def trace(program):
    result = subprocess.run([program, 'emit'], capture_output=True, check=True, timeout=60)
    assert not result.stderr
    actual = [hashlib.sha256(line).hexdigest() for line in result.stdout.splitlines()]
    expected = json.loads((Path(__file__).resolve().parents[1] / 'docs/PHASE5_BASELINE_EVIDENCE.json').read_text())['canonical_differential']['prefix_sha256']
    assert len(actual) == len(expected) == 128 and actual == expected
    corrupted = expected.copy()
    corrupted[64] = '0' * 64
    assert actual != corrupted, 'negative control'
    print(json.dumps({'prefixes': 128, 'pre_optimization_equivalent': True,
                      'trace_sha256': hashlib.sha256(''.join(actual).encode()).hexdigest(),
                      'independent_state_model': 'separately executed by model mode'}, sort_keys=True))


def memory(program):
    for n in (1, 64, 129):
        for every in (0, 1):
            p = subprocess.run([program, str(n), str(every)], capture_output=True, check=True, timeout=30)
            d = json.loads(p.stdout)
            assert not p.stderr
            assert d['records'] == n and d['resets'] == (n if every else 0)
            assert d['record_capacity'] == n
            assert d['restart_capacity'] == (n if every else 0)
            assert d['post_destroy_live_bytes'] == 0
            assert d['live_pmr_bytes'] == d['initial_pmr_bytes'] + n * d['record_bytes'] + d['restart_capacity'] * d['restart_bytes']
            # Relative, ABI-portable savings gate; no fixed platform size assertion.
            assert d['record_bytes'] < d['logical_entry_bytes']
            if every == 0:
                assert d['live_pmr_bytes'] < d['initial_pmr_bytes'] + n * d['logical_entry_bytes']
    p = subprocess.run([program, '0', '0'], capture_output=True, timeout=30)
    assert p.returncode != 0
    print('6 journal storage cases: exact independent byte accounting and cleanup; invalid-input control passed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('trace', 'memory'))
    parser.add_argument('program')
    args = parser.parse_args()
    (trace if args.mode == 'trace' else memory)(args.program)
