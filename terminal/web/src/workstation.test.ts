import test from 'node:test';
import assert from 'node:assert/strict';
import {workspaces,sceneActivity} from './workstation.ts';
test('all twelve retained workspaces have distinct purposeful compositions',()=>{
 assert.equal(Object.keys(workspaces).length,12);
 assert.equal(new Set(Object.values(workspaces).map(w=>w.layout)).size,12);
 assert.deepEqual(Object.values(workspaces).map(w=>w.number),Array.from({length:12},(_,i)=>String(i+1).padStart(2,'0')));
});
test('workspace shortcuts resolve to real existing destinations,never to themselves',()=>{
 for(const [name,page] of Object.entries(workspaces))for(const link of page.links){assert.ok(link in workspaces);assert.notEqual(link,name)}
});
test('research context explicitly separates IEX Level 1,authored replay and simulated execution',()=>{
 assert.match(workspaces['Live Markets'].description,/Level 1/);
 assert.match(workspaces['Historical Replay'].description,/synthetic/);
 assert.match(workspaces['Execution Simulator'].description,/execution stay disabled/);
 assert.doesNotMatch(JSON.stringify(workspaces),/GIG ATLAS|GIG Quant Terminal|GIG Research Terminal/);
});
test('static-scene reasons distinguish reduced motion,missing data and camera pause',()=>{
 assert.match(sceneActivity('empty'),/eligible input/);
 assert.match(sceneActivity('reduced'),/Reduced motion/);
 assert.match(sceneActivity('paused'),/paused/);
 assert.match(sceneActivity('orbiting'),/camera only/);
 assert.equal(new Set(['empty','reduced','paused','orbiting','hidden','offscreen','interacting','disposed'].map(sceneActivity)).size,8);
});
test('unrecognized rendering state never claims live source activity',()=>{
 assert.equal(sceneActivity('arbitrary'),'Preparing renderer');
 assert.doesNotMatch(sceneActivity('orbiting'),/live|trade|observed/i);
});
