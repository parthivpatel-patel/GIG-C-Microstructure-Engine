#!/usr/bin/env python3
"""Independent synthetic S1 ITCH oracle. No market bytes or production parsing imports.

All encoders use struct.pack; reference field extraction uses independent explicit
wire ranges/int.from_bytes. Runs one batched subprocess, fixed random seed 1729.
"""
import argparse
import hashlib
import random
import struct
import subprocess

LENGTHS = dict(zip('S R H Y L V W K J h A F E C X D U P Q B I N O'.split(),
                   [12,39,25,20,26,35,12,28,35,21,36,40,31,36,23,19,35,44,40,19,50,20,48]))
# Fields: wire offsets, byte widths, text flag. Common header deliberately separate.
FIELDS = {
 'S':[(11,1,False)],
 'R':[(11,8,True),(19,1,False),(20,1,False),(21,4,False),(25,1,False),(26,1,False),(27,2,True),(29,1,False),(30,1,False),(31,1,False),(32,1,False),(33,1,False),(34,4,False),(38,1,False)],
 'A':[(11,8,False),(19,1,False),(20,4,False),(24,8,True),(32,4,False)],
 'E':[(11,8,False),(19,4,False),(23,8,False)],
 'X':[(11,8,False),(19,4,False)], 'D':[(11,8,False)],
 'U':[(11,8,False),(19,8,False),(27,4,False),(31,4,False)],
 'Q':[(11,8,False),(19,8,True),(27,4,False),(31,8,False),(39,1,False)],
 'B':[(11,8,False)],
}
FIELDS['F']=FIELDS['A']+[(36,4,True)]
FIELDS['C']=FIELDS['E']+[(31,1,False),(32,4,False)]
FIELDS['P']=FIELDS['A']+[(36,8,False)]

def header(kind, locate=65535, tracking=258, timestamp=(1<<48)-1):
    return kind.encode()+struct.pack('>HH',locate,tracking)+timestamp.to_bytes(6,'big')

def fixtures(rng):
    ref=rng.randrange(1,1<<64); shares=rng.randrange(1,1<<32)
    match=rng.randrange(1<<64); price=rng.randrange(2_000_000_001)
    common=struct.pack('>QcI8sI',ref,b'S',shares,b'TEST    ',price)
    return {
      'S':header('S',0)+b'O',
      'R':header('R')+struct.pack('>8sccIcc2scccccIc',b'TEST    ',b'Q',b'N',100,b'N',b'C',b'  ',b'P',b'N',b'N',b'1',b'N',0,b'N'),
      'A':header('A')+common, 'F':header('F')+common+b'ABCD',
      'E':header('E')+struct.pack('>QIQ',ref,shares,match),
      'C':header('C')+struct.pack('>QIQcI',ref,shares,match,b'Y',price),
      'X':header('X')+struct.pack('>QI',ref,shares),
      'D':header('D')+struct.pack('>Q',ref),
      'U':header('U')+struct.pack('>QQII',ref,ref^1 or 2,shares,price),
      'P':header('P')+struct.pack('>QcI8sIQ',0,b'B',shares,b'TEST    ',price,match),
      'Q':header('Q')+struct.pack('>Q8sIQc',rng.randrange(1<<64),b'TEST    ',price,match,b'O'),
      'B':header('B')+struct.pack('>Q',match),
    }

def oracle(payload):
    kind=chr(payload[0]); parts=['OK',str(payload[0])]
    for off,size,text in [(1,2,False),(3,2,False),(5,6,False)]+FIELDS[kind]:
        value=payload[off:off+size]
        parts.append(value.hex() if text else str(int.from_bytes(value,'big')))
    return ','.join(parts)+',LOC,0,2,0,PROV,1,'+b'synthetic-reference'.hex()+',1729,'+bytes(range(32)).hex()

