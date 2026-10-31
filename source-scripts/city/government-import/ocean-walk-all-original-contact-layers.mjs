/** Incremental exact support evidence; retain runtime rejections per pair. No approval. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {supportSurface} from './support-contact.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),base=process.argv[2],hashes={};
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const folders=['government-xl-ocean-walk-six-original-component-closures-20261008','government-xl-ocean-walk-eleven-original-component-closures-20261008'];
const sources=new Map(),prior=[];
for(const folder of folders){const p='docs/astra-city/government-import/'+folder+'/';const inputs=read(p+'support-inputs.json');for(const r of inputs.sources){if(sources.has(r.uid))assert.equal(sources.get(r.uid).sourceSHA256,r.sourceSHA256);sources.set(r.uid,r);}prior.push(...read(p+'support-checks.json.gz').rows);}
const inputs={sources:[...sources.values()]};assert.equal(sources.size,18);assert.equal(prior.length,17);
const currentForms=new Map();
for(const row of inputs.sources){const tile=read('3d-viewer/'+row.source.tile);for(const b of tile.buildings)currentForms.set(b.uid,b);assert.deepEqual(currentForms.get(row.uid),row.source.building);}
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
async function get(uid){
 if(loaded.has(uid))return loaded.get(uid);
 const row=sources.get(uid),raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.candidate.entry.sha256);
 let asset;
 try{asset=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw),getBuilding:uid=>currentForms.get(uid)});}
 catch(error){if(error.message==='Official model does not fit its matched footprint')error.sourceUid=uid;throw error;}
 loaded.set(uid,asset);return asset;
}
const rows=[];
try{
 for(const uid of sources.keys())await get(uid);
 const surfaces=new Map([...loaded].map(([uid,asset])=>[uid,supportSurface(asset.record.modelGeometry)]));
 for(const pair of prior.filter(p=>!p.interface.passed)){
  const unresolved=pair.interface.unresolved.map(f=>{
   const [x,y,z]=f.position,otherOriginalContacts=[];
   for(const [uid,surface] of surfaces){
    if(uid===pair.uid||uid===pair.supportUid)continue;
    const contacts=surface.intersectionDetails(x,z).filter(h=>y-h.height>=-.1&&y-h.height<=1).map(h=>{
     const [a,b,c]=h.vertices;const normal=new THREE.Vector3().crossVectors(new THREE.Vector3().subVectors(new THREE.Vector3(...b),new THREE.Vector3(...a)),new THREE.Vector3().subVectors(new THREE.Vector3(...c),new THREE.Vector3(...a))).normalize();return {...h,normalY:normal.y};});
    if(contacts.length)otherOriginalContacts.push({uid,sourceSHA256:sources.get(uid).sourceSHA256,contacts});
   }
   return {...f,otherOriginalContacts};
  });
  rows.push({uid:pair.uid,sourceSHA256:pair.sourceSHA256,supportUid:pair.supportUid,originalUnresolved:unresolved.length,withOtherOriginalContactLayer:unresolved.filter(f=>f.otherOriginalContacts.length).length,unresolved,acceptanceGranted:false});
 }
}finally{for(const asset of loaded.values())disposeOfficialModel(asset);}
for(const p of ['source-scripts/city/government-import/ocean-walk-all-original-contact-layers.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js','3d-viewer/city/official-model-footprint-scopes.js','3d-viewer/city/official-model-footprint-scopes-ocean-walk.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
const {mkdirSync,existsSync}=await import('node:fs');assert(!existsSync(new URL(base+'contact-layers.json',root)));mkdirSync(new URL(base,root),{recursive:true});
writeFileSync(new URL(base+'contact-layers.json',root),JSON.stringify({rows,inputHashes:hashes,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,acceptanceGranted:false,qualification:'Exact original contact layers only. Downward caps or disconnected neighbouring surfaces are not structural support proof. All raw podium and identity/physical failures remain.'},null,2)+'\n');
console.log(JSON.stringify(rows.map(({uid,originalUnresolved,withOtherOriginalContactLayer})=>({uid,originalUnresolved,withOtherOriginalContactLayer}))));
