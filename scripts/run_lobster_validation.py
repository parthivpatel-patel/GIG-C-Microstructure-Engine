#!/usr/bin/env python3
"""Permission-gated local LOBSTER analysis. No download, extraction or full-L3 claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]


def load_manifest(path):
    with Path(path).open('rb') as f:data=f.read(65537)
    if len(data)>65536:raise ValueError('manifest budget')
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('duplicate manifest field')
            d[k]=v
        return d
    m=json.loads(data,object_pairs_hook=unique)
    return validate_manifest(m)


def validate_manifest(m):
    required={'schema','origin','dataset','session','instrument','initialization','message_sha256','reference_sha256','permission'}
    if type(m) is not dict or set(m)!=required or m['schema']!='gig.lobster.run.v1' or m['origin'] not in ('synthetic','observed'):raise ValueError('manifest schema/origin')
    for key in ('dataset','session'):
        if type(m[key]) is not str or not 1<=len(m[key])<=128 or any(not 33<=ord(c)<=126 for c in m[key]):raise ValueError('identity')
    if m['initialization']!='unknown':raise ValueError('false completeness declaration: five levels cannot seed L3')
    for key in ('message_sha256','reference_sha256'):
        if type(m[key]) is not str or not re.fullmatch('[0-9a-f]{64}',m[key]):raise ValueError('expected input hash')
    i=m['instrument']
    if type(i) is not dict or set(i)!={'symbol','native_id','venue_id'} or i['native_id']!=1 or type(i['native_id']) is not int or i['venue_id']!=1 or type(i['venue_id']) is not int or type(i['symbol']) is not str or not re.fullmatch('[A-Z0-9.]{1,16}',i['symbol']):raise ValueError('single explicit instrument binding')
    p=m['permission']
    if type(p) is not dict or set(p)!={'cloud_processing_approved','scope','evidence_reference','derivative_reporting_approved'} or type(p['cloud_processing_approved']) is not bool or type(p['derivative_reporting_approved']) is not bool or p['scope']!='private-research' or type(p['evidence_reference']) is not str or not 1<=len(p['evidence_reference'])<=128 or any(not 33<=ord(c)<=126 for c in p['evidence_reference']):raise ValueError('permission record')
    return m


def run(m,messages,reference,driver,*,max_rows=1000000,max_bytes=128*1024*1024,max_memory=64*1024*1024,timeout=120,max_line=4096):
    validate_manifest(m)
    if any(type(v) is not int for v in (max_rows,max_bytes,max_memory,max_line)):raise ValueError('integer resource budget required')
    if not(1<=max_rows<=10000000 and 1<=max_bytes<=1024**3 and 4096<=max_memory<=128*1024*1024 and 0<timeout<=3600 and 1<=max_line<=4096):raise ValueError('resource budget')
    if m['origin']=='observed' and not m['permission']['cloud_processing_approved']:
        return dict(schema='gig.lobster.run_result.v1',status='BLOCKED_PERMISSION',origin='observed',input_opened=False,empirical_statistics=None,full_l3_complete=False)
    if m['origin']=='observed':
        for path in (messages,reference):
            if Path(path).resolve().is_relative_to(ROOT):raise ValueError('private input must remain outside Git repository')
    dataset_sha=hashlib.sha256(('gig.lobster.pair.v1:'+m['message_sha256']+':'+m['reference_sha256']).encode()).hexdigest()
    env=os.environ.copy();env.update(GIG_LOBSTER_DATASET_ID=m['dataset'],GIG_LOBSTER_SESSION_ID=m['session'],GIG_LOBSTER_PERMISSION_REF=m['permission']['evidence_reference'],GIG_LOBSTER_TIMEOUT_MS=str(max(1,int(timeout*1000))),GIG_LOBSTER_LINE_LIMIT=str(max_line))
    command=[str(driver),'--authored' if m['origin']=='synthetic' else '--authorized-private',str(messages),str(reference),m['message_sha256'],m['reference_sha256'],dataset_sha,str(max_rows),str(max_bytes),str(max_memory)]
    start=time.monotonic()
    p=subprocess.run(command,capture_output=True,text=True,timeout=timeout+1,env=env)
    if len(p.stdout)+len(p.stderr)>65536:raise ValueError('bounded summary output')
    if p.returncode:raise ValueError('native input/resource refusal: '+p.stderr[:512].strip())
    result=json.loads(p.stdout)
    if result['origin']!=m['origin'] or result['initialization']!='unknown' or result['full_l3_complete'] is not False:raise ValueError('provenance/completeness contradiction')
    return dict(schema='gig.lobster.run_result.v1',status='ANALYZED_WITH_UNKNOWN_INITIAL_STATE',origin=m['origin'],manifest=m,dataset_sha256=dataset_sha,input_hashes_verified_by_native_reader=True,permission_basis='authored fixture' if m['origin']=='synthetic' else 'operator-supplied attestation, legal scope requires external verification',statistics=result,elapsed_seconds=time.monotonic()-start,full_l3_complete=False,evidence_level='synthetic' if m['origin']=='synthetic' else 'observed structural/conditional comparisons only; independent review required',limits=dict(bytes=max_bytes,rows=max_rows,line=max_line,pmr_bytes=max_memory,seconds=timeout,malformed_stop_count=1),interpretation='No overall L3 accuracy; each quantity/best/depth/known-subset metric has its own eligibility count')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest');p.add_argument('messages');p.add_argument('reference');p.add_argument('--driver',required=True);p.add_argument('--output');p.add_argument('--max-rows',type=int,default=1000000);p.add_argument('--max-bytes',type=int,default=128*1024*1024);p.add_argument('--max-memory',type=int,default=64*1024*1024);p.add_argument('--timeout',type=float,default=120);p.add_argument('--max-line',type=int,default=4096);a=p.parse_args()
    try:
        m=load_manifest(a.manifest)
        if m['origin']=='observed' and m['permission']['cloud_processing_approved']:
            if not a.output or Path(a.output).resolve().is_relative_to(ROOT):raise ValueError('observed report requires private output outside Git')
        r=run(m,a.messages,a.reference,a.driver,max_rows=a.max_rows,max_bytes=a.max_bytes,max_memory=a.max_memory,timeout=a.timeout,max_line=a.max_line)
        if a.output:
            with Path(a.output).open('xb') as f:f.write((json.dumps(r,sort_keys=True,indent=2)+'\n').encode())
            print(json.dumps(dict(status=r['status'],private_output_written=True,full_l3_complete=False)))
        else:print(json.dumps(r,sort_keys=True))
        return 2 if r['status']=='BLOCKED_PERMISSION' else 0
    except (ValueError,KeyError,TypeError,OSError,subprocess.TimeoutExpired,RecursionError) as e:p.exit(2,'validation refused: '+str(e)+'\n')

if __name__=='__main__':raise SystemExit(main())
