import {useEffect,useRef,useState} from 'react';
import {readOfflineJson,MAX_OFFLINE_BYTES} from './offlineJson';
import {verifySourceAccounting,verifyInlineAudit} from './financialSourceContract';
import type {SourceAccountingPacket,InlineAuditPacket} from './financialSourceContract';
import {createSourceImportGuard} from './sourceImportGuard';

type Kind='accounting'|'inline';
type Packet=SourceAccountingPacket|InlineAuditPacket;
type Slot={packet:Packet|null;busy:boolean;error:string};
const empty=():Slot=>({packet:null,busy:false,error:''});

/** The file path used by both controls always passes the strict byte reader first. */
export async function readSourceEvidence(kind:Kind,file:Blob,symbol:string,cik:string|null,signal?:AbortSignal):Promise<Packet>{
 if(!cik||!['accounting','inline'].includes(kind)||!file.size||file.size>MAX_OFFLINE_BYTES)throw Error('Unavailable identity or file size');
 const raw=await readOfflineJson(file,signal);
 const packet=await(kind==='accounting'?verifySourceAccounting(raw,symbol,cik):verifyInlineAudit(raw,symbol,cik));
 if(signal?.aborted)throw new DOMException('Offline import aborted','AbortError');
 return packet;
}

/** Each local import is independent. An identity change invalidates all pending work. */
export function SourceAccounting({symbol,cik}:{symbol:string;cik:string|null}){
 const identity=JSON.stringify([symbol,cik]);
 const guard=useRef<ReturnType<typeof createSourceImportGuard>|null>(null);
 const gate=guard.current??=createSourceImportGuard(identity);gate.setIdentity(identity);
 const [accounting,setAccounting]=useState<Slot>(empty),[inline,setInline]=useState<Slot>(empty);
 useEffect(()=>{setAccounting(empty());setInline(empty());return()=>gate.invalidate()},[symbol,cik,gate]);
 async function load(kind:Kind,file:File){
  const request=gate.begin(kind,identity);if(!request)return;
  const set=kind==='accounting'?setAccounting:setInline;set({packet:null,busy:true,error:''});
  const active=request.isCurrent;
  try{
   const packet=await readSourceEvidence(kind,file,symbol,cik,request.signal);
   if(active())set({packet,busy:false,error:''});
  }catch{if(active())set({packet:null,busy:false,error:kind==='accounting'?'Source-accounting export unavailable: issuer, cutoff, original source, relationships or integrity did not pass.':'Inline-source audit unavailable: issuer, cutoff, original set, immutable profiles or integrity did not pass.'})}
 }
 return <section aria-label="Original-source accounting and inline audit"><h4>Original-source accounting and inline audit</h4>
  <p>Open separately supplied private exports, up to 256 KiB each. Imports are read only and make no provider request. Caller-designated statement roles do not establish GAAP classifications. Missing and conflicting values remain unavailable.</p>
  {!cik&&<p role="status">An exact SEC issuer identity is required to admit these exports.</p>}
  <section aria-label="Private source-accounting import" aria-busy={accounting.busy}><label>Open source-accounting export<input type="file" accept="application/json,.json" disabled={!cik||accounting.busy} onChange={e=>{const file=e.target.files?.[0];e.target.value='';if(file)void load('accounting',file)}}/></label>
   <SourceImportFeedback kind="accounting" busy={accounting.busy} error={accounting.error}/>
   {accounting.packet?.schema==='gig.backend.company_source_accounting.v1'&&accounting.packet.instrument.symbol===symbol&&accounting.packet.instrument.cik===cik&&<SourceAccountingView packet={accounting.packet}/>}
  </section>
  <section aria-label="Private original-inline audit import" aria-busy={inline.busy}><label>Open original-inline audit export<input type="file" accept="application/json,.json" disabled={!cik||inline.busy} onChange={e=>{const file=e.target.files?.[0];e.target.value='';if(file)void load('inline',file)}}/></label>
   <SourceImportFeedback kind="inline" busy={inline.busy} error={inline.error}/>
   {inline.packet?.schema==='gig.backend.company_inline_source_audit.v1'&&inline.packet.instrument.symbol===symbol&&inline.packet.instrument.cik===cik&&<InlineAuditView packet={inline.packet}/>}
  </section>
 </section>;
}

