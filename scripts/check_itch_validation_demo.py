#!/usr/bin/env python3
"""Independent byte/lifecycle oracle for the versioned P1I synthetic demonstration.

The fixture and flat order/ledger model below use only Python's standard library.
No production generator, decoder, book, serializer or prior native output supplies
expected values. Byte-for-byte identities and exact integer arithmetic precede
comparison with the C++ executable. This is synthetic differential validation,
not NASDAQ data, publisher-reference evidence or exchange certification.
"""
import argparse
import copy
import hashlib
import json
import pathlib
import re
import os
import selectors
import time
import struct
import subprocess
import zlib

IMPLEMENTATION = hashlib.sha256(b'P1I independent demonstration verifier contract v1').hexdigest()
MAX_OUTPUT = 2 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def header(kind, locate=1):
    return kind.encode('ascii') + struct.pack('>HH', locate, 0) + (1).to_bytes(6, 'big')


def fixture():
    """Author bytes by published field widths, independently of C++ writers."""
    symbols = {1: b'TEST    ', 2: b'TWO     '}
    def system(code):
        return header('S', 0) + code.encode('ascii')
    def directory(locate):
        return header('R', locate) + struct.pack('>8sccIcc2scccccIc', symbols[locate], b'Q', b'N', 100, b'N', b'C', b'  ', b'P', b' ', b'N', b'1', b'N', 0, b'N')
    def add(ref, quantity, price=100, locate=1, side=b'B'):
        return header('A', locate) + struct.pack('>QcI8sI', ref, side, quantity, symbols[locate], price)
    records = [system('O'), directory(1), directory(2), add(101, 10), add(201, 20, 200, 2, b'S'), add(102, 20),
               header('E') + struct.pack('>QIQ', 102, 4, 1),
               header('X') + struct.pack('>QI', 101, 3),
               header('D') + struct.pack('>Q', 101),
               header('U') + struct.pack('>QQII', 102, 103, 15, 101),
               header('P') + struct.pack('>QcI8sIQ', 0, b'B', 3, symbols[1], 100, 2),
               header('Q') + struct.pack('>Q8sIQc', 0, symbols[1], 100, 3, b'O'),
               header('B') + struct.pack('>Q', 2)]
    records += [system(code) for code in 'SQMEC']
    framed = [struct.pack('>H', len(record)) + record for record in records]
    raw = b''.join(framed) + b'\0\0'
    # RFC1952 wrapper and RFC1951 stored block. Neither calls C++ fixture code.
    encoded = (b'\x1f\x8b\x08\0\0\0\0\0\0\xff\x01' +
               struct.pack('<HH', len(raw), len(raw) ^ 0xffff) + raw +
               struct.pack('<II', zlib.crc32(raw) & 0xffffffff, len(raw)))
    require(zlib.decompress(encoded, 31) == raw, 'independent gzip fixture invalid')
    require((len(records), len(raw), len(encoded)) == (18, 507, 530), 'independent fixture size drift')
    return records, framed, raw, encoded


