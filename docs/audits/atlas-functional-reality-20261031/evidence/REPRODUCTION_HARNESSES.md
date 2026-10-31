# Temporary audit reproduction harnesses

These are documentation transcripts of the executed audit-only harnesses,not application changes. Exact candidate5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9. Absolute paths reflect this environment;adapt the audit root only when reproducing. Never run fixture scripts against an operator live-enabled server. Private inputs are not read. The body-budget fixture overrides only its owned local synthetic endpoint,never production source.

## geometry.mjs

SHA256 `9445e15a12c8ea252fd43403a0601c3ee435bccc43bc96fc3b9371d65f6f8f83`

```javascript
import assert from 'node:assert/strict';import {test} from 'node:test';import fs from 'node:fs';
import {buildResearchPlot,levelOneResearch,vpinBuckets,executionVwap} from './worktree/terminal/web/src/research3d.ts';
import {researchPoints} from './worktree/terminal/web/src/marketGeometry.ts';
import {garchGrid} from './worktree/terminal/web/src/modelSurface.ts';
const observations=[];const close=(a,b)=>assert.ok(Math.abs(a-b)<=1e-11*Math.max(1,Math.abs(b)),`${a} versus ${b}`);
function book(n,q='10'){return {ordinal:n,time:String(n*1000000),symbol:'X',scale:'1',quantityScale:'1',bids:[{price_ticks:'99',quantity:q},{price_ticks:'98',quantity:'20'}],asks:[{price_ticks:'101',quantity:'20'},{price_ticks:'102',quantity:'20'}]}}
function event(n,q='10',price='100',aggressor='buy'){return {ordinal:n,time:String(n*1000000),symbol:'X',kind:'EXECUTE',order:'AUTHORED-'+n,side:aggressor==='buy'?'ask':'bid',price,quantity:q,aggressor}}
function source(q='10'){return {id:'audit-authored',origin:'HISTORICAL_SYNTHETIC',provider:'Independent audit fixture',coverage:'AUTHORED ONLY',symbols:['X'],books:[book(1,q),book(2,q)],events:[event(1,q),event(2,'20','120','sell')],quotes:Array.from({length:12},(_,i)=>({ordinal:i+1,time:String((i+1)*1000000),symbol:'X',scale:'1',bid:String(100*2**i),ask:String(100*2**i),bidSize:'10/1',askSize:'20/1',state:'SIMULATED'})),notes:[]}}
const models=['height','canyon','events','vwap','flow','wheel','dome','ribbon'];
for(const model of models){
 test(model+':deterministic changing input,zero change,empty,stale,disconnected,extremes,units',()=>{
  let s=source();if(model==='ribbon')s.quotes=s.quotes.map(q=>({...q,ask:String(Number(q.bid)+2)}));
  const plot=()=>buildResearchPlot(s,model,'X',12,3);const a=plot();assert.ok(a.marks.length>0);assert.deepEqual(a,plot());assert.equal(a.axes.length,3);assert.ok(a.notes.length&&a.summary.length);assert.ok(a.marks.every(m=>[m.x,m.y,m.z,m.value].every(Number.isFinite)));
  const empty=buildResearchPlot({...s,books:[],events:[],quotes:[]},model,'X',12);assert.equal(empty.marks.length,0);
  const scoped=buildResearchPlot(s,model,'OTHER',12);assert.equal(scoped.marks.length,0);
  const prior=buildResearchPlot(s,model,'X',1,3);assert.ok(prior.marks.length<a.marks.length||model==='flow'||model==='events'||model==='vwap');
  if(['height','canyon','wheel','events','flow'].includes(model)){
   const val=q=>{const p=buildResearchPlot(source(q),model,'X',12,3);return p.marks.find(m=>model==='events'||model==='flow'?m.ordinal===1:m.label.startsWith('BID')).value};
   assert.equal(val('10'),10);assert.equal(val('15'),15);assert.equal(val('5'),5);
   const extreme=buildResearchPlot(source('18446744073709551615'),model,'X',12,3);assert.ok(extreme.marks.every(m=>[m.x,m.y,m.z,m.value].every(Number.isFinite)));
  }
  if(model==='vwap'){close(a.marks.at(-1).value,340/3);const s2=source();s2.events[0].price='110';close(buildResearchPlot(s2,model,'X',12).marks.at(-1).value,350/3);s2.events[0].price='90';close(buildResearchPlot(s2,model,'X',12).marks.at(-1).value,330/3)}
  if(model==='ribbon'){assert.ok(a.marks.every(m=>m.value===2));s.quotes=s.quotes.map(q=>({...q,ask:String(Number(q.bid)+3)}));assert.ok(plot().marks.every(m=>m.value===3));s.quotes=s.quotes.map(q=>({...q,ask:q.bid}));assert.ok(plot().marks.every(m=>m.value===0))}
  if(model==='dome'){close(a.marks[0].value,Math.sqrt(8)*Math.log(2));for(const factor of [1,2,3]){s.quotes=s.quotes.map((q,i)=>({...q,bid:String(100*factor**i),ask:String(100*factor**i)}));close(plot().marks[0].value,Math.sqrt(8)*Math.log(factor))}}
  // Retained stale observations may remain displayed,never gain a live state.
  for(const state of ['STALE','UNAVAILABLE']){s=source();s.quotes=s.quotes.map(q=>({...q,state}));const p=plot();if(['dome','ribbon'].includes(model))assert.ok(p.summary.some(v=>v.includes(state)&&v.includes('not a currentness guarantee')))}
  observations.push({model,classification:'SIMULATED',data_driven_mapping:true,provider_verified:false,marks:a.marks.length,axes:a.axes,limits:'Normalized geometry may be unchanged by uniform rescaling;no motion is fabricated'});
 });
}
function quote(n,mid=100,state='SIMULATED'){return {symbol:'X',kind:'quote',origin:'HISTORICAL_SYNTHETIC',generation:1,receipt_index:n,timestamp:'2024-01-02T14:30:00Z',source_timestamp_ns:String(n),out_of_order:false,state,data:{bid:String(mid),ask:String(mid),bid_size:'10',ask_size:'20'}}}
for(const mode of ['quotes','comparison','volatility','trades'])test('Level1 '+mode+':changing input,empty,flat,extreme,state,independent formula',()=>{
 let rows=Array.from({length:12},(_,i)=>quote(i+1,100*2**i));if(mode==='trades')rows=rows.map((r,i)=>({...r,kind:'trade',data:{price:'100',size:String(i+1)}}));
 const a=researchPoints(rows,['X'],mode);assert.ok(a.length);assert.deepEqual(a,researchPoints(rows,['X'],mode));assert.equal(researchPoints([],['X'],mode).length,0);assert.equal(researchPoints(rows,['OTHER'],mode).length,0);
 if(mode==='quotes')assert.equal(a.at(-1).value,204800);
 if(mode==='comparison')close(a.at(-1).value,(2**11-1)*10000);
 if(mode==='volatility')close(a.at(-1).value,Math.sqrt(8)*Math.log(2));
 if(mode==='trades')close(a.at(-1).value,Math.log(13));
 if(mode!=='trades'){const flat=researchPoints(Array.from({length:12},(_,i)=>quote(i+1,100)),['X'],mode);if(mode!=='quotes')assert.ok(flat.every(p=>p.value===0));const up=researchPoints(Array.from({length:12},(_,i)=>quote(i+1,100+i)),['X'],mode);const down=researchPoints(Array.from({length:12},(_,i)=>quote(i+1,100-i)),['X'],mode);assert.ok(up.length&&down.length);const extreme=researchPoints(Array.from({length:12},(_,i)=>quote(i+1,1e15)),['X'],mode);assert.ok(extreme.every(p=>Number.isFinite(p.value)))}
 for(const state of ['STALE','UNAVAILABLE'])assert.ok(researchPoints(rows.map(r=>({...r,state})),['X'],mode).every(p=>p.row.state===state));
 observations.push({model:'L1-'+mode,classification:'SIMULATED',data_driven_mapping:true,provider_verified:false,marks:a.length});
});
test('GARCH:all441 mathematical vertices,flat/increase/decrease/missing/extreme parameters',()=>{
 const a=garchGrid(.000001,.08,.9).flat();assert.equal(a.length,441);for(const p of a)close(p.variance,.000001+.08*p.shock**2+.9*p.priorVariance);
 assert.ok(garchGrid(.000001,0,0).flat().every(p=>p.variance===.000001));const b=garchGrid(.000002,.08,.9).flat(),c=garchGrid(0,.08,.9).flat();a.forEach((p,i)=>{assert.ok(b[i].variance>p.variance);assert.ok(c[i].variance<p.variance)});
 for(const args of [[NaN,.08,.9],[undefined,.08,.9],[-1,.08,.9],[0,1,1],[Infinity,0,0]])assert.throws(()=>garchGrid(...args));
 observations.push({model:'GARCH-response',classification:'SIMULATED',data_driven_mapping:true,provider_verified:false,vertices:441,limits:'No stale/disconnected market input applies;declared parameter model,not observed surface'});
});
test('Independent VPIN/VWAP direction/volume arithmetic,not depth-implied flow',()=>{
 const ev=[event(1,'10','100','buy'),event(2,'10','100','sell'),event(3,'10','100','buy'),event(4,'10','100','sell'),event(5,'10','100','buy'),event(6,'10','100','sell'),event(7,'10','100','buy'),event(8,'10','100','sell')];assert.equal(vpinBuckets(ev).buckets.at(-1).vpin,0);assert.equal(executionVwap([event(1,'3','100'),event(2,'7','110')]).at(-1).numerator,1070n);
 const noDirection=structuredClone(ev);delete noDirection[0].aggressor;assert.equal(vpinBuckets(noDirection).buckets.length,0);
});
process.on('exit',()=>fs.writeFileSync(new URL('./evidence/geometry-observations.json',import.meta.url),JSON.stringify({scope:'Independent authored changing-input numerical tests;not actual market validation',models:observations},null,2)));

```

