/** Capture every actual rendered terrain facet touching recovered original bounds. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),doc='docs/astra-city/government-import/government-xl-unmapped-whole-context-v1-20261015';
const hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
const read=p=>{const b=readFileSync(new URL(p,root));hashes[p]=sha(b);return JSON.parse(b);};
const binding=read('docs/astra-city/government-import/government-xl-unmapped-two-primary-evidence-v1-20261015/viewer-bindings.json');
const native=read('docs/astra-city/government-import/government-xl-unmapped-full-bounds-provider-v1-20261015/native-inputs.json');
const regions=binding.rows.map(r=>{const b=native.rows.find(n=>n.model.modelId===r.modelId).model.worldBounds;return {modelId:r.modelId,bounds:[b[0][0]-2,b[0][2]-2,b[1][0]+2,b[1][2]+2],position:[],origins:[]};});
const closure=snapshotModuleClosure(new URL('3d-viewer/city/world.js',root),root);Object.assign(hashes,closure.inputHashes);
const manifest=read('3d-viewer/city/data/manifest.json'),data=read('3d-viewer/city/data/terrain.json');data.patches=manifest.terrainPatches.map(p=>read('3d-viewer/'+p.url));
const {makeTerrain}=await import(new URL('3d-viewer/city/world.js',root));const THREE=await import(new URL('3d-viewer/vendor/three.module.js',root));const ground=makeTerrain(data);ground.updateMatrixWorld(true);let faces=0,ordinal=0;
try{
 ground.traverse(m=>{if(!m.isMesh)return;assert(m.matrixWorld.equals(new THREE.Matrix4()));const p=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??p.count,mesh=ordinal++;assert(n%3===0);for(let i=0;i<n;i+=3){faces++;const vs=[0,1,2].map(k=>{const j=ix?ix.getX(i+k):i+k;return[p.getX(j),p.getY(j),p.getZ(j)];});assert(vs.flat().every(Number.isFinite));const xs=vs.map(v=>v[0]),zs=vs.map(v=>v[2]);for(const r of regions){const b=r.bounds;if(Math.max(...xs)<b[0]||Math.min(...xs)>b[2]||Math.max(...zs)<b[1]||Math.min(...zs)>b[3])continue;r.position.push(...vs.flat());r.origins.push({mesh,face:i/3});}}});
 for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);assert(verifyModuleClosure(closure,root));for(const r of regions)assert(r.position.length>0);
 const out=new URL(doc+'/ground.json.gz',root);assert(!existsSync(out));writeFileSync(out,gzipSync(JSON.stringify({regions,completeTraversedFaces:faces,inputHashes:hashes,closure,sourceGeometryChanges:0,terrainChanges:0,physicalAccepted:false})));console.log(JSON.stringify(regions.map(r=>({modelId:r.modelId,groundFaces:r.position.length/9}))));
}finally{ground.traverse(m=>{m.geometry?.dispose();for(const a of [].concat(m.material||[]))a.dispose();});}
