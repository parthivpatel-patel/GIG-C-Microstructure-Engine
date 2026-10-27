import {MarketProjectionReader} from './marketDelta';
import {MarketEventDecoder} from './marketStreamProtocol';
import {openMarketStream} from './api';
/** Bounded incremental SSE parser;no URL credentials,tokens or EventSource query proof. */
export async function consumeMarketStream(signal:AbortSignal,onState:(v:unknown)=>void){
 const linked=new AbortController(),abort=()=>linked.abort();signal.addEventListener('abort',abort,{once:true});if(signal.aborted)linked.abort();
 let reader:ReadableStreamDefaultReader<Uint8Array>|undefined;
 const opening=setTimeout(()=>linked.abort(),10000);
 try{
 const response=await openMarketStream(linked.signal);clearTimeout(opening);if(!response.body)throw Error('Stock push body unavailable');
 reader=response.body.getReader();const decoder=new MarketEventDecoder(),projection=new MarketProjectionReader();
 while(!signal.aborted){let timer:ReturnType<typeof setTimeout>|undefined;const result=await Promise.race([reader.read(),new Promise<never>((_,reject)=>{timer=setTimeout(()=>reject(Error('Stock push heartbeat timeout')),15000)})]).finally(()=>clearTimeout(timer));if(result.done){decoder.finish();throw Error('Stock push disconnected')}for(const data of decoder.push(result.value))onState(projection.accept(data))
 }
 }finally{clearTimeout(opening);linked.abort();signal.removeEventListener('abort',abort);await reader?.cancel().catch(()=>{});reader?.releaseLock()}
}
