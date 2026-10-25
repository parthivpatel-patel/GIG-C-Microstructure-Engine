import {assertFixtureServer} from './fixture-safety.mjs';
/** Actual secured browser/native recorded session, authored data only. */
import {waitState} from './wait-state.mjs';
import {chromium} from 'playwright';import assert from 'node:assert/strict';
const base=process.env.TERMINAL_URL||'http://127.0.0.1:8787';assert.match(base,/^http:\/\/(127\.0\.0\.1|localhost):8787$/);
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try{
 const page=await browser.newPage();await assertFixtureServer(page,base);await page.request.post(base+'/api/v1/recording',{headers:{Origin:new URL(base).origin},data:{action:'delete_l2',identity:'authored-l2-v2'}});await page.goto(base);
 async function mutation(action,operation){const committed=page.waitForResponse(r=>r.request().method()==='POST'&&JSON.parse(r.request().postData()||'{}').action===action);await operation();const response=await committed;assert.equal(response.status(),200);return response.json()}
 await mutation('mode',()=>page.getByLabel('Operating mode').selectOption('HISTORICAL_REPLAY'));
 await mutation('save_l2_fixture',()=>page.getByRole('button',{name:'Save authored L2 recording',exact:true}).click());
 await page.getByLabel('Recorded L2 session').selectOption('authored-l2-v2');
 await mutation('load_l2',()=>page.getByRole('button',{name:'Load L2 session',exact:true}).click());
 await waitState(page,base,s=>s.provider==='kraken-recorded');
 let state=await mutation('step',()=>page.getByLabel('Step replay',{exact:true}).click());
 assert.equal(state.position,1);assert.equal(state.origin,'HISTORICAL_SYNTHETIC');assert.equal(state.book.bids[0].quantity,'200000000');
 state=await mutation('seek',()=>page.getByLabel('Seek replay position').fill('2'));
 assert.equal(state.position,2);assert.equal(state.book.bids[0].quantity,'400000000');assert.deepEqual(state.research.metrics.ofi.value,{numerator:'200000000',denominator:'1'});await page.getByTestId('window-analytics').locator('.integrity-item').filter({hasText:'Displayed order-flow imbalance'}).getByText('2',{exact:true}).waitFor();
 state=await mutation('restart',()=>page.getByLabel('Restart replay',{exact:true}).click());assert.equal(state.position,0);
 state=await mutation('speed',()=>page.getByLabel('Replay speed',{exact:true}).selectOption('2'));assert.equal(state.speed,2);
 await mutation('play',()=>page.getByLabel('Play replay',{exact:true}).click());
 await waitState(page,base,s=>s.position===5);
 state=await(await page.request.get(base+'/api/v1/state')).json();assert.equal(state.position,5);assert.equal(state.playing,false);assert.equal(state.book.bids[0].price_ticks,'9900000000');
 await mutation('delete_l2',()=>page.getByRole('button',{name:'Delete L2 session',exact:true}).click());
 state=await mutation('dataset',()=>page.getByLabel('Replay source').selectOption('terminal-authored-v2'));assert.equal(state.provider,'authored');
 console.log(JSON.stringify({schema:'gig.browser.recorded_l2.v1',passed:9,failed:0,checks:['save authored native log','discover/select','native exact step','seek exact quantity','causal OFI corresponds to native prefix','restart prefix0','speed and playback to EOF','delete with owned cache','return to L3 authored source'],observed_data:false},null,2));
}finally{await browser.close()}
