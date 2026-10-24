#!/usr/bin/env python3
"""Check synthetic benchmark with independently constructed bytes and integer sum."""
import hashlib
import json
import struct
import subprocess
import sys

n = 1000
p = bytearray()
for i in range(n):
    payload = (b'A' + struct.pack('>HH', 1, i % 65536) + (i+1).to_bytes(6, 'big')
               + struct.pack('>QcI8sI', i+1, b'B', 100, b'X       ', 1000000))
    p += struct.pack('>H', len(payload)) + payload
p += b'\0\0'
fingerprint = 14695981039346656037
for b in p:
    fingerprint = ((fingerprint ^ b) * 1099511628211) % (1 << 64)
result = json.loads(subprocess.check_output([sys.argv[1], str(n), '3'], text=True))
expected = {'records': n, 'bytes': len(p), 'repetitions': 3,
            'checksum': sum(2*(i+1)+100+1000000 for i in range(n)),
            'fixture_fnv1a64': fingerprint, 'buffer_bytes': 65535}
for k, v in expected.items():
    if result[k] != v:
        raise RuntimeError((k, result[k], v))
if result['median_ns_per_record'] <= 0 or result['minimum_ns_per_record'] <= 0:
    raise RuntimeError('invalid measurement')
print(json.dumps({'independent_fixture_sha256': hashlib.sha256(p).hexdigest(),
                  'canonical': expected}, sort_keys=True))
