"""Seal log hashes only after the verification subprocess has exited successfully."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent;path=root/'packaging-verification.json';r=json.loads(path.read_text())
def hashed(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for name,record in r['logs'].items():
 if name!='verification-progress.log':assert hashed(root/name)==record,name
for name,record in r['packages'].items():assert hashed(root/'packages'/name)==record,name
config=json.loads((root/'configuration.json').read_text())
assert r['profiles']['default']['sdk']['tests']==8 and r['profiles']['default']['source']['tests']==config['expected_source_tests']
assert r['profiles']['streaming']['sdk']['tests']==8 and r['profiles']['streaming']['source']['tests']==33
for profile in r['profiles'].values():
 for result in profile.values():assert result['failures']==result['errors']==result['skipped']==0
config=json.loads((root/'configuration.json').read_text())
assert r['source']==config['source']
assert hashed(Path(config['guard_log']['path']))=={k:v for k,v in config['guard_log'].items()if k!='path'}
assert r['installed_ui']['statement_comparison']==43 and r['installed_comparison_exports']['variants']==19
assert r['installed_ui']['tests']==config['expected_ui_tests']and r['installed_ui']['failed']==r['installed_ui']['skipped']==0
assert '"receipt":'in(root/'verification-progress.log').read_text().splitlines()[-1]
r['logs']['verification-progress.log']=hashed(root/'verification-progress.log');r['progress_stream_sealed_after_exit']=True
r['verification_helpers']={name:hashed(root/name)for name in ('package-and-verify.py','installed-checks.py','seal-packaging-evidence.py')}
path.write_text(json.dumps(r,indent=2)+'\n')
for name,record in r['logs'].items():assert hashed(root/name)==record,name
print(json.dumps({'source':r['source'],'profiles':{k:{t:v['tests']for t,v in p.items()}for k,p in r['profiles'].items()},'ui':r['installed_ui'],'packages':r['packages'],'retained_log_hashes_verified':len(r['logs'])},sort_keys=True))
