/** Unexecuted full actual BASIC attribute bounds; no source/terrain mutations. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions,positionBounds} from './actual_float32_model_matrix_bounds_20261011.mjs';
const root=new URL('../../../',import.meta.url),draft='docs/astra-city/government-import/government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013/',hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(path,expected){const u=new URL(path,root);assert(u.pathname.startsWith(root.pathname));const raw=readFileSync(u);if(expected!==undefined)assert.equal(sha(raw),expected,path);hashes[path]=sha(raw);return raw;}
function read(path,expected){const raw=bytes(path,expected);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const inputPath=draft+'actual-basic-protection-input.json.gz',input=read(inputPath),inputSHA256=hashes[inputPath];
assert.equal(input.schema,'polyu25-complete-basic-protection-input-v1');assert.equal(input.forms.length,25);assert.equal(new Set(input.forms.map(r=>r.uid)).size,25);
for(const[p,h]of Object.entries(input.inputHashes))bytes(p,h);
const manifest=read('3d-viewer/city/data/manifest.json','c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7');
const natives=new Set();for(const url of manifest.officialModelCatalogues)for(const entry of read('3d-viewer/'+url).models){assert(!natives.has(entry.uid));natives.add(entry.uid);}assert.equal(natives.size,6650);
const wanted=new Map(input.forms.map(form=>[form.uid,form])),matches=new Map();
for(const tile of manifest.tiles)for(const form of read('3d-viewer/'+tile.url).buildings)if(wanted.has(form.uid)){assert(!matches.has(form.uid),'Duplicate actual source form');matches.set(form.uid,form);assert.deepEqual(form,wanted.get(form.uid));}
assert.equal(matches.size,25);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);
const helperClosures=['exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','actual_float32_model_matrix_bounds_20261011.mjs'].map(p=>snapshotModuleClosure(new URL('source-scripts/city/government-import/'+p,root),root));
for(const c of [closure,...helperClosures]){
 assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.completeAuditedLiteralImportClosure&&c.computedImportsRejected&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);assert.deepEqual(Object.keys(c.inputHashes).sort(),[...c.modules,...c.resources].sort());
 assert.equal(new Set(c.modules).size,c.modules.length);assert.equal(new Set(c.resources).size,c.resources.length);assert(c.resources.every(p=>!c.modules.includes(p)));
 const expected=c.modules.includes('3d-viewer/vendor/DRACOLoader.js')?['3d-viewer/vendor/draco_decoder.js','3d-viewer/vendor/draco_decoder.wasm','3d-viewer/vendor/draco_wasm_wrapper.js']:[];assert.deepEqual([...c.resources].sort(),expected.sort());Object.assign(hashes,c.inputHashes);
}
bytes('source-scripts/city/government-import/xl-polyu-sports305582-current25-basic-protection-geometry-draft-v1-20261013.mjs');
const {createBuildingGeometry}=await import(new URL('3d-viewer/city/building-geometry.js',root).href),THREE=await import(new URL('3d-viewer/vendor/three.module.js',root).href);
const identity=new THREE.Matrix4(),rows=[];assert.equal(new Uint8Array(new Uint32Array([1]).buffer)[0],1,'Recorded byte arithmetic requires actual little-endian host');
for(const form of input.forms){
 if(natives.has(form.uid)){assert.equal(form.uid,'landsd/305793:0');assert.equal(input.installedPodiumDependency.entry.publicationApproved,false);assert.equal(input.currentNativeBoundsRecord.uid,form.uid);rows.push({uid:form.uid,currentForm:form,classification:'installed-native-scalar-bounds-whole-terrain-regression-pending',completeCurrentNativeBoundsVerbatim:input.currentNativeBoundsRecord,installedEntryVerbatim:input.installedPodiumDependency.entry,wholeNativeBeforeAfterTerrainRegressionProved:false});continue;}
 const geometry=createBuildingGeometry(form);
 try{
  const p=geometry.attributes.position;assert(p&&p.itemSize===3&&p.array instanceof Float32Array);assert.equal(p.array.length,p.count*3);assert(Array.from(p.array).every(Number.isFinite));
  const ix=geometry.index?Array.from(geometry.index.array):Array.from({length:p.count},(_,i)=>i);assert.equal(ix.length%3,0);assert(ix.every(i=>Number.isInteger(i)&&i>=0&&i<p.count));
  if(p.count===0){assert.equal(ix.length,0);rows.push({uid:form.uid,currentForm:form,classification:'actual-production-BASIC',completePositionVertices:0,completeIndexedFaces:0,wholeUnusedPositionVerticesIncluded:true,identityWorldMatrix:identity.elements,boundsByArithmetic:null});continue;}
  const f=actualFloat32ModelMatrixPositions(p.array,identity.elements),literal=[],v=new THREE.Vector3();for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(identity);for(const value of v.toArray()){assert(Number.isFinite(value));literal.push(value);}}
  const left=f.leftAssociatedPerMultiplyAddFloat32WorldPosition,balanced=f.balancedPerMultiplyAddFloat32WorldPosition,attribute=Array.from(p.array);assert.deepEqual(literal,attribute);assert.deepEqual(left,attribute);assert.deepEqual(balanced,attribute);
  rows.push({uid:form.uid,currentForm:form,classification:'actual-production-BASIC',completePositionVertices:p.count,completeIndexedFaces:ix.length/3,wholeUnusedPositionVerticesIncluded:true,identityWorldMatrix:Array.from(identity.elements),modelMatrixUniformFloat32:f.modelMatrixUniformFloat32,positionAttributeSHA256:sha(Buffer.from(p.array.buffer,p.array.byteOffset,p.array.byteLength)),completeIndexSHA256:sha(Buffer.from(new Uint32Array(ix).buffer)),completeIndexBytesBase64:Buffer.from(new Uint32Array(ix).buffer).toString('base64'),completeStreamBytesBase64:{productionPositionAttribute:Buffer.from(p.array.buffer,p.array.byteOffset,p.array.byteLength).toString('base64'),actualLiteral:Buffer.from(new Float64Array(literal).buffer).toString('base64'),explicitLeftAssociatedF32ModelMatrix:Buffer.from(new Float64Array(left).buffer).toString('base64'),explicitBalancedF32ModelMatrix:Buffer.from(new Float64Array(balanced).buffer).toString('base64')},actualLiteralSHA256:sha(Buffer.from(new Float64Array(literal).buffer)),explicitLeftAssociatedF32SHA256:sha(Buffer.from(new Float64Array(left).buffer)),explicitBalancedF32SHA256:sha(Buffer.from(new Float64Array(balanced).buffer)),boundsByArithmetic:{productionPositionAttribute:positionBounds(attribute),actualLiteral:positionBounds(literal),explicitLeftAssociatedF32ModelMatrix:positionBounds(left),explicitBalancedF32ModelMatrix:positionBounds(balanced)}});
 }finally{geometry.dispose();}
}
assert.equal(rows.filter(r=>r.classification==='actual-production-BASIC').length,24);assert.equal(rows.filter(r=>r.classification==='installed-native-scalar-bounds-whole-terrain-regression-pending').length,1);
for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);for(const c of [closure,...helperClosures])assert(verifyModuleClosure(c,root));
const output=draft+'actual-basic-protection-proof.json.gz';assert(!existsSync(new URL(output,root)));writeFileSync(new URL(output,root),gzipSync(JSON.stringify({schema:'polyu25-complete-actual-basic-protection-v1',inputSHA256,completeScannedForms:25,domainBounds:input.domainBounds,rows,inputHashes:hashes,recursiveProductionModuleClosure:closure,recursiveHelperModuleClosures:helperClosures,startAndEndInputsVerified:true,providerOriginalGovernmentMeshClaim:false,modelGeometryChanges:0,terrainGeometryChanges:0,physicalAccepted:false,installationApproved:false})));
console.log(JSON.stringify({forms:rows.length,actualBASIC:rows.filter(r=>r.classification==='actual-production-BASIC').length,nativeRegistryForms:rows.filter(r=>r.classification==='installed-native-scalar-bounds-whole-terrain-regression-pending').length,output,physicalAccepted:false}));
