/** Exact current source-vertex attribution only; no tolerance or acceptance changes. */
import{readFileSync,writeFileSync,mkdirSync}from'node:fs';
import{gunzipSync,gzipSync}from'node:zlib';
import{createHash}from'node:crypto';
import assert from'node:assert/strict';
import{loadOfficialModel,prepareModelCatalogue,disposeOfficialModel}from'../../../3d-viewer/city/official-model-assets.js';
import{lowRimSamples}from'./support-contact.mjs';
import*as THREE from'../../../3d-viewer/vendor/three.module.js';
const root=new URL('../../../',import.meta.url),doc='docs/astra-city/government-import/government-xl-citywalk-current294-incident-faces-v2-20261015',hashes={},hash=b=>createHash('sha256').update(b).digest('hex');
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=hash(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const prior=read('docs/astra-city/government-import/government-xl-citywalk-saved294-source-layer-attribution-v1-20261014/complete-saved294-source-layer-attribution.json.gz'),points=prior.sourceWorldRows[0].rows;assert.equal(points.length,294);
const census=read('docs/astra-city/government-import/government-xl-complete-current-native-actual-position-matrix-bounds-v5-20261015/input.json.gz');
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],census.currentManifest.sha256);
const uids=new Set(points.map(p=>p.uid)),entries=new Map(),bindings=new Map(census.rows.map(r=>[r.uid,r]));
for(const url of manifest.officialModelCatalogues){const p='3d-viewer/'+url,cat=read(p);for(const e of prepareModelCatalogue(cat,new URL(p,root)))if(uids.has(e.uid))entries.set(e.uid,e);}
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const uid of uids){const binding=bindings.get(uid),entry=entries.get(uid);assert(entry&&binding);assert.equal(entry.sha256,points.find(p=>p.uid===uid).originalTowerSourceSHA256);const raw=readFileSync(new URL(binding.source.path,root));hashes[binding.source.path]=hash(raw);assert.equal(hash(raw),entry.sha256);
const model=await loadOfficialModel(entry,binding.currentBuilding,lighting,{fetcher:async()=>new Response(raw),getBuilding:id=>census.currentAllNativeSourceForms[id]});
try{const g=model.record.modelGeometry,p=g.position,ix=g.index,lookup=new Map(),incident=new Map();
for(let i=0;i<p.length;i+=3){const k=JSON.stringify([p[i],p[i+1],p[i+2]]);if(!lookup.has(k))lookup.set(k,[]);lookup.get(k).push(i/3);}
for(let i=0;i<ix.length;i+=3)for(let k=0;k<3;k++){const v=ix[i+k];if(!incident.has(v))incident.set(v,[]);incident.get(v).push(i/3);}
const edgePoints=new Map(),bottom=entry.worldBounds[0][1],rim=new Set(lowRimSamples(g,bottom).map(p=>JSON.stringify(p)));
for(let i=0;i<ix.length;i+=3){const v=[0,1,2].map(k=>Array.from(p.slice(ix[i+k]*3,ix[i+k]*3+3)));for(let edge=0;edge<3;edge++){const a=v[edge],b=v[(edge+1)%3];if(Math.max(a[1],b[1])>bottom+.35)continue;const steps=Math.ceil(Math.hypot(a[0]-b[0],a[2]-b[2]));for(let j=1;j<steps;j++){const q=a.map((n,k)=>n+(b[k]-n)*j/steps),key=JSON.stringify(q);if(!edgePoints.has(key))edgePoints.set(key,[]);edgePoints.get(key).push({faceIndex:i/3,edge,j,steps});}}}
const sourcePoints=points.filter(r=>r.uid===uid).map(r=>{const key=JSON.stringify(r.failure.position),vertices=lookup.get(key)||[],edges=edgePoints.get(key)||[];assert(rim.has(key),'Saved point not reproduced by current exact sampler');return{exactSamplerEdges:edges,ordinal:r.ordinal,failure:r.failure,exactCurrentVertexIndices:vertices,incidentFaceIndices:[...new Set([...vertices.flatMap(v=>incident.get(v)||[]),...edges.map(e=>e.faceIndex)])].sort((a,b)=>a-b)};});
const ids=[...new Set(sourcePoints.flatMap(r=>r.incidentFaceIndices))].sort((a,b)=>a-b);const faces=ids.map(id=>({faceIndex:id,index:Array.from(ix.slice(id*3,id*3+3)),vertices:Array.from(ix.slice(id*3,id*3+3),v=>Array.from(p.slice(v*3,v*3+3)))}));
rows.push({uid,sourceSHA256:entry.sha256,totalFaces:ix.length/3,points:sourcePoints,incidentFaces:faces,unmatchedPoints:sourcePoints.filter(r=>!r.incidentFaceIndices.length).map(r=>r.ordinal),allPointsExactSamplerAttributed:sourcePoints.every(r=>r.incidentFaceIndices.length)});
}finally{disposeOfficialModel(model);}}
for(const p of ['source-scripts/city/government-import/citywalk_current294_incident_faces_v2_20261015.mjs','3d-viewer/city/official-model-assets.js','3d-viewer/city/building-geometry.js','source-scripts/city/government-import/support-contact.mjs'])hashes[p]=hash(readFileSync(new URL(p,root)));
for(const[p,h]of Object.entries(hashes))assert.equal(hash(readFileSync(new URL(p,root))),h);
mkdirSync(new URL(doc+'/',root),{recursive:true});writeFileSync(new URL(doc+'/incident-faces.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,sourceGeometryChanges:0,acceptance:false,scope:'Exact current runtime vertex or original lowRimSamples edge arithmetic equality; complete saved membership reproduced. No distance tolerance.'})));
console.log(JSON.stringify(rows.map(r=>({uid:r.uid,points:r.points.length,unmatched:r.unmatchedPoints.length,incidentFaces:r.incidentFaces.length}))));
