import {assertFixtureServer} from './fixture-safety.mjs';
/** Actual default-gated terminal, no fabricated live feed or external request. */
import {waitState} from './wait-state.mjs';
import {chromium} from 'playwright';import assert from 'node:assert/strict';
const base=process.env.TERMINAL_URL||'http://127.0.0.1:8787';assert.match(base,/^http:\/\/(127\.0\.0\.1|localhost):8787$/);
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try{
 const page=await browser.newPage();await assertFixtureServer(page,base);await page.goto(base);await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button',{name:'Historical Replay',exact:true}).click();
 await page.getByLabel('Operating mode').selectOption('HISTORICAL_REPLAY');
 await page.getByLabel('Restart replay',{exact:true}).click();
 await waitState(page,base,s=>s.position===20);
 await page.getByLabel('Operating mode').selectOption('LIVE');
 await page.getByLabel('Live instrument').selectOption('ETH/USD');
 await page.getByRole('button',{name:'Connect public feed',exact:true}).click();
 await waitState(page,base,s=>s.instrument==='ETH/USD'&&s.feed.state==='ERROR');
 const state=await(await page.request.get(base+'/api/v1/state')).json();
 assert.equal(state.origin,'UNAVAILABLE');assert.deepEqual(state.book,{bids:[],asks:[]});assert.equal(state.feed.real_time,false);
 assert.equal(await page.getByLabel('Step replay').isDisabled(),true);
 await page.getByLabel('Live provider').selectOption('coinbase');
 await page.getByRole('button',{name:'Connect public feed',exact:true}).click();
 await waitState(page,base,s=>s.provider==='coinbase'&&s.feed.state==='ERROR');
 const cb=await(await page.request.get(base+'/api/v1/state')).json();assert.equal(cb.venue,'Coinbase Exchange');assert.equal(cb.origin,'UNAVAILABLE');assert.deepEqual(cb.book,{bids:[],asks:[]});assert.equal(cb.diagnostics.native_status.scope,'coinbase_L2');
 assert.equal(await page.getByRole('button',{name:'Start permitted recording',exact:true}).isDisabled(),true);
 await page.getByRole('button',{name:'Disconnect feed',exact:true}).click();
 await page.getByLabel('Operating mode').selectOption('HISTORICAL_REPLAY');
 await page.getByLabel('Step replay').click();
 await waitState(page,base,s=>s.position===21);
 await page.getByLabel('Pause visualization',{exact:true}).click();
 assert.equal(await page.getByLabel('Pause visualization',{exact:true}).getAttribute('aria-pressed'),'true');
 await page.getByLabel('Step replay').click();
 await waitState(page,base,s=>s.position===22);
 console.log(JSON.stringify({schema:'gig.browser.live_controls.v1',passed:9,failed:0,checks:['private-boundary proof controls','explicit ETH/USD selection','disabled live empty not authored','replay disabled in live mode','Coinbase selection and source isolation','Coinbase cannot use Kraken recorder','disconnect and native replay resume','visualization pause','native ingestion remains active while visualization paused'],live_verified:false},null,2));
}finally{await browser.close()}