def reference(prefix):
    """Independent flat maps, explicit lifecycle and nine exact ledger totals."""
    records, frames, _, _ = fixture()
    books = [dict(orders={}, revision=0, next_priority=0, ledger=[0] * 9),
             dict(orders={}, revision=0, next_priority=0, ledger=[0] * 9)]
    context = {}
    matches = {}
    receipts = []
    external = 0
    offset = 0
    stage = 0
    for ordinal, payload in enumerate(records[:prefix]):
        kind = chr(payload[0])
        locate = int.from_bytes(payload[1:3], 'big')
        get = lambda at, width: int.from_bytes(payload[at:at + width], 'big')
        native = kind in 'AEXDU'
        index = locate - 1 if kind != 'S' else None
        sequence = None
        if kind == 'S':
            stage += 1
        if native:
            book = books[index]
            ledger = book['ledger']
            if kind == 'A':
                ref, qty, price = get(11, 8), get(20, 4), get(32, 4)
                side = chr(payload[19])
                context[ref] = [ref, locate, ord(side), qty, price, ordinal, True]
                book['orders'][ref] = [ref, side, price, qty, book['next_priority']]
                book['next_priority'] += 1
                ledger[0] += qty
                ledger[7] += qty
            else:
                ref = get(11, 8)
                old = book['orders'][ref]
                if kind == 'U':
                    new, qty, price = get(19, 8), get(27, 4), get(31, 4)
                    ledger[6] += old[3]
                    ledger[8] += old[3]
                    ledger[5] += qty
                    ledger[7] += qty
                    context[ref][3] = 0
                    context[ref][6] = False
                    context[new] = [new, locate, ord(old[1]), qty, price, ordinal, True]
                    book['orders'][new] = [new, old[1], price, qty, book['next_priority']]
                    book['next_priority'] += 1
                    del book['orders'][ref]
                else:
                    qty = old[3] if kind == 'D' else get(19, 4)
                    old[3] -= qty
                    context[ref][3] -= qty
                    context[ref][6] = context[ref][3] > 0
                    if old[3] == 0:
                        del book['orders'][ref]
                    ledger[2 if kind == 'E' else 1] += qty
                    ledger[8] += qty
                    if kind == 'E':
                        matches[get(23, 8)] = [get(23, 8), locate, 0, False]
            sequence = book['revision']
            book['revision'] += 1
        else:
            external += 1
            if kind in 'PQ':
                match = get(36 if kind == 'P' else 31, 8)
                matches[match] = [match, locate, 1 if kind == 'P' else 2, False]
            if kind == 'B':
                matches[get(11, 8)][3] = True
        receipts.append([ordinal, offset, offset + 2, kind, locate, 0, 1, index, sequence])
        offset += len(frames[ordinal])
    for book in books:
        book['orders'] = sorted(book['orders'].values())
        book['remaining'] = sum(order[3] for order in book['orders'])
        book['count'] = len(book['orders'])
        book['journal'] = book['revision']
        for side, key in [('B', 'bids'), ('S', 'asks')]:
            levels = {}
            for _, order_side, price, qty, _ in book['orders']:
                if order_side == side:
                    quantity, count = levels.get(price, (0, 0))
                    levels[price] = quantity + qty, count + 1
            book[key] = [[price, *levels[price]] for price in sorted(levels, reverse=side == 'B')]
        del book['next_priority']
    return dict(books=books, orders=list(context.values()), matches=list(matches.values()), receipts=receipts,
                native=sum(book['revision'] for book in books), external=external, stage=stage,
                accepted=prefix, accepted_bytes=offset, accepted_hash=digest(b''.join(frames[:prefix])))


def subset(expected, actual, path=''):
    if type(expected) is not type(actual):
        raise ValueError(f'{path}: expected {type(expected).__name__}, got {type(actual).__name__}')
    if isinstance(expected, dict):
        for key, value in expected.items():
            require(key in actual, f'{path}.{key}: missing')
            subset(value, actual[key], path + '.' + key)
    elif isinstance(expected, list):
        require(len(expected) == len(actual), f'{path}: array length differs')
        for index, (left, right) in enumerate(zip(expected, actual)):
            subset(left, right, f'{path}[{index}]')
    else:
        require(expected == actual, f'{path}: expected {expected!r}, got {actual!r}')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def bounded_run(arguments):
    """Bound both captured streams before allocating/parsing an output document."""
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    selector = selectors.DefaultSelector()
    output = {'stdout': bytearray(), 'stderr': bytearray()}
    deadline = time.monotonic() + 30
    try:
        selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map():
            remaining = deadline - time.monotonic()
            require(remaining > 0, 'demonstration process timeout')
            ready = selector.select(remaining)
            require(bool(ready), 'demonstration process timeout')
            for key, _ in ready:
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                require(sum(len(v) for v in output.values()) + len(chunk) <= MAX_OUTPUT,
                        'demonstration output exceeds declared fixture bound')
                output[key.data] += chunk
        result = process.wait(timeout=max(0.01, deadline - time.monotonic()))
        return result, bytes(output['stdout']), bytes(output['stderr'])
    finally:
        selector.close()
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        process.stderr.close()


def load_output(executable, scenario):
    code, stdout, stderr = bounded_run([executable, scenario, IMPLEMENTATION])
    require(code == 0, f'{scenario}: executable failed: {stderr[:2000]!r}')
    require(not stderr, f'{scenario}: unexpected stderr: {stderr[:2000]!r}')
    return json.loads(stdout, object_pairs_hook=unique_object,
                      parse_constant=lambda token: (_ for _ in ()).throw(ValueError('nonfinite JSON: ' + token)))


