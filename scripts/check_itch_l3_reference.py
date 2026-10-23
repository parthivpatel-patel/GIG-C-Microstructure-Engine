#!/usr/bin/env python3
"""Independent source-byte -> two flat L3 books oracle; synthetic data only.

No production imports, decoder tables or native arithmetic helpers are used.
Fraction supplies the numeric oracle. Expected results are calculated before a
native process is launched. Every attempted candidate has a complete state.
"""
import argparse
import copy
from fractions import Fraction
import hashlib
import json
import itertools
import random
import struct
import subprocess

SEED = 0x503147
SYMBOLS = {1: b'TEST    ', 2: b'TWO     '}
LENGTHS = {'S':12,'R':39,'A':36,'F':40,'E':31,'C':36,'X':23,'D':19,'U':35,'P':44,'Q':40,'B':19}
UNSUPPORTED = {'H':25,'Y':20,'L':26,'V':35,'W':12,'K':28,'J':35,'h':21,'I':50,'N':20,'O':48}


def header(kind, locate=1, time=1, tracking=0):
    return kind.encode() + struct.pack('>HH', locate, tracking) + time.to_bytes(6, 'big')


def system(code, **kw):
    return header('S', 0, **kw) + code.encode()


def directory(locate=1, **kw):
    return header('R', locate, **kw)+struct.pack('>8sccIcc2scccccIc', SYMBOLS[locate], b'Q', b'N', 100, b'N', b'C', b'  ', b'P', b'N', b'N', b'1', b'N', 0, b'N')


def add(ref, qty=10, price=10000, side=b'B', locate=1, attributed=False, **kw):
    return header('F' if attributed else 'A', locate, **kw)+struct.pack('>QcI8sI',ref,side,qty,SYMBOLS[locate],price)+(b'ABCD' if attributed else b'')


def execute(ref, qty=1, match=1, locate=1, price=None, printable=b'Y', **kw):
    return header('E' if price is None else 'C',locate,**kw)+struct.pack('>QIQ',ref,qty,match)+(b'' if price is None else printable+struct.pack('>I',price))


def cancel(ref, qty=None, locate=1, **kw):
    return header('D' if qty is None else 'X',locate,**kw)+struct.pack('>Q',ref)+(b'' if qty is None else struct.pack('>I',qty))


def replace(old,new,qty=10,price=10000,locate=1,**kw):
    return header('U',locate,**kw)+struct.pack('>QQII',old,new,qty,price)


def print_trade(match=1,qty=1,price=10000,locate=1,ref=0,side=b'B',**kw):
    return header('P',locate,**kw)+struct.pack('>QcI8sIQ',ref,side,qty,SYMBOLS[locate],price,match)


def cross(match=1,qty=0,price=10000,locate=1,**kw):
    return header('Q',locate,**kw)+struct.pack('>Q8sIQc',qty,SYMBOLS[locate],price,match,b'O')


def broken(match,locate=1,**kw):
    return header('B',locate,**kw)+struct.pack('>Q',match)


def u(b,i,n):
    return int.from_bytes(b[i:i+n], 'big')


class Refusal(Exception):
    def __init__(self, category):
        self.category=category


