/** Actual shared compact loader, picking, collision and terrain diagnostics. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {BuildingIndex,makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url))),here=new URL('./',import.meta.url),base=read('../../../3d-viewer/city/data/terrain.json'),patch=read('../pui-o-completion/terrain-pui-o.json');
const catalogue=read('./compact/catalogue.json'),entries=prepareModelCatalogue(catalogue,'http://localhost/pui-o-detail-completion/catalogue.json'),selection=JSON.parse(gunzipSync(readFileSync(new URL('../pui-o-completion/building-selection.json.gz',here)))).buildings,byUid=new Map(selection.map(b=>[b.uid,b])),sampler=makeTerrainSampler({...base,patches:[patch]});
const results=[],lighting={night:{value:1},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}};
for(const entry of entries){
 const asset=readFileSync(new URL('./compact/'+entry.asset,here)),model=await loadOfficialModel(entry,byUid.get(entry.uid),lighting,{fetcher:async()=>new Response(asset)});assert(model.meshes.every(m=>m.userData.officialBuildingUid===entry.uid));let sample=null,terrainMin=Infinity,terrainMax=-Infinity;
 for(const mesh of model.meshes){const p=mesh.geometry.attributes.position,indices=mesh.geometry.index.array,a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3();
  for(let j=0;j<p.count;j++){a.fromBufferAttribute(p,j).applyMatrix4(mesh.matrixWorld);const h=sampler.height(a.x,a.z);terrainMin=Math.min(terrainMin,h);terrainMax=Math.max(terrainMax,h);}
  for(let i=0;i<indices.length;i+=3){a.fromBufferAttribute(p,indices[i]).applyMatrix4(mesh.matrixWorld);b.fromBufferAttribute(p,indices[i+1]).applyMatrix4(mesh.matrixWorld);c.fromBufferAttribute(p,indices[i+2]).applyMatrix4(mesh.matrixWorld);const normal=new THREE.Vector3().crossVectors(b.clone().sub(a),c.clone().sub(a));if(Math.abs(normal.y)<.01)continue;const centre=a.clone().add(b).add(c).divideScalar(3);if(!sample||centre.y>sample.y)sample=centre;}
 }
 assert(sample);const ray=new THREE.Raycaster(new THREE.Vector3(sample.x,entry.worldBounds[1][1]+10,sample.z),new THREE.Vector3(0,-1,0)),hits=ray.intersectObjects(model.meshes);assert(hits.length);assert.equal(hits[0].object.userData.officialBuildingUid,entry.uid);
 const index=new BuildingIndex([model.record]);assert.equal(index.collision(sample.x,sample.z,sample.y-.05,sample.y+.05,.1)?.uid,entry.uid);assert.equal(index.collision(sample.x,sample.z,entry.worldBounds[1][1]+1,entry.worldBounds[1][1]+2,.1),null);
 results.push({uid:entry.uid,triangles:entry.triangles,sourceBounds:entry.worldBounds,currentTerrainMin:terrainMin,currentTerrainMax:terrainMax,roofBelowSomeCurrentTerrain:entry.worldBounds[1][1]<terrainMax,roofBelowAllCurrentTerrain:entry.worldBounds[1][1]<terrainMin,sourcePicking:true,sourceCollision:true});disposeOfficialModel(model);
}
assert.equal(results.length,4);const report={staged:true,models:results.length,triangles:results.reduce((s,r)=>s+r.triangles,0),checks:['Actual shared catalogue and glTF loader: identity, hashes, native source bounds and source elevation guards','Source UID ray picking, actual model-triangle collision and above-roof clearance for all candidates','Current Pui O terrain sampled across source mesh vertices; conflicts reported without changing source heights'],results,limits:['CPU-only. No GPU appearance or frame-rate claim.','Terrain diagnostics use current published patch; original adjacent terrain has not been integrated.','A successful source identity match does not alone establish safe visible placement.']};
writeFileSync(new URL('../../../docs/astra-city/pui-o-detail-completion/runtime-verification.json',here),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
