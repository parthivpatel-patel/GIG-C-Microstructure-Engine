import {useEffect,useRef,useState} from 'react';
import {request} from './api';
import {backfillCandidates,backfillHistory} from './iexBackfill';
import type {HistoricalCore} from './historicalResearch';

export function IexBackfill({capture,generation}:{capture:string;generation:number}){
 const [gaps,setGaps]=useState<ReturnType<typeof backfillCandidates>>([]);
 const [history,setHistory]=useState<HistoricalCore|null>(null);
 const [message,setMessage]=useState('');
 const [busy,setBusy]=useState(false);
 const [failed,setFailed]=useState(false);
 const active=useRef(false);
 useEffect(()=>{active.current=true;return()=>{active.current=false}},[]);

 async function load(gap?:ReturnType<typeof backfillCandidates>[number]){
  setBusy(true);setHistory(null);setMessage('');setFailed(false);
  try{
   if(gap){
    const report=backfillHistory(await request('/stocks/live-backfill',{gap_id:gap.gap_id,max_pages:4},30000),gap,4);
    if(active.current)setHistory(report);
   }else{
    const candidates=backfillCandidates(await request('/stocks/live-backfill'),capture,generation);
    if(active.current){setGaps(candidates);if(!candidates.length)setMessage('No gap is bounded by retained observations.')}
   }
  }catch{
   if(active.current){setFailed(true);setMessage('Historical backfill unavailable. Check source permissions or refresh the retained gaps.')}
  }finally{if(active.current)setBusy(false)}
 }

 return <details>
  <summary>IEX reconnect backfill</summary>
  <p>Retrieve historical quotes or trades between retained live observations. Exchange loss remains unknown. Live metrics and observations stay separate.</p>
  <button disabled={busy} onClick={()=>void load()}>Find retained gaps</button>
  {gaps.map(gap=><p key={gap.gap_id}>
   <button disabled={busy} onClick={()=>void load(gap)}>Fetch {gap.symbol} {gap.kind}</button> {gap.start} → {gap.end}
  </p>)}
  {busy&&<p role="status">Reading IEX backfill…</p>}
  {message&&<p role={failed?'alert':'status'}>{message}</p>}
  {history&&<>
   <p role="status">{history.record_count} historical {history.kind} · {history.origin} · {history.has_more?'More pages advertised':'Source response exhausted'} · {history.canonical_sha256}</p>
   {history.records.length>0&&<div className="atlas-table-scroll" tabIndex={0} aria-label="Historical IEX backfill records">
    <table><caption>{history.symbol} historical IEX {history.kind}</caption>
     <thead><tr><th scope="col">Source time</th><th scope="col">{history.kind==='quotes'?'Bid × size':'Price × size'}</th>{history.kind==='quotes'&&<th scope="col">Ask × size</th>}</tr></thead>
     <tbody>{history.records.map(row=><tr key={String(row.source_record_sha256)}>
      <td>{row.timestamp}</td><td>{history.kind==='quotes'?`${row.bid} × ${row.bid_size}`:`${row.price} × ${row.size}`}</td>
      {history.kind==='quotes'&&<td>{row.ask} × {row.ask_size}</td>}
     </tr>)}</tbody>
    </table>
   </div>}
  </>}
 </details>;
}