# Independent validation rules from S1 field contracts. The unsigned reference
# and share fields specify widths, not a nonzero wire restriction. Zero is
# preserved here; contextual order-book validity is a separate future stage.
# Each descriptor is
# (offset, width, field, kind, permitted bytes). Declaration order defines which
# invalid field is reported first. This does not call the C++ decoder or import
# its headers, implementation, generated tables, or constants.
VALIDATION = {
 'S':[(11,1,'event_code','enum',b'OSQMEC')],
 'R':[(11,8,'stock','text',b''),(19,1,'market_category','enum',b'QGSNAPZV '),(20,1,'financial_status','enum',b'DEQSGHJKCN '),(25,1,'round_lots_only','enum',b'YN'),(26,1,'issue_classification','text',b''),(27,2,'issue_subtype','text',b''),(29,1,'authenticity','enum',b'PT'),(30,1,'short_sale_threshold','enum',b'YN '),(31,1,'ipo_flag','enum',b'YN '),(32,1,'luld_tier','enum',b'12 '),(33,1,'etp_flag','enum',b'YN '),(38,1,'inverse','enum',b'YN')],
 'A':[(19,1,'side','enum',b'BS'),(24,8,'stock','text',b''),(32,4,'price','price',b'')],
 'E':[],
 'X':[],
 'D':[],
 'U':[(31,4,'price','price',b'')],
 'Q':[(19,8,'stock','text',b''),(27,4,'cross_price','price',b''),(39,1,'cross_type','enum',b'OCH')],
 'B':[],
}
VALIDATION['F']=VALIDATION['A']+[(36,4,'attribution','text',b'')]
VALIDATION['C']=VALIDATION['E']+[(31,1,'printable','enum',b'YN'),(32,4,'execution_price','price',b'')]
VALIDATION['P']=VALIDATION['A']

def checked_oracle(payload):
    if not payload: return 'ERR,9,2,type,1,0'
    kind=chr(payload[0])
    if kind not in LENGTHS: return f'ERR,13,2,type,0,{payload[0]}'
    if len(payload)!=LENGTHS[kind]: return f'ERR,15,2,payload,{LENGTHS[kind]},{len(payload)}'
    if kind not in FIELDS: return f'ERR,14,2,type,0,{payload[0]}'
    for offset,width,field,rule,choices in VALIDATION[kind]:
        value=int.from_bytes(payload[offset:offset+width],'big')
        if rule=='enum' and value not in choices: return f'ERR,16,{offset+2},{field},0,{value}'
        if rule=='price' and value>2_000_000_000: return f'ERR,17,{offset+2},{field},2000000000,{value}'
        if rule=='text':
            for at in range(offset,offset+width):
                if not 32<=payload[at]<=126: return f'ERR,17,{at+2},{field},0,{payload[at]}'
    return oracle(payload)

def frame_oracle(payloads):
    position=0; pieces=[]
    for ordinal,p in enumerate(payloads):
        pieces.append(f'R,{position},{position+2},{ordinal},{p.hex()};')
        position+=len(p)+2
    return ''.join(pieces)+'END,1,0,0'

def incomplete_frame_oracle(stream):
    # Independent whole-input framing oracle, deliberately no incremental parser.
    position=0;ordinal=0;pieces=[]
    while position<len(stream):
        if len(stream)-position<2:
            return ''.join(pieces)+f'ERR,8,{position},length,2,1'
        length=int.from_bytes(stream[position:position+2],'big')
        if length==0: raise AssertionError('this helper expects unterminated prefixes')
        available=len(stream)-position-2
        if available<length:
            return ''.join(pieces)+f'ERR,9,{position+2},payload,{length},{available}'
        payload=stream[position+2:position+2+length]
        pieces.append(f'R,{position},{position+2},{ordinal},{payload.hex()};')
        position+=length+2;ordinal+=1
    return ''.join(pieces)+f'ERR,10,{position},terminator,2,0'

def compare_rows(labels, expected, actual):
    """Exact comparator shared by real validation and deliberately bad doubles."""
    for row in range(max(len(expected),len(actual))):
        if row>=len(expected) or row>=len(actual):
            raise AssertionError(f'first divergence row={row}: row count expected={len(expected)} actual={len(actual)}')
        if expected[row]!=actual[row]:
            left=expected[row].split(',');right=actual[row].split(',')
            for field in range(max(len(left),len(right))):
                want=left[field] if field<len(left) else '<missing>'
                got=right[field] if field<len(right) else '<missing>'
                if want!=got:
                    raise AssertionError(f'first divergence row={row} label={labels[row]} field={field} expected={want!r} actual={got!r}')


