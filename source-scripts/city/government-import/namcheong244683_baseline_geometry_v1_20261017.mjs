/** Capture complete current fallback geometry for all projected-overlap neighbours. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/',dir=base+'government-xl-namcheong244683-baseline-geometry-v1-20261017/',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
const read=p=>{const b=readFileSync(new URL(p,root));hashes[p]=sha(b);return JSON.parse(b);};
const context=read(base+'government-xl-namcheong244683-current-identity-runtime-v1-20261017/identity-context.json');
const wanted=new Set(context.intersectingForms.map(r=>r.uid));assert.equal(wanted.size,5);
const manifest=read('3d-viewer/city/data/manifest.json'),native=new Map();
for(const url of manifest.officialModelCatalogues)for(const m of read('3d-viewer/'+url).models)if(wanted.has(m.uid))native.set(m.uid,{catalogue:url,entry:m});
const forms=[];for(const tile of manifest.tiles){const p='3d-viewer/'+tile.url,b=readFileSync(new URL(p,root)),matches=JSON.parse(b).buildings.filter(f=>wanted.has(f.uid));if(matches.length){hashes[p]=sha(b);forms.push(...matches);}}
assert.equal(forms.length,wanted.size);assert.equal(new Set(forms.map(f=>f.uid)).size,wanted.size);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);Object.assign(hashes,closure.inputHashes);
const {createBuildingGeometry}=await import(new URL('3d-viewer/city/building-geometry.js',root));const rows=[];
for(const f of forms){if(native.has(f.uid)){rows.push({uid:f.uid,currentForm:f,native:native.get(f.uid)});continue;}
 const g=createBuildingGeometry(f);try{const p=Array.from(g.attributes.position.array),index=g.index?Array.from(g.index.array):Array.from({length:p.length/3},(_,i)=>i);assert(p.every(Number.isFinite)&&index.length%3===0);rows.push({uid:f.uid,currentForm:f,position:p,index,completeFaces:index.length/3});}finally{g.dispose();}}
for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);assert(verifyModuleClosure(closure,root));mkdirSync(new URL(dir,root),{recursive:true});const out=new URL(dir+'geometry.json.gz',root);assert(!existsSync(out));writeFileSync(out,gzipSync(JSON.stringify({rows,inputHashes:hashes,recursiveProductionModuleClosure:closure,currentInputsVerified:true,fullAcceptance:false,sourceGeometryChanges:0})));console.log(JSON.stringify(rows.map(r=>({uid:r.uid,faces:r.completeFaces,native:!!r.native}))));
