#!/usr/bin/env python3
"""Independent, authored-synthetic H/Y wire and context model. No production imports.

Expected fields use explicit byte ranges, public profile/error contracts and flat
symbol maps. Canonical identity is calculated from expected values before running
C++; equality against production is required. No observed payload fixtures.
"""
import argparse
import hashlib
import json
import random
import struct
import subprocess

SEED=917717

def header(kind,locate=1,tracking=0,time=1):
    return kind.encode()+struct.pack('>HH',locate,tracking)+time.to_bytes(6,'big')

def status(kind='H',action=b'T',stock=b'TEST    ',locate=1,tracking=0,time=1,reserved=b' ',reason=b'T1  '):
    return header(kind,locate,tracking,time)+stock+action+(reserved+reason if kind=='H' else b'')

def directory(locate=1,stock=b'TEST    ',time=1):
    return header('R',locate,time=time)+struct.pack('>8sccIcc2scccccIc',stock,b'Q',b'N',100,b'N',b'C',b'  ',b'P',b'N',b'N',b'1',b'N',0,b'N')

def system(code,time=1):return header('S',0,time=time)+code.encode()

def failure(code,offset,field):return dict(ok=False,code=code,offset=offset,field=field)

def decode(b,profile=1):
    if profile not in (0,1):return failure(16,2,'decode.profile')
    if not b:return failure(9,2,'type')
    kind=chr(b[0]);length={'H':25,'Y':20}.get(kind)
    if length is None:return failure(13,2,'type')
    if len(b)!=length:return failure(15,2,'payload')
    if not profile:return failure(14,2,'type')
    for at in range(11,19):
        if b[at]<32 or b[at]>126:return failure(17,2+at,'stock')
    if b[19] not in (b'HPQT' if kind=='H' else b'012'):
        return failure(16,21,'trading_state' if kind=='H' else 'reg_sho_action')
    if kind=='H':
        if not 32<=b[20]<=126:return failure(17,22,'reserved')
        for at in range(21,25):
            if not 32<=b[at]<=126:return failure(17,2+at,'reason')
    return dict(ok=True,type=b[0],locate=int.from_bytes(b[1:3],'big'),tracking=int.from_bytes(b[3:5],'big'),timestamp=int.from_bytes(b[5:11],'big'),stock=b[11:19].hex(),action=b[19],reserved=b[20] if kind=='H' else None,reason=b[21:25].hex() if kind=='H' else None,origin=1,seed=7707)

