import {useEffect,useRef,useState} from 'react';
import {request} from './api';
import {backfillCandidates,backfillPage} from './iexBackfill';

export function IexBackfill({capture,generation}:{capture:string;generation:number}){
 const [gaps,setGaps]=useState<ReturnType<typeof backfillCandidates>>([]);
 type Gap=ReturnType<typeof backfillCandidates>[number];
 const [page,setPage]=useState<(ReturnType<typeof backfillPage>&{gap:Gap})|null>(null);
 const [message,setMessage]=useState('');
 const [busy,setBusy]=useState(false);
 const [failed,setFailed]=useState(false);
 const serial=useRef(0);
 useEffect(()=>{serial.current++;setGaps([]);setPage(null);setBusy(false);setFailed(false);setMessage('');return()=>{serial.current++}},[capture,generation]);

 async function load(gap?:Gap,more=false){
  const previous=more?page?.continuation:undefined;
  const after=previous?.next_revision??null;
  if(more&&(!gap||!previous||!after))return;
  const id=++serial.current;
  setBusy(true);if(!more)setPage(null);setMessage('');setFailed(false);
  try{
   if(gap){
    const response=await request('/stocks/live-backfill',{gap_id:gap.gap_id,max_pages:4,...(after?{after_revision:after}:{})},30000);
    const report=backfillPage(response,gap,4,after,previous?.pages_seen??0);
    if(id===serial.current)setPage({...report,gap});
   }else{
    const candidates=backfillCandidates(await request('/stocks/live-backfill'),capture,generation);
    if(id===serial.current){setGaps(candidates);if(!candidates.length)setMessage('No gap is bounded by retained observations.')}
   }
  }catch{
   if(id===serial.current){setFailed(true);setMessage('Historical backfill unavailable. Check source permissions or refresh the retained gaps.')}
  }finally{if(id===serial.current)setBusy(false)}
 }
 const history=page?.history;

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
   <p role="status">{history.record_count} historical {history.kind} in this batch · {history.origin} · {history.has_more?(page?.continuation&&page.continuation.pages_seen===page.continuation.page_limit?'Backfill page limit reached':'More source pages advertised'):'Source response exhausted'} · {history.canonical_sha256}</p>
   {page?.continuation&&<p>{page.continuation.pages_seen} of {page.continuation.page_limit} permitted pages read for this gap.</p>}
   {page?.continuation?.next_revision&&<button disabled={busy} onClick={()=>void load(page.gap,true)}>Fetch next historical batch</button>}
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
