/** Private production terrain and complete BASIC streams; no official loader rerun. */
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
import {makeTerrain,makeBuildings} from '../../../3d-viewer/city/world.js';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/'));
function bytes(p,h){const u=new URL(p,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u),actual=sha(b);if(h!==undefined)assert.equal(actual,h,p);if(hashes[p])assert.equal(hashes[p],actual,p);hashes[p]=actual;return b;}
function read(p,h){const b=bytes(p,h);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz');assert.equal(input.schema,'heritage-parent-basic-production-capture-v1');
for(const q of input.allInputRefs)bytes(q.path,q.sha256);
const closure=snapshotModuleClosure(import.meta.url,root);for(const[p,h]of Object.entries(closure.inputHashes))bytes(p,h);
const manifest=read('3d-viewer/city/data/manifest.json',input.currentManifestSHA256),candidate=read(input.candidate.path,input.candidate.sha256);
assert.equal(candidate.nativeMesh.index.length/3,8341);assert.deepEqual(candidate.coarseCells,[528,306,532,309]);
const forms=input.currentForms.map(r=>r.building);assert.equal(forms.length,23);assert.equal(new Set(forms.map(b=>b.uid)).size,23);assert(forms.some(b=>b.uid===input.ownedUID));assert(input.currentForms.every(r=>r.existingNative===false));
const rows=[],identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],roi=[...input.parentDomain],vector=new THREE.Vector3();
function extend(values){for(let i=0;i<values.length;i+=3){roi[0]=Math.min(roi[0],values[i]);roi[1]=Math.min(roi[1],values[i+2]);roi[2]=Math.max(roi[2],values[i]);roi[3]=Math.max(roi[3],values[i+2]);}}
// Source four-world unused bounds extend ROI; their saved arrays remain separate inputs.
for(const b of input.ownedFourWorldUnusedBounds){extend(b[0]);extend(b[1]);}
for(const building of forms){const built=await makeBuildings([building],null,{worker:false,yield:false});built.group.updateMatrixWorld(true);const meshes=[];let faces=0;
 try{built.group.traverse(m=>{if(!m.isMesh)return;assert.deepEqual(m.matrixWorld.elements,identity);const p=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??p.count;assert(p.array instanceof Float32Array&&n%3===0);const literal=[],index=[];for(let i=0;i<p.count;i++){vector.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);literal.push(...vector.toArray());}for(let i=0;i<n;i++)index.push(ix?ix.getX(i):i);const ar=actualFloat32ModelMatrixPositions(p.array,m.matrixWorld.elements);const streams={constructorFloat32World:literal,leftFloat32World:ar.leftAssociatedPerMultiplyAddFloat32WorldPosition,balancedFloat32World:ar.balancedPerMultiplyAddFloat32WorldPosition};for(const values of Object.values(streams)){assert(values.every(Number.isFinite));extend(values);}meshes.push({positionAttributeFloat32:Array.from(p.array),positionAttributeSHA256:sha(Buffer.from(p.array.buffer,p.array.byteOffset,p.array.byteLength)),index,completePositionVerticesIncludingUnused:p.count,completeIndexedFaces:n/3,matrixWorldFloat64:Array.from(m.matrixWorld.elements),modelMatrixUniformFloat32:ar.modelMatrixUniformFloat32,streams});faces+=n/3;});assert(faces>0);rows.push({uid:building.uid,building,meshes,completeFaces:faces,beforeAfterBASICGeometryUnchanged:true});}
 finally{built.group.traverse(m=>m.geometry?.dispose());for(const m of built.materials)m.dispose();}
}
await writeExactJsonGzip(new URL(doc+'/complete23-current-basic-constructor-streams.json.gz',root),{rows,completeActorROI:roi,allSourceFormsRetained:true,completeUnusedPositionsRetained:true,explicitTwoFloat32OrdersNotUniversalGPUClaim:true,noBuildingGeometryChanges:true});
const base=read('3d-viewer/city/data/terrain.json'),patches=manifest.terrainPatches.map(q=>read('3d-viewer/'+q.url));assert(!patches.some(p=>p.id===candidate.id));
const outside=(t,d)=>Math.max(t[0],t[3],t[6])<d[0]||Math.min(t[0],t[3],t[6])>d[2]||Math.max(t[2],t[5],t[8])<d[1]||Math.min(t[2],t[5],t[8])>d[3];
function draw(data){const o=makeTerrain(data),selected=[];let total=0,roiOutside=0,parentOutside=0;const rh=createHash('sha256'),ph=createHash('sha256');o.updateMatrixWorld(true);
 try{o.traverse(m=>{if(!m.isMesh)return;assert.deepEqual(m.matrixWorld.elements,identity);const p=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??p.count;assert.equal(n%3,0);for(let i=0;i<n;i+=3){const t=[];for(let j=0;j<3;j++){const k=ix?ix.getX(i+j):i+j;t.push(p.getX(k),p.getY(k),p.getZ(k));}assert(t.every(Number.isFinite));total++;const buf=Buffer.allocUnsafe(72);for(let k=0;k<9;k++)buf.writeDoubleLE(t[k],k*8);if(outside(t,input.parentDomain)){ph.update(buf);parentOutside++;}if(outside(t,roi)){rh.update(buf);roiOutside++;}else selected.push(t);}});}
 finally{o.traverse(m=>{m.geometry?.dispose();for(const v of[].concat(m.material||[]))v?.dispose();});}
 return{completeDrawnFacets:total,completeRelevantDrawnTriplets:selected,completeActorROI:roi,parentDomain:input.parentDomain,strictOutsideParentFacets:parentOutside,strictOutsideParentOrderedSHA256:ph.digest('hex'),strictOutsideROIFacets:roiOutside,strictOutsideROIOrderedSHA256:rh.digest('hex')};}
const before=draw({...base,patches});await writeExactJsonGzip(new URL(doc+'/complete-before-ground.json.gz',root),before);
const after=draw({...base,patches:[...patches,candidate]});await writeExactJsonGzip(new URL(doc+'/complete-candidate-ground.json.gz',root),after);
const exteriorFields=['strictOutsideParentFacets','strictOutsideParentOrderedSHA256','strictOutsideROIFacets','strictOutsideROIOrderedSHA256'];const mismatched=exteriorFields.filter(k=>before[k]!==after[k]);
verifyModuleClosure(closure,root);for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
await writeExactJsonGzip(new URL(doc+'/actual-production-capture-report.json.gz',root),{beforeFacets:before.completeRelevantDrawnTriplets.length,afterFacets:after.completeRelevantDrawnTriplets.length,completeCurrentBASICActors:rows.length,completeActorROI:roi,completeParentDomain:input.parentDomain,exteriorEqualityFields:exteriorFields,exteriorMismatches:mismatched,strictOutsideParentAndActorROIDrawUnchanged:mismatched.length===0,inputHashes:hashes,completeRecursiveProductionModuleClosure:closure,startEndAllInputsVerified:true,noOfficialModelDecodeLoaderFoundationOrIdentityRerun:true,noSourceGeometryOrTerrainModification:true,physicalAccepted:false,installationApproved:false});
assert.equal(mismatched.length,0,'Actual exterior draw changed; no native outside reuse permitted');console.log(JSON.stringify({basicActors:rows.length,exteriorUnchanged:true,physicalAccepted:false}));
