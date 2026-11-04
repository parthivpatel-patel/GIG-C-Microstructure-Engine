import {ArrowIcon} from './WorkspaceIcon';
import type {ReactNode} from 'react';
import type {Workspace} from './Navigation';
import {workspaces} from './workstation';
export function WorkspaceHeading({section,children,onNavigate}:{section:Workspace;children:ReactNode;onNavigate:(name:Workspace)=>void}) {
 const page=workspaces[section];
 return <header className="workspace-heading" data-layout={page.layout}>
  <div className="workspace-heading-top"><span className="workspace-kicker"><b>{page.number}</b>{page.group}</span><div className="heading-tools">{children}</div></div>
  <div className="workspace-heading-body"><div><h1>{section}<span className="title-dot">.</span></h1><p>{page.description}</p></div><nav className="workspace-shortcuts" aria-label="Related workspaces">{page.links.map(name=><button key={name} onClick={()=>onNavigate(name)}>{name}<span aria-hidden="true"><ArrowIcon/></span></button>)}</nav></div>
 </header>;
}