## independent_math.py

SHA256 `435d68dbe7d7d91c5a31b816a6981899216ad4b00320f82e96b142c879111d7f`

```python
import copy,itertools,math,sys,unittest
from fractions import Fraction as F
from unittest.mock import Mock,patch
from starlette.testclient import TestClient
from terminal.stocks.quote_analytics import analyze as quote
from terminal.stocks.models import hmm_filter,kalman,garch_likelihood
from terminal.stocks.portfolio import analyze as portfolio
from terminal.stocks.research import analyze as research
from terminal.stocks.options import price
from terminal.stocks.alpaca_transport import validate_url
from terminal.stocks.service import StockWorkspace
from terminal.server.app import create_app

def rational(v):return F(int(v['numerator']),int(v['denominator']))
class IndependentMath(unittest.TestCase):
 def test_native_best_quote_independent_rationals(self):
  m=quote({'bid':'100','ask':'102','bid_size':'80','ask_size':'20'})['metrics']
  expected={'spread':F(2),'midpoint':F(101),'microprice':F(508,5),'depth_imbalance':F(3,5),'bid_depth':F(80),'ask_depth':F(20)}
  self.assertEqual({k:rational(v)for k,v in m.items()},expected)
 def test_hmm_against_brute_force_all_hidden_paths(self):
  x=[.01,-.02,.03];means=[-.01,.01];v=[.0001,.0004];a=[[.8,.2],[.1,.9]];p=[.6,.4];weights=[0.,0.]
  for path in itertools.product((0,1),repeat=3):
   w=p[path[0]]
   for i,j in enumerate(path):
    if i:w*=a[path[i-1]][j]
    w*=math.exp(-(x[i]-means[j])**2/(2*v[j]))/math.sqrt(2*math.pi*v[j])
   weights[path[-1]]+=w
  ll,post,_,_=hmm_filter(x,means,v,a,p);self.assertAlmostEqual(ll,math.log(sum(weights)),places=12)
  for j in (0,1):self.assertAlmostEqual(post[-1][j],weights[j]/sum(weights),places=12)
 def test_kalman_closed_form_and_missing_prediction(self):
  rows=kalman([.1,None])['states'];prediction=1.00001;gain=prediction/(prediction+.001)
  self.assertAlmostEqual(rows[0]['estimate'],gain*.1,places=14);self.assertAlmostEqual(rows[0]['variance'],prediction*.001/(prediction+.001),places=14)
  self.assertEqual(rows[1]['estimate'],rows[0]['estimate']);self.assertAlmostEqual(rows[1]['variance'],rows[0]['variance']+1e-5,places=14)
 def test_garch_direct_two_step_likelihood(self):
  ll,path,last=garch_likelihood([.1,-.1],0,.002,.1,.5,.01);self.assertEqual(path[0],.01);self.assertAlmostEqual(path[1],.008);self.assertAlmostEqual(last,.007)
  reference=-.5*(math.log(2*math.pi*.01)+1)-.5*(math.log(2*math.pi*.008)+1.25);self.assertAlmostEqual(ll,reference,places=12)
 def test_portfolio_exact_sample_variance_and_tail(self):
  data={'assets':{'A':['0.01','-0.01']*10,'B':['-0.02','0.02']*10},'weights':{'A':'0.6','B':'0.4'}};out=portfolio(data)
  self.assertEqual([rational(v)for v in out['portfolio_returns']],[F(-1,500),F(1,500)]*10)
  self.assertEqual(rational(out['historical_var']),F(1,500));self.assertEqual(rational(out['historical_es']),F(1,500))
  w=[F(3,5),F(2,5)];cov=out['sample_covariance'];self.assertEqual(sum(w[i]*w[j]*rational(cov[i][j])for i in range(2)for j in range(2)),F(1,237500))
 def test_authored_causal_turnover_backtest(self):
  out=research(['0.01']*20);self.assertEqual(out['strategy']['positions'],[0]*5+[1]*15)
  self.assertEqual(rational(out['strategy']['terminal_wealth']),F(10099,10000)*F(101,100)**14)
  a=['0.01']*40;b=a[:25]+['-0.02']*15;self.assertEqual(research(a)['strategy']['equity_curve'][:25],research(b)['strategy']['equity_curve'][:25])
 def test_options_raw_value_is_correct_despite_stale_browser_assertion(self):
  self.assertAlmostEqual(price(100,100,1,.2)['price'],7.965567455405804,places=12)
  self.assertEqual(format(price(100,100,1,.2)['price'],'.4g'),'7.966')
class PaperBoundary(unittest.TestCase):
 def test_order_account_position_rest_destinations_rejected_without_fetch(self):
  for host in ('paper-api.alpaca.markets','api.alpaca.markets'):
   for endpoint in ('orders','account','positions'):
    with self.subTest(host=host,endpoint=endpoint),self.assertRaises(ValueError):validate_url('https://'+host+'/v2/'+endpoint,'alpaca')
 def test_order_routes_absent_no_upstream_or_permission_changes(self):
  workspace=StockWorkspace(environment={});fetcher=Mock(side_effect=AssertionError('network prohibited'));workspace.fetcher=fetcher
  with TestClient(create_app(stock_workspace=workspace),base_url='http://127.0.0.1:8787')as c:
   for endpoint in ('/api/v1/orders','/api/v1/paper/orders','/api/v1/trading/orders'):
    response=c.post(endpoint,json={'symbol':'AAPL','qty':'1'},headers={'Origin':'http://127.0.0.1:8787'})
    self.assertIn(response.status_code,(403,404,405))
  fetcher.assert_not_called();self.assertEqual(workspace.environment,{})
if __name__=='__main__':unittest.main(verbosity=2)

```

