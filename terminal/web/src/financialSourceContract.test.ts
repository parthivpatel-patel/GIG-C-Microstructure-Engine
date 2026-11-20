import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {parseOfflineJson} from './offlineJson.ts';
import {verifySourceAccounting,verifyInlineAudit} from './financialSourceContract.ts';

type Packet=Record<string,any>;
const generated=JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON||'python3',[fileURLToPath(new URL('../../tests/source_accounting_ui_fixtures.py',import.meta.url))],{encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024})) as {accounting:[string,Packet][];inline:[string,Packet][]};
const accounting=new Map(generated.accounting),inline=new Map(generated.inline);
const edgeExports=JSON.parse(execFileSync(process.env.GIG_TEST_PYTHON||'python3',[fileURLToPath(new URL('../../tests/source_accounting_checks_fixtures.py',import.meta.url))],{encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024})) as [string,Packet][];
for(const [name,p]of edgeExports)test(`full strict admission of actual Python source-check edge export: ${name}`,async()=>{const admitted=await verifySourceAccounting(parseOfflineJson(JSON.stringify(p)),'AAPL','0000320193');assert.equal(admitted.sha256,p.sha256)});
const clone=(kind:'accounting'|'inline',name:string):Packet=>structuredClone((kind==='accounting'?accounting:inline).get(name)!);
function canonical(v:any):string{if(v===null||typeof v!=='object')return JSON.stringify(v);if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}'}
const digest=(v:any)=>createHash('sha256').update(canonical(v)).digest('hex');
function replace(root:any,old:string,next:string){if(!root||typeof root!=='object'||old===next)return;for(const k of Object.keys(root)){if(root[k]===old)root[k]=next;else replace(root[k],old,next)}}
function refresh(root:Packet,obj:Packet|null|undefined,key='sha256'){if(!obj)return;const body={...obj};delete body[key];const next=digest(body),old=obj[key];obj[key]=next;if(typeof old==='string')replace(root,old,next)}
/** Recompute every affected artifact identity, so rejection cannot rely on stale wrappers. */
function seal(p:Packet){if(p.dts){refresh(p,p.dts.effective_relationships);refresh(p,p.dts,'canonical_sha256')}if(p.source)refresh(p,p.source,'canonical_sha256');if(p.accounting){const a=p.accounting;refresh(p,a.accounting_report?.source_audit);refresh(p,a.accounting_report);refresh(p,a.lineage);refresh(p,a)}else{refresh(p,p.receipt);refresh(p,p.lineage)}refresh(p,p);return p}
const strict=(p:Packet)=>parseOfflineJson(JSON.stringify(p));
const rows=(p:Packet):Packet[]=>Object.values(p.accounting.statements).flatMap((section:any)=>section.periods.flatMap((period:any)=>period.rows));
const periods=(p:Packet):Packet[]=>Object.values(p.accounting.statements).flatMap((section:any)=>section.periods);
const alias=(p:Packet)=>rows(p).find(r=>r.accounting_relationships.length)!;
const calc=(p:Packet)=>periods(p).find(per=>per.calculations.length)!.calculations[0];
const checks=(p:Packet)=>[...p.accounting.accounting_report.networks.flatMap((n:any)=>n.arcs.flatMap((a:any)=>a.checks)),...rows(p).flatMap(r=>r.accounting_relationships.flatMap((a:any)=>a.checks))];
async function rejected(kind:'accounting'|'inline',name:string,mutate:(p:Packet)=>void){const p=clone(kind,name);mutate(p);seal(p);await assert.rejects(kind==='accounting'?verifySourceAccounting(strict(p),'AAPL','0000320193'):verifyInlineAudit(strict(p),'AAPL','0000320193'))}

for(const [name,p]of generated.accounting)test(`full strict admission of actual Python accounting export: ${name}`,async()=>{const admitted=await verifySourceAccounting(strict(p),'AAPL','0000320193');assert.equal(admitted.sha256,p.sha256)});
for(const [name,p]of generated.inline)test(`full strict admission of actual Python inline export: ${name}`,async()=>{const admitted=await verifyInlineAudit(strict(p),'AAPL','0000320193');assert.equal(admitted.sha256,p.sha256)});

test('rehash helper retains every unmodified valid Python export',async()=>{for(const [kind,entries]of [['accounting',generated.accounting],['inline',generated.inline]]as const)for(const [name,original]of entries){const packet=seal(clone(kind,name));assert.deepEqual(packet,original);await(kind==='accounting'?verifySourceAccounting(strict(packet),'AAPL','0000320193'):verifyInlineAudit(strict(packet),'AAPL','0000320193'))}});

