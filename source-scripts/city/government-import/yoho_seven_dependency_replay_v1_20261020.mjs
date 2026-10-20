/** Verify a metadata-only proposal through the actual production loader. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hash=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=hash(b);return JSON.parse(b);}
const packet=read(doc+'/proposal.json'),before=packet.before,after=packet.after,forms=new Map(packet.forms.map(b=>[b.uid,b]));
assert.equal(before.models.length,7);assert.equal(after.models.length,7);assert.equal(packet.changes.length,6);
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},results=[];
for(const [i,cat] of [before,after].entries()){
 const entries=prepareModelCatalogue(cat,new URL(packet.cataloguePath,root).href),seen=[];
 for(const entry of entries){const p=new URL(entry.assetURL);const raw=readFileSync(p);assert.equal(hash(raw),entry.sha256);const relative=p.pathname.slice(root.pathname.length);hashes[relative]=hash(raw);
  const model=await loadOfficialModel(entry,forms.get(entry.uid),lighting,{fetcher:async()=>new Response(raw),getBuilding:uid=>forms.get(uid)});
  try{const g=model.record.modelGeometry;assert.equal(g.index.length/3,entry.triangles);seen.push({uid:entry.uid,faces:g.index.length/3,positionSHA256:hash(Buffer.from(g.position.buffer,g.position.byteOffset,g.position.byteLength)),indexSHA256:hash(Buffer.from(g.index.buffer,g.index.byteOffset,g.index.byteLength))});}finally{disposeOfficialModel(model);}
 }
 results.push(seen);
}
assert.deepEqual(results[0],results[1]);
for(const change of packet.changes){const own=after.models.find(e=>e.uid===change.uid),support=after.models.find(e=>e.uid===change.supportUID),dep=own.supportDependencies[change.dependencyIndex];assert.deepEqual(dep,change.after);assert.equal(dep.state,'installed');assert.equal(dep.csuid,support.buildingCSUID);}
for(const [p,h] of Object.entries(hashes))assert.equal(hash(readFileSync(new URL(p,root))),h);
writeFileSync(new URL(doc+'/loader-check.json',root),JSON.stringify({passed:true,rows:results[1],geometryIdentical:true,dependencyChanges:6,inputHashes:hashes}));
console.log(JSON.stringify({passed:true,models:7,dependencies:6,geometryIdentical:true}));
