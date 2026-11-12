import {test} from 'node:test';import assert from 'node:assert/strict';
import {itchBookChoices,replayMinimum,replayProgress}from './itchSession.ts';
import type{TerminalState}from './contracts.ts';
const state=(changes:Record<string,unknown>={})=>({position:9,event_count:11,capabilities:{itch_book_selection:[{index:'0',stock:'TEST    '},{index:'1',stock:'TWO     '}],selected_itch_book:0},...changes}as unknown as TerminalState);
test('Restored stock choices retain both exact independent book identities',()=>assert.deepEqual(itchBookChoices(state()),[{index:0,label:'TEST'},{index:1,label:'TWO'}]));
test('Unknown/unbounded/forged identities are not turned into stock choices',()=>{
 for(const rows of [[{index:'1',stock:'TEST    '}],[{index:'0',stock:'BAD\x00    '}],Array(3).fill({index:'0',stock:'TEST    '}),[{index:'0',stock:'        '}]])assert.deepEqual(itchBookChoices(state({capabilities:{itch_book_selection:rows}})),[]);
});
test('Default authored replay still begins at zero',()=>assert.equal(replayMinimum(state()),0));
test('ITCH replay begins at its committed checkpoint boundary',()=>assert.equal(replayMinimum(state({replay_min_position:9})),9));
test('Replay cannot seek to an invented earlier prefix or noninteger boundary',()=>{
 for(const replay_min_position of[-1,10,Infinity,1.5,'9',true])assert.throws(()=>replayMinimum(state({replay_min_position})));
});

test('Replay progress describes only the available continuation,not missing history',()=>{
 assert.equal(replayProgress(state({replay_min_position:9})),0);
 assert.equal(replayProgress(state({position:10,replay_min_position:9})),50);
 assert.equal(replayProgress(state({position:11,replay_min_position:9})),100);
 assert.equal(replayProgress(state({position:0,event_count:0})),0);
});
test('A restored checkpoint without a replayable suffix has an empty progress range',()=>{
 assert.equal(replayProgress(state({position:10,event_count:10,replay_min_position:10})),0);
});
