import type {TerminalState} from './contracts';
import {price} from './format';

type MessageType='E'|'C'|'P'|'Q'|'B';
type Row={
 message_type:MessageType;match_number:string;stock_locate:string;ordinal:string;frame_offset:string;
 source_timestamp_ns:string;shares:string|null;order_reference:string|null;price4:string|null;
 printable:string|null;reported_side:string|null;cross_type:string|null;
 book_attribution:'SELECTED_LOCATE'|'SESSION_UNASSIGNED';native_book_committed:boolean;
};
type Receipt={schema:string;origin:string;capture:string;generation:string;complete_tape:false;
 selected_locate:string;scanned_records:string;source_records:string;rows:Row[]};
const names={E:'Order execution',C:'Order execution with price',P:'Trade message',Q:'Cross trade',B:'Broken trade'};
function unsigned(value:unknown):value is string{
 return typeof value==='string'&&/^(0|[1-9][0-9]{0,19})$/.test(value)&&BigInt(value)<=18446744073709551615n;
}

function validReceipt(state:TerminalState):Receipt|null{
 const packet=state.flow as Receipt|undefined;
 if(!packet||packet.schema!=='gig.itch.execution_receipts.v1')return null;
 if(state.mode!=='HISTORICAL_REPLAY'||state.provider!=='authored-itch'||state.origin!=='HISTORICAL_SYNTHETIC'||
    packet.origin!==state.origin||packet.complete_tape!==false||packet.capture!==state.provenance.capture||
    packet.generation!==state.provenance.generation||packet.source_records!==String(state.position)||
    !unsigned(packet.selected_locate)||BigInt(packet.selected_locate)>65535n||
    !unsigned(packet.scanned_records)||Number(packet.scanned_records)!==Math.min(256,state.position)||
    !Array.isArray(packet.rows)||packet.rows.length>Math.min(40,state.position))return null;
 let previousOrdinal:bigint|null=null,previousOffset:bigint|null=null;
 for(const row of packet.rows){
  if(!row||!Object.hasOwn(names,row.message_type)||typeof row.native_book_committed!=='boolean'||
     ![row.match_number,row.stock_locate,row.ordinal,row.frame_offset,row.source_timestamp_ns].every(unsigned)||
     ![row.shares,row.order_reference,row.price4].every(v=>v===null||unsigned(v))||
     ![row.printable,row.reported_side,row.cross_type].every(v=>v===null||typeof v==='string'&&/^[ -~]$/.test(v)))return null;
  if(row.book_attribution==='SELECTED_LOCATE'?row.stock_locate!==packet.selected_locate:
    row.book_attribution!=='SESSION_UNASSIGNED'||row.stock_locate!=='0'||row.message_type!=='B')return null;
  const type=row.message_type;
  if((row.price4!==null)!==['C','P','Q'].includes(type)||(row.shares!==null)!==(type!=='B')||
     (row.order_reference!==null)!==['E','C','P'].includes(type)||(row.printable!==null)!==(type==='C')||
     (row.reported_side!==null)!==(type==='P')||(row.cross_type!==null)!==(type==='Q')||
     row.native_book_committed&&type!=='E'&&type!=='C')return null;
  const ordinal=BigInt(row.ordinal),offset=BigInt(row.frame_offset);
  if(previousOrdinal!==null&&(ordinal>=previousOrdinal||offset>=previousOffset!))return null;
  previousOrdinal=ordinal;previousOffset=offset;
 }
 return packet;
}

export function ItchExecutions({state}:{state:TerminalState}){
 const packet=validReceipt(state);
 if(!packet)return null;
 return <details aria-label="Authored ITCH execution source messages">
  <summary>Authored ITCH execution messages</summary>
  <p>{packet.scanned_records} recent source frames considered for stock locate {packet.selected_locate}. Times are source intraday nanoseconds. The unassigned break records preserve raw match references.</p>
  {packet.rows.length? <div role="region" aria-label="Exact ITCH execution messages" className="atlas-table-scroll" tabIndex={0}>
   <table>
    <caption>Newest receipts first · bounded authored source · no aggressor inference</caption>
    <thead><tr><th scope="col">Frame</th><th scope="col">Source time</th><th scope="col">Message</th>
     <th scope="col">Match</th><th scope="col">Shares</th><th scope="col">Source price</th><th scope="col">Source scope</th></tr></thead>
    <tbody>{packet.rows.map(row=><tr key={row.ordinal}>
     <th scope="row">{row.ordinal}</th><td>{row.source_timestamp_ns}</td><td>{names[row.message_type]}</td>
     <td>{row.match_number}</td><td>{row.shares??'Unavailable'}</td>
     <td>{row.price4===null?'Unavailable':price(row.price4,'10000')}</td>
     <td><details><summary>{row.book_attribution==='SESSION_UNASSIGNED'?'Unassigned session break':row.native_book_committed?'Native book committed':'Source observation'}</summary>
      <dl><dt>Frame offset</dt><dd>{row.frame_offset}</dd><dt>Order reference</dt><dd>{row.order_reference??'Unavailable'}</dd>
       <dt>Source side code</dt><dd>{row.reported_side??'Unavailable'}</dd><dt>Printable code</dt><dd>{row.printable??'Unavailable'}</dd>
       <dt>Cross code</dt><dd>{row.cross_type??'Unavailable'}</dd></dl>
     </details></td>
    </tr>)}</tbody>
   </table>
  </div>: <p role="status">No execution-related records in the retained scope.</p>}
 </details>;
}
