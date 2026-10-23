#!/usr/bin/env python3
"""Independent synthetic gzip fixture/integrity/streaming benchmark preflight.

Explicit struct packing and Python's gzip decoder check the C++ fixture encoder.
No production decoder, normalized output or book arithmetic is imported. Timing
values are checked for actual positive samples; there is no throughput target.
"""
import binascii
import gzip
import hashlib
import json
import struct
import subprocess
import sys

SEED = 0x503147
SYMBOLS = {1: b'TEST    ', 2: b'TWO     '}
MASK = (1 << 64)-1


def fixture(n):
    def h(kind, locate):
        return kind.encode() + struct.pack('>HH', locate, SEED & 65535) + (1).to_bytes(6, 'big')
    records = [h('S', 0) + b'O']
    for locate in (1, 2):
        records.append(h('R', locate) + struct.pack('>8sccIcc2scccccIc', SYMBOLS[locate], b'Q', b'N', 100, b'N', b'C', b'  ', b'P', b'N', b'N', b'1', b'N', 0, b'N'))
    mapping = [(0, 1, MASK, MASK), (1, 1, 0, MASK), (2, 1, 1, MASK)]
    sequences = [0, 0]
    quantities = {}
    ledger = [[0]*9 for _ in range(2)]
    for phase in 'AXUE':
        for i in range(n):
            for locate in (1, 2):
                old, new = 4*i+locate, 4*i+locate+2
                book = ledger[locate-1]
                if phase == 'A':
                    p = h('A', locate) + struct.pack('>QcI8sI', old, b'B' if locate == 1 else b'S', 10, SYMBOLS[locate], 1000 if locate == 1 else 2000)
                    quantities[old] = 10
                    book[0] += 10
                    book[7] += 10
                elif phase == 'X':
                    p = h('X', locate) + struct.pack('>QI', old, 3)
                    quantities[old] -= 3
                    book[1] += 3
                    book[8] += 3
                elif phase == 'U':
                    p = h('U', locate) + struct.pack('>QQII', old, new, 8, 1001 if locate == 1 else 1999)
                    book[6] += quantities.pop(old)
                    book[8] += 7
                    quantities[new] = 8
                    book[5] += 8
                    book[7] += 8
                else:
                    p = h('E', locate) + struct.pack('>QIQ', new, 8, 2*i+locate)
                    if quantities.pop(new) != 8:
                        raise AssertionError('independent remaining shares')
                    book[2] += 8
                    book[8] += 8
                records.append(p)
                mapping.append((len(records)-1, 0, locate-1, sequences[locate-1]))
                sequences[locate-1] += 1
    for code in 'SQMEC':
        records.append(h('S', 0)+code.encode())
        mapping.append((len(records)-1, 1, MASK, MASK))
    expected_ledger = [10*n, 3*n, 8*n, 0, 0, 8*n, 7*n, 18*n, 18*n]
    if quantities or ledger != [expected_ledger, expected_ledger]:
        raise AssertionError('independent book conservation')
    prefix = b''.join(struct.pack('>H', len(record))+record for record in records)
    framed = prefix + b'\x00\x00'
    # Separate encoder using Python's native CRC implementation. gzip.decompress
    # below independently validates RFC framing/DEFLATE/trailer for actual bytes.
    compressed = bytearray.fromhex('1f8b08000000000000ff')
    for offset in range(0, len(framed), 65535):
        block = framed[offset:offset+65535]
        compressed += bytes([offset+len(block) == len(framed)])
        compressed += struct.pack('<HH', len(block), len(block) ^ 65535) + block
    compressed += struct.pack('<II', binascii.crc32(framed), len(framed))
    fingerprint = 14695981039346656037
    for fields in mapping:
        for value in fields:
            for byte in value.to_bytes(8, 'little'):
                fingerprint = ((fingerprint ^ byte)*1099511628211) & MASK
    return records, prefix, framed, bytes(compressed), fingerprint


