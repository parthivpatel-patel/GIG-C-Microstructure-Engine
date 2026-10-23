#!/usr/bin/env python3
"""Independent field packing/checksum and context benchmark correctness preflight."""
import hashlib
import json
import struct
import subprocess
import sys
n = 32
h = lambda kind,loc=1:kind.encode()+struct.pack('>HH',loc,0)+bytes.fromhex('000000000001')
records = [h('S',0)+b'O',h('R')+struct.pack('>8sccIcc2scccccIc',b'TEST    ',b'Q',b'N',100,b'N',b'C',b'  ',b'P',b'N',b'N',b'1',b'N',0,b'N')]
records += [h('A')+struct.pack('>QcI8sI',2*i+1,b'B',10,b'TEST    ',1000) for i in range(n)]
records += [h('X')+struct.pack('>QI',2*i+1,3) for i in range(n)]
records += [h('U')+struct.pack('>QQII',2*i+1,2*i+2,8,1001) for i in range(n)]
records += [h('E')+struct.pack('>QIQ',2*i+2,8,i+1) for i in range(n)]
payload = b''.join(records)
fingerprint = 14695981039346656037
for byte in payload:
    fingerprint = ((fingerprint ^ byte)*1099511628211) % (1<<64)
r = json.loads(subprocess.check_output([sys.argv[1], str(n), '3'], text=True))
expected = {'records':len(records),'checksum':25*n,'lifetime_orders':2*n,'retired_orders':2*n,'matches':n,'fixture_fnv1a64':fingerprint,'warmups':2,'repetitions':3,'allocations':3}
for key,value in expected.items():
    if r[key] != value:
        raise AssertionError((key,r[key],value))
if r['reserved_bytes'] != r['directory_state_bytes']+2*n*r['order_state_bytes']+n*r['match_state_bytes']:
    raise AssertionError('reservation accounting')
print(json.dumps({'canonical':expected,'independent_payload_sha256':hashlib.sha256(payload).hexdigest()},sort_keys=True))
