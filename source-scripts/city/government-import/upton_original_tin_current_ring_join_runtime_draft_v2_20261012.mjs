/** UNEXECUTED private grid/actual-draw/sampler replay. No publication. */
import {readFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function raw(p){const b=readFileSync(new URL(p,root)),h=sha(b);if(hashes[p])assert.equal(hashes[p],h,p);hashes[p]=h;return b;}
function read(p){const b=raw(p);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz'),nom=read(doc+'/geometry-nomination.json.gz');
const current='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540';assert.equal(input.currentManifest.sha256,current);
for(const [p,h]of [['source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579'],['source-scripts/city/government-import/dependency-closure-vendor/acorn-8.8.1/acorn.mjs','a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55'],['source-scripts/city/government-import/exact_incremental_json_gzip_v1_20261012.mjs','e5cfacfaf2361a0ce4444ee02f082a1341d8aa033ce8da432ff34b56d13ee6d9']])assert.equal(sha(raw(p)),h,p);
const closure=snapshotModuleClosure(import.meta.url,root);
assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
for(const [p,h]of Object.entries(closure.inputHashes))assert.equal(sha(raw(p)),h,p);
const {makeTerrain}=await import('../../../3d-viewer/city/world.js');
const {makeTerrainSampler}=await import('../../../3d-viewer/city/geo.js');
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
candidate.id='government-native-upton-original-current-ring-private-nomination';
candidate.nativeMesh={position:pos,index,source:{kind:'separately labelled scripted original-TIN/current-exterior join nomination',originalTINSource:'11-SW-7A',preservedOriginalTripletsReference:doc+'/complete-nominations-before-guards.json.gz',computedFragmentsAndVerticalJoinsAreNotUntouchedGovernmentGeometry:true,noNativeReacceptance:true,noNewCoverageOrOverlapApproval:true}};
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
verifyModuleClosure(closure,root);for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const output=doc+'/private-native-terrain-candidate.json.gz';assert(!existsSync(new URL(output,root))); // Adjacent evidence only, not a viewer path.
await writeExactJsonGzip(new URL(output,root),candidate);
await writeExactJsonGzip(new URL(doc+'/actual-production-replay.json.gz',root),{currentManifestSHA256:current,completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,before,after,gridNodeMapping:gridRows,completeOldGridNodeCount:old.w*old.h,actualCandidateSamplerGridFindings:sampler,completeSamplerProof:false,actualPOSITIONCastIsFloat32:true,untouchedRawTripletsDoNotImplyBinary64EqualsShaderPositions:true,currentExteriorXYZOrderedHashMatched:true,currentExteriorSamplerInputsUnchanged:true,globalWatertightTopologyNotRequired:true,verticalFacetsNotHeightIndexedByRuntime:true,actualNativeHeightIndexProjectedDeterminantThreshold:1e-10,sourceCurrentExteriorNormalAndColourByteEqualityNotClaimed:true,sourcePositionChanges:0,sourcePoseChanges:0,liveTerrainChanges:0,physicalAccepted:false,installationApproved:false});
console.log(JSON.stringify({candidateFaces:index.length/3,currentFaces:before.closedDomainDrawnTriplets.length,proposedFaces:after.closedDomainDrawnTriplets.length,exteriorXYZMatched:true,samplerGridErrors:sampler.filter(x=>x.error).length,noAcceptance:true}));
