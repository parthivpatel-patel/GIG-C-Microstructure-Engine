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
 if(!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(symbol))throw Error('Invalid company identity');
 if(!Number.isInteger(offset)||offset<0||offset>1024||(form!==undefined&&!['10-K','10-K/A','10-Q','10-Q/A','8-K','8-K/A','13F-HR','13F-HR/A'].includes(form)))throw Error('Invalid bounded filing query');
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
 try{return await decoded(await fetch('/api/v2/companies/'+encodeURIComponent(symbol)+(filings?'/filings?limit=50&offset='+offset+(form?'&form='+encodeURIComponent(form):''):''),{signal:controller.signal}));}finally{clearTimeout(timer);}
}

/** Endpoint-bound proof retains Codespaces rewrite protection for stock push. */
export async function openMarketStream(signal:AbortSignal):Promise<Response>{
 const target='/api/v1/stocks/events';
 const proof=await decoded(await fetch('/api/v1/request-proof',{headers:{'X-GIG-Bootstrap':'same-origin-v1','X-GIG-Browser-Origin':location.origin,'X-GIG-Target':target},signal}));
 if(!/^[A-Za-z0-9_-]{43}$/.test(proof.proof))throw Error('Invalid stock push proof');
 const response=await fetch(target,{method:'POST',headers:{'Content-Type':'application/json','X-GIG-Request-Proof':proof.proof},body:JSON.stringify({profile:'delta-v1'}),signal});
 if(!response.ok){await decoded(response);throw Error('Stock push unavailable')}
 if(!response.headers.get('content-type')?.startsWith('text/event-stream'))throw Error('Invalid stock push content type');
 return response;
}

export async function readAcceptance<T>(symbol:string,at:string):Promise<T>{
 if(!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(symbol)||!at||at.length>40)throw Error('Invalid acceptance query');
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
 try{return await decoded(await fetch('/api/v2/companies/'+encodeURIComponent(symbol)+'/acceptance-view?at='+encodeURIComponent(at),{signal:controller.signal})) as T}finally{clearTimeout(timer)}
}

export async function readRatioHistory(symbol:string,period:string,signal:AbortSignal):Promise<unknown>{
 if(!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(symbol)||!['annual','quarter','ytd','all'].includes(period))throw Error('Invalid reported ratio history query');
 return await readBoundedFinancial('/api/v2/companies/'+encodeURIComponent(symbol)+'/ratio-history?period='+period,signal);
}
export async function readStatements(symbol:string,statement:string,period:string,signal:AbortSignal):Promise<unknown>{
 if(!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(symbol)||!['income','balance','cash'].includes(statement)||!['annual','quarter','ytd','all'].includes(period))throw Error('Invalid statements query');
 return await readBoundedFinancial('/api/v2/companies/'+encodeURIComponent(symbol)+'/statements?statement='+statement+'&period='+period,signal);
}
async function readBoundedFinancial(path:string,signal:AbortSignal):Promise<unknown>{
 const c=new AbortController(),cancel=()=>c.abort();signal.addEventListener('abort',cancel,{once:true});if(signal.aborted)c.abort();const timer=setTimeout(cancel,10000);
 try{return await decoded(await fetch(path,{signal:c.signal}))}finally{clearTimeout(timer);signal.removeEventListener('abort',cancel)}
}

export async function readSecurities(query:string,offset:number,signal:AbortSignal):Promise<unknown>{
 if(query.length>80||!Number.isInteger(offset)||offset<0||offset>150000)throw Error('Invalid directory page');
 return await readBoundedFinancial('/api/v2/securities?q='+encodeURIComponent(query)+'&offset='+offset+'&limit=20',signal);
}
export async function readDirectoryStatus(signal:AbortSignal):Promise<unknown>{return await readBoundedFinancial('/api/v2/securities/status',signal)}
export async function readCompanyAvailability(symbol:string,signal:AbortSignal):Promise<unknown>{if(!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(symbol))throw Error('Invalid issuer');return await readBoundedFinancial('/api/v2/companies/'+encodeURIComponent(symbol)+'/availability',signal)}
