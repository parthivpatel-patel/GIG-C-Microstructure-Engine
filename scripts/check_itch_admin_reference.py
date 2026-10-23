#!/usr/bin/env python3
"""Independent spec-derived administrative wire oracle; no production imports."""
import argparse
import hashlib
import json
import random
import struct
import subprocess


def fixtures():
    common = struct.pack('>HH', 1, 65535) + ((1 << 48) - 1).to_bytes(6, 'big')
    return {'L': b'L' + common + b'MPIDTEST    YNA',
            'V': b'V' + common + struct.pack('>QQQ', 0, (1 << 64) - 1, 1 << 32),
            'W': b'W' + common + b'1',
            'h': b'h' + common + b'TEST    QH',
            'N': b'N' + common + b'TEST    A'}


def expected(profile, payload):
    lengths = {76: 26, 86: 35, 87: 12, 104: 21, 78: 20}
    t = payload[0]
    if len(payload) != lengths[t]:
        return {'ok': False, 'code': 15}
    if profile != 2:
        return {'ok': False, 'code': 14}
    # Validation follows field offset order, independently from the C++ reader.
    fields = {76: [(11, 12, None), (23, 1, b'YN'), (24, 1, b'NPSRL'), (25, 1, b'AEWSD')],
              86: [], 87: [(11, 1, b'123')],
              104: [(11, 8, None), (19, 1, b'QBX'), (20, 1, b'HT')],
              78: [(11, 8, None), (19, 1, b'BSAN')]}
    for offset, width, choices in fields[t]:
        field = payload[offset:offset + width]
        if choices is None and any(b < 32 or b > 126 for b in field):
            return {'ok': False, 'code': 17}
        if choices is not None and field[0] not in choices:
            return {'ok': False, 'code': 16}
    # Decode and encode full-width independent integer references without float.
    locate, tracking = struct.unpack_from('>HH', payload, 1)
    stamp = int.from_bytes(payload[5:11], 'big')
    rebuilt = bytes([t]) + struct.pack('>HH', locate, tracking) + stamp.to_bytes(6, 'big')
    if t == 86:
        rebuilt += struct.pack('>QQQ', *struct.unpack_from('>QQQ', payload, 11))
    else:
        rebuilt += payload[11:]
    return {'ok': True, 'wire': rebuilt.hex(), 'origin': 2}


