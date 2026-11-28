import {useEffect,useId,useRef,useState} from 'react';
import {searchKeyboard,searchResultId,searchSignature,activeSearchIndex} from './searchKeyboard';
import type {Workspace} from './Navigation';
type Props={section:Workspace;collapsed:boolean;onCollapse:()=>void;theme:string;onTheme:()=>void;onHelp:()=>void;transport:string;query:string;onQuery:(value:string)=>void;onSearch:()=>void;results:{symbol:string;company_name:string}[];message:string;onSelect:(symbol:string)=>void};
export function TerminalHeader(p:Props){
 const input=useRef<HTMLInputElement>(null),options=useRef<(HTMLButtonElement|null)[]>([]),id=useId(),resultId=`${id}-results`,instructionsId=`${id}-instructions`;
 const signature=searchSignature(p.query,p.results),[active,setActive]=useState({signature:'',index:-1});
 const activeIndex=activeSearchIndex(active,signature,p.results.length);
 const activeId=activeIndex<0?undefined:searchResultId(resultId,activeIndex);
 useEffect(()=>{if(activeIndex>=0)options.current[activeIndex]?.scrollIntoView({block:'nearest',behavior:'auto'})},[activeIndex,signature]);
 function clearActive(){setActive({signature:'',index:-1})}
 function select(index:number){const result=p.results[index];if(result){clearActive();p.onSelect(result.symbol)}}

 useEffect(()=>{const keyboard=(e:KeyboardEvent)=>{const editing=e.target instanceof HTMLElement&&(e.target.isContentEditable||!!e.target.closest('input,textarea,select'));if(e.isComposing)return;if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'||e.key==='/'&&!editing&&!e.ctrlKey&&!e.metaKey&&!e.altKey){e.preventDefault();input.current?.focus()}};document.addEventListener('keydown',keyboard);return()=>document.removeEventListener('keydown',keyboard)},[]);
 return <header className="topbar gig-topbar">
  <div className="workspace-location"><button className="atlas-navigation-toggle" aria-label="Toggle workspace navigation" aria-controls="atlas-sections" aria-expanded={!p.collapsed} onClick={p.onCollapse}><svg aria-hidden="true" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="2" y="3" width="16" height="14" rx="2"/><path d="M7 3v14"/></svg><span>{p.collapsed?'Show navigation':'Compact navigation'}</span></button><span className="breadcrumb">GIG <span>/</span> <b>{p.section}</b></span></div>
  <form className="atlas-global-search" role="search" aria-label="Global security search" onBlur={e=>{
   if(e.relatedTarget instanceof Node&&!e.currentTarget.contains(e.relatedTarget)){
    clearActive();p.onQuery(p.query);
   }
  }} onSubmit={e=>{e.preventDefault();clearActive();p.onSearch()}}>
   <svg aria-hidden="true" width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="8.5" cy="8.5" r="5.5"/><path d="m13 13 4 4"/></svg>
   <input ref={input} type="search" role="combobox" aria-label="Global company search" aria-autocomplete="list" aria-haspopup="listbox" aria-expanded={p.results.length>0} aria-controls={p.results.length?resultId:undefined} aria-activedescendant={activeId} aria-describedby={instructionsId} placeholder="Search companies & securities" autoComplete="off" maxLength={80} value={p.query} onKeyDown={e=>{
    const action=searchKeyboard({key:e.key,altKey:e.altKey,ctrlKey:e.ctrlKey,metaKey:e.metaKey,shiftKey:e.shiftKey,isComposing:e.nativeEvent.isComposing},p.results.length,activeIndex);
    if(action.kind==='none'){
     if(e.key==='Escape'&&!e.nativeEvent.isComposing){clearActive();p.onQuery(p.query)}
     return;
    }
    e.preventDefault();
    if(action.kind==='move')setActive({signature,index:action.index});
    else if(action.kind==='select')select(action.index);
    else {clearActive();p.onQuery(p.query)}
   }} onChange={e=>{clearActive();p.onQuery(e.target.value)}}/>
   <button aria-label="Search companies">Search</button><kbd aria-hidden="true">⌘ K</kbd>
   <span id={instructionsId} className="sr-only">Search to load company results. Use Up and Down Arrow to choose a result, Enter to open it, and Escape to dismiss results without changing the query. Tab moves to the next control.</span>
   <span role="status" aria-live="polite" aria-atomic="true" className="sr-only">{p.message||(p.results.length?`${p.results.length} company search ${p.results.length===1?'result':'results'} for ${p.query}. Use Up and Down Arrow to choose.`:'')}</span>
   {p.results.length>0&&<div id={resultId} className="atlas-search-results" role="listbox" aria-label="Company search results">{p.results.map((r,index)=><button ref={element=>{options.current[index]=element}} type="button" role="option" tabIndex={-1} id={searchResultId(resultId,index)} key={r.symbol} aria-selected={activeIndex===index} aria-label={`${r.symbol} · ${r.company_name}`} onMouseDown={e=>e.preventDefault()} onClick={()=>select(index)}><strong>{r.symbol}</strong><span>{r.company_name}</span><span aria-hidden="true">↗</span></button>)}</div>}
   {p.message&&<p className="atlas-search-results">{p.message}</p>}
  </form>
  <div className="topbar-health"><span className="transport-block"><span className="transport-context">Native transport</span><span className="transport" data-testid="connection-status"><i className={p.transport==='CONNECTED'?'online':''}/>{p.transport}</span></span><button className="theme-toggle" aria-label="Toggle color theme" onClick={p.onTheme}>{p.theme==='dark'?'Light':'Dark'}</button><button className="help-toggle" aria-label="Research help" onClick={p.onHelp}>?</button></div>
 </header>;
}
