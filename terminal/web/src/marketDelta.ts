import type {Feed,Observation} from './LiveMarket';
import {validateMarketState} from './marketContract.ts';
/** A fresh instance per HTTP connection forces full resynchronization after any error. */
export class MarketProjectionReader {
 private previous:Feed|null=null;private sequence=0;private profile:'legacy'|'delta'|null=null;
 accept(raw:unknown):Feed{
  const v=raw as Feed&{browser_delta?:{schema:string;mode:string;sequence:number;base_sequence:number;base_receipt:number;history_status:[number,string,number][]}};
  if(!Object.prototype.hasOwnProperty.call(v??{},'browser_delta')){
   if(this.profile==='delta')throw Error('Stock projection profile downgrade');
   const checked=validateMarketState(raw);this.profile='legacy';return checked;
  }
  if(this.profile==='legacy')throw Error('Stock projection profile changed');
  const d=v.browser_delta;
  if(!d||!Number.isSafeInteger(d.base_receipt)||d.base_receipt!==(this.previous?.accepted_observations??0))throw Error('Stock projection receipt baseline mismatch');
  if(!Array.isArray(v.channels)||v.channels.length>3||new Set(v.channels).size!==v.channels.length||v.channels.some(c=>!['quotes','trades','bars'].includes(c)))throw Error('Invalid stock projection channels');
  if(d.schema!=='gig.market.delta.v1'||!Number.isSafeInteger(d.sequence)||d.sequence!==this.sequence+1||d.base_sequence!==this.sequence||!Array.isArray(d.history_status)||d.history_status.length>256||d.history_status.some(r=>!Array.isArray(r)||r.length!==3))throw Error('Stock projection sequence mismatch');
  if(d.mode!=='full'&&d.mode!=='delta')throw Error('Unsupported stock projection mode');
  if(d.mode==='delta'&&(!this.previous||d.base_receipt!==this.previous.accepted_observations||v.generation!==this.previous.generation||JSON.stringify(v.symbols)!==JSON.stringify(this.previous.symbols)||JSON.stringify(v.channels)!==JSON.stringify(this.previous.channels)))throw Error('Stock projection requires full resynchronization');
  const checked=validateMarketState(v);if(this.previous&&checked.accepted_observations<this.previous.accepted_observations)throw Error('Stock projection receipt rollback');
  if(d.mode==='full'&&d.history_status.length!==checked.history.length)throw Error('Incomplete full stock projection');const cache=new Map<number,Observation>();
  if(d.mode==='delta')for(const r of this.previous!.history)cache.set(r.receipt_index,r);
  for(const r of checked.history){if(cache.has(r.receipt_index))throw Error('Duplicate stock projection identity');if(d.mode==='delta'&&r.receipt_index<=d.base_receipt)throw Error('Repeated stock projection observation');cache.set(r.receipt_index,r)}
  let previous=0;const history=d.history_status.map(([id,state,age])=>{
   const row=cache.get(id);if(!Number.isSafeInteger(id)||id<=previous||!row||!['LIVE','SIMULATED','STALE','UNAVAILABLE'].includes(state)||!Number.isFinite(age)||age<0)throw Error('Invalid stock projection history');previous=id;return {...row,state,receive_age_seconds:age};
  });
  if(checked.history.some(r=>!history.some(h=>h.receipt_index===r.receipt_index)))throw Error('Unaccounted stock projection observation');
  const result=validateMarketState({...checked,history});this.previous=result;this.sequence=d.sequence;this.profile='delta';return result;
 }
}
