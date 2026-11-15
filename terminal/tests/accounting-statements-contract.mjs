import {readFileSync} from 'node:fs';import assert from 'node:assert/strict';
import {parseOfflineJson} from '../web/src/offlineJson.ts';import {verifyXbrlDigest} from '../web/src/xbrlStatements.ts';
const rows=JSON.parse(readFileSync(process.argv[2],'utf8'));let assertions=0,rejections=0;
for(const [name,raw]of rows){
 const p=parseOfflineJson(JSON.stringify(raw));await verifyXbrlDigest(p);await verifyXbrlDigest(p.accounting_report);await verifyXbrlDigest(p.accounting_report.source_audit);assertions+=3;
 assert.equal(p.original_parsed_sha256,p.accounting_report.parsed_sha256);assert.equal(p.dts_sha256,p.accounting_report.dts_sha256);assert.equal(p.dts_sha256,p.accounting_report.source_audit.dts_sha256);assert.equal(p.source_filing.source_sha256,p.accounting_report.source_audit.source_sha256);assert.equal(p.lineage.sources[0].parsed_sha256,p.admitted_parsed_sha256);assert.equal(p.complete_statements,false);assertions+=6;
 const ids=new Set(p.accounting_report.source_audit.source_fact_ids);
 for(const section of Object.values(p.statements))for(const period of section.periods)for(const row of period.rows){assert.equal(row.classification.accounting_metric,null);assertions++;for(const fact of row.facts){assert.ok(ids.has(fact.source_fact_id));assertions++}if(row.status!=='SUPPORTED'){assert.equal(row.value,null);assertions++}}
 const alias=p.statements.income_statement.periods[0].rows.at(-1);
 assert.equal(alias.essence_concept,'{https://authored.invalid/taxonomy}IncomeTotal');assertions++;
 if(name==='reported'){assert.equal(alias.equivalence_status,'SOURCE_RELATIONSHIP_REPORTED_EQUAL');assert.equal(alias.value,'100');assertions+=2}
 if(name==='exact'){assert.equal(alias.equivalence_status,'SOURCE_EQUIVALENCE_VERIFIED');assertions++}
 if(name==='conflicting'){assert.equal(alias.status,'CONFLICTING');assertions++}
 if(name==='missing'||name==='amended_vintage'){assert.equal(alias.status,'MISSING');assert.equal(alias.facts.length,0);assertions+=2}
 if(name==='unsupported'){assert.equal(p.statements.cash_flow_statement.periods[0].rows[0].status,'UNSUPPORTED');assertions++}
 if(name==='original_vintage'){assert.equal(p.source_filing.accession,'0000000123-24-000001');assertions++}
 if(name==='amended_vintage'){assert.equal(p.source_filing.accession,'0000000123-24-000002');assert.equal(p.lineage.sources.length,2);assertions+=2}
 const bad=structuredClone(p);bad.source_filing.source_sha256='0'.repeat(64);await assert.rejects(verifyXbrlDigest(bad));rejections++;
}
console.log(JSON.stringify({schema:'gig.accounting_statement.offline_contract.v1',cases:rows.length,assertions,adversarial_rejections:rejections,provider_requested:false,application_started:false}));
