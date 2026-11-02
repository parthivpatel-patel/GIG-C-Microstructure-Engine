/** Actual native/fixture UI,ordinary clicks. Camera motion changes no observations. */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {assertFixtureServer} from './fixture-safety.mjs';
const base='http://127.0.0.1:8787',out=process.env.GIG_SPRINT3_EVIDENCE;
fs.mkdirSync(out,{recursive:true});
const checks=[],screenshots=[],errors=[],frames=[];let page,failure;
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const check=async(name,fn)=>{await fn();checks.push(name);console.log('PASS '+name)};
try{
 page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'no-preference'});page.setDefaultTimeout(15000);page.on('pageerror',e=>errors.push(e.message));
 await assertFixtureServer(page,base);await page.goto(base);await page.getByTestId('connection-status').filter({hasText:'CONNECTED'}).waitFor();
 const go=async(name)=>{await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button',{name,exact:true}).click();await page.getByRole('heading',{level:1,name:name+'.',exact:true}).waitFor();await page.waitForFunction(()=>![...document.querySelectorAll('.page-content [role="status"],.page-content .loading-panel')].some(el=>el.getBoundingClientRect().height&&/^Loading (company research workspace|market workspace|security master|research desk|equity health|mathematical research surface|offline paper sandbox|disabled paper-provider boundary)/.test(el.textContent.trim())));if(name==='Stock Intelligence')await page.getByRole('heading',{name:'AAPL · Apple Inc.',exact:true}).waitFor()};
 const shot=async(name,target)=>{const path=out+'/gig-'+name+'.png';if(target)await target.screenshot({path});else await page.screenshot({path,fullPage:false});screenshots.push({path,sha256:crypto.createHash('sha256').update(fs.readFileSync(path)).digest('hex'),classification:'AUTHORED_NATIVE_OR_FIXTURE_NOT_OBSERVED_MARKET'})};
 await check('GIG identity,system typography,accessible12-workspace navigation and real native transport',async()=>{
  assert.match(await page.title(),/^GIG \| Order Book/);assert.doesNotMatch(await page.locator('body').innerText(),/\bATLAS\b/);
  await page.getByRole('link',{name:'GIG Order Book & Market Microstructure Terminal',exact:true}).waitFor();
  assert.equal(await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button').count(),12);
  await page.keyboard.press('Tab');assert.ok(await page.getByRole('link',{name:'Skip to workspace',exact:true}).evaluate(el=>el.matches(':focus-visible')));await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'workspace-main');
  const styles=await page.evaluate(()=>({font:getComputedStyle(document.body).fontFamily,size:parseFloat(getComputedStyle(document.body).fontSize)}));assert.match(styles.font,/-apple-system/);assert.doesNotMatch(styles.font,/Inter/);assert.ok(styles.size>=14);
  await page.getByRole('button',{name:'Toggle color theme',exact:true}).focus();await page.keyboard.press('Space');assert.equal(await page.locator('html').getAttribute('data-theme'),'light');await page.keyboard.press('Space');await page.getByRole('button',{name:'Toggle workspace navigation',exact:true}).click();await page.waitForFunction(()=>document.querySelector('.atlas-nav-collapsed'));assert.equal(await page.locator('.brand>span:last-child').evaluate(el=>getComputedStyle(el).display),'none');assert.ok(await page.locator('.sidebar').evaluate(el=>el.getBoundingClientRect().width)<100);await page.getByRole('button',{name:'Toggle workspace navigation',exact:true}).click();await page.waitForFunction(()=>!document.querySelector('.atlas-nav-collapsed'));await shot('command-center-dark');
 });
 await go('Historical Replay');
 const replayAction=async(name)=>{const done=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/control'&&r.request().method()==='POST');await page.getByRole('button',{name,exact:true}).click();assert.equal((await done).status(),200);await page.waitForFunction(()=>!document.querySelector('button[aria-label="Step replay"]').disabled)};
 await replayAction('Restart replay');for(let i=0;i<16;i++)await replayAction('Step replay');
 const before=await(await page.request.get(base+'/api/v1/state')).json();assert.equal(before.origin,'HISTORICAL_SYNTHETIC');
 await check('two-sided exact native ladders expose size,cumulative quantity and source units',async()=>{
  await go('Order Book');const book=page.getByRole('region',{name:'Displayed order book',exact:true});await book.getByRole('table').first().waitFor();assert.equal(await book.getByRole('table').count(),2);assert.equal(await book.getByRole('columnheader',{name:'Cumulative',exact:true}).count(),2);
  assert.equal(await book.locator('.book-row.bid').count(),Math.min(40,before.book.bids.length));assert.equal(await book.locator('.book-row.ask').count(),Math.min(40,before.book.asks.length));
  const expected=before.book.bids.reduce((sum,r)=>sum+BigInt(r.quantity),0n);assert.ok(expected>0n);await book.getByText(/HISTORICAL_SYNTHETIC/).waitFor();await shot('order-book-dark');await shot('order-book-detail-dark',book);
 });
 await go('Market Depth');const landscape=page.getByRole('region',{name:'Liquidity landscape',exact:true}),canvas=landscape.getByTestId('liquidity-canvas');await landscape.getByRole('button',{name:'Enable 3D landscape',exact:true}).click();await canvas.waitFor();await canvas.scrollIntoViewIfNeeded();
 const motionReady=async(c)=>{const prior=Number(await c.getAttribute('data-motion-frames')||0);await page.waitForFunction(({el,prior})=>Number(el.dataset.motionFrames)>prior+2,{el:await c.elementHandle(),prior})};
 await check('native static-data camera automatically orbits only when visible',async()=>{
  await motionReady(canvas);const pose=await canvas.getAttribute('data-camera'),n=Number(await canvas.getAttribute('data-motion-frames'));await page.waitForTimeout(800);assert.notEqual(await canvas.getAttribute('data-camera'),pose);const delta=Number(await canvas.getAttribute('data-motion-frames'))-n;assert.ok(delta>0&&delta<=30);frames.push({scene:'native',interval_ms:800,frames:delta});
 });
 await check('accessible pause/resume and manual reset preserve independent camera control',async()=>{
  await landscape.getByRole('button',{name:'Pause automatic orbit',exact:true}).click();await page.waitForTimeout(120);const pose=await canvas.getAttribute('data-camera');await page.waitForTimeout(300);assert.equal(await canvas.getAttribute('data-camera'),pose);await landscape.getByRole('button',{name:'Reset camera',exact:true}).click();assert.notEqual(await canvas.getAttribute('data-camera'),pose);await landscape.getByRole('button',{name:'Resume automatic orbit',exact:true}).click();await motionReady(canvas);
 });
 await check('actual offscreen intersection suspends the loop and returning resumes it',async()=>{
  await page.getByRole('button',{name:'Open advanced research',exact:true}).click();await page.getByTestId('advanced-research-canvas').waitFor();await page.locator('.page-footer').scrollIntoViewIfNeeded();await page.waitForFunction(el=>el.dataset.motionState==='offscreen',await canvas.elementHandle());const n=await canvas.getAttribute('data-motion-frames');await page.waitForTimeout(300);assert.equal(await canvas.getAttribute('data-motion-frames'),n);await canvas.scrollIntoViewIfNeeded();await page.waitForFunction(el=>el.dataset.motionState==='orbiting',await canvas.elementHandle());
 });
 await check('visibility event suspension and browser reduced-motion preference stop camera work',async()=>{
  await page.evaluate(()=>{Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'hidden'});document.dispatchEvent(new Event('visibilitychange'))});const n=await canvas.getAttribute('data-motion-frames');await page.waitForTimeout(250);assert.equal(await canvas.getAttribute('data-motion-frames'),n);
  await page.evaluate(()=>{delete document.visibilityState;document.dispatchEvent(new Event('visibilitychange'))});await page.emulateMedia({reducedMotion:'reduce'});await landscape.getByRole('button',{name:'Automatic orbit off · reduced motion',exact:true}).waitFor();assert.ok(await landscape.getByRole('button',{name:'Automatic orbit off · reduced motion',exact:true}).isDisabled());const reduced=await canvas.getAttribute('data-motion-frames');await page.waitForTimeout(250);assert.equal(await canvas.getAttribute('data-motion-frames'),reduced);await page.emulateMedia({reducedMotion:'no-preference'});
 });
 const lab=page.getByRole('region',{name:'Advanced 3D research laboratory',exact:true});if(await lab.getByRole('button',{name:'Open advanced research',exact:true}).count())await lab.getByRole('button',{name:'Open advanced research',exact:true}).click();await lab.getByLabel('Research source',{exact:true}).selectOption('authored-research-v1');const advanced=lab.getByTestId('advanced-research-canvas');await advanced.waitFor();await advanced.scrollIntoViewIfNeeded();
 await check('multicolor authored research geometry rotates without changing native book or replay',async()=>{
  await motionReady(advanced);assert.ok(Number(await advanced.getAttribute('data-samples'))>0);assert.ok(Number(await advanced.getAttribute('data-draw-calls'))<=9);await lab.getByRole('button',{name:'Pause automatic orbit',exact:true}).click();await shot('research-3d-dark');assert.deepEqual((await(await page.request.get(base+'/api/v1/state')).json()).book,before.book);assert.equal((await(await page.request.get(base+'/api/v1/state')).json()).position,before.position);
 });
 await check('context loss retains2D table and retry creates a usable independent renderer',async()=>{
  const old=await advanced.elementHandle();await advanced.evaluate(c=>c.getContext('webgl2').getExtension('WEBGL_lose_context').loseContext());await lab.getByRole('button',{name:'Retry research WebGL',exact:true}).waitFor();assert.equal(await old.evaluate(c=>c.isConnected),false);await lab.getByRole('button',{name:'Retry research WebGL',exact:true}).click();await advanced.waitFor();await advanced.scrollIntoViewIfNeeded();await page.waitForFunction(el=>el.dataset.motionState==='paused',await advanced.elementHandle());await lab.getByRole('button',{name:'Resume automatic orbit',exact:true}).click();await motionReady(advanced);
 });
 await check('navigation disposes removed renderer loops and canvases',async()=>{const old=await advanced.elementHandle();await go('Command Center');assert.equal(await old.evaluate(c=>c.isConnected),false);assert.equal(await old.evaluate(c=>c.dataset.motionState),'disposed');assert.equal(await page.locator('canvas').count(),0)});
 await check('all12workspace pages remain accessible in both themes at1440and390px',async()=>{
  const names=['Command Center','Securities Universe','Stock Intelligence','Live Markets','Multi-Stock Comparison','Order Book','Market Depth','Order Flow','Historical Replay','Execution Simulator','Research & Validation','Operations'];
  for(const theme of ['dark','light']){
   if(await page.locator('html').getAttribute('data-theme')!==theme)await page.getByRole('button',{name:'Toggle color theme',exact:true}).click();
   for(const width of [1440,390]){await page.setViewportSize({width,height:1000});for(const name of names){await go(name);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,`${theme}/${width}/${name}`);assert.doesNotMatch(await page.locator('body').innerText(),/\bATLAS\b/);if(width===1440&&['Stock Intelligence','Execution Simulator','Operations'].includes(name)||width===390&&['Order Book','Stock Intelligence','Command Center'].includes(name))await shot(name.replaceAll(' ','-').toLowerCase()+'-'+theme+'-'+width,name==='Order Book'?page.getByRole('region',{name:'Displayed order book',exact:true}):undefined)}}
  }
 });
 assert.deepEqual(errors,[]);
}catch(e){failure=String(e.stack||e);if(page){await page.screenshot({path:out+'/gig-failure.png',fullPage:true});fs.writeFileSync(out+'/gig-failure-text.txt',await page.locator('body').innerText())}}
finally{await browser.close();fs.writeFileSync(out+'/gig-redesign-result.json',JSON.stringify({schema:'gig.redesign.browser.v1',passed:checks.length,failed:failure?1:0,skipped:0,checks,failure,frames,errors,screenshots,scope:'Loopback native/authored fixtures;software Chromium. Visibility event case is controlled injection;not physical-device or owner private authentication evidence.'},null,2));if(failure)console.error(failure)}
if(failure)process.exit(1);
