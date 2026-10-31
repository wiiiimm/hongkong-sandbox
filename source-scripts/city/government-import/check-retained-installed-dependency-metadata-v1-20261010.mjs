/** Check the real catalogue loader and original assets after a metadata-only repair. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const doc='docs/astra-city/government-import/government-xl-retained-installed-dependency-metadata-applied-v1-20261010/';
const hashes={},hash=raw=>createHash('sha256').update(raw).digest('hex');
const read=p=>{const raw=readFileSync(resolve(root,p));hashes[p]=hash(raw);return JSON.parse(raw);};
const receipt=read(doc+'result.json'),uids=new Set(receipt.uids);
assert.equal(uids.size,4);assert.equal(receipt.newlyInstalled,0);
const manifest=read('3d-viewer/city/data/manifest.json'),forms=new Map(),entries=new Map();
for(const t of manifest.tiles)for(const b of read('3d-viewer/'+t.url).buildings)if(uids.has(b.uid)){
 assert(!forms.has(b.uid));forms.set(b.uid,b);
}
for(const url of manifest.officialModelCatalogues){
 const path='3d-viewer/'+url;
 for(const entry of prepareModelCatalogue(read(path),pathToFileURL(resolve(root,path)).href))if(uids.has(entry.uid)){
  assert(!entries.has(entry.uid));entries.set(entry.uid,{entry,path:resolve(root,dirname(path),entry.asset)});
 }
}
assert.equal(entries.size,4);assert.equal(forms.size,4);
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const [uid,{entry,path}] of entries){
 for(const dependency of entry.supportDependencies||[]){
  const support=entries.get(dependency.uid)?.entry;
  assert(dependency.state==='installed'&&support&&support.buildingCSUID===dependency.csuid,'Pinned installed native dependency unavailable');
  if(dependency.sha256)assert.equal(dependency.sha256,support.sha256);
 }
 const raw=readFileSync(path);assert.equal(hash(raw),entry.sha256);
 hashes[path.slice(root.length+1)]=hash(raw);
 const model=await loadOfficialModel(entry,forms.get(uid),lighting,{fetcher:async()=>new Response(raw)});
 const g=model.record.modelGeometry;assert.equal(g.index.length/3,entry.triangles);
 assert(g.position.every(Number.isFinite));
 rows.push({uid,sourceSHA256:entry.sha256,faces:g.index.length/3,dependencies:entry.supportDependencies||[],loaded:true});
 disposeOfficialModel(model);
}
const output={passed:true,rows,hashes,newlyInstalled:0,geometryChanges:0,physicalAcceptance:false,qualification:'Actual production catalogue parser/asset loader and unchanged strict dependency assertion, without terrain or new model acceptance.'};
writeFileSync(resolve(root,doc+'runtime-metadata-check.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({passed:true,models:rows.length,newlyInstalled:0}));
