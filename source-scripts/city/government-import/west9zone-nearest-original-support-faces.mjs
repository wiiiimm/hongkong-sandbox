/** Exact face evidence for three old unresolved original WEST9ZONE contacts. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-west9zone-nearest-original-support-faces-20261008/',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const old='docs/astra-city/government-import/government-xl-west9zone-original-support-group-20261005/',selection=read(old+'selection.json.gz').rows,pairs=read(old+'interfaces.json.gz').rows;
const support=read('docs/astra-city/government-import/government-xl-west9zone-227099-native-terrain-group-20261005/selection.json.gz').rows[0];assert.equal(support.uid,'landsd/227099:0');assert.deepEqual(read('3d-viewer/'+support.source.tile).buildings.find(b=>b.uid===support.uid),support.source.building);const supportRaw=readFileSync(new URL(support.candidate.path,root));assert.equal(sha(supportRaw),support.sourceSHA256);hashes[support.candidate.path]=sha(supportRaw);
const light={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
const supportAsset=await loadOfficialModel(support.candidate.entry,support.source.building,light,{fetcher:async()=>new Response(supportRaw)});
const supportGeometry=supportAsset.record.modelGeometry;
function nearestSupport(position){const point=new THREE.Vector3(...position),triangle=new THREE.Triangle(),closest=new THREE.Vector3(),hits=[];for(let i=0;i<supportGeometry.index.length;i+=3){[triangle.a,triangle.b,triangle.c].forEach((v,k)=>v.fromArray(supportGeometry.position,supportGeometry.index[i+k]*3));if(triangle.getArea()===0)continue;triangle.closestPointToPoint(point,closest);hits.push({faceIndex:i/3,distanceM:closest.distanceTo(point),closest:closest.toArray(),vertices:[triangle.a.toArray(),triangle.b.toArray(),triangle.c.toArray()],normal:triangle.getNormal(new THREE.Vector3()).toArray()});}return hits.sort((a,b)=>a.distanceM-b.distanceM).slice(0,6);}
for(const pair of pairs){const row=selection.find(r=>r.uid===pair.uid);assert(row);const tile=read('3d-viewer/'+row.source.tile);assert.deepEqual(tile.buildings.find(b=>b.uid===row.uid),row.source.building);const raw=readFileSync(new URL(row.candidate.path,root));assert.equal(sha(raw),pair.sourceSHA256);hashes[row.candidate.path]=sha(raw);
 const asset=await loadOfficialModel(row.candidate.entry,row.source.building,light,{fetcher:async()=>new Response(raw)});
 try{const query=createSourceFaceQuery(asset.record.modelGeometry);for(const failure of pair.interface.unresolved){const faces=query(failure.position).map(f=>{const [a,b,c]=f.vertices.map(v=>new THREE.Vector3(...v));return {...f,areaSquared:new THREE.Vector3().crossVectors(b.clone().sub(a),c.clone().sub(a)).lengthSq()/4};});rows.push({uid:row.uid,sourceSHA256:pair.sourceSHA256,failure,faces,nearestSupportFaces:nearestSupport(failure.position),allIncidentFacesExactlyDegenerate:faces.length>0&&faces.every(f=>f.areaSquared===0)});}}
 finally{disposeOfficialModel(asset);}
}
disposeOfficialModel(supportAsset);assert.equal(rows.length,3);for(const p of ['source-scripts/city/government-import/west9zone-nearest-original-support-faces.mjs','source-scripts/city/government-import/source-face-query.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
assert(!existsSync(new URL(base+'faces.json',root)));mkdirSync(new URL(base,root),{recursive:true});writeFileSync(new URL(base+'faces.json',root),JSON.stringify({rows,inputHashes:hashes,acceptanceGranted:false,newlyInstalled:0,modelGeometryChanges:0,publication:false},null,2)+'\n');console.log(JSON.stringify(rows.map(r=>({uid:r.uid,position:r.failure.position,nearestSupportFaces:r.nearestSupportFaces.map(({faceIndex,distanceM,closest,normal})=>({faceIndex,distanceM,closest,normal}))}))));
