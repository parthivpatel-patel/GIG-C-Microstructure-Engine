import {chromium} from 'playwright';import assert from 'node:assert/strict';import fs from 'node:fs';import {assertFixtureServer} from './fixture-safety.mjs';
const kind=process.env.GIG_GPU_CASE||'landscape',base=kind==='landscape'?'http://127.0.0.1:8787':'http://127.0.0.1:18797';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});let checks=0;const errors=[];
try{const page=await browser.newPage({viewport:{width:1280,height:900}});page.on('pageerror',e=>errors.push(e.message));await assertFixtureServer(page,base);await page.goto(base);
 if(kind==='landscape'){
  const enable=page.getByRole('button',{name:'Enable 3D landscape'});await enable.click();
  const panel=page.getByRole('region',{name:'Liquidity landscape'});await panel.locator('canvas').waitFor();const before=await(await page.request.get(base+'/api/v1/state')).json();
  await panel.locator('canvas').evaluate(c=>{const gl=c.getContext('webgl2');assertExtension(gl);function assertExtension(gl){const ext=gl?.getExtension('WEBGL_lose_context');if(!ext)throw Error('No context-loss extension;test cannot qualify recovery');ext.loseContext()}});
  await panel.getByTestId('landscape-fallback').waitFor({timeout:5000});assert.equal(await panel.locator('canvas').count(),0);checks++;
  await panel.getByRole('button',{name:'Retry 3D view',exact:true}).click();await panel.locator('canvas').waitFor();checks++;const canvas=panel.locator('canvas');assert.equal(await canvas.getAttribute('tabindex'),'0');const pose=await canvas.getAttribute('data-camera');await canvas.focus();await canvas.press('ArrowRight');assert.notEqual(await canvas.getAttribute('data-camera'),pose);checks++;
  const after=await(await page.request.get(base+'/api/v1/state')).json();assert.deepEqual(after.book,before.book);assert.equal(after.position,before.position);checks++;
 }else{
  await page.getByRole('button',{name:'Stock Intelligence',exact:true}).click();await page.getByRole('button',{name:'Live Market',exact:true}).click();const panel=page.getByRole('region',{name:'Multi-stock market workspace'});await panel.getByRole('button',{name:'Apply authorized subscriptions'}).click();await page.waitForFunction(async()=>{const v=await(await fetch('/api/v1/stocks/live')).json();return v.history.length>2});await panel.getByRole('button',{name:'Enable Level 1 3D'}).click();await panel.locator('canvas').first().waitFor();const before=await(await page.request.get(base+'/api/v1/stocks/live')).json();
  await panel.locator('canvas').first().evaluate(c=>{const ext=c.getContext('webgl2')?.getExtension('WEBGL_lose_context');if(!ext)throw Error('No context-loss extension');ext.loseContext()});
  await panel.getByText('WebGL unavailable;the accessible quote cards and 2D traces remain available.',{exact:true}).waitFor({timeout:5000});assert.equal(await panel.locator('canvas').count(),1);checks++;
  await panel.getByRole('button',{name:'Retry Level 1 3D',exact:true}).click();await page.waitForFunction(()=>document.querySelectorAll('canvas[aria-label^="Retained Level 1"]').length===2);checks++;
  const after=await(await page.request.get(base+'/api/v1/stocks/live')).json();assert.equal(after.connection_count,before.connection_count);assert.equal(after.generation,before.generation);assert.ok(after.accepted_observations>=before.accepted_observations);checks++;
  await panel.getByRole('button',{name:'Stop shared stream'}).click();
 }
 assert.deepEqual(errors,[]);checks++;fs.writeFileSync('build/readiness/gpu-'+kind+'.json',JSON.stringify({passed:checks,failed:0,classification:'ACTUAL_WEBGL_EXTENSION_IN_HEADLESS_SWIFTSHADER_NOT_PHYSICAL_GPU'},null,2));console.log('PASS '+kind+' checks='+checks);
}finally{await browser.close()}
