import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {makeTerrainSampler,ORIGIN} from '../geo.js';
import {makeTerrain} from '../world.js';
import {nativeTerrainSurface} from '../native-terrain.js';
const meta={georef:{W:3,H:3,aE:5,aN:-5,bE:ORIGIN[0],bN:ORIGIN[1]}};
function patch(){return {w:3,h:3,elev:Array(9).fill(2),vegetation:Array(9).fill(0),coarseCells:[0,0,1,1],meta,nativeMesh:{position:[0,2,0,5,2,0,0,2,10,5,2,10,5,12,0,10,12,0,5,12,10,10,12,10],index:[0,2,1,1,2,3,4,6,5,5,6,7,1,3,4,4,3,6]}};}
test('native retaining edge stays sharp and walking matches exact rendered faces',()=>{
 const p=patch(),parent={w:2,h:2,elev:[2,2,2,2],vegetation:[0,0,0,0],meta:{georef:{...meta.georef,aE:10,aN:-10}},patches:[p]};
 const sample=makeTerrainSampler(parent),mesh=makeTerrain(parent);mesh.updateMatrixWorld(true);
 try{for(const [x,z,height] of [[4.999,2.31,2],[5.001,2.31,12],[1.25,8.7,2],[8.3,4.7,12]]){
  assert(Math.abs(sample.height(x,z)-height)<1e-9);const hits=new THREE.Raycaster(new THREE.Vector3(x,100,z),new THREE.Vector3(0,-1,0)).intersectObject(mesh,true);assert.equal(hits.length,1);assert(Math.abs(hits[0].point.y-height)<1e-6);
 }}finally{mesh.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});}
});
test('native height index uses renderer Float32 positions and rejects invalid input',()=>{
 const mesh=patch().nativeMesh,s=nativeTerrainSurface(mesh);assert(s.position instanceof Float32Array);assert.equal(nativeTerrainSurface(mesh),s);assert.equal(s.height(12,5),null);
 assert.throws(()=>nativeTerrainSurface({position:[0,NaN,0],index:[]}),/Invalid native/);
 assert.throws(()=>nativeTerrainSurface({position:[0,0,0],index:[0,1,0]}),/Invalid native/);
});
test('uncovered native interior fails explicitly instead of silently using a grid ramp',()=>{
 const p=patch();p.nativeMesh.index=[0,2,1];const s=makeTerrainSampler(p);assert.throws(()=>s.height(8,5),/uncovered/);
});
