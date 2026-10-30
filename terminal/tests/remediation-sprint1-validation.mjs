import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {assertFixtureServer} from './fixture-safety.mjs';
const base='http://127.0.0.1:18793',out='build/remediation-sprint1-browser';
await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const checks=[],images=[],errors=[];
try{
 const p=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
 p.on('pageerror',e=>errors.push(String(e)));
 await assertFixtureServer(p,base);await p.goto(base);
 await p.getByTestId('connection-status').filter({hasText:'CONNECTED'}).waitFor();
 const navigation=p.getByRole('navigation',{name:'Research sections',exact:true});
 await navigation.getByRole('button',{name:'Order Book',exact:true}).click();
 for(let i=0;i<3;i++)await p.getByRole('button',{name:'Step replay',exact:true}).click();
 const panel=p.getByRole('region',{name:'Proposed supplied-depth concentration',exact:true});
 await panel.getByTestId('concentration-result').waitFor();
 const source=await(await p.request.get(base+'/api/v2/research/concentration')).json();
 assert.equal(source.contract_status,'PROPOSED_RESEARCH_NOT_ORIGINAL_REQUIREMENT_ACCEPTANCE');
 assert.equal(source.source.origin,'HISTORICAL_SYNTHETIC');checks.push('Native-backed readonly research metric retains source and proposal status');
 for(const width of [390,1280]){
  await p.setViewportSize({width,height:900});
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  await panel.getByText('Exact concentration,formula scope and source lineage',{exact:true}).click();
  assert.ok((await panel.innerText()).includes(source.hhi.numerator));
  await panel.getByText('Exact concentration,formula scope and source lineage',{exact:true}).click();
  const path=`${out}/concentration-authored-${width}.png`;await p.screenshot({path,fullPage:true});images.push(path);
  checks.push(`Concentration ordinary-click details and contained layout at${width}px`);
 }
 await navigation.getByRole('button',{name:'Stock Intelligence',exact:true}).click();
 await p.getByRole('heading',{name:'AAPL · Apple Inc.',exact:true}).waitFor();
 await p.getByRole('navigation',{name:'Stock research sections',exact:true}).getByRole('button',{name:'Options',exact:true}).click();
 for(const value of ['0.000001','10000000','100']){
  await p.getByLabel('Scenario spot',{exact:true}).fill(value);await p.getByLabel('Scenario strike',{exact:true}).fill(value);
  const response=p.waitForResponse(r=>r.url().endsWith('/api/v1/stocks/options')&&r.request().method()==='POST');
  await p.getByRole('button',{name:'Calculate theoretical options',exact:true}).click();
  const r=await response;assert.equal(r.status(),200);const data=await r.json();
  await p.getByTestId('option-price').waitFor();
  assert.equal(data.surface_coverage.total,153);
  assert.equal(data.surface_coverage.unavailable>0,value!=='100');
  await p.getByText(/Priced auxiliary grid:/).waitFor();
  checks.push(`Options boundary${value}:valid base metrics,explicit auxiliary coverage`);
 }
 await p.screenshot({path:`${out}/options-authored.png`,fullPage:true});images.push(`${out}/options-authored.png`);
 assert.deepEqual(errors,[]);
 const result={schema:'gig.remediation.browser.v1',origin:'AUTHORED_FIXTURES_NOT_PROVIDER_ACCEPTANCE',passed:checks.length,failed:0,skipped:0,checks,images,browser:browser.version(),device:'Emulated viewports;not physical Android or current Codespaces'};
 await writeFile(`${out}/results.json`,JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}finally{await browser.close()}
