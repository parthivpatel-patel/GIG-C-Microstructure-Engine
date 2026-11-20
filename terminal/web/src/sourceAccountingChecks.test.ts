import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {verifyAccountingSourceChecks} from './sourceAccountingChecks.ts';
import type {SourceAccountingPacket} from './financialSourceContract.ts';

function generated(name:string){return JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON||'python3',[fileURLToPath(new URL('../../tests/'+name,import.meta.url))],{encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024}))}
const original=generated('source_accounting_ui_fixtures.py').accounting as [string,SourceAccountingPacket][];
const edges=generated('source_accounting_checks_fixtures.py') as [string,SourceAccountingPacket][];
const packets=new Map([...original,...edges]);
function packet(name:string){return structuredClone(packets.get(name)!)}
function arc(p:SourceAccountingPacket){return p.accounting.accounting_report!.networks.find(n=>n.kind==='essence-alias')!.arcs[0]}
for(const [name,p] of [...original,...edges])test('source relationship reconstruction admits actual Python export '+name,()=>verifyAccountingSourceChecks(p));

test('conflicting original 100 and 101 cannot become supported through metadata changes',()=>{
 const p=packet('conflicting'),c=arc(p).checks[0];c.status='SUPPORTED_EQUAL';delete c.reason;c.standards_value_equality_established=true;
 assert.throws(()=>verifyAccountingSourceChecks(p),/accounting relationship/);
});
test('finite accuracy equality cannot claim standards equality; INF cannot lose its derived flag',()=>{
 for(const name of ['reported','exact']){const p=packet(name),c=arc(p).checks[0];c.standards_value_equality_established=!c.standards_value_equality_established;assert.throws(()=>verifyAccountingSourceChecks(p))}
});
test('checks require all original duplicate facts and correct source/target memberships',()=>{
 for(const edit of [
  (p:SourceAccountingPacket)=>{arc(p).checks[0].alias_facts!.pop()},
  (p:SourceAccountingPacket)=>{arc(p).checks[0].source_fact_ids.reverse()},
  (p:SourceAccountingPacket)=>{const c=arc(p).checks[0];[c.essence_facts,c.alias_facts]=[c.alias_facts,c.essence_facts]},
 ]){const p=packet('duplicate');edit(p);assert.throws(()=>verifyAccountingSourceChecks(p))}
});
test('nil, dimensional, units and lexical identifiers cannot be masked as supported',()=>{
 for(const name of ['nil','dimensional','units','identifier']){const p=packet(name),c=arc(p).checks[0];c.status='SUPPORTED_EQUAL';delete c.reason;assert.throws(()=>verifyAccountingSourceChecks(p))}
});
test('source member decimals, nil state and raw values are independently reconstructed',()=>{
 for(const key of ['decimals','nil','reported_value','lexical_value']){const p=packet('reported');arc(p).checks[0].alias_facts![0][key]=key==='nil'?true:'101';assert.throws(()=>verifyAccountingSourceChecks(p))}
});
test('requires-element uses global occurrence rather than inventing value equivalence',()=>{
 const p=packet('requires_satisfied'),a=p.accounting.accounting_report!.networks.find(n=>n.kind==='requires-element')!.arcs[0];
 assert.equal(a.checks[0].status,'SATISFIED');a.checks[0].status='SUPPORTED_EQUAL';assert.throws(()=>verifyAccountingSourceChecks(p));
 const missing=packet('requires_missing'),m=missing.accounting.accounting_report!.networks.find(n=>n.kind==='requires-element')!.arcs[0];m.checks[0].status='SATISFIED';assert.throws(()=>verifyAccountingSourceChecks(missing));
});
test('requires-element occurrence includes nil targets and different lexical entity contexts',()=>{
 for(const name of ['requires_cross_context','requires_nil']){const p=packet(name),a=p.accounting.accounting_report!.networks.find(n=>n.kind==='requires-element')!.arcs[0];assert.equal(a.checks[0].status,'SATISFIED');verifyAccountingSourceChecks(p)}
});
test('numeric lexical spelling and signed zero compare exact values without Number conversion',()=>{
 for(const name of ['decimal_lexical','signed_zero']){const p=packet(name);assert.equal(arc(p).checks[0].status,'SUPPORTED_EQUAL');assert.equal(arc(p).checks[0].standards_value_equality_established,true);verifyAccountingSourceChecks(p)}
});
test('string values remain lexical and do not enter numeric parsing',()=>{
 const p=packet('strings');assert.equal(arc(p).checks[0].standards_value_equality_established,true);verifyAccountingSourceChecks(p);
 arc(p).checks[0].alias_facts![0].reported_value='different text';assert.throws(()=>verifyAccountingSourceChecks(p));
});
test('declaration claims must match the original DTS concepts and source document identities',()=>{
 const p=packet('reported');(arc(p).declaration_constraints as {period_type:string}).period_type='instant';assert.throws(()=>verifyAccountingSourceChecks(p));
});