def context_cases():
    rng = random.Random(817321)
    traces, truth = [], []
    bases = fixtures()
    for session in range(320):
        flags = session % 4
        stage = accepted = offset = 0
        last_time = None
        directories = {}
        candidates, results = [], []
        def system(code):
            return b'S' + b'\0' * 10 + code.encode()
        def directory(locate, stock):
            return (b'R' + struct.pack('>HH', locate, 9) + (1).to_bytes(6, 'big')
                    + stock + b'QN' + struct.pack('>I', 100) + b'NC  P N1N'
                    + struct.pack('>I', 0) + b'N')
        inventory = [system(c) for c in 'OSQMEC']
        inventory += [directory(1, b'TEST    '), directory(2, b'TWO     ')]
        inventory += list(bases.values())
        candidates = [system('O'), directory(1, b'TEST    '), directory(2, b'TWO     ')]
        for _ in range(50):
            payload = bytearray(rng.choice(inventory))
            payload[5:11] = rng.choice([0, 1, 2, (1 << 48) - 1]).to_bytes(6, 'big')
            if rng.randrange(4) == 0:
                payload[1:3] = struct.pack('>H', rng.choice([0, 1, 2, 65535]))
            if payload[0] in b'LhN' and rng.randrange(4) == 0:
                start = 15 if payload[0] == ord('L') else 11
                payload[start:start+8] = rng.choice([b'TEST    ', b'TWO     ', b'WRONG   '])
            if payload[0] in b'WhN' and rng.randrange(7) == 0:
                payload[-1] = ord('?')
            candidates.append(bytes(payload))
        for payload in candidates:
            t = chr(payload[0])
            locate = int.from_bytes(payload[1:3], 'big')
            stamp = int.from_bytes(payload[5:11], 'big')
            wire_valid = True if t in 'SR' else expected(2, payload)['ok']
            valid = wire_valid and stage < 6
            valid &= not(flags & 1 and last_time is not None and stamp < last_time)
            valid &= not(flags & 2 and stamp >= 86400000000000)
            if t == 'S':
                valid &= locate == 0 and payload[11] == ord('OSQMEC'[min(stage, 5)])
            else:
                valid &= stage != 0
                if t == 'R':
                    stock = payload[11:19]
                    valid &= locate != 0 and (locate not in directories or directories[locate] == stock)
                    valid &= all(key == locate or value != stock for key, value in directories.items())
                elif t in 'VW':
                    valid &= locate == 0
                else:
                    start = 15 if t == 'L' else 11
                    valid &= directories.get(locate) == payload[start:start+8]
            if valid:
                accepted += 1
                offset += len(payload) + 2
                last_time = stamp
                if t == 'S':
                    stage += 1
                if t == 'R':
                    directories[locate] = payload[11:19]
            results.append({'committed': bool(valid), 'accepted': accepted,
                            'directories': len(directories), 'orders': 0, 'matches': 0,
                            'offset': offset, 'version': 3 if valid else 0})
        traces.append(str(flags) + ' ' + ' '.join(b.hex() for b in candidates))
        truth.append(results)
    return traces, truth


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('driver')
    ap.add_argument('--negative-control', action='store_true')
    args = ap.parse_args()
    cases = []
    for payload in fixtures().values():
        for profile in range(3):
            cases.append((profile, payload))
        for n in range(1, len(payload) + 2):
            if n != len(payload):
                cases.append((2, (payload + b'\0')[:n]))
        for offset in range(11, len(payload)):
            for value in range(256):
                mutated = bytearray(payload)
                mutated[offset] = value
                cases.append((2, bytes(mutated)))
    rng = random.Random(731991)
    for _ in range(10000):
        values = [rng.getrandbits(64) for _ in range(3)]
        header = struct.pack('>HH', rng.getrandbits(16), rng.getrandbits(16))
        cases.append((2, b'V' + header + rng.getrandbits(48).to_bytes(6, 'big')
                      + struct.pack('>QQQ', *values)))
    reference = [expected(p, b) for p, b in cases]
    traces, context_reference = context_cases()
    canonical = hashlib.sha256(json.dumps([reference, context_reference], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    result = subprocess.run([args.driver, 'oracle'],
                            input=''.join(f'{p} {b.hex()}\n' for p, b in cases),
                            capture_output=True, text=True, check=True)
    actual = [json.loads(line) for line in result.stdout.splitlines()]
    context_run = subprocess.run([args.driver, 'context_oracle'], input='\n'.join(traces)+'\n', capture_output=True, text=True, check=True)
    context_actual = [json.loads(line) for line in context_run.stdout.splitlines()]
    if context_actual != context_reference:
        raise AssertionError('independent administrative context mismatch')
    if args.negative_control:
        reference[2] = dict(reference[2], wire='00')
        corrupted_context = [list(trace) for trace in context_reference]
        corrupted_context[0][0] = dict(corrupted_context[0][0], accepted=999)
        if context_actual == corrupted_context:
            raise AssertionError('corrupted context expectation escaped detection')
        if actual == reference:
            raise AssertionError('corrupted independent expectation escaped detection')
    elif actual != reference:
        mismatch = next((i for i, (a, b) in enumerate(zip(actual, reference)) if a != b), None)
        raise AssertionError(f'independent administrative mismatch at {mismatch}; outputs={len(actual)}/{len(reference)}')
    print(f'ADMIN independent wire_cases={len(cases)} numerical_candidates=10000 seed=731991 '
          f'context_candidates={sum(map(len, context_reference))} sessions={len(traces)} negative_control={args.negative_control} canonical_sha256={canonical}')


if __name__ == '__main__':
    main()
