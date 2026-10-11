/** Reuse the shared compact-loader, picking and collision checks without a GPU. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {BuildingIndex,makeTerrainSampler,terrainVertexHeight} from '../../../3d-viewer/city/geo.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url))),here=new URL('./',import.meta.url);
const catalogue=read('./compact/catalogue.json'),entries=prepareModelCatalogue(catalogue,'http://localhost/mui-wo-completion/catalogue.json'),selection=read('../../../3d-viewer/city/data/mui-wo-buildings.json').buildings,byUid=new Map(selection.map(b=>[b.uid,b]));
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
const report={staged:true,models:results.length,triangles:results.reduce((s,r)=>s+r.triangles,0),residentBudgetBytesAllModels:results.reduce((s,r)=>s+r.residentBudgetBytes,0),catalogueSha256:createHash('sha256').update(readFileSync(new URL('./compact/catalogue.json',here))).digest('hex'),checks:['Actual shared catalogue and GLTF loader accepts every staged model','SHA/byte counts, native source bounds, source UID/CSUID/elevation guards validated by shared loader','Ray picking returns source UID; exact model triangle collision and clear space above roof checked for every model'],results,limits:['CPU validation only; no GPU frame-rate, day/night or mobile render acceptance is claimed.','No live registry, tile or terrain mutation; placement against final terrain remains root integration work.','Shared loader LOD/cache must cap simultaneous models.']};
writeFileSync(new URL('../../../docs/astra-city/mui-wo-detail-completion/runtime-verification.json',here),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({models:report.models,triangles:report.triangles,residentBudgetBytesAllModels:report.residentBudgetBytesAllModels},null,2));
