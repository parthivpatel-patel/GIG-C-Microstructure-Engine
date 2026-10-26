import test from 'node:test';import assert from 'node:assert/strict';
import {captureOffset,currentGeneration} from './marketPlot.ts';
test('interleaved stocks share one capture axis rather than stretching separate symbol windows',()=>{assert.equal(captureOffset(2,2,10),0);assert.equal(captureOffset(4,2,10),.25);assert.equal(captureOffset(6,2,10),.5);assert.equal(captureOffset(10,2,10),1);assert.equal(captureOffset(2,2,2),.5)});
test('malformed capture coordinates cannot become misleading plotted positions',()=>{for(const args of [[NaN,1,2],[1,2,3],[4,2,3],[2,3,1],[Number.MAX_SAFE_INTEGER+1,0,Number.MAX_SAFE_INTEGER+1]])assert.throws(()=>captureOffset(...args as [number,number,number]))});

test('reconnect plot excludes retained old-generation observations without relabeling them live',()=>{const rows=[{generation:1,id:'old'},{generation:2,id:'first'},{generation:2,id:'second'}];assert.deepEqual(currentGeneration(rows,2).map(x=>x.id),['first','second']);assert.equal(rows.length,3);assert.deepEqual(currentGeneration(rows,3),[])})
