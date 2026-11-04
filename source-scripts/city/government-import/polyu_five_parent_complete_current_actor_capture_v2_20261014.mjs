/** UNEXECUTED targeted native59527 +24 BASIC production attributes; no acceptance. */
import {readFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
import {loadOfficialModel,disposeOfficialModel,prepareModelCatalogue} from '../../../3d-viewer/city/official-model-assets.js';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/'));
function bytes(path,expected){const u=new URL(path,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u),h=sha(b);if(expected!==undefined)assert.equal(h,expected,path);if(hashes[path])assert.equal(hashes[path],h);hashes[path]=h;return b;}
function read(path,expected){const b=bytes(path,expected);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz');assert.equal(input.schema,'polyu-five-current-parent-actual-production-capture-v2');
for(const q of input.allInputRefs)bytes(q.path,q.sha256);
const closure=snapshotModuleClosure(import.meta.url,root);assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
for(const[p,h]of Object.entries(closure.inputHashes))bytes(p,h);
const manifest=read('3d-viewer/city/data/manifest.json',input.currentManifestSHA256),installed=new Map(),prepared=new Map(),forms=new Map(),wanted=new Map(input.exact25CurrentForms.map(f=>[f.uid,f]));assert.equal(wanted.size,25);
for(const url of manifest.officialModelCatalogues){const path='3d-viewer/'+url,c=read(path);for(const e of c.models){assert(!installed.has(e.uid));installed.set(e.uid,e);}for(const e of prepareModelCatalogue(c,new URL('https://diagnostic.invalid/'+path).href))prepared.set(e.uid,e);}
assert.equal(installed.size,6650);
for(const tile of manifest.tiles)for(const f of read('3d-viewer/'+tile.url).buildings)if(wanted.has(f.uid)){assert(!forms.has(f.uid),'Duplicate current UID');forms.set(f.uid,f);assert.deepEqual(f,wanted.get(f.uid));}
assert.equal(forms.size,25);const native=input.targetedNativeSource;assert.equal(native.uid,'landsd/305793:0');assert.deepEqual(installed.get(native.uid),native.entry);assert.equal(native.entry.triangles,59527);
const dependencyUIDs=(native.entry.supportDependencies||[]).map(d=>typeof d==='string'?d:d.uid);assert(dependencyUIDs.every(uid=>forms.has(uid)),'Undeclared native dependency input');
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
function attribute(a){assert(!a.isInterleavedBufferAttribute);assert(Array.from(a.array).every(Number.isFinite));return {array:Array.from(a.array),arrayType:a.array.constructor.name,itemSize:a.itemSize,count:a.count,normalized:a.normalized,byteSHA256:sha(Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength))};}
const source=bytes(native.asset.path,native.asset.sha256);let model,nativeRow;
try{model=await loadOfficialModel({...prepared.get(native.uid),assetURL:'https://diagnostic.invalid/original.glb.gz'},forms.get(native.uid),lighting,{fetcher:async()=>new Response(source),getBuilding:uid=>{assert(forms.has(uid),'Undeclared getBuilding UID '+uid);return forms.get(uid);}});model.group.updateMatrixWorld(true);
 const meshes=[],position=[],index=[],left=[],balanced=[];let offset=0;
 for(const m of model.meshes){const p=m.geometry.attributes.position,ix=m.geometry.index;assert(p.array instanceof Float32Array&&p.itemSize===3&&ix);const arithmetic=actualFloat32ModelMatrixPositions(p.array,m.matrixWorld.elements),v=new THREE.Vector3();
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);position.push(...v.toArray());}
  for(const i of ix.array){assert(Number.isInteger(i)&&i>=0&&i<p.count);index.push(i+offset);}offset+=p.count;
  for(const v of arithmetic.leftAssociatedPerMultiplyAddFloat32WorldPosition)left.push(v);for(const v of arithmetic.balancedPerMultiplyAddFloat32WorldPosition)balanced.push(v);
  meshes.push({allActualAttributes:Object.fromEntries(Object.entries(m.geometry.attributes).map(([k,a])=>[k,attribute(a)])),indexAttribute:attribute(ix),completeOriginalVertexAttribute:Array.from(p.array),completeOriginalIndex:Array.from(ix.array),matrixWorldFloat64:Array.from(m.matrixWorld.elements),matrixLocalFloat64:Array.from(m.matrix.elements),modelMatrixUniformFloat32:arithmetic.modelMatrixUniformFloat32,wholeUnusedPositionVerticesIncluded:true});
 }
 assert.deepEqual(position,Array.from(model.record.modelGeometry.position));assert.deepEqual(index,Array.from(model.record.modelGeometry.index));assert.equal(index.length/3,59527);assert.equal(offset,135627);
 nativeRow={uid:native.uid,sourceSHA256:sha(source),rawInstalledEntry:native.entry,currentForm:forms.get(native.uid),cataloguePreparedRootTranslation:prepared.get(native.uid).rootTranslation,originalNodeMetadata:model.record.modelSource.originalNodes,originalMaterialMetadata:model.record.modelSource.originalMaterials,loadedGroupMatrixWorldFloat64:Array.from(model.group.matrixWorld.elements),loadedGroupScale:model.group.scale.toArray(),actualRenderMeshes:meshes,completeLiteralWorldPosition:position,completeOriginalIndex:index,completeExplicitLeftAssociatedFloat32WorldPosition:left,completeExplicitBalancedFloat32WorldPosition:balanced,completeFaces:59527,completePositionVertices:offset,wholeUnusedPositionVerticesIncluded:true,sourceGeometryChanges:0,nativeReacceptance:false};
}finally{if(model)disposeOfficialModel(model);}
const basicRows=[],identity=new THREE.Matrix4();
for(const f of input.exact25CurrentForms){if(installed.has(f.uid)){assert.equal(f.uid,native.uid);continue;}let g;
 try{g=createBuildingGeometry(f);const p=g.attributes.position;assert(p.array instanceof Float32Array&&p.itemSize===3);const ix=g.index?Array.from(g.index.array):Array.from({length:p.count},(_,i)=>i);assert.equal(ix.length%3,0);assert(ix.every(i=>Number.isInteger(i)&&i>=0&&i<p.count));
  const arithmetic=p.count?actualFloat32ModelMatrixPositions(p.array,identity.elements):{modelMatrixUniformFloat32:Array.from(new Float32Array(identity.elements)),leftAssociatedPerMultiplyAddFloat32WorldPosition:[],balancedPerMultiplyAddFloat32WorldPosition:[]},literal=[],v=new THREE.Vector3();for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(identity);literal.push(...v.toArray());}
  const left=arithmetic.leftAssociatedPerMultiplyAddFloat32WorldPosition,balanced=arithmetic.balancedPerMultiplyAddFloat32WorldPosition;
  basicRows.push({uid:f.uid,currentForm:f,classification:'actual-production-BASIC-constructor',currentSuppressedByNativeUIDs:[...installed.values()].filter(e=>(e.suppressesBuildingUids||[]).includes(f.uid)).map(e=>e.uid),captureDoesNotOverrideCurrentSuppression:true,completePositionVertices:p.count,completeIndexedFaces:ix.length/3,wholeUnusedPositionVerticesIncluded:true,positionAttribute:attribute(p),index:ix,identityWorldMatrix:Array.from(identity.elements),modelMatrixUniformFloat32:arithmetic.modelMatrixUniformFloat32,completeLiteralWorldPosition:literal,completeExplicitLeftAssociatedFloat32WorldPosition:left,completeExplicitBalancedFloat32WorldPosition:balanced,allActualAttributes:Object.fromEntries(Object.entries(g.attributes).map(([k,a])=>[k,attribute(a)])),emptyConstructorIsAccountedNotFabricated:true,providerOriginalGovernmentMeshClaim:false});
 }finally{g?.dispose();}
}
assert.equal(basicRows.length,24);verifyModuleClosure(closure,root);for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const out=new URL(doc+'/complete-fresh-current-native59527-and24-BASIC.json.gz',root);assert(!existsSync(out));await writeExactJsonGzip(out,{nativeRow,basicRows,inputHashes:hashes,completeRecursiveProductionModuleClosure:closure,startEndAllInputsVerified:true,currentManifestSHA256:input.currentManifestSHA256,currentNativeActors:6650,ownedOriginal10536IsSeparateFromCurrent305582BASIC:true,explicitArithmeticOnlyNotUniversalGPUClaim:true,physicalAccepted:false,nativeReacceptance:false});
console.log(JSON.stringify({freshNativeFaces:59527,freshNativeUnusedPositions:135627,freshBASICActors:24,current6650CatalogueCensusOnlyNoWhole6650MeshLoad:true,noAcceptance:true}));