def verify_snapshot(snapshot, prefix, state_kind):
    expected = reference(prefix)
    records, frames, raw, encoded = fixture()
    complete = state_kind == 'valid'
    paused = state_kind in ('pause', 'bounded')
    finished = state_kind != 'pause'
    source = snapshot['source']
    stream = snapshot['stream']
    position = [expected['receipts'][-1][1], expected['receipts'][-1][2], prefix - 1]
    subset(dict(considered=prefix, context_committed=prefix, native_committed=expected['native'],
                external_observations=expected['external'], rejected=0, pending=False,
                unconsidered_record=False, input_complete=complete, initialization_verified=True,
                eligibility=1 if complete or state_kind == 'pause' else 2,
                physical_position=position, committed_position=position), source, '.source')
    subset(dict(accepted_records=prefix, native_records=expected['native'],
                external_observations=expected['external'], source_records=prefix,
                accepted_prefix_bytes=expected['accepted_bytes'],
                accepted_prefix_sha256=expected['accepted_hash'], source_complete=complete,
                publication_eligible=complete, paused=paused, finished=finished,
                bounded_prefix=state_kind == 'bounded', residual_frame_bytes=0,
                error_code=1 if state_kind == 'corrupt' else 0,
                gzip_error_code=7 if state_kind == 'corrupt' else 0,
                observed_gzip_error_code=7 if state_kind == 'corrupt' else 0), stream, '.stream')
    require(type(stream['compressed_bytes']) is int and 0 <= stream['compressed_bytes'] <= len(encoded),
            'compressed byte count outside independently authored source')
    require(type(stream['decompressed_bytes']) is int and 0 <= stream['decompressed_bytes'] <= len(raw),
            'decompressed byte count outside independently authored source')
    require(type(stream['framing_bytes']) is int and type(stream['buffered_output_bytes']) is int
            and stream['framing_bytes'] >= 0 and stream['buffered_output_bytes'] >= 0,
            'physical framing/buffer counters invalid')
    require(stream['decompressed_bytes'] == stream['framing_bytes'] + stream['buffered_output_bytes'],
            'decompressed/framing/buffer conservation')
    require(stream['framing_bytes'] == expected['accepted_bytes'] + (2 if prefix == 18 else 0),
            'framing byte count including terminal marker')
    subset(dict(gzip_member_verified=complete, framer_terminated=prefix == 18,
                compressed_identity_verified=complete, decompressed_identity_verified=complete), stream, '.stream')
    actual_encoded = bytearray(encoded)
    if state_kind == 'corrupt':
        actual_encoded[-8] ^= 1
        # Independent bytewise zlib detects the exact trailer error boundary.
        decoder = zlib.decompressobj(31)
        produced = bytearray()
        consumed = 0
        for byte in actual_encoded:
            consumed += 1
            try:
                produced += decoder.decompress(bytes([byte]))
            except zlib.error:
                break
        require(consumed < len(encoded) and bytes(produced) == raw and not decoder.eof,
                'independent corrupt-trailer reference did not fail')
        require(stream['compressed_bytes'] == consumed, 'CRC failure compressed boundary differs')
    if prefix == 18:
        require(stream['decompressed_bytes'] == len(raw), 'full decoded raw extent')
        if complete:
            require(stream['compressed_bytes'] == len(encoded), 'full compressed extent')
    require(stream['compressed_sha256'] == digest(actual_encoded[:stream['compressed_bytes']]),
            'physical compressed-prefix hash differs')
    require(stream['decompressed_sha256'] == digest(raw[:stream['decompressed_bytes']]),
            'physical decompressed-prefix hash differs')
    context = snapshot['context']
    subset(dict(accepted_records=prefix, directories=2, lifetime_orders=len(expected['orders']),
                active_orders=sum(1 for order in expected['orders'] if order[6]),
                matches=len(expected['matches']), initialization_incomplete=True,
                session_incomplete=not complete, source_complete=complete,
                last_timestamp_ns=1, orders=expected['orders'],
                match_references=expected['matches']), context, '.context')
    receipts = copy.deepcopy(expected['receipts'])
    for receipt in receipts:
        receipt[3] = ord(receipt[3])
    subset(receipts, snapshot['receipts'], '.receipts')
    require(len(snapshot['books']) == 2, 'two-symbol book count')
    for index, (book_expected, book_actual) in enumerate(zip(expected['books'], snapshot['books'])):
        book_expected = dict(book_expected)
        book_expected['instrument_id'] = index + 1
        book_expected['stock_locate'] = index + 1
        book_expected['derived_sequence'] = book_expected['revision']
        book_expected['journal_records'] = book_expected.pop('journal')
        book_expected['order_count'] = book_expected.pop('count')
        book_expected['remaining_quantity'] = book_expected.pop('remaining')
        book_expected['needs_recovery'] = False
        book_expected['orders'] = [[ref, ord(side), price, qty, priority]
                                   for ref, side, price, qty, priority in book_expected['orders']]
        last_native = next(receipt for receipt in reversed(expected['receipts'])
                           if receipt[7] == index and receipt[8] is not None)
        book_expected['metadata'] = dict(capture_ordinal=last_native[0],
                                        source_record=f'p1i-h18:{last_native[0]}',
                                        sequence=last_native[8], stream_id=index + 1,
                                        session='p1i-authored-session', dataset='p1i-h18', version='1',
                                        sha256=digest(raw), generator_seed=7707, origin=0,
                                        event_timestamp=None, receive_timestamp=None)
        subset(book_expected, book_actual, f'.books[{index}]')
        # Quantities are integer lots (1share/lot), and prices exact Price(4) ticks.
        require(book_actual['ledger'][7] - book_actual['ledger'][8] == book_actual['remaining_quantity'],
                'independent ledger conservation')
    return expected


