/** ROOT-only full actual source/BASIC capture. No terrain or scene writes. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from '../../../../source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions,positionBounds} from '../../../../source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs';
import {appendFiniteOrdered,preflightActualRenderMesh} from '../../../../source-scripts/city/government-import/current_geometry_capture_preflight_20261011.mjs';
const root=new URL('../../../../',import.meta.url),packet=new URL('./',import.meta.url);
const hash=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function bytes(path,expected){const u=new URL(path,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u);if(expected!==undefined)assert.equal(hash(b),expected,path);hashes[path]=hash(b);return b;}
function read(path,expected){const b=bytes(path,expected);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const c=JSON.parse(readFileSync(new URL('input-contract.json',packet))),contractSHA=hash(readFileSync(new URL('input-contract.json',packet)));
for(const [p,h]of Object.entries(c.filePins))bytes(p,h);
assert.equal(hash(readFileSync(new URL(import.meta.url))),c.exporterSHA256);
assert.equal(hashes['3d-viewer/city/data/manifest.json'],c.currentManifestSHA256);
const entries=['3d-viewer/city/official-model-assets.js','3d-viewer/city/building-geometry.js',
 'source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs',
 'source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs',
 'source-scripts/city/government-import/current_geometry_capture_preflight_20261011.mjs'];
const closures=entries.map(p=>snapshotModuleClosure(new URL(p,root),root));
for(const closure of closures){
 assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');
 assert.equal(closure.unsupportedDynamicImports,0);assert.equal(closure.completeAuditedLiteralImportClosure,true);
 assert.equal(closure.computedImportsRejected,true);assert.equal(closure.opaqueResourcesAreNotParsedModules,true);
 assert.deepEqual(Object.keys(closure.inputHashes).sort(),[...closure.modules,...closure.resources].sort());
 assert.equal(new Set([...closure.modules,...closure.resources]).size,closure.modules.length+closure.resources.length);
 const resources=closure.modules.includes('3d-viewer/vendor/DRACOLoader.js')?
 ['3d-viewer/vendor/draco_decoder.js','3d-viewer/vendor/draco_decoder.wasm','3d-viewer/vendor/draco_wasm_wrapper.js']:[];
 assert.deepEqual([...closure.resources].sort(),resources.sort());
 Object.assign(hashes,closure.inputHashes);assert(verifyModuleClosure(closure,root));
}
function finalFence(){
 assert.equal(hash(readFileSync(new URL('input-contract.json',packet))),contractSHA);
 for(const[p,h]of Object.entries(hashes))assert.equal(hash(readFileSync(new URL(p,root))),h,p);
 for(const closure of closures)assert(verifyModuleClosure(closure,root));
}
if(process.argv[2]==='--closure-schema-only'){
 const target=new URL(process.argv[3],root);assert(target.pathname.startsWith(packet.pathname));assert(!existsSync(target));
 finalFence();writeFileSync(target,JSON.stringify({passed:true,closures,inputHashes:hashes,noProductionModuleImported:true,noGeometryCalculated:true},null,2)+'\n');
 console.log(JSON.stringify({passed:true,closures:closures.length,noProductionModuleImported:true}));
}else{
 assert.equal(process.argv[2],'--capture-current-full-geometry-only');
 const target=new URL('collision-output-v2/complete-current-star-and-museum-geometry.json.gz',packet);assert(!existsSync(target));
 const row=read(c.sourceRowPath),savedForms=read(c.currentFormsPath),forms=new Map(savedForms.map(r=>[r.form.uid,r.form]));
 assert.deepEqual([...forms.keys()].sort(),['landsd/104467:0','landsd/165054:0','landsd/57455:0']);
 for(const r of savedForms){const matches=read(r.sourceTile,r.sourceTileSHA256).buildings.filter(b=>b.uid===r.form.uid);assert.deepEqual(matches,[r.form]);}
 assert.equal(row.uid,'landsd/165054:0');assert.equal(row.triangles,15140);assert.equal(row.sourceSHA256,c.sourceSHA256);
 assert.deepEqual(row.candidate.entry.rootTranslation,[-834500,0,816500]);assert.deepEqual(row.source.building,forms.get(row.uid));
 assert.equal(row.candidate.entry.sha256,row.sourceSHA256);assert.equal(row.candidate.entry.triangles,15140);
 const manifest=read('3d-viewer/city/data/manifest.json'),native=[];
 for(const path of manifest.officialModelCatalogues)native.push(...read('3d-viewer/'+path).models);
 assert.equal(native.length,6650);assert.equal(new Set(native.map(e=>e.uid)).size,6650);
 for(const uid of [row.uid,'landsd/57455:0']){assert(!native.some(e=>e.uid===uid));assert(!native.some(e=>(e.suppressesBuildingUids||[]).includes(uid)));}
 const {loadOfficialModel,disposeOfficialModel}=await import('../../../../3d-viewer/city/official-model-assets.js');
 const {createBuildingGeometry}=await import('../../../../3d-viewer/city/building-geometry.js');
 const THREE=await import('../../../../3d-viewer/vendor/three.module.js');
 const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
 let model,basic;
 try{
  const raw=bytes(row.candidate.path,row.sourceSHA256);
  model=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/original.glb.gz'},forms.get(row.uid),lighting,{fetcher:async()=>new Response(raw),getBuilding:uid=>{assert(forms.has(uid));return forms.get(uid);}});
  model.group.updateMatrixWorld(true);assert.equal(model.meshes.length,1);
  // GLTFLoader.loadScene creates a Group; loadNode applies each original matrix
  // using Object3D.applyMatrix4 (decompose), then updateMatrixWorld composes TRS.
  // The raw matrix product is retained for comparison, never used as a new pose.
  const expectedGroup=new THREE.Group(),expectedRoot=new THREE.Object3D(),expectedMesh=new THREE.Object3D();
  expectedRoot.applyMatrix4(new THREE.Matrix4().fromArray(c.originalRootMatrix));
  expectedRoot.add(expectedMesh);expectedGroup.add(expectedRoot);
  const offset=row.candidate.entry.verticalPlacementOffsetHKPD??0;
  expectedGroup.position.set(row.candidate.entry.rootTranslation[0],row.candidate.entry.rootTranslation[1]+offset,row.candidate.entry.rootTranslation[2]);
  expectedGroup.updateMatrixWorld(true);
  const expectedMatrix=expectedMesh.matrixWorld;
  const directOriginalProduct=new THREE.Matrix4().makeTranslation(row.candidate.entry.rootTranslation[0],row.candidate.entry.rootTranslation[1]+offset,row.candidate.entry.rootTranslation[2]).multiply(new THREE.Matrix4().fromArray(c.originalRootMatrix));
  function matrixRecord(node){return {type:node.type,name:node.name,localMatrixFloat64:Array.from(node.matrix.elements),worldMatrixFloat64:Array.from(node.matrixWorld.elements),position:Array.from(node.position.toArray()),quaternion:Array.from(node.quaternion.toArray()),scale:Array.from(node.scale.toArray()),matrixAutoUpdate:node.matrixAutoUpdate,matrixWorldAutoUpdate:node.matrixWorldAutoUpdate,childCount:node.children.length};}
  const actualChain=[];model.group.traverse(node=>{const path=[];for(let n=node;n!==model.group;n=n.parent){assert(n.parent);path.unshift(n.parent.children.indexOf(n));}actualChain.push({childIndexPath:path,...matrixRecord(node)});});
  const actualRoot=model.group.children[0],actualMesh=model.meshes[0];
  const pose={uid:row.uid,sourceSHA256:row.sourceSHA256,originalNodesVerbatim:model.record.modelSource.originalNodes,
   expectedOriginalNodesVerbatim:c.originalSourceNodes,entryRootTranslation:row.candidate.entry.rootTranslation,
   entryVerticalPlacementOffsetPresent:Object.hasOwn(row.candidate.entry,'verticalPlacementOffsetHKPD'),entryVerticalPlacementOffsetHKPD:offset,
   originalRootMatrixFloat64:c.originalRootMatrix,actualCompleteSceneChain:actualChain,
   expectedLoaderSceneGroup:matrixRecord(expectedGroup),expectedLoaderOriginalRoot:matrixRecord(expectedRoot),expectedLoaderMesh:matrixRecord(expectedMesh),
   directOriginalMatrixProductFloat64:Array.from(directOriginalProduct.elements),
   exactActualMeshMatchesDirectOriginalProduct:actualMesh.matrixWorld.equals(directOriginalProduct),
   exactLoaderTransformContractMatched:model.group.matrix.equals(expectedGroup.matrix)&&model.group.matrixWorld.equals(expectedGroup.matrixWorld)&&
    !!actualRoot&&actualRoot.matrix.equals(expectedRoot.matrix)&&actualRoot.matrixWorld.equals(expectedRoot.matrixWorld)&&actualMesh.matrix.equals(expectedMesh.matrix)&&actualMesh.matrixWorld.equals(expectedMesh.matrixWorld),
   noToleranceIntroduced:true,sourcePoseChanges:0,sourceGeometryChanges:0,physicalAccepted:false,currentAcceptance:false};
  // Close complete actual/expected matrix evidence BEFORE pose/hierarchy asserts.
  finalFence();const poseTarget=new URL('collision-output-v2/actual-and-expected-source-pose.json',packet);assert(!existsSync(poseTarget));
  writeFileSync(poseTarget,JSON.stringify(pose,null,2)+'\n');
  assert.deepEqual(model.record.modelSource.originalNodes,c.originalSourceNodes,'Original node metadata differs');
  assert.deepEqual(c.originalSourceNodes,[{children:[1],matrix:c.originalRootMatrix,name:row.candidate.entry.modelId},{mesh:0}]);
  assert.equal(model.group.children.length,1);assert.equal(actualRoot.children.length,1);assert.equal(actualRoot.children[0],actualMesh);assert.equal(actualMesh.children.length,0);
  assert(pose.exactLoaderTransformContractMatched,'Current source differs from authentic loader transform contract');
  const meshes=[],literal=[],left=[],balanced=[],indices=[];
  for(const mesh of model.meshes){
   preflightActualRenderMesh(mesh);assert(mesh.matrixWorld.equals(expectedMatrix),'Current source pose differs');
   const p=mesh.geometry.attributes.position,ix=mesh.geometry.index.array,attr={};
   for(const[name,a]of Object.entries(mesh.geometry.attributes)){assert(Array.from(a.array).every(Number.isFinite));attr[name]={itemSize:a.itemSize,count:a.count,normalized:a.normalized,arrayType:a.array.constructor.name,values:Array.from(a.array)};}
   const f32=actualFloat32ModelMatrixPositions(p.array,mesh.matrixWorld.elements),v=new THREE.Vector3();
   for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(mesh.matrixWorld);literal.push(v.x,v.y,v.z);}
   for(const i of ix)indices.push(i);
   appendFiniteOrdered(left,f32.leftAssociatedPerMultiplyAddFloat32WorldPosition);
   appendFiniteOrdered(balanced,f32.balancedPerMultiplyAddFloat32WorldPosition);
   meshes.push({completeAttributes:attr,completeIndex:Array.from(ix),indexArrayType:ix.constructor.name,matrixWorldFloat64:Array.from(mesh.matrixWorld.elements),...f32});
  }
  assert.equal(indices.length/3,15140);assert.deepEqual(literal,Array.from(model.record.modelGeometry.position));assert.deepEqual(indices,Array.from(model.record.modelGeometry.index));
  basic=createBuildingGeometry(forms.get('landsd/57455:0'));
  const p=basic.attributes.position;assert(p.array instanceof Float32Array&&p.count>0);assert(Array.from(p.array).every(Number.isFinite));
  const ix=basic.index?Array.from(basic.index.array):Array.from({length:p.count},(_,i)=>i);assert(ix.length%3===0&&ix.every(i=>Number.isInteger(i)&&i>=0&&i<p.count));
  const identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],f32=actualFloat32ModelMatrixPositions(p.array,identity),attrs={};
  assert.deepEqual(f32.leftAssociatedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));assert.deepEqual(f32.balancedPerMultiplyAddFloat32WorldPosition,Array.from(p.array));
  for(const[name,a]of Object.entries(basic.attributes)){assert(Array.from(a.array).every(Number.isFinite));attrs[name]={itemSize:a.itemSize,count:a.count,normalized:a.normalized,arrayType:a.array.constructor.name,values:Array.from(a.array)};}
  finalFence();writeFileSync(target,gzipSync(JSON.stringify({uid:row.uid,sourceSHA256:row.sourceSHA256,entry:row.candidate.entry,currentSourceForm:forms.get(row.uid),
   poseAuditSHA256:hash(readFileSync(poseTarget)),completeOriginalFaceCount:15140,completeOriginalIndex:indices,completeLiteralWorldPosition:literal,completeLeftFloat32WorldPosition:left,completeBalancedFloat32WorldPosition:balanced,
   actualSourceMeshes:meshes,wholeUnusedWorldBounds:{literal:positionBounds(literal),left:positionBounds(left),balanced:positionBounds(balanced)},
   starMart:{uid:'landsd/57455:0',currentForm:forms.get('landsd/57455:0'),completeAttributes:attrs,completePosition:Array.from(p.array),completeIndex:ix,completeFaces:ix.length/3,completeVertices:p.count,
    matrixWorldFloat64:identity,wholeUnusedPositionBounds:positionBounds(Array.from(p.array)),...f32},
   completeClosures:closures,inputHashes:hashes,startAndEndInputsVerified:true,noTerrainCaptureOrChanges:true,sourceGeometryChanges:0,sourcePoseChanges:0,
   noActorSuppression:true,explicitArithmeticNotUniversalGPUGuarantee:true,physicalAccepted:false,currentAcceptance:false,installationApproved:false})));
  console.log(JSON.stringify({complete:true,sourceFaces:15140,fullBasicFaces:ix.length/3,sourceUnusedVertices:literal.length/3,basicUnusedVertices:p.count,captureSHA256:hash(readFileSync(target)),physicalAccepted:false}));
 }finally{if(model)disposeOfficialModel(model);if(basic)basic.dispose();}
}
