/** Runtime corroboration of exact retained-parent structural proof; no publication. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},hash=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/')&&!doc.includes('..'));
const read=p=>{const raw=readFileSync(new URL(p,root));hashes[p]=hash(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);};
const output=new URL(doc+'/sampler.json',root);assert(!existsSync(output));
const input=read(doc+'/input.json');for(const [p,h]of Object.entries(input.inputHashes))assert.equal(hash(readFileSync(new URL(p,root))),h);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/geo.js',root),root);assert(verifyModuleClosure(closure,root));Object.assign(hashes,closure.inputHashes);
const {makeTerrainSampler}=await import('../../../3d-viewer/city/geo.js');
const manifest=read('3d-viewer/city/data/manifest.json'),base=read('3d-viewer/city/data/terrain.json'),plan=read(input.plan)[0];
assert.equal(manifest.terrainPatches.filter(p=>p.url===plan.replaces.url).length,1);
base.patches=manifest.terrainPatches.map(p=>read('3d-viewer/'+p.url));
assert.equal(hashes['3d-viewer/'+plan.replaces.url],plan.replaces.sha256);
const before=makeTerrainSampler(base);
// Mirrors publisher removal followed by append, including patch precedence.
const variant={...base,patches:base.patches.filter((p,i)=>manifest.terrainPatches[i].url!==plan.replaces.url)};
variant.patches.push(read(plan.path));assert.equal(hashes[plan.path],plan.sha256);const after=makeTerrainSampler(variant);
const inventory=read(input.inventory),points=new Map();assert.equal(inventory.rows.length,6727);
for(const r of inventory.rows)for(const [lo,hi]of r.completeFourWorldBounds)for(const [x,z]of [[lo[0],lo[2]],[hi[0],lo[2]],[hi[0],hi[2]],[lo[0],hi[2]],[(lo[0]+hi[0])/2,(lo[2]+hi[2])/2]])points.set(x+','+z,[x,z]);
const errors=[],differences=[];let checked=0;
for(const [x,z]of points.values()){
 try{const a=[before.height(x,z),before.raw(x,z),before.resolutionAt(x,z)],b=[after.height(x,z),after.raw(x,z),after.resolutionAt(x,z)];assert(a.every(Number.isFinite)&&b.every(Number.isFinite));if(a.some((v,i)=>v!==b[i]))differences.push({x,z,before:a,after:b});checked++;}catch(e){errors.push({x,z,error:e.message});}
}
for(const [p,h]of Object.entries({...input.inputHashes,...hashes}))assert.equal(hash(readFileSync(new URL(p,root))),h);assert(verifyModuleClosure(closure,root));
writeFileSync(output,JSON.stringify({currentActors:inventory.rows.length,uniqueProbePoints:points.size,checked,errors,differences,passed:errors.length===0&&differences.length===0,completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,publication:false,qualification:'Four-world bound corners/centres corroborate separate complete structural/domain proof. These probes alone are not a complete-source or universal terrain equivalence proof.'})+'\n');console.log(JSON.stringify({checked,errors:errors.length,differences:differences.length}));
