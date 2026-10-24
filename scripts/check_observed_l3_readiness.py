#!/usr/bin/env python3
"""Fail-closed observed-L3 readiness audit, not an evidence attestation service."""
import argparse
import json
from pathlib import Path

SCHEMA = 'gig.observed_l3_readiness.v1'
GATES = ('artifact_integrity', 'complete_capture', 'authenticated_session',
         'complete_initial_state', 'all_messages_accounted', 'exact_units',
         'source_provenance', 'independent_book_reference', 'restart_equivalence',
         'memory_qualification')
CAPABILITIES = {'observed_adapter': False, 'observed_context_native_seed': False,
                'independent_observed_book_oracle': False}
STATES = {'missing', 'partial', 'claimed', 'failed'}


def evaluate(document):
    if type(document) is not dict or set(document) != {'schema', 'origin', 'initialization', 'gates'}:
        raise ValueError('invalid readiness envelope')
    if document['schema'] != SCHEMA:
        raise ValueError('unsupported readiness schema')
    if document['origin'] not in ('observed', 'synthetic', 'unknown'):
        raise ValueError('invalid origin')
    if document['initialization'] not in ('unknown', 'empty_boundary_claim', 'complete_seed_claim', 'incomplete'):
        raise ValueError('invalid initialization evidence kind')
    gates = document['gates']
    if type(gates) is not dict or set(gates) != set(GATES):
        raise ValueError('missing or unknown readiness gate')
    if any(type(state) is not str or state not in STATES for state in gates.values()):
        raise ValueError('readiness claims are not verified attestations')
    reasons = ['implementation.' + name for name, ready in CAPABILITIES.items() if not ready]
    if document['origin'] != 'observed':
        reasons.append('observed_origin_not_established')
    if document['initialization'] in ('unknown', 'incomplete'):
        reasons.append('initial_state_not_established')
    # Even all-claimed inputs do not independently authenticate any source fact.
    reasons.extend('evidence.' + gate + '.' + state for gate, state in gates.items())
    return {'schema': SCHEMA, 'assessment': 'BLOCKED', 'observed_certified': False,
            'reasons': sorted(reasons), 'implementation_capabilities': dict(CAPABILITIES),
            'input_claims_are_not_attestations': True}


def from_prefix(document):
    run = document['single_authorized_get']
    if type(run['network_body_bytes']) is not int or run['network_body_bytes'] != 16384 or type(run['worker']['http_status']) is not int or run['worker']['http_status'] != 206:
        raise ValueError('not the qualified second-prefix evidence')
    states = {gate: 'missing' for gate in GATES}
    for key in ('artifact_integrity', 'complete_capture', 'all_messages_accounted', 'source_provenance'):
        states[key] = 'partial'
    return {'schema': SCHEMA, 'origin': 'observed', 'initialization': 'unknown', 'gates': states}


def bounded_json(path):
    with Path(path).open('rb') as stream:
        data = stream.read(65537)
    if len(data) > 65536:
        raise ValueError('readiness input exceeds64KiB')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate readiness field')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--input')
    choice.add_argument('--from-second-prefix')
    args = parser.parse_args()
    try:
        data = bounded_json(args.input or args.from_second_prefix)
        if args.from_second_prefix:
            data = from_prefix(data)
        report = evaluate(data)
    except (ValueError, KeyError, TypeError, OSError, RecursionError):
        print(json.dumps({'assessment': 'INVALID_INPUT', 'observed_certified': False}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 1  # Current observed integration is blocked, never a certified PASS.


if __name__ == '__main__':
    raise SystemExit(main())
