import type {TerminalState} from './contracts';
import {chartRatio,price} from './format';

export function DepthChart({state}:{state?:TerminalState}){
 const bids=state?.book.bids||[],asks=state?.book.asks||[];
 if(!bids.length&&!asks.length)return <div className="empty-state">No depth available for the current mode.</div>;
 const totals=[bids,asks].map(levels=>levels.reduce((sum,level)=>sum+BigInt(level.quantity),0n));
 const maximum=totals.reduce((max,n)=>n>max?n:max,1n);
 const project=(levels:typeof bids,bid:boolean)=>{
  let cumulative=0n;
  return levels.map((level,i)=>{
   cumulative+=BigInt(level.quantity);
   return {x:bid?250-(i+1)/Math.max(1,levels.length)*225:250+(i+1)/Math.max(1,levels.length)*225,y:170-chartRatio(cumulative,maximum)*135,level,cumulative};
  });
 };
 return <figure className="depth-svg depth-figure"><div className="depth-scale"><span>Cumulative source quantity</span><b>{price(maximum.toString(),String(state?.quantity_scale||1))} max</b></div>
  <svg viewBox="0 0 500 200" role="img" aria-label="Cumulative bid and ask depth by occupied price level">
   <path className="chart-grid" d="M25 35H475M25 102H475M25 170H475M250 20V175"/>
   {[{levels:bids,bid:true},{levels:asks,bid:false}].map(({levels,bid})=>{
    const points=project(levels,bid);if(!points.length)return null;
    const d=points.map((p,i)=>i?`H${p.x}V${p.y}`:`M250,${p.y}H${p.x}`).join(' ');
    return <g key={bid?'bid':'ask'}><path className={bid?'bid-area':'ask-area'} d={d+`L${points.at(-1)!.x},170H250Z`}/><path className={bid?'bid-line':'ask-line'} d={d}/>
     {points.map((p,i)=><circle key={p.level.price_ticks} cx={p.x} cy={p.y} r={2.5} className={bid?'bid-point':'ask-point'}><title>{bid?'Bid':'Ask'} rank{i+1} · price {price(p.level.price_ticks,state!.price_scale)} · exact cumulative quantity {p.cumulative.toString()} / scale {String(state?.quantity_scale||1)}</title></circle>)}
    </g>;
   })}
   <text x="25" y="193" className="depth-axis-label">Farther bid ranks</text><text x="250" y="193" textAnchor="middle" className="depth-axis-label">Best levels</text><text x="475" y="193" textAnchor="end" className="depth-axis-label">Farther ask ranks</text>
  </svg>
  <div className="depth-labels"><span className="bid-text">BIDS · {bids.length} occupied levels · {price(totals[0].toString(),String(state?.quantity_scale||1))} total</span><span className="ask-text">ASKS · {asks.length} occupied levels · {price(totals[1].toString(),String(state?.quantity_scale||1))} total</span></div>
  <figcaption className="chart-caption">Cumulative displayed quantity · horizontal spacing by level rank,not price distance. Steps describe supplied occupied levels;no hidden liquidity is inferred.</figcaption>
 </figure>;
}
