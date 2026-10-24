#!/usr/bin/env python3
"""Independent spec-derived auction wire oracle; no production imports."""
import argparse
import hashlib
import json
import random
import struct
import subprocess


def fixtures():
    common = struct.pack('>HH', 1, 65535) + ((1 << 48) - 1).to_bytes(6, 'big')
    return {'K': b'K'+common+b'TEST    '+struct.pack('>IcI',123,b'A',100),
            'J': b'J'+common+b'TEST    '+struct.pack('>IIII',100,101,99,(1<<32)-1),
            'I': b'I'+common+struct.pack('>QQc8sIIIcc',(1<<64)-1,0,b'P',b'TEST    ',100,100,100,b'A',b' '),
            'O': b'O'+common+struct.pack('>8scIIIQII',b'TEST    ',b'Y',90,110,100,(1<<64)-1,99,101)}


def expected(profile, payload):
    lengths = {75:28,74:35,73:50,79:48}
    t=payload[0]
    if len(payload)!=lengths[t]:return {'ok':False,'code':15}
    if profile!=3:return {'ok':False,'code':14}
    # Field checks in wire order; price maximum from official Data Types.
    fields={75:[(11,8,None),(23,1,b'AC'),(24,4,'price')],
            74:[(11,8,None),(19,4,'price'),(23,4,'price'),(27,4,'price')],
            73:[(27,1,b'BSNOP'),(28,8,None),(36,4,'price'),(40,4,'price'),(44,4,'price'),(48,1,b'OCHA'),(49,1,b'L123456789ABC ')],
            79:[(11,8,None),(19,1,b'NY'),(20,4,'price'),(24,4,'price'),(28,4,'price'),(40,4,'price'),(44,4,'price')]}
    for at,n,policy in fields[t]:
        value=payload[at:at+n]
        if policy is None and any(v<32 or v>126 for v in value):return {'ok':False,'code':17}
        if policy=='price' and int.from_bytes(value,'big')>2000000000:return {'ok':False,'code':17}
        if isinstance(policy,bytes) and value[0] not in policy:return {'ok':False,'code':16}
    rebuilt=bytearray(payload)
    numeric={75:[(19,4),(24,4)],74:[(19,4),(23,4),(27,4),(31,4)],73:[(11,8),(19,8),(36,4),(40,4),(44,4)],79:[(20,4),(24,4),(28,4),(32,8),(40,4),(44,4)]}
    for at,n in [(1,2),(3,2),(5,6)]+numeric[t]:rebuilt[at:at+n]=int.from_bytes(payload[at:at+n],'big').to_bytes(n,'big')
    return {'ok':True,'wire':rebuilt.hex(),'origin':2}


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
            if payload[0] in b'KJIO' and rng.randrange(4) == 0:
                start = 28 if payload[0] == ord('I') else 11
                payload[start:start+8] = rng.choice([b'TEST    ', b'TWO     ', b'WRONG   '])
            if payload[0] in b'KIO' and rng.randrange(7) == 0:
                payload[-1] = ord('?')
            candidates.append(bytes(payload))
        for payload in candidates:
            t = chr(payload[0])
            locate = int.from_bytes(payload[1:3], 'big')
            stamp = int.from_bytes(payload[5:11], 'big')
            wire_valid = True if t in 'SR' else expected(3, payload)['ok']
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
                elif t == 'K':
                    valid &= locate == 0 and payload[11:19] in directories.values()
                    release=int.from_bytes(payload[19:23],'big');price=int.from_bytes(payload[24:28],'big')
                    valid &= payload[23]!=ord('C') or (release==0 and price==0)
                    valid &= not(flags&2 and release>=86400)
                else:
                    start=28 if t=='I' else 11
                    valid &= directories.get(locate)==payload[start:start+8]
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
                            'offset': offset, 'version': 4 if valid else 0})
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
        for profile in range(4):
            cases.append((profile, payload))
        for n in range(1, len(payload) + 2):
            if n != len(payload):
                cases.append((3, (payload + b'\0')[:n]))
        for offset in range(11, len(payload)):
            for value in range(256):
                mutated = bytearray(payload)
                mutated[offset] = value
                cases.append((3, bytes(mutated)))
    rng = random.Random(731991)
    for _ in range(10000):
        payload=bytearray(fixtures()['I' if rng.randrange(2) else 'O'])
        payload[1:5]=struct.pack('>HH',rng.getrandbits(16),rng.getrandbits(16))
        payload[5:11]=rng.getrandbits(48).to_bytes(6,'big')
        if payload[0]==ord('I'):
            payload[11:27]=struct.pack('>QQ',rng.getrandbits(64),rng.getrandbits(64))
        else:payload[32:40]=struct.pack('>Q',rng.getrandbits(64))
        cases.append((3,bytes(payload)))
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
        raise AssertionError('independent auction context mismatch')
    if args.negative_control:
        reference[3] = dict(reference[3], wire='00')
        corrupted_context = [list(trace) for trace in context_reference]
        corrupted_context[0][0] = dict(corrupted_context[0][0], accepted=999)
        if context_actual == corrupted_context:
            raise AssertionError('corrupted context expectation escaped detection')
        if actual == reference:
            raise AssertionError('corrupted independent expectation escaped detection')
    elif actual != reference:
        mismatch = next((i for i, (a, b) in enumerate(zip(actual, reference)) if a != b), None)
        raise AssertionError(f'independent auction mismatch at {mismatch}; outputs={len(actual)}/{len(reference)}')
    print(f'AUCTION independent wire_cases={len(cases)} numerical_candidates=10000 seed=731991 '
          f'context_candidates={sum(map(len, context_reference))} sessions={len(traces)} negative_control={args.negative_control} canonical_sha256={canonical}')


if __name__ == '__main__':
    main()
