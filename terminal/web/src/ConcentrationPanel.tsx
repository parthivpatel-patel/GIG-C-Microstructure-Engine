import type {TerminalState,Fraction} from './contracts';
import {researchFraction} from './format';
type Metric={schema:string;status:string;reason:string|null;side:string;selected_levels:number;requested_depth_per_side:number;hhi:Fraction|null;normalized_hhi:Fraction|null};
export function ConcentrationPanel({state}:{state:TerminalState}){
 const metric=(state.research_metrics as {concentration?:Metric}|undefined)?.concentration;
 return <section className="panel" aria-label="Proposed supplied-depth concentration"><header className="panel-header"><h2>Supplied-depth concentration</h2><span className="atlas-badge">PROPOSED RESEARCH v1</span></header><div className="panel-content">
 <p>Exact quantity-share HHI on supplied bid and ask levels. This research definition is a proposal;the historical metric-definition requirement remains open.</p>
 {metric?.schema==='gig.research.supplied_depth_concentration.v1'&&metric.status==='AVAILABLE_SUPPLIED_SUBSET'?<><dl data-testid="concentration-result"><dt>HHI · dimensionless</dt><dd>{researchFraction(metric.hhi)}</dd><dt>Normalized concentration · dimensionless</dt><dd>{researchFraction(metric.normalized_hhi)}</dd></dl><p>{metric.selected_levels} supplied levels · both sides · up to {metric.requested_depth_per_side} per side</p></>:<p role="status">Concentration unavailable: {metric?.reason||'eligible supplied depth required'}.</p>}
 <p className="panel-note">{state.origin} · {state.provider} · {state.instrument}. Not full-book,full-market,executable-liquidity or observed L3 completeness. More concentrated supplied quantities increase HHI;comparisons require the same side and depth scope.</p>
 <details><summary>Exact concentration,formula scope and source lineage</summary><pre>{JSON.stringify(metric??{status:'UNAVAILABLE'},null,2)}</pre></details></div></section>;
}
