#!/usr/bin/env python3
"""Independent byte fixture, flat arithmetic and receipt-map benchmark preflight.

No production parser, normalized output or arithmetic is imported. Timing is not an
acceptance threshold. The benchmark's workload includes both creation/destruction
and retained native journals, unlike standalone context throughput.
"""
import hashlib
import json
import struct
import subprocess
import sys

SEED = 0x503147
SYMBOLS = {1: b'TEST    ', 2: b'TWO     '}


def fixture(n):
    def h(kind, locate):
        return kind.encode() + struct.pack('>HH', locate, SEED & 65535) + (1).to_bytes(6, 'big')
    records = [h('S', 0) + b'O']
    for locate in (1, 2):
        records.append(h('R', locate) + struct.pack('>8sccIcc2scccccIc', SYMBOLS[locate], b'Q', b'N', 100, b'N', b'C', b'  ', b'P', b'N', b'N', b'1', b'N', 0, b'N'))
    quantities = {}
    sequences = [0, 0]
    checksum = 0
    mapping = [(0, 1, (1 << 64)-1, (1 << 64)-1), (1, 1, 0, (1 << 64)-1), (2, 1, 1, (1 << 64)-1)]
    for phase in 'AXUE':
        for i in range(n):
            for locate in (1, 2):
                old, new = 4*i+locate, 4*i+locate+2
                if phase == 'A':
                    p = h('A', locate) + struct.pack('>QcI8sI', old, b'B' if locate == 1 else b'S', 10, SYMBOLS[locate], 1000 if locate == 1 else 2000)
                    quantities[old] = 10
                elif phase == 'X':
                    p = h('X', locate) + struct.pack('>QI', old, 3)
                    quantities[old] -= 3
                elif phase == 'U':
                    p = h('U', locate) + struct.pack('>QQII', old, new, 8, 1001 if locate == 1 else 1999)
                    del quantities[old]
                    quantities[new] = 8
                else:
                    p = h('E', locate) + struct.pack('>QIQ', new, 8, 2*i+locate)
                    del quantities[new]
                records.append(p)
                checksum += sum(quantities.values())
                mapping.append((len(records)-1, 0, locate-1, sequences[locate-1]))
                sequences[locate-1] += 1
    if checksum != 100*n*n or quantities:
        raise AssertionError('independent literal conservation')
    framed = b''.join(struct.pack('>H', len(record))+record for record in records)
    fingerprint = 14695981039346656037
    for fields in mapping:
        for value in fields:
            for byte in value.to_bytes(8, 'little'):
                fingerprint = ((fingerprint ^ byte)*1099511628211) % (1 << 64)
    return records, framed, checksum, fingerprint


def main():
    canonical = []
    for n in (1, 8, 32):
        records, framed, checksum, mapping_hash = fixture(n)
        result = json.loads(subprocess.check_output([sys.argv[1], str(n), '3'], text=True))
        expected = dict(workload='synthetic_two_book_reconstruction_v1', orders_per_symbol=n,
                        symbols=2, records=len(records), input_bytes=len(framed),
                        fixture_sha256=hashlib.sha256(framed).hexdigest(), seed=SEED,
                        native_records=8*n, external_records=3, checksum=checksum,
                        receipt_fnv1a64=mapping_hash, lifetime_orders=4*n, matches=2*n,
                        journal_records_per_symbol=4*n, warmups=2, repetitions=3,
                        container_complete=False, initialization='authored_complete_empty_synthetic',
                        live_bytes_after_destroy=0)
        for field, value in expected.items():
            if result[field] != value:
                raise AssertionError((n, field, result[field], value))
        if result['journal_element_bytes'] != 8*n*result['journal_entry_bytes']:
            raise AssertionError('journal element accounting')
        if result['allocations'] != result['allocation_attempts'] or result['deallocations'] != result['allocations']:
            raise AssertionError('allocation/deallocation accounting')
        if result['peak_pmr_bytes'] < result['live_bytes_before_destroy'] or result['peak_pmr_bytes'] > result['pmr_budget_bytes']:
            raise AssertionError('hard PMR budget')
        if result['live_bytes_before_destroy'] < result['journal_element_bytes'] + result['records']*result['source_receipt_bytes'] + result['context_reserved_bytes']:
            raise AssertionError('retained state accounting')
        if len(result['elapsed_ns']) != 3 or any(x <= 0 for x in result['elapsed_ns']):
            raise AssertionError('actual repetitions')
        if result['median_ns_per_record'] <= 0 or result['throughput_records_per_second'] <= 0:
            raise AssertionError('actual timer')
        canonical.append(expected)
    payload = json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode()
    print(json.dumps({'canonical': canonical, 'canonical_sha256': hashlib.sha256(payload).hexdigest()}, sort_keys=True))


if __name__ == '__main__':
    main()
