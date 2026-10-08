import test from 'node:test';
import assert from 'node:assert/strict';
import {verifyOriginalContactSeams as verify} from './original-contact-seams.mjs';
const mesh=triangles=>({position:triangles.flat(2),index:Array.from({length:triangles.length*3},(_,i)=>i)});
const ground=[[-3,0,-3],[3,0,-3],[0,0,3]];
const source=mesh([[[0,0,0],[1,0,0],[1,2,0]],[[0,0,0],[1,2,0],[0,2,0]]]);
const supportingWall=[[1,-2,0],[1,0,0],[0,0,0]];
test('original vertical support upper edge resolves ray-omitted seam with other strict contact',()=>{
 const support=mesh([[[-.5,0,-1],[.5,0,-1],[0,0,1]],supportingWall]);
 const p=verify(source,0,support);assert.equal(p.rawInterface.passed,false);assert.equal(p.passed,true);assert(p.resolved.some(r=>r.kind==='original-wall-upper-edge-seam'));
});
test('a side contact below wall top does not resolve floating base',()=>{const support=mesh([[[-.5,0,-1],[.5,0,-1],[0,0,1]],[[1,-2,0],[1,2,0],[0,2,0]]]);assert.equal(verify(source,0,support).passed,false);});
test('seam above the unchanged geometric tolerance rejects',()=>{const support=mesh([[[-.5,0,-1],[.5,0,-1],[0,0,1]],supportingWall.map(([x,y,z])=>[x,y-.01,z])]);assert.equal(verify(source,0,support).passed,false);});
test('a top vertex alone does not establish a support edge',()=>{const support=mesh([[[-.5,0,-1],[.5,0,-1],[0,0,1]],[[1,0,0],[1,-1,0],[0,-1,0]]]);assert.equal(verify(source,0,support).passed,false);});
test('entirely floating source without strict contacts stays rejected',()=>{assert.equal(verify(source,0,mesh([supportingWall])).passed,false);});
test('horizontal source without rising original wall cannot use wall-edge rule',()=>{const s=mesh([[[0,0,0],[1,0,0],[0,0,.1]]]);assert.equal(verify(s,0,mesh([[[-.5,0,-1],[.5,0,-1],[0,0,1]],supportingWall])).passed,false);});
test('a higher corner with actual lower interior support is not covering a wall base',()=>{
 const support=mesh([ground,[[1,1,0],[2,1,0],[1,1,1]]]);const p=verify(source,0,support);assert.equal(p.rawInterface.passed,false);assert.equal(p.passed,true);assert(p.resolved.some(r=>r.kind==='zero-area-higher-deck-corners'));
});
test('a higher interior roof over a wall stays rejected',()=>{assert.equal(verify(source,0,mesh([ground,[[0,1,-1],[2,1,-1],[1,1,1]]])).passed,false);});
test('buried horizontal floor at a higher corner remains rejected',()=>{const s=mesh([[[0,0,0],[1,0,0],[0,2,0]],[[0,0,0],[1,0,0],[0,0,.2]]]);assert.equal(verify(s,0,mesh([ground,[[1,1,0],[2,1,0],[1,1,1]]])).passed,false);});
test('corner roof without strict interior lower contact stays rejected',()=>{assert.equal(verify(source,0,mesh([[[1,1,0],[2,1,0],[1,1,1]]])).passed,false);});
test('empty original mesh cannot gain acceptance',()=>{assert.equal(verify(mesh([]),0,mesh([ground])).passed,false);});
