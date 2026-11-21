"""Seal the progress stream only after package-and-verify has exited successfully."""
from pathlib import Path
import hashlib,json
w=Path(__file__).resolve().parent;p=w/'packaging-verification.json';r=json.loads(p.read_text())
def hashed(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for name,record in r['logs'].items():
 if name!='verification-progress.log':assert hashed(w/name)==record,name
for name,record in r['packages'].items():assert hashed(w/'packages'/name)==record,name
assert r['profiles']['default']['sdk']['tests']==8 and r['profiles']['default']['source']['tests']==773
assert r['profiles']['streaming']['sdk']['tests']==8 and r['profiles']['streaming']['source']['tests']==22
for profile in r['profiles'].values():
 for result in profile.values():assert result['failures']==result['errors']==result['skipped']==0
assert '"receipt":'in(w/'verification-progress.log').read_text().splitlines()[-1]
r['logs']['verification-progress.log']=hashed(w/'verification-progress.log')
r['progress_stream_sealed_after_exit']=True
p.write_text(json.dumps(r,indent=2)+'\n')
for name,record in r['logs'].items():assert hashed(w/name)==record,name
print(json.dumps({'source':r['source'],'profiles':{k:{t:v['tests']for t,v in p.items()}for k,p in r['profiles'].items()},'packages':r['packages'],'retained_log_hashes_verified':len(r['logs'])},sort_keys=True))
