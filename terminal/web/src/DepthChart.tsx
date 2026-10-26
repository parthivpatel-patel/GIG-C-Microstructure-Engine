import type {TerminalState} from './contracts';
import {chartRatio} from './format';
export function DepthChart({state}:{state?:TerminalState}){
 const bids=state?.book.bids||[],asks=state?.book.asks||[],values=[...bids,...asks];if(!values.length)return <div className="empty-state">No depth available for the current mode.</div>;
 let max=1n;for(const side of [bids,asks]){let total=0n;for(const l of side)total+=BigInt(l.quantity);if(total>max)max=total;}
 const path=(side:typeof bids,bid:boolean)=>{let sum=0n;return side.map((l,i)=>{sum+=BigInt(l.quantity);const x=bid?250-(i+1)/Math.max(1,side.length)*230:250+(i+1)/Math.max(1,side.length)*230,y=160-chartRatio(sum,max)*130;return `${i?'L':'M'}${x},${y}`}).join(' ')};
 return <div className="depth-svg"><svg viewBox="0 0 500 180" role="img" aria-label="Cumulative bid and ask depth by occupied price level"><path className="chart-grid" d="M20 30H480M20 95H480M20 160H480M250 15V165"/><path className="bid-line" d={path(bids,true)}/><path className="ask-line" d={path(asks,false)}/></svg><div className="depth-labels"><span className="bid-text">BIDS · {bids.length} occupied levels</span><span className="ask-text">ASKS · {asks.length} occupied levels</span></div><span className="chart-caption">Cumulative displayed quantity · horizontal spacing by level rank, not price distance</span></div>
}
