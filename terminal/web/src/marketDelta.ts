import type {Feed,Observation} from './LiveMarket';
import {validateMarketState} from './marketContract.ts';
/** A fresh instance per HTTP connection forces full resynchronization after any error. */
export class MarketProjectionReader {
 private previous:Feed|null=null;private sequence=0;
 accept(raw:unknown):Feed{
  const v=raw as Feed&{browser_delta?:{schema:string;mode:string;sequence:number;base_sequence:number;base_receipt:number;history_status:[number,string,number][]}};
  if(!v?.browser_delta)return validateMarketState(raw); // Legacy full profile remains supported.
  const d=v.browser_delta;
  if(d.schema!=='gig.market.delta.v1'||!Number.isSafeInteger(d.sequence)||d.sequence!==this.sequence+1||d.base_sequence!==this.sequence||!Array.isArray(d.history_status)||d.history_status.length>256)throw Error('Stock projection sequence mismatch');
  if(d.mode!=='full'&&d.mode!=='delta')throw Error('Unsupported stock projection mode');
  if(d.mode==='delta'&&(!this.previous||d.base_receipt!==this.previous.accepted_observations||v.generation!==this.previous.generation||JSON.stringify(v.symbols)!==JSON.stringify(this.previous.symbols)))throw Error('Stock projection requires full resynchronization');
  const checked=validateMarketState(v);if(this.previous&&checked.accepted_observations<this.previous.accepted_observations)throw Error('Stock projection receipt rollback');
  if(d.mode==='full'&&d.history_status.length!==checked.history.length)throw Error('Incomplete full stock projection');const cache=new Map<number,Observation>();
  if(d.mode==='delta')for(const r of this.previous!.history)cache.set(r.receipt_index,r);
  for(const r of checked.history){if(cache.has(r.receipt_index))throw Error('Duplicate stock projection identity');if(d.mode==='delta'&&r.receipt_index<=d.base_receipt)throw Error('Repeated stock projection observation');cache.set(r.receipt_index,r)}
  let previous=0;const history=d.history_status.map(([id,state,age])=>{
   const row=cache.get(id);if(!Number.isSafeInteger(id)||id<=previous||!row||!['LIVE','SIMULATED','STALE','UNAVAILABLE'].includes(state)||!Number.isFinite(age)||age<0)throw Error('Invalid stock projection history');previous=id;return {...row,state,receive_age_seconds:age};
  });
  if(checked.history.some(r=>!history.some(h=>h.receipt_index===r.receipt_index)))throw Error('Unaccounted stock projection observation');
  const result=validateMarketState({...checked,history});this.previous=result;this.sequence=d.sequence;return result;
 }
}
