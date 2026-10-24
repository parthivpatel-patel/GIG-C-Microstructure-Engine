#!/usr/bin/env python3
from fractions import Fraction as F
import random,subprocess,sys
rng=random.Random(4099);cases=[];expected=[]
for _ in range(2000):
 b=rng.randint(1,1000);a=b+rng.randint(0,10);c=rng.randint(1,1000);d=c+rng.randint(0,10)
 x,y,z,w=[rng.randint(1,10**12) for _ in range(4)];p=rng.randint(max(1,b-5),a+5)
 m0=F(a+b,2);m1=F(c+d,2);ofi=(z if c>=b else 0)-(x if c<=b else 0)-(w if d<=a else 0)+(y if d>=a else 0)
 sign=1 if p>m0 else -1 if p<m0 else 0
 values=[F(ofi),F(10**8),F(10**8),m1/m0-1,(m1/m0-1)**2]
 fields=[f'{v.numerator}/{v.denominator}' for v in values]+[str(1 if sign==1 else 2 if sign==-1 else 0)]
 for v in ([2*sign*(p-m0),2*sign*(p-m1),2*sign*(m1-m0)] if sign else [None]*3):fields.append('NA' if v is None else f'{v.numerator}/{v.denominator}')
 cases.append((b,a,x,y,c,d,z,w,p));expected.append(' '.join(fields))
r=subprocess.run([sys.argv[1],'reference'],input='\n'.join(' '.join(map(str,c)) for c in cases)+'\n',text=True,capture_output=True,check=True)
assert len(r.stdout.splitlines())==len(expected)
for c,want,got in zip(cases,expected,r.stdout.splitlines()):
 if want!=got:raise SystemExit(f'{c}: {want} != {got}')
print(f'PASS: {len(cases)} independent Fraction flow cases, seed 4099')