class Model:
    def __init__(self,flags):
        self.flags=flags;self.stage=0;self.dirs={};self.accepted=0;self.offset=0;self.time=None
    def step(self,b):
        status_code=0;code=0;source_code=0;kind=-1;version=0;integration=-1
        wire=None;typ=chr(b[0]) if b else '?'
        if typ in 'HY':
            wire=decode(b)
            if not wire['ok']:status_code=1;code=22;source_code=wire['code']
        elif typ not in 'SR':status_code=3;code=22;source_code=13
        elif len(b)!=({'S':12,'R':39}[typ]):status_code=1;code=22;source_code=15
        if status_code==0:
            ts=int.from_bytes(b[5:11],'big');loc=int.from_bytes(b[1:3],'big')
            if (self.flags&2 and ts>=86400000000000) or (self.flags&1 and self.time is not None and ts<self.time):status_code=2;code=5
            elif self.stage==6 or (typ!='S' and self.stage==0):status_code=2;code=6
            elif typ=='S':
                if loc!=0:status_code=2;code=7
                elif b[11]!=b'OSQMEC'[self.stage]:status_code=2;code=6
                else:self.stage+=1;kind=0
            elif typ=='R':
                symbol=b[11:19]
                if symbol==b' '*8:status_code=2;code=9
                elif loc==0:status_code=2;code=7
                elif loc in self.dirs and self.dirs[loc]!=b[11:]:status_code=2;code=8
                elif loc not in self.dirs and any(v[:8]==symbol for v in self.dirs.values()):status_code=2;code=8
                else:self.dirs[loc]=b[11:];kind=1
            else:
                if loc not in self.dirs:status_code=2;code=7
                elif self.dirs[loc][:8]!=b[11:19]:status_code=2;code=9
                else:kind=10 if typ=='H' else 11
            if status_code==0:
                self.accepted+=1;self.offset+=len(b)+2;self.time=ts;version=2;integration=0
        return dict(status=status_code,code=code,source_code=source_code,accepted=self.accepted,offset=self.offset,directories=len(self.dirs),orders=0,matches=0,kind=kind,normalization=version,integration=integration,incomplete=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('driver');parser.add_argument('--negative-control',action='store_true');args=parser.parse_args()
    rng=random.Random(SEED);commands=[];expected=[];decode_cases=0;context_cases=0
    def dcase(b,p=1):
        nonlocal decode_cases
        commands.append('D '+str(p)+' '+b.hex());expected.append([decode(b,p)]);decode_cases+=1
    for typ,actions in [('H',b'HPQT'),('Y',b'012')]:
        for action in actions:
            for time in [0,86400000000000,(1<<48)-1]:
                for loc in [0,1,65535]:dcase(status(typ,bytes([action]),locate=loc,tracking=65535,time=time))
        base=status(typ,b'T' if typ=='H' else b'0')
        for field in list(range(11,20))+(list(range(20,25)) if typ=='H' else []):
            for byte in range(256):
                altered=bytearray(base);altered[field]=byte;dcase(bytes(altered))
        for size in range(1,len(base)+3):
            if size!=len(base):dcase((base+bytes(2))[:size])
        dcase(base,0);dcase(base,255)
    for _ in range(2000):
        typ=rng.choice('HY');dcase(status(typ,bytes([rng.randrange(256)]),stock=bytes(rng.randrange(32,127) for _ in range(8)),locate=rng.randrange(65536),tracking=rng.randrange(65536),time=rng.randrange(1<<48),reserved=bytes([rng.randrange(256)]),reason=bytes(rng.randrange(256) for _ in range(4))))
    for i in range(320):
        flags=i%4;rows=[status('H'),system('O'),directory(),directory(2,b'TWO     ')];clock=2
        for j in range(40):
            typ=rng.choice('HY');loc=rng.choice([0,1,1,2,2,3]);symbol=b'TWO     ' if loc==2 else b'TEST    '
            action=bytes([rng.choice(b'HPQT?') if typ=='H' else rng.choice(b'012?')]);clock+=1
            t=rng.choice([0,clock,(1<<48)-1])
            rows.append(status(typ,action,stock=symbol,locate=loc,tracking=rng.randrange(65536),time=t))
        rows += [system(c,time=clock+1) for c in 'SQMEC'];rows.append(status('Y',b'0',time=clock+2))
        model=Model(flags);commands.append('C '+str(flags)+' '+' '.join(b.hex() for b in rows));expected.append([model.step(b) for b in rows]);context_cases+=len(rows)
    canonical=hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result=subprocess.run([args.driver,'oracle'],input='\n'.join(commands)+'\n',text=True,capture_output=True,check=True)
    actual=[json.loads(line) for line in result.stdout.splitlines()]
    if len(actual)!=len(expected):raise AssertionError('missing oracle rows')
    if args.negative_control:
        corrupted=json.loads(json.dumps(expected));corrupted[0][0]['timestamp']+=1
        if actual==corrupted:raise AssertionError('negative control not detected')
    if actual!=expected:
        for i,(a,e) in enumerate(zip(actual,expected)):
            if a!=e:raise AssertionError(f'row{i} command={commands[i]} expected={e} actual={a}')
    print(f'HY independent synthetic oracle decode_cases={decode_cases} context_candidates={context_cases} sessions=320 seed={SEED} negative_control={args.negative_control} canonical_sha256={canonical}')

if __name__=='__main__':main()
