import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import type {TerminalState} from './contracts';
import {chartRatio,price} from './format';
import {DepthChart} from './DepthChart';

type Inspection={side:string;price_ticks:string;quantity:string;position:number;time:string;scale:string;quantity_scale:string};
export function Landscape({history,fallback=false}:{history:TerminalState[];fallback?:boolean}) {
 const host=useRef<HTMLDivElement>(null),runtime=useRef<{renderer:THREE.WebGLRenderer;scene:THREE.Scene;camera:THREE.PerspectiveCamera;controls:OrbitControls;data:THREE.Group;render:()=>void;lookup:Map<THREE.Object3D,Inspection[]>}|null>(null);
 const [unavailable,setUnavailable]=useState(false),[twoD,setTwoD]=useState(fallback),[windowSize,setWindowSize]=useState(24),[depth,setDepth]=useState(10),[hover,setHover]=useState<Inspection|null>(null);
 const frames=history.slice(-windowSize),last=frames.at(-1),levels=frames.flatMap(f=>[...f.book.bids.slice(0,depth),...f.book.asks.slice(0,depth)]),allPrices=levels.map(l=>BigInt(l.price_ticks));
 const minimum=allPrices.length?allPrices.reduce((a,b)=>a<b?a:b):0n,maximum=allPrices.length?allPrices.reduce((a,b)=>a>b?a:b):1n;
 const timeAvailable=frames.length>0&&frames.every(f=>f.source_timestamp_ns||f.replay_time_ns),timeOf=(f:TerminalState)=>timeAvailable?BigInt(f.source_timestamp_ns||f.replay_time_ns||'0'):BigInt(f.position);
 useEffect(()=>{setTwoD(fallback)},[fallback]);
 useEffect(()=>{
  if(twoD||unavailable||!host.current)return;
  const container=host.current;let renderer:THREE.WebGLRenderer;
  try {renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'});renderer.setPixelRatio(Math.min(window.devicePixelRatio,1.5));}catch{setUnavailable(true);return;}
  const scene=new THREE.Scene();scene.background=new THREE.Color('#0c1119');
  const camera=new THREE.PerspectiveCamera(40,1,.1,100);camera.position.set(10,8,13);
  const controls=new OrbitControls(camera,renderer.domElement);controls.listenToKeyEvents(renderer.domElement);renderer.domElement.tabIndex=0;controls.target.set(0,1.5,0);controls.enableDamping=false;controls.minDistance=6;controls.maxDistance=35;controls.maxPolarAngle=Math.PI*.48;controls.update();
  const grid=new THREE.GridHelper(14,14,'#334455','#1a2735');grid.position.y=-.02;scene.add(grid);
  const data=new THREE.Group();scene.add(data);container.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-label','Interactive price by observation time by displayed liquidity');renderer.domElement.setAttribute('role','img');renderer.domElement.dataset.testid='liquidity-canvas';
  const lookup=new Map<THREE.Object3D,Inspection[]>();
  let lost=false;const contextLost=(event:Event)=>{event.preventDefault();lost=true;setHover(null);setUnavailable(true)};renderer.domElement.addEventListener('webglcontextlost',contextLost);
  const render=()=>{if(!lost&&document.visibilityState==='visible'){renderer.render(scene,camera);renderer.domElement.dataset.camera=camera.position.toArray().join(',')}};
  controls.addEventListener('change',render);
  const resize=new ResizeObserver(()=>{const w=container.clientWidth,h=container.clientHeight;if(w&&h){renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();render()}});resize.observe(container);
  const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();
  const move=(event:PointerEvent)=>{const rect=renderer.domElement.getBoundingClientRect();pointer.set((event.clientX-rect.left)/rect.width*2-1,-(event.clientY-rect.top)/rect.height*2+1);ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(data.children,false)[0];setHover(hit&&hit.instanceId!==undefined?lookup.get(hit.object)?.[hit.instanceId]||null:null)};
  const leave=()=>setHover(null);renderer.domElement.addEventListener('pointermove',move);renderer.domElement.addEventListener('pointerleave',leave);
  const visible=()=>render();document.addEventListener('visibilitychange',visible);
  runtime.current={renderer,scene,camera,controls,data,render,lookup};render();
  return()=>{resize.disconnect();controls.dispose();renderer.domElement.removeEventListener('pointermove',move);renderer.domElement.removeEventListener('pointerleave',leave);renderer.domElement.removeEventListener('webglcontextlost',contextLost);document.removeEventListener('visibilitychange',visible);for(const obj of data.children){const m=obj as THREE.InstancedMesh;m.geometry.dispose();(m.material as THREE.Material).dispose()}grid.geometry.dispose();(grid.material as THREE.Material).dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();runtime.current=null;};
 },[twoD,unavailable]);
 useEffect(()=>{
  const rt=runtime.current;if(!rt)return;
  for(const obj of rt.data.children)(obj as THREE.InstancedMesh).count=0;rt.lookup.clear();
  let maxQty=1n;for(const l of levels)if(BigInt(l.quantity)>maxQty)maxQty=BigInt(l.quantity);
  const span=maximum-minimum||1n,firstTime=frames.length?timeOf(frames[0]):0n,lastTime=last?timeOf(last):1n,timeSpan=lastTime-firstTime||1n;
  const dummy=new THREE.Object3D();
  for(const side of ['bids','asks'] as const){const entries=frames.flatMap(f=>f.book[side].slice(0,depth).map(l=>({side:side==='bids'?'BID':'ASK',price_ticks:l.price_ticks,quantity:l.quantity,position:f.position,time:timeOf(f).toString(),scale:f.price_scale,quantity_scale:String(f.quantity_scale||'1')})));if(!entries.length)continue;
   let mesh=rt.data.children.find(o=>o.name===side) as THREE.InstancedMesh|undefined;if(!mesh){mesh=new THREE.InstancedMesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial({color:side==='bids'?'#35cdb0':'#f27b89',transparent:true,opacity:.75}),960);mesh.name=side;mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);rt.data.add(mesh)}mesh.count=entries.length;const target=mesh;
   entries.forEach((entry,i)=>{const height=chartRatio(BigInt(entry.quantity),maxQty)*4;dummy.position.set(chartRatio(BigInt(entry.price_ticks)-minimum,span)*12-6,height/2,chartRatio(BigInt(entry.time)-firstTime,timeSpan)*10-5);dummy.scale.set(Math.min(.32,10/Math.max(10,allPrices.length)),Math.max(.015,height),Math.min(.36,8/Math.max(8,frames.length)));dummy.updateMatrix();target.setMatrixAt(i,dummy.matrix)});mesh.instanceMatrix.needsUpdate=true;mesh.computeBoundingSphere();rt.lookup.set(mesh,entries);
  }rt.render();
 },[history,windowSize,depth,twoD,unavailable]);
 const reset=()=>{const rt=runtime.current;if(rt){rt.camera.position.set(10,8,13);rt.controls.target.set(0,1.5,0);rt.controls.update();rt.render()}};
 return <section className="panel landscape-panel" aria-label="Liquidity landscape"><header className="panel-header"><div><span className="eyebrow">MICROSTRUCTURE EXPLORER</span><h2>Liquidity landscape <span className="tag">{twoD||unavailable?'2D':'3D'}</span></h2></div><div className="inline-controls"><label>Window<select aria-label="Landscape observation window" value={windowSize} onChange={e=>setWindowSize(Number(e.target.value))}><option value={8}>8 observations</option><option value={24}>24 observations</option><option value={48}>48 observations</option></select></label><label>Levels<select aria-label="Landscape price range" value={depth} onChange={e=>setDepth(Number(e.target.value))}><option value={5}>5 per side</option><option value={10}>10 per side</option><option value={20}>20 per side</option></select></label><button onClick={reset} disabled={twoD||unavailable} aria-label="Reset camera">↺</button><button onClick={()=>{if(unavailable){setUnavailable(false);setTwoD(false)}else setTwoD(!twoD)}} aria-pressed={twoD||unavailable}>{unavailable?'Retry 3D view':twoD?'3D view':'2D fallback'}</button></div></header>
 {(twoD||unavailable)?<div className="fallback-view" data-testid="landscape-fallback"><DepthChart state={last}/><p>{unavailable?'WebGL unavailable. ':''}Synchronized 2D depth • current observation only</p></div>:<div className="landscape-canvas" ref={host}>{!levels.length&&<div className="canvas-empty">Awaiting native book observations</div>}</div>}
 <div className="landscape-axes"><span>PRICE {price(minimum.toString(),last?.price_scale||'1')} → {price(maximum.toString(),last?.price_scale||'1')}</span><span>{timeAvailable?'SOURCE / REPLAY TIME (ns)':'CAPTURE ORDINAL — CLOCK UNAVAILABLE'}</span><span>HEIGHT = DISPLAYED QUANTITY</span></div>
 <div className="landscape-footer"><div><i className="dot bid"/> Bid liquidity <i className="dot ask"/> Ask liquidity <span className="muted">{frames.length} discrete observations · no interpolation</span></div><span className="muted">Drag rotate · pinch zoom · right-drag pan</span></div>
 {hover&&<div className="inspection" role="status">{hover.side} <b>{price(hover.price_ticks,hover.scale)}</b> · quantity <b>{price(hover.quantity,hover.quantity_scale)}</b> · {timeAvailable?'time':'ordinal'} {hover.time}</div>}
 </section>
}
