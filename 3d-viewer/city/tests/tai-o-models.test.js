import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {describeBuilding,createBuildingGeometry} from '../building-geometry.js';
import {makeTerrainSampler,terrainVertexHeight} from '../geo.js';
import {makeTerrain} from '../world.js';
const read=url=>JSON.parse(readFileSync(new URL(url,import.meta.url)));

test('Tai O source models retain the existing batching, windows and collision contract',()=>{
 const manifest=read('../data/manifest.json');let models=0,vertices=0;
 for(const tile of manifest.tiles.filter(t=>t.bounds[0]<-29965&&t.bounds[2]>-31535&&t.bounds[1]<3935&&t.bounds[3]>3265)){
  for(const building of read('../../'+tile.url).buildings){
   if(!building.modelGeometry?.sourceTile?.startsWith('9-SW-23'))continue;
   const desc=describeBuilding(building);assert.equal(desc.modelStatus,'usable',building.uid);assert.ok(desc.parts.length>0);
   assert.equal(building.buildingCSUID,building.modelGeometry.buildingCSUID);
   const geometry=createBuildingGeometry(building);
   assert.ok(geometry.attributes.position.count>=building.modelGeometry.position.length/3);
   assert.equal(geometry.attributes.cityWindows.count,geometry.attributes.position.count);
   geometry.dispose();models++;vertices+=building.modelGeometry.position.length/3;
  }
 }
 assert.equal(models,532);assert.equal(vertices,153621);
});

test('Tai O terrain joins the coarse terrain continuously and retains the independent Mui Wo patch',()=>{
 const manifest=read('../data/manifest.json');
 assert.ok(manifest.terrainPatches.some(p=>p.area==='Mui Wo'));
 const patch=read('../data/terrain-tai-o.json'),coarse=makeTerrainSampler(read('../data/terrain.json'));
 const sampler=makeTerrainSampler({...read('../data/terrain.json'),patches:[patch]}),g=patch.meta.georef;
 const original=read('../data/terrain.json');
 const coarseRendered=makeTerrainSampler({...original,elev:original.elev.map((_,i)=>terrainVertexHeight(original,i))});
 for(let r=0;r<patch.h;r++)for(let c=0;c<patch.w;c++){
  if(r!==0&&r!==patch.h-1&&c!==0&&c!==patch.w-1)continue;
  const x=g.bE+g.aE*c-834500,z=816500-(g.bN+g.aN*r);
  assert.ok(Math.abs(sampler.height(x,z)-coarse.height(x,z))<.011,`${c},${r}`);
  assert.ok(Math.abs(terrainVertexHeight(patch,r*patch.w+c)-coarseRendered.raw(x,z))<.011,`mesh edge ${c},${r}`);
  assert.ok(Math.abs(makeTerrainSampler(patch).raw(x,z)-coarse.raw(x,z))<.011,`raw source edge ${c},${r}`);
 }
});

test('terrain chunks and sampler use the same optional display heights, including zero',()=>{
 const patch=read('../data/terrain-tai-o.json'),base=read('../data/terrain.json'),g=patch.meta.georef;
 const sampler=makeTerrainSampler({...base,patches:[patch]}),group=makeTerrain({...base,patches:[patch]});let checked=0,seamNodes=0;
 const fineMeshes=[];group.traverse(mesh=>{if(mesh.isMesh&&mesh.name==='Lands Department · 5 m terrain')fineMeshes.push(mesh);});
 for(const mesh of fineMeshes){
  const pos=mesh.geometry.attributes.position;
  for(let i=0;i<pos.count;i++){
   const x=pos.getX(i),z=pos.getZ(i),y=pos.getY(i),c=Math.round((x+834500-g.bE)/g.aE),r=Math.round((816500-z-g.bN)/g.aN);
   assert.ok(Math.abs(y-terrainVertexHeight(patch,r*patch.w+c))<.001);
   const expected=sampler.mappedWater(x,z)?base.hydro.illustrativeBed:Math.max(1.2,y);
   assert.ok(Math.abs(expected-sampler.height(x,z))<.011);
   checked++;if(c===196)seamNodes++;
  }
 }
 assert.ok(checked>=patch.w*patch.h);assert.equal(seamNodes,patch.h*2);
 group.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});
 const simple={w:2,h:2,elev:[5,0,-2,9],renderedElev:[0,null,null,null],vegetation:[0,0,0,0],meta:{georef:{bE:834500,bN:816500,aE:5,aN:-5}}};
 assert.equal(terrainVertexHeight(simple,0),0);assert.equal(terrainVertexHeight(simple,1),-4);assert.equal(terrainVertexHeight(simple,3),9);
 const mesh=makeTerrain(simple);assert.equal(mesh.geometry.attributes.position.getY(0),0);mesh.geometry.dispose();mesh.material.dispose();
});
