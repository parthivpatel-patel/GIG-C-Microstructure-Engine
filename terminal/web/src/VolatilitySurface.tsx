import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/examples/jsm/controls/OrbitControls.js';
export type Point={strike:number;years:number;volatility:number;theoretical_price?:number|null;reason?:string};
export function VolatilitySurface({rows,pointsOnly=false}:{rows:Point[][];pointsOnly?:boolean}){
 const host=useRef<HTMLDivElement>(null),[fallback,setFallback]=useState(false);
 useEffect(()=>{if(!host.current)return;const container=host.current;let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,1.5))}catch{setFallback(true);return}
  const scene=new THREE.Scene();scene.background=new THREE.Color('#0c1119');const camera=new THREE.PerspectiveCamera(40,1,.1,100);camera.position.set(10,8,13);const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,1,0);controls.update();container.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-label',pointsOnly?'Indicative provider-IV observation points;drag to rotate':'Theoretical constant-volatility surface;drag to rotate');renderer.domElement.dataset.testid=pointsOnly?'observed-volatility-canvas':'volatility-canvas';
  const points=rows.flat(),minK=Math.min(...points.map(p=>p.strike)),maxK=Math.max(...points.map(p=>p.strike)),maxV=Math.max(1,...points.map(p=>p.volatility));
  const vertices=points.flatMap(p=>[(p.strike-minK)/(maxK-minK||1)*10-5,p.volatility/maxV*5,p.years*8-4]);const indices:number[]=[];
  for(let i=0;i<rows.length-1;i++)for(let j=0;j<rows[0].length-1;j++){const a=i*rows[0].length+j,b=a+rows[0].length;indices.push(a,b,a+1,a+1,b,b+1)}
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));if(!pointsOnly){geometry.setIndex(indices);geometry.computeVertexNormals()}const material=pointsOnly?new THREE.PointsMaterial({color:0x35cdb0,size:.16}):new THREE.MeshBasicMaterial({color:0x35cdb0,wireframe:true,side:THREE.DoubleSide});scene.add(pointsOnly?new THREE.Points(geometry,material as THREE.PointsMaterial):new THREE.Mesh(geometry,material));const grid=new THREE.GridHelper(12,12);scene.add(grid);
  const render=()=>{if(document.visibilityState==='visible')renderer.render(scene,camera)};controls.addEventListener('change',render);document.addEventListener('visibilitychange',render);const resize=new ResizeObserver(()=>{if(container.clientWidth){renderer.setSize(container.clientWidth,300);camera.aspect=container.clientWidth/300;camera.updateProjectionMatrix();render()}});resize.observe(container);render();
  return()=>{resize.disconnect();document.removeEventListener('visibilitychange',render);controls.dispose();geometry.dispose();material.dispose();grid.geometry.dispose();(grid.material as THREE.Material).dispose();renderer.dispose();renderer.domElement.remove()};
 },[rows,pointsOnly]);
 return <><div ref={host} style={{height:300}}/>{fallback&&<p>WebGL unavailable; inspect the exact scenario grid below.</p>}<p className="panel-note">X:strike · Y:input volatility · Z:years. {pointsOnly?'Discrete indicative provider-IV points only;no interpolation or calibrated surface. Calendar years measured from server receipt date,not an option valuation convention.':'Flat constant-volatility model plane, not an observed market smile.'} Drag/pinch to inspect. No continuous animation loop.</p></>
}
