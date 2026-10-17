/** UNEXECUTED bounded replay of exact existing six sample arrays/predicate; no source edits. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),sha=b=>createHash('sha256').update(b).digest('hex');
const closure=snapshotModuleClosure(import.meta.url,root);assert(closure.schema==='exact-literal-static-dynamic-resource-closure-v1'&&closure.computedImportsRejected&&closure.unsupportedDynamicImports===0&&closure.completeAuditedLiteralImportClosure);
const {guardSamples,gapBoundary,bits}=await import('./upton_six_basic_guard_samples_v1_20261012.mjs');
const {makeTerrainSampler}=await import('../../../3d-viewer/city/geo.js');
const inputPath=process.argv[2],outPath=process.argv[3],hashes={};assert(inputPath&&outPath);
function read(p){assert(typeof p==='string'&&!p.startsWith('/')&&!p.split('/').includes('..'));const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const input=read(inputPath);for(const q of input.inputRefs)assert.equal(sha(readFileSync(new URL(q.path,root))),q.sha256);
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],input.currentManifestSHA256);const data=read('3d-viewer/city/data/terrain.json'),selection=read(input.savedNeighbourInputs.path),report=read(input.savedNeighbourChecks.path);
for(const [p,h]of Object.entries(selection.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h);
data.patches=manifest.terrainPatches.map(p=>({entry:p,data:read('3d-viewer/'+p.url)}));const before=makeTerrainSampler({...data,patches:data.patches.map(p=>p.data)}),replaced=new Set(selection.patches.flatMap(p=>p.replaces?[p.replaces.url]:[])),patched={...data,patches:[...data.patches.filter(p=>!replaced.has(p.entry.url)).map(p=>p.data),...selection.patches.map(p=>{const d=read(p.path);assert.equal(hashes[p.path],p.sha256);return d;})]},after=makeTerrainSampler(patched),rows=[];
for(const uid of input.basicUIDs){
 const {building:b}=selection.rows.find(r=>r.building.uid===uid),prior=report.rows.find(r=>r.uid===uid),samples=guardSamples(b);assert.equal(samples.points.length,prior.checks);assert(prior.reasons.includes('increased-neighbour-ground-gap'));
 const old=samples.points.map(([x,z])=>before.height(x,z)),next=samples.points.map(([x,z])=>after.height(x,z));assert(old.every(Number.isFinite)&&next.every(Number.isFinite));const base=b.base+(b.minimum||0),beforeGap=[base-Math.max(...old),base-Math.min(...old)],afterGap=[base-Math.max(...next),base-Math.min(...next)];assert.deepEqual(beforeGap,prior.beforeGap);assert.deepEqual(afterGap,prior.afterGap);
 const boundary=gapBoundary(base,beforeGap[1]),records=samples.points.map((point,i)=>({sample:i,point,pointBitsHex:point.map(bits),origin:samples.origins[i],currentHeightM:old[i],candidateHeightM:next[i],currentHeightBitsHex:bits(old[i]),candidateHeightBitsHex:bits(next[i]),originalCandidateGapM:base-next[i],candidateExistingGapPredicatePass:base-next[i]<=boundary.existingGapLimitM}));assert.equal(records.every(q=>q.candidateExistingGapPredicatePass),afterGap[1]<=boundary.existingGapLimitM);
 rows.push({uid,exactCurrentForm:b,sampleSemantics:samples,boundary,rows:records,savedRawGuard:prior,noSupportOrContinuousCoverageCredit:true});
}
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);for(const q of input.inputRefs)assert.equal(sha(readFileSync(new URL(q.path,root))),q.sha256);verifyModuleClosure(closure,root);
writeFileSync(new URL(outPath,root),JSON.stringify({rows,inputHashes:hashes,completeLiteralDynamicResourceClosure:closure,startEndAllInputsVerified:true,samplerAndGuardAttributionOnly:true,terrainGeometryChanges:0,physicalAccepted:false},null,2)+'\n');
