/** Actual bounded Python v2 products,not a browser/server qualification. */
import {readFileSync,statSync} from 'node:fs';import assert from 'node:assert/strict';
import {verifyAccuracyXbrl} from '../web/src/xbrlAccuracy.ts';import {validateXbrl} from '../web/src/xbrlStatements.ts';
const path=process.argv[2];assert.ok(path&&statSync(path).size<=256*1024);const rows=JSON.parse(readFileSync(path,'utf8'));let assertions=0;
for(const [name,packet]of rows){
 const p=await verifyAccuracyXbrl(packet,'AAPL','0000320193'),s=p.statement_view;assert.equal(p.schema,'gig.backend.company_xbrl.v2');assertions++;
 assert.throws(()=>validateXbrl(p,'AAPL','0000320193'));assertions++;
 if(['compatible','boundary','inconsistent','unknown_accuracy','amendment'].includes(name)){assert.equal(s.periods[0].calculations[0].status,name==='inconsistent'?'DEFINITELY_INCONSISTENT':name==='unknown_accuracy'?'UNSUPPORTED_ACCURACY':'ROUNDING_COMPATIBLE');assertions++;}
 if(name==='compatible'||name==='same_local_name'){const r=s.periods[0].rows.at(-1);assert.equal(r.status,'REPORTED_EXTENSION');assert.equal(r.facts[0].value,null);assert.equal(r.numeric_facts[0].value,'400');assert.equal(r.statement_mapping.accounting_metric,null);assertions+=4;}
 if(name==='dimensioned'){assert.equal(s.periods.length,0);assert.ok(s.source_contexts.I.dimensions.length);assertions+=2;}
 if(name==='conflict'){assert.equal(s.periods[0].rows.at(-1).status,'CONFLICT');assertions++;}
 if(name==='unavailable'){assert.equal(s.status,'UNAVAILABLE');assertions++;}
 const bad=structuredClone(p);bad.statement_view.collection_sha256='f'.repeat(64);await assert.rejects(verifyAccuracyXbrl(bad,'AAPL','0000320193'));assertions++;
 await assert.rejects(verifyAccuracyXbrl(p,'MSFT','0000789019'));assertions++;
}
console.log(JSON.stringify({schema:'gig.company_xbrl.offline_accuracy_contract.v1',cases:rows.length,assertions,application_started:false,provider_requested:false}));
