import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {assertFixtureServer} from './fixture-safety.mjs';
const base='http://127.0.0.1:18798',out=resolve(process.env.GIG_SPRINT3_EVIDENCE||'build/development-completion/browser');
await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const checks=[];
try{
 const page=await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));await assertFixtureServer(page,base);await page.goto(base);
 await page.getByTestId('connection-status').filter({hasText:'CONNECTED'}).waitFor();
 await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button',{name:'Multi-Stock Comparison',exact:true}).click();
 const panel=page.getByRole('region',{name:'Bounded historical market research',exact:true});
 await panel.getByLabel('Market history start',{exact:true}).fill('2026-10-20');await panel.getByLabel('Market history end',{exact:true}).fill('2026-10-20');
 function fixture(symbol,origin='HISTORICAL_SYNTHETIC'){
  return {schema:'gig.alpaca.historical.v1',symbol,kind:'bars',timeframe:'1Day',provider:'alpaca',feed:'iex',adjustment:'raw',origin,freshness:'HISTORICAL_NOT_LIVE',availability:'AVAILABLE',records:[0,1].map(i=>({timestamp:`2026-10-20T1${i}:00:00Z`,source_timestamp_ns:String(BigInt(Date.parse(`2026-10-20T1${i}:00:00Z`))*1000000n),source_record_sha256:'a'.repeat(64),duplicate_record:false,open:'100',high:'110',low:'90',close:String(101+i),volume:'10'})),record_count:2,pages:1,has_more:false,complete_market_history:false,received_at:'2026-10-21T00:00:00Z',requested_interval:{start:'2026-10-20T00:00:00Z',exclusive_end:'2026-10-21T00:00:00Z'},source_records:[{url:'https://data.alpaca.markets/v2/stocks/bars',page:1,records:2,sha256:'b'.repeat(64),received_at:'2026-10-21T00:00:00Z'}],scope:'AUTHORED_TEST_ONLY',cache_status:'ACQUIRED'};
 }
 let mode='synthetic';
 await page.route('**/api/v1/stocks/market-history',async route=>{
  const q=route.request().postDataJSON();
  if(mode==='forbidden'||mode==='rate')return route.fulfill({status:422,json:{error:{message:mode==='forbidden'?'historical_provider_forbidden':'historical_rate_limited'}}});
  const h=fixture(q.symbol,mode==='observed'?'OBSERVED_OFFICIAL_RESPONSE':'HISTORICAL_SYNTHETIC');
  if(mode==='wrong-symbol')h.symbol='NVDA';
  if(mode==='empty'){h.records=[];h.record_count=0;h.source_records[0].records=0;h.availability='EMPTY_SOURCE_RESPONSE'}
  return route.fulfill({json:h});
 });
 const load=async()=>{const done=page.waitForResponse(r=>r.url().endsWith('/stocks/market-history')&&r.request().method()==='POST');await panel.getByRole('button',{name:'Load historical observations',exact:true}).click();await done;await panel.getByRole('button',{name:'Load historical observations',exact:true}).waitFor();await page.waitForFunction(()=>!Array.from(document.querySelectorAll('button')).some(b=>b.textContent==='Reading bounded interval…'))};
 const check=async(name,fn)=>{await fn();checks.push(name)};
 const before=(await(await page.request.get(base+'/api/v1/state')).json()).book;
 await check('authored bars must never be labeled observed',async()=>{await load();assert.match(await panel.locator('svg').first().getAttribute('aria-label'),/Authored historical OHLC/);assert.doesNotMatch(await panel.locator('svg').first().getAttribute('aria-label'),/observed/i);assert.match(await panel.innerText(),/HISTORICAL_SYNTHETIC/)});
 await check('observed historical bars explicitly retain feed,symbol and non-live scope',async()=>{mode='observed';await load();assert.match(await panel.locator('svg').first().getAttribute('aria-label'),/Observed historical OHLC.*AAPL.*IEX/);assert.match(await panel.innerText(),/Historical.*not live/)});
 await check('independent symbol change is reflected in accepted chart attribution',async()=>{await panel.getByLabel('Historical security',{exact:true}).selectOption('MSFT');mode='synthetic';await load();assert.match(await panel.locator('svg').first().getAttribute('aria-label'),/Authored historical OHLC.*MSFT/)});
 await check('wrong-symbol reply preserves explicitly labeled earlier state',async()=>{mode='wrong-symbol';await load();await panel.getByRole('alert').waitFor();assert.match(await panel.locator('svg').first().getAttribute('aria-label'),/MSFT/);assert.equal(await panel.getByRole('heading',{name:/^NVDA · bars/}).count(),0)});
 await check('source entitlement error has actionable privacy-safe classification',async()=>{mode='forbidden';await load();assert.match(await panel.getByRole('alert').innerText(),/Provider denied historical access/)});
 await check('source rate limit is distinguished without an automatic retry',async()=>{mode='rate';let calls=0;const listener=r=>{if(r.url().endsWith('/stocks/market-history'))calls++};page.on('request',listener);await load();assert.match(await panel.getByRole('alert').innerText(),/Provider rate limit/);await page.waitForTimeout(150);page.off('request',listener);assert.equal(calls,1)});
 await check('empty source response replaces prior chart without fabricating a candle',async()=>{mode='empty';await load();assert.equal(await panel.locator('svg').count(),0);assert.match(await panel.innerText(),/0 records/)});
 await check('history inspection does not mutate the native L3 book or open a provider stream',async()=>{assert.deepEqual((await(await page.request.get(base+'/api/v1/state')).json()).book,before);const f=await(await page.request.get(base+'/api/v1/stocks/live')).json();assert.equal(f.connection_count,0)});
 await check('company history container and its chart both preserve authored provenance',async()=>{await page.getByRole('navigation',{name:'Research sections',exact:true}).getByRole('button',{name:'Stock Intelligence',exact:true}).click();await page.getByRole('heading',{name:/^AAPL ·/}).waitFor();await page.getByText('Historical prices & research datasets',{exact:true}).click();await page.getByRole('heading',{name:'Authored price-history fixture',exact:true}).waitFor();const figure=page.locator('.company-history-tools .historical-candlesticks').last();await figure.getByRole('img',{name:/Authored historical OHLC.*AAPL/}).waitFor();await figure.screenshot({path:resolve(out,'authored-company-candles.png')})});
 await check('no browser exceptions',async()=>assert.deepEqual(errors,[]));
 await page.screenshot({path:resolve(out,'historical-integrity-authored.png'),fullPage:true});
 const result={schema:'gig.completion.browser.v1',classification:'LOCAL_NATIVE_AND_AUTHORED_FIXTURES_NOT_PROVIDER_QUALIFICATION',passed:checks.length,failed:0,skipped:0,checks,browser:browser.version()};
 await writeFile(resolve(out,'completion-results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
}finally{await browser.close()}