class Book:
    def __init__(self):
        self.orders={}
        self.ticket=-1
        self.revision=0
        self.ledger=[0]*9
        self.last_capture=None

    def mutate(self, kind, before, after, qty, ticks, ordinal):
        if kind in 'AFU':
            # Flat set scan is intentionally unrelated to the native price maps.
            for old in self.orders.values():
                if kind=='U' and old[0]==before[0]:
                    continue
                if old[1] != after[2] and ((after[2]==66 and ticks>old[2]) or (after[2]==83 and ticks<old[2])):
                    raise Refusal('native')
        if kind in 'AF':
            self.ticket+=1
            self.orders[after[0]]=[after[0],after[2],ticks,qty,self.ticket]
            self.ledger[0]+=qty
            self.ledger[7]+=qty
        elif kind=='U':
            old=self.orders.pop(before[0])
            self.ledger[6]+=old[3]
            self.ledger[8]+=old[3]
            self.ledger[5]+=qty
            self.ledger[7]+=qty
            self.ticket+=1
            self.orders[after[0]]=[after[0],after[2],ticks,qty,self.ticket]
        else:
            old=self.orders[before[0]]
            delta=old[3] if kind=='D' else qty
            old[3]-=delta
            if not old[3]:
                del self.orders[before[0]]
            category=2 if kind in 'EC' else 1
            self.ledger[category]+=delta
            self.ledger[8]+=delta
        self.revision+=1
        self.last_capture=ordinal

    def state(self):
        orders=sorted(o.copy() for o in self.orders.values())
        depth=[]
        for side in (66,83):
            levels={}
            for _,s,p,q,_ in orders:
                if side==s:
                    amount,count=levels.get(p,(0,0))
                    levels[p]=(amount+q,count+1)
            depth.append([[p,*levels[p]] for p in sorted(levels,reverse=side==66)])
        return dict(orders=orders,revision=self.revision,journal=self.revision,
                    remaining=sum(o[3] for o in orders),count=len(orders),ledger=self.ledger.copy(),
                    bids=depth[0],asks=depth[1],capture=self.last_capture)