## browser.py

SHA256 `fe498558aecca261daea60db4287ef46632c9f732b142202c02a2d643d469970`

```python
from pathlib import Path
import os,subprocess,socket,time,json,urllib.request,hashlib
work=Path('/workspace/GIG-C-Microstructure-Engine/build/functional-reality-audit/worktree');out=work.parent/'evidence';env=dict(os.environ);env['PYTHONPATH']=str(work.parent/'offline-guard')+':/workspace/GIG-C-Microstructure-Engine/build/python-release/python:'+str(work);env['GIG_TERMINAL_NATIVE_BUILD']='/workspace/GIG-C-Microstructure-Engine/build/python-release'
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):env[k]='0'
for k in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):env.pop(k,None)
link=work/'terminal/tests/node_modules';link.symlink_to('/workspace/GIG-C-Microstructure-Engine/terminal/tests/node_modules',target_is_directory=True)
code="from terminal.server.app import create_app;from terminal.stocks.service import StockWorkspace;import uvicorn;uvicorn.run(create_app(stock_workspace=StockWorkspace(environment={})),host='127.0.0.1',port=8787,proxy_headers=False)"
servers=[('native',8787,['-c',code]),('live-fixture',18797,['terminal/tests/live_market_fixture_server.py']),('workspace-fixture',18798,['terminal/tests/phase_next_fixture_server.py'])]
processes=[];logs=[];before={str(p.relative_to(work/'terminal/web/dist')):hashlib.sha256(p.read_bytes()).hexdigest()for p in (work/'terminal/web/dist').rglob('*')if p.is_file()};rows=json.loads((out/'browser-matrix.json').read_text())
try:
 for name,port,args in servers:
  with socket.socket()as guard:guard.bind(('127.0.0.1',port))
  log=(out/(name+'-browser-server.log')).open('w');logs.append(log)
  p=subprocess.Popen(['/workspace/gig-terminal-clean-venv/bin/python',*args],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT);processes.append(p)
  for _ in range(100):
   if p.poll()is not None:raise AssertionError(name+' exited')
   try:
    with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/api/v1/health',timeout=1)as response:assert json.load(response)['fixture_tests_safe']is True
    break
   except OSError:time.sleep(.1)
  else:raise AssertionError(name+' not ready')
 for name in ('advanced-research-validation',):
  begin=time.monotonic()
  with(out/(name+'.log')).open('w')as log:r=subprocess.run(['node','terminal/tests/'+name+'.mjs'],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
  rows.append({'script':name,'exit_code':r.returncode,'seconds':time.monotonic()-begin});(out/'browser-matrix.json').write_text(json.dumps(rows,indent=2)+'\n')
  if r.returncode:raise AssertionError(name+' failed;preserve log')
 # Extra audit-only test lives outside source. It explicitly checks native/BS updates.
 with(out/'legacy-3d-browser.log').open('w')as log:r=subprocess.run(['node',str(work.parent/'legacy-3d.mjs')],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120)
 assert r.returncode==0,'legacy-3d'
 after={str(p.relative_to(work/'terminal/web/dist')):hashlib.sha256(p.read_bytes()).hexdigest()for p in (work/'terminal/web/dist').rglob('*')if p.is_file()};assert before==after
 (out/'stable-assets.json').write_text(json.dumps({'assets':after,'mutated':False,'scope':'Built once before browser;authored fixtures,not provider/owner target'},indent=2)+'\n');print('PASS browser cohorts and legacy3D;allassetsstable')
finally:
 for p in processes:
  p.terminate()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 for f in logs:f.close()
 link.unlink()

```

