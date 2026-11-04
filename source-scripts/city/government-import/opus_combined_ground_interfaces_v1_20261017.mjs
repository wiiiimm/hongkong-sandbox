/** Canonical unchanged rim checks against the complete terrain and original podium. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {verifySupportInterface} from './support-interface.mjs';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),hash=b=>createHash('sha256').update(b).digest('hex'),inputs={};
function read(p){const b=readFileSync(new URL(p,root));inputs[p]=hash(b);return JSON.parse(gunzipSync(b));}
const [worldPath,groundPath,out]=process.argv.slice(2),worlds=read(worldPath),ground=read(groundPath),closure=snapshotModuleClosure(new URL('source-scripts/city/government-import/support-interface.mjs',root),root);
const geom=t=>({position:t.flat(2),index:Array.from({length:t.length*3},(_,i)=>i)}),base=[];
for(let i=0;i<ground.index.length;i+=3)base.push(ground.index.slice(i,i+3).map(j=>ground.position.slice(j*3,j*3+3)));
const rows=[];
for(const [mode,w]of Object.entries(worlds))for(const uid of ['landsd/322573:0','landsd/319559:0']){
 const source=geom(w[uid]),support=geom([...base,...w['landsd/248432:0']]);let bottom=Infinity;for(let i=1;i<source.position.length;i+=3)bottom=Math.min(bottom,source.position[i]);
 const proof=verifySupportInterface(source,bottom,support);rows.push({mode,uid,bottom,proof});console.log(mode,uid,JSON.stringify({samples:proof.samples,strict:proof.strictContacts,walls:proof.wallIntersections,unresolved:proof.unresolved.length,missing:proof.unresolved.filter(x=>x.gap==null).length}));
}
assert(verifyModuleClosure(closure,root));for(const [p,h]of Object.entries(inputs))assert.equal(hash(readFileSync(new URL(p,root))),h);
writeFileSync(new URL(out,root),gzipSync(JSON.stringify({rows,inputHashes:inputs,closure,sourceGeometryChanges:0,fullAcceptance:false})));
