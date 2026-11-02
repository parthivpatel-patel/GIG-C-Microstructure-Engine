import test from 'node:test';import assert from 'node:assert/strict';
import {displayedLadder} from './bookPresentation.ts';
test('display ladder keeps native ordering and exact cumulative quantities',()=>{const rows=[{price_ticks:'103',quantity:'2'},{price_ticks:'101',quantity:'3'}];const copy=structuredClone(rows);assert.deepEqual(displayedLadder(rows,40).map(r=>r.cumulative),['2','5']);assert.deepEqual(rows,copy)});
test('cumulative presentation never overflows uint64 or binary64',()=>{const m='18446744073709551615';assert.equal(displayedLadder([{price_ticks:'1',quantity:m},{price_ticks:'2',quantity:m}],40)[1].cumulative,'36893488147419103230')});
test('visible depth bound does not include unseen quantities',()=>{assert.equal(displayedLadder([{price_ticks:'1',quantity:'3'},{price_ticks:'2',quantity:'5'}],1).at(-1)?.cumulative,'3')});
test('invalid presentation bounds and negative quantities reject',()=>{for(const bound of [0,41,NaN,1.5])assert.throws(()=>displayedLadder([],bound));assert.throws(()=>displayedLadder([{price_ticks:'1',quantity:'-1'}],1))});
