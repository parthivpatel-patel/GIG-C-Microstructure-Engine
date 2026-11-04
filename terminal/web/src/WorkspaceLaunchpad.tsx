import {ArrowIcon} from './WorkspaceIcon';
import type {TerminalState} from './contracts';
import type {Workspace} from './Navigation';
import {price,chartRatio} from './format';
export function WorkspaceLaunchpad({state,onNavigate}:{state:TerminalState|null;onNavigate:(name:Workspace)=>void}){
 const levels=[...(state?.book.bids||[]).slice(0,10),...(state?.book.asks||[]).slice(0,10)];
 const max=levels.reduce((v,row)=>BigInt(row.quantity)>v?BigInt(row.quantity):v,1n);
 return <section className="gig-launchpad" aria-label="Microstructure research overview">
  <div className="launchpad-intro"><span className="eyebrow">THE GIG RESEARCH DESK</span><h2>Find your next<br/><em>point of view.</em></h2><p>Company context. Market observations. Native experiments. One workspace, with every source in focus.</p><div className="desk-actions"><button className="primary-button" onClick={()=>onNavigate('Securities Universe')}>Explore securities <span aria-hidden="true"><ArrowIcon/></span></button><button onClick={()=>onNavigate('Historical Replay')}>Open replay</button></div><span className="launchpad-caption">Private by design · no live-money execution</span></div>
  <div className="launchpad-native"><div className="launchpad-native-heading"><span className="eyebrow">NATIVE LAB / CURRENT SNAPSHOT</span><span className="tag">{state?.origin||'UNAVAILABLE'}</span></div><div className="launchpad-market-title"><h3>{state?.instrument||'Awaiting native engine'}</h3><button onClick={()=>onNavigate('Order Book')}>Inspect order book <ArrowIcon/></button></div><div className="launchpad-quote"><div><span>Best bid</span><strong className="bid-text">{price(state?.book.bids[0]?.price_ticks,state?.price_scale||'1')}</strong></div><span aria-hidden="true">/</span><div><span>Best ask</span><strong className="ask-text">{price(state?.book.asks[0]?.price_ticks,state?.price_scale||'1')}</strong></div></div>
   <figure className="snapshot-profile"><svg viewBox="0 0 500 88" role="img" aria-label="Current native displayed quantities by price-level rank,not market history">{levels.map((row,i)=><rect key={i} x={i*24+6} y={84-chartRatio(BigInt(row.quantity),max)*70} width="17" height={chartRatio(BigInt(row.quantity),max)*70} rx="2" fill={i<Math.min(10,state?.book.bids.length||0)?'var(--bid)':'var(--ask)'}><title>Rank {i+1} · exact quantity {row.quantity} · {state?.origin}</title></rect>)}</svg><figcaption>{levels.length?'Displayed quantity · occupied level rank →':'No accepted displayed liquidity;no invented bars.'}</figcaption></figure>
   <dl><div><dt>Source position</dt><dd>{state?`${state.position} / ${state.event_count}`:'Unavailable'}</dd></div><div><dt>Occupied levels</dt><dd>{state?state.book.bids.length+state.book.asks.length:'Unavailable'}</dd></div><div><dt>Feed state</dt><dd>{state?.feed.state||'Unavailable'}</dd></div></dl>
  </div>
 </section>;
}