def exact_keys(value, keys, name):
    require(type(value) is dict and set(value) == set(keys), name + ': versioned fields differ')


def verify_output(output, scenario):
    """Validate the declared contract against independently authored source/state."""
    exact_keys(output, ('schema_version', 'scenario', 'provenance', 'profile',
                        'restart_verified', 'pause', 'replayed', 'final', 'resources'), 'root')
    subset(1, output['schema_version'], '.schema_version')
    subset(scenario, output['scenario'], '.scenario')
    _, _, raw, encoded = fixture()
    actual = bytearray(encoded)
    if scenario == 'corrupt':
        actual[-8] ^= 1
    provenance = dict(origin='synthetic', source='p1i-authored-source', session='p1i-authored-session',
                      fixture='p1i-h18', fixture_version=1, generator='p1i-literal-generator',
                      generator_seed=7707, initialization='authored_complete_empty',
                      implementation_sha256=IMPLEMENTATION, implementation_identity_status='caller_declared',
                      expected_compressed_sha256=digest(encoded), actual_input_sha256=digest(actual),
                      expected_decompressed_sha256=digest(raw), declared_records=18,
                      declared_compressed_bytes=len(encoded), declared_decompressed_bytes=len(raw),
                      trading_date=None, receive_clock=None)
    exact_keys(output['provenance'], provenance, 'provenance')
    subset(provenance, output['provenance'], '.provenance')
    profile = dict(name='p1i-h18-bounded-v1', pmr_budget_bytes=4 * 1024 * 1024,
                   book_count=2, max_orders_per_book=8, max_levels_per_book=8, depth_per_book=8,
                   journal_cap_per_book=16, source_record_cap=32, receipt_budget_bytes=65536,
                   context_directories=2, context_lifetime_orders=4, context_matches=3,
                   context_logical_budget_bytes=4096, gzip_output_buffer_bytes=128,
                   compressed_byte_cap=1024, decompressed_byte_cap=1024,
                   expansion_ratio_cap=2, expansion_slack_bytes=64, header_byte_cap=64,
                   framer_payload_cap=64, framer_buffer_bytes=64, framer_record_cap=32,
                   framer_byte_cap=1024, price_tick=[1, 10000], quantity_lot=[1, 1],
                   allow_c_book_only=False, pause_after_accepted=8)
    exact_keys(output['profile'], profile, 'profile')
    subset(profile, output['profile'], '.profile')
    require(type(output['restart_verified']) is bool and output['restart_verified'] == (scenario == 'restart'),
            'restart verification disposition')
    if scenario == 'restart':
        verify_snapshot(output['pause'], 8, 'pause')
        verify_snapshot(output['replayed'], 18, 'valid')
        verify_snapshot(output['final'], 18, 'valid')
        require(output['replayed'] == output['final'], 'restart final state/output differs')
    else:
        require(output['pause'] is None and output['replayed'] is None, 'unexpected restart snapshot')
        verify_snapshot(output['final'], 8 if scenario == 'bounded' else 18,
                        'bounded' if scenario == 'bounded' else scenario)
    for snapshot in (output['pause'], output['replayed'], output['final']):
        if snapshot is None:
            continue
        exact_keys(snapshot, ('stream', 'source', 'context', 'receipts', 'books'), 'snapshot')
        exact_keys(snapshot['stream'], ('compressed_bytes', 'decompressed_bytes', 'framing_bytes',
                    'accepted_prefix_bytes', 'source_records', 'accepted_records', 'native_records',
                    'external_observations', 'compressed_sha256', 'decompressed_sha256',
                    'accepted_prefix_sha256', 'gzip_member_verified', 'framer_terminated',
                    'compressed_identity_verified', 'decompressed_identity_verified',
                    'source_complete', 'publication_eligible', 'paused', 'finished', 'bounded_prefix',
                    'residual_frame_bytes', 'buffered_output_bytes', 'error_code', 'gzip_error_code',
                    'observed_gzip_error_code'), 'stream')
        exact_keys(snapshot['source'], ('considered', 'context_committed', 'native_committed',
                    'external_observations', 'rejected', 'pending', 'unconsidered_record', 'input_complete',
                    'initialization_verified', 'eligibility', 'physical_position', 'committed_position'), 'source')
        exact_keys(snapshot['context'], ('accepted_records', 'directories', 'lifetime_orders', 'active_orders',
                    'matches', 'initialization_incomplete', 'session_incomplete', 'source_complete',
                    'last_timestamp_ns', 'orders', 'match_references'), 'context')
        for book in snapshot['books']:
            exact_keys(book, ('instrument_id', 'stock_locate', 'derived_sequence', 'revision',
                        'journal_records', 'order_count', 'remaining_quantity', 'needs_recovery',
                        'orders', 'bids', 'asks', 'ledger', 'metadata'), 'book')
            exact_keys(book['metadata'], ('capture_ordinal', 'source_record', 'sequence', 'stream_id',
                        'session', 'dataset', 'version', 'sha256', 'generator_seed', 'origin',
                        'event_timestamp', 'receive_timestamp'), 'metadata')
    resources = output['resources']
    exact_keys(resources, ('allocation_attempts', 'allocations', 'deallocations', 'peak_pmr_bytes',
                'restart_coexistence_peak_pmr_bytes', 'live_pmr_bytes_after_destroy',
                'live_pmr_blocks_after_destroy', 'scope'), 'resources')
    for key in resources:
        if key != 'scope':
            require(type(resources[key]) is int and resources[key] >= 0, 'resource counter invalid: ' + key)
    require(resources['allocations'] == resources['deallocations'] > 0
            and resources['allocation_attempts'] >= resources['allocations'], 'allocator accounting differs')
    require(resources['live_pmr_bytes_after_destroy'] == resources['live_pmr_blocks_after_destroy'] == 0,
            'pipeline/query allocation leak')
    require(0 < resources['peak_pmr_bytes'] <= profile['pmr_budget_bytes'], 'declared PMR budget exceeded')
    require((scenario == 'restart' and 0 < resources['restart_coexistence_peak_pmr_bytes'] <= resources['peak_pmr_bytes'])
            or (scenario != 'restart' and resources['restart_coexistence_peak_pmr_bytes'] == 0),
            'restart coexistence measurement missing/contradictory')
    subset('pipeline PMR plus native queries; fixed objects, fixture and output buffers excluded',
           resources['scope'], '.resources.scope')
    return output


