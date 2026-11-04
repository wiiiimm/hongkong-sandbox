/** Export exact runtime geometry for explicitly retained installed source UIDs.
 * Diagnostic only; no source/terrain edits or acceptance flags are added.
 */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const [requestPath,outputPath]=process.argv.slice(2),hashes={};
assert(requestPath&&outputPath);
const hash=b=>createHash('sha256').update(b).digest('hex');
function read(path){const raw=readFileSync(resolve(root,path));hashes[path]=hash(raw);return JSON.parse(raw);}
const requested=read(requestPath).uids;
assert(requested.length&&new Set(requested).size===requested.length);
const wanted=new Set(requested),manifest=read('3d-viewer/city/data/manifest.json'),entries=new Map(),forms=new Map();
for(const url of manifest.officialModelCatalogues){
 const path='3d-viewer/'+url;
 for(const entry of prepareModelCatalogue(read(path),pathToFileURL(resolve(root,path)).href)){
  if(!wanted.has(entry.uid))continue;
  assert(!entries.has(entry.uid));entries.set(entry.uid,{entry,path:resolve(root,dirname(path),entry.asset)});
 }
}
assert.equal(entries.size,wanted.size);
for(const tile of manifest.tiles){
 const path='3d-viewer/'+tile.url,raw=readFileSync(resolve(root,path)),buildings=JSON.parse(raw).buildings;
 for(const building of buildings){
  if(!wanted.has(building.uid))continue;
  assert(!forms.has(building.uid));forms.set(building.uid,building);hashes[path]=hash(raw);
 }
}
assert.equal(forms.size,wanted.size);
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const uid of requested){
 const {entry,path}=entries.get(uid),form=forms.get(uid),raw=readFileSync(path);
 assert.equal(hash(raw),entry.sha256);assert.equal(entry.objectId,form.objectId);assert.equal(entry.buildingCSUID,form.buildingCSUID);
 hashes[path.slice(root.length+1)]=hash(raw);
 const model=await loadOfficialModel(entry,form,lighting,{fetcher:async()=>new Response(raw)});
 try{
  const geometry=model.record.modelGeometry;
  assert.equal(geometry.index.length/3,entry.triangles);
  rows.push({uid,sourceSHA256:entry.sha256,worldBounds:entry.worldBounds,
    position:Array.from(geometry.position),index:Array.from(geometry.index)});
 }finally{disposeOfficialModel(model);}
}
hashes['source-scripts/city/government-import/retained-native-geometry.mjs']=hash(readFileSync(fileURLToPath(import.meta.url)));
for(const [path,expected] of Object.entries(hashes))assert.equal(hash(readFileSync(resolve(root,path))),expected,'Input changed during export');
writeFileSync(resolve(root,outputPath),gzipSync(JSON.stringify({rows,inputHashes:hashes,modelGeometryChanges:0,publication:false})));
console.log(JSON.stringify({models:rows.length,originalTriangles:rows.reduce((n,r)=>n+r.index.length/3,0),publication:false}));
