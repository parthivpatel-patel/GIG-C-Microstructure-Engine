import {OptionalBoundary} from './OptionalBoundary';
import {lazy,Suspense,useState} from 'react';
import type {TerminalState} from './contracts';
import {DepthChart} from './DepthChart';
export {DepthChart} from './DepthChart';
const ThreeLandscape=lazy(()=>import('./Landscape3D').then(m=>({default:m.Landscape})));
export function Landscape({history,fallback=false}:{history:TerminalState[];fallback?:boolean}){
 const [enabled,setEnabled]=useState(false);
 if(enabled&&!fallback)return <OptionalBoundary fallback={<DepthChart state={history.at(-1)}/>}><Suspense fallback={<section className="panel loading-panel" role="status">Loading optional 3D renderer… 2D depth remains available below.<DepthChart state={history.at(-1)}/></section>}><ThreeLandscape history={history}/></Suspense></OptionalBoundary>;
 return <section className="panel landscape-panel" aria-label="Liquidity landscape"><header className="panel-header"><div><span className="eyebrow">SOURCE-AWARE LIQUIDITY</span><h2>Liquidity landscape <span className="tag">2D</span></h2></div><button disabled={fallback} onClick={()=>setEnabled(true)}>Enable 3D landscape</button></header><div className="fallback-view" data-testid="landscape-fallback"><DepthChart state={history.at(-1)}/><p>Current native observation · cumulative depth. Optional 3D shows discrete retained observations.</p></div><p className="panel-note">3D is loaded only on request. No interpolation, inferred orders or synthetic-to-observed relabeling.</p></section>;
}