const accountingAttacks:[string,string,(p:Packet)=>void][]=[
 ['reported','fabricated supported row amount',p=>{rows(p)[0].value='999999'}],
 ['reported','fabricated source numeric amount',p=>{rows(p)[0].numeric_facts[0].value='999999'}],
 ['reported','duplicate statement row identity',p=>{const per=periods(p)[0];per.rows.push(structuredClone(per.rows[0]))}],
 ['reported','missing required presentation row',p=>{periods(p)[0].rows.pop()}],
 ['reported','missing bound calculation network result',p=>{periods(p)[0].calculations=[]}],
 ['reported','duplicate calculation binding',p=>{const per=periods(p)[0];per.calculations.push(structuredClone(per.calculations[0]))}],
 ['reported','unsupported accounting alias inference',p=>{rows(p)[0].classification.accounting_metric='net_income'}],
 ['reported','false declaration source digest',p=>{rows(p)[0].classification.declaration_documents[0].sha256='0'.repeat(64)}],
 ['reported','foreign row unit',p=>{rows(p)[0].unit.numerator=['{http://www.xbrl.org/2003/iso4217}EUR']}],
 ['reported','changed accounting source provenance',p=>{p.accounting.accounting_report.networks[0].arcs[0].provenance[0].source_sha256='0'.repeat(64)}],
 ['reported','invented source accounting network role',p=>{const r=p.accounting.accounting_report.networks[0],old=r.role;r.role='urn:invented:accounting';for(const section of Object.values(p.accounting.statements)as any[])if(section.accounting_role===old)section.accounting_role=r.role;for(const row of rows(p))for(const relation of row.accounting_relationships)if(relation.role===old)relation.role=r.role}],
 ['reported','reported equality promoted to standards equality',p=>{for(const c of checks(p))c.standards_value_equality_established=true;alias(p).equivalence_status='SOURCE_EQUIVALENCE_VERIFIED'}],
 ['conflicting','conflicting values relabelled equal',p=>{for(const c of checks(p)){c.status='SUPPORTED_EQUAL';c.standards_value_equality_established=false}const row=alias(p);row.equivalence_status='SOURCE_RELATIONSHIP_REPORTED_EQUAL';row.status='SUPPORTED';row.reason=null;row.value=row.numeric_facts[0].value;row.unit=structuredClone(p.source.units[row.facts[0].unit_ref])}],
 ['missing','missing alias manufactured from essence',p=>{const row=alias(p);row.status='SUPPORTED';row.value='100';row.unit=structuredClone(p.source.units.USD)}],
 ['reported','calculation parent interval tamper',p=>{calc(p).calculation.parent_interval.lower.numerator='1998'}],
 ['reported','calculation residual interval tamper',p=>{calc(p).calculation.residual_interval.upper.numerator='9000'}],
 ['reported','calculation weighted interval tamper',p=>{calc(p).calculation.terms[0].weighted_interval.upper.numerator='9000'}],
 ['reported','calculation term weight tamper',p=>{calc(p).calculation.terms[0].weight.numerator='-1'}],
 ['reported','calculation source IDs removed',p=>{calc(p).calculation.source_fact_ids=[]}],
 ['reported','calculation profile invented',p=>{calc(p).calculation.profile='APPROXIMATE_UNBOUNDED'}],
 ['reported','calculation source relation digest tamper',p=>{calc(p).relationship_provenance[0][0].source_sha256='0'.repeat(64)}],
 ['reported','source audit hash mismatch',p=>{p.accounting.accounting_report.source_audit.source_sha256='0'.repeat(64)}],
 ['reported','source issuer mismatch despite new artifact hash',p=>{p.source.source.issuer_cik='0000000001'}],
 ['reported','invalid source filing calendar date',p=>{const old=p.source.source.filed;replace(p,old,'2024-02-30')}],
 ['reported','invalid statement calendar period',p=>{periods(p)[0].end='2023-02-30'}],
 ['reported','invalid source context calendar period with fresh semantic hash',p=>{const c=p.source.contexts.I,old=c.semantic_sha256;c.period.end='2023-02-30';const semantic={issuer_cik:c.issuer_cik,period:c.period,dimensions:c.dimensions,opaque_segment:c.opaque_segment};c.semantic_sha256=digest(semantic);replace(p,old,c.semantic_sha256)}],
 ['reported','contradictory original unit semantic hash',p=>{p.source.units.USD.numerator=['{http://www.xbrl.org/2003/iso4217}EUR']}],
 ['reported','duplicate original source fact identity',p=>{p.source.facts.push(structuredClone(p.source.facts[0]))}],
 ['amended_vintage','amendment ancestry removed',p=>{p.accounting.lineage.sources.pop()}],
 ['amended_vintage','amendment source duplicated',p=>{p.accounting.lineage.sources.push(structuredClone(p.accounting.lineage.sources[0]))}],
 ['reported','acceptance cutoff precedes selected filing',p=>{replace(p,p.as_of,'2024-01-01T00:00:00Z');replace(p,p.cutoff_ns,'1704067200000000000')}],
 ['reported','future filed date cannot precede acceptance cutoff',p=>{replace(p,p.source.source.filed,'2025-01-01')}],
 ['reported','calculation entity lexical cannot cross-bind',p=>{calc(p).identifier_lexical='320193'}],
 ['reported','calculation context cannot cross-bind',p=>{calc(p).context_sha256=p.source.contexts.FD.semantic_sha256}],
 ['reported','calculation unit cannot cross-bind',p=>{calc(p).unit_sha256='0'.repeat(64)}],
 ['reported','dropped entire presentation period',p=>{p.accounting.statements.balance_sheet.periods=[]}],
 ['reported','duplicate presentation period',p=>{const section=p.accounting.statements.balance_sheet;section.periods.push(structuredClone(section.periods[0]))}],
 ['reported','row order diverges from presentation network',p=>{periods(p)[0].rows.reverse()}],
 ['amended_vintage','explicit amendment link changed',p=>{p.accounting.lineage.links[0].amends_accession='0000000123-24-999999'}],
 ['reported','source confidence claims issuer authentication',p=>{p.source_confidence.independent_issuer_authentication=true}],
];
for(const [name,label,mutate]of accountingAttacks)test(`rehashed accounting forgery rejects: ${label}`,()=>rejected('accounting',name,mutate));

