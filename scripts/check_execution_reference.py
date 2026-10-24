#!/usr/bin/env python3
from fractions import Fraction as F
import random,subprocess,sys
rng=random.Random(6011);lines=[];expected=[]
def schedule(items):return str(len(items))+''.join(f' {t}:{q}' for t,q in items)
for _ in range(700):
 n=rng.randint(1,16);target=rng.randint(1,(1<<64)-1);weights=[rng.randint(0,(1<<64)-1) for _ in range(n)]
 total=sum(weights);quotas=[F(target*w,total) for w in weights];alloc=[q.numerator//q.denominator for q in quotas]
 remainder=sorted(range(n),key=lambda i:(-(quotas[i]-alloc[i]),i))
 for i in remainder[:target-sum(alloc)]:alloc[i]+=1
 lines.append('W '+str(target)+' '+str(n)+' '+' '.join(map(str,weights)));expected.append(schedule([(1000*i//n,q) for i,q in enumerate(alloc) if q]))
for _ in range(700):
 n=rng.randint(1,16);target=rng.randint(1,100000);den=rng.randint(1,1000);num=rng.randint(0,den);vol=[rng.randint(0,10000) for _ in range(n)];items=[];total=0;submitted=0
 for i,q in enumerate(vol):
  total+=q;budget=min(target,int(F(total*num,den)))
  if budget>submitted:items.append((i+1,budget-submitted));submitted=budget
 lines.append(f'P {target} {num} {den} {n} '+' '.join(map(str,vol)));expected.append(schedule(items))
for _ in range(1200):
 side=rng.randrange(2);target=rng.randint(1,10**12);q=rng.randint(1,target);p,a,d,t=[rng.randint(1,10000) for _ in range(4)];fn=rng.randint(-10,10);fd=rng.randint(1,100);sign=-1 if side else 1
 fee=F(fn,fd)*q;delay=sign*(d-a)*q;spread=sign*(p-d)*q;slip=delay+spread;opp=sign*(t-a)*(target-q);short=slip+fee+opp
 values=[F(p),F(p*q),F(delay),F(spread),fee,F(slip),F(opp),short,short/100]
 lines.append(f'C {side} {target} {q} {p} {a} {d} {t} {fn} {fd}');expected.append(' '.join(f'{v.numerator}/{v.denominator}' for v in values))
# Python arbitrary-precision integers independently decide the symmetric 127-bit
# magnitude boundary, including signed-minimum times zero and every sign pair.
limit=(1<<127)-1
boundary=[0,1,2,3,(1<<63)-1,1<<63,1<<64,1<<126,limit//3,limit//2,limit,1<<127]
pairs=[(a*sa,b*sb) for a in boundary for b in boundary for sa in [-1,1] for sb in [-1,1] if a*sa<=(limit) and b*sb<=limit]
for _ in range(2000):
 pairs.append((rng.randrange(-limit-1,limit+1),rng.randrange(-limit-1,limit+1)))
def limbs(value):
 magnitude=abs(value)
 return f'{magnitude>>64} {magnitude&((1<<64)-1)} {int(value<0)}'
for a,b in pairs:
 product=a*b
 lines.append('M '+limbs(a)+' '+limbs(b))
 expected.append(str(product) if -limit<=product<=limit else 'overflow')
r=subprocess.run([sys.argv[1],'reference'],input='\n'.join(lines)+'\n',capture_output=True,text=True,check=True);actual=r.stdout.splitlines();assert len(actual)==len(expected)
for line,want,got in zip(lines,expected,actual):
 if want!=got:raise SystemExit(f'{line}: expected {want}, got {got}')
print(f'PASS: {len(lines)} independent Fraction/integer arithmetic, apportionment, participation and cost cases; seed 6011')
