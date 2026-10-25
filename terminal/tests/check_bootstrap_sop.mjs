/** Real hostile browser-origin negative control. No public target or credential output. */
import {createServer} from 'node:http';import {chromium} from 'playwright';import assert from 'node:assert/strict';
const target=process.env.TERMINAL_URL||'http://127.0.0.1:8787';assert.match(target,/^http:\/\/(127\.0\.0\.1|localhost):[0-9]+$/);
const server=createServer((_,r)=>{r.setHeader('Content-Type','text/html');r.end('<!doctype html><title>Authored cross-origin negative control</title>')});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const attacker=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try{
 const page=await browser.newPage();
 const legitimate=await page.request.get(target+'/api/v1/request-proof',{headers:{'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':target,'X-GIG-Target':'/api/v1/control'}});assert.equal(legitimate.status(),200);
 const prior=await(await page.request.get(target+'/api/v1/connection')).json();
 await page.goto(attacker);
 const result=await page.evaluate(async(target)=>{try{const r=await fetch(target+'/api/v1/request-proof',{credentials:'include',headers:{'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':target,'X-GIG-Target':'/api/v1/control'}});return {readable:true,status:r.status,body:await r.text()}}catch{return {readable:false}}},target);
 assert.equal(result.readable,false);
 const after=await(await page.request.get(target+'/api/v1/connection')).json();assert.deepEqual(after.last_request_proof_bootstrap,prior.last_request_proof_bootstrap);
 const opaque=await page.evaluate(async(target)=>{const r=await fetch(target+'/api/v1/request-proof',{mode:'no-cors',credentials:'include',headers:{'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':target,'X-GIG-Target':'/api/v1/control'}});return {type:r.type,text:await r.text()}},target);
 assert.equal(opaque.type,'opaque');assert.equal(opaque.text,'');
 const final=await(await page.request.get(target+'/api/v1/connection')).json();assert.notEqual(final.last_request_proof_bootstrap.decision,'same_origin_read');
 console.log(JSON.stringify({schema:'gig.bootstrap.sop_negative.v1',different_browser_origin:attacker,protected_target:target,legitimate_read_status:200,cross_origin_custom_header_read_blocked:true,issuer_not_reached_after_preflight:true,no_cors_response_opaque:true,no_cors_issuer_denied:true,credentials_recorded:false},null,2));
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
