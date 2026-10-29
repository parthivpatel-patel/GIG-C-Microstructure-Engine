#!/usr/bin/env python3
"""Build once,run all current browser journeys serially,retain isolated safe evidence."""
import argparse,hashlib,json,os,re,socket,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SERVERS=[('stock_fixture_server',18787),('atlas_fixture_server',18788),('atlas2_fixture_server',18789),('atlas4_fixture_server',18792),('atlas5_fixture_server',18793),('atlas_final_fixture_server',18794),('sec_fixture_server',18796),('live_market_fixture_server',18797),('phase_next_fixture_server',18798)]
CASES=['browser-validation','stock-intelligence-validation','stock-loading-validation','atlas-validation','atlas2-validation','recorded-playback-validation','live-controls-validation','ratio-history-validation','live-market-validation','sec-completion-validation','discovery-validation','gpu-recovery-validation','market-unavailable-validation','atlas4-validation','atlas5-validation','atlas-final-validation','sec-integration-validation','product-validation','phase-next-validation','advanced-research-validation','workspace-qualification']
def snapshot():return {str(p.relative_to(ROOT/'terminal/web/dist')):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'terminal/web/dist').rglob('*')) if p.is_file()}
def summary(text):
    decoder=json.JSONDecoder();matches=[]
    for m in re.finditer(r'\{',text):
        try:
            v,_=decoder.raw_decode(text[m.start():])
            if type(v) is dict and ('passed'in v or 'summary'in v):matches.append(v)
        except (ValueError,RecursionError):pass
    if matches:return matches[-1].get('summary',matches[-1])
    m=re.search(r'PASS [^\n]+ checks=(\d+)',text) or re.search(r'^PASS ratio-history browser (\d+)$',text,re.M) or re.search(r'^PASS (\d+)/\1 [^\n]+$',text,re.M)
    if m:return {'passed':int(m[1]),'failed':0,'skipped':0}
    raise ValueError('cohort_result_missing')
