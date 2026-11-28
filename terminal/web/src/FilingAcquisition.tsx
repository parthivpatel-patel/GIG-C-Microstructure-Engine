import {useEffect,useRef,useState} from 'react';
import {readSecFilingReadiness,requestV2} from './api';
import {readOfflineJson} from './offlineJson';

const accessionPattern=/^[0-9]{10}-[0-9]{2}-[0-9]{6}$/;
const hashPattern=/^[a-f0-9]{64}$/;
type Candidate={accession:string;filed:string;form:string;accepted_at:string|null;shard?:string};
type Schedule={rows:Candidate[];truncated:boolean};
function validDate(value:unknown):value is string{
 return typeof value==='string'&&/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/.test(value)&&
  Number(value.slice(0,4))>0&&Number.isFinite(Date.parse(value))&&new Date(value).toISOString().startsWith(value);
}
function admittedSchedule(raw:unknown,cik:string,start:string,end:string):Schedule{
 const value=raw as {schema?:string;issuer_cik?:string;start?:string;end?:string;complete_history?:boolean;truncated?:boolean;
  entries?:{filing:Candidate;metadata_sources:{url:string;sha256:string}[]}[]};
 if(!value||value.schema!=='gig.sec.filing_schedule.v1'||value.issuer_cik!==cik||value.start!==start||value.end!==end||
  value.complete_history!==false||typeof value.truncated!=='boolean'||!Array.isArray(value.entries)||value.entries.length>8){
  throw Error('Invalid filing schedule');
 }
 const seen=new Set<string>(),recent='https://data.sec.gov/submissions/CIK'+cik+'.json';
 const historical=new RegExp('^https://data[.]sec[.]gov/submissions/(CIK'+cik+'-submissions-[0-9]{3}[.]json)$');
 const rows=value.entries.map(entry=>{
  const f=entry?.filing,sources=entry?.metadata_sources;
  if(!f||!accessionPattern.test(f.accession)||seen.has(f.accession)||!validDate(f.filed)||
     f.filed<start||f.filed>end||!['10-K','10-Q','10-K/A','10-Q/A'].includes(f.form)||
     f.accepted_at!==null&&(typeof f.accepted_at!=='string'||f.accepted_at.length>40)||
     !Array.isArray(sources)||!sources.length||sources.length>5||
     sources.some(s=>!s||typeof s.url!=='string'||!hashPattern.test(s.sha256)||s.url!==recent&&!historical.test(s.url))){
   throw Error('Invalid filing schedule entry');
  }
  seen.add(f.accession);
  const shard=sources.some(s=>s.url===recent)?undefined:historical.exec(sources[0].url)?.[1];
  return {accession:f.accession,form:f.form,filed:f.filed,accepted_at:f.accepted_at,shard};
 });
 return {rows,truncated:value.truncated};
}

