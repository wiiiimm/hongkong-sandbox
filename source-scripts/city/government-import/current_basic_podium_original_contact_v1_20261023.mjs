/** Actual unchanged basic podiums under exact original towers. Diagnostic only. */
import{readFileSync,writeFileSync}from'node:fs';import{gunzipSync,gzipSync}from'node:zlib';import{createHash}from'node:crypto';import assert from'node:assert/strict';
import*as THREE from'../../../3d-viewer/vendor/three.module.js';
import{loadOfficialModel,disposeOfficialModel}from'../../../3d-viewer/city/official-model-assets.js';
import{createBuildingGeometry}from'../../../3d-viewer/city/building-geometry.js';
import{verifySupportInterface}from'./support-interface.mjs';
import{snapshotModuleClosure,verifyModuleClosure}from'./exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/government-xl-')&&!doc.includes('..'));
const read=p=>{const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw)};
const input=read(doc+'/input.json.gz'),manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],input.manifestSHA256);
const native=new Set();for(const url of manifest.officialModelCatalogues)for(const m of read('3d-viewer/'+url).models)native.add(m.uid);
for(const e of input.evidenceRefs)assert.equal(sha(readFileSync(new URL(e.path,root))),e.sha256);
const closures=['3d-viewer/city/building-geometry.js','3d-viewer/city/official-model-assets.js','source-scripts/city/government-import/support-interface.mjs'].map(p=>snapshotModuleClosure(new URL(p,root),root));for(const c of closures)Object.assign(hashes,c.inputHashes);
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
const save=()=>writeFileSync(new URL(doc+'/checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,sourceGeometryChanges:0,installationApproved:false,publication:false})));
for(const r of input.rows){
 const source=r.source,b=r.supportForm.building;assert.equal(b.uid,r.supportUid);assert.equal(source.source.building.parent,b.parent);assert.equal(b.structureType,'Podium');assert(source.source.building.parent);
 assert.deepEqual(read('3d-viewer/'+r.supportForm.tile).buildings.find(f=>f.uid===b.uid),b);
 const raw=readFileSync(new URL(source.candidate.path,root));hashes[source.candidate.path]=sha(raw);assert.equal(sha(raw),source.sourceSHA256);assert.equal(sha(raw),source.candidate.entry.sha256);
 let asset,g;
 try{
  asset=await loadOfficialModel({...source.candidate.entry,assetURL:'https://diagnostic.invalid/original.glb.gz'},source.source.building,lighting,{fetcher:async()=>new Response(raw)});
  g=createBuildingGeometry(b);const support={position:Array.from(g.attributes.position.array),index:g.index?Array.from(g.index.array):Array.from({length:g.attributes.position.count},(_,i)=>i)};
  const proof=verifySupportInterface(asset.record.modelGeometry,source.candidate.entry.worldBounds[0][1],support),isActualBasic=!native.has(b.uid);
  rows.push({uid:r.uid,supportUid:b.uid,sourceSHA256:source.sourceSHA256,supportForm:b,supportGeometry:support,supportGeometrySHA256:sha(Buffer.from(new Float32Array(support.position).buffer)),basicIsCurrentFinalSupport:isActualBasic,proof,canonicalContactPassed:proof.passed,usableBasicSupportDiagnostic:proof.passed&&isActualBasic,installationApproved:false});
  console.log(JSON.stringify({uid:r.uid,supportUid:b.uid,passed:proof.passed,strictContacts:proof.strictContacts,unresolved:proof.unresolved.length,basicIsActual:isActualBasic}));save();
 }finally{if(asset)disposeOfficialModel(asset);g?.dispose()}
}
for(const c of closures)assert(verifyModuleClosure(c,root));for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);save();
