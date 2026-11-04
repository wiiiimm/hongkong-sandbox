/** Actual unchanged basic companions against the proposed original podium. Diagnostic only. */
import {readFileSync,writeFileSync} from 'node:fs';import{gunzipSync,gzipSync}from'node:zlib';import{createHash}from'node:crypto';import assert from'node:assert/strict';
import{snapshotModuleClosure,verifyModuleClosure}from'./exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import{verifySupportInterface}from'./support-interface.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
const read=p=>{const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);};
const input=read(doc+'/input.json.gz');for(const e of input.evidenceRefs)assert.equal(sha(readFileSync(new URL(e.path,root))),e.sha256);
const closures=['3d-viewer/city/building-geometry.js','source-scripts/city/government-import/support-interface.mjs'].map(p=>snapshotModuleClosure(new URL(p,root),root));for(const c of closures)Object.assign(hashes,c.inputHashes);
const {createBuildingGeometry}=await import('../../../3d-viewer/city/building-geometry.js');const rows=[];
for(const b of input.buildings){const g=createBuildingGeometry(b);try{const position=Array.from(g.attributes.position.array),index=g.index?Array.from(g.index.array):Array.from({length:position.length/3},(_,i)=>i);const proof=verifySupportInterface({position,index},Math.min(...position.filter((_,i)=>i%3===1)),input.podium);rows.push({uid:b.uid,building:b,position,index,proof});}finally{g.dispose();}}
for(const c of closures)assert(verifyModuleClosure(c,root));for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);for(const e of input.evidenceRefs)assert.equal(sha(readFileSync(new URL(e.path,root))),e.sha256);
writeFileSync(new URL(doc+'/support.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,installationApproved:false})));console.log(JSON.stringify(rows.map(r=>({uid:r.uid,passed:r.proof.passed,samples:r.proof.samples,contacts:r.proof.strictContacts,unresolved:r.proof.unresolved.length}))));
