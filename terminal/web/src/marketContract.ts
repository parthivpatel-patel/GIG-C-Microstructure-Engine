import type {Feed} from './LiveMarket';
function object(v:unknown){return v!==null&&typeof v==='object'&&!Array.isArray(v)}
function count(v:unknown){return typeof v==='number'&&Number.isSafeInteger(v)&&v>=0}
/** Validate both push and mutation replies before charts receive their required fields. */
export function validateMarketState(raw:unknown):Feed{
 const v=raw as Feed;
 if(!object(v)||v.schema!=='gig.alpaca.live.v1'||typeof v.state!=='string'||typeof v.phase!=='string'||!count(v.generation)||!count(v.accepted_observations)||!count(v.connection_count)||!object(v.metrics)||!object(v.readiness)||typeof v.readiness.ready!=='boolean'||!Array.isArray(v.symbols)||v.symbols.length>4||v.symbols.some(s=>typeof s!=='string'||!/^[A-Z]{1,5}(?:[.-][A-Z])?$/.test(s))||new Set(v.symbols).size!==v.symbols.length||!Array.isArray(v.history)||v.history.length>256||!Array.isArray(v.observations)||v.observations.length>20)throw Error('Invalid bounded stock state contract');
 for(const r of [...v.history,...v.observations]){
  if(!object(r)||typeof r.symbol!=='string'||!count(r.receipt_index)||!count(r.generation)||r.receipt_index<1||r.receipt_index>v.accepted_observations||r.generation>v.generation||typeof r.out_of_order!=='boolean'||typeof r.receive_age_seconds!=='number'||!Number.isFinite(r.receive_age_seconds)||r.receive_age_seconds<0||(!v.symbols.includes(r.symbol)&&r.state!=='UNAVAILABLE')||typeof r.timestamp!=='string'||typeof r.source_timestamp_ns!=='string'||!/^[-]?\d{1,24}$/.test(r.source_timestamp_ns)||!['LIVE','SIMULATED','STALE','UNAVAILABLE'].includes(r.state)||!object(r.data))throw Error('Invalid stock observation contract');
  const fields:{[key:string]:string[]}={quote:['bid','ask','bid_size','ask_size'],trade:['price','size'],bar:['open','high','low','close','volume'],correction:['original_price','corrected_price','original_size','corrected_size'],cancel:['price','size']};
  if(!fields[r.kind]||fields[r.kind].some(k=>typeof r.data[k]!=='string'||!r.data[k].trim()||!Number.isFinite(Number(r.data[k]))||Number(r.data[k])<0))throw Error('Invalid stock numeric observation');
 }
 return v;
}
