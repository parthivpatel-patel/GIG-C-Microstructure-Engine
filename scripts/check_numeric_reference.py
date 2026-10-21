#!/usr/bin/env python3
"""Arbitrary-precision integer/Fraction oracle, independent of C++ overflow formulas."""
import argparse
from fractions import Fraction
import itertools
import random
import subprocess

p=argparse.ArgumentParser(); p.add_argument('executable'); args=p.parse_args()
rng=random.Random(1729)
lo,hi,umax=-(1<<63),(1<<63)-1,(1<<64)-1
cases=[]; expected=[]
def case(line,answer):
    cases.append(line); expected.append(str(answer))
for signed in (True,False):
    bounds=(lo,hi) if signed else (0,umax)
    edges=[lo,lo+1,-2,-1,0,1,2,hi-1,hi] if signed else [0,1,2,(1<<63),umax-1,umax]
    pairs=list(itertools.product(edges,repeat=2))
    pairs += [(rng.randint(*bounds),rng.randint(*bounds)) for _ in range(1000)]
    for a,b in pairs:
        for suffix,result in [('add',a+b),('sub',a-b),('mul',a*b)]:
            case(('s' if signed else 'u')+suffix+f' {a} {b}',result if bounds[0]<=result<=bounds[1] else 'error')
for decimal in ['0','0.0','1','-1','0.1','0.3','-0.3','0.31','9223372036854775807','-9223372036854775808','18446744073709551615','0.000000000000000001']:
    for n,d in [(1,1),(1,10),(1,100),(3,10),(1,10**18),(umax,umax)]:
        ratio=Fraction(decimal)/Fraction(n,d)
        for op,bounds in [('ticks',(lo,hi)),('lots',(0,umax))]:
            answer=ratio.numerator if ratio.denominator==1 and bounds[0]<=ratio<=bounds[1] else 'error'
            case(f'{op} {decimal} {n} {d}',answer)
for _ in range(1000):
    # Bounded mantissa exactly within parser limits; Fraction determines divisibility.
    mantissa=rng.randint(-10**12,10**12); digits=rng.randint(0,6)
    text=('-' if mantissa<0 else '')+str(abs(mantissa)//10**digits)
    if digits: text+='.'+str(abs(mantissa)%10**digits).zfill(digits)
    n,d=rng.randint(1,10000),10**rng.randint(0,6)
    ratio=Fraction(mantissa,10**digits)/Fraction(n,d)
    for op,bounds in [('ticks',(lo,hi)),('lots',(0,umax))]:
        answer=ratio.numerator if ratio.denominator==1 and bounds[0]<=ratio<=bounds[1] else 'error'
        case(f'{op} {text} {n} {d}',answer)
for malformed in ['+1','1e3','nan','1.','--1','.1','1.2.3','1.0000000000000000001','18446744073709551616']:
    case(f'ticks {malformed} 1 1','error')
case('ticks 1 0 1','error');case('lots 1 1 0','error');case('lots -0 1 1','error')
result=subprocess.run([args.executable],input='\n'.join(cases)+'\n',text=True,capture_output=True,check=True)
actual=result.stdout.splitlines()
if len(actual)!=len(expected): raise SystemExit(f'wrong result count: {len(actual)} != {len(expected)}')
for line,want,got in zip(cases,expected,actual):
    if want!=got: raise SystemExit(f'{line}: expected {want}, got {got}')
print(f'PASS: {len(cases)} independent integer/Fraction reference cases (seed 1729)')
