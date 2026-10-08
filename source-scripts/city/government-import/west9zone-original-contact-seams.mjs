/** Check exact original WEST9ZONE seam correction; no publication or model edits. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifyOriginalContactSeams} from './original-contact-seams.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-west9zone-original-contact-seams-20261008/',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const old='docs/astra-city/government-import/government-xl-west9zone-original-support-group-20261005/',sources=read(old+'selection.json.gz').rows;
const support=read('docs/astra-city/government-import/government-xl-west9zone-227099-native-terrain-group-20261005/selection.json.gz').rows[0];assert.equal(support.uid,'landsd/227099:0');sources.push(support);
const light={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map(),rows=[];
try{
 for(const row of sources){const b=read('3d-viewer/'+row.source.tile).buildings.find(b=>b.uid===row.uid);assert.deepEqual(b,row.source.building);const raw=readFileSync(new URL(row.candidate.path,root));assert.equal(sha(raw),row.sourceSHA256);hashes[row.candidate.path]=sha(raw);loaded.set(row.uid,await loadOfficialModel(row.candidate.entry,b,light,{fetcher:async()=>new Response(raw)}));}
 for(const row of sources.filter(r=>r.uid!==support.uid)){const proof=verifyOriginalContactSeams(loaded.get(row.uid).record.modelGeometry,row.native.model.worldBounds[0][1],loaded.get(support.uid).record.modelGeometry);rows.push({uid:row.uid,sourceSHA256:row.sourceSHA256,supportUid:support.uid,supportSHA256:support.sourceSHA256,interface:proof,installationApproved:false});}
}finally{for(const asset of loaded.values())disposeOfficialModel(asset);}
for(const p of ['source-scripts/city/government-import/west9zone-original-contact-seams.mjs','source-scripts/city/government-import/original-contact-seams.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
assert(!existsSync(new URL(base+'interfaces.json',root)));mkdirSync(new URL(base,root),{recursive:true});writeFileSync(new URL(base+'interfaces.json',root),JSON.stringify({rows,inputHashes:hashes,newlyInstalled:0,modelGeometryChanges:0,publication:false},null,2)+'\n');console.log(JSON.stringify(rows.map(r=>({uid:r.uid,passed:r.interface.passed,rawUnresolved:r.interface.rawInterface.unresolved.length,seamCorrections:r.interface.seamCorrections,unresolved:r.interface.unresolved.length}))));