class Model:
    def __init__(self, flags=0, tick=(1,100),lot=(1,1),digest=""):
        self.digest=digest
        self.flags=flags
        self.tick=Fraction(*tick)
        self.lot=Fraction(*lot)
        self.directories={}
        self.directory_bytes={}
        self.orders={}
        self.matches={}
        self.stage=0
        self.accepted=0
        self.offset=0
        self.native=0
        self.external=0
        self.last_timestamp=None
        self.books=[Book(),Book()]
        self.receipts=[]
        self.physical=None

    def state(self, committed, category, native_index=None):
        return dict(committed=committed,category=category,book=native_index,
                    source_summary=dict(considered=self.accepted+(not committed),context_committed=self.accepted,rejected=int(not committed),pending=False,input_complete=False,finished=False,initialization_verified=True,unconsidered_record=False,eligibility=1 if committed else 2,physical=self.physical,committed_position=[self.receipts[-1][1],self.receipts[-1][2],self.receipts[-1][0]] if self.receipts else None,native_counts=[b.revision for b in self.books]),
                    context_incomplete=True,context_session_incomplete=True,
                    accepted=self.accepted,offset=self.offset,native=self.native,external=self.external,
                    stage=self.stage,last_timestamp=self.last_timestamp,
                    directories=[[k,v.hex()] for k,v in self.directory_bytes.items()],
                    context_orders=[v.copy() for v in self.orders.values()],
                    matches=[v.copy() for v in self.matches.values()],
                    receipts=copy.deepcopy(self.receipts),
                    books=[self.book_state(i,b) for i,b in enumerate(self.books)])

    def book_state(self,index,book):
        value=book.state()
        value["needs_recovery"]=False
        value["metadata"]=None if book.last_capture is None else dict(instrument=index+1,venue=1,stream=index+1,sequence=book.revision-1,capture=book.last_capture,source_record=f"l3-fixture:{book.last_capture}",event_time=None,receive_time=None,session="synthetic-day",epoch=0,unit=1,dataset="l3-fixture",version="1",license="synthetic-private-evaluation",digest=self.digest,origin=0,source=0,seed=SEED,lineage=[0,3],parent="l3-fixture")
        return value

    def apply(self, payload):
        before=copy.deepcopy(self.__dict__)
        physical=[self.offset,self.offset+2,self.accepted]
        self.physical=physical
        try:
            native_index=self.transition(payload)
        except Refusal as error:
            self.__dict__=before
            self.physical=physical
            return self.state(False,error.category)
        self.receipts.append([self.accepted,self.offset,self.offset+2,payload[0],u(payload,1,2),u(payload,3,2),u(payload,5,6),native_index,self.books[native_index].revision-1 if native_index is not None else None])
        self.accepted+=1
        self.offset+=len(payload)+2
        self.last_timestamp=u(payload,5,6)
        return self.state(True,'native' if native_index is not None else 'external',native_index)

    def transition(self,p):
        def check(condition,category='context'):
            if not condition:
                raise Refusal(category)
        check(bool(p),'source')
        k=chr(p[0])
        check(k in LENGTHS,'unsupported' if k in UNSUPPORTED or k not in LENGTHS else 'source')
        check(len(p)==LENGTHS[k],'source')
        locate=u(p,1,2)
        timestamp=u(p,5,6)
        if k in 'AFP':
            check(p[19] in (66,83),'source')
        if k in 'AFCUPQ':
            at={'A':32,'F':32,'C':32,'U':31,'P':32,'Q':27}[k]
            check(u(p,at,4)<=2_000_000_000,'source')
        if k=='C':check(p[31] in b'YN','source')
        if k=='Q':check(p[39] in b'OCHI','source')
        if k=='S':check(p[11] in b'OSQMEC','source')
        check(self.stage<6)
        if self.flags&4 and self.last_timestamp is not None:
            check(timestamp>=self.last_timestamp)
        if k=='S':
            check(locate==0)
            check(p[11]==b'OSQMEC'[self.stage])
            self.stage+=1
            self.external+=1
            return None
        check(self.stage>0)
        if k=='R':
            stock=p[11:19]
            check(locate>0 and stock!=b'        ')
            check(locate not in self.directory_bytes or self.directory_bytes[locate]==p[11:])
            check(locate in self.directories or stock not in self.directories.values())
            self.directories[locate]=stock
            self.directory_bytes[locate]=p[11:]
            self.external+=1
            return None
        check(locate in self.directories)
        check(locate in SYMBOLS,'binding')
        index=locate-1
        if k in 'AFPQ':
            at=19 if k=='Q' else 24
            check(p[at:at+8]==self.directories[locate])
        old=new=None
        quantity=price=0
        if k in 'AF':
            ref=u(p,11,8)
            check(ref>0 and ref not in self.orders)
            quantity=u(p,20,4)
            price=u(p,32,4)
            check(quantity>0)
            new=[ref,locate,p[19],quantity,price,self.accepted,1,p[36:40].hex() if k=='F' else '']
            self.orders[ref]=new
        elif k in 'ECXDU':
            ref=u(p,11,8)
            check(ref in self.orders)
            old=self.orders[ref].copy()
            check(old[1]==locate and old[6])
            price=old[4]
            if k=='D':quantity=old[3]
            elif k=='U':
                newref=u(p,19,8)
                quantity=u(p,27,4)
                price=u(p,31,4)
                check(newref>0 and newref not in self.orders and quantity>0)
                new=[newref,locate,old[2],quantity,price,self.accepted,1,old[7]]
                self.orders[ref][3]=0
                self.orders[ref][6]=0
                self.orders[newref]=new
            else:
                quantity=u(p,19,4)
                check(0<quantity<=old[3])
                check(k!='X' or quantity<old[3] or self.flags&2)
            if k!='U':
                self.orders[ref][3]-=quantity
                self.orders[ref][6]=int(self.orders[ref][3]>0)
                new=self.orders[ref]
        elif k=='P':
            quantity=u(p,20,4)
            price=u(p,32,4)
        elif k=='Q':
            quantity=u(p,11,8)
            price=u(p,27,4)
        if k in 'ECPQ':
            at=31 if k=='Q' else 36 if k=='P' else 23
            match=u(p,at,8)
            check(match not in self.matches)
            self.matches[match]=[match,locate,0 if k in 'EC' else 1 if k=='P' else 2,0]
        if k=='B':
            match=u(p,11,8)
            check(match in self.matches)
            record=self.matches[match]
            check(record[1]==locate)
            check(record[2]!=2,'unsupported')
            check(not record[3])
            record[3]=1
        if k in 'PQB':
            self.external+=1
            return None
        if k=='C':
            check(bool(self.flags&1),'projection')
        tickvalue=Fraction(price,10000)/self.tick
        lots=Fraction(quantity,1)/self.lot
        check(tickvalue.denominator==1 and 0<tickvalue<=2**63-1,'numeric')
        check(lots.denominator==1 and 0<lots<=2**64-1,'numeric')
        self.books[index].mutate(k,old,new,int(lots),int(tickvalue),self.accepted)
        self.native+=1
        return index


