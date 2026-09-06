import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as THREE from '../../vendor/three.module.js';
import {makeTerrainSampler} from '../geo.js';
import {makeTerrain} from '../world.js';
const georef={aE:10,aN:-10,bE:834500,bN:816500};
function regional(id,x,bed){
 const p=(a,b)=>[a,bed,b];return {schemaVersion:1,region:id,bounds:[x,0,x+10,10],illustrativeBed:bed,source:{id},water:[{id:id+'-water',rings:[[[x,0],[x+10,0],[x+10,10],[x,10],[x,0]]]}],terrainCuts:[{georef,cells:[{x,z:0,c:x/10,r:0,land:[]}]}],bedTriangles:[...p(x,0),...p(x,10),...p(x+10,0),...p(x+10,0),...p(x,10),...p(x+10,10)],bankTriangles:[]};
}
const a=regional('west',0,-4),b=regional('east',70,-7),arrays=['water','terrainCuts','bedTriangles','bankTriangles'];
const composite={schemaVersion:1,region:'composite',bounds:[0,0,80,10],illustrativeBed:null,regions:[],...Object.fromEntries(arrays.map(k=>[k,[]]))};
for(const input of [a,b]){const r={region:input.region,bounds:input.bounds,illustrativeBed:input.illustrativeBed,source:input.source,geometryRanges:{}};for(const key of arrays){r.geometryRanges[key]=[composite[key].length,input[key].length];composite[key].push(...input[key]);}composite.regions.push(r);}
const base={w:9,h:2,elev:Array(18).fill(5),vegetation:Array(18).fill(0),meta:{georef}};
function dispose(group){group.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});}
test('disjoint regional water uses its own bed level while the gap remains source land',()=>{
 const sampler=makeTerrainSampler({...base,hydro:composite});
 for(const [x,water,height] of [[5,true,-4],[40,false,5],[75,true,-7]]){assert.equal(sampler.mappedWater(x,5),water);assert.equal(sampler.height(x,5),height);assert.equal(sampler.raw(x,5),5);}
});
test('legacy standalone regional water and a numeric zero bed retain exact semantics',()=>{
 for(const hydro of [undefined,a,{...a,illustrativeBed:0}]){const sampler=makeTerrainSampler({...base,hydro});assert.equal(sampler.height(5,5),hydro?hydro.illustrativeBed:5);assert.equal(sampler.height(40,5),5);assert.equal(sampler.raw(5,5),5);}
});
test('flattened regional cuts remove both actual mesh cells without bridging the dry gap',()=>{
 const terrain=makeTerrain({...base,hydro:composite});terrain.updateMatrixWorld(true);const ray=new THREE.Raycaster();
 try{for(const [x,height] of [[5,-4],[40,5],[75,-7]]){ray.set(new THREE.Vector3(x,50,5),new THREE.Vector3(0,-1,0));assert.ok(Math.abs(ray.intersectObject(terrain,true)[0].point.y-height)<1e-5);}}finally{dispose(terrain);}
});
function minimapLandRectangles(hydro){
 const rectangles=[],ctx=new Proxy({fillRect(x,y,w,h){rectangles.push({colour:this.fillStyle,rect:[x,y,w,h]});},getImageData(){return {};}} ,{get:(obj,k)=>k in obj?obj[k]:()=>{}});
 const labels={},context={nav:{mode:'orbit'},controls:{target:{x:40,z:5}},camera:{position:{x:0,z:0}},place:'central',lightState:{night:0},overview:{},terrain:{userData:{data:{...base,elev:Array(18).fill(0),hydro}}},mapStamp:null,mapBackdrop:null,mapBounds:null,mapCoords:(x,z)=>[x,z],closestPlace:()=> 'test',PLACES:{test:{title:'Test'}},$:id=>id==='minimap'?{getContext:()=>ctx}:(labels[id]||={})};
 const app=fs.readFileSync(new URL('../app.js',import.meta.url),'utf8'),start=app.indexOf('function drawMinimap(){'),end=app.indexOf('\nfunction updateStreamStatus()',start);assert.ok(start>=0&&end>start);vm.runInNewContext(app.slice(start,end)+'\ndrawMinimap();',context);
 return rectangles.filter(r=>r.colour==='#dce3c9').map(r=>r.rect);
}
test('actual minimap paints separate regional land bounds, never their union sea rectangle',()=>{
 assert.deepEqual(minimapLandRectangles(composite),[[0,0,10,10],[70,0,10,10]]);assert.deepEqual(minimapLandRectangles(a),[[0,0,10,10]]);
});
