import {useState, type ReactNode} from 'react';
import type {TerminalState} from './contracts';
import {chartRatio,price} from './format';

function ExactDepthDisclosure({children}:{children:ReactNode}){
 const [open,setOpen]=useState(false);
 return <details onToggle={e=>setOpen(e.currentTarget.open)}>
  <summary>Exact cumulative depth by rank</summary>
  {open&&children}
 </details>;
}

type DepthPoint={level:TerminalState['book']['bids'][number];cumulative:bigint;x:number;y:number};
type DepthSide={label:'Bid'|'Ask';points:DepthPoint[]};

function DepthValues({sides,state}:{sides:DepthSide[];state:TerminalState}){
 return <div className="atlas-table-scroll" role="region" tabIndex={0} aria-label="Exact cumulative depth">
  <table><caption>{state.instrument} · {state.origin} · price scale {state.price_scale} · quantity scale {String(state.quantity_scale||1)}</caption>
   <thead><tr><th scope="col">Side and rank</th><th scope="col">Price ticks</th><th scope="col">Quantity integer</th><th scope="col">Cumulative quantity integer</th></tr></thead>
   <tbody>{sides.flatMap(({label,points})=>points.map(({level,cumulative},i)=><tr key={label+level.price_ticks}>
    <th scope="row">{label} {i+1}</th><td>{level.price_ticks}</td><td>{level.quantity}</td><td>{cumulative.toString()}</td>
   </tr>))}</tbody>
  </table>
 </div>;
}

export function DepthChart({state}:{state?:TerminalState}){
 const bids=state?.book.bids||[],asks=state?.book.asks||[];
 if(!state||(!bids.length&&!asks.length))return <div className="empty-state">No depth available for the current mode.</div>;
 const totals=[bids,asks].map(levels=>levels.reduce((sum,level)=>sum+BigInt(level.quantity),0n));
 const maximum=totals.reduce((max,n)=>n>max?n:max,1n);
 const project=(levels:typeof bids,bid:boolean)=>{
  let cumulative=0n;
  return levels.map((level,i)=>{
   cumulative+=BigInt(level.quantity);
   return {x:bid?250-(i+1)/Math.max(1,levels.length)*225:250+(i+1)/Math.max(1,levels.length)*225,y:170-chartRatio(cumulative,maximum)*135,level,cumulative};
  });
 };
 const sides:DepthSide[]=[{label:'Bid',points:project(bids,true)},{label:'Ask',points:project(asks,false)}];
 return <figure className="depth-svg depth-figure"><div className="depth-scale"><span>Cumulative source quantity</span><b>{price(maximum.toString(),String(state?.quantity_scale||1))} max</b></div>
  <svg viewBox="0 0 500 200" role="img" aria-label="Cumulative bid and ask depth by occupied price level">
   <path className="chart-grid" d="M25 35H475M25 102H475M25 170H475M250 20V175"/>
   {sides.map(({label,points})=>{
    if(!points.length)return null;
    const bid=label==='Bid';
    const d=points.map((p,i)=>i?`H${p.x}V${p.y}`:`M250,${p.y}H${p.x}`).join(' ');
    return <g key={bid?'bid':'ask'}><path className={bid?'bid-area':'ask-area'} d={d+`L${points.at(-1)!.x},170H250Z`}/><path className={bid?'bid-line':'ask-line'} d={d}/>
     {points.map((p,i)=><circle key={p.level.price_ticks} cx={p.x} cy={p.y} r={2.5} className={bid?'bid-point':'ask-point'}><title>{`${label} rank ${i+1} · price ${price(p.level.price_ticks,state.price_scale)} · exact cumulative quantity ${p.cumulative} / scale ${String(state.quantity_scale||1)}`}</title></circle>)}
    </g>;
   })}
   <text x="25" y="193" className="depth-axis-label">Farther bid ranks</text><text x="250" y="193" textAnchor="middle" className="depth-axis-label">Best levels</text><text x="475" y="193" textAnchor="end" className="depth-axis-label">Farther ask ranks</text>
  </svg>
  <div className="depth-labels"><span className="bid-text">BIDS · {bids.length} occupied levels · {price(totals[0].toString(),String(state?.quantity_scale||1))} total</span><span className="ask-text">ASKS · {asks.length} occupied levels · {price(totals[1].toString(),String(state?.quantity_scale||1))} total</span></div>
  <ExactDepthDisclosure><DepthValues sides={sides} state={state}/></ExactDepthDisclosure>
  <figcaption className="chart-caption">Cumulative displayed quantity · horizontal spacing by level rank,not price distance. Steps describe supplied occupied levels;no hidden liquidity is inferred.</figcaption>
 </figure>;
}