def session(payloads,flags=0,tick=(1,100),lot=(1,1)):
    fixture=b"".join(struct.pack(">H",len(p))+p for p in payloads)+b"\0\0"
    digest=hashlib.sha256(fixture).hexdigest()
    model=Model(flags,tick,lot,digest)
    expected=[]
    for raw in payloads:
        expected.append(model.apply(raw))
        if not expected[-1]['committed']:
            break
    return dict(flags=flags,tick=tick,lot=lot,digest=digest,payloads=payloads[:len(expected)],expected=expected)


def fixtures():
    start=[system('O'),directory(),directory(2)]
    cases=[]
    # G04 literal ledger, with a second symbol between every native transition.
    literal=[add(101,10,10000),add(102,20,10000),execute(102,4,71),cancel(101,3),cancel(101),replace(102,103,15,10100)]
    interleaved=start.copy()
    for i,event in enumerate(literal):
        interleaved.extend([event,add(500+i,2,20000,locate=2)])
    cases.append(session(interleaved))
    assert cases[-1]["expected"][-1]["books"][0]["ledger"]==[30,10,4,0,0,15,16,45,30]
    assert cases[-1]["expected"][-1]["books"][0]["orders"]==[[103,66,101,15,2]]
    # Explicit source families and no-restore corrections.
    cases.append(session(start+[add(1,20,attributed=True),execute(1,5,3,price=9999,printable=b'N'),print_trade(4),broken(4),cross(5),replace(1,2,10),cancel(2),system('S'),system('Q'),system('M'),system('E'),system('C')],1))
    cases.append(session(start+[add(1),add(2),replace(1,3,5),execute(2,2,1),execute(3,5,2)]))
    cases.append(session(start+[add(1,10,10000),add(2,10,10000,side=b'S'),add(3,10,10100)]))
    cases.append(session(start+[add(2**64-1,2**32-1,2_000_000_000),execute(2**64-1,2**32-1,2**64-1)]))
    # Exact fractional units, conversion failures and maximal raw timestamp.
    cases.append(session(start+[add(1,6,10500),execute(1,2,1),cancel(1)],tick=(3,200),lot=(2,1)))
    cases.append(session(start+[add(1,1,10001)]))
    cases.append(session(start+[add(1,3,10000)],lot=(2,1)))
    cases.append(session(start+[add(1,time=2**48-1),cancel(1,time=0)]))
    cases.append(session(start+[add(1,time=9),cancel(1,time=8)],4))
    # Distinct wrong-state/error surfaces, each at an independently valid prefix.
    bad=[add(0),add(1,0),add(1,side=b'?'),execute(1,11),execute(88),cancel(1,10),cancel(1,0),cancel(1,11),cancel(88),replace(1,1),replace(1,0),broken(999),execute(1,1,price=10000),header('H')+b' '*14,b'?',add(1)[:-1]]
    for event in bad:
        cases.append(session(start+[add(1),event]))
    cases.append(session(start+[add(1),cancel(1),add(1)]))
    cases.append(session(start+[add(1),add(1,locate=2)]))
    cases.append(session(start+[add(1),execute(1,1,1),execute(1,1,1)]))
    cases.append(session(start+[print_trade(1),broken(1),broken(1)]))
    cases.append(session(start+[cross(1),broken(1)]))
    cases.append(session(start+[add(1),cancel(1,10)],2))
    return cases


