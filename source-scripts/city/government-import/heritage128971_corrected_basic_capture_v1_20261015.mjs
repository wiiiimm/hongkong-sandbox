/** Private recapture of a terrain-estimated BASIC form; no government mesh edits. */
import {readFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
import {makeBuildings} from '../../../3d-viewer/city/world.js';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],sha=b=>createHash('sha256').update(b).digest('hex');
assert.equal(doc,'docs/astra-city/government-import/government-xl-heritage128971-corrected-basic-validation-v1-20261015');
const raw=readFileSync(new URL(doc+'/input.json.gz',root)),input=JSON.parse(gunzipSync(raw));
const closure=snapshotModuleClosure(import.meta.url,root);
const verify=()=>{for(const q of input.evidenceRefs)assert.equal(sha(readFileSync(new URL(q.path,root))),q.sha256,q.path);verifyModuleClosure(closure,root);};verify();
const b=input.building;assert.equal(b.uid,'landsd/128971:0');assert.equal(b.baseSource,'terrain-estimated');assert.equal(b.heightSource,'estimated');assert.equal(b.height,3);assert.equal(b.baseHeightHKPD??null,null);assert.equal(b.topHeightHKPD??null,null);assert(!b.modelGeometry);
const built=await makeBuildings([b],null,{worker:false,yield:false}),meshes=[],identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],v=new THREE.Vector3();let faces=0;
try{built.group.updateMatrixWorld(true);built.group.traverse(m=>{if(!m.isMesh)return;assert.deepEqual(m.matrixWorld.elements,identity);const p=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??p.count;assert(p.array instanceof Float32Array&&n%3===0);const literal=[],index=[];for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);literal.push(...v.toArray());}for(let i=0;i<n;i++)index.push(ix?ix.getX(i):i);const ar=actualFloat32ModelMatrixPositions(p.array,m.matrixWorld.elements);const streams={constructorFloat32World:literal,leftFloat32World:ar.leftAssociatedPerMultiplyAddFloat32WorldPosition,balancedFloat32World:ar.balancedPerMultiplyAddFloat32WorldPosition};assert(Object.values(streams).every(a=>a.every(Number.isFinite)));meshes.push({positionAttributeFloat32:Array.from(p.array),positionAttributeSHA256:sha(Buffer.from(p.array.buffer,p.array.byteOffset,p.array.byteLength)),index,completePositionVerticesIncludingUnused:p.count,completeIndexedFaces:n/3,matrixWorldFloat64:Array.from(m.matrixWorld.elements),modelMatrixUniformFloat32:ar.modelMatrixUniformFloat32,streams});faces+=n/3;});assert(faces>0);}
finally{built.group.traverse(m=>m.geometry?.dispose());for(const m of built.materials)m.dispose();}
verify();assert.equal(sha(readFileSync(new URL(doc+'/input.json.gz',root))),sha(raw));
await writeExactJsonGzip(new URL(doc+'/corrected-basic-streams.json.gz',root),{uid:b.uid,building:b,meshes,completeFaces:faces,completeRecursiveProductionModuleClosure:closure,completeUnusedPositionsRetained:true,governmentGeometryChanged:false,estimatedBasicBaseChanged:true,installationApproved:false});console.log(JSON.stringify({uid:b.uid,faces}));