## legacy-3d.mjs

SHA256 `6bfac2c7b6afba842532ea54cd323f22da2cc48399b8c399847897bb8031dc04`

```javascript
import {createRequire}from'node:module';const require=createRequire('/workspace/GIG-C-Microstructure-Engine/terminal/tests/package.json');const {chromium}=require('playwright');import assert from'node:assert/strict';import fs from'node:fs';import crypto from'node:crypto';const out='/workspace/GIG-C-Microstructure-Engine/build/functional-reality-audit/evidence';const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});let checks=[];try{const p=await b.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});await p.goto('http://127.0.0.1:8787');await p.getByTestId('connection-status').filter({hasText:'CONNECTED'}).waitFor();const nav=p.getByRole('navigation',{name:'Research sections',exact:true});await nav.getByRole('button',{name:'Market Depth',exact:true}).click();const panel=p.locator('.landscape-panel');const toggle=panel.getByRole('button');console.log('Landscape buttons',await toggle.allTextContents());const open=panel.getByRole('button',{name:/Enable|Open|3D/}).first();if(await panel.locator('canvas').count()===0)await open.click();const c=panel.locator('canvas');await c.waitFor();const before=await c.screenshot();const state=await(await p.request.get('http://127.0.0.1:8787/api/v1/state')).json();await p.getByRole('button',{name:'Step replay',exact:true}).click();await p.waitForFunction(async n=>(await(await fetch('/api/v1/state')).json()).position===n+1,state.position);await p.waitForTimeout(350);const next=await(await p.request.get('http://127.0.0.1:8787/api/v1/state')).json();assert.equal(next.position,state.position+1);const after=await c.screenshot();assert.equal(before.equals(after),false);checks.push('Native legacy landscape changes actual pixels after native replay event,not camera input');await c.screenshot({path:out+'/legacy-landscape-authored.png'});await nav.getByRole('button',{name:'Stock Intelligence',exact:true}).click();await p.getByRole('navigation',{name:'Stock research sections',exact:true}).getByRole('button',{name:'Options',exact:true}).click();await p.getByRole('button',{name:'Calculate theoretical options',exact:true}).click();const v=p.getByTestId('volatility-canvas');await v.waitFor();const a=await v.screenshot();console.log('labels',await p.locator('label').allTextContents());const vol=p.getByLabel('Scenario volatility',{exact:true});await vol.fill('0.3');await p.getByRole('button',{name:'Calculate theoretical options',exact:true}).click();await p.waitForTimeout(250);assert.equal(a.equals(await v.screenshot()),false);checks.push('Legacy theoretical flat volatility plane changes pixels when declared volatility changes;not observed smile');await v.screenshot({path:out+'/legacy-options-authored.png'});fs.writeFileSync(out+'/legacy-3d.json',JSON.stringify({passed:checks.length,failed:0,checks,scope:'AUTHORED_SYNTHETIC;camera unchanged;legacy modes beyond13 denominator'},null,2));console.log(JSON.stringify({checks,passed:checks.length,failed:0}));}finally{await b.close()}

```

## budget_server.py

SHA256 `075ad2d4d956f49009b1ed03a59cd1cd943a54899370d004127c64ecafc5f412`

```python
import sys,os
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent/'worktree'))
from terminal.server.app import create_app
from terminal.stocks.service import StockWorkspace
from starlette.routing import Route
from starlette.responses import StreamingResponse
import uvicorn
async def authored(request):
 async def chunks():
  for _ in range(48):yield b' '*65536
 return StreamingResponse(chunks(),media_type='application/json')
app=create_app(stock_workspace=StockWorkspace(environment={}))
app.router.routes.insert(0,Route('/api/v1/catalog',authored,methods=['GET']))
uvicorn.run(app,host='127.0.0.1',port=8787,proxy_headers=False)

```

## budget_probe.mjs

SHA256 `52d4d97cf9eaed205862e6da08c7d4eea123e7d6e9c6678d53b32b525f8bafe5`

```javascript
import{createRequire}from'node:module';const require=createRequire('/workspace/GIG-C-Microstructure-Engine/terminal/tests/package.json');const{chromium}=require('playwright');import fs from'node:fs';import assert from'node:assert/strict';const b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});try{const p=await b.newPage();await p.addInitScript(()=>{window.__auditText=[];const original=Response.prototype.text;Response.prototype.text=async function(){const value=await original.call(this);if(this.url.endsWith('/api/v1/catalog'))window.__auditText.push(value.length);return value}});await p.goto('http://127.0.0.1:8787');await p.waitForFunction(()=>window.__auditText.length===1);const consumed=await p.evaluate(()=>window.__auditText[0]);assert.equal(consumed,3145728);const entry=await p.evaluate(()=>performance.getEntriesByType('resource').filter(x=>x.name.endsWith('/api/v1/catalog')).map(x=>({decodedBodySize:x.decodedBodySize,encodedBodySize:x.encodedBodySize,transferSize:x.transferSize})));assert.equal(entry.length,1);assert.equal(entry[0].decodedBodySize,3145728);const x={schema:'gig.audit.response_budget.v1',finding:'S3-BUDGET',reproduced:true,pass:false,application_expected_limit_bytes:2097152,authored_chunked_response_bytes:3145728,resource:entry[0],client_rejection_visible:false,optional_catalog_error_swallowed:true,actual_text_characters_consumed:consumed,scope:'Production generic decoded() reads all text before budget check when Content-Length absent;controlled local synthetic endpoint only;no application source edits'};fs.writeFileSync(new URL('./evidence/response-budget.json',import.meta.url),JSON.stringify(x,null,2));console.log(JSON.stringify(x));}finally{await b.close()}

```

