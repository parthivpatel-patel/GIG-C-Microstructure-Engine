#!/usr/bin/env python3
"""Bounded initialization contract validation; external completeness is never inferred."""
import argparse
import copy
import datetime
import hashlib
import json
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_ORDERS = 128
MODES = {'complete', 'seeded', 'unknown', 'invalid'}
FIELDS = {'schema','mode','origin','provider','dataset','instruments','session_date',
          'source_sha256','capture_start','capture_end','initial_state_source',
          'snapshot_sha256','complete','verification_method','event_boundary',
          'sequence_info','missing_data','license','redistribution','validation_status',
          'snapshot','session_stage','last_timestamp'}


def canonical_snapshot(snapshot):
    """Vector order is not priority: explicit arrival/priority ranks carry meaning."""
    value = copy.deepcopy(snapshot)
    value['orders'].sort(key=lambda x: x['reference'])
    value['retired_references'].sort()
    value['matches'].sort(key=lambda x: x['number'])
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def digest(text):
    return type(text) is str and len(text) == 64 and all(c in '0123456789abcdef' for c in text)


def integer(x, lo, hi):
    return type(x) is int and lo <= x <= hi


def validate(m, trusted_source=None, trusted_snapshot=None):
    def require(ok, field):
        if not ok: raise ValueError(field)
    require(type(m) is dict and set(m) == FIELDS, 'manifest.fields')
    require(m['schema'] == 'gig.market_initialization.v1', 'manifest.schema')
    require(m['mode'] in MODES and m['origin'] in {'synthetic','observed'}, 'manifest.mode_origin')
    for field in ('provider','dataset','initial_state_source','license','redistribution'):
        s=m[field];require(type(s) is str and 1<=len(s)<=128 and all(32<=ord(c)<=126 for c in s), field)
    require(digest(m['source_sha256']), 'source_sha256')
    require(m['session_date'] is None or (type(m['session_date']) is str and len(m['session_date'])==10 and datetime.date.fromisoformat(m['session_date']).isoformat()==m['session_date']), 'session_date')
    require(integer(m['capture_start'],0,2**64-3) and integer(m['capture_end'],m['capture_start'],2**64-1), 'capture')
    b=m['event_boundary'];require(type(b) is dict and set(b)=={'frame_offset','payload_offset','ordinal'}, 'event_boundary')
    require(integer(b['frame_offset'],m['capture_start'],m['capture_end']) and b['frame_offset']<=2**64-3 and type(b['payload_offset']) is int and b['payload_offset']==b['frame_offset']+2 and integer(b['ordinal'],0,2**64-1), 'event_boundary.values')
    require(type(m['complete']) is bool and type(m['missing_data']) is bool, 'completeness.flags')
    require(m['verification_method'] in {'none','authored_fixture','external_evidence_pending'}, 'verification_method')
    require(m['validation_status'] in {'declared','invalid','unknown'}, 'validation_status')
    seq=m['sequence_info'];require(seq is None or (type(seq) is dict and set(seq)=={'unit','next'} and seq['unit']=='capture_ordinal' and type(seq['next']) is int and seq['next']==b['ordinal']), 'sequence_info')
    require(integer(m['session_stage'],0,5), 'session_stage')
    require(m['last_timestamp'] is None or integer(m['last_timestamp'],0,2**48-1), 'last_timestamp')
    instruments=m['instruments'];require(type(instruments) is list and 1<=len(instruments)<=2, 'instruments')
    locates=set();symbols=set();ids=set()
    for x in instruments:
        require(type(x) is dict and set(x)=={'locate','symbol','instrument'}, 'instrument.fields')
        require(integer(x['locate'],1,65535) and integer(x['instrument'],1,2**32-1), 'instrument.identity')
        require(type(x['symbol']) is str and len(x['symbol'])==8 and all(32<=ord(c)<=126 for c in x['symbol']) and x['symbol'].strip(), 'instrument.symbol')
        require(x['locate'] not in locates and x['symbol'] not in symbols and x['instrument'] not in ids, 'instrument.duplicate')
        locates.add(x['locate']);symbols.add(x['symbol']);ids.add(x['instrument'])
    snapshot=m['snapshot'];require(type(snapshot) is dict and set(snapshot)=={'orders','retired_references','matches'}, 'snapshot.fields')
    orders=snapshot['orders'];retired=snapshot['retired_references'];matches=snapshot['matches']
    require(type(orders) is list and len(orders)<=MAX_ORDERS and type(retired) is list and len(retired)<=4096 and type(matches) is list and len(matches)<=4096, 'snapshot.capacity')
    references=set();ranks=set();arrivals=set();counts={x:0 for x in locates}
    for o in orders:
        require(type(o) is dict and set(o)=={'reference','locate','side','price4','remaining','priority','arrival'}, 'order.fields')
        require(integer(o['reference'],1,2**64-1) and o['reference'] not in references, 'order.reference')
        require(type(o['locate']) is int and o['locate'] in locates and o['side'] in {'B','S'}, 'order.instrument_side')
        require(integer(o['remaining'],1,2**32-1) and integer(o['price4'],1,2**32-1), 'order.quantity_price')
        require(integer(o['priority'],1,2**64-1) and (o['locate'],o['priority']) not in ranks, 'order.priority')
        require(integer(o['arrival'],0,b['ordinal']-1) and o['arrival'] not in arrivals, 'order.arrival')
        references.add(o['reference']);ranks.add((o['locate'],o['priority']));arrivals.add(o['arrival']);counts[o['locate']]+=1
        require(counts[o['locate']]<=64, 'snapshot.per_book_capacity')
    for ref in retired:
        require(integer(ref,1,2**64-1) and ref not in references, 'retired.reference');references.add(ref)
    nums=set()
    for match in matches:
        require(type(match) is dict and set(match)=={'number','locate','kind','broken'}, 'match.fields')
        require(integer(match['number'],1,2**64-1) and match['number'] not in nums and type(match['locate']) is int and match['locate'] in locates and match['kind'] in {'execution','print','cross'} and type(match['broken']) is bool, 'match.values');nums.add(match['number'])
    actual=hashlib.sha256(canonical_snapshot(snapshot)).hexdigest()
    require(m['snapshot_sha256'] is None or (digest(m['snapshot_sha256']) and m['snapshot_sha256']==actual), 'snapshot.digest')
    if m['mode']=='seeded':require(m['snapshot_sha256'] is not None and b['ordinal']>0, 'seed.evidence')
    if m['mode']=='complete':require(not orders and not retired and not matches and b['ordinal']==0 and b['frame_offset']==m['capture_start'] and m['session_stage']==0 and m['last_timestamp'] is None, 'empty.boundary')
    eligible=(m['mode'] in {'complete','seeded'} and m['origin']=='synthetic' and m['complete'] and not m['missing_data'] and m['verification_method']=='authored_fixture' and m['validation_status']=='declared' and trusted_source==m['source_sha256'] and (m['mode']!='seeded' or trusted_snapshot==actual))
    return dict(schema='gig.initialization_assessment.v1',mode=m['mode'],origin=m['origin'],status='invalid' if m['mode']=='invalid' or m['validation_status']=='invalid' else 'synthetic_eligible' if eligible else 'context_only',full_l3_eligible=eligible,observed_initialization_verified=False,snapshot_sha256=actual,sequence_information_available=seq is not None,limitations=['Trusted digests supplied separately establish fixture integrity, not publisher authority','Observed evidence verifier is not implemented; caller assertions never grant observed L3'])


def load(path):
    with Path(path).open('rb') as f: data=f.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise ValueError('manifest byte budget')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('duplicate manifest field')
            out[k]=v
        return out
    return json.loads(data,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON number')))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('--trusted-source-sha256');p.add_argument('--trusted-snapshot-sha256');a=p.parse_args()
    try:result=validate(load(a.manifest),a.trusted_source_sha256,a.trusted_snapshot_sha256)
    except (ValueError,KeyError,TypeError,OverflowError,OSError,RecursionError) as e:p.exit(2,'invalid initialization: '+str(e)+'\n')
    print(json.dumps(result,sort_keys=True));return 0 if result['full_l3_eligible'] else 1

if __name__=='__main__':raise SystemExit(main())
