import test from 'node:test';import assert from 'node:assert/strict';
import {parseOfflineJson,readOfflineJson,MAX_OFFLINE_BYTES} from './offlineJson.ts';

test('bounded financial-export JSON preserves actual reported strings, safe metadata and authored arrays',()=>{
 const raw='{"schema":"authored","integer":9007199254740991,"negative":-2,"exact":"900719925474099312345.001","lineage":[{"accession":"first"},{"accession":"second"}],"null":null,"bool":true,"escaped":"a\\n\\u03bb"}';
 assert.deepEqual(parseOfflineJson(raw),JSON.parse(raw));assert.equal((parseOfflineJson('{"n":1e3}')as {n:number}).n,1000);
});
test('duplicate decoded member names reject at root and inside unrelated nested branches',()=>{
 for(const raw of['{"issuer_cik":"wrong","issuer_cik":"right"}','{"issuer_cik":1,"issuer_\\u0063ik":1}','{"report":{"source":1,"source":1}}','[{"x":1,"x":2}]','{"sha256":"old","sha256":"new"}'])assert.throws(()=>parseOfflineJson(raw));
 assert.deepEqual(parseOfflineJson('{"a":{"x":1},"b":{"x":2}}'),{a:{x:1},b:{x:2}});
});
test('JSON grammar rejects malformed escapes, literals, containers, numbers and trailing input',()=>{
 for(const raw of['',' ','{"x":1,}','[1,]','{"x":01}','{"x":.5}','{"x":+1}','{"x":NaN}','{"x":truefalse}','{"x":"\\x20"}','{"x":"\\u0g00"}','{"x":"unterminated}','[1] [2]','{"x":1\u0000}'])assert.throws(()=>parseOfflineJson(raw));
});
test('numeric overflow, fractional metadata and integer precision loss cannot silently rehash as other values',()=>{
 for(const raw of['{"x":9007199254740993}','{"x":-9007199254740993}','{"x":1e99999}','{"x":0.5}','{"x":1.0000000000000001}','{"x":9007199254740991.1}','{"x":-9007199254740991.1}','{"x":1e-999}','{"x":1e-128}','{"x":0e129}','{"x":'+ '1'.repeat(129)+'}'])assert.throws(()=>parseOfflineJson(raw));
 assert.deepEqual(parseOfflineJson('{"exact":"9007199254740993","integer":9007199254740991}'),{exact:'9007199254740993',integer:9007199254740991});
 for(const [token,value]of[['1e3',1000],['1.0000000000000000',1],['1000e-3',1],['900719925474099100e-2',9007199254740991],['0e-128',0],['0e128',0]]as const)assert.deepEqual(parseOfflineJson('{"n":'+token+'}'),{n:value});
});
test('UTF-8 bytes, depth, node count and decoded string limits reject before object construction',()=>{
 for(const raw of[' '.repeat(MAX_OFFLINE_BYTES+1),'"'+'é'.repeat(140000)+'"','['.repeat(34)+'0'+']'.repeat(34),'['+Array(40001).fill('0').join(',')+']','"'+'a'.repeat(16385)+'"','"'+'\\u0061'.repeat(16385)+'"'])assert.throws(()=>parseOfflineJson(raw));
 assert.equal((parseOfflineJson('"'+'\\u0061'.repeat(16384)+'"') as string).length,16384);
});
test('prototype-shaped keys remain data without prototype assignment or inherited-key collisions',()=>{
 const result=parseOfflineJson('{"__proto__":{"source":1},"constructor":2,"toString":3}')as Record<string,unknown>;
 assert.equal(Object.prototype.hasOwnProperty.call(result,'__proto__'),true);assert.equal(Object.getPrototypeOf(result),Object.prototype);assert.equal(({}as {source?:number}).source,undefined);assert.throws(()=>parseOfflineJson('{"__proto__":1,"__proto__":2}'));
});
test('file reader validates original UTF-8 and exact byte size rather than accepting replacement characters',async()=>{
 assert.deepEqual(await readOfflineJson(new Blob(['{"x":"λ"}'])),{x:'λ'});
 await assert.rejects(readOfflineJson(new Blob([new Uint8Array([123,34,120,34,58,34,0xc3,0x28,34,125])])));
 await assert.rejects(readOfflineJson({size:2,arrayBuffer:async()=>new TextEncoder().encode('{} ').buffer}));
 let calls=0;await assert.rejects(readOfflineJson({size:MAX_OFFLINE_BYTES+1,arrayBuffer:async()=>{calls++;return new ArrayBuffer(0)}}));assert.equal(calls,0);
});
test('abort before and during bounded file read prevents parsing stale bytes',async()=>{
 const first=new AbortController();first.abort();let calls=0;
 await assert.rejects(readOfflineJson({size:2,arrayBuffer:async()=>{calls++;return new ArrayBuffer(2)}},first.signal),{name:'AbortError'});assert.equal(calls,0);
 const second=new AbortController();await assert.rejects(readOfflineJson({size:2,arrayBuffer:async()=>{second.abort();return new TextEncoder().encode('{}').buffer}},second.signal),{name:'AbortError'});
});
