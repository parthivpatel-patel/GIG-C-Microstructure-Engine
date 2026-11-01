"""Finalized assets,owned loopback fixture,network guard and bounded browser run."""
import argparse,hashlib,json,os,socket,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--node-modules',required=True,type=Path);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);work=Path(__file__).resolve().parents[2]
def snapshot():return {str(p.relative_to(work/'terminal/web/dist')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(work/'terminal/web/dist').rglob('*')if p.is_file()}
before=snapshot();assert before,'Build assets first;never rebuild concurrently'
with socket.socket()as guard:guard.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);guard.bind(('127.0.0.1',18804))
link=work/'terminal/tests/node_modules';owned=False
if not link.exists():link.symlink_to(a.node_modules.resolve(),target_is_directory=True);owned=True
with tempfile.TemporaryDirectory(prefix='gig-sprint4-')as d:
 env=dict(os.environ);env.update(PYTHONPATH=str(work/'terminal/tests/offline_guard')+':'+str(work)+':'+env.get('PYTHONPATH',''),GIG_SPRINT4_PRIVATE=d,GIG_SPRINT4_EVIDENCE=str(out),GIG_SEC_ENABLED='0',GIG_ALPACA_ENABLED='0',GIG_LIVE_ENABLED='0',GIG_COINBASE_ENABLED='0')
 for k in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):env.pop(k,None)
 with(out/'server.log').open('w')as log:
  child=subprocess.Popen([sys.executable,'terminal/tests/sprint4_fixture_server.py'],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
  try:
   for _ in range(100):
    if child.poll()is not None:raise RuntimeError('Fixture exited')
    try:
     with urllib.request.urlopen('http://127.0.0.1:18804/api/v1/health',timeout=1)as r:assert json.load(r)['fixture_tests_safe']is True
     break
    except OSError:time.sleep(.1)
   else:raise RuntimeError('Fixture not ready')
   with(out/'browser.log').open('w')as browserlog:result=subprocess.run(['node','terminal/tests/sprint4-validation.mjs'],cwd=work,env=env,stdout=browserlog,stderr=subprocess.STDOUT,timeout=240)
   assert snapshot()==before,'Assets changed during browser run'
   (out/'assets.json').write_text(json.dumps(before,indent=2)+'\n');raise SystemExit(result.returncode)
  finally:
   child.terminate()
   try:child.wait(timeout=8)
   except subprocess.TimeoutExpired:child.kill();child.wait()
   if owned:link.unlink()
