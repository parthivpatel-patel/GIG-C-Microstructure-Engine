import test from 'node:test';
import assert from 'node:assert/strict';
import {createCameraMotion} from './cameraMotion.ts';
function harness(){let identity=0;const queue=new Map<number,(t:number)=>void>(),steps:number[]=[],states:string[]=[];
 const motion=createCameraMotion({request:f=>{queue.set(++identity,f);return identity},cancel:id=>{queue.delete(id)},step:s=>steps.push(s),state:s=>states.push(s)});
 return {motion,queue,steps,states,tick(t:number){const current=[...queue.values()];queue.clear();current.forEach(f=>f(t))}};
}
test('automatic camera starts with a single scheduled loop',()=>{const h=harness();h.motion.set('empty',false);h.motion.set('hidden',false);assert.equal(h.queue.size,1);h.tick(0);h.tick(40);assert.equal(h.steps.length,1);assert.equal(h.queue.size,1)});
test('frame time controls angle and busy frames are clamped',()=>{const h=harness();h.motion.set('paused',false);h.tick(0);h.tick(40);h.tick(10040);assert.deepEqual(h.steps,[.04,.1])});
test('30Hz cap avoids rendering on every refresh callback',()=>{const h=harness();h.motion.set('paused',false);for(let i=0;i<100;i++)h.tick(i);assert.equal(h.steps.length,2)});
for(const flag of ['paused','hidden','offscreen','reduced','empty','interacting']as const)test(flag+' suspends and resumes without catch-up or duplicate loops',()=>{const h=harness();h.motion.set(flag,true);assert.equal(h.queue.size,0);h.tick(100);assert.equal(h.steps.length,0);h.motion.set(flag,false);h.motion.set(flag,false);assert.equal(h.queue.size,1);h.tick(10000);h.tick(10040);assert.deepEqual(h.steps,[.04]);h.motion.set(flag,true);assert.equal(h.queue.size,0)});
test('multiple suspension reasons cannot override reduced motion',()=>{const h=harness();h.motion.set('reduced',true);h.motion.set('paused',true);h.motion.set('paused',false);assert.equal(h.queue.size,0);h.motion.set('reduced',false);assert.equal(h.queue.size,1)});
test('dispose cancels pending work and cannot restart',()=>{const h=harness();h.motion.set('empty',false);h.motion.dispose();h.motion.set('paused',false);h.tick(100);assert.equal(h.queue.size,0);assert.deepEqual(h.steps,[]);assert.equal(h.motion.state,'disposed')});
test('disposing or pausing inside a frame cannot resurrect a loop',()=>{let callback:((t:number)=>void)|undefined,n=0;const m=createCameraMotion({request:f=>{callback=f;return++n},cancel:()=>{callback=undefined},step:()=>m.dispose()});m.set('empty',false);callback!(0);callback!(40);assert.equal(m.state,'disposed');assert.equal(n,2)});
