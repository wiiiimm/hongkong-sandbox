/** Compare the actual production adapter with immutable original render inputs. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as production from '../../../3d-viewer/city/building-geometry.js';
import * as core from '../../../3d-viewer/city/building-geometry-core.js';
import * as prototype from '../../../3d-viewer/city/source-bound-basic-geometry-private.js';
import {officialModelFootprint} from '../../../3d-viewer/city/official-model-footprint-scopes.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[inputPath,outputPath]=process.argv.slice(2),sha=b=>createHash('sha256').update(b).digest('hex'),raw=p=>readFileSync(new URL(p,root));
const read=p=>{const b=raw(p);return JSON.parse(b[0]===31&&b[1]===139?gunzipSync(b):b);};
const input=read(inputPath);for(const [path,hash]of Object.entries(input.inputHashes))assert.equal(sha(raw(path)),hash,path);
assert.equal(sha(raw('3d-viewer/city/building-geometry-core.js')),'f3336a37c5164a78c931c702ad2ca5f62ed872adab9513787d3f8517fb3bdd4e');
const current=raw('3d-viewer/city/building-geometry.js').toString(),shadow=raw(input.oldPrivateShadow).toString();
assert.equal(current.slice(current.indexOf('import *')),shadow.slice(shadow.indexOf('import *')).replaceAll('building-geometry-original-private.js','building-geometry-core.js'));
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const basic=read(input.basics),runtime=read(input.runtime),selection=read(input.selection),proposal=read(input.proposal),forms=new Map(basic.rows.map(r=>[r.uid,r.currentBuilding]));
assert.equal(forms.size,70);assert.equal(runtime.rows.length,7);const legacy=[],native=[],hinted=[];
const equal=(a,b)=>{assert.deepEqual(Object.keys(a.attributes),Object.keys(b.attributes));for(const key of Object.keys(a.attributes))assert.deepEqual(a.attributes[key].array,b.attributes[key].array,key);assert.deepEqual(a.index?.array,b.index?.array);};
for(const row of basic.rows){
 const a=production.createBuildingGeometry(row.currentBuilding),b=core.createBuildingGeometry(row.currentBuilding);equal(a,b);assert.deepEqual(Array.from(a.attributes.position.array),row.position);assert.deepEqual(a.index?Array.from(a.index.array):Array.from({length:a.attributes.position.count},(_,i)=>i),row.index);legacy.push({uid:row.uid,originalAttributesUnchanged:true,originalCapturedPositionAndIndexUnchanged:true});a.dispose();b.dispose();
}
for(const row of runtime.rows){
 const source=selection.rows.find(r=>r.uid===row.uid);assert(source&&source.sourceSHA256===row.sourceSHA256);const before=source.source.building;
 const hint=proposal.rows.find(r=>r.uid===row.uid)?.hint,building=hint?{...before,nativeFallbackGround:hint}:before;
 const entry=source.candidate.entry,footprintBoundary=officialModelFootprint(entry,building,uid=>forms.get(uid)),modelGeometry={position:row.position,index:row.index,...(footprintBoundary?{footprintBoundary}:{})},record={...building,modelGeometry};
 const a=production.createBuildingGeometry(record),b=core.createBuildingGeometry(record);assert.equal(production.describeBuilding(record).modelStatus,'usable');assert(!production.describeBuilding(record).sourceBoundBasicContinuation);equal(a,b);native.push({uid:row.uid,sourceSHA256:row.sourceSHA256,actualSourceVertices:row.position.length/3,allNativeAttributesUnchanged:true,basicContinuationApplied:false});a.dispose();b.dispose();
}
for(const row of proposal.rows){
 const a=production.createBuildingGeometry(row.proposedBuilding),b=prototype.createBuildingGeometry(row.proposedBuilding),old=core.createBuildingGeometry(row.originalBuilding);equal(a,b);for(const [key,attr]of Object.entries(old.attributes))assert.deepEqual(a.attributes[key].array.slice(0,attr.array.length),attr.array);assert.deepEqual(production.collisionVolumes(row.proposedBuilding),prototype.collisionVolumes(row.proposedBuilding));hinted.push({uid:row.uid,allProductionAttributesEqualBrowserTestedPrototype:true,originalCoreAttributesUnchanged:true,visualAndCollisionDescriptionsEqual:true});for(const g of[a,b,old])g.dispose();
}
assert(verifyModuleClosure(closure,root));for(const [path,hash]of Object.entries(input.inputHashes))assert.equal(sha(raw(path)),hash,path);
const inputHashes={...input.inputHashes,...closure.inputHashes,[inputPath]:sha(raw(inputPath)),'3d-viewer/city/source-bound-basic-geometry-private.js':sha(raw('3d-viewer/city/source-bound-basic-geometry-private.js')),'source-scripts/city/government-import/source_bound_production_geometry_equivalence_v1_20261029.mjs':sha(raw('source-scripts/city/government-import/source_bound_production_geometry_equivalence_v1_20261029.mjs'))};
writeFileSync(new URL(outputPath,root),JSON.stringify({uids:selection.rows.map(r=>r.uid),legacy,native,hinted,inputHashes,unchangedLegacyForms:70,unchangedOriginalModels:7,equivalentBasicContinuations:3,originalCorePreservedByteForByte:true,productionAdapterEqualsPrivateShadow:true,sourceGeometryChanges:0,publication:false,installationApproved:false,qualification:'Actual production adapter compared with70complete frozen BASIC render meshes,7actual native geometry arrays and3browser-tested private continuation outputs. All vertex attributes and indices equal; original core bytes preserved. Native source coordinates/poses unchanged. No runtime/browser/publication acceptance follows solely from this equivalence.'},null,2)+'\n');
console.log(JSON.stringify({unchangedLegacyForms:legacy.length,unchangedOriginalModels:native.length,equivalentBasicContinuations:hinted.length}));
