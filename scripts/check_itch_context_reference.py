#!/usr/bin/env python3
"""Independent synthetic ITCH context/lifecycle oracle (no production imports).

The Python model uses ordinary dictionaries and integer rational-unit checks.
It never invokes the engine book or derives expected state from C++ output.
"""
import argparse
import copy
import hashlib
import random
import struct
import subprocess

SEED = 0x503146
WIRE_LENGTHS=dict(zip('S R H Y L V W K J h A F E C X D U P Q B I N O'.split(),[12,39,25,20,26,35,12,28,35,21,36,40,31,36,23,19,35,44,40,19,50,20,48]))
SUPPORTED=set('SRAFECXDUPQB')


def header(kind, time=1, locate=1):
    return kind.encode()+struct.pack('>HH', locate, 0)+time.to_bytes(6, 'big')


def system(code, time=1):
    return header('S', time, 0)+code.encode()


def directory(time=2):
    return header('R', time)+struct.pack('>8sccIcc2scccccIc', b'TEST    ', b'Q', b'N', 100, b'N', b'C', b'  ', b'P', b'N', b'N', b'1', b'N', 0, b'N')


def add(ref, shares=100, price=123400, side=b'B', time=10, kind='A'):
    payload=header(kind, time)+struct.pack('>QcI8sI', ref, side, shares, b'TEST    ', price)
    return payload+(b'ABCD' if kind=='F' else b'')


def execute(ref, shares, match, time=20, price=None, printable=b'Y'):
    return header('E' if price is None else 'C', time)+struct.pack('>QIQ', ref, shares, match)+(b'' if price is None else struct.pack('>cI', printable, price))


def cancel(ref, shares=None, time=30):
    return header('D' if shares is None else 'X', time)+struct.pack('>Q', ref)+(b'' if shares is None else struct.pack('>I', shares))


def replace(old, new, shares=200, price=123500, time=40):
    return header('U', time)+struct.pack('>QQII', old, new, shares, price)


def broken(match, time=50):
    return header('B', time)+struct.pack('>Q', match)


def scalar(payload, offset, width):
    return int.from_bytes(payload[offset:offset+width], 'big')


def order_text(order):
    if order is None:
        return '-'
    return ','.join(str(value) for value in order)


PROVENANCE = '1,'+b'synthetic-context'.hex()+',1729,'+bytes(range(32)).hex()
MANIFEST = b'synthetic-context'.hex()+','+b'synthetic-day'.hex()+',1,'+PROVENANCE


