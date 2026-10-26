import {validateState} from './contracts';import type {TerminalState} from './contracts';
async function decoded(r:Response){const length=Number(r.headers.get('Content-Length')||0);if(length>2*1024*1024)throw new Error('Response exceeds terminal budget');const text=await r.text();if(text.length>2*1024*1024)throw new Error('Response exceeds terminal budget');let result;try{result=JSON.parse(text)}catch{throw new Error(`API returned non-JSON response (${r.status})`)}if(!r.ok)throw new Error(result.detail?.message||result.error?.message||result.detail||`API error ${r.status}`);return result;}
export async function request<T=unknown>(path:string,body?:unknown,timeoutMs=10000):Promise<T>{const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),Math.min(30000,Math.max(1000,timeoutMs)));try{
 const headers:Record<string,string>={'Content-Type':'application/json'};
 if(body!==undefined){
  // Same-origin custom-header read;cross-origin callers cannot pass its preflight.
  const capability=await decoded(await fetch('/api/v1/request-proof',{headers:{'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':location.origin,'X-GIG-Target':'/api/v1'+path},signal:controller.signal}));
  if(!/^[A-Za-z0-9_-]{43}$/.test(capability.proof))throw new Error('Invalid request proof');
  headers['X-GIG-Request-Proof']=capability.proof;
 }
 return await decoded(await fetch('/api/v1'+path,{method:body===undefined?'GET':'POST',headers:body===undefined?{}:headers,body:body===undefined?undefined:JSON.stringify(body),signal:controller.signal})) as T;
 }finally{clearTimeout(timer)}}
export async function getState():Promise<TerminalState>{return validateState(await request('/state'))}
/** Cache-only v2 reads; caller cannot provide an arbitrary host or mutation. */
export async function readCompanyV2(symbol:string,filings=false,offset=0,form?:string):Promise<unknown>{
 if(!/^[A-Z]{1,5}(?:[.-][A-Z])?$/.test(symbol))throw Error('Invalid company identity');
 if(!Number.isInteger(offset)||offset<0||offset>128||(form!==undefined&&!['10-K','10-K/A','10-Q','10-Q/A','8-K','8-K/A','13F-HR','13F-HR/A'].includes(form)))throw Error('Invalid bounded filing query');
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
 try{return await decoded(await fetch('/api/v2/companies/'+encodeURIComponent(symbol)+(filings?'/filings?limit=50&offset='+offset+(form?'&form='+encodeURIComponent(form):''):''),{signal:controller.signal}));}finally{clearTimeout(timer);}
}

/** Endpoint-bound proof retains Codespaces rewrite protection for stock push. */
export async function openMarketStream(signal:AbortSignal):Promise<Response>{
 const target='/api/v1/stocks/events';
 const proof=await decoded(await fetch('/api/v1/request-proof',{headers:{'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':location.origin,'X-GIG-Target':target},signal}));
 if(!/^[A-Za-z0-9_-]{43}$/.test(proof.proof))throw Error('Invalid stock push proof');
 const response=await fetch(target,{method:'POST',headers:{'Content-Type':'application/json','X-GIG-Request-Proof':proof.proof},body:'{}',signal});
 if(!response.ok){await decoded(response);throw Error('Stock push unavailable')}
 if(!response.headers.get('content-type')?.startsWith('text/event-stream'))throw Error('Invalid stock push content type');
 return response;
}