## budget_probe.py

SHA256 `71747560136fddfed2b53ed58da7b0ebc9b6eeb64a5796687c09b91652d70647`

```python
from pathlib import Path
import subprocess,os,socket,time,urllib.request,json
base=Path(__file__).parent;work=base/'worktree';out=base/'evidence';env=dict(os.environ);env['PYTHONPATH']=str(base/'offline-guard')+':/workspace/GIG-C-Microstructure-Engine/build/python-release/python:'+str(work)
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):env[k]='0'
for k in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):env.pop(k,None)
with socket.socket()as s:s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',8787))
with(out/'response-budget-server.log').open('w')as log:
 p=subprocess.Popen(['/workspace/gig-terminal-clean-venv/bin/python',str(base/'budget_server.py')],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
 try:
  for _ in range(50):
   try:
    with urllib.request.urlopen('http://127.0.0.1:8787/api/v1/health',timeout=1)as r:assert json.load(r)['fixture_tests_safe']
    break
   except OSError:time.sleep(.1)
  else:raise AssertionError('fixture startup failed')
  with(out/'response-budget.log').open('w')as log:r=subprocess.run(['node',str(base/'budget_probe.mjs')],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30)
  assert r.returncode==0,'see preserved reproduction log'
 finally:
  p.terminate();p.wait(timeout=8)
print('Reproduced transport-boundary defect;client eventually rejects but consumes3MiB')

```

## controls.mjs

SHA256 `6dcbda36ee260303255fa0dda2cf3d6d43f6b5adc7aa2a9f0fbd5b6e4a07624a`

```javascript
import {createRequire}from'node:module';import fs from'node:fs';import path from'node:path';const require=createRequire('/workspace/GIG-C-Microstructure-Engine/terminal/web/package.json');const ts=require('typescript');const root='/workspace/GIG-C-Microstructure-Engine/build/functional-reality-audit/worktree',rows=[];
for(const name of fs.readdirSync(root+'/terminal/web/src').filter(x=>x.endsWith('.tsx'))){const file='terminal/web/src/'+name,raw=fs.readFileSync(root+'/'+file,'utf8'),source=ts.createSourceFile(file,raw,ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX);function visit(n){if(ts.isJsxOpeningElement(n)||ts.isJsxSelfClosingElement(n)){const tag=n.tagName.getText(source);if(['button','input','select','textarea','summary','option','a','dialog','canvas'].includes(tag)){const attrs={};for(const a of n.attributes.properties)if(ts.isJsxAttribute(a))attrs[a.name.getText(source)]=a.initializer?(ts.isStringLiteral(a.initializer)?a.initializer.text:a.initializer.getText(source)):true;let label=attrs['aria-label']||attrs.title||attrs.placeholder||'';if(!label&&ts.isJsxElement(n.parent))label=n.parent.children.map(c=>c.getText(source)).join(' ').replace(/\s+/g,' ').slice(0,180);if(!label)label=attrs.name||attrs.type||tag;const line=source.getLineAndCharacterOfPosition(n.getStart()).line+1;rows.push({path:file,line,tag,label:String(label).slice(0,200),handler:Object.keys(attrs).filter(k=>k.startsWith('on')),type:attrs.type||null,disabled:attrs.disabled||null});}}ts.forEachChild(n,visit)}visit(source)}
fs.writeFileSync(new URL('./evidence/ui-controls.json',import.meta.url),JSON.stringify(rows,null,2));console.log('Inventoried',rows.length,'static JSX interaction declarations');

```

## inventory.py

SHA256 `8c428adf457a0d8fb2a66f0db90b3e28c81697eedb275c3013ffa4ba5bf5c317`