const inlineAttacks:[string,(p:Packet)=>void][]=[
 ['unsupported transformation profile',p=>{p.receipt.transformation_profile='REGISTRY_2015_NUMERIC_V999'}],
 ['unsupported embedded profile',p=>{p.receipt.embedded_profile='SCHEMA_APPINFO_LINKBASE_V999'}],
 ['unsupported original audit profile',p=>{p.receipt.profile='CLAIMED_COMPLETE_INLINE_V1'}],
 ['changed parsed source binding',p=>{p.receipt.parsed_sha256='0'.repeat(64)}],
 ['changed original document-set binding',p=>{p.receipt.document_set_sha256='0'.repeat(64)}],
 ['duplicate original document identity',p=>{p.receipt.inline_documents[1]=structuredClone(p.receipt.inline_documents[0])}],
 ['duplicate supplied document order',p=>{p.receipt.supplied_document_order[1]=p.receipt.supplied_document_order[0]}],
 ['changed canonical parsed document order',p=>{p.receipt.parsed_document_order.reverse()}],
 ['missing advertised original member',p=>{p.receipt.inline_documents.pop()}],
 ['unsafe original document URI',p=>{p.receipt.inline_documents[0].uri='file:///tmp/not-an-original'}],
 ['invalid original document hash',p=>{p.receipt.inline_documents[0].source_sha256='invalid'}],
 ['duplicate source fact identity',p=>{p.receipt.source_fact_ids.push(p.receipt.source_fact_ids[0])}],
 ['invalid context source digest',p=>{p.receipt.source_context_sha256s.I='invalid'}],
 ['duplicate taxonomy identity',p=>{p.receipt.taxonomy_documents.push(structuredClone(p.receipt.taxonomy_documents[0]))}],
 ['document acceptance inconsistent with filing',p=>{p.receipt.inline_documents[0].accepted_at='2024-01-01T00:00:00Z'}],
 ['claimed independent authentication',p=>{p.receipt.independent_source_authentication=true}],
 ['live-provider request claim',p=>{p.receipt.provider_requested=true}],
];
for(const [label,mutate]of inlineAttacks)test(`rehashed inline forgery rejects: ${label}`,()=>rejected('inline','legacy',mutate));

for(const numeric of ['1.00000000000000001','9007199254740993','1e-1','-0'])test(`strict lexical JSON rejects ${numeric} before Number conversion`,()=>{const p=JSON.stringify(accounting.get('reported'));assert.throws(()=>parseOfflineJson(p.replace('"read_only":true',`"read_only":true,"untrusted":${numeric}`)))});
test('strict JSON rejects duplicate source-sensitive keys before full verification',()=>{const p=JSON.stringify(accounting.get('reported'));assert.throws(()=>parseOfflineJson(p.replace('"read_only":true','"read_only":true,"read_only":false')))});

test('exact integral exponent and decimal metadata remain legitimate JSON tokens',()=>{assert.deepEqual(parseOfflineJson('{\"a\":1e0,\"b\":10e-1,\"c\":1.00}'),{a:1,b:1,c:1})});
