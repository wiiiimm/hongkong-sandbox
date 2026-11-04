/** UNEXECUTED private grid/actual-draw/sampler replay. No publication. */
import {readFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],nomDoc=process.argv[3],hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function raw(p){const b=readFileSync(new URL(p,root)),h=sha(b);if(hashes[p])assert.equal(hashes[p],h,p);hashes[p]=h;return b;}
function read(p){const b=raw(p);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz'),nom=read(nomDoc+'/private-source-family-subdivision-nomination.json.gz');
assert.equal(nom.candidateRawPositionTriplets.length,11577);assert.equal(nom.completeOldNewIndexMapping.length,11575);assert.equal(nom.protectedWholeCurrentTripletsUnchanged.length,68);
assert.equal(nom.computedCurrentRing12PreviousCandidateMapping.length,11576);assert.deepEqual(nom.computedCurrentRing12PreviousCandidateMapping[1159].newCandidateFaces,[1159,1160]);assert(nom.allFreshActualDrawAndFullActorRuntimeAcceptancePending&&!nom.physicalAccepted&&!nom.installationApproved);
const current='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';assert.equal(input.currentManifest.sha256,current);
for(const [p,h]of [['source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579'],['source-scripts/city/government-import/dependency-closure-vendor/acorn-8.8.1/acorn.mjs','a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55'],['source-scripts/city/government-import/exact_incremental_json_gzip_v1_20261012.mjs','e5cfacfaf2361a0ce4444ee02f082a1341d8aa033ce8da432ff34b56d13ee6d9']])assert.equal(sha(raw(p)),h,p);
const closure=snapshotModuleClosure(import.meta.url,root);
assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
for(const [p,h]of Object.entries(closure.inputHashes))assert.equal(sha(raw(p)),h,p);
const {makeTerrain}=await import('../../../3d-viewer/city/world.js');
const {makeTerrainSampler}=await import('../../../3d-viewer/city/geo.js');
const {guardSamples,bits}=await import('./upton_six_basic_guard_samples_v1_20261012.mjs');
const {nativeTerrainSurface}=await import('../../../3d-viewer/city/native-terrain.js?v=20261010-finite1');
const {withinFiniteTriangleProjection}=await import('../../../3d-viewer/city/exact-finite-triangle-projection.js');
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],current);
for(const pin of input.allCurrentInputRefs)assert.equal(sha(raw(pin.path)),pin.sha256,pin.path);
const base=read('3d-viewer/city/data/terrain.json');
const patches=manifest.terrainPatches.map(e=>({entry:e,path:'3d-viewer/'+e.url,data:read('3d-viewer/'+e.url)}));
const at=patches.findIndex(p=>p.path===input.retainedParent.path);assert(at>=0);assert.equal(patches.filter(p=>p.path===input.retainedParent.path).length,1);assert.equal(sha(raw(patches[at].path)),input.retainedParent.sha256);
const old=patches[at].data,candidate=structuredClone(old),g=old.meta.georef,d=input.domain;
assert.deepEqual(input.coarseCells,[457,449,460,451]);assert.deepEqual(old.coarseCells,[457,449,459,451]);assert.deepEqual(d,[-2477.5,-37.5,-2267.5,102.5]);
assert.equal(g.bE-834500,d[0]);assert.equal(816500-g.bN,d[1]);assert.equal(g.aE,5);assert.equal(g.aN,-5);assert.equal(old.w,29);assert.equal(old.h,29);
candidate.w=(d[2]-d[0])/g.aE+1;candidate.h=(d[3]-d[1])/(-g.aN)+1;assert.equal(candidate.w,43);assert.equal(candidate.h,29);candidate.coarseCells=input.coarseCells;
const beforeData={...base,patches:patches.map(p=>p.data)},beforeSampler=makeTerrainSampler(beforeData);
const grids={elev:[],renderedElev:[],vegetation:[]},gridRows=[];
assert.equal(old.elev.length,old.w*old.h);assert.equal(old.renderedElev.length,old.w*old.h);assert.equal(old.vegetation.length,old.w*old.h);
for(let r=0;r<candidate.h;r++)for(let c=0;c<candidate.w;c++){
 const x=g.bE+c*g.aE-834500,z=816500-(g.bN+r*g.aN),retained=c<old.w&&r<old.h;
 if(retained){const k=r*old.w+c;for(const key of Object.keys(grids))grids[key].push(old[key][k]);gridRows.push({row:r,column:c,oldNode:k,newNode:r*candidate.w+c,exactNodeSameXZ:true,allThreeValuesByteSemanticsUnchanged:true});}
 else {grids.elev.push(beforeSampler.raw(x,z));grids.renderedElev.push(beforeSampler.height(x,z));const bg=base.meta.georef,bc=Math.max(0,Math.min(base.w-1,Math.round((x+834500-bg.bE)/bg.aE))),br=Math.max(0,Math.min(base.h-1,Math.round((816500-z-bg.bN)/bg.aN)));grids.vegetation.push(base.vegetation[br*base.w+bc]);gridRows.push({row:r,column:c,baseVegetationNode:br*base.w+bc,convention:'JS Math.round then clamp; current sampler raw/rendered for new nodes'});}
}
for(const [k,v]of Object.entries(grids)){assert(v.length===candidate.w*candidate.h&&v.every(Number.isFinite));candidate[k]=v;}
const pos=[],index=[];for(const face of nom.candidateRawPositionTriplets){assert.equal(face.length,3);for(const p of face){assert.equal(p.length,3);assert(p.every(Number.isFinite));const i=pos.length/3;for(const v of p){pos.push(v);}index.push(i);}}
candidate.id='government-native-upton-current-ring12-exact-subdivision-private-nomination';
candidate.nativeMesh={position:pos,index,source:{kind:'separately labelled exact current-ring12 hanging-node subdivision on saved source35676 original-TIN/current-ring/mask join nomination',originalTINSource:'11-SW-7A',preservedOriginalTripletsReference:nomDoc+'/private-source-family-subdivision-nomination.json.gz',computedFragmentsAndVerticalJoinsAreNotUntouchedGovernmentGeometry:true,noNativeReacceptance:true,noNewCoverageOrOverlapApproval:true}};
// Old sourceOverlap/numerical fallback approvals apply to old geometry only.
assert(!candidate.nativeMesh.sourceOverlap&&!candidate.nativeMesh.source.numericalCoverageGap);
assert.deepEqual(candidate.meta.targetUids,old.meta.targetUids);assert.deepEqual(candidate.meta.georef,old.meta.georef);
const afterPatches=patches.map((p,i)=>i===at?candidate:p.data),afterData={...base,patches:afterPatches};
function touches(t){const xs=[t[0],t[3],t[6]],zs=[t[2],t[5],t[8]];return !(Math.max(...xs)<d[0]||Math.min(...xs)>d[2]||Math.max(...zs)<d[1]||Math.min(...zs)>d[3]);}
const identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
function draw(data){const object=makeTerrain(data);object.updateMatrixWorld(true);const exterior=createHash('sha256'),rows=[];let total=0,outside=0,meshCount=0;object.traverse(m=>{if(!m.isMesh)return;meshCount++;assert.deepEqual(m.matrixWorld.elements,identity);const a=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??a.count;assert.equal(n%3,0);for(let i=0;i<n;i+=3){const t=[];for(let j=0;j<3;j++){const k=ix?ix.getX(i+j):i+j;t.push(a.getX(k),a.getY(k),a.getZ(k));}assert(t.every(Number.isFinite));total++;if(touches(t))rows.push(t);else{const bytes=Buffer.allocUnsafe(72);for(let k=0;k<9;k++)bytes.writeDoubleLE(t[k],k*8);exterior.update(bytes);outside++;}}});object.traverse(m=>{m.geometry?.dispose();for(const v of [].concat(m.material||[]))v?.dispose();});return {total,outside,meshCount,exteriorOrderedBinary64SHA256:exterior.digest('hex'),closedDomainDrawnTriplets:rows};}
const before=draw(beforeData),after=draw(afterData);assert.equal(before.exteriorOrderedBinary64SHA256,after.exteriorOrderedBinary64SHA256);assert.equal(before.outside,after.outside);
assert.equal(before.closedDomainDrawnTriplets.length,9214);
const afterSampler=makeTerrainSampler(afterData),sampler=[];
for(let r=0;r<candidate.h;r++)for(let c=0;c<candidate.w;c++){
 const x=g.bE+c*g.aE-834500,z=816500-(g.bN+r*g.aN);let error=null,rawValue=null,height=null;try{rawValue=afterSampler.raw(x,z);height=afterSampler.height(x,z);assert(Number.isFinite(rawValue)&&Number.isFinite(height));}catch(e){error=String(e);}sampler.push({row:r,column:c,x,z,rawValue,height,error,sampledOnlyNotCompleteCoverageProof:true});
}
// Save the identical nominee and actual draw BEFORE any candidate guard can throw.
const output=doc+'/private-native-terrain-candidate.json.gz';assert(!existsSync(new URL(output,root)));
await writeExactJsonGzip(new URL(output,root),candidate);
await writeExactJsonGzip(new URL(doc+'/actual-production-draw-before-guards.json.gz',root),{currentManifestSHA256:current,inputHashes:hashes,before,after,gridNodeMapping:gridRows,completeOldGridNodeCount:old.w*old.h,actualCandidateSamplerGridFindings:sampler,drawRecordedBeforeCandidateGuards:true,noProductionGeometryChanges:true,notCompletedGuardOrPhysicalApproval:true});
function gridDetails(data,x,z){
 const g=data.meta.georef,c=(x+834500-g.bE)/g.aE,r=(816500-z-g.bN)/g.aN,cc=Math.max(0,Math.min(data.w-1,c)),rr=Math.max(0,Math.min(data.h-1,r)),i=Math.min(data.w-2,Math.floor(cc)),j=Math.min(data.h-2,Math.floor(rr));
 return {georef:g,w:data.w,h:data.h,unclampedColumnRow:[c,r],contains:c>=0&&r>=0&&c<data.w-1&&r<data.h-1,clampedColumnRow:[cc,rr],cellColumnRow:[i,j],rawGridCellNodes:[j*data.w+i,j*data.w+i+1,(j+1)*data.w+i,(j+1)*data.w+i+1].map(k=>({index:k,elev:data.elev[k],renderedElev:data.renderedElev?.[k]})),nativeFallbackPolicy:data.nativeMesh?.source?.numericalCoverageGap?.policy??null};
}
function meshCoverage(mesh,x,z){
 const native=nativeTerrainSurface(mesh),pos=native.position,ix=native.index,rows=[];let determinantSkipped=0;const bin=[Math.floor(x/20),Math.floor(z/20)];
 for(let face=0;face<ix.length/3;face++){
  const a=ix[3*face]*3,b=ix[3*face+1]*3,c=ix[3*face+2]*3,t=[[pos[a],pos[a+1],pos[a+2]],[pos[b],pos[b+1],pos[b+2]],[pos[c],pos[c+1],pos[c+2]]],xs=t.map(p=>p[0]),zs=t.map(p=>p[2]);
  const determinant=(pos[b+2]-pos[c+2])*(pos[a]-pos[c])+(pos[c]-pos[b])*(pos[a+2]-pos[c+2]),indexed=Math.abs(determinant)>=1e-10;
  if(!indexed)determinantSkipped++;
  if(x<Math.min(...xs)||x>Math.max(...xs)||z<Math.min(...zs)||z>Math.max(...zs))continue;
  const finiteProjectionContains=withinFiniteTriangleProjection([pos[a],pos[a+2]],[pos[b],pos[b+2]],[pos[c],pos[c+2]],[x,z]);
  rows.push({nativeMeshFace:face,actualFloat32Triplet:t,productionJSDeterminant:determinant,productionHeightIndexIncludesFacet:indexed,production20mBinCoversPoint:bin[0]>=Math.floor(Math.min(...xs)/20)&&bin[0]<=Math.floor(Math.max(...xs)/20)&&bin[1]>=Math.floor(Math.min(...zs)/20)&&bin[1]<=Math.floor(Math.max(...zs)/20),exactProductionFiniteProjectionContainsPoint:finiteProjectionContains});
 }
 return {completeMeshFacetCount:ix.length/3,completeUnusedPositionVertexCount:pos.length/3,productionIndexedNoncollapsedFacets:native.triangles,productionDeterminantSkippedFacets:determinantSkipped,productionBin:bin,allClosedAABBCandidateFacets:rows,actualNativeSurfaceHeight:native.height(x,z),allOmittedFacetsStrictClosedAABBOutside:true,noTerrainOrIndexChange:true};
}
function errorContext(x,z){
 const scene=patches=>patches.flatMap(p=>{const grid=gridDetails(p.data,x,z);return grid.contains?[{path:p.path,grid,nativeCoverage:p.data.nativeMesh?meshCoverage(p.data.nativeMesh,x,z):null}]:[];});
 const drawn=[];for(let face=0;face<after.closedDomainDrawnTriplets.length;face++){const f=after.closedDomainDrawnTriplets[face],xs=[f[0],f[3],f[6]],zs=[f[2],f[5],f[8]];if(x<Math.min(...xs)||x>Math.max(...xs)||z<Math.min(...zs)||z>Math.max(...zs))continue;drawn.push({closedDomainDrawnFace:face,actualTriplet:f,exactProductionFiniteProjectionContainsPoint:withinFiniteTriangleProjection([f[0],f[2]],[f[3],f[5]],[f[6],f[8]],[x,z])});}
 return {point:[x,z],pointBitsHex:[bits(x),bits(z)],baselineCoveringParentPatches:scene(patches),candidateCoveringParentPatches:scene(patches.map((p,i)=>i===at?{...p,data:candidate}:p)),allActualClosedDomainDrawnAABBCandidateFacets:drawn,allOmittedClosedDomainDrawnFacetsStrictAABBOutside:true,drawnCoverageDoesNotWaiveSamplerFailure:true};
}
const saved=read(input.exactOldGuardSamples.path);assert.equal(hashes[input.exactOldGuardSamples.path],input.exactOldGuardSamples.sha256);
const protectionGuards=[],allSamplerErrors=[];
for(const prior of saved.rows){
 const b=prior.exactCurrentForm,samples=guardSamples(b);assert.deepEqual(samples,prior.sampleSemantics);
 const rows=samples.points.map(([x,z],i)=>{
  const oldHeight=beforeSampler.height(x,z);assert.equal(bits(oldHeight),prior.rows[i].currentHeightBitsHex);
  try{const newHeight=afterSampler.height(x,z);return {sample:i,point:[x,z],beforeHeight:oldHeight,afterHeight:newHeight,afterGap:b.base+(b.minimum||0)-newHeight,samplerError:null};}
  catch(e){const failure={uid:prior.uid,sample:i,point:[x,z],pointBitsHex:[bits(x),bits(z)],error:String(e),coverage:errorContext(x,z),noFallbackInfillOrAcceptanceCredit:true};allSamplerErrors.push(failure);return {sample:i,point:[x,z],beforeHeight:oldHeight,afterHeight:null,afterGap:null,samplerError:String(e)};}
 });
 const errors=rows.filter(q=>q.samplerError),oldGap=rows.map(q=>b.base+(b.minimum||0)-q.beforeHeight),newGap=rows.filter(q=>!q.samplerError).map(q=>q.afterGap),oldTop=rows.map(q=>q.beforeHeight),newTop=rows.filter(q=>!q.samplerError).map(q=>q.afterHeight);
 // A real throwing sample prevents guard PASS. Partial finite ranges are descriptive only.
 const upperGapPassed=errors.length?null:Math.max(...newGap)<=Math.max(1,Math.max(...oldGap))+.25;
 const burialPassed=errors.length?null:Math.min(...newGap)>=Math.min(-.5,Math.min(...oldGap))-.25;
 const roofPassed=errors.length?null:Math.max(...newTop)<=Math.max(b.base+b.height-.1,Math.max(...oldTop))+.25;
 protectionGuards.push({uid:prior.uid,exactCurrentForm:b,rows,samplerErrorCount:errors.length,upperGapPassed,burialPassed,roofPassed,passed:!errors.length&&upperGapPassed&&burialPassed&&roofPassed,existingPredicatesUnchanged:true,notContinuousCoverageOrWholeForeignApproval:true});
}
assert.equal(protectionGuards.length,6);assert.equal(protectionGuards.reduce((s,r)=>s+r.rows.length,0),516);
await writeExactJsonGzip(new URL(doc+'/six-existing-production-protection-guards.json.gz',root),{rows:protectionGuards,allSamplerErrors,allPassed:protectionGuards.every(q=>q.passed),noToleranceChanges:true,noSamplerErrorWaiver:true});
verifyModuleClosure(closure,root);for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
await writeExactJsonGzip(new URL(doc+'/actual-production-replay.json.gz',root),{currentManifestSHA256:current,completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,actualCandidateWrittenBeforeGuards:true,completeSamplerErrors:allSamplerErrors,noSamplerErrorWaiver:true,before,after,gridNodeMapping:gridRows,completeOldGridNodeCount:old.w*old.h,actualCandidateSamplerGridFindings:sampler,completeSamplerProof:false,actualPOSITIONCastIsFloat32:true,untouchedRawTripletsDoNotImplyBinary64EqualsShaderPositions:true,currentExteriorXYZOrderedHashMatched:true,currentExteriorSamplerInputsUnchanged:true,globalWatertightTopologyNotRequired:true,verticalFacetsNotHeightIndexedByRuntime:true,actualNativeHeightIndexProjectedDeterminantThreshold:1e-10,sourceCurrentExteriorNormalAndColourByteEqualityNotClaimed:true,sourcePositionChanges:0,sourcePoseChanges:0,liveTerrainChanges:0,physicalAccepted:false,installationApproved:false});
console.log(JSON.stringify({candidateFaces:index.length/3,currentFaces:before.closedDomainDrawnTriplets.length,proposedFaces:after.closedDomainDrawnTriplets.length,exteriorXYZMatched:true,samplerGridErrors:sampler.filter(x=>x.error).length,guardSamplerErrors:allSamplerErrors.length,sixExistingGuardsPassed:protectionGuards.every(q=>q.passed),noAcceptance:true}));
