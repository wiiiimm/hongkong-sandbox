import test from 'node:test';
import assert from 'node:assert/strict';
import {renderedPatchHeight} from '../../../3d-viewer/city/rendered-patch-height.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';

function fixture(nativeHeight,bed){
 const meta={georef:{bE:834500,bN:816500,aE:1,aN:-1}};
 const position=[0,nativeHeight,0,1,nativeHeight,0,0,nativeHeight,1,1,nativeHeight,1];
 const child={w:2,h:2,elev:[2,2,2,2],vegetation:[0,0,0,0],meta,coarseCells:[0,0,1,1],nativeMesh:{position,index:[0,2,1,1,2,3]}};
 const bedTriangles=[0,bed,0,0,bed,1,1,bed,0,1,bed,0,0,bed,1,1,bed,1];
 const hydro={bedTriangles,bounds:[0,0,1,1],water:[{rings:[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}],illustrativeBed:bed};
 const data={w:2,h:2,elev:[2,2,2,2],vegetation:[0,0,0,0],meta,patches:[child],hydro};
 return data;
}
function drawnHeight(data){
 const terrain=makeTerrain(data),position=[];
 terrain.traverse(mesh=>{
  if(!mesh.isMesh)return;
  const p=mesh.geometry.attributes.position,idx=mesh.geometry.index;
  for(let i=0;i<(idx?.count??p.count);i++){const j=idx?idx.getX(i):i;position.push(p.getX(j),p.getY(j),p.getZ(j));}
 });
 const height=nativeTerrainSurface({position,index:Array.from({length:position.length/3},(_,i)=>i)}).height(.25,.25);
 terrain.traverse(mesh=>{if(mesh.isMesh){mesh.geometry.dispose();mesh.material.dispose();}});
 return height;
}
test('higher native ground wins over the actually drawn parent water bed',()=>{
 const data=fixture(5.1031435,5),before=JSON.stringify(data);
 assert.ok(Math.abs(renderedPatchHeight(5.1031435,5,()=>{throw Error('Unused grid');})-drawnHeight(data))<1e-6);
 assert.equal(JSON.stringify(data),before);
});
test('higher drawn water bed remains the top surface above a native patch',()=>{
 assert.equal(renderedPatchHeight(4.8,5,()=>2),drawnHeight(fixture(4.8,5)));
});
test('dry child patch is retained and fallback is evaluated only without either surface',()=>{
 assert.equal(renderedPatchHeight(7,undefined,()=>{throw Error('Unused grid');}),7);
 assert.equal(renderedPatchHeight(undefined,5,()=>{throw Error('Unused grid');}),5);
 assert.equal(renderedPatchHeight(undefined,undefined,()=>3),3);
});
test('production sampler matches the highest rendered terrain across parent water and native patches',()=>{
 for(const native of [4.8,5.1031435,7]){
  const data=fixture(native,5),before=JSON.stringify(data);
  assert.ok(Math.abs(makeTerrainSampler(data).height(.25,.25)-drawnHeight(data))<1e-6);
  assert.equal(JSON.stringify(data),before);
 }
});
