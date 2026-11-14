import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {verifyVintages} from '../web/src/xbrlVintages.ts';
const p=JSON.parse(readFileSync(process.argv[2],'utf8'));await verifyVintages(p,'AAPL','0000320193');
assert.deepEqual(p.entries.map(e=>e.transition),['UNAVAILABLE','FIRST_AVAILABLE','SOURCE_CHANGED']);
assert.equal(p.entries[1].packet.statement_view.periods[0].rows.at(-1).value,'400');assert.equal(p.entries[2].packet.statement_view.periods[0].rows.at(-1).value,'399');
function canonical(x){if(x===null||typeof x!=='object')return JSON.stringify(x);if(Array.isArray(x))return '['+x.map(canonical).join(',')+']';return '{'+Object.keys(x).sort().map(k=>canonical(k)+':'+canonical(x[k])).join(',')+'}'}
function resign(x){const {sha256,...body}=x;x.sha256=createHash('sha256').update(canonical(body)).digest('hex')}
let refused=0;for(const kind of ['order','transition','collection','child','source']){const bad=structuredClone(p);if(kind==='order')bad.entries.reverse();if(kind==='transition')bad.entries[1].transition='UNCHANGED_SOURCE';if(kind==='collection')bad.collection_sha256='f'.repeat(64);if(kind==='child')bad.entries[2].packet.statement_view.periods[0].rows.at(-1).value='0';if(kind==='source')bad.entries[2].previous_accession=null;resign(bad);await assert.rejects(verifyVintages(bad,'AAPL','0000320193'));refused++}
await assert.rejects(verifyVintages(p,'MSFT','0000789019'));console.log(JSON.stringify({schema:'gig.xbrl.vintage_contract.v1',entries:p.entries.length,adversarial_rejections:refused+1,provider_requested:false,application_started:false}));
