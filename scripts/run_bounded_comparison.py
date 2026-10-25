#!/usr/bin/env python3
"""Bounded authored-fixture comparison; observed initialization remains blocked."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import check_initialization_manifest as policy
import check_itch_l3_reference as ref
import check_seeded_reference as seeded
from check_adapter_differential import run, encoded as empty_encoded


def framed(payloads):return b''.join(struct.pack('>H',len(p))+p for p in payloads)+b'\0\0'


def read_bounded(path,maximum):
    if type(maximum) is not int or not 1<=maximum<=2*1024*1024:raise ValueError('input byte budget configuration')
    data=bytearray()
    with Path(path).open('rb') as f:
        while True:
            part=f.read(min(65536,maximum-len(data)+1))
            if not part:break
            if len(data)+len(part)>maximum:raise ValueError('input byte budget')
            data+=part
    return bytes(data)


def frames(data,record_limit,event_limit):
    out=[];at=0
    while at<len(data):
        if at+2>len(data):raise ValueError('truncated BinaryFile length')
        size=int.from_bytes(data[at:at+2],'big');at+=2
        if not size:
            if at!=len(data):raise ValueError('bytes after terminal')
            return out
        if at+size>len(data):raise ValueError('truncated BinaryFile payload')
        if len(out)>=min(record_limit,event_limit):raise ValueError('record/event budget')
        out.append(data[at:at+size]);at+=size
    raise ValueError('missing terminal; incomplete bounded input')


def compare(manifest,raw,driver,trusted_source=None,trusted_snapshot=None,*,max_bytes=1024*1024,max_records=512,max_events=512,max_memory=128*1024*1024,timeout=120,inject=False):
    start=time.monotonic()
    if not(1<=max_bytes<=2*1024*1024 and 1<=max_records<=1024 and 1<=max_events<=1024 and 4096<=max_memory<=128*1024*1024 and 0<timeout<=120):raise ValueError('comparison budget configuration')
    assessment=policy.validate(manifest,trusted_source,trusted_snapshot)
    base=dict(schema='gig.bounded_comparison.v1',dataset=manifest['dataset'],origin=manifest['origin'],initialization=assessment,observed_validated=False,evidence_level='authored fixtures plus independent algorithm; no observed evidence')
    if not assessment['full_l3_eligible']:
        return dict(base,status='initialization_blocked',source_records=None,reason='no implementation-qualified observed initialization or trusted complete authored fixture')
    if manifest['provider']!='authored-only' or sorted(manifest['instruments'],key=lambda x:x['locate'])!=[dict(locate=i,symbol=ref.SYMBOLS[i].decode(),instrument=i) for i in (1,2)]:raise ValueError('fixture driver instrument/provider scope')
    if len(raw)>max_bytes:raise ValueError('input byte budget')
    source_hash=hashlib.sha256(raw).hexdigest()
    if source_hash!=manifest['source_sha256'] or manifest['capture_end']!=manifest['event_boundary']['frame_offset']+len(raw):raise ValueError('source checksum/boundary contradiction')
    payloads=frames(raw,max_records,max_events)
    if not payloads:raise ValueError('comparison needs a nonempty authored interval')
    if len(manifest['snapshot']['orders'])*(len(payloads)+1)>32768:raise ValueError('reference state cell budget')
    if manifest['mode']=='seeded':
        if manifest['last_timestamp'] is None or manifest['session_stage']==0:raise ValueError('fixture driver requires supplied seed clock/stage; no metadata invented')
        model=seeded.SeedModel(manifest,source_hash);initial=model.state(True,'external')
        arguments=[driver,'--seed','7',str(max_memory)];data=seeded.encoded(manifest,payloads,source_hash,7)
    else:
        if manifest['capture_start']!=0:raise ValueError('empty fixture starts at byte0')
        model=ref.Model(1,(1,10000),(1,1),source_hash);initial=None
        case=dict(flags=1,tick=(1,10000),lot=(1,1),digest=source_hash,payloads=payloads)
        arguments=[driver,'--adapter','7',manifest['dataset']];data=empty_encoded(case)
        if max_memory!=128*1024*1024:raise ValueError('empty fixture driver memory profile fixed128MiB; use seeded mode for configurable PMR')
    expected=[]
    for p in payloads:
        state=model.apply(p);expected.append(state)
        if not state['committed']:break
    remaining=timeout-(time.monotonic()-start)
    if remaining<=0:raise TimeoutError('reference preparation deadline')
    try:actual=run(arguments,data,remaining)
    except (ValueError,OSError,TimeoutError) as e:return dict(base,status='candidate_error',source_records=len(payloads),event_index=None,event_type=None,reason=str(e),accepted_records=None)
    if type(actual) is not dict or type(actual.get('events')) is not list or type(actual.get('summary')) is not dict:raise ValueError('candidate envelope')
    index=None;field=None;expected_state=actual_state=None
    if initial is not None:
        difference=ref.first_difference(initial,actual.get('initial'))
        if difference:field=difference[0];expected_state=initial;actual_state=actual.get('initial')
    if not field and len(expected)!=len(actual['events']):field='events.length';expected_state=len(expected);actual_state=len(actual['events'])
    for i,(e,a) in enumerate(zip(expected,actual['events'])):
        if field:break
        e=copy.deepcopy(e)
        if inject and i==0:
            if e['books'][0]['orders']:e['books'][0]['orders'][0][3]+=1
            else:e['source_summary']['considered']+=1
        difference=ref.first_difference(e,a)
        if difference:index=i;field=difference[0];expected_state=e;actual_state=a;break
    accepted=sum(e['committed'] for e in expected);rejected=len(expected)-accepted
    complete=not rejected;session_closed=model.stage==6
    required_summary=dict(native=expected[-1]['native'],records=len(expected),accepted=accepted,rejected=rejected,input_complete=complete,l3_complete=complete and session_closed,publication_eligible=complete and session_closed)
    for k,v in required_summary.items():
        if field:break
        if type(actual['summary'].get(k)) is not type(v) or actual['summary'][k]!=v:field='summary.'+k;expected_state=v;actual_state=actual['summary'].get(k)
    reasons={}
    for e in expected:
        if not e['committed']:reasons[e['category']]=reasons.get(e['category'],0)+1
    metrics=dict(order_state_divergences=0,quantity_divergences=0,price_level_divergences=0,best_bid_ask_divergences=0,absolute_remaining_lots_difference=0)
    if field:
        if isinstance(expected_state,dict) and isinstance(actual_state,dict) and 'books' in expected_state and 'books' in actual_state:
            try:
                for eb,ab in zip(expected_state['books'],actual_state['books']):
                    eo={o[0]:o for o in eb['orders']};ao={o[0]:o for o in ab['orders']}
                    for identity in eo.keys()|ao.keys():
                        metrics['order_state_divergences']+=int(eo.get(identity)!=ao.get(identity))
                        eq=eo[identity][3] if identity in eo else 0;aq=ao[identity][3] if identity in ao else 0
                        metrics['quantity_divergences']+=int(eq!=aq);metrics['absolute_remaining_lots_difference']+=abs(eq-aq)
                    for side in ('bids','asks'):
                        el={x[0]:x[1:] for x in eb[side]};al={x[0]:x[1:] for x in ab[side]}
                        metrics['price_level_divergences']+=sum(el.get(p)!=al.get(p) for p in el.keys()|al.keys())
                        metrics['best_bid_ask_divergences']+=int(eb[side][:1]!=ab[side][:1])
            except (KeyError,TypeError,IndexError):metrics={k:None for k in metrics}
        else:metrics={k:None for k in metrics}
    result=dict(base,status='divergence' if field else 'accepted_prefix_agreement_with_rejection' if rejected else 'reference_agreement',source_records=len(payloads),accepted_records=accepted,rejected_records=rejected,examined_records=len(expected),unprocessed_after_stop=len(payloads)-len(expected),acceptance_rate=f'{accepted}/{len(payloads)}',rejection_reasons=reasons,unsupported_events=reasons.get('unsupported',0),sequence_discontinuities=None,sequence_observability='Exact local capture adjacency only; no upstream exchange sequence inferred',initialization_complete=True,final_state_agreement=not bool(field),divergence_count=int(bool(field)),divergence_metrics_scope='All book fields of first divergent compared state; later events not enumerated',event_index=index,event_type=chr(payloads[index][0]) if index is not None else None,first_difference=field,expected_state=expected_state,actual_state=actual_state,negative_control=inject,source_sha256=source_hash,snapshot_sha256=manifest['snapshot_sha256'],budgets=dict(input_bytes=max_bytes,records=max_records,events=max_events,candidate_pmr_bytes=max_memory,timeout_seconds=timeout,error_stop_count=1,reference_cells=32768),memory_scope='Candidate PMR governor; reference model additionally count/cell-bounded, not a total-process RSS/ASan-virtual-memory cap')
    result.update(metrics)
    return result


def write_divergence(path,result,manifest,raw,driver,inject):
    if manifest['origin']!='synthetic' or result['origin']!='synthetic':raise ValueError('observed payload export forbidden')
    m=copy.deepcopy(manifest);data=raw;description='original bounded fixture; no smaller reproduction established'
    index=result['event_index']
    if index is not None:
        payloads=frames(raw,1024,1024);candidate=framed(payloads[:index+1]);candidate_manifest=copy.deepcopy(m)
        candidate_manifest['source_sha256']=hashlib.sha256(candidate).hexdigest();candidate_manifest['capture_end']=m['event_boundary']['frame_offset']+len(candidate)
        repeated=compare(candidate_manifest,candidate,driver,candidate_manifest['source_sha256'],candidate_manifest['snapshot_sha256'],inject=inject)
        if repeated.get('first_difference')==result['first_difference']:
            m=candidate_manifest;data=candidate;description='verified authored first-diverging prefix; not globally delta-minimal'
    report=dict(schema='gig.bounded_divergence.v1',dataset=m['dataset'],origin='synthetic',original_source_sha256=result['source_sha256'],input_sha256=hashlib.sha256(data).hexdigest(),initialization_manifest=m,event_index=result['event_index'],event_type=result['event_type'],expected_state=result['expected_state'],actual_state=result['actual_state'],first_difference=result['first_difference'],negative_control=inject,minimization=description,fixture_hex=data.hex(),reproduction_argv=[sys.executable,str(Path(__file__).resolve()),'--driver',driver,'--reproduce',str(path)])
    # Recompute states using the retained reduced artifact; retain original parent separately.
    reduced=compare(m,data,driver,m['source_sha256'],m['snapshot_sha256'],inject=inject)
    report.update(expected_state=reduced['expected_state'],actual_state=reduced['actual_state'])
    encoded=json.dumps(report,sort_keys=True,indent=2).encode()
    if len(encoded)>policy.MAX_BYTES:raise ValueError('divergence report byte budget')
    with Path(path).open('xb') as f:f.write(encoded)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',nargs='?');p.add_argument('input',nargs='?');p.add_argument('--driver',required=True);p.add_argument('--trusted-source-sha256');p.add_argument('--trusted-snapshot-sha256');p.add_argument('--max-bytes',type=int,default=1024*1024);p.add_argument('--max-records',type=int,default=512);p.add_argument('--max-events',type=int,default=512);p.add_argument('--max-memory-bytes',type=int,default=128*1024*1024);p.add_argument('--timeout-seconds',type=float,default=120);p.add_argument('--max-errors',type=int,choices=[1],default=1);p.add_argument('--inject-reference-error',action='store_true');p.add_argument('--report');p.add_argument('--reproduce');a=p.parse_args()
    try:
        if a.reproduce:
            report=policy.load(a.reproduce)
            if report['schema']!='gig.bounded_divergence.v1' or report['origin']!='synthetic' or type(report['negative_control']) is not bool:raise ValueError('only authored reproduction supported')
            m=report['initialization_manifest'];data=bytes.fromhex(report['fixture_hex'])
            if hashlib.sha256(data).hexdigest()!=report['input_sha256']:raise ValueError('reproduction checksum')
            result=compare(m,data,a.driver,m['source_sha256'],m['snapshot_sha256'],inject=report['negative_control'])
            if result.get('first_difference')!=report['first_difference'] or result.get('status')!='divergence':raise ValueError('divergence not reproduced')
        else:
            if not a.manifest or not a.input:p.error('manifest and input required')
            m=policy.load(a.manifest);assessment=policy.validate(m,a.trusted_source_sha256,a.trusted_snapshot_sha256)
            data=read_bounded(a.input,a.max_bytes) if assessment['full_l3_eligible'] else b''
            result=compare(m,data,a.driver,a.trusted_source_sha256,a.trusted_snapshot_sha256,max_bytes=a.max_bytes,max_records=a.max_records,max_events=a.max_events,max_memory=a.max_memory_bytes,timeout=a.timeout_seconds,inject=a.inject_reference_error)
            if a.report and result['status']=='divergence':write_divergence(a.report,result,m,data,a.driver,a.inject_reference_error)
        print(json.dumps(result,sort_keys=True));return 3 if result['status']=='divergence' else 0 if result['status']=='reference_agreement' else 2
    except (ValueError,KeyError,TypeError,OSError,OverflowError,RecursionError,TimeoutError) as e:p.exit(2,'comparison refused: '+str(e)+'\n')

if __name__=='__main__':raise SystemExit(main())
