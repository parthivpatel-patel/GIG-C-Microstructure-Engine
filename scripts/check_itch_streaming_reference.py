#!/usr/bin/env python3
"""Independent synthetic gzip -> BinaryFile -> L3 reference checks.

Fixtures are authored here, framed independently and compressed as raw DEFLATE
with an explicitly constructed RFC1952 wrapper and independently calculated CRC
and ISIZE. No NASDAQ or LOBSTER bytes are used. Production output never supplies
expected orders, lifecycle state, ledger arithmetic or source dispositions.
"""
import argparse
import copy
import gzip
import hashlib
import itertools
import json
import struct
import subprocess
import zlib

import check_itch_l3_reference as l3

SEED=0x503148


def binary_file(records,terminal=True):
    return b''.join(struct.pack('>H',len(record))+record for record in records)+(b'\0\0' if terminal else b'')


def gzip_bytes(raw,optional=False,header_crc=True):
    flags=30 if optional else 0
    header=b'\x1f\x8b\x08'+bytes([flags])+b'\0\0\0\0\0\xff'
    if optional:
        extra=b'LX\x02\x00ok'
        header+=struct.pack('<H',len(extra))+extra+b'synthetic.itch\0'+b'private synthetic fixture\0'
        header+=struct.pack('<H',(zlib.crc32(header)&0xffff) if header_crc else ((zlib.crc32(header)^1)&0xffff))
    compressor=zlib.compressobj(6,zlib.DEFLATED,-15)
    body=compressor.compress(raw)+compressor.flush()
    trailer=struct.pack('<II',zlib.crc32(raw)&0xffffffff,len(raw)&0xffffffff)
    result=header+body+trailer
    if not optional or header_crc:
        assert gzip.decompress(result)==raw
    return result


def source_records():
    records=[l3.system('O'),l3.directory(),l3.directory(2),l3.add(101,10),l3.add(201,20,20000,side=b'S',locate=2),l3.add(102,20),l3.execute(102,4,1),l3.cancel(101,3),l3.cancel(101),l3.replace(102,103,15,10100),l3.execute(201,2,2,locate=2,price=20100,printable=b'N'),l3.print_trade(3),l3.cross(4),l3.broken(3),l3.broken(1)]
    records.extend(l3.system(code) for code in 'SQMEC')
    return records


def decompressed_prefix(encoded):
    """Bytewise independent wrapper reference retains output before CRC failure.

    Every source byte is supplied separately, so a failing trailer byte cannot
    hide output produced from preceding compressed data. Empty/raw/zlib formats
    are deliberately not auto-detected.
    """
    decoder=zlib.decompressobj(31)
    out=bytearray()
    error=False
    for byte in encoded:
        try:
            piece=decoder.decompress(bytes([byte]))
        except zlib.error:
            error=True
            break
        out+=piece
        if decoder.eof:
            break
    return bytes(out),decoder.eof,error


def logical_source(raw_prefix,digest):
    model=l3.Model(1,(1,100),(1,1),digest)
    position=0
    state=None
    terminated=False
    framing_error=False
    while position+2<=len(raw_prefix):
        size=int.from_bytes(raw_prefix[position:position+2],'big')
        if size==0:
            terminated=True
            position+=2
            if position!=len(raw_prefix):framing_error=True
            break
        if position+2+size>len(raw_prefix):break
        state=model.apply(raw_prefix[position+2:position+2+size])
        position+=2+size
        if not state['committed']:break
    if state is None:
        state=model.state(True,'external')
        state['source_summary']['considered']=0
    return model,state,position,terminated,framing_error


def test_case(name,raw,encoded=None,chunk=17,cut=None,kind='valid',end=0,compressed_limit=1<<20,decompressed_limit=1<<20,ratio=1024,slack=65536,header_limit=65536,output_buffer=64):
    encoded=gzip_bytes(raw) if encoded is None else encoded
    if cut is None:cut=len(encoded)
    return dict(name=name,raw=raw,encoded=encoded[:cut],full_encoded=encoded,chunk=chunk,kind=kind,end=end,compressed_limit=compressed_limit,decompressed_limit=decompressed_limit,ratio=ratio,slack=slack,header_limit=header_limit,output_buffer=output_buffer,digest=hashlib.sha256(raw).hexdigest(),compressed_digest=hashlib.sha256(encoded).hexdigest())


