/** Byte limits apply to application-retained buffers. Browser transport may prefetch
 * independently; cancel immediately on overflow rather than decoding a whole body. */
export const MAX_API_RESPONSE_BYTES=2*1024*1024;

export async function boundedText(response:Response,signal?:AbortSignal,limit=MAX_API_RESPONSE_BYTES):Promise<string>{
 if(!Number.isSafeInteger(limit)||limit<1||limit>MAX_API_RESPONSE_BYTES)throw Error('Invalid response budget');
 let reader:ReadableStreamDefaultReader<Uint8Array>|undefined;
 const cancel=()=>{if(reader)void reader.cancel().catch(()=>{});else void response.body?.cancel().catch(()=>{});};
 const header=response.headers.get('Content-Length');let declared:number|undefined;
 if(header!==null){
  if(!/^[0-9]{1,16}$/.test(header)||!Number.isSafeInteger(Number(header))){cancel();throw Error('Invalid API Content-Length');}
  declared=Number(header);
  if(declared>limit){cancel();throw Error('Response exceeds terminal budget');}
 }
 if(signal?.aborted){cancel();throw new DOMException('API response aborted','AbortError');}
 if(!response.body){if(declared)throw Error('API response length mismatch');return '';}
 reader=response.body.getReader();
 let rejectAbort:(reason:unknown)=>void=()=>{};
 const aborted=new Promise<never>((_,reject)=>{rejectAbort=reject;});
 const onAbort=()=>{cancel();rejectAbort(new DOMException('API response aborted','AbortError'));};
 signal?.addEventListener('abort',onAbort,{once:true});
 let bytes=new Uint8Array(Math.min(limit,declared||8192)),used=0,complete=false;
 try{
  // The source is not trusted to honor Content-Length. Every chunk is checked
  // before copying or decoding; geometric buffers avoid per-byte chunk arrays.
  while(true){
   const {done,value}=await Promise.race([reader.read(),aborted]);
   if(signal?.aborted)throw new DOMException('API response aborted','AbortError');
   if(done){complete=true;break;}
   if(!(value instanceof Uint8Array))throw Error('Invalid API response chunk');
   if(value.byteLength>limit-used)throw Error('Response exceeds terminal budget');
   if(used+value.byteLength>bytes.byteLength){
    const grown=new Uint8Array(Math.min(limit,Math.max(used+value.byteLength,bytes.byteLength*2)));
    grown.set(bytes.subarray(0,used));bytes=grown;
   }
   bytes.set(value,used);used+=value.byteLength;
  }
  // Fetch returns decompressed bytes while Content-Length may describe encoded
  // bytes. Compare only identity representations;enforce the byte budget for both.
  if(declared!==undefined&&['','identity'].includes(response.headers.get('Content-Encoding')||'')&&used!==declared)throw Error('API response length mismatch');
  try{return new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(0,used));}
  catch{throw Error('Invalid UTF-8 API response');}
 }finally{
  signal?.removeEventListener('abort',onAbort);
  if(!complete)cancel();
  reader.releaseLock();
 }
}

export async function decoded(response:Response,signal?:AbortSignal):Promise<any>{
 const text=await boundedText(response,signal);let value;
 try{value=JSON.parse(text);}catch{throw Error(`API returned non-JSON response (${response.status})`);}
 if(!response.ok){
  const reason=value?.detail?.message||value?.error?.message||value?.detail;
  throw Error(typeof reason==='string'&&reason.length<=240?reason:`API error ${response.status}`);
 }
 return value;
}
