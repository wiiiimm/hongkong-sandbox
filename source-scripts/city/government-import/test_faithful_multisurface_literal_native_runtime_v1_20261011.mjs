/** DRAFT literal production schema counterexamples; no viewer/current writes. */
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
function data(position){return {w:2,h:2,vegetation:[0,0,0,0],meta:{georef:{aE:1,aN:-1,bE:0,bN:0}},nativeMesh:{position,index:Array.from({length:position.length/3},(_,i)=>i)}};}
const low=[0,1,0,0,1,2,2,1,0],high=[0,9,0,0,9,2,2,9,0],vertical=[0,0,0,0,1,0,0,0,1];let count=0;
let d=data([...low,...high,...vertical]),mesh=makeTerrain(d),surface=nativeTerrainSurface(d.nativeMesh);assert.equal(mesh.geometry.index.count/3,3);assert.equal(surface.triangles,2);assert.equal(surface.height(.5,.5),9);assert.equal(mesh.geometry.attributes.position.count,9);mesh.geometry.dispose();mesh.material.dispose();count++;
d=data(vertical);mesh=makeTerrain(d);surface=nativeTerrainSurface(d.nativeMesh);assert.equal(mesh.geometry.index.count/3,1);assert.equal(surface.triangles,0);assert.equal(surface.height(0,.5),null);mesh.geometry.dispose();mesh.material.dispose();count++;
d=data([0,0,0,1e-6,0,0,0,0,1e-6]);mesh=makeTerrain(d);surface=nativeTerrainSurface(d.nativeMesh);assert.equal(mesh.geometry.index.count/3,1);assert.equal(surface.triangles,0);assert.equal(surface.height(1e-7,1e-7),null);assert.notEqual((mesh.geometry.attributes.position.getX(1)*mesh.geometry.attributes.position.getZ(2)),0);mesh.geometry.dispose();mesh.material.dispose();count++;
d=data([2,1,0,0,1,2,0,1,0]);mesh=makeTerrain(d);assert.deepEqual(Array.from(mesh.geometry.index.array),[0,2,1]);assert.deepEqual(Array.from(mesh.geometry.attributes.position.array),d.nativeMesh.position);mesh.geometry.dispose();mesh.material.dispose();count++;
console.log(JSON.stringify({literalRuntimeTestsPassed:count,allDrawnFacesPreserved:true,maxHeightSchema:true,verticalIndexExclusion:true,tinyNonverticalExclusionRetainedFailure:true,noCurrentChanges:true}));