def fixtures():
    records=source_records()
    raw=binary_file(records)
    compressed=gzip_bytes(raw)
    for pause in range(len(records)+1):
        candidate=test_case('restart-boundary-'+str(pause),raw,compressed,7)
        candidate['pause']=pause
        yield candidate
    for chunk in (1,2,3,7,17,64,len(compressed),len(compressed)+1):
        yield test_case('golden-fragments-'+str(chunk),raw,compressed,chunk)
    for output_buffer in (1,7):
        yield test_case('bounded-output-buffer-'+str(output_buffer),raw,compressed,17,output_buffer=output_buffer)
    optional=gzip_bytes(raw,optional=True)
    for chunk in (1,7,len(optional)):
        yield test_case('optional-header-'+str(chunk),raw,optional,chunk)
    for chunk in (1,len(compressed)):
        bad=bytearray(compressed);bad[-8]^=1
        candidate=test_case('crc-pause-restart-'+str(chunk),raw,bytes(bad),chunk,kind='corrupt')
        candidate['pause']=4
        yield candidate
    for chunk in (1,13,len(compressed)):
        bad=bytearray(compressed);bad[-8]^=1
        yield test_case('corrupt-crc-'+str(chunk),raw,bytes(bad),chunk,kind='corrupt')
        bad=bytearray(compressed);bad[-4]^=1
        yield test_case('corrupt-isize-'+str(chunk),raw,bytes(bad),chunk,kind='corrupt')
    for i in range(len(compressed)):
        yield test_case('truncated-eof-'+str(i),raw,compressed,7,cut=i,kind='truncated')
        yield test_case('bounded-interruption-'+str(i),raw,compressed,7,cut=i,kind='bounded',end=1)
    for name,index,value in [('magic',0,0),('method',2,0),('reserved-flags',3,0xe0)]:
        bad=bytearray(compressed);bad[index]=value
        yield test_case(name,raw,bytes(bad),1,kind='corrupt')
    yield test_case('bad-fhcrc',raw,gzip_bytes(raw,optional=True,header_crc=False),1,kind='corrupt')
    yield test_case('header-cap',raw,optional,1,kind='header_limit',header_limit=16)
    yield test_case('concat-members',raw,compressed+compressed,1,kind='trailing')
    yield test_case('trailing-garbage',raw,compressed+b'garbage',1,kind='trailing')
    yield test_case('compressed-cap',raw,compressed,1,kind='compressed_limit',compressed_limit=len(compressed)-1,header_limit=10)
    yield test_case('decompressed-cap',raw,compressed,1,kind='decompressed_limit',decompressed_limit=len(raw)-1)
    yield test_case('decompressed-exact-cap',raw,compressed,1,decompressed_limit=len(raw))
    yield test_case('compressed-exact-cap',raw,compressed,1,compressed_limit=len(compressed))
    yield test_case('expansion-limit',raw,compressed,1,kind='expansion_limit',ratio=1,slack=0)
    yield test_case('binaryfile-missing-terminal',raw[:-2],kind='framing')
    yield test_case('binaryfile-trailing',raw+b'X',kind='framing')
    yield test_case('binaryfile-truncated-length',b'\x00',kind='framing')
    yield test_case('binaryfile-truncated-payload',b'\xff\xff'+b'A'*20,kind='framing')
    yield test_case('binaryfile-invalid-message-length',b'\x00\x01A\x00\x00',kind='semantic')
    unsupported=binary_file(records[:3]+[l3.header('H')+b' '*14]+records[3:])
    yield test_case('unsupported-itch',unsupported,kind='semantic')
    lifecycle=binary_file(records[:3]+[l3.execute(999,1,1)]+records[3:])
    yield test_case('unknown-order',lifecycle,kind='semantic')
    no_start=binary_file([l3.directory(),l3.add(1)])
    yield test_case('missing-lifecycle-start',no_start,kind='semantic')
    # A permitted empty gzip member is not a complete BinaryFile source.
    yield test_case('empty-gzip',b'',kind='framing')
    wrong=test_case('wrong-compressed-identity',raw,compressed,kind='identity')
    wrong['compressed_digest']='0'*64
    yield wrong
    wrong=test_case('wrong-decompressed-identity',raw,compressed,kind='identity')
    wrong['digest']='0'*64
    yield wrong


