/** Replay the production asset loader; validate only the210 corrected edges. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const doc='docs/astra-city/government-import/government-xl-all-installed-dependency-metadata-applied-v1-20261010/';
const hashes={},hash=raw=>createHash('sha256').update(raw).digest('hex');
const read=p=>{const raw=readFileSync(resolve(root,p));hashes[p]=hash(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);};
const receipt=read(doc+'result.json'),packet=read(receipt.proposal.path),uids=new Set(receipt.uids);
assert.equal(uids.size,254);assert.equal(receipt.newlyInstalled,0);assert.equal(packet.changes.length,210);
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
assert.equal(entries.size,254);assert.equal(forms.size,254);
for(const change of packet.changes){
 const own=entries.get(change.uid).entry,support=entries.get(change.supportUID).entry;
 const dependency=own.supportDependencies[change.dependencyIndex];
 assert.deepEqual(dependency,change.after);assert.equal(dependency.state,'installed');
 assert.equal(dependency.csuid,support.buildingCSUID);assert.equal(own.sha256,change.ownSourceSHA256);assert.equal(support.sha256,change.supportSourceSHA256);
 if(dependency.sha256)assert.equal(dependency.sha256,support.sha256);
}
const lighting={night:{value:0},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const [uid,{entry,path}] of entries){
 const raw=readFileSync(path);assert.equal(hash(raw),entry.sha256);assert.equal(raw.length,entry.bytes);hashes[path.slice(root.length+1)]=hash(raw);
 const model=await loadOfficialModel(entry,forms.get(uid),lighting,{fetcher:async()=>new Response(raw)});
 const g=model.record.modelGeometry;assert.equal(g.index.length/3,entry.triangles);assert(g.position.every(Number.isFinite));
 rows.push({uid,sourceSHA256:entry.sha256,faces:g.index.length/3,loaded:true});disposeOfficialModel(model);
 if(rows.length%25===0)console.log(JSON.stringify({loaded:rows.length,total:254}));
}
for(const [path,sha] of Object.entries(hashes))assert.equal(hash(readFileSync(resolve(root,path))),sha,'Changed during production replay');
const output={passed:true,rows,correctedDependencies:210,retainedFallbackOrLegacyRelations:27,hashes,newlyInstalled:0,geometryChanges:0,physicalAcceptance:false,qualification:'Actual production catalogue parser and254complete assets loaded and disposed. Only210 metadata-corrected native dependencies validated;27intentional fallback/legacy relations remain unchanged. No terrain or new model acceptance.'};
writeFileSync(resolve(root,doc+'runtime-metadata-check.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({passed:true,models:rows.length,dependencies:210,newlyInstalled:0}));
