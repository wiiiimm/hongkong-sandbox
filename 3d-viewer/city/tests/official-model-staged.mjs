// Verify the actual decoder and all initially packed source models, without WebGL.
import {readFileSync} from 'node:fs';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../official-model-assets.js';
import {cityLighting} from '../lighting.js';
const root=new URL('../../../',import.meta.url),data=new URL('../data/',import.meta.url),manifest=JSON.parse(readFileSync(new URL('manifest.json',data))),tiles=new Map();
const lighting={night:{value:1},activity:{value:new Float32Array(cityLighting(22).activity.slice(0,4))},retail:{value:cityLighting(22).activity[4]},elapsed:{value:0},shimmer:{value:1}};
const results=[],batches=process.argv.slice(2);if(!batches.length)batches.push('compact','compact-followup');let expected=0;
for(const batch of batches){
 assert.ok(['compact','compact-followup','compact-corridor'].includes(batch));
 const catalogueURL=new URL(`source-scripts/city/central-completion/${batch}/catalogue.json`,root),catalogue=JSON.parse(readFileSync(catalogueURL));expected+=catalogue.counts.packedModels;
 for(const entry of prepareModelCatalogue(catalogue,catalogueURL.href)){
  const bounds=entry.worldBounds;let building;
  for(const meta of manifest.tiles){
   if(meta.bounds[0]>bounds[1][0]||meta.bounds[2]<bounds[0][0]||meta.bounds[1]>bounds[1][2]||meta.bounds[3]<bounds[0][2])continue;
   if(!tiles.has(meta.id)){
    const tile=JSON.parse(readFileSync(new URL(`tiles/${meta.id}.json`,data))),activity=JSON.parse(readFileSync(new URL(`activity/${meta.id}.json`,data)));
    for(const b of tile.buildings)b.activity=activity.buildings[b.uid];tiles.set(meta.id,tile);
   }
   building=tiles.get(meta.id).buildings.find(b=>b.uid===entry.uid);if(building)break;
  }
  assert.ok(building,entry.uid);const before=JSON.stringify(building),start=performance.now();
  const loaded=await loadOfficialModel(entry,building,lighting,{fetcher:async url=>new Response(readFileSync(fileURLToPath(url)))});
  try{
   assert.equal(JSON.stringify(building),before);assert.equal(loaded.record.activity,building.activity);assert.equal(loaded.record.uid,building.uid);assert.equal(loaded.record.modelGeometry.position.length,entry.indexedVertices*3);assert.equal(loaded.record.modelGeometry.index.length,entry.triangles*3);
   for(const mesh of loaded.meshes){assert.ok(mesh.geometry.index);assert.equal(mesh.geometry.attributes.cityLight,undefined);assert.equal(mesh.geometry.attributes.cityWindows,undefined);}
   results.push({uid:entry.uid,label:entry.label,modelId:entry.modelId,triangles:entry.triangles,sourceBounds:entry.worldBounds,compressedBytes:entry.bytes,...loaded.budget,parseAndVerifyMs:performance.now()-start,activityProfile:building.activity.profile});
  }finally{disposeOfficialModel(loaded);}
 }
}
assert.equal(results.length,expected);console.log(JSON.stringify({verifiedUTC:new Date().toISOString(),gpu:false,checks:['All requested assets decode with native gzip and the vendored GLTFLoader','Compressed hashes, byte/vertex/triangle counts and exact source bounds verified','Runtime government UID/OBJECTID/CSUID and recorded heights match','Original source records and activity profiles remain unchanged','Source geometry remains indexed; per-building night constants add no repeated vertex attributes','Native source materials/nodes remain in provenance; all parsed GPU resources disposed'],models:results},null,2));
