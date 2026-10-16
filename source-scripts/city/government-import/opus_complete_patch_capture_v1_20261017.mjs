/** Capture every actually drawn face of the unchanged private native patch. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),sha=b=>createHash('sha256').update(b).digest('hex');
const [path,out]=process.argv.slice(2),raw=readFileSync(new URL(path,root));
const entry=new URL('3d-viewer/city/world.js',root),closure=snapshotModuleClosure(entry,root);
const {makeTerrain}=await import(entry.href),patch=JSON.parse(raw),mesh=makeTerrain(patch);mesh.updateMatrixWorld(true);
assert(mesh.isMesh);assert.deepEqual(mesh.matrixWorld.elements,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
const p=mesh.geometry.attributes.position.array,index=mesh.geometry.index.array;
assert.equal(index.length,patch.nativeMesh.index.length);
assert.deepEqual(Array.from(p),Array.from(new Float32Array(patch.nativeMesh.position)));
assert.equal(sha(readFileSync(new URL(path,root))),sha(raw));assert(verifyModuleClosure(closure,root));
writeFileSync(new URL(out,root),gzipSync(JSON.stringify({position:Array.from(p),index:Array.from(index),patchPath:path,patchSHA256:sha(raw),closure,sourceGeometryChanges:0,terrainChanges:0})));
mesh.geometry.dispose();mesh.material.dispose();console.log('Captured all '+index.length/3+' unchanged drawn terrain faces');
