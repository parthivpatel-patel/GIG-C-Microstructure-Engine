#!/usr/bin/env python3
"""Independent fixed-width RNG and explicit quantity-then-price fixture contract."""
import subprocess
import sys
MASK=(1<<64)-1

def expected(count,seed):
    state=seed
    def draw():
        nonlocal state
        state^=(state<<13)&MASK
        state^=state>>7
        state^=(state<<17)&MASK
        return state
    rows=[]
    for index in range(count):
        quantity=10+draw()%91
        side=index%2
        price=(100 if side==0 else 200)+draw()%16
        rows.append(f'{index+1} {side} {price} {quantity}')
    return rows

for seed in [1,42,1729,MASK]:
    for count in [1,16,512,2048]:
        result=subprocess.run([sys.argv[1],str(count),str(seed)],capture_output=True,text=True,check=True)
        lines=result.stdout.splitlines();want=expected(count,seed)
        if lines[1:]!=want:
            mismatch=next((i for i,(a,b) in enumerate(zip(lines[1:],want)) if a!=b),min(len(lines)-1,len(want)))
            raise SystemExit(f'FAIL: seed={seed}, count={count}, row={mismatch}, expected={want[mismatch:mismatch+1]}, got={lines[1+mismatch:2+mismatch]}')
        if lines[0]!='phase2-benchmark-generator-v2 2 2 2':raise SystemExit('FAIL: fixture generator version not v2')
print('PASS:16 fixture cases,4 seeds, counts1/16/512/2048; explicit fixed-width quantity-then-price reference')