def grammar_fixtures():
    # Yield one bounded session at a time; retaining all independently computed
    # expected prefixes would defeat the oracle's own memory budget.
    start=[system('O'),directory(),directory(2)]
    # Seeded grammar: 1000 independent valid prefixes + one adversarial tail.
    # Attempts are bounded; invalid tails do not authorize corrected source bytes.
    rng=random.Random(SEED)
    for run in range(1000):
        events=start.copy()
        live={}
        nextref=1000
        nextmatch=1
        flags=1|(2 if run%2 else 0)
        for step in range(16):
            if not live or rng.randrange(5)<2:
                locate=rng.choice([1,2]);ref=nextref;nextref+=1
                quantity=rng.randrange(2,30);price=rng.randrange(90,110)*100
                events.append(add(ref,quantity,price,locate=locate,attributed=bool(rng.getrandbits(1))))
                live[ref]=[locate,quantity,price]
            else:
                ref=rng.choice(list(live));locate,qty,price=live[ref]
                choice=rng.randrange(6)
                if choice==0:
                    events.append(cancel(ref,locate=locate));del live[ref]
                elif choice==1:
                    new=nextref;nextref+=1;quantity=rng.randrange(2,30)
                    events.append(replace(ref,new,quantity,price,locate));del live[ref];live[new]=[locate,quantity,price]
                elif choice==2 and qty>1:
                    reduction=rng.randrange(1,qty)
                    events.append(cancel(ref,reduction,locate));live[ref][1]-=reduction
                elif choice in (3,4):
                    reduction=rng.randrange(1,qty+1)
                    events.append(execute(ref,reduction,nextmatch,locate,price+1 if choice==4 else None,printable=b'N'))
                    nextmatch+=1;live[ref][1]-=reduction
                    if not live[ref][1]:del live[ref]
                else:
                    events.append(print_trade(nextmatch,locate=locate));nextmatch+=1
        badkind=run%10
        if badkind==0:tail=add(0)
        elif badkind==1:tail=cancel(2**63)
        elif badkind==2:tail=execute(2**63)
        elif badkind==3:tail=add(nextref,price=10001)
        elif badkind==4:tail=replace(2**63,nextref)
        elif badkind==5:tail=broken(2**63)
        elif badkind==6:tail=add(nextref,side=b'?')
        elif badkind==7:tail=add(nextref,qty=0)
        elif badkind==8:tail=header('H')+b' '*14
        else:tail=b'\xff'
        yield session(events+[tail],flags)



def mutation_fixtures():
    """9,000 individually invalid tails, independent bounded source sessions.

    Together with the 1,000 grammar-session tails these are >=10,000 explicit
    adversarial rejections, not an inflation by counting valid setup records.
    """
    rng=random.Random(SEED ^ 0xBAD)
    prefix=[system('O'),directory(),directory(2),add(1,10)]
    for index in range(9000):
        kind=index%12
        if kind==0:tail=bytes([rng.randrange(128,256)])
        elif kind==1:
            tail=bytearray(add(2));tail[19]=rng.choice(b'?Zz01');tail=bytes(tail)
        elif kind==2:
            wire=add(2);tail=wire[:rng.randrange(1,len(wire))]
        elif kind==3:tail=add(2)+bytes([rng.randrange(256)])
        elif kind==4:tail=add(0)
        elif kind==5:tail=add(1)
        elif kind==6:tail=execute(rng.randrange(10,2**64),1,index+1)
        elif kind==7:tail=cancel(1,rng.randrange(11,2**32))
        elif kind==8:tail=execute(1,1,index+1,price=10000,printable=b'?')
        elif kind==9:tail=replace(1,0)
        elif kind==10:tail=broken(rng.randrange(1,2**64))
        else:
            tail=bytearray(add(2));tail[32:36]=(2_000_000_001+rng.randrange(1_000_000)).to_bytes(4,'big');tail=bytes(tail)
        candidate=session(prefix+[tail],1)
        assert not candidate['expected'][-1]['committed']
        yield candidate


