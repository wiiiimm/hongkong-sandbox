/** Export actual unchanged current basic render meshes; never change runtime. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const hash=x=>createHash('sha256').update(x).digest('hex');
const input=JSON.parse(readFileSync(process.argv[2]));
const manifest=readFileSync('3d-viewer/city/data/manifest.json');
assert.equal(hash(manifest),input.manifestSHA256);
const root=new URL('../../../',import.meta.url);const closure=snapshotModuleClosure(import.meta.url,root);const inputs={...closure.inputHashes};inputs[process.argv[2]]=hash(readFileSync(process.argv[2]));
for(const [p,h] of Object.entries(input.currentInputHashes)){const b=readFileSync(p);assert.equal(hash(b),h);inputs[p]=h;}
const rows=[];
for(const item of input.rows){
 const raw=readFileSync(item.tile),tile=JSON.parse(item.tile.endsWith('.gz')?gunzipSync(raw):raw);
 const actual=tile.buildings.find(b=>b.uid===item.building.uid);assert.deepEqual(actual,item.building);
 assert(!actual.modelGeometry);
 const g=createBuildingGeometry(actual),position=Array.from(g.attributes.position.array),index=g.index?Array.from(g.index.array):Array.from({length:position.length/3},(_,i)=>i);
 assert(position.length>0&&index.length%3===0);
 rows.push({uid:actual.uid,currentBuilding:actual,position,index});g.dispose();
}
for(const p of ['3d-viewer/city/building-geometry.js','3d-viewer/city/tai-o-estimates.js','3d-viewer/vendor/three.module.js','3d-viewer/vendor/BufferGeometryUtils.js'])inputs[p]=hash(readFileSync(p));
for(const [p,h] of Object.entries(inputs))assert.equal(hash(readFileSync(p)),h,'Basic production/input changed: '+p);
assert(verifyModuleClosure(closure,root));
assert.equal(hash(readFileSync('3d-viewer/city/data/manifest.json')),input.manifestSHA256);
writeFileSync(process.argv[3],JSON.stringify({rows,inputHashes:inputs,completeRecursiveProductionModuleClosure:closure,startAndEndInputHashesVerified:true,currentManifestSHA256:input.manifestSHA256,qualification:'Actual current basic Float32 render meshes only. Diagnostic, not complete geographic actor-scope or physical acceptance.'})+'\n');
