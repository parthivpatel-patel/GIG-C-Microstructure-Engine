import {test}from'node:test';import assert from'node:assert/strict';
import{boundedText,decoded}from'./response.ts';
function fixture(chunks:Uint8Array[],headers:Record<string,string>={}){
 let pulls=0,canceled=false;
 const response=new Response(new ReadableStream<Uint8Array>({pull(c){if(pulls<chunks.length)c.enqueue(chunks[pulls++]);else c.close();},cancel(){canceled=true;}},{highWaterMark:0}),{headers});
 return{response,status:()=>({pulls,canceled})};
}
const bytes=(s:string)=>new TextEncoder().encode(s);
test('small JSON and HTTP errors retain contracts',async()=>{
 assert.deepEqual(await decoded(new Response('{"ok":true}')),{ok:true});
 await assert.rejects(()=>decoded(new Response('{"error":{"message":"bounded failure"}}',{status:422})),/bounded failure/);
});
test('unknown length stops at first overflow chunk before full accumulation',async()=>{
 const f=fixture(Array.from({length:48},()=>new Uint8Array(65536)));
 await assert.rejects(()=>boundedText(f.response),/exceeds terminal budget/);
 assert.deepEqual(f.status(),{pulls:33,canceled:true}); // 2MiB retained + one rejected chunk,not3MiB.
});
test('announced oversize or malformed length cancels before any body pull',async()=>{
 for(const size of ['2097153','-1','NaN','9007199254740993']){
  const f=fixture([bytes('{}')],{'Content-Length':size});await assert.rejects(()=>boundedText(f.response));
  assert.deepEqual(f.status(),{pulls:0,canceled:true});
 }
});
test('false small length cannot bypass actual byte cap',async()=>{
 const f=fixture([new Uint8Array(128),new Uint8Array(1)],{'Content-Length':'1'});
 await assert.rejects(()=>boundedText(f.response,undefined,128),/exceeds terminal budget/);assert.equal(f.status().canceled,true);
});
test('truncated or false identity lengths reject',async()=>{
 for(const size of ['0','3']){const f=fixture([bytes('{}')],{'Content-Length':size});await assert.rejects(()=>boundedText(f.response),/length mismatch/);}
});
test('exact byte boundary and UTF8 split across chunks work',async()=>{
 const data=bytes('€🙂');const f=fixture([data.subarray(0,1),data.subarray(1,4),data.subarray(4)],{'Content-Length':'7'});
 assert.equal(await boundedText(f.response,undefined,7),'€🙂');
 await assert.rejects(()=>boundedText(fixture([data]).response,undefined,6),/budget/);
});
test('invalid or unfinished UTF8 is rejected explicitly',async()=>{
 for(const data of [new Uint8Array([0xc3]),new Uint8Array([0xff])])await assert.rejects(()=>boundedText(fixture([data]).response),/UTF-8/);
});
test('encoded Content-Length is not compared to decoded size',async()=>{
 assert.equal(await boundedText(fixture([bytes('decoded text')],{'Content-Length':'2','Content-Encoding':'gzip'}).response),'decoded text');
});
test('abort cancels a stalled read and releases its lock',async()=>{
 const c=new AbortController();let canceled=false;const body=new ReadableStream<Uint8Array>({cancel(){canceled=true;}});const r=new Response(body);
 const result=boundedText(r,c.signal);c.abort();await assert.rejects(()=>result,{name:'AbortError'});assert.equal(canceled,true);assert.equal(body.locked,false);
});
test('already aborted input and stalled cancel cannot hang the reader',async()=>{
 const c=new AbortController();c.abort();const f=fixture([bytes('{}')]);await assert.rejects(()=>boundedText(f.response,c.signal),{name:'AbortError'});assert.equal(f.status().pulls,0);
 const body=new ReadableStream<Uint8Array>({pull(x){x.enqueue(new Uint8Array(129));},cancel(){return new Promise(()=>{});}},{highWaterMark:0});
 await assert.rejects(()=>boundedText(new Response(body),undefined,128),/budget/);assert.equal(body.locked,false);
});
