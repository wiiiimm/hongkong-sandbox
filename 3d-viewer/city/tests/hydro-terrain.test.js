import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../../vendor/three.module.js';
import {makeTerrainSampler,segmentDistanceSq} from '../geo.js';
import {makeTerrain} from '../world.js';
const data=JSON.parse(fs.readFileSync(new URL('../data/terrain.json',import.meta.url)));
const manifest=JSON.parse(fs.readFileSync(new URL('../data/manifest.json',import.meta.url)));
data.patches=manifest.terrainPatches.map(p=>JSON.parse(fs.readFileSync(new URL('../../'+p.url,import.meta.url))));
const taiRegion=data.hydro.regions?.find(r=>r.region==='tai-o'),taiRange=taiRegion?.geometryRanges.terrainCuts;
const taiCuts=taiRange?data.hydro.terrainCuts.slice(taiRange[0],taiRange[0]+taiRange[1]):data.hydro.terrainCuts;
const sampler=makeTerrainSampler(data),terrain=makeTerrain(data);terrain.updateMatrixWorld(true);
const before=makeTerrainSampler({...data,hydro:undefined});
const ray=new THREE.Raycaster();
function rendered(x,z){ray.set(new THREE.Vector3(x,500,z),new THREE.Vector3(0,-1,0));return ray.intersectObject(terrain,true)[0]?.point.y;}
test('source-mapped tidal channels cut actual terrain and sampler while preserving raw heights',()=>{
 const probes=[[-30523.45,3546.88],[-30400,3550],[-30556.76,3396.27],[-30685,3680],[-30450,3120],[-31300,3900]];
 let positive=0;
 for(const [x,z]of probes){assert.ok(sampler.mappedWater(x,z),`Expected channel at ${x},${z}`);assert.equal(sampler.raw(x,z),before.raw(x,z));if(sampler.raw(x,z)>0)positive++;assert.equal(sampler.height(x,z),-4);assert.ok(Math.abs(rendered(x,z)+4)<.01,`Rendered bed at ${x},${z}`);}
 assert.ok(positive>=3,'Includes actual positive-DTM channel corrections');
});
test('source land and out-of-Tai-O terrain retain previous heights and optional-path behaviour',()=>{
 for(const [x,z]of [[-31100,3250],[-30787.2,3819.5],[0,0],[-19000,50]]){assert.equal(sampler.mappedWater(x,z),false);assert.equal(sampler.height(x,z),before.height(x,z));assert.equal(sampler.raw(x,z),before.raw(x,z));}
 const unmodified=makeTerrainSampler({w:2,h:2,elev:[5,5,5,5],meta:{georef:{aE:5,aN:-5,bE:834500,bN:816500}}});assert.equal(unmodified.mappedWater(2,2),false);assert.equal(unmodified.height(2,2),5);
});
test('precomputed shoreline cuts reach both fine chunks and surrounding coarse terrain',()=>{
 assert.equal(taiCuts.length,2);assert.ok(taiCuts.every(g=>g.cells.length));
 const fine=taiCuts.find(g=>g.georef.aE===5);assert.ok(fine.cells.some(c=>c.c<196));assert.ok(fine.cells.some(c=>c.c>=196));
 const cuts=[];terrain.traverse(o=>{if(o.name.startsWith('Terrain clipped to mapped'))cuts.push(o);});assert.ok(cuts.length>=3);
 for(const m of cuts){const p=m.geometry.attributes.position;for(let i=0;i<p.count;i+=3){const x=(p.getX(i)+p.getX(i+1)+p.getX(i+2))/3,z=(p.getZ(i)+p.getZ(i+1)+p.getZ(i+2))/3;
   if(sampler.mappedWater(x,z)){const edge=data.hydro.water.some(p=>p.rings.some(r=>r.some((a,j)=>j>0&&segmentDistanceSq(x,z,r[j-1],a)<.035**2)));assert.ok(edge,'No rendered land triangles inside mapped channel, allowing3.5cm Float32 boundary tolerance');}
  }}
 for(const [x,z]of [[-30757.55,3800],[-30757.45,3800],[-30450,3112.45],[-30450,3112.55]]){assert.ok(sampler.mappedWater(x,z));assert.ok(Math.abs(rendered(x,z)+4)<.01,'Water cuts join fine/fine and fine/coarse boundaries');}
});
