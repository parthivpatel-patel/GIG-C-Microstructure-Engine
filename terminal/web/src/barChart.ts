import {historicalAmount,historyNanoseconds} from './historicalMarket.ts';
export type Bar={timestamp:string;open:string;high:string;low:string;close:string;volume:string};
export type BarSource={symbol?:string;origin?:string;feed?:string;adjustment?:string;received_at?:string};
/** Display projection only. Exact values and provenance remain available to users. */
export function barSourceLabel(source:BarSource={}){
 const identity=typeof source.symbol==='string'&&/^[A-Z][A-Z0-9]{0,9}(?:[.-][A-Z0-9]{1,3})?$/.test(source.symbol)?source.symbol:'Unverified symbol';
 const feed=source.feed==='iex'?'IEX':source.feed==='sip'?'SIP':'Unverified feed';
 const classification=source.origin==='HISTORICAL_SYNTHETIC'?'Authored historical OHLC':source.origin==='OBSERVED_OFFICIAL_RESPONSE'?'Observed historical OHLC':'Source-unverified historical OHLC';
 return {title:`${classification} · ${identity} · ${feed}`,classification,feed,identity,
  adjustment:['raw','split','dividend','all'].includes(source.adjustment||'')?source.adjustment:'unverified',
  received:typeof source.received_at==='string'&&source.received_at.length<=40&&Number.isFinite(Date.parse(source.received_at))?source.received_at:'Unavailable'};
}
/** Validate exact OHLC relationships before converting bounded source prices to SVG. */
export function barGeometry(bars:Bar[]){
 if(!Array.isArray(bars)||bars.length>256)throw Error('Bar count exceeds chart budget');
 if(!bars.length)return [];
 let prior=-1n;
 const values=bars.map(b=>{
  if(!b||typeof b.timestamp!=='string'||b.timestamp.length>40)throw Error('Invalid bar timestamp');
  const time=historyNanoseconds(b.timestamp);if(time<=prior)throw Error('Invalid bar ordering');prior=time;
  const exact=Object.fromEntries(['open','high','low','close','volume'].map(k=>[k,historicalAmount(b[k as keyof Bar])])) as Record<string,bigint>;
  if(exact.low===0n||exact.open<exact.low||exact.close<exact.low||exact.open>exact.high||exact.close>exact.high)throw Error('Invalid bar OHLC');
  return b;
 });
 const low=Math.min(...values.map(b=>Number(b.low))),high=Math.max(...values.map(b=>Number(b.high))),span=high-low||1,step=600/values.length;
 const y=(price:string)=>160-(Number(price)-low)*140/span;
 return values.map((b,i)=>({bar:b,x:20+(i+.5)*step,left:20+i*step+step*.15,width:Math.max(.5,step*.7),high:y(b.high),low:y(b.low),top:Math.min(y(b.open),y(b.close)),height:Math.max(.5,Math.abs(y(b.open)-y(b.close))),rising:historicalAmount(b.close)>=historicalAmount(b.open)}));
}
/** Only fixed, reviewed messages escape a failed historical request. Never echo a source body. */
export function historicalRequestError(error:unknown):string{
 const code=error instanceof Error?error.message:'';
 const messages:Record<string,string>={
  historical_provider_forbidden:'Provider denied historical access. Review the existing feed entitlement;no feed fallback or retry was attempted.',
  historical_credentials_rejected:'Provider rejected the server credentials. Review private configuration;do not paste keys into the browser.',
  historical_rate_limited:'Provider rate limit or cooldown. Wait before another explicit request;no automatic retry was attempted.',
  historical_interval_rejected:'Historical interval or page budget rejected. Review the documented date,kind and page limits.',
  historical_deadline:'Historical request deadline reached. Previous accepted results remain labeled;the source may have received the read request.',
  historical_source_unavailable:'Historical source transport unavailable. Previous accepted results remain labeled;no synthetic fallback was used.',
  provider_http_403:'Provider denied historical access. Review the existing feed entitlement;no paid feed fallback was attempted.',
  provider_http_401:'Provider rejected the server credentials. Review private configuration;do not paste keys into the browser.',
  provider_http_429:'Provider rate limit. Retry budget exhausted or server wait exceeds the bounded operation.',
 };
 return messages[code]||'Historical request unavailable or rejected. Check configuration,source entitlement,date limits and cooldown. Previous accepted results,if any,remain explicitly labelled below.';
}
