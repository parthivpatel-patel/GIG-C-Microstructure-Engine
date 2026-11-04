import {useEffect,useRef} from 'react';
import type {Workspace} from './Navigation';
type Props={section:Workspace;collapsed:boolean;onCollapse:()=>void;theme:string;onTheme:()=>void;onHelp:()=>void;transport:string;query:string;onQuery:(value:string)=>void;onSearch:()=>void;results:{symbol:string;company_name:string}[];message:string;onSelect:(symbol:string)=>void};
export function TerminalHeader(p:Props){
 const input=useRef<HTMLInputElement>(null);
 useEffect(()=>{const keyboard=(e:KeyboardEvent)=>{const editing=e.target instanceof HTMLElement&&!!e.target.closest('input,textarea,select,[contenteditable="true"]');if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'||e.key==='/'&&!editing&&!e.ctrlKey&&!e.metaKey&&!e.altKey){e.preventDefault();input.current?.focus()}};document.addEventListener('keydown',keyboard);return()=>document.removeEventListener('keydown',keyboard)},[]);
 return <header className="topbar gig-topbar">
  <div className="workspace-location"><button className="atlas-navigation-toggle" aria-label="Toggle workspace navigation" aria-controls="atlas-sections" aria-expanded={!p.collapsed} onClick={p.onCollapse}><svg aria-hidden="true" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="3" width="16" height="14" rx="2"/><path d="M7 3v14"/></svg><span>{p.collapsed?'Show navigation':'Compact navigation'}</span></button><span className="breadcrumb">GIG <span>/</span> <b>{p.section}</b></span></div>
  <form className="atlas-global-search" role="search" aria-label="Global security search" onSubmit={e=>{e.preventDefault();p.onSearch()}}>
   <svg aria-hidden="true" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="8.5" cy="8.5" r="5.5"/><path d="m13 13 4 4"/></svg>
   <input ref={input} aria-label="Global company search" placeholder="Search companies & securities" autoComplete="off" maxLength={80} value={p.query} onKeyDown={e=>{if(e.key==='Escape')p.onQuery(p.query)}} onChange={e=>p.onQuery(e.target.value)}/>
   <button aria-label="Search companies">Search</button><kbd aria-hidden="true">⌘ K</kbd>
   {p.results.length>0&&<div className="atlas-search-results" role="region" aria-label="Company search results">{p.results.map(r=><button type="button" key={r.symbol} aria-label={`${r.symbol} · ${r.company_name}`} onClick={()=>p.onSelect(r.symbol)}><strong>{r.symbol}</strong><span>{r.company_name}</span><span aria-hidden="true">↗</span></button>)}</div>}
   {p.message&&<p className="atlas-search-results" role="status">{p.message}</p>}
  </form>
  <div className="topbar-health"><span className="transport-block"><span className="transport-context">Native transport</span><span className="transport" data-testid="connection-status"><i className={p.transport==='CONNECTED'?'online':''}/>{p.transport}</span></span><button className="theme-toggle" aria-label="Toggle color theme" onClick={p.onTheme}>{p.theme==='dark'?'Light':'Dark'}</button><button className="help-toggle" aria-label="Research help" onClick={p.onHelp}>?</button></div>
 </header>;
}
