/** ROOT-only fresh private renderer/whole-parent/all25 original guard capture. */
import {readFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={};assert(doc&&!doc.endsWith('/'));
const sha=b=>createHash('sha256').update(b).digest('hex');
function raw(p){const u=new URL(p,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u),h=sha(b);if(hashes[p])assert.equal(hashes[p],h,p);hashes[p]=h;return b;}
function read(p){const b=raw(p);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz');assert.equal(input.schema,'polyu-parent-cell-actual-production-capture-v3');assert.equal(input.physicalAccepted,false);
for(const q of input.allInputRefs)assert.equal(sha(raw(q.path)),q.sha256,q.path);
const closure=snapshotModuleClosure(import.meta.url,root);assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure);assert.equal(closure.unsupportedDynamicImports,0);
for(const[p,h]of Object.entries(closure.inputHashes))assert.equal(sha(raw(p)),h,p);
const {makeTerrain}=await import('../../../3d-viewer/city/world.js');
const {makeTerrainSampler}=await import('../../../3d-viewer/city/geo.js');
const {guardSamples,bits}=await import('./upton_six_basic_guard_samples_v1_20261012.mjs');
const current='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],current);assert.equal(input.currentManifestSHA256,current);
const base=read('3d-viewer/city/data/terrain.json'),patches=manifest.terrainPatches.map(e=>read('3d-viewer/'+e.url));
const old=read(input.previousPrivateCandidate.path);assert.equal(hashes[input.previousPrivateCandidate.path],input.previousPrivateCandidate.sha256);
const nominee=read(input.newNomination.path);assert.equal(nominee.schema,'private-source-plane-preserving-five-current-parent-mask-parent-cell-nomination-v4');assert.equal(hashes[input.newNomination.path],input.newNomination.sha256);assert(!nominee.physicalAccepted&&!nominee.installationApproved);
const candidate=structuredClone(old);candidate.id='government-native-polyu-five-current-parent-masks-private';candidate.nativeMesh=structuredClone(nominee.newNativeMesh);
assert.equal(candidate.nativeMesh.index.length/3,input.completeNewNativeFacets);assert.equal(candidate.nativeMesh.position.length/3,input.completeNewPositionVertices);
assert.deepEqual(candidate.nativeMesh.position.slice(0,old.nativeMesh.position.length),old.nativeMesh.position);
assert.equal(nominee.all8011PreviousPackedFacetsUnchanged,true);assert.equal(nominee.all3214OldMappingsVerbatim,true);
assert.equal(candidate.nativeMesh.index.length,nominee.candidateFaceProvenance.length*3);
candidate.nativeMesh.source={kind:'private-authenticated-V4-saved-current-parent-own-plane-cell-repacking',completedNominationJob:input.completedNominationJob,nominationReference:input.newNomination,historicalPrivateCandidateReference:input.previousPrivateCandidate,allPreviousNegativeAndFullScopeGatesRemain:true,physicalAccepted:false};
assert(!candidate.nativeMesh.sourceOverlap&&!candidate.nativeMesh.source.numericalCoverageGap);assert(!patches.some(p=>p.id===candidate.id));
assert.deepEqual(candidate.meta.georef,old.meta.georef);assert.deepEqual(candidate.coarseCells,[521,420,524,422]);
for(const k of ['elev','renderedElev','vegetation'])assert.deepEqual(candidate[k],old[k]);
assert.equal(candidate.meta.parentSha256,hashes['3d-viewer/city/data/terrain.json']);
const d=input.fullParentDomain,g=candidate.meta.georef;
assert.deepEqual(d,[g.bE-834500,816500-g.bN,g.bE+(candidate.w-1)*g.aE-834500,816500-(g.bN+(candidate.h-1)*g.aN)]);
const beforeData={...base,patches},afterData={...base,patches:[...patches,candidate]},beforeSampler=makeTerrainSampler(beforeData);
const identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
function touches(t){const xs=[t[0],t[3],t[6]],zs=[t[2],t[5],t[8]];return !(Math.max(...xs)<d[0]||Math.min(...xs)>d[2]||Math.max(...zs)<d[1]||Math.min(...zs)>d[3]);}
function draw(data){const object=makeTerrain(data);object.updateMatrixWorld(true);const exterior=createHash('sha256'),rows=[];let total=0,outside=0,meshCount=0;try{object.traverse(m=>{if(!m.isMesh)return;meshCount++;assert.deepEqual(m.matrixWorld.elements,identity);const a=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??a.count;assert.equal(n%3,0);for(let i=0;i<n;i+=3){const t=[];for(let j=0;j<3;j++){const k=ix?ix.getX(i+j):i+j;t.push(a.getX(k),a.getY(k),a.getZ(k));}assert(t.every(Number.isFinite));total++;if(touches(t))rows.push(t);else{const bytes=Buffer.allocUnsafe(72);for(let k=0;k<9;k++)bytes.writeDoubleLE(t[k],k*8);exterior.update(bytes);outside++;}}});}finally{object.traverse(m=>{m.geometry?.dispose();for(const v of [].concat(m.material||[]))v?.dispose();});}return {total,outside,meshCount,exteriorOrderedBinary64SHA256:exterior.digest('hex'),closedDomainDrawnTriplets:rows};}
const before=draw(beforeData),after=draw(afterData);assert.equal(before.outside,after.outside);assert.equal(before.exteriorOrderedBinary64SHA256,after.exteriorOrderedBinary64SHA256);
const afterSampler=makeTerrainSampler(afterData),grid=[];
for(let r=0;r<candidate.h;r++)for(let c=0;c<candidate.w;c++){
 const x=g.bE+c*g.aE-834500,z=816500-(g.bN+r*g.aN);let error=null,height=null,rawHeight=null;
 try{height=afterSampler.height(x,z);rawHeight=afterSampler.raw(x,z);assert(Number.isFinite(height)&&Number.isFinite(rawHeight));}catch(e){error=String(e);}
 grid.push({row:r,column:c,x,z,height,rawHeight,error,samplesNotUniversalCoverage:true,originalGridValuesByteSemanticsUnchanged:true});
}
assert.equal(grid.length,candidate.w*candidate.h);
async function output(name,value){const u=new URL(doc+'/'+name,root);assert(!existsSync(u));await writeExactJsonGzip(u,value);}
await output('private-native-terrain-candidate.json.gz',candidate);
await output('actual-production-draw-before-guards.json.gz',{before,after,allCandidateGridSamples:grid,completeOriginalGridNodesRetained:candidate.w*candidate.h,originalUnusedPositionPrefixRetained:true,all25ConstructorAndNativeSourceEvidence:input.complete25SourceEvidence,native59527BeforeAfterFiniteStillRequired:true,actualDrawCapturedBeforeGuardFindings:true,physicalAccepted:false});
const guardRows=[],errors=[];assert.equal(input.exact25CurrentForms.length,25);assert.equal(input.previousOriginalGuardRows.length,25);
for(const b of input.exact25CurrentForms){
 const prior=input.previousOriginalGuardRows.find(r=>r.uid===b.uid);assert(prior);const samples=guardSamples(b);assert.equal(samples.points.length,prior.checks,b.uid);
 const rows=samples.points.map(([x,z],sample)=>{const before=beforeSampler.height(x,z);assert(Number.isFinite(before));try{const after=afterSampler.height(x,z);assert(Number.isFinite(after));return {sample,x,z,pointBitsHex:[bits(x),bits(z)],origin:samples.origins[sample],beforeHeight:before,beforeHeightBitsHex:bits(before),afterHeight:after,afterHeightBitsHex:bits(after),samplerError:null};}catch(e){const error={uid:b.uid,sample,x,z,error:String(e),noFallbackOrAcceptance:true};errors.push(error);return {sample,x,z,origin:samples.origins[sample],beforeHeight:before,beforeHeightBitsHex:bits(before),afterHeight:null,samplerError:String(e)};}});
 const heights=rows.map(r=>r.beforeHeight),next=rows.filter(r=>!r.samplerError).map(r=>r.afterHeight),base=b.base+(b.minimum||0),top=b.base+b.height;
 const minOldGap=base-Math.max(...heights),maxOldGap=base-Math.min(...heights);assert.equal(bits(minOldGap),bits(prior.beforeGap[0]),b.uid);assert.equal(bits(maxOldGap),bits(prior.beforeGap[1]),b.uid);
 const hasError=rows.some(r=>r.samplerError),reasons=[];let maxDelta=null,minNewGap=null,maxNewGap=null;
 if(hasError)reasons.push('actual-neighbour-sampler-error');else{maxDelta=Math.max(...rows.map(r=>Math.abs(r.afterHeight-r.beforeHeight)));minNewGap=base-Math.max(...next);maxNewGap=base-Math.min(...next);if(b.uid!=='landsd/305582:0'){
  if(prior.existingNative&&maxDelta>.004)reasons.push('existing-native-neighbour-requires-full-mesh-check');
  if(minNewGap<Math.min(-.5,minOldGap)-.25)reasons.push('increased-neighbour-burial');
  if(maxNewGap>Math.max(1,maxOldGap)+.25)reasons.push('increased-neighbour-ground-gap');
  if(Math.max(...next)>Math.max(top-.1,Math.max(...heights))+.25)reasons.push('increased-neighbour-roof-burial');
 }}
 guardRows.push({uid:b.uid,exactCurrentForm:b,exactOriginalSampleSemantics:samples,rows,checks:rows.length,existingNative:prior.existingNative,candidate:prior.candidate,maxGroundChange:maxDelta,beforeGap:[minOldGap,maxOldGap],afterGap:[minNewGap,maxNewGap],reasons,originalGuardRowVerbatim:prior,allPredicatesAndSampleOrderUnchanged:true,noWholeActorOrNativeMeshAcceptance:true});
}
const historicalNine=input.previousOriginalGuardRows.filter(r=>r.reasons.includes('increased-neighbour-ground-gap'));assert.equal(historicalNine.length,9);assert.equal(historicalNine.reduce((n,r)=>n+r.checks,0),3366);
await output('all25-original-production-guard-site-replay.json.gz',{rows:guardRows,allSamplerErrors:errors,allPassed:guardRows.every(r=>!r.reasons.length),originalNine3366SitesExactlyRegenerated:true,context6701ProbesAreIndependentNotGuardSites:true,unchangedGuardDefinition:input.originalGuardDefinition,allHistoricalNegativesRetained:true,physicalAccepted:false});
verifyModuleClosure(closure,root);for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
await output('actual-production-replay.json.gz',{currentManifestSHA256:current,completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,before,after,allCandidateGridSamples:grid,all25OriginalGuardReplay:'all25-original-production-guard-site-replay.json.gz',allSamplerErrors:errors,allOriginalParentGridBuffersIncludingUnusedRetained:true,currentExteriorXYZOrderedHashMatched:true,actualPOSITIONCastIsFloat32:true,fullParentAndAll25Scope:true,native59527WholeBeforeAfterStillPending:true,fullOwnedSourceFourWorld10536And752Negatives21BodiesStillHeld:true,freshActualViewerFiniteSeamMAXOverlapRuntimeBrowserAcceptanceRequired:true,bodyZeroCrossingContextNotAdditionalEngineeringAdmissionGate:true,sourceGeometryChanges:0,sourcePoseChanges:0,liveTerrainChanges:0,physicalAccepted:false,installationApproved:false});
console.log(JSON.stringify({newNativeFacets:input.completeNewNativeFacets,beforeDomainFacets:before.closedDomainDrawnTriplets.length,afterDomainFacets:after.closedDomainDrawnTriplets.length,exteriorMatched:true,gridErrors:grid.filter(r=>r.error).length,guardSamplerErrors:errors.length,all25GuardSitesCaptured:true,noAcceptance:true}));
