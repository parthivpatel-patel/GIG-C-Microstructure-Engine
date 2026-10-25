/** Browser-side Origin evidence;never records protocols,cookies or ticket responses. */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const base=process.env.TERMINAL_URL||'http://127.0.0.1:8787';
assert.match(base,/^http:\/\/(127\.0\.0\.1|localhost):[0-9]+$/);
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
try{
 const page=await browser.newPage();const cdp=await page.context().newCDPSession(page);await cdp.send('Network.enable');
 const urls=new Map();let captured;
 cdp.on('Network.webSocketCreated',event=>urls.set(event.requestId,event.url));
 cdp.on('Network.webSocketWillSendHandshakeRequest',event=>{const h=event.request.headers;captured={url:urls.get(event.requestId),origin:h.Origin||h.origin||null};});
 await page.goto(base,{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.querySelector('[data-testid="connection-status"]')?.textContent==='CONNECTED');
 const actual=await page.evaluate(()=>({origin:location.origin,host:location.host,protocol:location.protocol}));
 assert.equal(captured.origin,actual.origin);assert.equal(captured.url,base.replace('http:','ws:')+'/api/v1/stream');
 const diag=await(await page.request.get(base+'/api/v1/connection')).json();
 assert.equal(diag.last_browser_bootstrap.browser_origin,actual.origin);
 assert.equal(diag.last_authenticated_websocket.attempt_id,diag.last_browser_bootstrap.attempt_id);
 assert.equal(diag.last_authenticated_websocket.authorization,'accepted_origin_ticket');
 console.log(JSON.stringify({schema:'gig.browser.handshake_evidence.v1',browser:browser.version(),document:actual,outgoing_browser_handshake:captured,bootstrap_and_socket_correlated:true,credential_headers_recorded:false,scope:'Local browser CDP capture;not owner private Codespaces edge capture'},null,2));
}finally{await browser.close();}
