/** Emulated mobile touch through Chromium input;not physical Android qualification. */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {assertFixtureServer} from './fixture-safety.mjs';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader']});
const checks=[],errors=[];fs.mkdirSync('build/mobile-touch',{recursive:true});
async function drag(page,canvas){
 await canvas.scrollIntoViewIfNeeded();const b=await canvas.boundingBox();assert.ok(b);
 const x=b.x+b.width*.4,y=b.y+b.height*.5;
 assert.ok(await canvas.evaluate((el,p)=>document.elementFromPoint(p.x,p.y)===el,{x,y}),'touch target must be unobscured');
 const session=await page.context().newCDPSession(page);
 try{
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});
  for(let i=1;i<=6;i++)await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:x+i*10,y:y-i*4}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 }finally{await session.detach()}
}
try{
 const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true,reducedMotion:'reduce'});
 page.on('pageerror',e=>errors.push(e.message));await assertFixtureServer(page,'http://127.0.0.1:8787');await page.goto('http://127.0.0.1:8787');
 const nav=page.getByRole('navigation',{name:'Research sections',exact:true});await nav.getByRole('button',{name:'Market Depth',exact:true}).tap();
 const lab=page.getByRole('region',{name:'Advanced 3D research laboratory',exact:true});await lab.getByRole('button',{name:'Open advanced research',exact:true}).tap();
 await lab.getByLabel('Research source',{exact:true}).selectOption('authored-research-v1');await page.waitForFunction(()=>Number(document.querySelector('[data-testid="advanced-research-canvas"]')?.getAttribute('data-samples'))>0);
 const canvas=lab.getByTestId('advanced-research-canvas');await canvas.waitFor();const before=await canvas.getAttribute('data-camera');assert.ok(before);await drag(page,canvas);
 await page.waitForFunction(before=>document.querySelector('[data-testid="advanced-research-canvas"]')?.getAttribute('data-camera')!==before,before);
 await lab.screenshot({path:'build/mobile-touch/advanced-replay-touch.png'});checks.push('research renderer responds to unobscured emulated touch drag');

 await assertFixtureServer(page,'http://127.0.0.1:18798');await page.goto('http://127.0.0.1:18798');const other=page.getByRole('navigation',{name:'Research sections',exact:true});
 await other.getByRole('button',{name:'Multi-Stock Comparison',exact:true}).tap();const market=page.getByRole('region',{name:'Multi-stock market workspace',exact:true});
 await market.getByRole('button',{name:'Apply authorized subscriptions',exact:true}).tap();await page.waitForFunction(async()=>{const s=await(await fetch('/api/v1/stocks/live')).json();return ['AAPL','MSFT'].every(symbol=>s.history.filter(r=>r.generation===s.generation&&r.kind==='quote'&&r.symbol===symbol).length>=4)});await market.getByRole('button',{name:'Open coordinated 3D comparison',exact:true}).tap();
 const cloud=market.getByRole('region',{name:'Level 1 observation cloud AAPL, MSFT',exact:true});await cloud.locator('canvas').waitFor();await cloud.getByText(/insufficient eligible observations/).waitFor({state:'hidden'});await cloud.getByRole('button',{name:'Pause this chart',exact:true}).tap();
 const old=await cloud.locator('canvas').getAttribute('data-camera');assert.ok(old);await drag(page,cloud.locator('canvas'));
 await page.waitForFunction(old=>document.querySelector('.quote-cloud canvas')?.getAttribute('data-camera')!==old,old);
 await cloud.screenshot({path:'build/mobile-touch/level1-authored-touch.png'});checks.push('quote renderer responds to touch with paused authored source');
 await market.getByRole('button',{name:'Stop shared stream',exact:true}).tap();

 await other.getByRole('button',{name:'Research & Validation',exact:true}).tap();const model=page.getByRole('region',{name:'Research surface explorer',exact:true});const surface=model.getByTestId('research-model-surface');await surface.waitFor();
 await surface.scrollIntoViewIfNeeded();const original=await surface.screenshot();assert.ok((await surface.screenshot()).equals(original),'modeled input is static before touch');await drag(page,surface);assert.equal((await surface.screenshot()).equals(original),false);
 await model.screenshot({path:'build/mobile-touch/garch-modeled-touch.png'});checks.push('static modeled surface camera responds to actual browser touch input');
 assert.deepEqual(errors,[]);console.log(JSON.stringify({schema:'gig.atlas.mobile_touch.v1',passed:checks.length,failed:0,skipped:0,checks,classification:'AUTHORED_REPLAY_LEVEL1_AND_MODEL_FIXTURES_EMULATED_TOUCH_NOT_PHYSICAL_DEVICE'}));
}finally{await browser.close()}
