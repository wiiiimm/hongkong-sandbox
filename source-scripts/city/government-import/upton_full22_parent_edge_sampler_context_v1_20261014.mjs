/** ROOT-only 860 saved seam queries. No renderer, rays, geometry or live edits. */
import {readFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js?v=20261010-finite1';
import {bits} from './upton_six_basic_guard_samples_v1_20261012.mjs';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={};assert(doc);
const sha=b=>createHash('sha256').update(b).digest('hex');
function raw(p){const b=readFileSync(new URL(p,root)),h=sha(b);if(hashes[p])assert.equal(hashes[p],h,p);hashes[p]=h;return b;}
function read(p){const b=raw(p);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/sampler-input.json.gz');assert.equal(input.schema,'upton-full22-saved-parent-edge-sampler-context-v1');assert.equal(input.rows.length,860);
for(const q of input.allCurrentInputRefs)assert.equal(sha(raw(q.path)),q.sha256,q.path);
const closure=snapshotModuleClosure(import.meta.url,root);assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure);assert.equal(closure.unsupportedDynamicImports,0);
for(const[p,h]of Object.entries(closure.inputHashes))assert.equal(sha(raw(p)),h,p);
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],input.currentManifestSHA256);
const base=read('3d-viewer/city/data/terrain.json'),patches=manifest.terrainPatches.map(e=>({path:'3d-viewer/'+e.url,data:read('3d-viewer/'+e.url)}));
const at=patches.findIndex(p=>p.path===input.retainedParent.path);assert(at>=0);assert.equal(hashes[input.retainedParent.path],input.retainedParent.sha256);
const candidate=read(input.candidate.path);assert.equal(hashes[input.candidate.path],input.candidate.sha256);
const old=patches[at].data,before=makeTerrainSampler({...base,patches:patches.map(p=>p.data)}),after=makeTerrainSampler({...base,patches:patches.map((p,i)=>i===at?candidate:p.data)}),baseGrid=makeTerrainSampler(base),candidateSampler=makeTerrainSampler(candidate),oldSampler=makeTerrainSampler(old),candidateNative=nativeTerrainSurface(candidate.nativeMesh),oldNative=nativeTerrainSurface(old.nativeMesh);
function query(fn){try{const value=fn();assert(value===null||Number.isFinite(value));return {value,bitsHex:value===null?null:bits(value),error:null};}catch(e){return {value:null,bitsHex:null,error:String(e),noErrorWaiver:true};}}
const rows=input.rows.map((r,occurrence)=>{const {x,y,z}=r.savedMeasuredEdgeVerbatim;return {occurrence,savedMeasuredEdgeVerbatim:r.savedMeasuredEdgeVerbatim,candidateVertexProvenance:r.candidateVertexProvenance,actualBeforeSceneHeight:query(()=>before.height(x,z)),actualAfterSceneHeight:query(()=>after.height(x,z)),actualBaseGridHeight:query(()=>baseGrid.height(x,z)),actualCandidatePatchHeight:query(()=>candidateSampler.height(x,z)),actualRetainedPatchHeight:query(()=>oldSampler.height(x,z)),actualCandidateNativeTop:query(()=>candidateNative.height(x,z)),actualRetainedNativeTop:query(()=>oldNative.height(x,z)),candidateHalfOpenContains:candidateSampler.contains(x,z),retainedHalfOpenContains:oldSampler.contains(x,z),candidateGridCoordinate:candidateSampler.grid(x,z),retainedGridCoordinate:oldSampler.grid(x,z),sourceVertexY:y,sourceVertexNeedNotEqualNativeMaximum:true,canonicalVertexToParentGuardSeparateAndUnchanged:true,noGeometryOrGridChanges:true};});
verifyModuleClosure(closure,root);for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const output=new URL(doc+'/all860-actual-production-sampler-context.json.gz',root);assert(!existsSync(output));await writeExactJsonGzip(output,{rows,completeProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,noRendererRayAllPairsSourceDecodeOrGeometryEdits:true,notContinuousSeamOrPhysicalAcceptance:true,physicalAccepted:false,installationApproved:false});
console.log(JSON.stringify({savedEdgeOccurrences:rows.length,noAcceptance:true,noGeometryChanges:true}));