class Model:
    def __init__(self, quantum=100, lots=10, order_cap=8, match_cap=6, flags=0):
        self.quantum=quantum
        self.lots=lots
        self.order_cap=order_cap
        self.match_cap=match_cap
        self.flags=flags
        self.directories={}
        self.orders={}
        self.matches={}
        self.stage=0
        self.accepted=0
        self.offset=0
        self.last=None
        self.last_timestamp=None
        self.finished=0
        self.source_complete=0
        self.bounded_prefix=0
        self.session_incomplete=1

    def state(self):
        active=sum(order[-1] for order in self.orders.values())
        summary=[self.accepted,len(self.directories),len(self.orders),len(self.matches),active]
        summary+=list(self.last) if self.last else ['-','-','-']
        summary+=[self.last_timestamp if self.last_timestamp is not None else '-',1,self.finished,self.source_complete,self.bounded_prefix,self.session_incomplete,0]
        directories=''.join(f'{locate},{payload.hex()}/' for locate,payload in self.directories.items())
        orders=''.join(order_text(order)+'/' for order in self.orders.values())
        matches=''.join(','.join(map(str,match))+'/' for match in self.matches.values())
        return '|S:'+','.join(map(str,summary))+'|D:'+directories+'|O:'+orders+'|M:'+matches

    def apply(self, payload):
        if isinstance(payload,str):
            if not self.finished:
                self.finished=1;self.source_complete=int(payload=='!1');self.bounded_prefix=int(payload=='!0')
                self.session_incomplete=int(not(self.source_complete and self.stage==6))
            return '0,0,,0,0,0,0,0,0,0,,0,0|N:-'+self.state()
        # Independent source-boundary cases: framing-independent exact S1
        # lengths, unsupported type registry, and controlled invalid side.
        source_error=None
        payload_offset=self.offset+2
        if not payload:source_error=(9,payload_offset,'type',1,0)
        else:
            kind=chr(payload[0])
            if kind not in WIRE_LENGTHS:source_error=(13,payload_offset,'type',0,payload[0])
            elif len(payload)!=WIRE_LENGTHS[kind]:source_error=(15,payload_offset,'payload',WIRE_LENGTHS[kind],len(payload))
            elif kind not in SUPPORTED:source_error=(14,payload_offset,'type',0,payload[0])
            elif kind in 'AFP' and payload[19] not in b'BS':source_error=(16,payload_offset+19,'side',0,payload[19])
        if source_error:
            code,offset,field,want,got=source_error
            status=3 if code in (13,14) else 1
            location=(self.offset,self.offset+2,self.accepted)
            return ','.join(map(str,[status,22,field,want,got,*location,code,offset,field,want,got]))+'|N:-'+self.state()
        before_snapshot=copy.deepcopy(self.__dict__)
        kind=chr(payload[0]);locate=scalar(payload,1,2);timestamp=scalar(payload,5,6)
        location=(self.offset,self.offset+2,self.accepted)
        before=None;after=None;execution_price=None;printable=None;ticks=None;lots=None
        semantic={'S':0,'R':1,'A':2,'F':2,'E':3,'C':3,'X':4,'D':5,'U':6,'P':7,'Q':8,'B':9}[kind]
        integration=0
        status=0
        error=None
        def fail(code,field,expected=0,actual=0,status_value=2):
            nonlocal error
            if error is None:error=(status_value,code,field,expected,actual)
        if self.finished:fail(23,'finished')
        if self.flags&1 and self.last_timestamp is not None and timestamp<self.last_timestamp:
            fail(5,'timestamp')
        if self.flags&2 and timestamp>=86_400_000_000_000:
            fail(5,'timestamp')
        if self.stage==6:fail(6,'after_end_of_messages')
        if kind!='S' and self.stage==0:fail(6,'start_of_messages')
        if kind=='S':
            code=chr(payload[11]);expected='OSQMEC'[self.stage] if self.stage<6 else '?'
            if locate!=0:fail(7,'global_stock_locate',0,locate)
            if code!=expected:fail(6,'system_event',ord(expected),ord(code))
            if error is None:self.stage+=1
        elif self.stage==0 or self.stage==6:
            fail(6,'after_end_of_messages' if self.stage==6 else 'start_of_messages')
        elif kind=='R':
            # A printable wire field still needs a nonempty contextual identity.
            # This admission policy preserves the original bytes on rejection.
            if payload[11:19]==b'        ':fail(9,'empty_stock')
            if locate==0:fail(7,'stock_locate')
            existing=self.directories.get(locate)
            if existing is not None and existing!=payload[11:]:fail(8,'directory')
            if existing is None and any(p[:8]==payload[11:19] for p in self.directories.values()):fail(8,'stock_mapping')
            if existing is None and len(self.directories)>=8:fail(20,'storage',status_value=5)
            if error is None:self.directories[locate]=payload[11:]
        else:
            directory_payload=self.directories.get(locate)
            if directory_payload is None:fail(7,'stock_locate')
            if kind in 'AFPQ' and directory_payload is not None:
                stock=payload[19:27] if kind=='Q' else payload[24:32]
                if stock!=directory_payload[:8]:fail(9,'stock')
            if kind in 'AF':
                ref=scalar(payload,11,8);quantity=scalar(payload,20,4);price=scalar(payload,32,4)
                if ref==0:fail(10,'order_reference')
                elif ref in self.orders:fail(11,'order_reference')
                if quantity==0:fail(14,'shares')
                if error is None and len(self.orders)>=self.order_cap:fail(20,'storage',status_value=5)
                if error is None:
                    after=[ref,locate,payload[24:32].hex(),payload[19],quantity,price,payload[36:40].hex() if kind=='F' else '-',self.accepted,1]
                    self.orders[ref]=after.copy()
                integration=1
            elif kind in 'ECXDU':
                ref=scalar(payload,11,8);original=self.orders.get(ref)
                if original is None:fail(12,'order_reference')
                elif original[1]!=locate:fail(9,'stock_locate')
                elif not original[-1]:fail(13,'order_reference')
                if error is None:
                    before=original.copy();after=original.copy()
                    if kind=='D':
                        quantity=original[4];price=original[5];after[4]=0;after[-1]=0
                    elif kind=='U':
                        new=scalar(payload,19,8);quantity=scalar(payload,27,4);price=scalar(payload,31,4)
                        if new==0:fail(10,'new_reference')
                        elif new in self.orders:fail(11,'new_reference')
                        if quantity==0:fail(14,'shares')
                        if error is None and len(self.orders)>=self.order_cap:fail(20,'storage',status_value=5)
                        after=[new,locate,original[2],original[3],quantity,price,original[6],self.accepted,1]
                    else:
                        quantity=scalar(payload,19,4);price=original[5]
                        if quantity==0:fail(14,'executed_shares' if kind in 'EC' else 'cancelled_shares')
                        if kind in 'EC' and scalar(payload,23,8) in self.matches:fail(17,'match_number')
                        if quantity>original[4]:fail(15,'executed_shares' if kind in 'EC' else 'cancelled_shares')
                        elif kind=='X' and quantity==original[4] and not self.flags&4:fail(16,'cancelled_shares')
                        after[4]-=quantity;after[-1]=int(after[4]!=0)
                    if error is None:
                        if kind=='U':
                            self.orders[ref][4]=0;self.orders[ref][-1]=0
                            self.orders[after[0]]=after.copy()
                        else:self.orders[ref]=after.copy()
                integration=1
                if kind=='C':
                    execution_price=scalar(payload,32,4);printable=payload[31]
                    if before is not None and execution_price!=before[5]:integration=2;status=4
            elif kind=='P':
                quantity=scalar(payload,20,4);price=scalar(payload,32,4)
                execution_price=price
                integration=1
            elif kind=='Q':
                quantity=scalar(payload,11,8);price=scalar(payload,27,4)
                execution_price=price
                integration=3;status=4
            if kind in 'ECPQ':
                at={'E':23,'C':23,'P':36,'Q':31}[kind];match=scalar(payload,at,8)
                if match in self.matches:fail(17,'match_number')
                if error is None and len(self.matches)>=self.match_cap:fail(20,'storage',status_value=5)
                if error is None:self.matches[match]=[match,locate,0 if kind in 'EC' else 1 if kind=='P' else 2,0]
            elif kind=='B':
                match=scalar(payload,11,8);state=self.matches.get(match)
                if state is None:fail(18,'match_number')
                elif state[1]!=locate:fail(9,'stock_locate')
                elif state[2]==2:fail(22,'cross_break',status_value=3)
                elif state[3]:fail(19,'match_number')
                if error is None:self.matches[match][-1]=1
                integration=3;status=4
            if kind not in 'B' and 'quantity' in locals() and error is None:
                if price==0 or quantity==0 or price%self.quantum or quantity%self.lots:
                    status=4
                if price>0 and price%self.quantum==0:ticks=price//self.quantum
                if quantity>0 and quantity%self.lots==0:lots=quantity//self.lots
        if error:
            self.__dict__=before_snapshot
            status,code,field,expected,actual=error
            prefix=','.join(map(str,[status,code,field,expected,actual,*location,0,0,'',0,0]))
            return prefix+'|N:-'+self.state()
        normalized=','.join(map(str,[semantic,integration,payload.hex(),*location]))+';'+PROVENANCE+';'+MANIFEST+';'+order_text(before)+';'+order_text(after)+';'+str(execution_price if execution_price is not None else '-')+';'+str(printable if printable is not None else '-')+';'+str(ticks if ticks is not None else '-')+';'+str(lots if lots is not None else '-')+';1;P:'+','.join(map(str,[1,8,self.order_cap,self.match_cap,4194304,0,2,0,int(bool(self.flags&1)),int(bool(self.flags&2)),1,int(bool(self.flags&4)),self.quantum,self.lots]))
        self.last=location;self.last_timestamp=timestamp;self.accepted+=1;self.offset+=len(payload)+2
        error_code=21 if status==4 and integration==1 else 22 if status==4 else 0
        error_field='native_units' if error_code==21 else 'native_contract' if error_code==22 else ''
        error_location=location if error_code else (0,0,0)
        prefix=','.join(map(str,[status,error_code,error_field,0,0,*error_location,0,0,'',0,0]))
        return prefix+'|N:'+normalized+self.state()


