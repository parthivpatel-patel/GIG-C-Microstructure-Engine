import {Component} from 'react';
import type {ReactNode} from 'react';
/** A missing optional deployment chunk must not take down native transport/navigation. */
export class OptionalBoundary extends Component<{children:ReactNode;fallback?:ReactNode},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 render(){return this.state.failed?<section className="panel" role="alert"><div className="panel-content"><h2>Optional workspace could not load</h2><p>The current native state is unchanged. Use the available 2D/table views or reload the page to obtain matching deployment assets.</p>{this.props.fallback}<button onClick={()=>location.reload()}>Reload application assets</button></div></section>:this.props.children;}
}