def main():
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--resume',action='store_true');args=a.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=args.resume)
    work=out/'workspace';work.mkdir(exist_ok=args.resume);(work/'terminal/web').mkdir(parents=True,exist_ok=args.resume)
    if not args.resume:(work/'terminal/web/dist').symlink_to(ROOT/'terminal/web/dist',target_is_directory=True)
    for name in ('terminal','live-market','product','final','readiness','completion','advanced-3d','development-next'):(work/'build'/name).mkdir(parents=True,exist_ok=True)
    env={k:v for k,v in os.environ.items() if not k.startswith(('GIG_','ALPACA_','APCA_','CODESPACE','GITHUB_CODESPACES_'))}
    env.update(GIG_SEC_ENABLED='0',GIG_ALPACA_ENABLED='0',GIG_LIVE_ENABLED='0',GIG_COINBASE_ENABLED='0',PYTHONPATH=os.environ.get('PYTHONPATH',str(ROOT)),TERMINAL_URL='http://127.0.0.1:8787',TERMINAL_EVIDENCE=str(work/'build/terminal/browser'),GIG_MARKET_EVIDENCE=str(work/'build/live-market'),GIG_TERMINAL_L2_RECORDINGS=str(out/'l2-fixture'))
    servers=[];prior=json.loads((out/'campaign.json').read_text()) if args.resume else {};results=prior.get('cases',[]);failed_attempts=prior.get('failed_attempts',[]);expected=prior.get('assets')
    if args.resume:
        for item in list(results):
            if item['returncode']:
                original=out/(item['case']+'.log');archived=out/(item['case']+'.failed-'+str(len(failed_attempts)+1)+'.log');archived.write_bytes(original.read_bytes());failed_attempts.append({**item,'preserved_log':str(archived)});results.remove(item)
    for item in results:
        if item['returncode'] or snapshot()!=expected:raise RuntimeError('Cannot reuse failed or stale-asset evidence')
        path=out/(item['case']+'.log');digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get('log_sha256',digest)!=digest:raise RuntimeError('Changed prior cohort evidence')
        item['log_sha256']=digest
    def save():
        (out/'campaign.json').write_text(json.dumps({'schema':'gig.atlas.offline.campaign.v1','fixture_only':True,'cases':results,'failed_attempts':failed_attempts,'assets':expected,'all_passed':len(results)==len(CASES)+2 and all(r['returncode']==0 for r in results),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'working_tree_dirty':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())},indent=2)+'\n')
    try:
        for port in [8787]+[p for _,p in SERVERS]:
            with socket.socket() as sock:
                sock.settimeout(.1)
                if sock.connect_ex(('127.0.0.1',port))==0:raise RuntimeError(f'Fixture port{port} already occupied;no process changed')
        if not args.resume:
            with (out/'build.log').open('w') as log:subprocess.run(['npm','--prefix','terminal/web','run','build'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
            expected=snapshot()
        native="import os;os.environ['GIG_TERMINAL_ALLOWED_ORIGINS']='http://127.0.0.1:8787';from terminal.server.app import create_app;from terminal.stocks.service import StockWorkspace;import uvicorn;uvicorn.run(create_app(stock_workspace=StockWorkspace(environment={})),host='127.0.0.1',port=8787)"
        for name,port,command in [('native',8787,[sys.executable,'-c',native])]+[(n,p,[sys.executable,str(ROOT/'terminal/tests'/f'{n}.py')])for n,p in SERVERS]:
            log=(out/(name+'.log')).open('w');process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT);servers.append((process,log))
            deadline=time.monotonic()+15
            while True:
                if process.poll() is not None:raise RuntimeError(name+' fixture startup failed')
                try:
                    with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/v1/health',timeout=1)as r:health=json.load(r)
                    if health.get('fixture_tests_safe') is not True:raise RuntimeError('Refusing non-fixture source')
                    break
                except (OSError,ValueError):
                    if time.monotonic()>deadline:raise RuntimeError(name+' fixture readiness timeout')
                    time.sleep(.1)
        commands=[(n,['node',str(ROOT/'terminal/tests'/f'{n}.mjs')],env)for n in CASES]+[('gpu-quote',['node',str(ROOT/'terminal/tests/gpu-recovery-validation.mjs')],{**env,'GIG_GPU_CASE':'quote'}),('performance',['node',str(ROOT/'terminal/tests/atlas-final-performance.mjs')],env)]
        for name,command,caseenv in commands:
            if any(item['case']==name for item in results):continue
            if snapshot()!=expected:raise RuntimeError('Assets mutated before '+name)
            # Reset only the dedicated native fixture,awaiting each acknowledged mutation.
            for action in ({'action':'mode','value':'HISTORICAL_REPLAY'},{'action':'restart'}):
                req=urllib.request.Request('http://127.0.0.1:8787/api/v1/control',data=json.dumps(action).encode(),headers={'Origin':'http://127.0.0.1:8787','Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=5)as response:assert response.status==200
            start=time.monotonic()
            with (out/(name+'.log')).open('w')as log:r=subprocess.run(command,cwd=work,env=caseenv,stdout=log,stderr=subprocess.STDOUT,timeout=300)
            entry={'case':name,'command':command,'cwd':str(work),'returncode':r.returncode,'elapsed_seconds':time.monotonic()-start,'log_sha256':hashlib.sha256((out/(name+'.log')).read_bytes()).hexdigest()}
            if name!='performance' and r.returncode==0:entry['summary']=summary((out/(name+'.log')).read_text());assert entry['summary'].get('passed',0)>0 and not entry['summary'].get('failed',0) and not entry['summary'].get('skipped',0)
            if snapshot()!=expected:raise RuntimeError('Assets mutated during '+name)
            results.append(entry);save();print(name+' '+str(r.returncode),flush=True)
            if r.returncode:raise RuntimeError(name+' failed;original log retained')
        return 0
    finally:
        for process,log in reversed(servers):
            process.terminate()
            try:process.wait(timeout=8)
            except subprocess.TimeoutExpired:process.kill();process.wait()
            log.close()
        save()
if __name__=='__main__':raise SystemExit(main())
