/** UNEXECUTED candidate-only 64 sites: actual native MAX and full indexed ray. */
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
const closure=snapshotModuleClosure(import.meta.url,root);
assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');
assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
const THREE=await import('../../../3d-viewer/vendor/three.module.js');
const {nativeTerrainSurface}=await import('../../../3d-viewer/city/native-terrain.js');
const {withinFiniteTriangleProjection}=await import('../../../3d-viewer/city/exact-finite-triangle-projection.js');
const input=read(doc+'/input.json.gz');assert.equal(input.schema,'polyu-saved64-candidate-only-max-v1');
assert(input.candidateOnly&&input.historicalSourceContext&&!input.currentAcceptance);
for(const pin of input.runtimeInputRefs)assert.equal(sha(raw(pin.path)),pin.sha256,pin.path);
const candidate=read(input.candidate.path);assert.equal(hashes[input.candidate.path],input.candidate.sha256);assert(!candidate.nativeMesh.sourceOverlap);
const saved=read(input.sites.path);assert.equal(hashes[input.sites.path],input.sites.sha256);assert.equal(saved.rows.length,64);assert.equal(saved.samples,64);
const surface=nativeTerrainSurface(candidate.nativeMesh);assert.equal(candidate.nativeMesh.index.length/3,input.completeMeshBinding.completeIndexedFaces);assert.equal(surface.position.length/3,input.completeMeshBinding.completePositionVertices);
const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(surface.position,3));geometry.setIndex(candidate.nativeMesh.index);
const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.updateMatrixWorld(true);
assert.deepEqual(mesh.matrixWorld.elements,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
let high=-Infinity;for(let i=1;i<surface.position.length;i+=3)high=Math.max(high,surface.position[i]);assert(Number.isFinite(high));
function member(face,x,z){const p=surface.position,idx=candidate.nativeMesh.index,vs=idx.slice(face*3,face*3+3).map(i=>[p[i*3],p[i*3+2]]);return withinFiniteTriangleProjection(vs[0],vs[1],vs[2],[x,z]);}
const rows=[];
for(let site=0;site<64;site++){
 const s=saved.rows[site],{x,z}=s;assert(Number.isFinite(x)&&Number.isFinite(z));
 const membership=[member(s.leftFace,x,z),member(s.rightFace,x,z)];
 const hits=new THREE.Raycaster(new THREE.Vector3(x,high+100,z),new THREE.Vector3(0,-1,0)).intersectObject(mesh);
 const sampled=surface.height(x,z),ray=hits.length?hits[0].point.y:null,error=sampled!==null&&ray!==null?Math.abs(sampled-ray):null;
 rows.push({site,x,z,leftFace:s.leftFace,rightFace:s.rightFace,group:s.group,sameAuthenticatedIdealPlane:s.sameAuthenticatedIdealPlane,
  actualSelectedPairClosedProjectionMembership:membership,actualSamplerHeight:sampled,highestCompleteRayHeight:ray,hits:hits.length,
  highestRayCandidateFace:hits.length?hits[0].faceIndex:null,error,existingCompleteRayAuditLimitM:1e-5,existingGeometryBoundRayAgreementLimitM:.01,
  passed:membership.every(Boolean)&&error!==null&&Number.isFinite(error)&&error<1e-5,
  geometryBoundContractPass:error!==null&&Number.isFinite(error)&&error<.01});
 console.log(JSON.stringify({completedSites:site+1,failed:!rows.at(-1).passed}));
}
geometry.dispose();mesh.material.dispose();verifyModuleClosure(closure,root);
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
for(const pin of input.runtimeInputRefs)assert.equal(sha(readFileSync(new URL(pin.path,root))),pin.sha256,pin.path);
await writeExactJsonGzip(new URL(doc+'/actual-saved64-full-candidate-native-max-ray-findings.json.gz',root),{
 rows,samples:64,maxError:Math.max(...rows.filter(r=>r.error!==null).map(r=>r.error),0),failedRows:rows.filter(r=>!r.passed),
 completeCandidateFacets:input.completeMeshBinding.completeIndexedFaces,completeUnusedPositionVertices:input.completeMeshBinding.completePositionVertices,productionIndexedTriangleCount:surface.triangles,
 allDrawnCandidateIndicesUsedForIndependentRay:true,productionMAXEligibilityAnd20mBinsUnmodified:true,
 completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,
 samplesNotWholeSurfaceCoverageOrContinuousMAXProof:true,candidateOnly:true,currentAcceptance:false,noGeometryChanges:true,noApprovalWrittenByRuntime:true});
