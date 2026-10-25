"""Independently authored toy prices/IDs, never copied from an observed dataset."""
import hashlib
import json
from pathlib import Path

def book(bid=20):return [110,10,100,bid,120,11,90,21,130,12,80,22,140,13,70,23,150,14,60,24]
def rows():
    messages=['1,1,11,10,100,1','2,1,12,5,100,1','3,2,11,3,100,1','4,4,12,5,100,1','5,5,0,2,100,1','6,7,0,0,-1,-1','7,3,11,7,100,1','8,2,99,1,90,1','9,6,0,0,0,0','10,1,13,1,100,1']
    books=[book(x) for x in (30,35,32,27,27,27,20,20,20,21)];books[7][7]=20;books[8][7]=20;books[9][7]=20
    return messages,books

def manifest(messages,reference):
    return dict(schema='gig.lobster.run.v1',origin='synthetic',dataset='authored-lobster-pair',session='authored-session',instrument=dict(symbol='SYNTH',native_id=1,venue_id=1),initialization='unknown',message_sha256=hashlib.sha256(messages).hexdigest(),reference_sha256=hashlib.sha256(reference).hexdigest(),permission=dict(cloud_processing_approved=False,scope='private-research',evidence_reference='independently-authored-fixture',derivative_reporting_approved=True))

def write(directory,message_rows,book_rows):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    m=('\n'.join(message_rows)+'\n').encode();b=('\n'.join(','.join(map(str,r)) for r in book_rows)+'\n').encode()
    (directory/'authored-messages.csv').write_bytes(m);(directory/'authored-reference.csv').write_bytes(b)
    data=manifest(m,b);(directory/'manifest.json').write_text(json.dumps(data,indent=2)+'\n');return data,directory/'authored-messages.csv',directory/'authored-reference.csv'
