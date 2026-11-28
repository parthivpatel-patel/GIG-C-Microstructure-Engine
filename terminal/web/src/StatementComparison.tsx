import {useEffect,useRef,useState} from 'react';
import {createSourceImportGuard} from './sourceImportGuard';
import {MAX_COMPARISON_BYTES,readStatementComparisonJson,verifyStatementComparison} from './statementComparisonContract';
import type {ComparisonRow,StatementComparisonPacket} from './statementComparisonContract';
export async function readStatementComparison(file:Blob,symbol:string,cik:string|null,signal?:AbortSignal){if(!cik||file.size<1||file.size>MAX_COMPARISON_BYTES)throw Error('Unavailable issuer or comparison size');const packet=await verifyStatementComparison(await readStatementComparisonJson(file,signal),symbol,cik);if(signal?.aborted)throw new DOMException('Offline import aborted','AbortError');return packet}
export function StatementComparison({symbol,cik}:{symbol:string;cik:string|null}){
 const identity=JSON.stringify([symbol,cik]),ref=useRef<ReturnType<typeof createSourceImportGuard>|null>(null),gate=ref.current??=createSourceImportGuard(identity);gate.setIdentity(identity);
 const [state,setState]=useState<{packet:StatementComparisonPacket|null;busy:boolean;error:string}>({packet:null,busy:false,error:''});
 useEffect(()=>{setState({packet:null,busy:false,error:''});return()=>gate.invalidate()},[symbol,cik,gate]);
 async function load(file:File){const request=gate.begin('accounting',identity);if(!request)return;setState({packet:null,busy:true,error:''});try{const packet=await readStatementComparison(file,symbol,cik,request.signal);if(request.isCurrent())setState({packet,busy:false,error:''})}catch{if(request.isCurrent())setState({packet:null,busy:false,error:'Statement comparison unavailable: issuer, acceptance cutoffs, source packets, derived relationships or integrity did not pass.'})}}
 return <section aria-label="Private statement-vintage comparison import" aria-busy={state.busy}><h5>Compare supplied statement vintages</h5><p>Open a separately generated original-source comparison export, up to 4 MiB. Read only; no provider request. Each exact acceptance cutoff retains its own selected filing. Missing or incompatible rows remain unavailable.</p><label>Open statement-vintage comparison export<input type="file" accept="application/json,.json" disabled={!cik||state.busy} onChange={e=>{const file=e.target.files?.[0];e.target.value='';if(file)void load(file)}}/></label>{!cik&&<p role="status">An exact SEC issuer identity is required to compare supplied vintages.</p>}{state.busy&&<p role="status">Validating adjacent vintages and original-source relationships…</p>}{state.error&&<p role="alert">{state.error}</p>}{state.packet?.instrument.symbol===symbol&&state.packet.instrument.cik===cik&&<StatementComparisonView packet={state.packet}/>}</section>
}
export function StatementComparisonView({packet}:{packet:StatementComparisonPacket}){
 return <ComparisonPeriods key={packet.sha256} packet={packet}/>;
}

function ComparisonPeriods({packet}:{packet:StatementComparisonPacket}){
 const [index,setIndex]=useState(0);
 const comparison=packet.comparisons[index];
 return <section aria-label="Admitted statement-vintage comparison">
  <p>Reported values are compared only when their original aspects and relationships agree. Missing values remain unavailable.</p>
  <p>Collection SHA-256 <code>{packet.collection_sha256}</code> · comparison SHA-256 <code>{packet.sha256}</code></p>
  <ol aria-label="Exact supplied acceptance cutoffs">{packet.entries.map(entry=><li key={entry.cutoff_ns}>
   <time dateTime={entry.as_of}>{entry.as_of}</time> · cutoff ns <code>{entry.cutoff_ns}</code> · {entry.status}
   {' · accession '}{entry.accounting.source_filing?.accession??'unavailable'} · {entry.accounting.source_filing?.origin??'unavailable'}
   {' · source packet '}<code>{entry.sha256}</code>
  </li>)}</ol>
  {packet.comparisons.length>1&&<label>Adjacent cutoff pair<select value={index} onChange={e=>setIndex(Number(e.target.value))}>
   {packet.comparisons.map((entry,i)=><option key={i} value={i}>
    {packet.entries[entry.previous_entry_index].as_of} → {packet.entries[entry.current_entry_index].as_of}
   </option>)}
  </select></label>}
  {comparison&&<section aria-label="Selected adjacent filing vintages">
   <h6>Cutoff {comparison.previous_entry_index+1} → {comparison.current_entry_index+1} · {comparison.source_relation}</h6>
   {Object.entries(comparison.statements).map(([kind,statement])=>
    <ComparisonTable key={index+':'+kind} label={kind.replaceAll('_',' ')} statement={statement}/>)}
  </section>}
 </section>;
}

