/** Offline real Python-product → TypeScript validation;no browser or listener. */
import assert from 'node:assert/strict';import {readFileSync,statSync} from 'node:fs';
import {verifyXbrl} from '../web/src/xbrlStatements.ts';
const path=process.argv[2];assert.ok(path&&statSync(path).size<=256*1024);const data=JSON.parse(readFileSync(path,'utf8'));let checks=0;
for(const [name,expected,p]of data){
 const v=await verifyXbrl(p,'AAPL','0000320193');assert.equal(v.statement_view.status,expected);checks++;
 assert.equal(v.data_origin,name==='unavailable'?'UNAVAILABLE':'HISTORICAL_SYNTHETIC');checks++;
 if(v.statement_view.status==='AVAILABLE'){assert.equal(v.statement_view.source_filing.received_at,null);checks++;for(const per of v.statement_view.periods)for(const row of per.rows)if(row.status==='REPORTED'){assert.equal(typeof row.value,'string');assert.ok(row.facts.length);checks+=2;}}
 const bad=structuredClone(p);bad.statement_view.collection_sha256='f'.repeat(64);await assert.rejects(verifyXbrl(bad,'AAPL','0000320193'));checks++;
 await assert.rejects(verifyXbrl(p,'MSFT','0000789019'));checks++;
}
console.log(JSON.stringify({schema:'gig.company_xbrl.offline_contract.v1',cases:data.length,assertions:checks,application_started:false,provider_requested:false}));