```python
from pathlib import Path
import json,csv
from collections import Counter
root=Path(__file__).parent/'worktree';e=root.parent/'evidence';dest=root/'docs/audits/atlas-functional-reality-20261031';dest.mkdir(parents=True,exist_ok=True);rows=[]
def add(category,name,classification,path,line=1,functional='VERIFIED_OFFLINE',tests='Actual native/Python/frontend/browser suites;see TEST_EXECUTION_REPORT',evidence='TEST_EXECUTION_REPORT.md',severity='None',action='Preserve declared scope;no provider/empirical qualification inferred',state='IMPLEMENTED'):
 rows.append(dict(feature_id='F%04d'%(len(rows)+1),category=category,feature=name,primary_classification=classification,confidence='High source presence;offline only unless unverified',implementation_status=state,functional_status=functional,source_path=path,source_line=line,dependencies='Existing C++20/native/Python/React/Three stack',data_provenance='Authored inputs or disconnected source;see MARKET_DATA_PROVENANCE.md',runtime_behavior=name,tests=tests,evidence=evidence,failure_handling='Bounded validation/error/unavailable per contract;unexercised individual branches not certified',severity=severity,required_action=action))
workspaces=['Command Center','Securities Universe','Stock Intelligence','Live Markets','Multi-Stock Comparison','Order Book','Market Depth','Order Flow','Historical Replay','Execution Simulator','Research & Validation','Operations']
for name in workspaces:add('workspace',name,'DISCONNECTED'if name in ('Live Markets','Multi-Stock Comparison')else'SIMULATED','terminal/web/src/App.tsx',19,evidence='evidence/workspace-qualification.log',action='Fixture rendering/navigation verified;source/interaction limits in workspace matrix')
texts='\n'.join((root/'terminal/tests'/f'{n}.mjs').read_text()for n in ('workspace-qualification','advanced-research-validation'))+(root.parent/'legacy-3d.mjs').read_text()
for c in json.loads((e/'ui-controls.json').read_text()):
 label=c['label'];clean=label.strip('"');seen=("name:'"+clean+"'")in texts or("getByLabel('"+clean+"'")in texts;seen=seen and c['tag']not in ('option','a','dialog')
 add('ui_'+c['tag'],label,'SIMULATED'if seen else'UNVERIFIED',c['path'],c['line'],functional='VERIFIED_OFFLINE_FLOW'if seen else'SOURCE_PRESENT_NOT_INDIVIDUALLY_EXERCISED',tests='Specific locator in passing ordinary-click flow'if seen else'Source AST inventory only;individual behavior not claimed',evidence='evidence/advanced-research-validation.log; evidence/workspace-qualification.log'if seen else'evidence/ui-controls.json',action='Preserve tested behavior'if seen else'Exercise individual dynamic branch in final acceptance;rendering is not functional proof')
providers={'assets_refresh','market_history','directory_refresh','stock_events','stock_live_control','history_ingest','sec_directory','sec_history','stock_refresh','stock_load'}
for r in json.loads((e/'routes.json').read_text()):add('api_contract',r['method']+' '+r['route'],'DISCONNECTED'if r['handler']in providers else'SIMULATED',r['path'],r['line'],evidence='evidence/python-matrix.json; evidence/security.log',action='Provider paths fixture/gate-tested only;no network qualification'if r['handler']in providers else'Preserve typed/bounded contract;selected fixtures do not exhaust input states')
advanced=[('height','Height map'),('canyon','V-canyon'),('events','Event voxels/points'),('vwap','VWAP corridor'),('flow','Declared flow/VPIN'),('wheel','Depth wheel'),('dome','Volatility dome'),('ribbon','Spread ribbon')]
for mode,name in advanced:add('3d_model',name,'SIMULATED','terminal/web/src/research3d.ts',76,evidence='evidence/geometry-tests.log; evidence/advanced-research-validation.log')
for mode in ('quotes','comparison','volatility','trades'):add('3d_model','L1 '+mode,'SIMULATED','terminal/web/src/marketGeometry.ts',5,evidence='evidence/geometry-tests.log; evidence/advanced-research-validation.log')
for name,path in [('GARCH response surface','terminal/web/src/modelSurface.ts'),('Legacy native landscape','terminal/web/src/Landscape3D.tsx'),('Legacy theoretical volatility plane','terminal/web/src/VolatilitySurface.tsx')]:add('3d_model',name,'SIMULATED',path,evidence='evidence/legacy-3d.json; evidence/geometry-tests.log')
add('visual_encoding','Dome decorative cross-section','VISUAL_ONLY','terminal/web/src/research3d.ts',117,functional='INTENTIONAL_DECORATIVE_DIMENSION',evidence='THREED_MODEL_AUDIT.md',action='Keep explicit no-market-axis disclosure;variation dimension remains analytical')
quant=[('Exact L1 spread/mid/microprice/size imbalance','quote_analytics.py'),('Retained quote frequency/log variation/print totals','live_metrics.py'),('Black-Scholes/Greeks/bounded IV','options.py'),('HMM EM diagnostic fit','models.py'),('Finite-grid GARCH fit','models.py'),('Joseph scalar Kalman','models.py'),('Missing-emission fixed HMM','advanced_models.py'),('Conditional GARCH coordinate search','advanced_models.py'),('Training-only holdouts','evaluation.py'),('Bounded expanding folds','evaluation.py'),('Descriptive raw-close returns/drawdown','price_research.py'),('Historical/Gaussian loss risk','risk.py'),('Explicit portfolio covariance/tails/drawdown','portfolio.py'),('Linear single-asset scenarios','risk.py'),('Historical revision interval alignment','datasets.py'),('Causal toy five-return backtest','research.py'),('Fixed-parameter model demonstrations','research.py'),('Twelve SEC exact financial descriptors','financials.py'),('Retained acceptance-time financial filter','vintages.py'),('Selected statement tables','statements.py'),('Reported ratio histories','ratio_history.py'),('Accounting residual checks','accounting.py')]
for name,path in quant:add('quantitative_capability',name,'SIMULATED','terminal/stocks/'+path,evidence='evidence/independent-math.log; evidence/python-matrix.json',action='Numerical/contract scope only;no empirical predictive reliability inferred')
for name,path in [('Native OFI/signing/effective-realized spread','include/gig/analytics/flow_metrics.hpp'),('Exact supplied-depth HHI proposal','terminal/server/concentration.py')]:add('quantitative_capability',name,'SIMULATED',path,evidence='evidence/native-matrix.json; evidence/sprint1-release.log')
for name in ['Cointegration/statistical arbitrage','Cross-sectional factors','Portfolio optimizer','Euler risk decomposition','Survivorship-safe empirical backtest']:
 add('candidate_model_absence',name,'UNVERIFIED','terminal/stocks',functional='ABSENT_NOT_FAILED_CURRENT_MODEL',state='ABSENT',severity='Scope decision',action='Optional future specification;do not invent from menu/report references',evidence='QUANT_MODEL_INVENTORY.md')
native=[('Strong numeric/event validation','include/gig/events/contracts.hpp'),('FIFO L3 book','include/gig/book/order_book.hpp'),('Aggregate depth','include/gig/market_data/aggregate_depth.hpp'),('Replay sequences/recovery/journal','include/gig/replay/replay.hpp'),('Synthetic matching/latency/partial fills','include/gig/simulation/simulator.hpp'),('TWAP','include/gig/execution/execution.hpp'),('Ex-ante VWAP','include/gig/execution/execution.hpp'),('Causal POV','include/gig/execution/execution.hpp'),('Exact TCA','include/gig/execution/execution.hpp'),('Exports/verification/Python API','python/gig_microstructure'),('ITCH frame/context/L3/gzip','include/gig/itch'),('Initialization evidence/seed contracts','include/gig/itch/seed.hpp'),('LOBSTER CSV ingestion/comparison','include/gig/lobster/adapter.hpp')]
for name,path in native:add('native_capability',name,'SIMULATED',path,evidence='evidence/native-matrix.json; evidence/wheel-interface.log; evidence/wheel-exports.log',action='Preserve deterministic identity;no exchange equivalence or observed L3 claim')
for name,path in [('SEC facts/submissions','terminal/stocks/sec.py'),('Alpaca REST/history','terminal/stocks/alpaca_history.py'),('Alpaca MessagePack IEX','terminal/stocks/live.py'),('Indicative options','terminal/stocks/option_feed.py'),('Kraken depth','terminal/providers/kraken.py'),('Coinbase candidate','terminal/providers/coinbase_candidate.py'),('NASDAQ listings parsers','terminal/stocks/directory.py')]:add('source_adapter',name,'DISCONNECTED',path,evidence='evidence/python-matrix.json',action='No external calls;permissions and source qualification still required')
for name,path in [('Curated13-symbol catalog','terminal/stocks/market_catalog.py'),('Public schemas','schemas')]:add('static_reference',name,'REAL_STATIC_REFERENCE',path,action='Static artifact only;not fresh complete exchange reference')
for name in ['Paper-only account verification','Paper/live order separation','Paper-order authorization','Pre-trade validation','Max order notional','Max position exposure','Daily loss limit','Idempotent client order IDs','Duplicate order prevention','Trading kill switch','Cancel-all orders','Order-state reconciliation','Position/buying-power reconciliation','Partial/rejected broker fills','Broker reconnect recovery','Durable intent restart','Execution audit trail','Paper provider routing']:
 add('paper_execution_absence',name,'UNVERIFIED','terminal/stocks/alpaca_transport.py',functional='ABSENT_FOR_BROKER_EXECUTION',state='ABSENT',severity='P1 readiness gap (grouped S3-PAPER)',action='Approved future paper-only design/negative tests before activation;no orders now',evidence='evidence/independent-math.log; ALPACA_PAPER_TRADING_READINESS.md')
for name,path in [('Observation suffix persistence','terminal/stocks/observation_store.py'),('History/backup/restore','terminal/stocks/history_backup.py'),('Bounded SSE/reconnect','terminal/server/market_events.py'),('Origin/Host/one-use proofs','terminal/server/connection.py'),('SEC evidence binding','terminal/verification/sec_binding.py'),('Source/runtime receipts','terminal/verification/deployment.py')]:add('reliability_security_tool',name,'SIMULATED',path,evidence='evidence/python-matrix.json; evidence/security.log; SECURITY_AND_DEPLOYMENT.md')
add('qualification_tool','Committed stock browser stale option summary assertion','BROKEN','terminal/tests/stock-intelligence-validation.mjs',15,functional='REPRODUCED_FAILURE',severity='P2 (S3-TEST)',action='Next sprint assert formatted display plus raw/full-precision numeric reference;do not change pricing',evidence='evidence/stock-intelligence-validation.log')
add('owner_observation','Owner SEC10429 identities/1772 selected matches','UNVERIFIED','docs/remediation/sprint-2/SEC_EVIDENCE_BINDING.md',functional='OWNER_REPORTED_NOT_INDEPENDENTLY_REVALIDATED',action='Bind existing original report/hash/tested SHA/time;no new fetch',evidence='SEC_AND_HISTORICAL_DATA_AUDIT.md')
add('api_client','Generic response body budget at read boundary','BROKEN','terminal/web/src/api.ts',2,functional='REPRODUCED_FAILURE',severity='P2 (S3-BUDGET)',action='Use bounded incremental read/cancel before accumulating full body;preserve safe errors and existing contracts',evidence='evidence/response-budget.json')
for r in rows:assert(root/r['source_path']).exists(),r['source_path']
with(dest/'FEATURE_INVENTORY.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'audited_sha':'5c9c9c6e38bf027c8ed731caa9e5c241cd25a4d9','inventory_rows':len(rows),'primary_classifications':dict(Counter(r['primary_classification']for r in rows)),'verified_offline_functional_rows':sum(r['functional_status'].startswith('VERIFIED_OFFLINE')for r in rows),'provider_verified_functional_rows':0,'inventory_unit':'Source-declared UI/options and route-method contracts plus capabilities;not deduplicated user journeys or universal historical requirement count','static_JSX_declarations':306,'route_method_contracts':51,'workspaces':12,'3d_modes_including_legacy':15}
(e/'inventory-counts.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

```

