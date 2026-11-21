import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import ts from 'typescript';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {parseOfflineJson} from './offlineJson.ts';
import {createSourceImportGuard} from './sourceImportGuard.ts';
import {comparisonCanonical,parseStatementComparisonJson,readStatementComparisonJson,verifyStatementComparison,MAX_COMPARISON_BYTES} from './statementComparisonContract.ts';
import type {StatementComparisonPacket} from './statementComparisonContract.ts';
const jsx=ts.transpileModule(readFileSync(new URL('./StatementComparison.tsx',import.meta.url),'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const compiled=jsx.replace(/from (["'])([^"']+)\1/g,(_,_q:string,name:string)=>`from ${JSON.stringify(import.meta.resolve(name.startsWith('.')&&!name.endsWith('.ts')?name+'.ts':name))}`);
const {StatementComparison,StatementComparisonView,readStatementComparison}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
const generated=JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON||'python3',[fileURLToPath(new URL('../../tests/statement_comparison_ui_fixtures.py',import.meta.url))],{encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024})) as [string,StatementComparisonPacket][];
const base=generated.find(([name])=>name==='changed')![1];
async function resign(p:StatementComparisonPacket){const {sha256,...body}=p;void sha256;p.sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(comparisonCanonical(body)))),b=>b.toString(16).padStart(2,'0')).join('');return p}
for(const [name,raw]of generated)test(`actual Python comparison -> strict admission -> React source table: ${name}`,async()=>{
 const packet:StatementComparisonPacket=await readStatementComparison(new Blob([JSON.stringify(raw)]),'AAPL','0000320193');const html=renderToStaticMarkup(createElement(StatementComparisonView,{packet}));assert.match(html,/aria-label="Admitted statement-vintage comparison"/);assert.match(html,/restatements are not established/);assert.match(html,/do not independently authenticate the issuer/);assert.ok(html.includes(packet.sha256));for(const entry of packet.entries){assert.ok(html.includes(entry.cutoff_ns));assert.ok(html.includes(entry.sha256));if(entry.accounting.source_filing)assert.ok(html.includes(entry.accounting.source_filing.origin))}for(const comparison of packet.comparisons)for(const section of Object.values(comparison.statements))for(const row of section.rows){assert.ok(html.includes(row.status));for(const side of [row.previous,row.current])if(side){assert.ok(html.includes(side.source_sha256));assert.ok(html.includes(side.row_sha256))}}if(packet.comparisons.some(c=>Object.values(c.statements).some(s=>s.rows.length))){assert.match(html,/scope="col"/);assert.match(html,/scope="row"/);assert.match(html,/tabindex="0"/)}
});
test('unadmitted actual panel exposes accessible bounded control without invented rows',()=>{for(const cik of ['0000320193',null]){const html=renderToStaticMarkup(createElement(StatementComparison,{symbol:'AAPL',cik}));assert.match(html,/Open statement-vintage comparison export/);assert.match(html,/4 MiB/);assert.match(html,/aria-busy="false"/);assert.doesNotMatch(html,/<table/);if(!cik)assert.match(html,/disabled=""/);else assert.doesNotMatch(html,/disabled=""/)}});
const edits:[string,(p:StatementComparisonPacket)=>void][]=[
 ['derived status',p=>{p.comparisons[0].statements.income_statement.rows.find(r=>r.status==='REPORTED_NUMERIC_VALUE_CHANGED')!.status='REPORTED_NUMERIC_VALUE_UNCHANGED'}],
 ['comparable flag',p=>{p.comparisons[0].statements.income_statement.rows[0].reported_values_comparable=false}],
 ['source relation',p=>{p.comparisons[0].source_relation='SAME_SELECTED_FILING'}],
 ['adjacency',p=>{p.comparisons[0].current_entry_index=0}],
 ['role binding',p=>{p.comparisons[0].statements.income_statement.current_role_binding!.accounting_role='invented'}],
 ['row omission',p=>{p.comparisons[0].statements.income_statement.rows.pop()}],
 ['row order',p=>{p.comparisons[0].statements.income_statement.rows.reverse()}],
 ['source hash',p=>{p.comparisons[0].statements.income_statement.rows[0].current!.source_sha256='0'.repeat(64)}],
 ['source fact',p=>{p.comparisons[0].statements.income_statement.rows[0].current!.source_facts=[]}],
 ['exact reported value',p=>{p.comparisons[0].statements.income_statement.rows[0].current!.reported_value='999'}],
 ['calculation omission',p=>{p.comparisons[0].statements.cash_flow_statement.rows[0].current_calculations=[]}],
 ['period',p=>{p.comparisons[0].statements.income_statement.rows[0].period.end='2024-02-31'}],
 ['unit',p=>{p.comparisons[0].statements.income_statement.rows[0].current!.unit!.numerator=['invented']}],
 ['complete claim',p=>{(p as unknown as Record<string,unknown>).complete_history=true}],
 ['restatement claim',p=>{(p.comparisons[0]as unknown as Record<string,unknown>).restatement_established=true}],
 ['policy',p=>{p.policy='All filings complete'}],
 ['extra keys',p=>{(p as unknown as Record<string,unknown>).invented=true}],
 ['cutoff order',p=>{p.entries.reverse()}],
 ['nested source integrity',p=>{p.entries[1].source!.facts[0].lexical_value='999'}],
 ['collection mismatch',p=>{p.collection_sha256='0'.repeat(64)}],
];
for(const [name,edit]of edits)test(`re-signed derived forgery rejected: ${name}`,async()=>{const p=structuredClone(base);edit(p);await assert.rejects(verifyStatementComparison(await resign(p),'AAPL','0000320193'))});
test('strict comparison lexemes reject duplicates, precision loss, negative zero and malformed UTF-8',async()=>{for(const text of ['{"a":1,"a":2}','{"a":9007199254740991.1}','{"a":1.00000000000000001}','{"a":9007199254740992}','{"a":1e309}','{"a":-0}','{"a":-0e5}','{"a":1e-1}'])assert.throws(()=>parseStatementComparisonJson(text));assert.deepEqual(parseStatementComparisonJson('{"a":1e2,"b":1.000}'),{a:100,b:1});await assert.rejects(readStatementComparisonJson(new Blob([new Uint8Array([0xff])])))});
test('comparison-specific 4 MiB allowance does not change legacy 256 KiB admission',async()=>{const text=JSON.stringify(Array.from({length:40},()=> 'x'.repeat(8000)));assert.ok(text.length>256*1024);assert.throws(()=>parseOfflineJson(text));assert.equal((parseStatementComparisonJson(text)as unknown[]).length,40);await assert.rejects(readStatementComparisonJson(new Blob([' '.repeat(MAX_COMPARISON_BYTES+1)])));await assert.rejects(readStatementComparison(new Blob([JSON.stringify(base)]),'AAPL',null));await assert.rejects(verifyStatementComparison(base,'MSFT','0000789019'))});
test('async local imports cannot install stale responses after newer request, issuer change or unmount',async()=>{for(const action of ['replace','identity','unmount']){const identity=JSON.stringify(['AAPL','0000320193']),gate=createSourceImportGuard(identity),request=gate.begin('accounting',identity)!;let release!:(b:ArrayBuffer)=>void;const blob=new Blob([JSON.stringify(base)]),bytes=await blob.arrayBuffer(),file={size:bytes.byteLength,arrayBuffer:()=>new Promise<ArrayBuffer>(resolve=>{release=resolve})};const pending=readStatementComparison(file as Blob,'AAPL','0000320193',request.signal);if(action==='replace')gate.begin('accounting',identity);if(action==='identity')gate.setIdentity(JSON.stringify(['MSFT','0000789019']));if(action==='unmount')gate.invalidate();release(bytes);await assert.rejects(pending);assert.equal(request.isCurrent(),false)}const packet:StatementComparisonPacket=await readStatementComparison(new Blob([JSON.stringify(base)]),'AAPL','0000320193');assert.equal(packet.sha256,base.sha256)});
