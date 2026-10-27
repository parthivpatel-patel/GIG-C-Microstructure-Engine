import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {assertFixtureServer} from './fixture-safety.mjs';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});const results=[];
try{
 const page=await browser.newPage({viewport:{width:1280,height:900}});const base='http://127.0.0.1:8787';await assertFixtureServer(page,base);await page.goto(base);
 for(const symbol of ['AAPL','APLD','CRWV']){
  await page.getByLabel('Global company search').fill(symbol);await page.getByRole('button',{name:'Search companies',exact:true}).click();await page.getByRole('region',{name:'Company search results'}).getByRole('button',{name:new RegExp('^'+symbol+' ·')}).click();
  const stock=page.getByTestId('stock-workspace');await stock.getByRole('heading',{name:new RegExp('^'+symbol+' ·')}).waitFor();assert.equal(await stock.getByRole('button',{name:'Refresh SEC disclosures'}).isEnabled(),false);
  if(symbol!=='AAPL')await stock.getByText(/CIK not verified/).waitFor();
  const api=await(await page.request.get(base+'/api/v1/stocks/company?symbol='+symbol)).json();assert.equal(api.instrument.symbol,symbol);assert.equal(api.instrument.cik,symbol==='AAPL'?'0000320193':null);assert.equal(api.classification,'UNAVAILABLE');results.push({symbol,passed:true,sec_available:false,live_entitlement_granted:false});
 }
 await page.screenshot({path:'build/continuation/discovery-crwv-gated.png',fullPage:true});
 fs.writeFileSync('build/continuation/discovery-browser.json',JSON.stringify({results,origin:'GATED_NO_PROVIDER_REQUESTS',passed:3,failed:0},null,2));console.log('PASS 3/3 AAPL,APLD,CRWV browser discovery');
}finally{await browser.close()}
