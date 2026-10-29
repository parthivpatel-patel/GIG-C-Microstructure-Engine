import type {Bar} from './EquityPanels';
export type HistoryRow=Partial<Bar>&{timestamp:string;source_timestamp_ns:string;source_record_sha256:string;duplicate_record:boolean;bid?:string;ask?:string;bid_size?:string;ask_size?:string;price?:string;size?:string};
export type MarketHistory={schema:string;symbol:string;kind:'bars'|'quotes'|'trades';timeframe:string|null;provider:string;feed:string;origin:string;freshness:string;availability:string;records:HistoryRow[];record_count:number;pages:number;has_more:boolean;complete_market_history:false;received_at:string;requested_interval:{start:string;exclusive_end:string};source_records:{url:string;sha256:string;page:number;records:number;received_at:string}[];scope:string;cache_status:string};
/** Same UTC nanosecond boundary as the native/provider adapter;Date is not the source clock. */
export function historyNanoseconds(value:unknown):bigint{
 if(typeof value!=='string')throw Error('Historical timestamp rejected');
 const m=/^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z$/.exec(value),ms=m?Date.parse(m[1]+'Z'):NaN;
 if(!m||!Number.isFinite(ms)||new Date(ms).toISOString().slice(0,19)!==m[1])throw Error('Historical timestamp rejected');
 const ns=BigInt(ms)*1000000n+BigInt((m[2]||'').padEnd(9,'0')||'0');
 if(ns<0n||ns>9223372036854775807n)throw Error('Historical clock boundary rejected');return ns;
}
function amount(value:unknown):bigint{
 if(typeof value!=='string'||value.length>48)throw Error('Historical numeric field rejected');
 const m=/^(\d+(?:\.\d*)?|\.\d+)(?:[Ee]([+-]?\d{1,3}))?$/.exec(value);
 if(!m)throw Error('Historical numeric field rejected');
 const fraction=(m[1].split('.')[1]||'').length,exponent=Number(m[2]||0)-fraction;
 if(exponent< -12||exponent>15)throw Error('Historical precision rejected');
 const n=BigInt(m[1].replace('.',''))*10n**BigInt(exponent+12);
 if(n>10n**27n)throw Error('Historical numeric boundary rejected');return n;
}
export function validateHistory(raw:unknown,symbol:string,kind:string):MarketHistory{
 const h=raw as MarketHistory;
 if(!h||!['bars','quotes','trades'].includes(kind)||h.schema!=='gig.alpaca.historical.v1'||h.symbol!==symbol||h.kind!==kind||h.provider!=='alpaca'||h.feed!=='iex'||h.freshness!=='HISTORICAL_NOT_LIVE'||!['OBSERVED_OFFICIAL_RESPONSE','HISTORICAL_SYNTHETIC'].includes(h.origin)||h.complete_market_history!==false||typeof h.has_more!=='boolean'||!Array.isArray(h.records)||h.records.length>256||h.records.length!==h.record_count||!Number.isInteger(h.pages)||h.pages<1||h.pages>4||!Array.isArray(h.source_records)||h.source_records.length!==h.pages||!Number.isFinite(Date.parse(h.received_at))||!h.requested_interval)throw Error('Historical response rejected');
 if(kind==='bars'?!['1Day','1Hour','1Min'].includes(h.timeframe||''):h.timeframe!==null)throw Error('Historical timeframe rejected');
 if(h.availability!==(h.records.length?'AVAILABLE':'EMPTY_SOURCE_RESPONSE'))throw Error('Historical availability rejected');
 const lower=historyNanoseconds(h.requested_interval.start),upper=historyNanoseconds(h.requested_interval.exclusive_end);
 if(upper<=lower)throw Error('Historical interval rejected');
 if(h.source_records.some((r,i)=>!r||r.url!=='https://data.alpaca.markets/v2/stocks/'+kind||! /^[a-f0-9]{64}$/.test(r.sha256)||r.page!==i+1||!Number.isInteger(r.records)||r.records<0||r.records>64||!Number.isFinite(Date.parse(r.received_at)))||h.source_records.reduce((n,r)=>n+r.records,0)!==h.record_count)throw Error('Historical source receipt rejected');
 let prior=-1n;
 for(const r of h.records){
  if(!r||typeof r.source_timestamp_ns!=='string'||!/^\d{1,25}$/.test(r.source_timestamp_ns)||! /^[0-9a-f]{64}$/.test(r.source_record_sha256)||typeof r.duplicate_record!=='boolean')throw Error('Historical record rejected');
  const ns=BigInt(r.source_timestamp_ns);
  if(ns!==historyNanoseconds(r.timestamp)||ns<lower||ns>=upper)throw Error('Historical source clock or interval disagreement');
  if(ns<prior||kind==='bars'&&ns===prior)throw Error('Historical ordering rejected');prior=ns;
  const fields=kind==='bars'?['open','high','low','close','volume']:kind==='quotes'?['bid','ask','bid_size','ask_size']:['price','size'];
  const numbers=new Map(fields.map(field=>[field,amount(r[field as keyof HistoryRow])]));
  if(fields.some(field=>(kind==='bars'&&field!=='volume'||kind==='trades')&&numbers.get(field)===0n))throw Error('Historical positive price/quantity rejected');
  if(kind==='bars'&&(numbers.get('low')!>numbers.get('high')!||['open','close'].some(k=>numbers.get(k)!<numbers.get('low')!||numbers.get(k)!>numbers.get('high')!)))throw Error('Historical OHLC rejected');
 }
 return h;
}
/** Approximate graphics only. Strict timestamp intersection,no nearest-neighbour fill. */
export function alignedComparison(histories:MarketHistory[]):{timestamps:string[];series:{symbol:string;values:number[]}[];reason?:string}{
 if(histories.length>4||new Set(histories.map(h=>h.symbol)).size!==histories.length||histories.length<2||histories.some(h=>h.origin!==histories[0].origin||h.provider!==histories[0].provider||h.feed!==histories[0].feed||h.kind!=='bars'||h.timeframe!==histories[0].timeframe||h.requested_interval.start!==histories[0].requested_interval.start||h.requested_interval.exclusive_end!==histories[0].requested_interval.exclusive_end))return {timestamps:[],series:[],reason:'Instrument,source-origin or reporting-window scopes differ.'};
 const maps=histories.map(h=>new Map(h.records.map(r=>[r.source_timestamp_ns,r]))),times=[...maps[0].keys()].filter(k=>maps.every(m=>m.has(k))).sort((a,b)=>BigInt(a)<BigInt(b)?-1:1);
 if(!times.length)return {timestamps:[],series:[]};
 return {timestamps:times.map(k=>maps[0].get(k)!.timestamp),series:histories.map((h,i)=>{const base=Number(maps[i].get(times[0])!.close);return {symbol:h.symbol,values:times.map(k=>(Number(maps[i].get(k)!.close)/base-1)*100)}})};
}
