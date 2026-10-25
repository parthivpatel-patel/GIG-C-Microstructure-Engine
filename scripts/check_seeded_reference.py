#!/usr/bin/env python3
"""Independent authored-snapshot -> flat-book differential validation, never observed."""
import copy
import hashlib
import json
import random
import struct
import sys
from pathlib import Path
import check_itch_l3_reference as ref
from check_adapter_differential import run
from check_initialization_manifest import load


def seed_digest(m):
    parts=[]
    def n(x):parts.append(struct.pack('>Q',x))
    def text(s):
        b=s.encode() if isinstance(s,str) else s;n(len(b));parts.append(b)
    text('gig.typed_seed.v1');text('synthetic-l3');text('synthetic-day')
    b=m['event_boundary'];n(b['frame_offset']);n(b['payload_offset']);n(b['ordinal']);n(m['session_stage']);n(1);n(m['last_timestamp'])
    dirs=sorted(ref.directory(i) for i in (1,2));n(2);parts.extend(dirs)
    orders=sorted(m['snapshot']['orders'],key=lambda x:x['reference']);n(len(orders))
    for o in orders:
        n(o['reference']);n(o['locate']);text(ref.SYMBOLS[o['locate']]);n(ord(o['side']));n(o['remaining']);n(o['price4']);n(0);n(o['arrival']);n(1);n(o['priority'])
    retired=sorted(m['snapshot']['retired_references']);n(len(retired))
    for x in retired:n(x)
    matches=sorted(m['snapshot']['matches'],key=lambda x:x['number']);n(len(matches))
    for x in matches:n(x['number']);n(x['locate']);n({'execution':0,'print':1,'cross':2}[x['kind']]);n(int(x['broken']))
    return hashlib.sha256(b''.join(parts)).hexdigest()


class SeedModel(ref.Model):
    def __init__(self,m,digest):
        super().__init__(1,(1,10000),(1,1),digest)
        self.start=m['event_boundary']['ordinal'];self.accepted=self.start
        self.offset=m['event_boundary']['frame_offset'];self.initial_stage=m['session_stage'];self.stage=self.initial_stage
        self.last_timestamp=m['last_timestamp'];self.retired=set(m['snapshot']['retired_references'])
        for i in (1,2):self.directories[i]=ref.SYMBOLS[i];self.directory_bytes[i]=ref.directory(i)[11:]
        for o in sorted(m['snapshot']['orders'],key=lambda x:x['reference']):
            self.orders[o['reference']]=[o['reference'],o['locate'],ord(o['side']),o['remaining'],o['price4'],o['arrival'],1,'']
            book=self.books[o['locate']-1];book.orders[o['reference']]=[o['reference'],ord(o['side']),o['price4'],o['remaining'],o['priority']]
            book.ticket=max(book.ticket,o['priority'])
        for book in self.books:
            book.revision=1;book.last_capture=self.start-1
            total=sum(o[3] for o in book.orders.values());book.ledger[4]=total;book.ledger[7]=total
        for x in m['snapshot']['matches']:self.matches[x['number']]=[x['number'],x['locate'],{'execution':0,'print':1,'cross':2}[x['kind']],int(x['broken'])]
    def state(self,committed,category,native_index=None):
        value=super().state(committed,category,native_index)
        for key in ('considered','context_committed'):value['source_summary'][key]-=self.start
        value['source_summary']['native_counts']=[b.revision-1 for b in self.books]
        value['source_summary']['eligibility']=3 if committed else 2
        value['accepted']-=self.start;value['stage']-=self.initial_stage
        value['context_incomplete']=False
        if not self.receipts:value['offset']=0
        return value
    def book_state(self,index,book):
        value=super().book_state(index,book)
        value['metadata']['lineage']=[0,3,3]
        if book.revision==1:value['metadata']['source_record']='l3-fixture'
        return value
    def apply(self,p):
        if chr(p[0]) in 'AFECXDU' and (ref.u(p,11,8) in self.retired or (chr(p[0])=='U' and ref.u(p,19,8) in self.retired)):
            self.physical=[self.offset,self.offset+2,self.accepted];return self.state(False,'context')
        return super().apply(p)


