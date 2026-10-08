import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {makeTerrainSampler,ORIGIN} from '../geo.js';
import {makeTerrain} from '../world.js';
import {Navigation} from '../navigation.js';

function grid(elev,step=10,w=2,h=2){
 return {w,h,elev,vegetation:Array(w*h).fill(0),meta:{georef:{aE:step,aN:-step,bE:ORIGIN[0],bN:ORIGIN[1]}}};
}
function checkDrawn(data,points){
 const sampler=makeTerrainSampler(data),mesh=makeTerrain(data);mesh.updateMatrixWorld(true);
 try{
  for(const [x,z,expected] of points){
   const hits=new THREE.Raycaster(new THREE.Vector3(x,100,z),new THREE.Vector3(0,-1,0)).intersectObject(mesh,true);
   assert.equal(hits.length,1,`one rendered surface at ${x},${z}`);
   assert.ok(Math.abs(hits[0].point.y-expected)<1e-6,`rendered height at ${x},${z}`);
   assert.ok(Math.abs(sampler.height(x,z)-hits[0].point.y)<1e-6,`sampler agrees with coastal triangle at ${x},${z}`);
  }
 }finally{mesh.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});}
}
test('mixed coastal grid triangles retain their rendered slopes below 1.2m',()=>{
 checkDrawn(grid([0,2,2,2]),[[1,1,-2.8],[3,3,-.4],[4,4,.8],[8,8,2]]);
 checkDrawn(grid([2,2,2,0]),[[2,2,2],[6,6,.8],[8,8,-1.6]]);
});
test('a coastal child patch matches rendered heights after replacing its parent',()=>{
 const child={...grid([0,2,2,2,2,2,2,2,2],10,3,3),coarseCells:[0,0,1,1]};
 checkDrawn({...grid([5,5,5,5],20),patches:[child]},[[1,1,-2.8],[4,4,.8],[13,13,2]]);
});
test('walking rejects a submerged coastal slope even when raw DTM is above zero',()=>{
 const data=grid([0,2,2,2]),sampler=makeTerrainSampler(data);
 const nav=Object.assign(Object.create(Navigation.prototype),{sampler,index:{collision:()=>false},waterLevel:()=>.3});
 assert.ok(sampler.raw(2,2)>.5);
 assert.equal(nav.walkHeight(2,2,1.2,4),undefined);
 const safe=nav.safeGround(2,2);
 assert.ok(safe&&Math.hypot(safe.x-2,safe.z-2)>1, 'arrival searches for actual dry ground');
 assert.deepEqual(data.elev,[0,2,2,2], 'sampling does not edit raw terrain');
});
test('root water clips regular descendants while native surfaces retain their drawn height',()=>{
 const child={...grid([3,3,3,3,3,3,3,3,3],5,3,3),coarseCells:[0,0,1,1]};
 const ring=[[0,0],[10,0],[10,10],[0,10],[0,0]];
 const hydro={bounds:[0,0,10,10],water:[{rings:[ring]}],illustrativeBed:-4,
  bedTriangles:[0,-4,0,0,-4,10,10,-4,0,10,-4,0,0,-4,10,10,-4,10],
  terrainCuts:[{georef:child.meta.georef,cells:[0,1].flatMap(c=>[0,1].map(r=>({x:c*5,z:r*5,land:[]})))}]};
 const data={...grid([3,3,3,3]),patches:[child],hydro};
 checkDrawn(data,[[2,3,-4]]);
 const original=JSON.stringify(child.elev);
 const native={...grid([3,3,3,3],2),coarseCells:[0,0,1,1],meta:{georef:{aE:2,aN:-2,bE:ORIGIN[0]+1,bN:ORIGIN[1]-1}},
  nativeMesh:{position:[1,7,1,3,7,1,1,7,3,3,7,3],index:[0,2,1,1,2,3]}};
 child.patches=[native];
 const sampler=makeTerrainSampler(data),mesh=makeTerrain(data);mesh.updateMatrixWorld(true);
 try{
  const hits=new THREE.Raycaster(new THREE.Vector3(2,100,2.2),new THREE.Vector3(0,-1,0)).intersectObject(mesh,true);
  assert.equal(hits[0].point.y,7);assert.equal(sampler.height(2,2.2),7);
  assert.equal(sampler.height(7,7),-4);assert.equal(sampler.raw(7,7),3);
  assert.equal(JSON.stringify(child.elev),original);
 }finally{mesh.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});}
});