def negative_controls(outputs):
    """Mutate independently checked contracts; every deliberately wrong claim must fail."""
    cases = []
    def add(name, mode, mutate):
        bad = copy.deepcopy(outputs[mode])
        mutate(bad)
        cases.append((name, mode, bad))
    add('contradictory_compressed_digest', 'valid',
        lambda x: x['provenance'].__setitem__('expected_compressed_sha256', '0' * 64))
    add('contradictory_raw_digest', 'valid',
        lambda x: x['provenance'].__setitem__('expected_decompressed_sha256', '0' * 64))
    add('native_provenance_digest', 'valid',
        lambda x: x['final']['books'][0]['metadata'].__setitem__('sha256', '0' * 64))
    add('fifo_priority', 'valid', lambda x: x['final']['books'][0]['orders'][0].__setitem__(4, 0))
    add('wrong_order_identity', 'valid', lambda x: x['final']['books'][0]['orders'][0].__setitem__(0, 102))
    add('wrong_ledger', 'valid', lambda x: x['final']['books'][0]['ledger'].__setitem__(2, 5))
    add('dropped_source_receipt', 'valid', lambda x: x['final']['receipts'].pop())
    add('invented_exchange_time', 'valid', lambda x: x['final']['books'][0]['metadata'].__setitem__('event_timestamp', 1))
    add('observed_origin', 'valid', lambda x: x['provenance'].__setitem__('origin', 'observed'))
    add('false_bounded_publication', 'bounded', lambda x: x['final']['stream'].__setitem__('publication_eligible', True))
    add('false_corrupt_integrity', 'corrupt', lambda x: x['final']['stream'].__setitem__('gzip_member_verified', True))
    add('wrong_restart_prefix', 'restart', lambda x: x['pause']['stream'].__setitem__('accepted_prefix_sha256', '0' * 64))
    add('wrong_restarted_membership', 'restart', lambda x: x['replayed']['books'][1]['orders'][0].__setitem__(3, 19))
    add('unknown_version', 'valid', lambda x: x.__setitem__('schema_version', 2))
    add('bool_disguised_as_integer', 'valid', lambda x: x['final']['stream'].__setitem__('accepted_records', True))
    add('negative_resource_count', 'valid', lambda x: x['resources'].__setitem__('allocations', -1))
    add('false_resource_release', 'valid', lambda x: x['resources'].__setitem__('live_pmr_bytes_after_destroy', 1))
    rejected = []
    for name, scenario, bad in cases:
        try:
            verify_output(bad, scenario)
        except (ValueError, KeyError, TypeError):
            rejected.append(name)
        else:
            raise ValueError('negative control was accepted: ' + name)
    return rejected


