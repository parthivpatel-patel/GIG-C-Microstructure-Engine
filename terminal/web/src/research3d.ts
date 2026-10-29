/** Bounded research-only projections. Exact integers stay in labels; binary64 is display geometry only. */
import type {TerminalState} from './contracts';
import type {Observation} from './LiveMarket';
export const MODELS = [
 ['height','Order-book height-map surface'],['canyon','V-canyon liquidity'],['events','Order-event voxels / point cloud'],['vwap','VWAP liquidity corridor'],
 ['flow','Order-flow streamlines / VPIN'],['wheel','Cylindrical market-depth wheel'],['dome','Volatility dome'],['ribbon','Bid-ask spread ribbon']
] as const;
export type ResearchModel=typeof MODELS[number][0];
export type BookSample={ordinal:number;time:string;symbol:string;scale:string;quantityScale:string;bids:{price_ticks:string;quantity:string}[];asks:{price_ticks:string;quantity:string}[]};
export type ResearchEvent={ordinal:number;time:string;symbol:string;kind:'ADD'|'CANCEL'|'DELETE'|'EXECUTE';order:string;side:'bid'|'ask';price:string;quantity:string;aggressor?:'buy'|'sell'};
export type QuoteSample={ordinal:number;time:string;symbol:string;bid:string;ask:string;bidSize:string;askSize:string;scale:string;state:string};
export type ResearchSource={id:string;origin:string;provider:string;coverage:string;symbols:string[];books:BookSample[];events:ResearchEvent[];quotes:QuoteSample[];notes:string[]};
export type Mark={x:number;y:number;z:number;value:number;label:string;color:string;ordinal:number};
export type Surface={vertices:number[];indices:number[];color:string};
export type Plot={marks:Mark[];lines:{points:number[][];color:string}[];surfaces:Surface[];axes:[string,string,string];notes:string[];summary:string[]};
const uint=/^(0|[1-9][0-9]{0,38})$/;
function integer(v:string,positive=false){if(!uint.test(v)||positive&&BigInt(v)===0n)throw Error('Invalid exact research integer');return BigInt(v)}
export function ratio(n:bigint,d:bigint){if(d<=0n)throw Error('Invalid research scale');const value=Number(n)/Number(d);if(!Number.isFinite(value))throw Error('Research display ratio outside binary64 range');return value}
export function decimal(v:string){if(!/^(0|[1-9][0-9]{0,29})(\.[0-9]{1,18})?$/.test(v))throw Error('Invalid source decimal');const [a,b='']=v.split('.');return {n:BigInt(a+b),d:10n**BigInt(b.length)}}
function scaled(v:string,scale:string){return ratio(integer(v),integer(scale,true))}
export function nativeResearch(history:TerminalState[]):ResearchSource{
 const last=history.at(-1),notes=['Snapshot history is coalesced and incomplete;no order events or executions are inferred from depth changes.'];
 const relevant=last?history.slice(-48).filter(f=>f.instrument===last.instrument&&f.provider===last.provider&&f.origin===last.origin&&f.mode===last.mode&&f.price_scale===last.price_scale&&String(f.quantity_scale||'1')===String(last.quantity_scale||'1')&&f.provenance.session_segment===last.provenance.session_segment):[];
 let previous=-1;const books:BookSample[]=[];
 for(const f of relevant){if(f.position<=previous){notes.push('Non-increasing snapshot position excluded.');continue}previous=f.position;
  const sides=[f.book.bids.slice(0,12),f.book.asks.slice(0,12)];let valid=true;try{integer(f.price_scale,true);integer(String(f.quantity_scale||'1'),true);sides.forEach((ls,s)=>ls.forEach((l,i)=>{integer(l.price_ticks,true);integer(l.quantity,true);if(i&&(s===0?BigInt(ls[i-1].price_ticks)<=BigInt(l.price_ticks):BigInt(ls[i-1].price_ticks)>=BigInt(l.price_ticks)))valid=false}));if(sides.every(s=>s.length)&&BigInt(sides[0][0].price_ticks)>BigInt(sides[1][0].price_ticks))valid=false}catch{valid=false}
  if(!valid){notes.push('Malformed or crossed snapshot excluded.');continue}books.push({ordinal:f.position,time:f.source_timestamp_ns||f.replay_time_ns||'UNAVAILABLE',symbol:f.instrument,scale:f.price_scale,quantityScale:String(f.quantity_scale||'1'),bids:sides[0],asks:sides[1]});
 }
 return {id:'native-retained',origin:last?.origin||'UNAVAILABLE',provider:last?.provider||'unavailable',coverage:`${last?.mode||'NO SOURCE'} · supplied native snapshot depth only · at most12 levels/side`,symbols:last?[last.instrument]:[],books,events:[],quotes:[],notes:[...new Set(notes)]};
}
export function levelOneResearch(rows:Observation[],symbols:string[]):ResearchSource{
 const quotes:QuoteSample[]=[],notes=['IEX venue-limited Level 1 only;no SIP/NBBO,displayed depth,order identities,or trade-direction classification.'];
 const generation=Math.max(-1,...rows.slice(-256).map(r=>r.generation));let prior=-1;const lastTime=new Map<string,bigint>();let origin='UNAVAILABLE';
 for(const r of rows.slice(-256)){
  if(r.generation!==generation||!symbols.includes(r.symbol))continue;
  const evidence=(r as Observation&{origin?:string}).origin;
  if(!['HISTORICAL_SYNTHETIC','OBSERVED_OFFICIAL_RESPONSE'].includes(evidence||'')){notes.push('Unverified source-origin observations excluded.');continue}
  if(origin!=='UNAVAILABLE'&&origin!==evidence){notes.push('Mixed-origin input rejected.');return {id:'iex-retained',origin:'UNAVAILABLE',provider:'alpaca / iex',coverage:'MIXED ORIGIN REJECTED',symbols,books:[],events:[],quotes:[],notes}}
  origin=evidence!;
  if(r.kind!=='quote'||r.out_of_order||r.receipt_index<=prior||r.state==='UNAVAILABLE')continue;
  try{const bid=decimal(r.data.bid),ask=decimal(r.data.ask),bs=decimal(r.data.bid_size),as=decimal(r.data.ask_size),time=integer(r.source_timestamp_ns);if(bid.n===0n||ask.n*bid.d<bid.n*ask.d||time<(lastTime.get(r.symbol)??0n))continue;
   // Common fixed precision is exact;provider source strings remain in the original observation.
   const scale=10n**18n;integer((bid.n*(scale/bid.d)).toString(),true);integer((ask.n*(scale/ask.d)).toString(),true);quotes.push({ordinal:r.receipt_index,time:r.source_timestamp_ns,symbol:r.symbol,bid:(bid.n*(scale/bid.d)).toString(),ask:(ask.n*(scale/ask.d)).toString(),bidSize:`${bs.n}/${bs.d}`,askSize:`${as.n}/${as.d}`,scale:scale.toString(),state:r.state});prior=r.receipt_index;lastTime.set(r.symbol,time);
  }catch{notes.push('Malformed quote excluded.')}
 }
 return {id:'iex-retained',origin,provider:'alpaca / iex',coverage:'IEX venue-limited Level 1 only · retained quotes · current connection generation only · clocks unsynchronized',symbols:symbols.slice(0,4),books:[],events:[],quotes,notes:[...new Set(notes)]};
}
/** Authored two-symbol fixture v1: no exchange observation or native engine replacement. */
export function syntheticResearch():ResearchSource{
 const books:BookSample[]=[],events:ResearchEvent[]=[];let n=0;
 for(const [s,symbol] of ['DEMO-A','DEMO-B'].entries()){
  const orders=new Map<string,{side:'bid'|'ask';price:string;quantity:bigint}>();const base=10000+s*5000;
  const apply=(kind:ResearchEvent['kind'],order:string,side:'bid'|'ask',price:string,quantity:bigint)=>{
   const ordinal=++n,time=String(BigInt(ordinal)*1_000_000n),before=orders.get(order);
   if(kind==='ADD')orders.set(order,{side,price,quantity});else if(before){before.quantity-=quantity;if(!before.quantity)orders.delete(order)}
   events.push({ordinal,time,symbol,kind,order,side,price,quantity:String(quantity),...(kind==='EXECUTE'?{aggressor:side==='ask'?'buy' as const:'sell' as const}:{})});
   const sideBook=(side:'bid'|'ask')=>{const totals=new Map<string,bigint>();for(const o of orders.values())if(o.side===side)totals.set(o.price,(totals.get(o.price)||0n)+o.quantity);return [...totals].sort((a,b)=>Number(BigInt(side==='bid'?b[0]:a[0])-BigInt(side==='bid'?a[0]:b[0]))).map(([price_ticks,q])=>({price_ticks,quantity:String(q)}))};
   books.push({ordinal,time,symbol,scale:'100',quantityScale:'1',bids:sideBook('bid'),asks:sideBook('ask')});
  };
  for(const side of ['bid','ask'] as const)for(let i=0;i<6;i++)apply('ADD',`${symbol}-${side}-${i}`,side,String(base+(side==='bid'?-2-i:2+i)),BigInt(100+i*10));
  for(let i=0;i<36;i++){const side=i%2?'bid':'ask',price=String(base+(side==='bid'?-2:2)),id=`${symbol}-extra-${i}`;apply('ADD',id,side,price,30n+BigInt(i%4)*5n);apply(i%5===0?'CANCEL':'EXECUTE',id,side,price,10n);apply('DELETE',id,side,price,20n+BigInt(i%4)*5n)}
 }
 return {id:'authored-research-v1',origin:'HISTORICAL_SYNTHETIC',provider:'GIG authored fixture v1 · not exchange data',coverage:'Two declared synthetic symbols · known fixture order identities and execution directions · no real-world clock',symbols:['DEMO-A','DEMO-B'],books,events,quotes:[],notes:['Authored fixture generated independently of native replay. All event quantities and directions are declared,not inferred.']};
}
export function executionVwap(events:ResearchEvent[]){let numerator=0n,quantity=0n;return events.filter(e=>e.kind==='EXECUTE').map(e=>{const q=integer(e.quantity,true);numerator+=integer(e.price,true)*q;quantity+=q;return {event:e,numerator,quantity}})}
/** Equal-volume buckets,split exactly;rolling mean of absolute directional imbalance. No classifier. */
export function vpinBuckets(events:ResearchEvent[],bucket=20n,window=4){
 if(bucket<=0n||!Number.isSafeInteger(window)||window<1||window>32||events.length>512)throw Error('Invalid bounded VPIN configuration');
 const completed:{ordinal:number;buy:bigint;sell:bigint;vpin:number|null}[]=[];let buy=0n,sell=0n;
 for(const e of events.filter(e=>e.kind==='EXECUTE')){if(!e.aggressor)return {buckets:[],reason:'Execution direction unavailable;VPIN not computed.'};let q=integer(e.quantity,true);if(q>100000n)return {buckets:[],reason:'Execution exceeds bounded bucket-work budget.'};while(q){const used=q<bucket-buy-sell?q:bucket-buy-sell;if(e.aggressor==='buy')buy+=used;else sell+=used;q-=used;if(buy+sell===bucket){if(completed.length>=512)return {buckets:[],reason:'VPIN bucket-work budget exceeded.'};const sums=[...(window>1?completed.slice(-(window-1)):[]),{buy,sell}];const vpin=sums.length>=window?ratio(sums.slice(-window).reduce((sum,b)=>sum+(b.buy>b.sell?b.buy-b.sell:b.sell-b.buy),0n),bucket*BigInt(window)):null;completed.push({ordinal:e.ordinal,buy,sell,vpin});buy=0n;sell=0n}}}
 return {buckets:completed,reason:`Equal-volume ${bucket} source units;rolling ${window} completed buckets;incomplete final bucket excluded. Toy uncalibrated VPIN;not toxicity evidence.`};
}
function quotesFor(books:BookSample[],quotes:QuoteSample[]){return quotes.length?quotes:books.filter(b=>b.bids.length&&b.asks.length).map(b=>({ordinal:b.ordinal,time:b.time,symbol:b.symbol,bid:b.bids[0].price_ticks,ask:b.asks[0].price_ticks,bidSize:b.bids[0].quantity,askSize:b.asks[0].quantity,scale:b.scale,state:'RETAINED SNAPSHOT'}))}
export function buildResearchPlot(source:ResearchSource,model:ResearchModel,symbol:string,end:number,depth=6,side:'both'|'bid'|'ask'='both'):Plot{
 const out:Plot={marks:[],lines:[],surfaces:[],axes:['SOURCE PRICE','SOURCE QUANTITY','CAPTURE ORDINAL'],notes:[...source.notes],summary:[]};
 if(!Number.isSafeInteger(end)||!Number.isSafeInteger(depth)||depth<1||depth>12)throw Error('Invalid bounded research view');
 const books=source.books.filter(b=>b.symbol===symbol&&b.ordinal<=end).slice(-32),events=source.events.filter(e=>e.symbol===symbol&&e.ordinal<=end).slice(-256),quotes=quotesFor(books,source.quotes.filter(q=>q.symbol===symbol&&q.ordinal<=end).slice(-128));
 const ordinals=[...books,...events,...quotes].map(x=>x.ordinal),minO=Math.min(...ordinals),maxO=Math.max(...ordinals),time=(v:number)=>(maxO===minO?0:(v-minO)/(maxO-minO)*8-4);
 const entries=books.flatMap(b=>(['bid','ask'] as const).filter(s=>side==='both'||s===side).flatMap(s=>b[s==='bid'?'bids':'asks'].slice(0,depth).map(l=>({b,s,p:BigInt(l.price_ticks),q:BigInt(l.quantity)}))));
 const prices=[...entries.map(e=>e.p),...events.map(e=>BigInt(e.price))],lo=prices.length?prices.reduce((a,b)=>a<b?a:b):0n,hi=prices.length?prices.reduce((a,b)=>a>b?a:b):1n,span=hi-lo||1n,x=(p:bigint)=>ratio(p-lo,span)*12-6,maxQ=entries.reduce((m,e)=>e.q>m?e.q:m,1n),color=(s:string)=>s==='bid'?'#35cdb0':'#f5a869';
 const label=(e:typeof entries[number])=>`${e.s.toUpperCase()} price ${e.p}/${e.b.scale};quantity ${e.q}/${e.b.quantityScale};capture ${e.b.ordinal};source/replay ns ${e.b.time}`;
 if(['height','canyon','wheel'].includes(model)&&!entries.length){out.notes.push('No supplied depth in this source/window. Level 1 quotes cannot populate this model.');return out}
 if(model==='height'||model==='canyon'){
  out.axes=model==='height'?['SOURCE PRICE (linear occupied range)','DISPLAYED QUANTITY (linear)','CAPTURE ORDINAL (not elapsed time)']:['SIGNED PRICE DISTANCE FROM EACH MID','CUMULATIVE SIDE QUANTITY','CAPTURE ORDINAL (not elapsed time)'];
  let maxC=1n;for(const b of books)for(const ls of [b.bids,b.asks]){const q=ls.slice(0,depth).reduce((n,l)=>n+BigInt(l.quantity),0n);if(q>maxC)maxC=q}
  const maxDistance=span||1n;
  for(const b of books){for(const s of ['bid','ask'] as const){if(side!=='both'&&side!==s)continue;let cumulative=0n;const path:number[][]=[];for(const e of entries.filter(e=>e.b===b&&e.s===s)){cumulative+=e.q;const mid=b.bids.length&&b.asks.length?BigInt(b.bids[0].price_ticks)+BigInt(b.asks[0].price_ticks):null;if(model==='canyon'&&mid===null)continue;const px=model==='height'?x(e.p):ratio(2n*e.p-mid!,2n*maxDistance)*12;const y=ratio(model==='height'?e.q:cumulative,model==='height'?maxQ:maxC)*5;out.marks.push({x:px,y,z:time(b.ordinal),value:scaled((model==='height'?e.q:cumulative).toString(),b.quantityScale),label:label(e)+(model==='canyon'?`;cumulative ${cumulative}`:''),color:color(s),ordinal:b.ordinal});path.push([px,y,time(b.ordinal)])}if(path.length>1)out.lines.push({points:path,color:color(s)})}}
  for(const s of ['bid','ask'] as const){const vertices:number[]=[],indices:number[]=[];for(let i=1;i<books.length;i++){const a=out.marks.filter(m=>m.ordinal===books[i-1].ordinal&&m.color===color(s)),b=out.marks.filter(m=>m.ordinal===books[i].ordinal&&m.color===color(s));for(let j=1;j<a.length;j++){const c=b.find(m=>m.x===a[j-1].x),d=b.find(m=>m.x===a[j].x);if(c&&d){const n=vertices.length/3;for(const m of [a[j-1],a[j],c,d])vertices.push(m.x,m.y,m.z);indices.push(n,n+1,n+2,n+1,n+3,n+2)}}}if(vertices.length)out.surfaces.push({vertices,indices,color:color(s)})}
  out.notes.push(model==='height'?'Surface joins only adjacent retained snapshots with matching occupied prices. Gaps stay holes;triangles are display interpolation,not additional observations.':'Separate discrete cumulative-liquidity walls;no trade flow inferred. Mid-relative price positions vary with each supplied snapshot.');
 }
 if(model==='events'){
  out.axes=['SOURCE EVENT PRICE','EVENT QUANTITY','CAPTURE ORDINAL'];const max=events.reduce((m,e)=>BigInt(e.quantity)>m?BigInt(e.quantity):m,1n);
  for(const e of events)if(side==='both'||e.side===side)out.marks.push({x:x(BigInt(e.price)),y:ratio(BigInt(e.quantity),max)*5,z:time(e.ordinal),value:Number(e.quantity),ordinal:e.ordinal,color:e.kind==='EXECUTE'?'#8faeff':e.kind==='ADD'?color(e.side):'#c4a1f5',label:`${e.kind} ${e.side} order ${e.order};price ${e.price};quantity ${e.quantity};capture ${e.ordinal};ns ${e.time}`});
  out.notes.push('Explicit source events only. Snapshot differences cannot identify adds,cancels,executions,or queue identities.');
 }
 if(model==='vwap'){
  out.axes=['SOURCE PRICE','CUMULATIVE EXECUTED QUANTITY','CAPTURE ORDINAL'];const vwap=executionVwap(events),total=vwap.at(-1)?.quantity||1n;const points:number[][]=[];
  for(const v of vwap){const px=ratio(v.numerator-lo*v.quantity,span*v.quantity)*12-6,y=ratio(v.quantity,total)*5,z=time(v.event.ordinal);points.push([px,y,z]);out.marks.push({x:px,y,z,value:ratio(v.numerator,v.quantity),ordinal:v.event.ordinal,color:'#b79eff',label:`Cumulative execution VWAP ${v.numerator}/${v.quantity} ticks;executed quantity ${v.quantity};capture ${v.event.ordinal};ns ${v.event.time}`})}
  if(points.length>1)out.lines.push({points,color:'#b79eff'});for(const s of ['bid','ask'] as const){const rail=books.filter(b=>b[s==='bid'?'bids':'asks'].length).map(b=>[x(BigInt(b[s==='bid'?'bids':'asks'][0].price_ticks)),0,time(b.ordinal)]);if(rail.length>1)out.lines.push({points:rail,color:color(s)})}
  out.notes.push('VWAP uses explicit EXECUTE price×quantity only. Floor rails are supplied best quotes,not a forecast band or executable capacity. No execution history means VWAP unavailable.');
 }
 if(model==='flow'){
  out.axes=['CAPTURE ORDINAL','DECLARED EXECUTION QUANTITY','BUY (+) / SELL (−) FLOW'];const trades=events.filter(e=>e.kind==='EXECUTE'),max=trades.reduce((m,e)=>BigInt(e.quantity)>m?BigInt(e.quantity):m,1n);
  for(const e of trades)if(e.aggressor){const y=ratio(BigInt(e.quantity),max)*5,z=e.aggressor==='buy'?3:-3,px=time(e.ordinal)*1.5;out.lines.push({points:[[px,0,0],[px,y*.5,z*.25],[px,y,z]],color:e.aggressor==='buy'?color('bid'):color('ask')});out.marks.push({x:px,y,z,value:Number(e.quantity),ordinal:e.ordinal,color:e.aggressor==='buy'?color('bid'):color('ask'),label:`Declared ${e.aggressor} execution ${e.quantity};price ${e.price};capture ${e.ordinal};ns ${e.time}`})}
  const buckets=vpinBuckets(events);out.summary.push(`VPIN: ${buckets.buckets.at(-1)?.vpin??'unavailable'}`,`Completed volume buckets: ${buckets.buckets.length}`);out.notes.push(buckets.reason,'Streamlines connect declared execution-direction glyphs;not measured fluid trajectories. Quotes/unsigned prints cannot establish VPIN.');
 }
 if(model==='wheel'){
  out.axes=['ANGLE = SIDE / OCCUPIED LEVEL RANK','CAPTURE ORDINAL','RADIUS = DISPLAYED QUANTITY'];
  for(const b of books){for(const s of ['bid','ask'] as const){const group=entries.filter(e=>e.b===b&&e.s===s);for(const [rank,e] of group.entries()){const angle=(s==='bid'?Math.PI:0)+(rank+.5)/depth*Math.PI,r=1+ratio(e.q,maxQ)*4,px=Math.cos(angle)*r,z=Math.sin(angle)*r,y=(time(b.ordinal)+4)/8*5;out.marks.push({x:px,y,z,value:scaled(e.q.toString(),b.quantityScale),ordinal:b.ordinal,color:color(s),label:label(e)+`;side rank ${rank+1};angle categorical,not price distance`});out.lines.push({points:[[Math.cos(angle),y,Math.sin(angle)],[px,y,z]],color:color(s)})}}}
  out.notes.push('Cylinder slices are retained capture ordinals;angular position is categorical side/rank. Radius is linear quantity,not price. No continuous circular market or hidden liquidity implied.');
 }
 if(model==='ribbon'){
  out.axes=['CAPTURE ORDINAL','SOURCE BID / ASK PRICE','BID / ASK EDGE'];
  if(quotes.length){const common=quotes[0].scale,eligible=quotes.filter(q=>q.scale===common),p=eligible.flatMap(q=>[BigInt(q.bid),BigInt(q.ask)]),low=p.reduce((a,b)=>a<b?a:b),high=p.reduce((a,b)=>a>b?a:b),range=high-low||1n,vertices:number[]=[],indices:number[]=[];for(const [i,q] of eligible.entries()){const px=time(q.ordinal)*1.5,yb=ratio(BigInt(q.bid)-low,range)*5,ya=ratio(BigInt(q.ask)-low,range)*5;vertices.push(px,yb,-1,px,ya,1);if(i){const n=i*2;indices.push(n-2,n-1,n,n-1,n,n+1)}out.marks.push({x:px,y:yb,z:-1,value:scaled((BigInt(q.ask)-BigInt(q.bid)).toString(),q.scale),ordinal:q.ordinal,color:color('bid'),label:`Bid ${q.bid}/${q.scale};ask ${q.ask}/${q.scale};exact spread ${(BigInt(q.ask)-BigInt(q.bid))}/${q.scale};capture ${q.ordinal};ns ${q.time};${q.state}`});out.marks.push({...out.marks.at(-1)!,y:ya,z:1,color:color('ask')})}if(indices.length)out.surfaces.push({vertices,indices,color:'#80adf5'})}
  out.notes.push('Ribbon joins discrete best quotes for display;gaps and unobserved path are unknown. No depth or NBBO inference.');
 }
 if(model==='dome'){
  out.axes=['CAPTURE ORDINAL','ROLLING LOG-MID VARIATION','DECORATIVE CROSS-SECTION (no market axis)'];
  const mids:bigint[]=[],scales:string[]=[];const vertices:number[]=[],indices:number[]=[];let row=0;
  const variations:{q:QuoteSample;v:number}[]=[];for(const q of quotes){if(scales.length&&scales.at(-1)!==q.scale){mids.length=0;scales.length=0}mids.push(BigInt(q.bid)+BigInt(q.ask));scales.push(q.scale);if(mids.length>=9){const w=mids.slice(-9),v=Math.sqrt(w.slice(1).reduce((s,m,i)=>s+Math.log1p(Number(m-w[i])/Number(w[i]))**2,0));if(Number.isFinite(v))variations.push({q,v})}}
  const max=Math.max(...variations.map(x=>x.v),0)||1;for(const {q,v} of variations){for(let j=0;j<=8;j++){const z=j/8*6-3,y=v/max*5*Math.sqrt(Math.max(0,1-(z/3)**2));vertices.push(time(q.ordinal)*1.5,y,z);if(row&&j){const n=row*9+j;indices.push(n-10,n-9,n-1,n-9,n-1,n)}}out.marks.push({x:time(q.ordinal)*1.5,y:v/max*5,z:0,value:v,ordinal:q.ordinal,color:'#bca0ff',label:`Derived sqrt(sum of8 squared log-mid changes)=${v};capture ${q.ordinal};ns ${q.time};${q.state};not annualized`});row++}if(indices.length)out.surfaces.push({vertices,indices,color:'#bca0ff'});
  out.notes.push('Minimum9 valid ordered quotes. Dome cross-section is decorative modeled geometry scaled by derived8-return variation;not option implied volatility,a calibrated surface,a forecast,or observed depth.');
 }
 if(quotes.length)out.summary.push(`Last retained quote state: ${quotes.at(-1)!.state};not a currentness guarantee`);
 out.summary.push(`Price scale: ${books.at(-1)?.scale||quotes.at(-1)?.scale||'unavailable'} integer units / source price;quantity scale: ${books.at(-1)?.quantityScale||'provider units (not lot-converted)'}`,`${out.marks.length} inspectable samples`,`Retained source timestamp: ${[...books,...quotes,...events].sort((a,b)=>a.ordinal-b.ordinal).at(-1)?.time||'unavailable'} ns`);
 if(!out.marks.length)out.notes.push('Required inputs unavailable in the selected source,filter,or time window. Choose the authored fixture for a labeled demonstration.');
 return out;
}
