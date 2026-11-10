import {historicalAmount} from './historicalMarket.ts';
export type TapeTrade={trade_id:string;exchange:string;tape:string;price:string;size:string;original_receipt:number;source_timestamp_ns:string;lineage_receipts:number[]};
export type TradeTape={schema:string;symbol:string;generation:number;state:'UNRESOLVED'|'NO_TRADE_INPUT'|'CONSISTENT_RETAINED_WINDOW';origin:string;input_records:number;relevant_records:number;accepted_prefix_records:number;duplicate_records:number;applied_corrections:number;applied_cancels:number;active_count:number;trades:TapeTrade[];error:{code:string;receipt_index:number|null}|null;corrected_size_sum:{numerator:string;denominator:string}|null;source_sha256:string[];complete_tape:false;order_book_mutations:0;canonical_sha256:string;policy:string};
const count=(v:unknown):v is number=>typeof v==='number'&&Number.isSafeInteger(v)&&v>=0;
const hash=(v:unknown)=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
const ref=(v:unknown)=>typeof v==='string'&&/^[!-~]{1,64}$/.test(v);
export function validateTradeTape(raw:unknown,symbol:string,generation:number):TradeTape{
 const t=raw as TradeTape;
 if(!t||t.schema!=='gig.bounded.trade_reconciliation.v1'||t.symbol!==symbol||t.generation!==generation||!['UNRESOLVED','NO_TRADE_INPUT','CONSISTENT_RETAINED_WINDOW'].includes(t.state)||!['UNAVAILABLE','HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'].includes(t.origin)||t.complete_tape!==false||t.order_book_mutations!==0||!hash(t.canonical_sha256)||typeof t.policy!=='string'||t.policy.length>1024)throw Error('Invalid bounded trade derivation');
 for(const key of ['input_records','relevant_records','accepted_prefix_records','duplicate_records','applied_corrections','applied_cancels','active_count']as const)if(!count(t[key])||t[key]>256)throw Error('Trade derivation resource limit');
 if(t.relevant_records>t.input_records||t.accepted_prefix_records>t.relevant_records||!Array.isArray(t.trades)||t.trades.length!==t.active_count||t.active_count>t.accepted_prefix_records||!Array.isArray(t.source_sha256)||t.source_sha256.length>256||!t.source_sha256.every(hash))throw Error('Trade derivation accounting rejected');
 if(t.state==='UNRESOLVED'?(t.corrected_size_sum!==null||!t.error||! /^[A-Z_]{1,64}$/.test(t.error.code)):(t.error!==null))throw Error('Unresolved trade state cannot publish totals');
 if(t.state==='NO_TRADE_INPUT'&&(t.active_count||t.corrected_size_sum!==null))throw Error('Missing trade input cannot invent totals');
 const ids=new Set<string>();let total=0n,prior=0;
 for(const r of t.trades){
  if(!r||!ref(r.trade_id)||!ref(r.exchange)||!ref(r.tape)||!count(r.original_receipt)||r.original_receipt<=prior||typeof r.source_timestamp_ns!=='string'||!/^\d{1,24}$/.test(r.source_timestamp_ns)||!Array.isArray(r.lineage_receipts)||!r.lineage_receipts.length||r.lineage_receipts.length>256||r.lineage_receipts[0]!==r.original_receipt||r.lineage_receipts.some((n,i)=>!count(n)||n<1||i>0&&n<=r.lineage_receipts[i-1]))throw Error('Trade lineage rejected');
  prior=r.original_receipt;const id=JSON.stringify([r.exchange,r.tape,r.trade_id]);if(ids.has(id))throw Error('Duplicate active trade identity');ids.add(id);
  if(historicalAmount(r.price)===0n||historicalAmount(r.size)===0n)throw Error('Trade amount rejected');total+=historicalAmount(r.size);
 }
 if(t.corrected_size_sum){const f=t.corrected_size_sum;if(!/^(0|[1-9]\d{0,80})$/.test(f.numerator)||! /^[1-9]\d{0,80}$/.test(f.denominator)||BigInt(f.numerator)*1000000000000n!==total*BigInt(f.denominator))throw Error('Trade total disagreement')}
 else if(t.state==='CONSISTENT_RETAINED_WINDOW')throw Error('Missing reconciled total');
 return t;
}
