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
