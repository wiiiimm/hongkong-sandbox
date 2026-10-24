/** UNEXECUTED: 64 saved sites, actual MAX sampler and complete candidate ray. */
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function raw(path){const b=readFileSync(new URL(path,root)),h=sha(b);if(hashes[path])assert.equal(hashes[path],h,path);hashes[path]=h;return b;}
function read(path){const b=raw(path);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
for(const [p,h]of [['source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579'],['source-scripts/city/government-import/dependency-closure-vendor/acorn-8.8.1/acorn.mjs','a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55'],['source-scripts/city/government-import/exact_incremental_json_gzip_v1_20261012.mjs','e5cfacfaf2361a0ce4444ee02f082a1341d8aa033ce8da432ff34b56d13ee6d9']])assert.equal(sha(raw(p)),h,p);
const closure=snapshotModuleClosure(import.meta.url,root);assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
const THREE=await import('../../../3d-viewer/vendor/three.module.js');
const {nativeTerrainSurface}=await import('../../../3d-viewer/city/native-terrain.js');
const input=read(doc+'/input.json.gz');assert.equal(input.currentManifest.sha256,'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7');assert.equal(sha(raw(input.currentManifest.path)),input.currentManifest.sha256);
for(const pin of input.runtimeInputRefs)assert.equal(sha(raw(pin.path)),pin.sha256,pin.path);
const candidate=read(input.candidate.path);assert.equal(hashes[input.candidate.path],input.candidate.sha256);assert(!candidate.nativeMesh.sourceOverlap);
const saved=read(input.measuredOverlap.path);assert.equal(hashes[input.measuredOverlap.path],input.measuredOverlap.sha256);assert.equal(saved.measured.candidateGeometryCanonicalSHA256,input.geometryCanonicalSHA256);
const sites=saved.measured.float32HighestRayAgreement.rows;assert.equal(sites.length,64);assert.equal(saved.measured.float32HighestRayAgreement.samples,64);
const surface=nativeTerrainSurface(candidate.nativeMesh);assert.equal(candidate.nativeMesh.index.length/3,11576);
const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(surface.position,3));geometry.setIndex(candidate.nativeMesh.index);
const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.updateMatrixWorld(true);assert.deepEqual(mesh.matrixWorld.elements,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
let high=-Infinity;for(let i=1;i<surface.position.length;i+=3)high=Math.max(high,surface.position[i]);assert(Number.isFinite(high));
const rows=[];
for(let site=0;site<sites.length;site++){
 const savedSite=sites[site],{x,z}=savedSite;assert(Number.isFinite(x)&&Number.isFinite(z));
 const hits=new THREE.Raycaster(new THREE.Vector3(x,high+100,z),new THREE.Vector3(0,-1,0)).intersectObject(mesh);
 const sampled=surface.height(x,z),ray=hits.length?hits[0].point.y:null,error=sampled!==null&&ray!==null?Math.abs(sampled-ray):null;
 rows.push({site,x,z,savedMeasuredPairFaces:[savedSite.leftFace,savedSite.rightFace],actualSamplerHeight:sampled,highestCompleteRayHeight:ray,hits:hits.length,highestRayCandidateFace:hits.length?hits[0].faceIndex:null,error,existingCompleteRayAuditLimitM:1e-5,existingGeometryBoundRayAgreementLimitM:.01,passed:error!==null&&Number.isFinite(error)&&error<1e-5,geometryBoundContractPass:error!==null&&Number.isFinite(error)&&error<.01});
}
geometry.dispose();mesh.material.dispose();verifyModuleClosure(closure,root);
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
for(const pin of input.runtimeInputRefs)assert.equal(sha(readFileSync(new URL(pin.path,root))),pin.sha256,pin.path);
await writeExactJsonGzip(new URL(doc+'/actual-saved64-full-candidate-native-max-ray-findings.json.gz',root),{rows,samples:64,maxError:Math.max(...rows.filter(r=>r.error!==null).map(r=>r.error),0),failedRows:rows.filter(r=>!r.passed),completeCandidateFacets:11576,completeUnusedPositionVertices:surface.position.length/3,productionIndexedTriangleCount:surface.triangles,allDrawnCandidateIndicesUsedForIndependentRay:true,productionMAXEligibilityAnd20mBinsUnmodified:true,completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,samplesNotWholeSurfaceCoverageOrContinuousMAXProof:true,noGeometryChanges:true,noApprovalWrittenByRuntime:true});
console.log(JSON.stringify({samples:64,failedRows:rows.filter(r=>!r.passed).length,noGeometryChanges:true,noApprovalWrittenByRuntime:true}));