export function SourceImportFeedback({kind,busy,error}:{kind:Kind;busy:boolean;error:string}){return <>{busy&&<p role="status">{kind==='accounting'?'Validating original-source accounting bindings…':'Validating inline-set receipts and source identities…'}</p>}{error&&<p role="alert">{error}</p>}</>}

function Confidence(){return <p>Source confidence: supplied original audit receipt. When a receipt is available, the backend reports reconstruction of supplied originals. This browser validates the export contract and source bindings; it does not validate original XML bytes or independently authenticate the issuer. Complete financial statements, complete history and full standards conformance are not established.</p>}
function Cutoff({packet}:{packet:{as_of:string;cutoff_ns:string;collection_sha256:string}}){return <><p>Exact acceptance cutoff: <time dateTime={packet.as_of}>{packet.as_of}</time> · nanoseconds <code>{packet.cutoff_ns}</code></p><p>Collection SHA-256: <code>{packet.collection_sha256}</code></p></>}
type Accounting=SourceAccountingPacket['accounting'];
type Statements=Accounting['statements'];
type Row=Statements[keyof Statements]['periods'][number]['rows'][number];

export function SourceAccountingView({packet}:{packet:SourceAccountingPacket}){
 const a=packet.accounting;
 return <section aria-label="Admitted source-accounting evidence"><h5>Source-accounting evidence · {packet.status}</h5><Confidence/><Cutoff packet={packet}/>
  <p role="status">{packet.reason??'Supported supplied-source accounting views'} · no missing values are filled and no contradictory reported fact is selected.</p>
  {a.source_filing&&<details><summary>Filing and original-source identities</summary><p>{a.source_filing.form} · filed {a.source_filing.filed} · accession {a.source_filing.accession}</p><p>Accepted {a.source_filing.accepted_at??'unavailable'} · received {a.source_filing.received_at??'unavailable'} · origin {a.source_filing.origin}</p><p>Original source SHA-256: <code>{a.source_filing.source_sha256}</code></p><p>Original parsed SHA-256: <code>{a.original_parsed_sha256??'unavailable'}</code></p><p>Admitted parsed SHA-256: <code>{a.admitted_parsed_sha256??'unavailable'}</code></p><p>Original DTS SHA-256: <code>{a.dts_sha256??'unavailable'}</code></p></details>}
  {a.lineage&&<details><summary>Explicit supplied amendment lineage · {a.lineage.status}</summary><p>Each supplied source remains separate. No additive amendment filling or complete-history claim.</p>{a.lineage.sources.map(s=><p key={s.source.accession}>{s.source.accession} · accepted {s.source.accepted_at??'unavailable'} · original <code>{s.source.source_sha256}</code> · admitted parsed <code>{s.parsed_sha256}</code></p>)}</details>}
  {Object.entries(a.statements).map(([kind,statement])=><section key={kind} aria-label={`${kind.replaceAll('_',' ')} source view`}><h6>{kind.replaceAll('_',' ')} · {statement.status}</h6><p>Caller-designated presentation role: {statement.presentation_role??'unavailable'} · accounting relationship role: {statement.accounting_role??'unavailable'}</p>{statement.reason&&<p role="status">{statement.reason}</p>}
   {statement.periods.map((period,index)=><section key={index} aria-label={`${kind.replaceAll('_',' ')} period ${index+1}`}><p><strong>Exact reported period: {period.start??'Instant'} → {period.end}</strong></p>
    <div role="region" aria-label={`${kind.replaceAll('_',' ')} source-accounting table ${index+1}`} tabIndex={0} style={{overflowX:'auto'}}><table><caption>Original source facts and explicit relationship classifications; incomplete statement</caption><thead><tr><th scope="col">Source concept</th><th scope="col">Reported value and status</th><th scope="col">Units and source evidence</th></tr></thead><tbody>{period.rows.map(row=><AccountingRow key={row.concept} row={row}/>)}</tbody></table></div>
    {period.calculations.length>0&&<details><summary>Exact source calculation intervals</summary><p>Diagnostics retain missing inputs and original aspects; they do not select reported values or certify accounting validity.</p>{period.calculations.map((check,i)=><div key={i}><p>{check.parent??'Network'} · {check.calculation?.status??check.status??'unavailable'}</p>{check.calculation&&<><p>Context <code>{check.context_sha256}</code> · unit <code>{check.unit_sha256}</code></p><ExactInterval label="Parent enclosure" interval={check.calculation.parent_interval}/><ExactInterval label="Weighted-sum enclosure" interval={check.calculation.weighted_sum_interval}/><ExactInterval label="Residual enclosure" interval={check.calculation.residual_interval}/></>}</div>)}</details>}
   </section>)}
  </section>)}
 </section>;
}

