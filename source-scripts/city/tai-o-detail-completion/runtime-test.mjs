/** Source compact-loader and actual terrain-mesh checks, without a GPU. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {BuildingIndex,makeTerrainSampler,terrainVertexHeight} from '../../../3d-viewer/city/geo.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url))),here=new URL('./',import.meta.url),base=read('../../../3d-viewer/city/data/terrain.json'),patch=read('../../../3d-viewer/city/data/terrain-tai-o.json');
const catalogue=read('./compact/catalogue.json'),entries=prepareModelCatalogue(catalogue,'http://localhost/pui-o/catalogue.json'),selection=JSON.parse(gunzipSync(readFileSync(new URL('../tai-o-models/building-selection.json.gz',here)))).buildings,byUid=new Map(selection.map(b=>[b.uid,b]));
const results=[],lighting={night:{value:1},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
for(const entry of entries){
 const started=performance.now(),asset=readFileSync(new URL('./compact/'+entry.asset,here)),model=await loadOfficialModel(entry,byUid.get(entry.uid),lighting,{fetcher:async()=>new Response(asset)});
 assert(model.meshes.every(m=>m.userData.officialBuildingUid===entry.uid));
 let sample=null;
 for(const mesh of model.meshes){
  const p=mesh.geometry.attributes.position,indices=mesh.geometry.index.array,a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
  for(let i=0;i<indices.length;i+=3){a.fromBufferAttribute(p,indices[i]).applyMatrix4(mesh.matrixWorld);b.fromBufferAttribute(p,indices[i+1]).applyMatrix4(mesh.matrixWorld);c.fromBufferAttribute(p,indices[i+2]).applyMatrix4(mesh.matrixWorld);
   const normal=new THREE.Vector3().crossVectors(b.clone().sub(a),c.clone().sub(a));if(Math.abs(normal.y)<.01)continue;
   const centre=a.clone().add(b).add(c).divideScalar(3);if(!sample||centre.y>sample.y)sample=centre;
  }
 }
 assert(sample,entry.uid+' has a source horizontal surface');
 const ray=new THREE.Raycaster(new THREE.Vector3(sample.x,entry.worldBounds[1][1]+10,sample.z),new THREE.Vector3(0,-1,0));
 const hits=ray.intersectObjects(model.meshes);assert(hits.length,entry.uid+' source picking');assert.equal(hits[0].object.userData.officialBuildingUid,entry.uid);
 const index=new BuildingIndex([model.record]);assert.equal(index.collision(sample.x,sample.z,sample.y-.05,sample.y+.05,.1)?.uid,entry.uid,'source surface collision');
 assert.equal(index.collision(sample.x,sample.z,entry.worldBounds[1][1]+1,entry.worldBounds[1][1]+2,.1),null);
 results.push({uid:entry.uid,triangles:entry.triangles,bytes:entry.bytes,residentBudgetBytes:model.budget.residentBytes,decodeVerifyMs:performance.now()-started});disposeOfficialModel(model);
}
assert.equal(results.length,catalogue.models.length);
const terrain=makeTerrainSampler({...base,patches:[patch]});
for(const r of results){const e=entries.find(e=>e.uid===r.uid),b=byUid.get(r.uid),x=b.centre[0],z=b.centre[1];r.terrainAtFootprintCentre=terrain.height(x,z);r.sourceModelYBounds=[e.worldBounds[0][1],e.worldBounds[1][1]];r.roofBelowCentreTerrain=e.worldBounds[1][1]<r.terrainAtFootprintCentre;}
const report={staged:true,models:results.length,triangles:results.reduce((s,r)=>s+r.triangles,0),residentBudgetBytesAllModels:results.reduce((s,r)=>s+r.residentBudgetBytes,0),checks:['Actual shared loadOfficialModel accepts all staged models with source identity and bound guards','Source roof ray-picking resolves expected UID','Exact source triangle collision succeeds and space above highest roof is clear'],results,limits:['CPU geometry acceptance, not full architectural or GPU/browser verification','Terrain centre diagnostic is not whole-footprint/foundation acceptance; source absolute elevations preserved']};
writeFileSync(new URL('../../../docs/astra-city/tai-o-detail-completion/runtime-verification.json',here),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
