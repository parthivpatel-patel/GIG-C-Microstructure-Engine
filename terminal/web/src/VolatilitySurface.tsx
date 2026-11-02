import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
import {bindCameraMotion,OrbitButton,useOrbitPreference} from './OrbitMotion';
import type {CameraMotion} from './OrbitMotion';
export type Point={strike:number;years:number;volatility:number;theoretical_price?:number|null;reason?:string};

export function VolatilitySurface({rows,pointsOnly=false}:{rows:Point[][];pointsOnly?:boolean}){
 const host=useRef<HTMLDivElement>(null),runtime=useRef<{camera:THREE.PerspectiveCamera;controls:OrbitControls;motion:CameraMotion;draw:()=>void}|null>(null);
 const [fallback,setFallback]=useState(false),orbit=useOrbitPreference();
 useEffect(()=>{
  if(fallback||!host.current)return;
  const container=host.current;let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'low-power'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.25))}catch{setFallback(true);return}
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,1,.1,100);
  camera.position.set(10,8,13);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,1,0);controls.enableDamping=false;controls.minDistance=4;controls.maxDistance=40;controls.listenToKeyEvents(renderer.domElement);controls.update();
  container.appendChild(renderer.domElement);renderer.domElement.tabIndex=0;renderer.domElement.setAttribute('role','img');
  renderer.domElement.setAttribute('aria-label',pointsOnly?'Indicative provider-IV observation points;drag to rotate':'Theoretical constant-volatility surface;drag to rotate');renderer.domElement.dataset.testid=pointsOnly?'observed-volatility-canvas':'volatility-canvas';
  const points=rows.flat(),minK=Math.min(...points.map(p=>p.strike)),maxK=Math.max(...points.map(p=>p.strike)),maxV=Math.max(1,...points.map(p=>p.volatility));
  const vertices=points.flatMap(p=>[(p.strike-minK)/(maxK-minK||1)*10-5,p.volatility/maxV*5,p.years*8-4]),indices:number[]=[];
  for(let i=0;i<rows.length-1;i++)for(let j=0;j<rows[0].length-1;j++){const a=i*rows[0].length+j,b=a+rows[0].length;indices.push(a,b,a+1,a+1,b,b+1)}
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));if(!pointsOnly){geometry.setIndex(indices);geometry.computeVertexNormals()}
  const material=pointsOnly?new THREE.PointsMaterial({color:0x35cdb0,size:.16}):new THREE.MeshBasicMaterial({color:0x35cdb0,wireframe:true,side:THREE.DoubleSide});
  scene.add(pointsOnly?new THREE.Points(geometry,material as THREE.PointsMaterial):new THREE.Mesh(geometry,material));
  const grid=new THREE.GridHelper(12,12);scene.add(grid);let alive=true;
  const draw=()=>{if(alive&&document.visibilityState==='visible'){renderer.render(scene,camera);renderer.domElement.dataset.camera=camera.position.toArray().join(',');renderer.domElement.dataset.renderCount=String(Number(renderer.domElement.dataset.renderCount||0)+1)}};
  const motion=bindCameraMotion(container,renderer.domElement,controls,draw,orbit.current.current);motion.set('empty',points.length===0);
  runtime.current={camera,controls,motion,draw};
  const changed=()=>{if(!motion.stepping)draw()};controls.addEventListener('change',changed);
  const theme=()=>{scene.background=new THREE.Color(getComputedStyle(document.documentElement).getPropertyValue('--atlas-bg').trim()||'#101722');draw()};
  const themeObserver=new MutationObserver(theme);themeObserver.observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});theme();
  const resize=new ResizeObserver(()=>{if(container.clientWidth&&container.clientHeight){renderer.setSize(container.clientWidth,container.clientHeight,false);camera.aspect=container.clientWidth/container.clientHeight;camera.updateProjectionMatrix();draw()}});resize.observe(container);
  const lost=(event:Event)=>{event.preventDefault();setFallback(true)};renderer.domElement.addEventListener('webglcontextlost',lost);
  return()=>{alive=false;runtime.current=null;motion.dispose();themeObserver.disconnect();resize.disconnect();controls.dispose();renderer.domElement.removeEventListener('webglcontextlost',lost);geometry.dispose();material.dispose();grid.geometry.dispose();(grid.material as THREE.Material).dispose();renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove()};
 },[rows,pointsOnly,fallback]);
 useEffect(()=>{runtime.current?.motion.set('paused',orbit.paused)},[orbit.paused]);
 const reset=()=>{const r=runtime.current;if(r){r.camera.position.set(10,8,13);r.controls.target.set(0,1,0);r.controls.update();r.draw()}};
 return <><div className="inline-controls"><OrbitButton paused={orbit.paused} onToggle={orbit.toggle} disabled={fallback}/><button onClick={reset} disabled={fallback}>Reset option camera</button><button onClick={()=>setFallback(!fallback)}>{fallback?'Retry option 3D':'Use option 2D table'}</button></div>{fallback?<p role="status">WebGL off or unavailable;inspect the exact scenario grid below.</p>:<div ref={host} className="atlas-analysis-canvas"/>}<p className="panel-note">X:strike · Y:input volatility · Z:years. {pointsOnly?'Discrete indicative provider-IV points only;no interpolation or calibrated surface. Calendar years measured from server receipt date,not an option valuation convention.':'Flat constant-volatility model plane,not an observed market smile.'} Slow camera orbit changes only the viewpoint;the exact inputs remain in the table.</p></>;
}
