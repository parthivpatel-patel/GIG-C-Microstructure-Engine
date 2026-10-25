#!/usr/bin/env python3
"""Authored-only offline acceptance demonstration. Creates a new private directory."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import check_initialization_manifest as policy
import check_itch_l3_reference as ref
from run_bounded_comparison import framed


def main(driver,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[1];driver=str(Path(driver).resolve())
    original=policy.load(root/'tests/fixtures/market_seed_manifest.json')
    seed_events=[ref.execute(11,2,71),ref.replace(12,13,9,101),ref.system('E'),ref.system('C')]
    scenarios=[('seeded',seed_events,0),('empty',[],0),('unknown',seed_events,2),('corrupt_snapshot',seed_events,2),('missing_events',seed_events,2),('duplicate',[ref.add(11,1,100)],2),('unknown_order',[ref.execute(999,1,71)],2),('unsupported',[b'?'+b'\0'*11],2),('memory_cap',seed_events,2),('reference_divergence',seed_events,3)]
    rows=[]
    for name,events,expected_exit in scenarios:
        m=copy.deepcopy(original)
        if name=='empty':
            m.update(mode='complete',snapshot={'orders':[],'retired_references':[],'matches':[]},snapshot_sha256=None,session_stage=0,last_timestamp=None,capture_start=0,event_boundary=dict(frame_offset=0,payload_offset=2,ordinal=0))
            events=[ref.system('O'),ref.directory(),ref.directory(2),ref.add(11,10,100),*[ref.system(c) for c in 'SQMEC']]
        raw=framed(events);m['source_sha256']=hashlib.sha256(raw).hexdigest();m['capture_end']=m['event_boundary']['frame_offset']+len(raw)
        if name=='unknown':m['mode']='unknown'
        if name=='corrupt_snapshot':m['snapshot']['orders'][0]['remaining']+=1
        if name=='missing_events':raw=framed(events[1:])
        manifest=directory/(name+'.json');source=directory/(name+'.bin');manifest.write_text(json.dumps(m,indent=2)+'\n');source.write_bytes(raw)
        command=[sys.executable,str(root/'scripts/run_bounded_comparison.py'),str(manifest),str(source),'--driver',driver,'--trusted-source-sha256',m['source_sha256']]
        if m['snapshot_sha256']:command+=['--trusted-snapshot-sha256',m['snapshot_sha256']]
        if name=='memory_cap':command+=['--max-memory-bytes','4096']
        if name=='reference_divergence':command+=['--inject-reference-error','--report',str(directory/'divergence.json')]
        result=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=130)
        assert result.returncode==expected_exit,(name,result.returncode,result.stderr)
        output=json.loads(result.stdout) if result.stdout else None
        if output is not None:assert not output['observed_validated']
        rows.append(dict(scenario=name,command=command,exit=result.returncode,expected_exit=expected_exit,output=output,diagnostic=result.stderr,source_bytes=len(raw),source_sha256=hashlib.sha256(raw).hexdigest()))
    command=[sys.executable,str(root/'scripts/run_bounded_comparison.py'),'--driver',driver,'--reproduce',str(directory/'divergence.json')]
    result=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=130);assert result.returncode==3,result.stderr
    repro=json.loads(result.stdout);assert repro['status']=='divergence'
    rows.append(dict(scenario='reproduce_negative_control',command=command,exit=3,expected_exit=3,output=repro))
    report=dict(schema='gig.bounded_comparison_demo.v1',origin='synthetic',observed_validated=False,checks_passed=len(rows),unexpected_failures=0,rows=rows)
    (directory/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checks_passed=len(rows),unexpected_failures=0,statuses=[(r['scenario'],r['exit'],r['output']['status'] if r.get('output') else 'refused_before_candidate') for r in rows],observed_validated=False),sort_keys=True))
    return report

if __name__=='__main__':main(sys.argv[1],sys.argv[2])