function AccountingRow({row}:{row:Row}){return <tr><th scope="row">{row.concept}</th><td><p>{row.status} · {row.value??'Value unavailable'}</p>{row.reason&&<p>{row.reason}</p>}<p>Source equivalence: {row.equivalence_status}</p><p>Source essence concept: {row.essence_concept??'unavailable'}</p></td><td>
 {row.unit?<p>{row.unit.numerator.join(' × ')}{row.unit.denominator.length?' / '+row.unit.denominator.join(' × '):''}</p>:<p>Projected unit unavailable</p>}
 <details><summary>Original declaration and relationship classification</summary><p>{row.classification.basis}</p><p>Declared type {row.classification.declared_type} · period type {row.classification.period_type} · balance {row.classification.balance??'unspecified'}</p><p>Accounting metric unavailable; no GAAP alias inferred.</p>{row.classification.declaration_documents.map(d=><p key={d.uri}>{d.uri} · <code>{d.sha256}</code></p>)}{row.accounting_relationships.map((r,i)=><div key={i}><p>{r.kind} · {r.role} · {r.from} → {r.to}</p>{r.provenance.map((arc,j)=><p key={j}>Original relationship source {arc.source_uri} · <code>{arc.source_sha256}</code></p>)}{r.checks.map((c,j)=><div key={j}><p>Source relationship check: {c.status}</p>{c.source_fact_ids.map(id=><p key={id}>Comparison source fact <code>{id}</code></p>)}{c.essence_facts?.map(f=><p key={f.source_fact_id}>Essence reported value {f.reported_value??'unavailable'} · lexical {f.lexical_value} · source fact <code>{f.source_fact_id}</code></p>)}{c.alias_facts?.map(f=><p key={f.source_fact_id}>Alias reported value {f.reported_value??'unavailable'} · lexical {f.lexical_value} · source fact <code>{f.source_fact_id}</code></p>)}</div>)}</div>)}</details>
 <details><summary>{row.facts.length} original reported fact reference(s)</summary>{row.facts.length===0&&<p>No reported source fact. Missing values remain unavailable.</p>}{row.facts.map(f=><p key={f.source_fact_id}><code>{f.source_fact_id}</code> · context {f.context_ref} · unit {f.unit_ref??'unavailable'} · lexical <span>{f.lexical_value||'(empty)'}</span> · nil {f.nil?'true':'false'} · decimals {f.decimals??'unspecified'} · precision {f.precision??'unspecified'} · context SHA <code>{f.context_sha256}</code> · unit SHA <code>{f.unit_sha256??'unavailable'}</code></p>)}{row.numeric_facts.map(f=><p key={f.source_fact_id}>Source numeric value {f.value??'unavailable'} · fact <code>{f.source_fact_id}</code> · original lexical {f.original_lexical_value}</p>)}</details>
 </td></tr>}

type Enclosure={lower:{numerator:string;denominator:string};upper:{numerator:string;denominator:string};lower_closed:boolean;upper_closed:boolean};
function ExactInterval({label,interval}:{label:string;interval:Enclosure|null}){return interval?<p>{label}: {interval.lower_closed?'[':'('}{interval.lower.numerator}/{interval.lower.denominator}, {interval.upper.numerator}/{interval.upper.denominator}{interval.upper_closed?']':')'} · exact rational endpoints</p>:<p>{label}: unavailable</p>}

