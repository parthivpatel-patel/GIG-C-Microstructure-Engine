import {useEffect,useRef,useState} from 'react';
import {request} from './api';
import type {Fraction} from './contracts';

const labels={
  ofi:'Top-of-book order-flow imbalance',
  quote_intensity:'Quote observations per logical second',
  window_return:'Midpoint return',
  realized_variance:'Midpoint realized variance',
} as const;
type Metric={value:Fraction|null;unavailable:string|null};
type Flow={
  schema:string;origin:string;dataset:string;fixture_sha256:string;position:number;
  clock:string;as_of_elapsed_ns:string;window_ns:string;
  trade_observations_used:false;provider_requested:false;
  metrics:Record<keyof typeof labels,Metric>;parents:{journal_prefix:string}[];
};
function admit(raw:unknown,position:number,fixture:string):Flow{
  const f=raw as Flow;
  if(!f||f.schema!=='gig.terminal.authored_quote_flow.v1'||f.origin!=='HISTORICAL_SYNTHETIC'||
     f.dataset!=='terminal-authored-v2'||f.fixture_sha256!==fixture||f.position!==position||
     f.clock!=='AUTHORED_LOGICAL_50MS'||f.as_of_elapsed_ns!==String((position-1)*50000000)||
     f.window_ns!==String(Math.min(20,position-1)*50000000)||
     f.trade_observations_used!==false||f.provider_requested!==false||
     !Array.isArray(f.parents)||f.parents.length!==position||
     f.parents.some((parent,i)=>parent.journal_prefix!==String(i+1)))throw Error('Invalid authored quote flow');
  for(const key of Object.keys(labels) as (keyof typeof labels)[]){
    const metric=f.metrics?.[key];
    if(!metric||(metric.value===null?typeof metric.unavailable!=='string':
      !metric.value||!/^[-]?(0|[1-9][0-9]{0,38})$/.test(metric.value.numerator)||
      !/^[1-9][0-9]{0,38}$/.test(metric.value.denominator)))throw Error('Invalid exact quote metric');
  }
  return f;
}

export function NativeQuoteFlow({position,fixture}:{position:number;fixture:string}){
  const [report,setReport]=useState<Flow|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
  const revision=useRef(0);
  useEffect(()=>{revision.current++;setReport(null);setBusy(false);setError('');return()=>{revision.current++}},[fixture]);
  async function capture(){
    const current=++revision.current;
    setBusy(true);setError('');
    try{
      const candidate=admit(await request('/research/native-quote-flow',{position}),position,fixture);
      if(current===revision.current)setReport(candidate);
    }catch{
      if(current===revision.current)setError('Native quote flow is unavailable for this replay position.');
    }finally{
      if(current===revision.current)setBusy(false);
    }
  }
  return <section aria-label="Native authored quote flow" aria-busy={busy}>
    <button type="button" onClick={()=>void capture()} disabled={busy||position<2}>Calculate native quote flow</button>
    {error&&<p role="alert">{error}</p>}
    {report&&<>
      <p>Authored replay position {report.position} · {Number(report.window_ns)/1000000} ms logical window. Quotes only.</p>
      <dl>{(Object.keys(labels) as (keyof typeof labels)[]).map(key=>{
        const value=report.metrics[key].value;
        return <div key={key}><dt>{labels[key]}</dt><dd>{value?<code>{value.numerator}/{value.denominator}</code>:'Unavailable'}</dd></div>;
      })}</dl>
      <details><summary>Source lineage</summary><p>Fixture SHA-256 <code>{report.fixture_sha256}</code></p><p>{report.parents.length} native replay quote references.</p></details>
    </>}
  </section>;
}
