import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';
import {parseOfflineJson,readOfflineJson} from '../web/src/offlineJson.ts';
import {verifyCalculationPacket} from '../web/src/xbrlCalculationReport.ts';
import {verifyVintages} from '../web/src/xbrlVintages.ts';import {verifyAccuracyXbrl} from '../web/src/xbrlAccuracy.ts';
const rows=JSON.parse(readFileSync(process.argv[2],'utf8'));let rejected=0,ambiguousPreviouslyAccepted=0;
for(const [kind,packet]of rows){
 const verify=kind==='calculation'?verifyCalculationPacket:kind==='vintages'?verifyVintages:verifyAccuracyXbrl;
 const text=JSON.stringify(packet);assert.deepEqual(parseOfflineJson(text),packet);assert.deepEqual(await readOfflineJson(new Blob([text])),packet);await verify(parseOfflineJson(text),'AAPL','0000320193');
 const duplicate='{"schema":"ambiguous-before-last-value",'+text.slice(1);
 // The old JSON.parse boundary silently discarded this contradictory schema.
 await verify(JSON.parse(duplicate),'AAPL','0000320193');ambiguousPreviouslyAccepted++;
 assert.throws(()=>parseOfflineJson(duplicate));rejected++;
 const alias='{"\\u0073chema":"escaped-contradiction",'+text.slice(1);assert.throws(()=>parseOfflineJson(alias));rejected++;
}
console.log(JSON.stringify({schema:'gig.offline_json_ingress.contract.v1',cases:rows.length,ambiguous_previously_accepted:ambiguousPreviouslyAccepted,adversarial_rejections:rejected,provider_requested:false,application_started:false}));
