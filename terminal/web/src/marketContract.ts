import {validateTradeTape} from './tradeTape.ts';
import type {Feed} from './LiveMarket';
function object(v:unknown){return v!==null&&typeof v==='object'&&!Array.isArray(v)}
function count(v:unknown){return typeof v==='number'&&Number.isSafeInteger(v)&&v>=0}
/** Validate both push and mutation replies before charts receive their required fields. */
export function validateMarketState(raw:unknown):Feed{
 const v=raw as Feed;
 if(!object(v)||v.schema!=='gig.alpaca.live.v1'||typeof v.state!=='string'||typeof v.phase!=='string'||!count(v.generation)||!count(v.accepted_observations)||!count(v.connection_count)||!object(v.metrics)||!object(v.readiness)||typeof v.readiness.ready!=='boolean'||!Array.isArray(v.symbols)||v.symbols.length>4||v.symbols.some(s=>typeof s!=='string'||!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(s))||new Set(v.symbols).size!==v.symbols.length||!Array.isArray(v.history)||v.history.length>256||!Array.isArray(v.observations)||v.observations.length>20)throw Error('Invalid bounded stock state contract');
 if(v.last_failure!=null){const f=v.last_failure;if(!object(f)||Object.keys(f).sort().join(',')!=='category,code,phase,provider_code'||!['LOCAL_PROTOCOL_REJECTION','PROVIDER_AUTH_REJECTION','PROVIDER_SUBSCRIPTION_REJECTION','PROVIDER_RUNTIME_REJECTION','PROVIDER_CONNECT_REJECTION'].includes(f.category)||typeof f.phase!=='string'||!(/^[A-Z_]{1,40}$/).test(f.phase)||typeof f.code!=='string'||!(/^[a-z0-9_.-]{1,80}$/).test(f.code)||f.provider_code!==null&&(typeof f.provider_code!=='string'||!(/^-?[0-9]{1,20}$/).test(f.provider_code)))throw Error('Invalid safe provider diagnostic');}
 for(const r of [...v.history,...v.observations]){
  if(!object(r)||typeof r.symbol!=='string'||!count(r.receipt_index)||!count(r.generation)||r.receipt_index<1||r.receipt_index>v.accepted_observations||r.generation>v.generation||typeof r.out_of_order!=='boolean'||typeof r.receive_age_seconds!=='number'||!Number.isFinite(r.receive_age_seconds)||r.receive_age_seconds<0||(!v.symbols.includes(r.symbol)&&r.state!=='UNAVAILABLE')||typeof r.timestamp!=='string'||typeof r.source_timestamp_ns!=='string'||!/^[-]?\d{1,24}$/.test(r.source_timestamp_ns)||!['LIVE','SIMULATED','STALE','UNAVAILABLE'].includes(r.state)||!object(r.data))throw Error('Invalid stock observation contract');
  const fields:{[key:string]:string[]}={quote:['bid','ask','bid_size','ask_size'],trade:['price','size'],bar:['open','high','low','close','volume'],correction:['original_price','corrected_price','original_size','corrected_size'],cancel:['price','size']};
  if(!fields[r.kind]||fields[r.kind].some(k=>typeof r.data[k]!=='string'||!r.data[k].trim()||!Number.isFinite(Number(r.data[k]))||Number(r.data[k])<0))throw Error('Invalid stock numeric observation');
 }
 if(v.trade_reconciliation!==undefined){if(!object(v.trade_reconciliation)||Object.keys(v.trade_reconciliation).length!==v.symbols.length||Object.keys(v.trade_reconciliation).some(s=>!v.symbols.includes(s)))throw Error('Trade derivation scope rejected');for(const s of v.symbols){const t=validateTradeTape(v.trade_reconciliation[s],s,v.generation);if(t.source_session_id!==null&&t.source_session_id!==v.source_session_id)throw Error('Trade/source capture disagreement');if(t.input_records!==v.history.length)throw Error('Trade/source window disagreement');const scoped=v.history.filter(r=>r.symbol===s&&r.generation===v.generation),ids=new Set(scoped.map(r=>r.receipt_index));if(t.relevant_records>scoped.length||t.trades.some(r=>!ids.has(r.original_receipt)||r.lineage_receipts.some(n=>!ids.has(n))))throw Error('Trade/source lineage disagreement')}}
 return v;
}

export type MarketDirectory={results:{symbol:string}[];catalog_count:number;matches:number;returned?:number;source:{authority:string;as_of?:string|null}};
/** Identity discovery never asserts current listing coverage,CIK or feed permission. */
export function validateMarketDirectory(raw:unknown):MarketDirectory{
 const x=raw as MarketDirectory;
 if(!object(x)||!Array.isArray(x.results)||x.results.length>20||x.results.some(r=>!object(r)||typeof r.symbol!=='string'||!/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(r.symbol))||new Set(x.results.map(r=>r.symbol)).size!==x.results.length||!count(x.catalog_count)||x.catalog_count>150000||!count(x.matches)||x.matches>x.catalog_count||x.results.length>x.matches||x.returned!==undefined&&x.returned!==x.results.length||!object(x.source)||typeof x.source.authority!=='string'||!x.source.authority.trim()||x.source.authority.length>180||x.source.as_of!=null&&(typeof x.source.as_of!=='string'||x.source.as_of.length>64))throw Error('Invalid bounded market directory contract');
 return x;
}
