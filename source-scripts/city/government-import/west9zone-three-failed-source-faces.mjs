/** Exact face evidence for three old unresolved original WEST9ZONE contacts. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-west9zone-three-failed-source-faces-20261008/',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const old='docs/astra-city/government-import/government-xl-west9zone-original-support-group-20261005/',selection=read(old+'selection.json.gz').rows,pairs=read(old+'interfaces.json.gz').rows;
const light={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const pair of pairs){const row=selection.find(r=>r.uid===pair.uid);assert(row);const tile=read('3d-viewer/'+row.source.tile);assert.deepEqual(tile.buildings.find(b=>b.uid===row.uid),row.source.building);const raw=readFileSync(new URL(row.candidate.path,root));assert.equal(sha(raw),pair.sourceSHA256);hashes[row.candidate.path]=sha(raw);
 const asset=await loadOfficialModel(row.candidate.entry,row.source.building,light,{fetcher:async()=>new Response(raw)});
 try{const query=createSourceFaceQuery(asset.record.modelGeometry);for(const failure of pair.interface.unresolved){const faces=query(failure.position).map(f=>{const [a,b,c]=f.vertices.map(v=>new THREE.Vector3(...v));return {...f,areaSquared:new THREE.Vector3().crossVectors(b.clone().sub(a),c.clone().sub(a)).lengthSq()/4};});rows.push({uid:row.uid,sourceSHA256:pair.sourceSHA256,failure,faces,allIncidentFacesExactlyDegenerate:faces.length>0&&faces.every(f=>f.areaSquared===0)});}}
 finally{disposeOfficialModel(asset);}
}
assert.equal(rows.length,3);for(const p of ['source-scripts/city/government-import/west9zone-three-failed-source-faces.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
assert(!existsSync(new URL(base+'faces.json',root)));mkdirSync(new URL(base,root),{recursive:true});writeFileSync(new URL(base+'faces.json',root),JSON.stringify({rows,inputHashes:hashes,acceptanceGranted:false,newlyInstalled:0,modelGeometryChanges:0,publication:false},null,2)+'\n');console.log(JSON.stringify(rows.map(r=>({uid:r.uid,failure:r.failure,allExactlyDegenerate:r.allIncidentFacesExactlyDegenerate,faces:r.faces.map(f=>({faceIndex:f.faceIndex,vertices:f.vertices,areaSquared:f.areaSquared,normal:f.normal}))}))));