type Statement=StatementComparisonPacket['comparisons'][number]['statements'][string];
const PAGE=32;
function ComparisonTable({label,statement}:{label:string;statement:Statement}){
 const [offset,setOffset]=useState(0);
 const {rows}=statement;
 return <section aria-label={label+' vintage comparison'}>
  <h6>{label} · {statement.status}</h6>
  <p>Previous {statement.previous_status??'unavailable'} · {statement.previous_reason??'no diagnostic'}. Current {statement.current_status??'unavailable'} · {statement.current_reason??'no diagnostic'}.</p>
  <details><summary>Exact role bindings</summary>
   <p>Previous {statement.previous_role_binding?.presentation_role??'unavailable'} / {statement.previous_role_binding?.accounting_role??'unavailable'}</p>
   <p>Current {statement.current_role_binding?.presentation_role??'unavailable'} / {statement.current_role_binding?.accounting_role??'unavailable'}</p>
  </details>
  {!!rows.length&&<>
   <div role="region" aria-label={label+' adjacent source comparison table'} tabIndex={0} className="atlas-table-scroll">
    <table>
     <caption>Exact source concepts and reported periods</caption>
     <thead><tr><th scope="col">Source concept and period</th><th scope="col">Comparison status</th>
      <th scope="col">Previous source row</th><th scope="col">Current source row</th></tr></thead>
     <tbody>{rows.slice(offset,offset+PAGE).map(row=>
      <tr key={JSON.stringify([row.concept,row.period.start,row.period.end])}>
       <th scope="row">{row.concept}<p>{row.period.start??'Instant'} → {row.period.end}</p></th>
       <td>{row.status}<p>Reported values comparable {row.reported_values_comparable?'yes':'no'}</p>
        <p>Previous calculation {row.previous_calculations.map(c=>c.calculation?.status??c.status).join(', ')||'unavailable'}</p>
        <p>Current calculation {row.current_calculations.map(c=>c.calculation?.status??c.status).join(', ')||'unavailable'}</p>
       </td>
       <td><SourceSide side={row.previous}/></td><td><SourceSide side={row.current}/></td>
      </tr>)}</tbody>
    </table>
   </div>
   {rows.length>PAGE&&<div className="inline-controls" role="group" aria-label={label+' comparison pages'}>
    <button disabled={offset===0} onClick={()=>setOffset(offset-PAGE)}>Previous rows</button>
    <span role="status">{offset+1}–{Math.min(offset+PAGE,rows.length)} of {rows.length} rows</span>
    <button disabled={offset+PAGE>=rows.length} onClick={()=>setOffset(offset+PAGE)}>Next rows</button>
   </div>}
  </>}
 </section>;
}

function SourceSide({side}:{side:ComparisonRow['previous']}){
 if(!side)return <p>Row unavailable in this source view.</p>;
 return <>
  <p>{side.status} · {side.reported_value??'Value unavailable'}</p>{side.reason&&<p>{side.reason}</p>}
  <p>Unit {side.unit?side.unit.numerator.join(' × ')+(side.unit.denominator.length?' / '+side.unit.denominator.join(' × '):''):'unavailable'}</p>
  <details><summary>Exact source provenance</summary>
   <p>Accession {side.accession} · source <code>{side.source_sha256}</code></p>
   <p>Source packet <code>{side.source_packet_sha256}</code> · row <code>{side.row_sha256}</code></p>
   <p>Original parsed <code>{side.original_parsed_sha256}</code> · DTS <code>{side.dts_sha256}</code></p>
   <p>Equivalence {side.equivalence_status} · source essence {side.essence_concept??'unavailable'}</p>
   {side.source_facts.map(f=><p key={f.source_fact_id}>Fact <code>{f.source_fact_id}</code> · lexical {f.lexical_value}
    {' · context '}<code>{f.context_sha256}</code> · unit <code>{f.unit_sha256??'unavailable'}</code></p>)}
  </details>
 </>;
}