def gzip_header_size(encoded):
    if len(encoded)<10:return None
    flags=encoded[3]
    at=10
    if flags&4:
        if len(encoded)<at+2:return None
        at+=2+int.from_bytes(encoded[at:at+2],'little')
        if len(encoded)<at:return None
    for flag in (8,16):
        if flags&flag:
            found=encoded.find(b'\0',at)
            if found<0:return None
            at=found+1
    if flags&2:at+=2
    return at if at<=len(encoded) else None


def gzip_reference(case):
    decoder=zlib.decompressobj(31)
    out=bytearray()
    encoded=case['encoded']
    header_end=gzip_header_size(case['full_encoded'])
    compressed=0
    error=0
    verified=False
    for byte in encoded:
        if verified:
            error=9 # explicit single-member/trailing-data rejection
            break
        if compressed==case['compressed_limit']:
            error=3
            break
        if compressed==case['header_limit'] and (header_end is None or compressed<header_end):
            error=6
            break
        compressed+=1
        try:piece=decoder.decompress(bytes([byte]))
        except zlib.error:
            error=7
            break
        allowed_ratio=case['slack']+case['ratio']*compressed
        allowed=min(case['decompressed_limit'],allowed_ratio)
        available=max(0,allowed-len(out))
        out+=piece[:available]
        if len(piece)>available:
            error=4 if case['decompressed_limit']<=allowed_ratio else 5
            break
        if decoder.eof:verified=True
    if not error and not verified and not case['end']:error=8
    return dict(output=bytes(out),compressed=compressed,error=error,verified=verified)


def expected(case):
    reference=gzip_reference(case)
    raw=reference['output']
    model,state,position,terminated,trailing=logical_source(raw,case['digest'])
    semantic_failure=not state['committed']
    framing_error=0
    error=0
    gzip_error=reference['error']
    if semantic_failure:error=3
    elif trailing:error=2;framing_error=11
    elif gzip_error:error=1
    elif not case['end'] and not terminated:
        error=2
        if len(raw)-position==1:framing_error=8
        elif len(raw)-position>=2:framing_error=9
        else:framing_error=10
    compressed_actual=hashlib.sha256(case['encoded'][:reference['compressed']]).hexdigest()
    decompressed_actual=hashlib.sha256(raw).hexdigest()
    accepted_bytes=model.offset
    compressed_identity=reference['verified'] and compressed_actual==case['compressed_digest']
    decompressed_identity=reference['verified'] and decompressed_actual==case['digest']
    if not error and not case['end'] and not(compressed_identity and decompressed_identity):error=4
    complete=not error and not case['end'] and reference['verified'] and terminated
    stream=dict(accepted_prefix=accepted_bytes,source_records=model.accepted+int(semantic_failure),accepted_records=model.accepted,native_records=model.native,external_observations=model.external,
                accepted_prefix_sha256=hashlib.sha256(raw[:accepted_bytes]).hexdigest(),
                framer_terminated=terminated,source_complete=complete,publication_eligible=complete,
                paused=False,finished=True,bounded_prefix=bool(case['end']),error=error,framing_error=framing_error)
    # Native semantic rejection may stop midway through a bounded decompression
    # output. Such transport read-ahead is not a logical source position. Full
    # codecs are independently checked on all nonsemantic fixtures.
    if not semantic_failure and not trailing:
        stream.update(observed_gzip_error=gzip_error,compressed=reference['compressed'],decompressed=len(raw),gzip_verified=reference['verified'],compressed_sha256=compressed_actual,decompressed_sha256=decompressed_actual,compressed_identity=compressed_identity,decompressed_identity=decompressed_identity,gzip_error=gzip_error)
        # BinaryFile consumes every available byte unless a terminal has trailing
        # data. A partial final frame is deliberately not an accepted source row.
        framing_position=position if trailing else len(raw)
        stream['framing']=framing_position
        stream['residual']=0 if terminated else len(raw)-position
        stream['buffered_output_bytes']=0
    # The pipeline seals its scoped context on end; gzip/container validity remains
    # independent from the source's local S/O..S/C observation policy.
    state['source_summary']['finished']=True
    state['source_summary']['input_complete']=complete
    state['source_summary']['eligibility']=1 if complete else 2
    state['context_session_incomplete']=not(complete and model.stage==6)
    if not model.accepted and not semantic_failure:
        for field in ('committed','category','book'):state.pop(field,None)
    return dict(stream=stream,source=state,restart_verified=case.get('pause',-1)>=0)


