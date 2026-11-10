/** Actual native-backed GIG workstation,ordinary browser interactions,authored inputs only. */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {assertFixtureServer} from './fixture-safety.mjs';
const base='http://127.0.0.1:8787',out=(process.env.GIG_SPRINT3_EVIDENCE||'build/gig-redesign-next/visual')+'/workstation';fs.mkdirSync(out,{recursive:true});
const names=['Command Center','Securities Universe','Stock Intelligence','Live Markets','Multi-Stock Comparison','Order Book','Market Depth','Order Flow','Historical Replay','Execution Simulator','Research & Validation','Operations'];
const checks=[],combinations=[],screenshots=[],errors=[];let failure,page,overviewMetrics;
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const check=async(name,fn)=>{await fn();checks.push(name);console.log('PASS '+name)};
const shot=async name=>{const path=out+'/'+name+'.png';await page.screenshot({path});screenshots.push({path,sha256:crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex'),classification:'AUTHORED_NATIVE_FIXTURE_NOT_REAL_PROVIDER'})};
try{
 page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'no-preference'});page.on('pageerror',e=>errors.push(e.message));await assertFixtureServer(page,base);await page.goto(base);await page.getByTestId('connection-status').filter({hasText:'CONNECTED'}).waitFor();
 const go=async name=>{await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button',{name,exact:true}).click();await page.getByRole('heading',{level:1,name:name+'.',exact:true}).waitFor();await page.waitForFunction(()=>![...document.querySelectorAll('.workspace-stage [role="status"],.workspace-stage .loading-panel')].some(e=>e.getBoundingClientRect().height&&/^Loading (company research workspace|market workspace|security master|research desk|equity health|mathematical research surface)/.test(e.textContent.trim())));if(name==='Stock Intelligence')await page.getByRole('heading',{name:'AAPL · Apple Inc.',exact:true}).waitFor()};
 await check('native GIG shell,keyboard search and source boundaries',async()=>{
  assert.match(await page.title(),/^GIG \|/);assert.equal(await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button').count(),12);
  await page.keyboard.press('Control+k');assert.equal(await page.getByRole('textbox',{name:'Global company search'}).evaluate(e=>e===document.activeElement),true);
  await page.getByRole('textbox',{name:'Global company search'}).fill('NVDA');await page.getByRole('button',{name:'Search companies',exact:true}).click();await page.getByRole('region',{name:'Company search results'}).getByRole('button',{name:/NVDA/}).click();await page.getByRole('heading',{name:/NVDA ·/}).waitFor();
  await page.getByRole('textbox',{name:'Global company search'}).fill('AAPL');await page.getByRole('button',{name:'Search companies',exact:true}).click();await page.getByRole('region',{name:'Company search results'}).getByRole('button',{name:/AAPL/}).click();await page.getByRole('heading',{name:'AAPL · Apple Inc.',exact:true}).waitFor();
  assert.equal(await page.getByTestId('origin-label').count(),0);assert.equal((await(await page.request.get(base+'/api/v1/state')).json()).engine.native,true);
 });
 await check('company financial summary precedes secondary acquisition workflows',async()=>{
  await go('Stock Intelligence');await page.locator('.page-content').evaluate(e=>{e.scrollTop=0});
  const heading=page.getByRole('heading',{name:'Financial snapshot',exact:true});const box=await heading.boundingBox();assert.ok(box&&box.y<850,`Financial heading must enter the initial900px viewport,got ${box?.y}`);
  assert.equal(await page.locator('.company-history-tools').getAttribute('open'),null);
  overviewMetrics=await page.evaluate(()=>{const pane=document.querySelector('.page-content'),heading=[...document.querySelectorAll('h2')].find(e=>e.textContent==='Financial snapshot');return{viewport:[innerWidth,innerHeight],paneHeight:pane.clientHeight,scrollHeight:pane.scrollHeight,financialHeadingY:heading.getBoundingClientRect().top,firstFactY:document.querySelector('.atlas-fact-card strong')?.getBoundingClientRect().top,firstFactBottom:document.querySelector('.atlas-fact-card strong')?.getBoundingClientRect().bottom}});
  assert.ok(overviewMetrics.firstFactBottom<=900,`First financial value must be fully visible,got bottom ${overviewMetrics.firstFactBottom}`);
  const feed=await(await page.request.get(base+'/api/v1/stocks/live')).json();assert.equal(feed.connection_count,0);
 });
 await check('historical and source tools stay reachable through explicit disclosure',async()=>{
  await page.getByText('Historical prices & research datasets',{exact:true}).click();await page.getByRole('heading',{name:'Historical price inputs',exact:true}).waitFor();await page.getByText('Private historical snapshot archive',{exact:true}).waitFor();
  await page.getByText('Historical prices & research datasets',{exact:true}).click();await page.getByText('Provider setup and data availability · configuration is not validation',{exact:true}).click();await page.getByText(/01 \/ Identity evidence/).waitFor();
  const financial=page.getByRole('region',{name:'Reported financial research',exact:true});await financial.getByText('Reported-period rules and limitations',{exact:true}).click();await financial.getByText(/No cumulative-to-quarter subtraction/).waitFor();await financial.getByText('Reported-period rules and limitations',{exact:true}).click();
  const feed=await(await page.request.get(base+'/api/v1/stocks/live')).json();assert.equal(feed.connection_count,0);await page.getByText('Provider setup and data availability · configuration is not validation',{exact:true}).click();
 });
 await check('all12 compositions in both themes and all five target viewports',async()=>{
  for(const theme of ['dark','light']){
   if(await page.locator('html').getAttribute('data-theme')!==theme)await page.getByRole('button',{name:'Toggle color theme',exact:true}).click();
   for(const [width,height]of [[1366,768],[1440,900],[1920,1080],[390,844],[360,800]]){
    await page.setViewportSize({width,height});
    for(const name of names){await go(name);const result=await page.evaluate(()=>{
     const root=document.querySelector('.page-content'),r=root.getBoundingClientRect();const overflow=[];
     for(const e of document.querySelectorAll('.workspace-stage button,.workspace-stage input,.workspace-stage select')){
      const b=e.getBoundingClientRect();if(!b.width||!b.height||b.bottom<r.top||b.top>r.bottom||getComputedStyle(e).visibility==='hidden')continue;
      if(e.closest('.atlas-table-scroll,.company-research-tabs,.ladder-scroll'))continue;
      // Internal designated scroll areas may reveal their items by ordinary scrolling.
      if(b.left<r.left-1||b.right>r.right+1)overflow.push((e.getAttribute('aria-label')||e.textContent).slice(0,80));
     }
     return{pageOverflow:document.documentElement.scrollWidth>innerWidth+1,font:parseFloat(getComputedStyle(document.body).fontSize),overflow,layout:document.querySelector('.workspace-stage').className};
    });assert.equal(result.pageOverflow,false,`${theme}/${width}/${name}`);assert.equal(result.font,16);assert.deepEqual(result.overflow,[],`${theme}/${width}/${name}`);assert.doesNotMatch(await page.locator('body').innerText(),/GIG ATLAS|GIG Research Terminal|GIG Quant Terminal/);combinations.push({theme,width,height,workspace:name,layout:result.layout});
     if(width===1440&&theme==='dark'||width===390&&['Command Center','Stock Intelligence','Market Depth'].includes(name)||width===1440&&theme==='light'&&['Stock Intelligence','Live Markets','Operations'].includes(name))await shot(name.replaceAll(/[^a-z0-9]+/gi,'-').toLowerCase()+'-'+theme+'-'+width);
    }
   }
  }
 });
 await page.setViewportSize({width:1440,height:900});if(await page.locator('html').getAttribute('data-theme')!=='dark')await page.getByRole('button',{name:'Toggle color theme',exact:true}).click();
 await check('native ladder columns cannot overlap at the desktop target widths',async()=>{
  for(const [width,height]of [[1366,768],[1440,900],[1920,1080]]){await page.setViewportSize({width,height});for(const name of ['Order Book','Market Depth']){
   await go(name);const book=page.getByRole('region',{name:'Displayed order book',exact:true});const rows=await book.locator('tbody tr').evaluateAll(list=>list.map(row=>({display:getComputedStyle(row).display,cells:[...row.children].map(c=>{const r=c.getBoundingClientRect();return{left:r.left,right:r.right,width:r.width}})})));
   assert.equal(rows.length,name==='Order Book'?20:10);for(const row of rows){assert.equal(row.display,'table-row');assert.equal(row.cells.length,3);for(let i=0;i<3;i++){assert.ok(row.cells[i].width>=24);if(i)assert.ok(row.cells[i-1].right<=row.cells[i].left+1,`${name}/${width}:overlapping columns`)}}
  }}await page.setViewportSize({width:1440,height:900});
 });
 await check('research and simulation views reveal existing tools without conflating broker execution',async()=>{
  await go('Execution Simulator');await page.getByRole('button',{name:'Offline paper sandbox',exact:true}).click();await page.getByRole('region',{name:'Paper execution infrastructure',exact:true}).waitFor();await page.getByRole('button',{name:'Disabled paper boundary',exact:true}).click();await page.getByRole('heading',{name:'Alpaca paper provider boundary',exact:true}).waitFor();await page.getByRole('button',{name:'Native simulator',exact:true}).click();await page.getByLabel('Simulation quantity',{exact:true}).waitFor();
  await go('Research & Validation');await page.getByRole('button',{name:'Validation & evidence',exact:true}).click();await page.getByRole('button',{name:'Validate authored ITCH',exact:true}).waitFor();await page.getByRole('button',{name:'3D laboratory',exact:true}).click();await page.getByRole('button',{name:'Open advanced research',exact:true}).waitFor();await page.getByRole('button',{name:'Model scenarios',exact:true}).click();await page.getByRole('region',{name:'Research surface explorer',exact:true}).waitFor();
 });
 await check('native3D visibly orbits,manual pause/reset and reduced motion are accurately explained',async()=>{
  await go('Market Depth');await page.getByRole('button',{name:'Enable 3D landscape',exact:true}).click();const scene=page.getByRole('region',{name:'Liquidity landscape',exact:true}),canvas=scene.getByTestId('liquidity-canvas');await canvas.waitFor();await canvas.scrollIntoViewIfNeeded();
  await page.waitForFunction(()=>document.querySelector('[data-testid="liquidity-canvas"]')?.dataset.motionState==='orbiting');await scene.getByText('Automatic orbit · camera only',{exact:true}).waitFor();const before=await canvas.getAttribute('data-camera');await page.waitForTimeout(800);assert.notEqual(await canvas.getAttribute('data-camera'),before);const box=await canvas.boundingBox();assert.ok(box.height>=440);
  await scene.getByRole('button',{name:'Pause automatic orbit',exact:true}).click();await scene.getByText('Camera paused · drag to inspect',{exact:true}).waitFor();await page.waitForTimeout(100);const paused=await canvas.getAttribute('data-camera');await page.waitForTimeout(250);assert.equal(await canvas.getAttribute('data-camera'),paused);await scene.getByRole('button',{name:'Reset camera',exact:true}).click();await scene.getByRole('button',{name:'Resume automatic orbit',exact:true}).click();await page.emulateMedia({reducedMotion:'reduce'});await scene.getByText('Reduced motion · drag to inspect',{exact:true}).waitFor();assert.equal(await scene.getByRole('button',{name:'Automatic orbit off · reduced motion',exact:true}).isDisabled(),true);await shot('native-camera-dark');
  const handle=await canvas.elementHandle();await go('Command Center');assert.equal(await handle.evaluate(e=>e.dataset.motionState),'disposed');assert.equal(await handle.evaluate(e=>e.isConnected),false);
 });
 await check('no browser runtime errors',async()=>assert.deepEqual(errors,[]));
}catch(e){failure=String(e.stack||e);if(page){await shot('failure');fs.writeFileSync(out+'/failure-text.txt',await page.locator('body').innerText())}}
finally{await browser.close();fs.writeFileSync(out+'/results.json',JSON.stringify({schema:'gig.workstation.redesign.v1',passed:checks.length,failed:failure?1:0,skipped:0,checks,combinations,screenshots,errors,failure,overviewMetrics,scope:'Local native C++ plus authored fixtures;ordinary clicks,no provider calls,no real GPU/device/private owner edge qualification'},null,2));if(failure)console.error(failure)}
if(failure)process.exit(1);
