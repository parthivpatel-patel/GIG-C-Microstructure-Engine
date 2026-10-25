#!/usr/bin/env python3
"""Reproducible authored source-log/native-replay demonstration; no observed files."""
import argparse,hashlib,json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from terminal.l2_recording import L2Writer,load_l2,replay_l2
from terminal.providers.fixtures import EVENTS

p=argparse.ArgumentParser();p.add_argument('--position',type=int,default=5);a=p.parse_args()
if not 0<=a.position<=len(EVENTS):p.error('position must be between0 and5')
with tempfile.TemporaryDirectory(prefix='gig-authored-l2-') as directory:
    writer=L2Writer(directory,'authored-demo',enabled=True)
    for i,raw in enumerate(EVENTS):writer.append(raw,i*50_000_000)
    manifest=writer.finish();manifest,rows=load_l2(directory,'authored-demo')
    result=replay_l2(manifest,rows,a.position)
    result['canonical_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(result,indent=2))