def main():
    driver = sys.argv[1]
    canonical = []
    for n in (8, 32, 128, 256):
        records, prefix, framed, compressed, receipt_hash = fixture(n)
        actual = subprocess.check_output([driver, '--fixture', str(n)])
        if actual != compressed or gzip.decompress(actual) != framed:
            raise AssertionError(('independent gzip fixture', n))
        crc, size = struct.unpack('<II', actual[-8:])
        if crc != binascii.crc32(framed) or size != len(framed):
            raise AssertionError(('gzip CRC/ISIZE', n))
        expected = dict(workload='synthetic_two_book_gzip_streaming_v1',
                        compression_fixture='manual_RFC1951_stored_blocks',
                        orders_per_symbol=n, symbols=2, records=len(records),
                        compressed_bytes=len(compressed), decompressed_bytes=len(framed),
                        accepted_prefix_bytes=len(prefix), seed=SEED,
                        compressed_sha256=hashlib.sha256(compressed).hexdigest(),
                        decompressed_sha256=hashlib.sha256(framed).hexdigest(),
                        accepted_prefix_sha256=hashlib.sha256(prefix).hexdigest(),
                        native_records=8*n, external_records=8,
                        receipt_fnv1a64=receipt_hash, lifetime_orders=4*n,
                        active_orders=0, retired_orders=4*n, matches=2*n,
                        journal_records_per_symbol=4*n, live_bytes_after_destroy=0,
                        source_complete=True, session_complete=True,
                        publication_eligible=True, observed_market_validated=False,
                        initialization='authored_complete_empty_synthetic')
        # Keep CTest quick: every fixture size is independently integrity-checked;
        # n8/n32 additionally run full pipelines under both fragmentation schedules.
        for chunk in (17, 65536) if n <= 32 else ():
            result = json.loads(subprocess.check_output([driver, str(n), '3', str(chunk)], text=True))
            for field, value in expected.items():
                if result[field] != value:
                    raise AssertionError((n, chunk, field, result[field], value))
            if result['input_chunk_bytes'] != chunk or result['warmups'] != 2 or result['repetitions'] != 3:
                raise AssertionError('declared run schedule')
            if result['compressed_input_budget_bytes'] != len(compressed) or result['decompressed_output_budget_bytes'] != len(framed):
                raise AssertionError('explicit byte budget')
            if result['journal_element_bytes'] != 8*n*result['journal_entry_bytes']:
                raise AssertionError('journal element accounting')
            if result['allocations'] != result['allocation_attempts'] or result['deallocations'] != result['allocations']:
                raise AssertionError('allocation/deallocation accounting')
            if result['context_reserved_bytes'] != 2*result['directory_state_bytes']+4*n*result['order_state_bytes']+2*n*result['match_state_bytes']:
                raise AssertionError('context allocation accounting')
            retained = result['journal_element_bytes']+len(records)*result['source_receipt_bytes']+result['context_reserved_bytes']+result['gzip_output_buffer_bytes']+result['framer_buffer_bytes']
            if result['live_bytes_before_destroy'] < retained or result['peak_pmr_bytes'] < result['live_bytes_before_destroy'] or result['peak_pmr_bytes'] > result['pmr_budget_bytes']:
                raise AssertionError('retained state and hard PMR budget')
            if len(result['elapsed_ns']) != 3 or min(result['elapsed_ns']) <= 0:
                raise AssertionError('actual elapsed samples')
            if result['median_ns_per_record'] <= 0 or result['throughput_records_per_second'] <= 0:
                raise AssertionError('actual timer')
        canonical.append(expected)
    payload = json.dumps(canonical, sort_keys=True, separators=(',', ':')).encode()
    print(json.dumps({'canonical': canonical, 'canonical_sha256': hashlib.sha256(payload).hexdigest(),
                      'pipeline_schedules': [[n, chunk] for n in (8, 32) for chunk in (17, 65536)],
                      'fixture_sizes_checked': [8, 32, 128, 256]}, sort_keys=True))


if __name__ == '__main__':
    main()