def encoded(m,payloads,digest,chunk):
    b=m['event_boundary'];tokens=[1,1,10000,1,1,digest,b['frame_offset'],b['ordinal'],m['session_stage'],m['last_timestamp'],len(m['snapshot']['orders'])]
    for o in m['snapshot']['orders']:tokens.extend([o['reference'],o['locate'],ord(o['side']),o['remaining'],o['price4'],o['priority'],o['arrival']])
    retired=m['snapshot']['retired_references'];tokens.extend([len(retired),*retired]);matches=m['snapshot']['matches'];tokens.append(len(matches))
    for x in matches:tokens.extend([x['number'],x['locate'],{'execution':0,'print':1,'cross':2}[x['kind']],int(x['broken'])])
    tokens.extend([ref.directory(1).hex(),ref.directory(2).hex(),seed_digest(m),*[p.hex() for p in payloads]])
    return (' '.join(map(str,tokens))+'\n').encode()


def cases():
    m=load(Path(__file__).resolve().parents[1]/'tests/fixtures/market_seed_manifest.json')
    base=[ref.execute(11,2,71),ref.replace(12,13,9,101),ref.cancel(11,1),ref.cancel(13),ref.add(14,5,100),ref.execute(21,2,72,locate=2),ref.broken(70),ref.system('E'),ref.system('C')]
    yield m,base
    for p in [ref.execute(11,11,71),ref.cancel(11,11),ref.add(11,1,100),ref.add(9,1,100),ref.execute(9,1,71),ref.execute(999,1,71),ref.replace(11,9,1,100),ref.execute(11,1,70),ref.broken(999),b'?'+b'\0'*11]:yield m,[p]
    rng=random.Random(0x53454544)
    for _ in range(64):
        events=[];left=10
        for i in range(6):
            q=rng.randint(1,max(1,left+1));events.append(ref.execute(11,q,100+i))
            if q>left:break
            left-=q
            if left==0:break
        yield m,events
    large=copy.deepcopy(m);large['snapshot']['orders']=[]
    for locate in (1,2):
        for i in range(64):large['snapshot']['orders'].append(dict(reference=locate*1000+i,locate=locate,side='B' if locate==1 else 'S',price4=(100 if locate==1 else 200)+(i%8),remaining=2**32-1,priority=i+1,arrival=(locate-1)*64+i))
    large['event_boundary'].update(ordinal=1000)
    yield large,[ref.execute(1000,1,800),ref.cancel(2063,1,locate=2),ref.replace(1001,9000,1,100)]


def main(driver,report=None):
    digest=hashlib.sha256();sessions=events=0;measurements=[]
    for m,payloads in cases():
        raw=b''.join(struct.pack('>H',len(p))+p for p in payloads)+b'\0\0';source_digest=hashlib.sha256(raw).hexdigest()
        model=SeedModel(m,source_digest);initial=model.state(True,'external');expected=[]
        for p in payloads:
            state=model.apply(p);expected.append(state)
            if not state['committed']:break
        for chunk in (1,257):
            actual=run([driver,'--seed',str(chunk)],encoded(m,payloads,source_digest,chunk))
            assert actual['seed_sha256']==seed_digest(m),'independent binary snapshot digest'
            difference=ref.first_difference(initial,actual['initial'])
            assert not difference,('seed initial',difference)
            if sessions==0:
                for field in ('quantity','priority','accounting'):
                    wrong=copy.deepcopy(initial)
                    if field=='quantity':wrong['books'][0]['orders'][0][3]+=1
                    elif field=='priority':wrong['books'][0]['orders'][0][4]+=1
                    else:wrong['source_summary']['considered']+=1
                    assert ref.first_difference(wrong,actual['initial']),field
            difference=ref.first_difference(expected,actual['events'])
            assert not difference,('seed event',sessions,difference)
            digest.update(json.dumps(dict(initial=initial,events=expected),sort_keys=True,separators=(',',':')).encode())
            measurements.append(actual['measurements']);sessions+=1;events+=len(expected)
    evidence=dict(scope='independent authored seeded L3, not observed',schedules=sessions,event_prefixes=events,seed=0x53454544,canonical_sha256=digest.hexdigest(),measurements=measurements,failures=0,negative_controls=3,observed_validated=False)
    if report:Path(report).write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({k:v for k,v in evidence.items() if k!='measurements'},sort_keys=True));return evidence

if __name__=='__main__':main(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
