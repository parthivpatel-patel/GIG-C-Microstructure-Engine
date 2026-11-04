import type {CSSProperties} from 'react';
import type {TerminalState} from './contracts';
import {price,rational,chartRatio} from './format';
import {displayedLadder} from './bookPresentation';

export function OrderBook({state,expanded=false,compact=false}:{state:TerminalState;expanded?:boolean;compact?:boolean}){
 const limit=expanded?40:compact?5:10;
 const bids=displayedLadder(state.book.bids,limit),asks=displayedLadder(state.book.asks,limit);
 const maximum=[...bids,...asks].reduce((max,row)=>BigInt(row.quantity)>max?BigInt(row.quantity):max,1n);
 const quantities=String(state.quantity_scale||'1');
 const ladder=(rows:typeof bids,side:'bid'|'ask')=><div className={'ladder-side '+side}>
  <div className="ladder-title"><span><i className={'dot '+side}/>{side==='bid'?'Bids':'Asks'}</span><span>{rows.length} levels</span></div>
  <div className="ladder-scroll" tabIndex={0} aria-label={side+' price ladder'}>
   <table className="book-table"><caption className="sr-only">{side==='bid'?'Bid':'Ask'} prices,size and cumulative displayed quantity</caption>
    <thead><tr><th scope="col">Price</th><th scope="col">Size</th><th scope="col">Cumulative</th></tr></thead>
    <tbody>{rows.map(row=><tr key={row.price_ticks} className={'book-row '+side} tabIndex={0}
     title={`Exact ${side} price ticks ${row.price_ticks}; quantity ${row.quantity}; cumulative ${row.cumulative}`}
     style={{'--row-depth':`${chartRatio(BigInt(row.quantity),maximum)*100}%`} as CSSProperties}>
     <th scope="row">{price(row.price_ticks,state.price_scale)}</th>
     <td>{price(row.quantity,quantities)}</td><td>{price(row.cumulative,quantities)}</td>
    </tr>)}</tbody>
   </table>
   {!rows.length&&<p className="empty-state">No accepted {side} levels</p>}
  </div>
 </div>;
 return <section className="panel orderbook-panel" aria-label="Displayed order book">
  <header className="panel-header"><div><span className="eyebrow">OCCUPIED PRICE LEVELS</span><h2>Order book</h2></div><span className="tag">{state.feed_type==='L2_AGGREGATE'?'L2 AGGREGATE':'NATIVE L3 · DISPLAYED DEPTH'}</span></header>
  <div className="book-market-summary"><div><span>Best bid</span><strong className="bid-text">{price(state.book.bids[0]?.price_ticks,state.price_scale)}</strong></div><div><span>Spread · source price units</span><strong>{rational(state.metrics.spread,state.price_scale)}</strong></div><div><span>Best ask</span><strong className="ask-text">{price(state.book.asks[0]?.price_ticks,state.price_scale)}</strong></div></div>
  <div className="book-ladders">{ladder(bids,'bid')}{ladder(asks,'ask')}</div>
  <div className="book-foot"><span>{state.origin} · showing {bids.length}/{state.book.bids.length} bid and {asks.length}/{state.book.asks.length} ask levels</span><span>Size and cumulative values retain source units · price scale {state.price_scale} · quantity scale {quantities}. Displayed totals only;no inferred hidden orders or queue identities.</span></div>
 </section>;
}
