#!/usr/bin/env python3
"""Independent arbitrary-precision Fraction reference; no C++ production formulas imported."""
from fractions import Fraction as F
import itertools,random,subprocess,sys
rng=random.Random(3071);maximum=(1<<64)-1;lo=-(1<<63);hi=(1<<63)-1
cases=list(itertools.product([lo,-1,0,1,hi],[lo,-1,0,1,hi],[(0,0),(1,0),(0,1),(1,1),(maximum-1,1),(1,maximum-1)]))
inputs=[(b,a,x,y) for b,a,(x,y) in cases]
for _ in range(2500):
 b,a=sorted([rng.randint(lo,hi),rng.randint(lo,hi)]);total=rng.randint(2,maximum);x=rng.randint(1,total-1);inputs.append((b,a,x,total-x))
expected=[]
for b,a,x,y in inputs:
 if x and y and b>a: expected.append('error');continue
 v=[F(b) if x else None,F(a) if y else None]
 if x and y: v += [F(a-b),F(a+b,2),F(a*x+b*y,x+y),F(x-y,x+y)]
 else: v += [None]*4
 v += [F(x),F(y),F(x-y,x+y) if x and y else None]
 expected.append(' '.join(f'{z.numerator}/{z.denominator}' if z is not None else 'NA' for z in v))
r=subprocess.run([sys.argv[1],'reference'],input='\n'.join(' '.join(map(str,v)) for v in inputs)+'\n',text=True,capture_output=True,check=True)
assert len(r.stdout.splitlines())==len(expected)
for c,e,a in zip(inputs,expected,r.stdout.splitlines()):
 if e!=a:raise SystemExit(f'{c}: expected {e}, got {a}')
print(f'PASS: {len(expected)} independent Fraction book metric cases, seed 3071')