def first_difference(expected,actual,path=''):
    if type(expected)!=type(actual):
        return path,expected,actual
    if isinstance(expected,dict):
        # Driver may expose additional diagnostics, but every oracle field is mandatory.
        for key,value in expected.items():
            if key not in actual:return path+'.'+key,value,'<missing>'
            mismatch=first_difference(value,actual[key],path+'.'+key)
            if mismatch:return mismatch
    elif isinstance(expected,list):
        if len(expected)!=len(actual):return path+'.length',len(expected),len(actual)
        for i,(left,right) in enumerate(zip(expected,actual)):
            mismatch=first_difference(left,right,f'{path}[{i}]')
            if mismatch:return mismatch
    elif expected!=actual:
        return path,expected,actual
    return None


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('driver')
    parser.add_argument('--negative-control',action='store_true')
    parser.add_argument('--batch-size',type=int,default=64)
    args=parser.parse_args()
    if not 1<=args.batch_size<=256:parser.error('batch size must be1..256')
    directed_and_grammar=fixtures()
    truth=directed_and_grammar[0]['expected'][-1]
    cases=iter(directed_and_grammar[:32]) if args.negative_control else itertools.chain(directed_and_grammar,grammar_fixtures(),mutation_fixtures())
    canonical=hashlib.sha256()
    count=sessions=rejected=0
    while True:
        batch=list(itertools.islice(cases,args.batch_size))
        if not batch:break
        encoded=[]
        for c in batch:
            encoded.append(' '.join(map(str,[c['flags'],*c['tick'],*c['lot']]))+' '+c['digest']+' '+' '.join(p.hex() for p in c['payloads']))
        native=subprocess.run([args.driver],input='\n'.join(encoded)+'\n',text=True,capture_output=True,check=True)
        actual=[json.loads(line) for line in native.stdout.splitlines()]
        assert len(actual)==len(batch),(len(actual),len(batch),native.stderr)
        for i,(c,outputs) in enumerate(zip(batch,actual)):
            if len(outputs)!=len(c['expected']):
                raise AssertionError(('output count',sessions+i,len(outputs),len(c['expected'])))
            for j,(expected,observed) in enumerate(zip(c['expected'],outputs)):
                mismatch=first_difference(expected,observed)
                if mismatch:
                    raise AssertionError(dict(seed=SEED,session=sessions+i,candidate=j,fixture_sha256=c['digest'],raw=c['payloads'][j].hex(),difference=mismatch))
                canonical.update(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()+b'\n')
                count+=1
                rejected+=not expected['committed']
        sessions+=len(batch)
    if args.negative_control:
        # Six intentional model defects; these mutate reference expectations only.
        controls=[]
        wrong=copy.deepcopy(truth);wrong['books'][0]['orders'][0][2]*=100;controls.append(wrong)
        # Non-head execution wrongly applied to head (literal state after E1024).
        head_truth=directed_and_grammar[0]['expected'][7]
        wrong=copy.deepcopy(head_truth);wrong['books'][0]['orders'][0][3]-=4;wrong['books'][0]['orders'][1][3]+=4
        assert first_difference(head_truth,wrong) is not None
        # Replacement incorrectly retains the retired identity's priority.
        wrong=copy.deepcopy(truth);wrong['books'][0]['orders'][0][4]=1;controls.append(wrong)
        # A broken-trade observation incorrectly restores liquidity.
        wrong=copy.deepcopy(truth);wrong['books'][0]['orders'][0][3]+=4;controls.append(wrong)
        wrong=copy.deepcopy(truth);wrong['books'].reverse();controls.append(wrong)
        wrong=copy.deepcopy(truth);wrong['accepted']-=1;controls.append(wrong)
        assert all(first_difference(truth,wrong) is not None for wrong in controls)
        print('negative_controls=6 rejected=6')
    else:
        assert count>=10000 and rejected>=10000,(count,rejected)
    print(f'sessions={sessions} source_candidates={count} rejected_candidates={rejected} seed={SEED} canonical_sha256={canonical.hexdigest()}')


if __name__=='__main__':main()