def negative_control(driver):
    """T05: ensure the actual comparator rejects controlled incorrect oracles.

    These doubles alter expected outputs only. They are never injected into
    production code, and do not claim exhaustive proof of oracle correctness.
    """
    payloads=fixtures(random.Random(1729))
    payloads['A']=header('A',258,772,0x010203040506)+struct.pack('>QcI8sI',0x0102030405060708,b'B',0x01020304,b'TEST    ',123456789)
    records=[payloads['A'],payloads['E']]
    labels=['control-A','control-E']
    expected=[oracle(p) for p in records]
    result=subprocess.run([driver],input=''.join('D '+p.hex()+'\n' for p in records),text=True,capture_output=True,check=True)
    actual=result.stdout.splitlines()
    compare_rows(labels,expected,actual)
    doubles=[]
    for name,field,value in [
        ('wrong-endian',4,int.from_bytes(records[0][5:11],'little')),
        ('wrong-field-offset',5,int.from_bytes(records[0][12:20],'big')),
        ('wrong-quantity',7,0x01020304+1),
    ]:
        fields=expected[0].split(',');fields[field]=str(value)
        doubles.append((name,[','.join(fields),expected[1]]))
    doubles.append(('wrong-row-alignment',list(reversed(expected))))
    for name,bad in doubles:
        try: compare_rows(labels,bad,actual)
        except AssertionError as error: print(f'REJECTED {name}: {error}')
        else: raise AssertionError(f'negative-control double escaped detection: {name}')
    print('PASS T05 oracle negative controls: 4/4 rejected; correct baseline accepted')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('driver');parser.add_argument('--negative-control',action='store_true');args=parser.parse_args()
    if args.negative_control:
        negative_control(args.driver)
        return
    rng=random.Random(1729); requests=[]; expected=[]; labels=[]
    def case(request,result,label): requests.append(request);expected.append(result);labels.append(label)
    # Literal S/O golden from the official table: locate/tracking0, timestamp1.
    golden=bytes.fromhex('53000000000000000000014f')
    case('D '+golden.hex(),oracle(golden),'literal-S-O')
    first=fixtures(rng)
    for batch in range(128):
        for kind,payload in fixtures(rng).items():
            assert len(payload)==LENGTHS[kind]
            case('D '+payload.hex(),oracle(payload),f'{kind}-valid-{batch}')
    # Full unsigned integer boundaries, independent from randomized distributions.
    for kind in FIELDS:
        for timestamp in (0,1,0x010203040506,(1<<48)-1):
            payload=bytearray(first[kind]);payload[5:11]=timestamp.to_bytes(6,'big')
            case('D '+payload.hex(),oracle(payload),f'{kind}-time-{timestamp}')
    enum_cases=0
    for kind,offset,choices,field in [('S',11,b'OSQMEC','event_code'),('A',19,b'BS','side'),('C',31,b'YN','printable'),('Q',39,b'OCH','cross_type')]:
        for byte in range(256):
            payload=bytearray(first[kind]);payload[offset]=byte
            expected_value=oracle(payload) if byte in choices else f'ERR,16,{offset+2},{field},0,{byte}'
            case('D '+payload.hex(),expected_value,f'{kind}-enum-{byte}')
            enum_cases+=1
    numeric_cases=0
    for kind,offset,width,values in [('A',11,8,[1,(1<<63)-1,1<<63,(1<<64)-1]),('A',20,4,[1,(1<<32)-1]),('A',32,4,[0,1,2_000_000_000]),('Q',11,8,[0,(1<<64)-1]),('B',11,8,[0,(1<<64)-1])]:
        for value in values:
            payload=bytearray(first[kind]);payload[offset:offset+width]=value.to_bytes(width,'big')
            case('D '+payload.hex(),oracle(payload),f'{kind}-boundary-{offset}-{value}')
            numeric_cases+=1
    for offset,width,field,maximum,value in [(11,8,'order_reference',1,0),(20,4,'shares',1,0),(32,4,'price',2_000_000_000,2_000_000_001),(32,4,'price',2_000_000_000,(1<<32)-1)]:
        payload=bytearray(first['A']);payload[offset:offset+width]=value.to_bytes(width,'big')
        want=oracle(payload) if value==0 else f'ERR,17,{offset+2},{field},{maximum},{value}'
        case('D '+payload.hex(),want,f'A-zero-preservation-or-invalid-price-{offset}-{value}')
        numeric_cases+=1
    payloads=list(first.values());stream=b''.join(struct.pack('>H',len(p))+p for p in payloads)+b'\0\0'
    for chunk in [1,2,3,7,11,12,19,31,64,len(stream)]:
        case(f'F {chunk} {stream.hex()}',frame_oracle(payloads),f'fragments-{chunk}')
    case('F 1 0000','END,1,0,0','empty-terminal')
    truncation_cases=0
    for size in range(len(stream)-1):
        prefix=stream[:size]
        case('F 7 '+(prefix.hex() or '-'),incomplete_frame_oracle(prefix),f'framing-truncate-{size}')
        truncation_cases+=1
    case('F 64 000000','ERR,11,2,trailing,0,1','trailing-after-terminal')
    case('F 1 0001ff0000','R,0,2,0,ff;END,1,0,0','unknown-type-framer-opaque')
    # Negative decode cases compare complete structured wire diagnostics.
    negatives=[]
    for kind,payload in first.items():
        for length in range(len(payload)):
            p=payload[:length]; negatives.append((p,9 if length==0 else 15,f'{kind}-truncate-{length}'))
        negatives.append((payload+b'\0',15,f'{kind}-overlong'))
    for kind,length in LENGTHS.items():
        if kind not in FIELDS: negatives.append((header(kind)+bytes(length-11),14,f'{kind}-unsupported'))
    negatives.append((b'\xff',13,'unknown'))
    for p,code,label in negatives:
        if not p: want='ERR,9,2,type,1,0'
        elif code==15: want=f'ERR,15,2,payload,{LENGTHS[chr(p[0])]},{len(p)}'
        elif code==14: want=f'ERR,14,2,type,0,{p[0]}'
        else: want=f'ERR,13,2,type,0,{p[0]}'
        case('D '+(p.hex() or '-'),want,label)
    # Bounded deterministic adversarial campaign: unrestricted payload bytes,
    # plus 1..4 independent bit mutations of valid records. The complete suite
    # remains 10,000 cases; no coverage is inferred from mere lack of a crash.
    fuzz_rng=random.Random(0x49544348)
    fuzz_cases=6564
    for index in range(fuzz_cases):
        if index<5000:
            payload=bytes(fuzz_rng.randrange(256) for _ in range(fuzz_rng.randrange(65)))
        else:
            payload=bytearray(first[list(first)[fuzz_rng.randrange(len(first))]])
            for _ in range(fuzz_rng.randrange(1,5)):
                payload[fuzz_rng.randrange(len(payload))]^=1<<fuzz_rng.randrange(8)
        case('D '+(payload.hex() or '-'),checked_oracle(payload),f'adversarial-{index}')
    assert len(expected)==10000
    result=subprocess.run([args.driver],input='\n'.join(requests)+'\n',text=True,capture_output=True,check=True)
    lines=result.stdout.splitlines()
    compare_rows(labels,expected,lines)
    digest=hashlib.sha256(result.stdout.encode()).hexdigest()
    print(f'PASS independent ITCH oracle: {len(expected)} cases; seed=1729; canonical_sha256={digest}')
    print(f'coverage: valid={128*12+49}; framing={13+truncation_cases}; enum_sweep={enum_cases}; numeric={numeric_cases}; negative={len(negatives)}; adversarial={fuzz_cases}; no external data')
if __name__=='__main__': main()
