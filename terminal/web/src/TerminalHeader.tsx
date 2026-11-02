import type {Workspace} from './Navigation';
type Props={section:Workspace;collapsed:boolean;onCollapse:()=>void;theme:string;onTheme:()=>void;onHelp:()=>void;transport:string;query:string;onQuery:(value:string)=>void;onSearch:()=>void;results:{symbol:string;company_name:string}[];message:string;onSelect:(symbol:string)=>void};
export function TerminalHeader(p:Props){
 return <header className="topbar gig-topbar">
  <div className="workspace-location"><button className="atlas-navigation-toggle" aria-label="Toggle workspace navigation" aria-controls="atlas-sections" aria-expanded={!p.collapsed} onClick={p.onCollapse}>{p.collapsed?'Show navigation':'Compact navigation'}</button>
   <span className="breadcrumb">GIG <span>/</span> <b>{p.section}</b></span>
  </div>
  <form className="atlas-global-search" role="search" onSubmit={e=>{e.preventDefault();p.onSearch()}}>
   <span className="search-glyph" aria-hidden="true">⌕</span>
   <input aria-label="Global company search" placeholder="Find a security or company" maxLength={80} value={p.query} onChange={e=>p.onQuery(e.target.value)}/>
   <button aria-label="Search companies">Search</button>
   {p.results.length>0&&<div className="atlas-search-results" role="region" aria-label="Company search results">
    {p.results.map(r=><button type="button" key={r.symbol} aria-label={`${r.symbol} · ${r.company_name}`} onClick={()=>p.onSelect(r.symbol)}><strong>{r.symbol}</strong><span>{r.company_name}</span></button>)}
   </div>}
   {p.message&&<p className="atlas-search-results" role="status">{p.message}</p>}
  </form>
  <div className="topbar-health">
   <span className="transport-block"><span className="transport-context">Native API</span><span className="transport" data-testid="connection-status"><i className={p.transport==='CONNECTED'?'online':''}/>{p.transport}</span></span>
   <button className="theme-toggle" aria-label="Toggle color theme" onClick={p.onTheme}>{p.theme==='dark'?'Light':'Dark'}</button>
   <button aria-label="Research help" onClick={p.onHelp}>Help</button>
  </div>
 </header>;
}
