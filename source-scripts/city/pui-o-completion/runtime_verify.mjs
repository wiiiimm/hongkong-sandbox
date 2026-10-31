/** Source compact-loader and actual terrain-mesh checks, without a GPU. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {BuildingIndex,makeTerrainSampler,terrainVertexHeight} from '../../../3d-viewer/city/geo.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url))),here=new URL('./',import.meta.url),base=read('../../../3d-viewer/city/data/terrain.json'),patch=read('./terrain-pui-o.json');
const catalogue=read('./compact/catalogue.json'),entries=prepareModelCatalogue(catalogue,'http://localhost/pui-o/catalogue.json'),selection=JSON.parse(gunzipSync(readFileSync(new URL('./building-selection.json.gz',here)))).buildings,byUid=new Map(selection.map(b=>[b.uid,b]));
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
assert.equal(results.length,681);
const sampler=makeTerrainSampler({...base,patches:[patch]}),coarse=makeTerrainSampler(base),coarseRendered=makeTerrainSampler({...base,elev:base.elev.map((_,i)=>terrainVertexHeight(base,i))}),g=patch.meta.georef,mesh=makeTerrain(patch),pos=mesh.geometry.attributes.position;let edgeChecks=0,maxEdgeError=0,maxMeshError=0;
for(let r=0;r<patch.h;r++)for(let c=0;c<patch.w;c++){
 const i=r*patch.w+c,x=g.bE+g.aE*c-834500,z=816500-(g.bN+g.aN*r),expected=terrainVertexHeight(patch,i);maxMeshError=Math.max(maxMeshError,Math.abs(pos.getY(i)-expected));
 if(r!==0&&r!==patch.h-1&&c!==0&&c!==patch.w-1)continue;
 const error=Math.abs(expected-coarseRendered.raw(x,z));maxEdgeError=Math.max(maxEdgeError,error);assert(error<.011,'rendered terrain joins coarse mesh');assert(Math.abs(sampler.height(x,z)-coarse.height(x,z))<.011,'sampler at staged patch boundary');edgeChecks++;
}
assert(maxMeshError<.001);mesh.geometry.dispose();mesh.material.dispose();
const report={staged:true,models:results.length,triangles:results.reduce((s,r)=>s+r.triangles,0),residentBudgetBytesAllModels:results.reduce((s,r)=>s+r.residentBudgetBytes,0),catalogueSha256:createHash('sha256').update(readFileSync(new URL('./compact/catalogue.json',here))).digest('hex'),checks:['Actual shared catalogue and GLTF loader accepts all 681 source-matched models','SHA/byte counts, native source bounds, source UID/CSUID/elevation guards validated by shared loader','Ray picking returns source UID; exact model triangle collision and clear space above roof checked for every model','Actual staged terrain mesh vertices retain display elevations; patch perimeter joins current coarse mesh and sampler'],terrain:{vertices:pos.count,edgeChecks,maxEdgeError,maxMeshError},results,limits:['CPU validation only; no GPU frame-rate, day/night or mobile render acceptance is claimed.','All-model resident budget is a ceiling comparison; shared loader LOD/cache must cap simultaneous models.']};
writeFileSync(new URL('../../../docs/astra-city/pui-o-completion/runtime-verification.json',here),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({models:report.models,triangles:report.triangles,residentBudgetBytesAllModels:report.residentBudgetBytesAllModels,terrain:report.terrain},null,2));