## validate.py

SHA256 `4f808d7d88f0f34e313038f9fbd46ac030afb80438bd6fdec7e11fd08b870a1b`

```python
import json,os,subprocess,time
from pathlib import Path
root=Path('/workspace/GIG-C-Microstructure-Engine');work=root/'build/functional-reality-audit/worktree';out=root/'build/functional-reality-audit/evidence';rows=[]
cohorts=[('sprint2','terminal/tests/run_remediation_sprint2.py',30),('sprint1','terminal/tests/run_remediation_sprint1.py',25),('sources','terminal/tests/run_source_qualification_suite.py',142),('stocks','terminal/tests/run_live_market_suite.py',207),('terminal','terminal/tests/run_native_suite.py',274)]
for config in ('debug','release','asan-ubsan'):
 env=dict(os.environ);native=root/('build/python-'+config);env['PYTHONPATH']=str(root/'build/functional-reality-audit/offline-guard')+':'+str(native/'python')+':'+str(work);env['GIG_TERMINAL_NATIVE_BUILD']=str(native)
 for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):env[k]='0'
 if config=='asan-ubsan':env.update(LD_PRELOAD='/usr/lib/gcc/x86_64-linux-gnu/14/libasan.so:/usr/lib/gcc/x86_64-linux-gnu/14/libstdc++.so',PYTHONMALLOC='malloc',ASAN_OPTIONS='detect_leaks=1:leak_check_at_exit=0:halt_on_error=1')
 for name,script,count in cohorts:
  cmd=['/workspace/gig-terminal-clean-venv/bin/python']
  if config=='asan-ubsan':cmd+=['scripts/run_python_sanitized.py']
  cmd+=[script]
  if name=='terminal':cmd+=['--expected-tests','274']
  start=time.monotonic();log=out/(name+'-'+config+'.log')
  with log.open('w') as f:r=subprocess.run(cmd,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=240)
  raw=log.read_text();success=r.returncode==0 and ('Ran '+str(count)+' tests') in raw and ('LIVE_LSAN_CHECK=0' in raw if config=='asan-ubsan' else True)
  rows.append(dict(configuration=config,cohort=name,expected=count,exit_code=r.returncode,verified_pass=success,seconds=time.monotonic()-start,log=log.name,command=cmd))
  (out/'python-matrix.json').write_text(json.dumps(rows,indent=2)+'\n');print(config,name,success,round(time.monotonic()-start,3),flush=True)
  if not success:raise SystemExit(1)

```

