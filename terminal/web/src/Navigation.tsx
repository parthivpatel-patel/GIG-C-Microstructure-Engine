import {WorkspaceIcon} from './WorkspaceIcon';
export type Workspace = 'Command Center'|'Securities Universe'|'Stock Intelligence'|'Live Markets'|'Multi-Stock Comparison'|'Order Book'|'Market Depth'|'Order Flow'|'Historical Replay'|'Execution Simulator'|'Research & Validation'|'Operations';
const groups: {label:string;items:Workspace[]}[] = [
 {label:'Overview',items:['Command Center']},
 {label:'Markets',items:['Securities Universe','Stock Intelligence','Live Markets','Multi-Stock Comparison']},
 {label:'Microstructure',items:['Order Book','Market Depth','Order Flow']},
 {label:'Laboratory',items:['Historical Replay','Execution Simulator','Research & Validation']},
 {label:'System',items:['Operations']}
];
export function Navigation({selected,onSelect}:{selected:Workspace;onSelect:(name:Workspace)=>void}){
 return <aside className="sidebar gig-navigation">
  <a className="brand" href="#workspace-main" aria-label="GIG Order Book & Market Microstructure Terminal">
   <span className="brand-mark" aria-hidden="true"><i/><i/><i/></span>
   <span><strong>GIG</strong><span className="brand-sub">RESEARCH WORKSTATION</span></span>
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
   <p>Private workspace<br/>Personal research. No trading.</p>
   <span className="version-tag">PRIVATE · RESEARCH ONLY</span>
  </div>
 </aside>;
}
