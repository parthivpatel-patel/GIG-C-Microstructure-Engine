import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import ts from 'typescript';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {createSourceImportGuard} from './sourceImportGuard.ts';
import {parseOfflineJson} from './offlineJson.ts';
import {verifySourceAccounting,verifyInlineAudit} from './financialSourceContract.ts';
const source=new URL('./SourceAccounting.tsx',import.meta.url);
const jsx=ts.transpileModule(readFileSync(source,'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const compiled=jsx.replace(/from (["'])([^"']+)\1/g,(_,_q:string,name:string)=>`from ${JSON.stringify(import.meta.resolve(name.startsWith('.')&&!name.endsWith('.ts')?name+'.ts':name))}`);
const {SourceAccounting,SourceAccountingView,InlineAuditView,SourceImportFeedback,readSourceEvidence}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
const generated=JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON||'python3',[fileURLToPath(new URL('../../tests/source_accounting_ui_fixtures.py',import.meta.url))],{encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024})) as {accounting:[string,unknown][];inline:[string,unknown][]};

test('actual offline panel names both file controls and leaves financial data absent until admission',()=>{
 const html=renderToStaticMarkup(createElement(SourceAccounting,{symbol:'AAPL',cik:'0000320193'}));
 assert.match(html,/aria-label="Original-source accounting and inline audit"/);assert.match(html,/Open source-accounting export/);assert.match(html,/Open original-inline audit export/);
 assert.equal((html.match(/type="file"/g)||[]).length,2);assert.equal((html.match(/aria-busy="false"/g)||[]).length,2);assert.match(html,/256 KiB/);assert.match(html,/read only and make no provider request/);assert.match(html,/Missing and conflicting values remain unavailable/);assert.doesNotMatch(html,/<table|type="submit"|href="https?:/);
});
test('unknown CIK disables both local admission controls with an announced explanation',()=>{
 const html=renderToStaticMarkup(createElement(SourceAccounting,{symbol:'UNKNOWN',cik:null}));assert.equal((html.match(/disabled=""/g)||[]).length,2);assert.match(html,/role="status">An exact SEC issuer identity/);assert.doesNotMatch(html,/<table/);
});
test('actual import feedback announces progress and escaped validation errors',()=>{
 for(const kind of ['accounting','inline']){
  const busy=renderToStaticMarkup(createElement(SourceImportFeedback,{kind,busy:true,error:''}));assert.match(busy,/role="status">Validating/);assert.doesNotMatch(busy,/role="alert"/);
  const failed=renderToStaticMarkup(createElement(SourceImportFeedback,{kind,busy:false,error:'Invalid <source> & cutoff'}));assert.match(failed,/role="alert"/);assert.match(failed,/Invalid &lt;source&gt; &amp; cutoff/);assert.doesNotMatch(failed,/<source>/);
 }
});
test('a second import invalidates only its own in-flight channel',()=>{
 const gate=createSourceImportGuard('AAPL:0000320193'),first=gate.begin('accounting','AAPL:0000320193')!,audit=gate.begin('inline','AAPL:0000320193')!;
 const second=gate.begin('accounting','AAPL:0000320193')!;assert.equal(first.isCurrent(),false);assert.equal(first.signal.aborted,true);assert.equal(second.isCurrent(),true);assert.equal(audit.isCurrent(),true);assert.equal(audit.signal.aborted,false);
});
test('changed symbol or CIK rejects late reads and stale event callbacks on both channels',async()=>{
 for(const next of ['MSFT:0000789019','AAPL:0000000001','AAPL:null']){
  const gate=createSourceImportGuard('AAPL:0000320193'),old=gate.begin('accounting','AAPL:0000320193')!,audit=gate.begin('inline','AAPL:0000320193')!;
  let complete!:()=>void,installed=false;const delayed=new Promise<void>(resolve=>{complete=resolve}).then(()=>{if(old.isCurrent())installed=true});
  gate.setIdentity(next);complete();await delayed;assert.equal(installed,false);assert.equal(old.signal.aborted,true);assert.equal(audit.isCurrent(),false);assert.equal(audit.signal.aborted,true);assert.equal(gate.begin('accounting','AAPL:0000320193'),null);assert.equal(gate.begin('accounting',next)!.isCurrent(),true);
 }
});
test('unmount invalidation prevents delayed installation while an effect replay can begin again',()=>{
 const gate=createSourceImportGuard('AAPL'),request=gate.begin('accounting','AAPL')!;gate.invalidate();assert.equal(request.isCurrent(),false);assert.equal(request.signal.aborted,true);gate.setIdentity('AAPL');assert.equal(gate.begin('inline','AAPL')!.isCurrent(),true);
});

for(const [name,raw]of generated.accounting)test(`actual backend source-accounting export renders only after strict semantic admission: ${name}`,async()=>{
 const packet=await verifySourceAccounting(parseOfflineJson(JSON.stringify(raw)),'AAPL','0000320193');
 const html=renderToStaticMarkup(createElement(SourceAccountingView,{packet}));
 assert.match(html,/aria-label="Admitted source-accounting evidence"/);assert.ok(html.includes(packet.as_of));assert.ok(html.includes(packet.cutoff_ns));assert.ok(html.includes(packet.collection_sha256));
 assert.match(html,/does not validate original XML bytes or independently authenticate the issuer/);assert.match(html,/no contradictory reported fact is selected/);assert.doesNotMatch(html,/<script|<iframe|href="https?:/);
 for(const [kind,section]of Object.entries(packet.accounting.statements)){
  assert.ok(html.includes(kind.replaceAll('_',' ')));if(section.presentation_role)assert.ok(html.includes(section.presentation_role));
  for(const period of section.periods){assert.ok(html.includes(period.end));for(const row of period.rows){assert.ok(html.includes(row.concept));assert.ok(html.includes(row.status));assert.ok(html.includes(row.equivalence_status));for(const fact of row.facts)assert.ok(html.includes(fact.source_fact_id));for(const relation of row.accounting_relationships)for(const arc of relation.provenance)assert.ok(html.includes(arc.source_sha256))}}
 }
 if(name==='reported'){assert.match(html,/SOURCE_RELATIONSHIP_REPORTED_EQUAL/);assert.match(html,/Parent enclosure: \[199\/2, 201\/2\]/);assert.match(html,/scope="col"/);assert.match(html,/scope="row"/);assert.match(html,/role="region"[^>]*tabindex="0"/);assert.match(html,/Accounting metric unavailable; no GAAP alias inferred/)}
 if(name==='exact')assert.match(html,/SOURCE_EQUIVALENCE_VERIFIED/);
 if(name==='conflicting'){assert.match(html,/CONFLICTING · Value unavailable/);assert.match(html,/Source numeric value 101/);assert.match(html,/Essence reported value 100/);assert.match(html,/Alias reported value 101/);assert.match(html,/lexical <span>101/)}
 if(name==='missing'||name==='amended_vintage')assert.match(html,/No reported source fact. Missing values remain unavailable/);
 if(name==='amended_vintage'){assert.match(html,/0000000123-24-000002/);assert.match(html,/0000000123-24-000001/);assert.match(html,/No additive amendment filling/)}
 if(name==='unsupported')assert.match(html,/UNSUPPORTED · Value unavailable/);
 if(name==='partial')assert.match(html,/PRESENTATION_ROLE_NOT_DESIGNATED/);
 if(name==='before_acceptance'||name==='no_collection'){assert.doesNotMatch(html,/<table/);assert.match(html,/UNAVAILABLE/)}
});
for(const [name,raw]of generated.inline)test(`actual backend original-inline receipt preserves source/profile/order disclosures: ${name}`,async()=>{
 const packet=await verifyInlineAudit(parseOfflineJson(JSON.stringify(raw)),'AAPL','0000320193');
 const html=renderToStaticMarkup(createElement(InlineAuditView,{packet}));assert.match(html,/aria-label="Admitted original-inline audit evidence"/);assert.ok(html.includes(packet.as_of));assert.ok(html.includes(packet.cutoff_ns));assert.match(html,/does not validate original XML bytes or independently authenticate the issuer/);assert.doesNotMatch(html,/authored-private-reference|<script|<iframe/);
 if(packet.receipt){const r=packet.receipt;for(const hash of [r.parsed_sha256,r.dts_sha256,r.document_set_sha256,r.sha256])assert.ok(html.includes(hash));for(const doc of r.inline_documents){assert.ok(html.includes(doc.uri));assert.ok(html.includes(doc.source_sha256));assert.ok(html.includes(doc.received_at!))}assert.match(html,/aria-label="Supplied original document order"/);assert.match(html,/aria-label="Canonical parsed document order"/);assert.match(html,/scope="row"/);assert.match(html,/tabindex="0"/);assert.match(html,/not issuer authentication/);if(name==='transformed')assert.match(html,/REGISTRY_2015_NUMERIC_V2/);if(name==='without_acquisition')assert.match(html,/No accepted acquisition-order claim supplied/);else assert.ok(html.includes(r.acquisition_manifest_sha256!));if(name==='permission_receipts')for(const d of r.inline_documents)assert.ok(html.includes(d.permission_reference_sha256!))}
 else {assert.doesNotMatch(html,/<table/);assert.match(html,/UNAVAILABLE/)}
});
test('actual local-file path rejects ambiguous bytes, oversized files, absent identity and cancellation',async()=>{
 for(const text of ['', '{"schema":"a","schema":"b"}', '{"number":9007199254740993}', '{"value":-0}'])await assert.rejects(readSourceEvidence('accounting',new Blob([text]),'AAPL','0000320193'));
 await assert.rejects(readSourceEvidence('inline',new Blob([new Uint8Array([0xff])]),'AAPL','0000320193'));
 await assert.rejects(readSourceEvidence('accounting',new Blob([' '.repeat(256*1024+1)]),'AAPL','0000320193'));
 await assert.rejects(readSourceEvidence('inline',new Blob(['{}']),'AAPL',null));
 const controller=new AbortController();controller.abort();await assert.rejects(readSourceEvidence('accounting',new Blob([JSON.stringify(generated.accounting[0][1])]),'AAPL','0000320193',controller.signal));
 for(const [kind,raw]of [['accounting',generated.accounting[0][1]],['inline',generated.inline[0][1]]]as const){const p=await readSourceEvidence(kind,new Blob([JSON.stringify(raw)]),'AAPL','0000320193');assert.equal(p.instrument.symbol,'AAPL');assert.equal(p.instrument.cik,'0000320193')}
});
test('the UI admission boundary refuses cross-symbol and cross-CIK packets',async()=>{
 await assert.rejects(verifySourceAccounting(generated.accounting[0][1],'MSFT','0000789019'));await assert.rejects(verifySourceAccounting(generated.accounting[0][1],'AAPL','0000000001'));await assert.rejects(verifyInlineAudit(generated.inline[0][1],'MSFT','0000789019'));await assert.rejects(verifyInlineAudit(generated.inline[0][1],'AAPL',null));
});