def trade(match, quantity=100, price=123400, time=20, cross=False):
    if cross:
        return header('Q',time)+struct.pack('>Q8sIQc',quantity,b'TEST    ',price,match,b'O')
    return header('P',time)+struct.pack('>QcI8sIQ',0,b'B',quantity,b'TEST    ',price,match)


def compare(expected, actual, label):
    if expected==actual:return
    left=expected.split('~');right=actual.split('~')
    for index in range(max(len(left),len(right))):
        want=left[index] if index<len(left) else '<missing>'
        got=right[index] if index<len(right) else '<missing>'
        if want!=got:
            raise AssertionError(f'{label} first divergence event={index}\nexpected={want}\nactual={got}')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('driver')
    parser.add_argument('--negative-control',action='store_true')
    args=parser.parse_args()
    golden=[system('O'),directory(),system('S',3),system('Q',4),add(1,100),execute(1,40,11),cancel(1,10),replace(1,2,200),execute(2,50,12,price=123600),broken(12),cancel(2),add(2),system('M',60),system('E',61),cancel(1),system('C',62),system('O',63)]
    # Hand-computed lifecycle oracle: each tuple is the complete reference-size
    # and match-correction state after that candidate (including rejections).
    golden_states=[
        (1,{},{}),(2,{},{}),(3,{},{}),(4,{},{}),
        (5,{1:(100,1)},{}),(6,{1:(60,1)},{11:0}),
        (7,{1:(50,1)},{11:0}),
        (8,{1:(0,0),2:(200,1)},{11:0}),
        (9,{1:(0,0),2:(150,1)},{11:0,12:0}),
        (10,{1:(0,0),2:(150,1)},{11:0,12:1}),
        (11,{1:(0,0),2:(0,0)},{11:0,12:1}),
        (11,{1:(0,0),2:(0,0)},{11:0,12:1}),
        (12,{1:(0,0),2:(0,0)},{11:0,12:1}),
        (13,{1:(0,0),2:(0,0)},{11:0,12:1}),
        (13,{1:(0,0),2:(0,0)},{11:0,12:1}),
        (14,{1:(0,0),2:(0,0)},{11:0,12:1}),
        (14,{1:(0,0),2:(0,0)},{11:0,12:1}),
    ]
    hand=Model()
    for index,(payload,want) in enumerate(zip(golden,golden_states)):
        hand.apply(payload)
        got=(hand.accepted,{ref:(state[4],state[8]) for ref,state in hand.orders.items()},{ref:state[3] for ref,state in hand.matches.items()})
        if want!=got:raise AssertionError(f'hand golden state event={index}: expected={want} actual={got}')
    requests=[];expected=[];labels=[];events=0
    def case(sequence,config=(100,10,8,6,0),label=''):
        nonlocal events
        model=Model(*config)
        expected.append('~'.join(model.apply(payload) for payload in sequence))
        requests.append(' '.join(map(str,config))+' '+ ' '.join((p.hex() or '-') if isinstance(p,bytes) else p for p in sequence))
        labels.append(label);events+=len(sequence)
    case(golden,label='hand-authored-lifecycle')
    rng=random.Random(SEED)
    for session in range(0 if args.negative_control else 500):
        sequence=[system('O'),directory(),system('S',3),system('Q',4)]
        for step in range(20):
            time=100+step;ref=rng.randrange(13);quantity=rng.choice([0,1,10,50,100,200,0xffffffff]);price=rng.choice([0,123400,123450,2_000_000_000])
            action=rng.randrange(10)
            if action<2:payload=add(ref,quantity,price,b'B' if rng.randrange(2) else b'S',time,'F' if action else 'A')
            elif action==2:payload=execute(ref,quantity,rng.randrange(8),time)
            elif action==3:payload=execute(ref,quantity,rng.randrange(8),time,price,b'N' if rng.randrange(2) else b'Y')
            elif action==4:payload=cancel(ref,quantity,time)
            elif action==5:payload=cancel(ref,time=time)
            elif action==6:payload=replace(ref,rng.randrange(13),quantity,price,time)
            elif action==7:payload=trade(rng.randrange(8),quantity,price,time,cross=bool(rng.randrange(2)))
            elif action==8:payload=broken(rng.randrange(8),time)
            else:payload=system(rng.choice('OSQMEC'),time)
            sequence.append(payload)
        case(sequence,config=(rng.choice([1,100]),rng.choice([1,10]),rng.choice([2,8]),rng.choice([2,6]),rng.choice([0,1,4])),label=f'property-session-{session}')
    if not args.negative_control:
        # Independent multisymbol identity and high-unsigned-reference fixtures.
        second_directory=bytearray(directory());second_directory[1:3]=struct.pack('>H',2);second_directory[11:19]=b'ALT     '
        second_add=bytearray(add((1<<64)-1,100,123400,b'S'));second_add[1:3]=struct.pack('>H',2);second_add[24:32]=b'ALT     '
        second_execute=bytearray(execute((1<<64)-1,40,(1<<64)-1));second_execute[1:3]=struct.pack('>H',2)
        case([system('O'),directory(),bytes(second_directory),add(1),bytes(second_add),execute((1<<64)-1,40,2),bytes(second_execute)],label='multisymbol-high-references')
        case([directory(),system('O'),add(1),directory(),directory(),add(1)],label='initialization-and-directory-retry')
        for flags in (0,1,2,3):
            case([system('O',0),directory(1),add(1,time=(1<<48)-1),add(2,time=0),add(3,time=86_400_000_000_000-1)],config=(1,1,8,6,flags),label=f'clock-policy-{flags}')
    if not args.negative_control:
        case([system('O'),directory(),add(1),b'',b'\xff',header('H')+bytes(14),add(2)[:20],add(2,side=b'Z'),add(2)],label='source-boundary-error-atomicity')
        blank_directory=bytearray(directory());blank_directory[11:19]=b'        '
        case([system('O'),bytes(blank_directory),bytes(blank_directory),directory(),directory(),add(1)],label='blank-symbol-admission-atomicity')
        for ending in ('!0','!1','!2'):
            case([system('O'),ending,add(1),ending],label='finish-partial-'+ending)
            case([system(code,index) for index,code in enumerate('OSQMEC')]+[ending,system('O',7),ending],label='finish-complete-'+ending)
    result=subprocess.run([args.driver],input='\n'.join(requests)+'\n',text=True,capture_output=True,check=True)
    actual=result.stdout.splitlines()
    if len(actual)!=len(expected):raise AssertionError(f'row count expected={len(expected)} actual={len(actual)} stderr={result.stderr}')
    for want,got,label in zip(expected,actual,labels):compare(want,got,label)
    if args.negative_control:
        correct=expected[0].split('~')
        doubles=[]
        bad=correct.copy();bad[5]=bad[5].replace(',60,123400,',',61,123400,');doubles.append(('wrong-remaining-after-execution',bad))
        bad=correct.copy();bad[11]=bad[11].replace('2,11,order_reference','0,0,order_reference',1);doubles.append(('accept-retired-reference-reuse',bad))
        bad=correct.copy();bad[9]=bad[9].replace(',150,123500,',',200,123500,');doubles.append(('broken-trade-restores-liquidity',bad))
        bad=correct.copy();bad[4],bad[5]=bad[5],bad[4];doubles.append(('wrong-event-alignment',bad))
        for name,bad in doubles:
            try:compare('~'.join(bad),actual[0],name)
            except AssertionError as error:print('REJECTED '+str(error).split('\n')[0])
            else:raise AssertionError(f'negative control escaped: {name}')
        print('PASS context oracle negative controls: 4/4 rejected; correct baseline accepted')
        return
    print(f'PASS context independent oracle: sessions={len(expected)} events={events} randomized_mutations=10000 seed={SEED} canonical_sha256={hashlib.sha256(result.stdout.encode()).hexdigest()}')

if __name__=='__main__':main()