def encode_case(case):
    fields=[case['chunk'],case['end'],case['compressed_limit'],case['decompressed_limit'],case['ratio'],case['slack'],case['header_limit'],case['output_buffer'],case.get('pause',-1),case['digest'],case['compressed_digest'],case['encoded'].hex() or '-']
    return ' '.join(map(str,fields))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('driver')
    parser.add_argument('--negative-control',action='store_true')
    args=parser.parse_args()
    candidates=list(fixtures())
    if args.negative_control:candidates=[case for case in candidates if case['name']=='golden-fragments-1']
    canonical=hashlib.sha256()
    counts={}
    source_candidates=0
    accepted_records=0
    for start in range(0,len(candidates),32):
        batch=candidates[start:start+32]
        truth=[expected(case) for case in batch]
        result=subprocess.run([args.driver],input='\n'.join(encode_case(case) for case in batch)+'\n',text=True,capture_output=True)
        if result.returncode:raise AssertionError(dict(driver_returncode=result.returncode,stderr=result.stderr,first_fixture=batch[0]['name']))
        outputs=[json.loads(line) for line in result.stdout.splitlines()]
        assert len(outputs)==len(batch),(len(outputs),len(batch))
        for case,reference,actual in zip(batch,truth,outputs):
            mismatch=l3.first_difference(reference,actual)
            if mismatch:raise AssertionError(dict(fixture=case['name'],raw_sha256=hashlib.sha256(case['raw']).hexdigest(),gzip_sha256=hashlib.sha256(case['full_encoded']).hexdigest(),chunk=case['chunk'],difference=mismatch))
            transport=actual['stream']
            # Every reported transport prefix is authenticated against independently
            # authored bytes, even when a semantic/framing stop permits bounded
            # read-ahead differences between caller fragment schedules.
            assert 0<=transport['compressed']<=len(case['encoded'])
            assert 0<=transport['decompressed']<=len(case['raw'])
            assert transport['accepted_prefix']<=transport['framing']<=transport['decompressed']
            assert transport['decompressed']==transport['framing']+transport['buffered_output_bytes']
            if transport['error'] in (2,3):
                # A logical source/framing stop leaves an unverified reader prefix;
                # it does not prove that the unread gzip source is truncated.
                assert transport['observed_gzip_error']==0
            assert transport['compressed_sha256']==hashlib.sha256(case['encoded'][:transport['compressed']]).hexdigest()
            assert transport['decompressed_sha256']==hashlib.sha256(case['raw'][:transport['decompressed']]).hexdigest()
            # Disjoint source accounting is checked even when transport read-ahead
            # is intentionally excluded from semantic rejection expectations.
            summary=actual['source']['source_summary']
            assert summary['considered']==summary['context_committed']+summary['rejected']+int(summary['pending'])
            assert actual['stream']['native_records']+actual['stream']['external_observations']==actual['stream']['accepted_records']
            canonical.update(json.dumps(reference,sort_keys=True,separators=(',',':')).encode()+b'\n')
            counts[case['kind']]=counts.get(case['kind'],0)+1
            source_candidates+=reference['stream']['source_records']
            accepted_records+=reference['stream']['accepted_records']
    if args.negative_control:
        truth=expected(candidates[0]);controls=[]
        for change in ('crc','complete','restore','sequence','digest','source_count'):
            wrong=copy.deepcopy(truth)
            if change=='crc':wrong['stream']['gzip_verified']=False
            elif change=='complete':wrong['stream']['publication_eligible']=False
            elif change=='restore':wrong['source']['books'][0]['orders'][0][3]+=4
            elif change=='sequence':wrong['source']['books'][0]['metadata']['sequence']+=1
            elif change=='digest':wrong['stream']['accepted_prefix_sha256']='0'*64
            else:wrong['stream']['source_records']+=1
            controls.append(wrong)
        assert all(l3.first_difference(truth,wrong) for wrong in controls)
        print('negative_controls=6 rejected=6')
    print(f'fixture_python_zlib_runtime={zlib.ZLIB_RUNTIME_VERSION}')
    print(f'streaming_fixtures={len(candidates)} framed_source_records_across_fixtures={source_candidates} accepted_source_records_across_fixtures={accepted_records} categories={json.dumps(counts,sort_keys=True,separators=(",",":"))} canonical_sha256={canonical.hexdigest()}')


if __name__=='__main__':main()
