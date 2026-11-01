"""Build once and run actual native/browser fixtures with a loopback-only Python guard.

Requires the installed native package,server dependencies,Node,Playwright and Chromium.
Never kills an existing listener,changes port visibility or accesses a provider.
Evidence is local and authored-only. Rebuilds never race the browser programs.
"""
from pathlib import Path
import os,subprocess,socket,time,json,urllib.request,hashlib,tempfile
import argparse,sys
parser=argparse.ArgumentParser(description='Offline provider-disabled native/browser qualification;owns only its child servers')
parser.add_argument('--output',type=Path,default=Path('build/sprint3-qualification'))
parser.add_argument('--node-modules',type=Path,help='Optional existing Playwright modules;creates/removes only a new test-local symlink')
parser.add_argument('--skip-build',action='store_true',help='Require finalized assets already built;hash checks still enforce immutability')
args=parser.parse_args();work=Path(__file__).resolve().parents[2];out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);env=dict(os.environ)
if not args.skip_build:
 with (out/'build.log').open('w')as log:subprocess.run(['npm','--offline','--prefix','terminal/web','run','build'],cwd=work,check=True,stdout=log,stderr=subprocess.STDOUT)
if not (work/'terminal/web/dist/.vite/manifest.json').is_file():raise SystemExit('Build finalized frontend assets first')
env['PYTHONPATH']=str(work/'terminal/tests/offline_guard')+os.pathsep+str(work)+os.pathsep+env.get('PYTHONPATH','')
# Native wheel/build path is supplied by the invoking validated environment.
(out/'visual').mkdir(parents=True,exist_ok=True)
env['GIG_SPRINT3_EVIDENCE']=str(out/'visual')
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):env[k]='0'
for k in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):env.pop(k,None)
private=tempfile.TemporaryDirectory(prefix='gig-s3-fixtures-',dir='/tmp');env['GIG_SPRINT3_PAPER']=private.name+'/private'
link=work/'terminal/tests/node_modules';owned_link=False
if not link.exists():
 if args.node_modules is None or not args.node_modules.resolve().is_dir():raise SystemExit('Install terminal/tests dependencies first;no dependency download is automatic')
 link.symlink_to(args.node_modules.resolve(),target_is_directory=True);owned_link=True
code="from terminal.server.app import create_app;from terminal.stocks.service import StockWorkspace;from terminal.paper.workspace import PaperWorkspace;import uvicorn,os;uvicorn.run(create_app(stock_workspace=StockWorkspace(environment={}),paper_workspace=PaperWorkspace(os.environ['GIG_SPRINT3_PAPER'])),host='127.0.0.1',port=8787,proxy_headers=False)"
servers=[('native',8787,['-c',code]),('stock',18787,['terminal/tests/stock_fixture_server.py']),('atlas',18788,['terminal/tests/atlas_fixture_server.py']),('atlas2',18789,['terminal/tests/atlas2_fixture_server.py']),('live',18797,['terminal/tests/live_market_fixture_server.py']),('workspaces',18798,['terminal/tests/phase_next_fixture_server.py'])]
def snapshot():return {str(p.relative_to(work/'terminal/web/dist')):hashlib.sha256(p.read_bytes()).hexdigest()for p in (work/'terminal/web/dist').rglob('*')if p.is_file()}
env['TERMINAL_URL']='http://127.0.0.1:8787';env['TERMINAL_EVIDENCE']=str(out/'native-browser')
# Bind public source bytes without enumerating private configuration/data trees.
paths=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=work).split(b'\0')
source={}
for raw in paths:
 name=raw.decode()
 if name.startswith(('terminal/web/src/','terminal/server/','terminal/paper/','terminal/stocks/','terminal/providers/','terminal/tests/')) and name.endswith(('.py','.mjs','.ts','.tsx','.css')):
  source[name]=hashlib.sha256((work/name).read_bytes()).hexdigest()
receipt={'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip(),
         'tracked_dirty':bool(subprocess.check_output(['git','diff','HEAD','--name-only'],cwd=work)),
         'source_sha256':dict(sorted(source.items())),'assets':snapshot(),
         'scope':'Offline fixtures on this machine;not provider,ARM64 or Codespaces authentication evidence'}
(out/'source-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
processes=[];logs=[];before=snapshot();rows=[]
try:
 for name,port,args in servers:
  with socket.socket()as guard:guard.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);guard.bind(('127.0.0.1',port))
  log=(out/(name+'-final-server.log')).open('w');logs.append(log)
  p=subprocess.Popen([sys.executable,*args],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT);processes.append(p)
  for _ in range(100):
   if p.poll()is not None:raise AssertionError(name+' exited')
   try:
    with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/api/v1/health',timeout=1)as response:assert json.load(response)['fixture_tests_safe']is True
    break
   except OSError:time.sleep(.1)
  else:raise AssertionError(name+' not ready')
 for name in ('browser-validation','contrast-scan','measure_sprint3_browser','stock-intelligence-validation','stock-loading-validation','atlas-validation','atlas2-validation','advanced-research-validation','workspace-qualification','check_bootstrap_sop','check_browser_handshake','sprint3-validation'):
  assert snapshot()==before,'assets changed before'+name
  begin=time.monotonic()
  with(out/(name+'-final.log')).open('w')as log:r=subprocess.run(['node','terminal/tests/'+name+'.mjs'],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
  rows.append({'script':name,'exit_code':r.returncode,'seconds':time.monotonic()-begin});(out/'browser-final-matrix.json').write_text(json.dumps(rows,indent=2)+'\n')
  print(name,r.returncode,round(time.monotonic()-begin,3),flush=True)
  assert snapshot()==before,'assets changed during'+name
  if r.returncode:raise AssertionError(name+' failed;preserve log')
 (out/'stable-assets-final.json').write_text(json.dumps({'assets':before,'mutated':False,'scope':'Built before browser;authored fixtures,not provider/owner target'},indent=2)+'\n')
finally:
 for p in processes:
  p.terminate()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 for log in logs:log.close()
 if owned_link:link.unlink()
 private.cleanup()