def cli_controls(executable):
    invalid = [('short_text', ['valid', 'not-a-hash']),
               ('nonhex64', ['valid', 'g' * 64]), ('quote64', ['valid', '"' * 64]),
               ('short63', ['valid', '1' * 63]), ('long65', ['valid', '1' * 65]),
               ('uppercase64', ['valid', 'A' * 64]), ('invalid_mode', ['unknown', IMPLEMENTATION]),
               ('missing_identity', ['valid']), ('missing_arguments', [])]
    for name, arguments in invalid:
        code, stdout, _ = bounded_run([executable, *arguments])
        require(code != 0 and not stdout, 'invalid CLI must reject without publishing JSON: ' + name)
    # A failed sink is an export failure, not successful delivery. This check does
    # not assert whole-source rollback or persistent crash-safe publication.
    if os.path.exists('/dev/full'):
        with open('/dev/full', 'wb', buffering=0) as sink:
            result = subprocess.run([executable, 'valid', IMPLEMENTATION], stdout=sink,
                                    stderr=subprocess.PIPE, timeout=30)
        require(result.returncode != 0, 'failed output sink reported success')
        return len(invalid) + 1
    return len(invalid)


def normalized(output):
    value = copy.deepcopy(output)
    del value['resources']  # Actual allocation/RSS measurements are separate evidence.
    del value['provenance']['implementation_sha256']  # Caller identity is not fixture semantics.
    return value


def main():
    global IMPLEMENTATION
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable')
    parser.add_argument('--negative-controls', action='store_true')
    parser.add_argument('--implementation-sha256', default=IMPLEMENTATION,
                        help='caller-declared frozen implementation manifest SHA256 (not origin authentication)')
    args = parser.parse_args()
    require(re.fullmatch(r'[0-9a-f]{64}', args.implementation_sha256) is not None,
            'implementation identity must be exactly64 lowercase hexadecimal characters')
    IMPLEMENTATION = args.implementation_sha256
    outputs = {}
    for scenario in ('valid', 'bounded', 'restart', 'corrupt'):
        output = load_output(args.executable, scenario)
        verify_output(output, scenario)
        outputs[scenario] = output
        # A second actual execution must preserve the complete semantic contract;
        # allocator measurements are deliberately outside semantic canonicalization.
        repeated = load_output(args.executable, scenario)
        verify_output(repeated, scenario)
        require(normalized(output) == normalized(repeated), scenario + ': nondeterministic semantic output')
    controls = negative_controls(outputs) if args.negative_controls else []
    cli_checks = cli_controls(args.executable)
    canonical = digest(json.dumps({name: normalized(value) for name, value in outputs.items()},
                                  sort_keys=True, separators=(',', ':')).encode())
    print('PASS: P1I independent end-to-end scenarios=4 repeated_runs=4 '
          f'negative_controls={len(controls)} cli_controls={cli_checks} canonical_sha256={canonical}')


if __name__ == '__main__':
    main()