export function FilingAcquisition({symbol,cik}:{symbol:string;cik:string|null}){
 const [ready,setReady]=useState(false),[start,setStart]=useState(''),[end,setEnd]=useState('');
 const [schedule,setSchedule]=useState<Schedule|null>(null),[accession,setAccession]=useState('');
 const [amends,setAmends]=useState(''),[manifest,setManifest]=useState<File|null>(null);
 const [transform,setTransform]=useState(false),[numericBounds,setNumericBounds]=useState(false),[busy,setBusy]=useState(false);
 const [error,setError]=useState(''),[receipt,setReceipt]=useState('');
 const active=useRef<AbortController|null>(null);
 useEffect(()=>{
  if(!cik)return;
  const controller=new AbortController();
  void readSecFilingReadiness(symbol,controller.signal).then(raw=>{
   const value=raw as {schema:string;symbol:string;cik:string;ready:boolean};
   if(!controller.signal.aborted)setReady(value?.schema==='gig.sec.filing_acquisition.readiness.v1'&&
      value.symbol===symbol&&value.cik===cik&&value.ready===true);
  }).catch(()=>{if(!controller.signal.aborted)setReady(false)});
  return()=>{controller.abort();active.current?.abort()};
 },[symbol,cik]);
 if(!ready||!cik)return null;
 const issuer=cik;
 async function run(action:'discover'|'ingest'){
  active.current?.abort();
  const controller=new AbortController();active.current=controller;
  const {signal}=controller;
  setBusy(true);setError('');setReceipt('');
  try{
   if(action==='discover'){
    if(!validDate(start)||!validDate(end)||start>end)throw Error('Filing date range is required');
    setSchedule(null);
    const result=await requestV2('/sec-filings/acquire',{action,symbol,start,end},signal);
    if(!signal.aborted)setSchedule(admittedSchedule(result,issuer,start,end));
   }else{
    if(!accessionPattern.test(accession)||amends&&!accessionPattern.test(amends))throw Error('Exact accession is required');
    if(manifest&&(!manifest.size||manifest.size>16384))throw Error('Invalid manifest size');
    const inline_manifest=manifest?await readOfflineJson(manifest,signal):undefined;
    if(signal.aborted)return;
    const shard=schedule?.rows.find(row=>row.accession===accession)?.shard;
    const result=await requestV2<{schema:string;status:string;issuer_cik:string;accession:string;installed:boolean;collection_sha256:string}>(
     '/sec-filings/acquire',{action,symbol,accession,...(shard?{metadata_shard:shard}:{}),...(amends?{amends_accession:amends}:{}),
     ...(manifest?{inline_manifest,...(transform?{transformation_profile:'REGISTRY_2015_NUMERIC_V2'}:{})}:{}),
      ...(numericBounds?{numeric_profile:'NUMERIC_BOUND_RESTRICTIONS_V6'}:{})},signal);
    if(signal.aborted)return;
    if(result?.schema!=='gig.sec.filing_ingestion.v1'||result.status!=='ACCEPTED'||result.issuer_cik!==issuer||
       result.accession!==accession||result.installed!==true||!hashPattern.test(result.collection_sha256))throw Error('Invalid filing receipt');
    setReceipt('Filing '+accession+' admitted to the company cache. Collection '+result.collection_sha256);
   }
  }catch{
   if(!signal.aborted)setError('SEC filing operation unavailable. Check the date range, exact accession, source receipts and processing permission.');
  }finally{
   if(active.current===controller){active.current=null;if(!signal.aborted)setBusy(false)}
  }
 }
 return <details>
  <summary>Acquire authorized SEC filings</summary>
  <form onSubmit={e=>{e.preventDefault();void run('discover')}}>
   <label>Filed from<input type="date" required disabled={busy} value={start} onChange={e=>setStart(e.target.value)}/></label>
   <label>Filed through<input type="date" required disabled={busy} value={end} onChange={e=>setEnd(e.target.value)}/></label>
   <button disabled={busy}>Find filing accessions</button>
  </form>
  {schedule&&<p role="status">{schedule.rows.length} eligible filings{schedule.truncated?' · bounded results; more metadata may be available':''}</p>}
  {schedule?.rows.length!==0&&schedule&&<ul aria-label="Discovered filings">{schedule.rows.map(row=><li key={row.accession}>
   <button type="button" disabled={busy} onClick={()=>{setAccession(row.accession);setAmends('')}}>{row.form} · {row.filed} · {row.accession}</button>
   {row.accepted_at&&<span> · accepted {row.accepted_at}</span>}
  </li>)}</ul>}
  <form onSubmit={e=>{e.preventDefault();void run('ingest')}}>
   <label>Exact accession<input required disabled={busy} value={accession} maxLength={20} onChange={e=>setAccession(e.target.value)}/></label>
   <label>Earlier accession for an amendment (optional)<input disabled={busy} value={amends} maxLength={20} onChange={e=>setAmends(e.target.value)}/></label>
   <label>Original inline document manifest (optional)<input type="file" accept="application/json,.json" disabled={busy}
    onChange={e=>{setManifest(e.target.files?.[0]??null);setTransform(false)}}/></label>
   {manifest&&<label><input type="checkbox" checked={transform} disabled={busy} onChange={e=>setTransform(e.target.checked)}/>Use the 2015 numeric transformation profile</label>}
   <label><input type="checkbox" checked={numericBounds} disabled={busy} onChange={e=>setNumericBounds(e.target.checked)}/>
    Apply inherited numeric bounds from supplied schemas
   </label>
   <button disabled={busy}>Acquire selected filing</button>
  </form>
  {busy&&<p role="status">Reading authorized SEC sources…</p>}
  {error&&<p role="alert">{error}</p>}
  {receipt&&<p role="status">{receipt}</p>}
 </details>;
}
