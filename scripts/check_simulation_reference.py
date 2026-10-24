#!/usr/bin/env python3
"""Independent sorted-list price/time matching oracle; compares each submitted/cancelled state."""
import random,subprocess,sys
count=0
for seed in [5,42,1729,2027]:
 rng=random.Random(seed);orders=[];fills=[];priority=0;issued=0;submitted=executed=cancelled=expired=rejected=0;commands=[];expected=[];reports=[]
 for _ in range(250):
  if issued and rng.randrange(5)==0:
   identifier=rng.randint(1,issued);commands.append(f'C {identifier}');found=False
   for o in list(orders):
    if o[0]==identifier:
     cancelled+=o[3];reports.append((identifier,2,0,o[3],'-'));orders.remove(o);found=True
   if not found:reports.append((identifier,3,1,0,'-'))
  else:
   issued+=1;identifier=issued;side=rng.randrange(2);price=rng.randint(80,120);quantity=rng.randint(1,20);tif=rng.randrange(3);post=int(tif==0 and rng.randrange(5)==0)
   commands.append(f'S {identifier} {side} {price} {quantity} {tif} {post}');submitted+=quantity
   eligible=sorted([o for o in orders if o[1]!=side and (o[2]<=price if side==0 else o[2]>=price)],key=lambda o:(o[2] if side==0 else -o[2],o[4]))
   if (post and eligible) or (tif==2 and sum(o[3] for o in eligible)<quantity):
    rejected+=quantity;reports.append((identifier,1,2 if post and eligible else 3,quantity,'-'))
   else:
    remaining=quantity;reports.append((identifier,0,0,quantity,'-'))
    for maker in eligible:
     take=min(remaining,maker[3]);index=len(fills);reports.extend([(identifier,5,0,take,index),(maker[0],5,0,take,index)]);fills.append([maker[0],identifier,maker[2],take]);maker[3]-=take;remaining-=take;executed+=2*take
     if maker[3]==0:orders.remove(maker)
     if remaining==0:break
    if remaining:
     if tif==1:expired+=remaining;reports.append((identifier,4,0,remaining,'-'))
     else:orders.append([identifier,side,price,remaining,priority]);priority+=1
  left=str(len(orders))+''.join(' '+':'.join(map(str,o)) for o in orders)
  middle=' |'+''.join(' '+':'.join(map(str,f)) for f in fills)
  expected.append(left+middle+' | '+':'.join(map(str,[submitted,executed,cancelled,expired,rejected]))+' |'+''.join(' '+':'.join(map(str,r)) for r in reports))
 r=subprocess.run([sys.argv[1],'reference'],input='\n'.join(commands)+'\n',text=True,capture_output=True,check=True)
 actual=r.stdout.splitlines();assert len(actual)==len(expected)
 for n,(want,got) in enumerate(zip(expected,actual)):
  if want!=got:raise SystemExit(f'seed={seed}, command={n} {commands[n]}: expected {want}, got {got}')
 count+=len(commands)
print(f'PASS: {count} independent synthetic matching/cancel/client-report states; seeds 5,42,1729,2027')
