import {WorkspaceIcon} from './WorkspaceIcon';
export type Workspace = 'Command Center'|'Securities Universe'|'Stock Intelligence'|'Live Markets'|'Multi-Stock Comparison'|'Order Book'|'Market Depth'|'Order Flow'|'Historical Replay'|'Execution Simulator'|'Research & Validation'|'Operations';
const groups: {label:string;items:Workspace[]}[] = [
 {label:'Workspace',items:['Command Center']},
 {label:'Market structure',items:['Order Book','Market Depth','Order Flow','Live Markets','Multi-Stock Comparison']},
 {label:'Research',items:['Securities Universe','Stock Intelligence','Historical Replay','Execution Simulator','Research & Validation']},
 {label:'System',items:['Operations']}
];
export function Navigation({selected,onSelect}:{selected:Workspace;onSelect:(name:Workspace)=>void}){
 return <aside className="sidebar gig-navigation">
  <a className="brand" href="#workspace-main" aria-label="GIG Order Book & Market Microstructure Terminal">
   <span className="brand-mark" aria-hidden="true"><i/><i/><i/></span>
   <span><strong>GIG</strong><span className="brand-sub">Order Book & Market<br/>Microstructure Terminal</span></span>
  </a>
  <nav id="atlas-sections" aria-label="Research sections">
   {groups.map(group=><div className="navigation-group" key={group.label}>
    <span className="navigation-heading">{group.label}</span>
    {group.items.map(name=><button key={name} title={name} aria-label={name}
      aria-current={selected===name?'page':undefined} className={selected===name?'active':''}
      onClick={()=>onSelect(name)}>
     <span className="nav-icon"><WorkspaceIcon name={name}/></span>
     <span className="navigation-label">{name}</span>
    </button>)}
   </div>)}
  </nav>
  <div className="sidebar-bottom"><span className="native-indicator"><i/> C++20 NATIVE CORE</span>
   <p>C++20 Research &amp;<br/>Execution Simulation</p>
   <span className="version-tag">PRIVATE · RESEARCH ONLY</span>
  </div>
 </aside>;
}
