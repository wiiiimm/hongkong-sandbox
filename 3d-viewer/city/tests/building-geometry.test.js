import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {describeBuilding,createBuildingGeometry,collisionVolumes} from '../building-geometry.js';
const outline=[[-6,-4],[6,-4],[6,4],[-6,4],[-6,-4]];
const roof=()=>({id:'landsd/1',base:10,height:4,minimum:0,rings:[outline],structureType:'Open-sided Structure'});

test('open-sided roofs keep source top and omit walls/windows',()=>{
 const b=roof(),saved=JSON.stringify(b),description=describeBuilding(b),geometry=createBuildingGeometry(b);geometry.computeBoundingBox();
 assert.equal(description.openSided,true);assert.equal(description.parts[0].top,14);assert.equal(geometry.boundingBox.max.y,14);
 assert.ok(description.illustrativeSupports>=2&&description.illustrativeSupports<=8);assert.ok(description.parts.every(p=>!p.windows));assert.ok([...geometry.attributes.cityWindows.array].every(v=>v===0));
 const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.updateMatrixWorld();
 assert.equal(new THREE.Raycaster(new THREE.Vector3(0,12,10),new THREE.Vector3(0,0,-1)).intersectObject(mesh).length,0,'centre air is visibly open');
 assert.ok(new THREE.Raycaster(new THREE.Vector3(0,20,0),new THREE.Vector3(0,-1,0)).intersectObject(mesh).length>0,'exact roof remains ray-pickable');
 assert.equal(JSON.stringify(b),saved);geometry.dispose();mesh.material.dispose();
});
test('source courtyard remains open through roof and supports',()=>{
 const b=roof();b.rings=[outline,[[-2,-2],[-2,2],[2,2],[2,-2],[-2,-2]]];
 const geometry=createBuildingGeometry(b),mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.updateMatrixWorld();
 assert.equal(new THREE.Raycaster(new THREE.Vector3(0,20,0),new THREE.Vector3(0,-1,0)).intersectObject(mesh).length,0);
 for(const part of collisionVolumes(b).filter(p=>p.kind==='post'))for(const [x,z] of part.rings[0])assert.ok(Math.abs(x)>2||Math.abs(z)>2);
 geometry.dispose();mesh.material.dispose();
});
test('explicit foundation skirt does not move the source roof or acquire windows',()=>{
 const b={...roof(),structureType:'Tower',foundationBase:7},description=describeBuilding(b),geometry=createBuildingGeometry(b);geometry.computeBoundingBox();
 assert.equal(geometry.boundingBox.min.y,7);assert.equal(geometry.boundingBox.max.y,14);assert.equal(b.base,10);assert.equal(b.height,4);
 assert.deepEqual(description.parts.map(p=>[p.kind,p.bottom,p.top,p.windows]),[['building',10,14,true],['foundation',7,10,false]]);
 const y=geometry.attributes.position,w=geometry.attributes.cityWindows;for(let i=0;i<y.count;i++)if(y.getY(i)<10)assert.equal(w.getX(i),0);
 geometry.dispose();
});
test('open supports use explicit foundation while leaving air unsealed',()=>{
 const b={...roof(),foundationBase:7},parts=collisionVolumes(b);
 assert.equal(parts.find(p=>p.kind==='roof').top,14);assert.ok(parts.filter(p=>p.kind==='post').every(p=>p.bottom===7));assert.ok(parts.every(p=>p.kind!=='foundation'));
});
test('ordinary buildings preserve single volume and window attributes',()=>{
 const b={...roof(),structureType:'Tower',minimum:1},parts=collisionVolumes(b),geometry=createBuildingGeometry(b);geometry.computeBoundingBox();
 assert.equal(parts.length,1);assert.equal(geometry.boundingBox.min.y,11);assert.equal(geometry.boundingBox.max.y,14);assert.ok([...geometry.attributes.cityWindows.array].every(v=>v===1));geometry.dispose();
});
test('cached layout updates if explicitly supplied foundation changes',()=>{
 const b=roof(),old=describeBuilding(b);assert.equal(describeBuilding(b),old);b.foundationBase=8;assert.notEqual(describeBuilding(b),old);assert.equal(describeBuilding(b).foundationApplied,true);
});

test('BuildingIndex shares open roof and support geometry',async()=>{
 const {BuildingIndex}=await import('../geo.js'),b=roof(),index=new BuildingIndex([b]),parts=collisionVolumes(b),post=parts.find(p=>p.kind==='post'),x=(post.bounds[0]+post.bounds[2])/2,z=(post.bounds[1]+post.bounds[3])/2;
 assert.equal(index.collision(0,0,10.2,12,.2),null);assert.equal(index.collision(x,z,10.2,12,.2),b);assert.equal(index.collision(0,0,13.9,14.1,.2),b);
});
test('terrain exact grid edges preserve source vertex elevations',async()=>{
 const {makeTerrainSampler,ORIGIN}=await import('../geo.js'),sampler=makeTerrainSampler({w:2,h:2,elev:[3,5,7,19],meta:{georef:{bE:ORIGIN[0],bN:ORIGIN[1],aE:5,aN:-5}}});
 assert.equal(sampler.raw(5,5),19);assert.equal(sampler.raw(5,0),5);assert.equal(sampler.raw(0,5),7);assert.equal(sampler.height(5,5),19);
});

test('validated detailed model geometry replaces the simple extrusion',()=>{
 const b={...roof(),structureType:'Tower',modelGeometry:{position:[-2,10,-2,2,10,-2,0,18,0,-2,10,2,2,10,2,0,18,0],normal:[0,0,-1,0,0,-1,0,0,-1,0,0,1,0,0,1,0,0,1]}},saved=JSON.stringify(b),description=describeBuilding(b),geometry=createBuildingGeometry(b);geometry.computeBoundingBox();
 assert.equal(description.modelStatus,'usable');assert.equal(geometry.attributes.position.count,6);assert.equal(geometry.boundingBox.max.y,18);assert.equal(JSON.stringify(b),saved);assert.equal(description.parts[0].top,18);geometry.dispose();
});
test('invalid or misplaced detailed arrays retain source extrusion fallback',()=>{
 for(const modelGeometry of [{position:[1,2,NaN]},{position:[0,0,0,1,0,0,0,1,0],index:[0,1,99]},{position:[9000,10,9000,9001,10,9000,9000,18,9001]}]){
  const b={...roof(),modelGeometry},description=describeBuilding(b),geometry=createBuildingGeometry(b);geometry.computeBoundingBox();assert.equal(description.modelStatus,'invalid-fallback');assert.equal(geometry.boundingBox.max.y,14);geometry.dispose();
 }
});

test('indexed detailed geometry joins the non-indexed shared palette batches',()=>{
 const b={...roof(),structureType:'Tower',modelGeometry:{position:[-2,10,-2,2,10,-2,0,18,0,0,10,2],index:[0,1,2,1,3,2,3,0,2,0,3,1]}},geometry=createBuildingGeometry(b);assert.equal(describeBuilding(b).modelStatus,'usable');assert.equal(geometry.index,null);assert.equal(geometry.attributes.position.count,12);assert.equal(geometry.attributes.cityWindows.count,12);geometry.dispose();
});
