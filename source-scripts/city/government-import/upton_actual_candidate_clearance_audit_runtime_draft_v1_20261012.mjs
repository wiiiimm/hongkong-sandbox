/** Read-only actual native Float32 sampler/complete THREE ray comparison. */
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={};
const sha=b=>createHash('sha256').update(b).digest('hex');
function read(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
for(const [p,h]of [['source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579'],['source-scripts/city/government-import/dependency-closure-vendor/acorn-8.8.1/acorn.mjs','a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55']])assert.equal(sha(readFileSync(new URL(p,root))),h);
const closure=snapshotModuleClosure(import.meta.url,root);assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
const THREE=await import('../../../3d-viewer/vendor/three.module.js');
const {nativeTerrainSurface}=await import('../../../3d-viewer/city/native-terrain.js');
const input=read(doc+'/input.json.gz');for(const pin of input.runtimeInputRefs)assert.equal(sha(readFileSync(new URL(pin.path,root))),pin.sha256,pin.path);
const candidate=read(input.candidate.path);assert.equal(hashes[input.candidate.path],input.candidate.sha256);
const audit=read(doc+'/measured-projection-and-parent-edge.json.gz'),surface=nativeTerrainSurface(candidate.nativeMesh),geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(surface.position,3));geometry.setIndex(candidate.nativeMesh.index);
const mesh=new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));mesh.updateMatrixWorld(true);let high=-Infinity;for(let i=1;i<surface.position.length;i+=3)high=Math.max(high,surface.position[i]);
const rows=[];for(const {x,z}of audit.float32HighestRayAgreement.rows){const hits=new THREE.Raycaster(new THREE.Vector3(x,high+100,z),new THREE.Vector3(0,-1,0)).intersectObject(mesh);const height=surface.height(x,z),ray=hits.length?hits[0].point.y:null;rows.push({x,z,actualSamplerHeight:height,highestCompleteRayHeight:ray,hits:hits.length,error:height!==null&&ray!==null?Math.abs(height-ray):null,existingRayAgreementLimitM:1e-5,passed:height!==null&&ray!==null&&Math.abs(height-ray)<1e-5});}
geometry.dispose();mesh.material.dispose();verifyModuleClosure(closure,root);for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);for(const pin of input.runtimeInputRefs)assert.equal(sha(readFileSync(new URL(pin.path,root))),pin.sha256,pin.path);
await writeExactJsonGzip(new URL(doc+'/actual-native-sampler-ray-findings.json.gz',root),{rows,samples:rows.length,maxError:Math.max(...rows.filter(r=>r.error!==null).map(r=>r.error),0),failedRows:rows.filter(r=>!r.passed),completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true,sampledAgreementNotContinuousSeamOrApproval:true,noGeometryChanges:true});
console.log(JSON.stringify({samples:rows.length,failedRows:rows.filter(r=>!r.passed).length,noApproval:true}));
