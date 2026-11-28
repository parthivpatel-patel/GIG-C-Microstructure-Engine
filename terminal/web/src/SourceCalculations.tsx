import {useEffect,useRef,useState} from 'react';
import {readOfflineJson} from './offlineJson';
import {verifyCalculationPacket} from './xbrlCalculationReport';
import type {CalculationPacket} from './xbrlCalculationReport';

type Report=NonNullable<CalculationPacket['report']>;
type Binding=Report['bindings'][number];
type Interval=NonNullable<Binding['calculation']['parent_interval']>;

function exactInterval(value:Interval|null){
 if(!value)return 'Unavailable';
 const fraction=(r:Interval['lower'])=>r.denominator==='1'?r.numerator:`${r.numerator}/${r.denominator}`;
 return `${value.lower_closed?'[':'('}${fraction(value.lower)}, ${fraction(value.upper)}${value.upper_closed?']':')'}`;
}

function CalculationInputs({binding,report}:{binding:Binding;report:Report}){
 const {calculation}=binding;
 return <details><summary>Exact intervals and source facts</summary>
  <dl>
   <dt>Parent interval</dt><dd>{exactInterval(calculation.parent_interval)}</dd>
   <dt>Weighted sum</dt><dd>{exactInterval(calculation.weighted_sum_interval)}</dd>
   <dt>Residual</dt><dd>{exactInterval(calculation.residual_interval)}</dd>
  </dl>
  {calculation.terms.length>0&&<ul>{calculation.terms.map(term=><li key={term.concept}>
   {term.concept} · weight {term.weight.numerator}/{term.weight.denominator} · {exactInterval(term.weighted_interval)}
  </li>)}</ul>}
  {Object.entries(binding.data_points).map(([concept,point])=><div key={concept}>
   <p>{concept} · {point.status} · {exactInterval(point.interval)}</p>
   <ul>{point.source_fact_ids.map(id=>{
    const fact=report.fact_provenance[id];
    return <li key={id}>Fact <code>{id}</code> · context {fact.context_ref} · unit {fact.unit_ref}
     {fact.declaration_documents.length>0&&<ul>{fact.declaration_documents.map(doc=><li key={doc.uri}>{doc.uri} · <code>{doc.sha256}</code></li>)}</ul>}
    </li>;
   })}</ul>
  </div>)}
 </details>;
}

export function SourceCalculations({symbol,cik}:{symbol:string;cik:string|null}){
 const [packet,setPacket]=useState<CalculationPacket|null>(null);
 const [busy,setBusy]=useState(false),[error,setError]=useState('');
 const serial=useRef(0);
 useEffect(()=>{
  serial.current++;setPacket(null);setError('');setBusy(false);
  return()=>{serial.current++};
 },[symbol,cik]);

 async function load(file:File){
  const n=++serial.current;
  setPacket(null);setError('');setBusy(true);
  try{
   if(!file.size||file.size>256*1024)throw Error();
   const p=await verifyCalculationPacket(await readOfflineJson(file),symbol,cik);
   if(n===serial.current)setPacket(p);
  }catch{
   if(n===serial.current)setError('Calculation export unavailable: source, cutoff, network, interval or integrity binding did not pass.');
  }finally{
   if(n===serial.current)setBusy(false);
  }
 }
 return <section aria-label="Source-bound calculation report" aria-busy={busy}>
  <h4>Source-bound calculation diagnostics</h4>
  <label>Open calculation report<input type="file" accept="application/json,.json" disabled={busy||!cik}
   onChange={e=>{const file=e.target.files?.[0];e.target.value='';if(file)void load(file)}}/></label>
  {busy&&<p role="status">Validating calculation sources and exact intervals…</p>}
  {error&&<p role="alert">{error}</p>}
  {packet&&<SourceCalculationView packet={packet}/>}
 </section>;
}

export function SourceCalculationView({packet}:{packet:CalculationPacket}){
 const report=packet.report;
 return <>
   <p>Acceptance cutoff {packet.as_of} · {packet.rounding_mode} · {packet.status}</p>
   <p>Calculation role {packet.role??'unavailable'} · {packet.reason??'source-bound diagnostic available'}</p>
   {packet.weight_profile&&<p>Original decimal relationship weights are applied as exact fractions.</p>}
   {packet.lineage&&<p>Amendment lineage {packet.lineage.status} · {packet.lineage.sources.length} supplied sources</p>}
   {report&&<div role="region" aria-label="Calculation diagnostic table" tabIndex={0} className="atlas-table-scroll">
    <table>
     <caption>Exact source-bound calculation checks</caption>
     <thead><tr><th scope="col">Parent concept</th><th scope="col">Source context</th><th scope="col">Source unit</th><th scope="col">Diagnostic</th><th scope="col">Missing contributors</th></tr></thead>
     <tbody>{report.bindings.map(b=><tr key={b.parent+'|'+(b.aspect_sha256??b.aspects.context_sha256)+'|'+b.aspects.unit_sha256}>
      <th scope="row">{b.parent}</th>
      <td>{b.aspects.context_sha256??b.source_context_sha256s?.join(', ')}
       {!!b.aspects.effective_dimension_values?.length&&<details><summary>Calculation dimensions</summary><dl>
        {b.aspects.effective_dimension_values.map(axis=><div key={axis.dimension}><dt>{axis.dimension}</dt><dd>{axis.member}{b.aspects.dimensions.some(d=>d.dimension===axis.dimension)?' (reported)':' (taxonomy default)'}</dd></div>)}
       </dl></details>}
      </td>
      <td>{b.aspects.unit_sha256}</td>
      <td>{b.calculation.status}<CalculationInputs binding={b} report={report}/></td>
      <td>{b.missing_concepts.join(', ')||'None'}</td>
     </tr>)}</tbody>
    </table>
   </div>}
 </>;
}
