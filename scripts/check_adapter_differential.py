#!/usr/bin/env python3
"""Bounded synthetic byte-adapter differential harness; not observed certification."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import selectors
import struct
import subprocess
import tempfile
import time
import check_itch_l3_reference as ref

MAX_INPUT = 2 * 1024 * 1024
MAX_OUTPUT = 32 * 1024 * 1024


def run(arguments, data, timeout=120):
    if len(data) > MAX_INPUT:
        raise ValueError('fixture input budget')
    with tempfile.TemporaryFile() as source:
        source.write(data); source.seek(0)
        process = subprocess.Popen(arguments, stdin=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        selector = selectors.DefaultSelector()
        output = {'stdout': bytearray(), 'stderr': bytearray()}
        deadline = time.monotonic() + timeout
        try:
            selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
            selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
            total = 0
            while selector.get_map():
                remaining = deadline-time.monotonic()
                if remaining <= 0: raise TimeoutError('candidate deadline exceeded')
                ready = selector.select(remaining)
                if not ready: raise TimeoutError('candidate deadline exceeded')
                for key, _ in ready:
                    block = os.read(key.fd, min(65536, MAX_OUTPUT-total+1))
                    if not block:
                        selector.unregister(key.fileobj); continue
                    total += len(block)
                    if total > MAX_OUTPUT: raise ValueError('candidate output budget')
                    output[key.data] += block
            code = process.wait(timeout=max(.01, deadline-time.monotonic()))
            if code or output['stderr']:
                raise ValueError('candidate failure: '+bytes(output['stderr'][:4096]).decode(errors='replace'))
            return json.loads(output['stdout'])
        finally:
            selector.close()
            if process.poll() is None: process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()


def raw_bytes(payloads):
    return b''.join(struct.pack('>H', len(p))+p for p in payloads)+b'\0\0'


def case(payloads, flags=0, tick=(1,100), lot=(1,1)):
    # Re-authenticate the exact supplied prefix, not an omitted old fixture tail.
    return ref.session(list(payloads), flags=flags, tick=tick, lot=lot)


def encoded(c):
    return (' '.join(map(str, [c['flags'], *c['tick'], *c['lot']]))+' '+c['digest']+' '+
            ' '.join(p.hex() for p in c['payloads'])+'\n').encode()


def compare(driver, c, chunk, injected=False, dataset='adapter-differential-v1'):
    try:
        result = run([driver, '--adapter', str(chunk), dataset], encoded(c))
        if type(result) is not dict or set(result) != {'events', 'summary'} or type(result['events']) is not list or type(result['summary']) is not dict:
            raise ValueError('candidate output envelope')
    except (ValueError, TimeoutError, OSError, subprocess.TimeoutExpired) as error:
        return None, 'candidate.execution', {'valid_bounded_output': True}, {'error': type(error).__name__, 'diagnostic': str(error)}, None
    actual = result['events']
    if len(actual) != len(c['expected']):
        return 0, 'events.length', c['expected'], actual, result
    for index, (expected, got) in enumerate(zip(c['expected'], actual)):
        expected = copy.deepcopy(expected)
        if injected and any(book['orders'] for book in expected['books']):
            next(book for book in expected['books'] if book['orders'])['orders'][0][3] += 1
        difference = ref.first_difference(expected, got)
        if difference:
            return index, difference[0], expected, got, result
    summary = result['summary']; last = c['expected'][-1]
    good = all(x['committed'] for x in c['expected'])
    consumed = raw_bytes(c['payloads']) if good else raw_bytes(c['payloads'])[:-2]
    expected_summary = dict(dataset_hex=dataset.encode('ascii').hex(), records=len(c['expected']), accepted=last['accepted'], native=last['native'],
                            rejected=int(not good), bytes=len(consumed), input_complete=good,
                            l3_complete=good and last['stage']==6,
                            publication_eligible=good and last['stage']==6,
                            input_sha256=hashlib.sha256(consumed).hexdigest())
    for key, value in expected_summary.items():
        if key not in summary or type(summary[key]) is not type(value) or summary[key] != value:
            return len(actual)-1, 'summary.'+key, value, summary.get(key,'<missing>'), result
    if type(summary.get('error')) is not int or not 0<=summary['error']<=8:
        return len(actual)-1, 'summary.error_type', 'adapter enum integer', summary.get('error'), result
    if bool(summary['error']) == good:
        return len(actual)-1, 'summary.error', not good, bool(summary['error']), result
    return None


def fixtures():
    for c in ref.fixtures():
        yield case(c['payloads'], c['flags'], c['tick'], c['lot'])
    start = [ref.system('O'), ref.directory(), ref.directory(2)]
    for orders in (8, 64):
        payloads = start.copy()
        for book in (1, 2):
            for i in range(orders):
                payloads.append(ref.add(book*1000+i, 2**32-1,
                                        (10000 if book==1 else 20000)+(i%32)*100,
                                        b'B' if book==1 else b'S', book))
        for _ in range(2):
            for book in (1, 2):
                for i in range(orders): payloads.append(ref.cancel(book*1000+i, 1, book))
        payloads += [ref.system(code) for code in 'SQMEC']
        yield case(payloads)
    # Fixed-seed bounded grammar and byte mutations reuse only independent oracle code.
    for index, c in enumerate(ref.grammar_fixtures()):
        if index == 16: break
        yield case(c['payloads'], c['flags'], c['tick'], c['lot'])
    for index, c in enumerate(ref.mutation_fixtures()):
        if index == 32: break
        yield case(c['payloads'], c['flags'], c['tick'], c['lot'])


def report(driver, c, difference, dataset, chunk, injected, path):
    index, field, expected, actual, _ = difference
    reduced_ok = False
    if index is not None:
        prefix = case(c['payloads'][:index+1], c['flags'], c['tick'], c['lot'])
        reduced = compare(driver, prefix, chunk, injected, dataset)
        if reduced is not None and reduced[1] == field:
            c = prefix; index, field, expected, actual, _ = reduced
            reduced_ok = True
    document = dict(schema='gig.book_divergence.v1', origin='synthetic', dataset=dataset,
                    generator_seed=ref.SEED, fixture_sha256=c['digest'], event_index=index,
                    event_type=chr(c['payloads'][index][0]) if index is not None else None, first_difference=field,
                    expected_state=expected, actual_state=actual, negative_control=injected,
                    minimization='verified first-diverging prefix; not globally delta-minimal' if reduced_ok else 'original bounded fixture retained; no smaller reproducer established',
                    fixture=dict(flags=c['flags'], tick=list(c['tick']), lot=list(c['lot']),
                                 payloads_hex=[p.hex() for p in c['payloads']]),
                    reproduction_argv=['python3','scripts/check_adapter_differential.py',driver,'--reproduce',str(path)])
    data=json.dumps(document, sort_keys=True, indent=2).encode()
    if len(data)>MAX_INPUT: raise ValueError('divergence report budget')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(data)
    return document


def load(path):
    with path.open('rb') as stream: data=stream.read(MAX_INPUT+1)
    if len(data)>MAX_INPUT: raise ValueError('report input budget')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out: raise ValueError('duplicate report field')
            out[k]=v
        return out
    value=json.loads(data,object_pairs_hook=unique)
    if value['schema']!='gig.book_divergence.v1' or value['origin']!='synthetic' or type(value['negative_control']) is not bool:
        raise ValueError('only declared synthetic reproduction supported')
    fixture=value['fixture'];payloads=[bytes.fromhex(p) for p in fixture['payloads_hex']]
    if not 1<=len(payloads)<=1024 or any(not p or len(p)>65535 for p in payloads) or len(raw_bytes(payloads))>MAX_INPUT:
        raise ValueError('fixture record/byte budget')
    for scale in (fixture['tick'],fixture['lot']):
        if len(scale)!=2 or any(type(v) is not int or not 1<=v<=1000000 for v in scale):raise ValueError('scale bound')
    if type(fixture['flags']) is not int or not 0<=fixture['flags']<=7:raise ValueError('flags bound')
    if type(value['dataset']) is not str or not 1<=len(value['dataset'])<=128 or any(not 33<=ord(c)<=126 for c in value['dataset']):raise ValueError('dataset identity')
    c=case(payloads,fixture['flags'],fixture['tick'],fixture['lot'])
    if c['digest']!=value['fixture_sha256']:raise ValueError('fixture digest contradiction')
    return value,c


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('driver')
    parser.add_argument('--report',type=Path);parser.add_argument('--reproduce',type=Path)
    parser.add_argument('--dataset-id',default='adapter-differential-v1')
    parser.add_argument('--inject-reference-error',action='store_true')
    args=parser.parse_args()
    if not 1<=len(args.dataset_id)<=128 or any(not 33<=ord(c)<=126 for c in args.dataset_id):parser.error('dataset identity bound')
    digest=hashlib.sha256();sessions=candidates=0
    if args.reproduce:
        prior,c=load(args.reproduce);difference=compare(args.driver,c,7,prior['negative_control'],prior['dataset'])
        if difference is None:raise SystemExit('reported divergence no longer reproduced')
        print(json.dumps(dict(reproduced=True,event_index=difference[0],first_difference=difference[1],negative_control=prior['negative_control']),sort_keys=True));return 1
    for c in fixtures():
        for chunk in (1,257):
            difference=compare(args.driver,c,chunk,args.inject_reference_error,args.dataset_id)
            if difference:
                if args.report: detail=report(args.driver,c,difference,args.dataset_id,chunk,args.inject_reference_error,args.report)
                else:detail=dict(event_index=difference[0],first_difference=difference[1],fixture_sha256=c['digest'])
                print(json.dumps(detail,sort_keys=True));return 1
            digest.update(json.dumps(c['expected'],sort_keys=True,separators=(',',':')).encode())
            candidates+=len(c['expected']);sessions+=1
    print(json.dumps(dict(scope='synthetic independent model versus byte-adapter/native engine',sessions=sessions,candidates=candidates,seed=ref.SEED,canonical_sha256=digest.hexdigest(),observed_validated=False),sort_keys=True));return 0


if __name__=='__main__': raise SystemExit(main())
