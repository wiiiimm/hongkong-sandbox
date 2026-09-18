import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {makeTerrain} from '../world.js';
import {makeTerrainSampler,ORIGIN} from '../geo.js';
function grid(w,h,step,x,z,height){return {w,h,elev:Array(w*h).fill(height),vegetation:Array(w*h).fill(0),meta:{georef:{aE:step,aN:-step,bE:ORIGIN[0]+x,bN:ORIGIN[1]-z}}};}
function dispose(root){root.traverse(o=>{o.geometry?.dispose();for(const m of o.material?[].concat(o.material):[])m.dispose();});}
function hitHeights(mesh,x,z){mesh.updateMatrixWorld(true);return new THREE.Raycaster(new THREE.Vector3(x,100,z),new THREE.Vector3(0,-1,0)).intersectObject(mesh,true).map(h=>h.point.y);}
test('nested source terrain crossing a drawing-chunk boundary replaces its parent exactly once',()=>{
 const coarse=grid(5,3,1000,0,0,2),parent=grid(401,201,5,0,0,2);parent.coarseCells=[0,0,2,1];coarse.patches=[parent];
 const child=grid(61,31,1,950,10,8);child.coarseCells=[190,2,202,8];parent.patches=[child];
 const grandchild=grid(21,21,.5,970,20,12);grandchild.coarseCells=[20,10,30,20];child.patches=[grandchild];
 const sampler=makeTerrainSampler(coarse),mesh=makeTerrain(coarse);
 try{
  for(const [x,z,res] of [[960.21,13.37,1],[985.21,13.37,1],[975.21,22.37,.5],[1030.21,22.37,5],[2500.21,22.37,1000]]){
   const hits=hitHeights(mesh,x,z);assert.equal(hits.length,1,`one surface at ${x},${z}: ${hits}`);assert.ok(Math.abs(hits[0]-sampler.height(x,z))<1e-5);assert.equal(sampler.resolutionAt(x,z),res);
  }
 }finally{dispose(mesh);}
});
test('a nested child also removes parent hydro-cut triangles under its footprint',()=>{
 const coarse=grid(3,3,10,0,0,2),parent=grid(5,5,5,0,0,2);parent.coarseCells=[0,0,2,2];coarse.patches=[parent];
 const child=grid(6,6,1,5,5,8);child.coarseCells=[1,1,2,2];parent.patches=[child];
 coarse.hydro={terrainCuts:[{georef:parent.meta.georef,cells:[{x:5,z:5,land:[5,2,5,5,2,10,10,2,5,10,2,5,5,2,10,10,2,10]}]}]};
 const mesh=makeTerrain(coarse);try{assert.deepEqual(hitHeights(mesh,6.21,6.37),[8]);}finally{dispose(mesh);}
});