## run_native.py

SHA256 `37ff1ecb55eca27f5243c96f66eeadb0961625c36001b8b08c8bad69d28319fb`

```python
import concurrent.futures,json,os,subprocess,time,xml.etree.ElementTree as ET
from pathlib import Path
root=Path('/workspace/GIG-C-Microstructure-Engine');out=root/'build/functional-reality-audit/evidence'
prior=json.loads((root/'docs/overnight/overnight_evidence.json').read_text());expected=json.loads((root/'build/overnight/canonical-comparison.json').read_text())['expected']
# No native/binding/build source changed;exercise existing exact-source builds.
work=root/'build/functional-reality-audit/worktree'
assert not subprocess.check_output(['git','diff','--name-only','10eaee3','--','include','src','python','CMakeLists.txt','CMakePresets.json','cmake','tests'],cwd=work)
def run(row):
 name=row['name'];log=out/(name+'.log');xml=out/(name+'.xml');cmd=['/workspace/gig-tools/bin/ctest','--test-dir',str(root/row['directory']),'--output-on-failure','-j','2','--output-junit',str(xml)]
 env=dict(os.environ)
 for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED'):env[k]='0'
 start=time.monotonic()
 with log.open('w')as f:r=subprocess.run(cmd,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=420)
 x=ET.parse(xml).getroot();counts={k:int(x.get(k,0)) for k in ('tests','failures','skipped','disabled')}
 assert r.returncode==0 and counts['tests']==row['tests']and not any(counts[k]for k in ('failures','skipped','disabled')),(name,r.returncode,counts)
 cases={c.get('name'):''.join(c.itertext())for c in x.findall('testcase')}
 assert all(v in cases[k]for k,v in expected.items())
 result={'configuration':name,'build_directory':row['directory'],'command':cmd,'counts':counts,'frozen_hashes_unchanged':8,'seconds':time.monotonic()-start,'log':str(log.relative_to(root)),'scope':'Rerun on unchanged native-source build;not a fresh compile of modified terminal Python/TS'}
 print(name,'PASS',counts,flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:rows=list(pool.map(run,prior['native_six']))
(out/'native-matrix.json').write_text(json.dumps({'results':rows,'expected_hashes':expected,'all_48_unchanged':True},indent=2)+'\n')

```

## local_receipt.py

SHA256 `49aba1ea57a2047847ca3393f4834e3df858fc9102dbd6756699a1d248e6e716`

```python
from pathlib import Path
import os,subprocess,socket,time,json,urllib.request
work=Path('/workspace/GIG-C-Microstructure-Engine/build/functional-reality-audit/worktree');out=work.parent/'evidence';sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip()
with socket.socket()as guard:guard.bind(('127.0.0.1',8787))
env=dict(os.environ);env['PYTHONPATH']=str(work.parent/'offline-guard')+':/workspace/GIG-C-Microstructure-Engine/build/python-release/python:'+str(work)
for k in ('GIG_SEC_ENABLED','GIG_ALPACA_ENABLED','GIG_LIVE_ENABLED','GIG_COINBASE_ENABLED','GIG_ALPACA_STORE_ENABLED','GIG_HISTORY_STORE_ENABLED'):env[k]='0'
for k in ('CODESPACES','CODESPACE_NAME','GIG_TERMINAL_ALLOWED_ORIGINS'):env.pop(k,None)
code="from terminal.server.app import create_app;from terminal.stocks.service import StockWorkspace;import uvicorn;uvicorn.run(create_app(stock_workspace=StockWorkspace(environment={})),host='127.0.0.1',port=8787,proxy_headers=False)"
with(out/'local-receipt-server.log').open('w')as log:
 server=subprocess.Popen(['/workspace/gig-terminal-clean-venv/bin/python','-c',code],cwd=work,env=env,stdout=log,stderr=subprocess.STDOUT)
 try:
  for _ in range(50):
   if server.poll()is not None:raise AssertionError('owned fixture exited')
   try:
    with urllib.request.urlopen('http://127.0.0.1:8787/api/v1/health',timeout=1)as response:assert json.load(response)['fixture_tests_safe']is True
    break
   except OSError:time.sleep(.1)
  else:raise AssertionError('owned fixture not ready')
  command=['/workspace/gig-terminal-clean-venv/bin/python','scripts/qualify_private_deployment.py','--expected-sha',sha,'--check-local-server','--output',str(out/'runtime-local.json')]
  result=subprocess.run(command,cwd=work,env=env,capture_output=True,text=True,timeout=15);(out/'runtime-local.log').write_text(result.stdout+result.stderr)
  value=json.loads(result.stdout);assert result.returncode==0 and value['local_server']['status']=='MATCH';print('PASS local startup receipt,0external requests;not private Codespaces authentication')
 finally:
  server.terminate()
  try:server.wait(timeout=8)
  except subprocess.TimeoutExpired:server.kill();server.wait()

```

## offline-guard/sitecustomize.py

SHA256 `7778961555bfd540373287fc2de788b08cbbabc3590ec28fa753e93748a20e88`

```python
# Audit-only provider/network fail-closed harness,not application code.
import socket
_original=socket.socket.connect
_original_ex=socket.socket.connect_ex
def permitted(address):
 if isinstance(address,str):return True # local Unix domain socket
 return isinstance(address,tuple)and address[0]in ('127.0.0.1','::1','localhost')
def connect(self,address):
 if not permitted(address):raise AssertionError('AUDIT_EXTERNAL_NETWORK_FORBIDDEN')
 return _original(self,address)
def connect_ex(self,address):
 if not permitted(address):raise AssertionError('AUDIT_EXTERNAL_NETWORK_FORBIDDEN')
 return _original_ex(self,address)
socket.socket.connect=connect;socket.socket.connect_ex=connect_ex

```
