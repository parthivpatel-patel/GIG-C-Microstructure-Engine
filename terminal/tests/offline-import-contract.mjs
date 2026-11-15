import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {parseOfflineJson,readOfflineJson} from '../web/src/offlineJson.ts';
import {verifyCalculationPacket} from '../web/src/xbrlCalculationReport.ts';
import {verifyVintages} from '../web/src/xbrlVintages.ts';import {verifyAccuracyXbrl} from '../web/src/xbrlAccuracy.ts';
const rows=JSON.parse(readFileSync(process.argv[2],'utf8'));let rejected=0,ambiguousPreviouslyAccepted=0;
function canonical(x){if(x===null||typeof x!=='object')return JSON.stringify(x);if(Array.isArray(x))return '['+x.map(canonical).join(',')+']';return '{'+Object.keys(x).sort().map(k=>canonical(k)+':'+canonical(x[k])).join(',')+'}'}
function sign(p){const {sha256,...body}=p;p.sha256=createHash('sha256').update(canonical(body)).digest('hex')}
for(const [kind,packet]of rows){
 const verify=kind==='calculation'?verifyCalculationPacket:kind==='vintages'?verifyVintages:verifyAccuracyXbrl;
 const text=JSON.stringify(packet);assert.deepEqual(parseOfflineJson(text),packet);assert.deepEqual(await readOfflineJson(new Blob([text])),packet);await verify(parseOfflineJson(text),'AAPL','0000320193');
 const duplicate='{"schema":"ambiguous-before-last-value",'+text.slice(1);
 // The old JSON.parse boundary silently discarded this contradictory schema.
 await verify(JSON.parse(duplicate),'AAPL','0000320193');ambiguousPreviouslyAccepted++;
 assert.throws(()=>parseOfflineJson(duplicate));rejected++;
 const alias='{"\\u0073chema":"escaped-contradiction",'+text.slice(1);assert.throws(()=>parseOfflineJson(alias));rejected++;
}
const original=rows.find(([kind])=>kind==='statement')[1];
for(const mutation of['period','acceptance','cutoff','source-hash']){
 const packet=structuredClone(original),view=packet.statement_view;
 if(mutation==='period')view.periods[0].end='2023-02-30';
 if(mutation==='acceptance')view.source_filing.accepted_at='2024-02-30T00:00:00Z';
 if(mutation==='cutoff')view.cutoff_ns='0';
 if(mutation==='source-hash')view.source_filing.source_sha256='0'.repeat(64);
 if(mutation!=='source-hash'){sign(view);sign(packet)}
 await assert.rejects(verifyAccuracyXbrl(parseOfflineJson(JSON.stringify(packet)),'AAPL','0000320193'),undefined,mutation);rejected++;
}
for(const token of['1.0000000000000001','9007199254740991.1','9007199254740993','1e-999','-0','-0.0','-0e12']){assert.throws(()=>parseOfflineJson('{"index":'+token+'}'));rejected++}
console.log(JSON.stringify({schema:'gig.offline_json_ingress.contract.v1',cases:rows.length,ambiguous_previously_accepted:ambiguousPreviouslyAccepted,adversarial_rejections:rejected,provider_requested:false,application_started:false}));
