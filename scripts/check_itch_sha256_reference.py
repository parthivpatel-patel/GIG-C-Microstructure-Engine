#!/usr/bin/env python3
"""Independent hashlib SHA-256 reference for fixed-state synthetic integrity helper."""
import hashlib
import random
import subprocess
import sys
rng = random.Random(0x534841)
lengths = list(range(130)) + [255, 256, 511, 512, 1023, 1024, 4095, 4096, 65535]
values = [bytes(rng.randrange(256) for _ in range(n)) for n in lengths]
actual = subprocess.check_output([sys.argv[1], 'sha256'], input='\n'.join(b.hex() for b in values)+'\n', text=True).splitlines()
expected = [hashlib.sha256(b).hexdigest() for b in values]
assert actual == expected, next(((n,a,b) for n,a,b in zip(lengths,actual,expected) if a != b), 'output count')
print(f'hashlib independent cases={len(values)} canonical_sha256={hashlib.sha256("".join(expected).encode()).hexdigest()}')
