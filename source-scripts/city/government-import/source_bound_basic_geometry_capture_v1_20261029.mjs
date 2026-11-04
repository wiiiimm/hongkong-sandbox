/** Real-source private adapter preservation proof; no viewer or asset writes. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {describeBuilding as baseline,createBuildingGeometry as oldGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {describeBuilding,createBuildingGeometry,collisionVolumes} from '../../../3d-viewer/city/source-bound-basic-geometry-private.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[proposalPath,runtimePath,outputPath]=process.argv.slice(2),hash=b=>createHash('sha256').update(b).digest('hex');
for(const path of [proposalPath,runtimePath,outputPath])assert(path&&!path.includes('..')&&(path.startsWith('docs/astra-city/government-import/')||path.startsWith('source-scripts/city/government-import/local/')));
const read=path=>{const raw=readFileSync(new URL(path,root));return JSON.parse(raw[0]===31&&raw[1]===139?gunzipSync(raw):raw);};
const packet=read(proposalPath),runtime=read(runtimePath),rows=[];
assert.equal(packet.privateProposalOnly,true);assert.equal(packet.publication,false);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/source-bound-basic-geometry-private.js',root),root);
assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
for(const row of packet.rows){
 const original=row.originalBuilding,b=row.proposedBuilding,raw=runtime.rows.find(r=>r.uid===row.uid);
 assert(raw&&raw.sourceSHA256===row.hint.sourceSHA256);const snapshot=JSON.stringify(b);
 const before=oldGeometry(original),after=createBuildingGeometry(b),description=describeBuilding(b),part=description.parts.at(-1);
 for(const [name,a]of Object.entries(before.attributes))assert.deepEqual(after.attributes[name].array.slice(0,a.array.length),a.array);
 assert.deepEqual(description.parts.slice(0,-1),baseline(original).parts);assert.deepEqual(collisionVolumes(b),description.parts);
 assert.equal(part.kind,'basic-ground-continuation');assert.equal(part.top,original.base+(original.minimum||0));assert.equal(part.bottom,row.hint.base);assert.equal(part.windows,false);
 const coreCount=before.attributes.position.count,position=after.attributes.position;
 const xz=new Set(original.rings.flat().map(([x,z])=>`${Math.fround(x)},${Math.fround(z)}`));
 for(let i=coreCount;i<position.count;i++){
  assert(xz.has(`${position.getX(i)},${position.getZ(i)}`));assert([Math.fround(part.top),Math.fround(part.bottom)].includes(position.getY(i)));
  assert.equal(after.attributes.cityWindows.getX(i),0);
 }
 const modelGeometry={position:raw.position,index:raw.index},native={...b,modelGeometry},nativeBefore=JSON.stringify(modelGeometry),nativeOld=oldGeometry(native),nativeNext=createBuildingGeometry(native);
 assert.equal(describeBuilding(native).modelStatus,'usable');assert(!describeBuilding(native).sourceBoundBasicContinuation);
 for(const name of Object.keys(nativeOld.attributes))assert.deepEqual(nativeNext.attributes[name].array,nativeOld.attributes[name].array);
 assert.equal(JSON.stringify(modelGeometry),nativeBefore);assert.equal(JSON.stringify(b),snapshot);
 rows.push({uid:row.uid,sourceSHA256:raw.sourceSHA256,base:original.base,top:original.base+original.height,continuationBottom:part.bottom,continuationTop:part.top,originalCoreVertices:coreCount,addedVertices:position.count-coreCount,actualOriginalSourceVertices:raw.position.length/3,actualNativeOutputVertices:nativeNext.attributes.position.count,allOriginalAttributesPreserved:true,nativeGeometryAttributesUnchanged:true,recordedHeightsUnchanged:true,addedXZUsesExistingFootprintOnly:true,addedWindows:false,visualAndCollisionDescriptionsAgree:true});
 for(const g of [before,after,nativeOld,nativeNext])g.dispose();
}
assert(verifyModuleClosure(closure,root));
const inputHashes={...closure.inputHashes};for(const p of [proposalPath,runtimePath,'source-scripts/city/government-import/source_bound_basic_geometry_capture_v1_20261029.mjs'])inputHashes[p]=hash(readFileSync(new URL(p,root)));
writeFileSync(new URL(outputPath,root),JSON.stringify({uids:rows.map(r=>r.uid),rows,inputHashes,privateProposalOnly:true,productionIntegration:false,wholeSceneCollisionAccepted:false,visualAcceptance:false,installationApproved:false,publication:false,qualification:'Actual original renderer arrays and existing BASIC core attributes are exactly retained. Only a private illustrative BASIC lower envelope is generated. Source/terrain identity is supplied by authenticated upstream receipts; no physical, scene collision, browser or publication acceptance follows.'},null,2)+'\n');
console.log(JSON.stringify({models:rows.length,allOriginalAttributesPreserved:true,nativeGeometryAttributesUnchanged:true}));
