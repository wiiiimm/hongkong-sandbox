/** Original source-space contact diagnosis; no renderer or installation acceptance. */
import assert from 'node:assert/strict';
import{readFileSync,writeFileSync}from'node:fs';
import{gunzipSync,gzipSync}from'node:zlib';
import{createHash}from'node:crypto';
import{verifySupportInterface}from'./support-interface.mjs';
import{snapshotModuleClosure,verifyModuleClosure}from'./exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[input,out]=process.argv.slice(2),raw=readFileSync(new URL(input,root)),d=JSON.parse(gunzipSync(raw)),hash=b=>createHash('sha256').update(b).digest('hex'),closure=snapshotModuleClosure(new URL('./support-interface.mjs',import.meta.url),root),geom=t=>({position:t.flat(2),index:Array.from({length:t.length*3},(_,i)=>i)}),source=geom(d.source.triangles);
let bottom=Infinity;for(let i=1;i<source.position.length;i+=3)bottom=Math.min(bottom,source.position[i]);
const rows=[];for(const ids of [['landsd/223206:0'],['landsd/222465:0'],['landsd/222465:0','landsd/223206:0']]){const proof=verifySupportInterface(source,bottom,geom(d.supports.filter(s=>ids.includes(s.uid)).flatMap(s=>s.triangles)));rows.push({supportUids:ids,proof});console.log(JSON.stringify({supportUids:ids,samples:proof.samples,strict:proof.strictContacts,walls:proof.wallIntersections,unresolved:proof.unresolved.length}));}
assert(verifyModuleClosure(closure,root));assert.equal(hash(readFileSync(new URL(input,root))),hash(raw));writeFileSync(new URL(out,root),gzipSync(JSON.stringify({rows,bottom,sourceGeometryChanges:0,inputHashes:{[input]:hash(raw)},closure,fullAcceptance:false})));