export function InlineAuditView({packet}:{packet:InlineAuditPacket}){
 const r=packet.receipt;
 return <section aria-label="Admitted original-inline audit evidence"><h5>Original-inline audit evidence · {packet.status}</h5><Confidence/><Cutoff packet={packet}/><p role="status">{packet.reason??'Supplied original-source reconstruction receipt admitted'}</p>
 {packet.lineage&&<details><summary>Supplied filing lineage · {packet.lineage.status}</summary>{packet.lineage.sources.map(s=><p key={s.source.accession}>{s.source.form} · accession {s.source.accession} · accepted {s.source.accepted_at??'unavailable'} · filing source identity <code>{s.source.source_sha256}</code></p>)}<p>Sources remain separate; no complete-history or additive amendment claim.</p></details>}
 {r&&<><p>{r.status} · origin {r.origin}</p><p>Transformation profile: {r.transformation_profile??'Legacy default (no selected profile)'} · embedded profile: {r.embedded_profile??'Legacy default (no selected profile)'}</p>
 <details><summary>Original set, parse, DTS and receipt identities</summary><p>Document-set SHA-256: <code>{r.document_set_sha256}</code></p><p>Original parsed SHA-256: <code>{r.parsed_sha256}</code></p><p>Admitted parsed SHA-256: <code>{packet.admitted_parsed_sha256??'unavailable'}</code></p><p>Original DTS SHA-256: <code>{r.dts_sha256}</code></p><p>Audit receipt SHA-256: <code>{r.sha256}</code></p><p>Accepted acquisition-manifest SHA-256: <code>{r.acquisition_manifest_sha256??'unavailable'}</code></p><p>{r.acquisition_manifest_sha256?'Authored acquisition order is bound to the separately retained accepted manifest identity.':'No accepted acquisition-order claim supplied. Supplied input order alone is not accepted acquisition intent.'}</p></details>
 <details><summary>Original document ordering</summary><p>Supplied audit input order is recorded separately from canonical parsed order.</p><ol aria-label="Supplied original document order">{r.supplied_document_order.map(u=><li key={u}>{u}</li>)}</ol><p>Canonical parsed URI order; original facts and continuation segments retain their source references.</p><ol aria-label="Canonical parsed document order">{r.parsed_document_order.map(u=><li key={u}>{u}</li>)}</ol></details>
 <div role="region" aria-label="Inline original receipt table" tabIndex={0} style={{overflowX:'auto'}}><table><caption>Every original document receipt; hashes establish supplied-byte identity, not issuer authentication</caption><thead><tr><th scope="col">Original URI and hash</th><th scope="col">Accepted and received</th><th scope="col">Processing-reference digest</th></tr></thead><tbody>{r.inline_documents.map(d=><tr key={d.uri}><th scope="row">{d.uri}<p><code>{d.source_sha256}</code></p></th><td><p>Accepted {d.accepted_at??'unavailable'}</p><p>Received {d.received_at??'unavailable'}</p></td><td><code>{d.permission_reference_sha256??'No processing reference (authored source)'}</code></td></tr>)}</tbody></table></div>
 <details><summary>Taxonomy originals and source references</summary>{r.taxonomy_documents.map(d=><p key={d.uri}>{d.uri} · <code>{d.sha256}</code></p>)}<p>{r.source_fact_ids.length} original fact reference(s); no facts synthesized.</p>{r.source_fact_ids.map(id=><p key={id}>Fact <code>{id}</code></p>)}{Object.entries(r.source_context_sha256s).map(([id,sha])=><p key={id}>Context {id} · <code>{sha}</code></p>)}{Object.entries(r.source_unit_sha256s).map(([id,sha])=><p key={id}>Unit {id} · <code>{sha}</code></p>)}</details>
 {r.limitations.map(limit=><p key={limit}>{limit}</p>)}</>}
 </section>;
}
