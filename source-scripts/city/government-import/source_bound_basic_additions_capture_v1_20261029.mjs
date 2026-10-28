/** Capture only the new private illustrative BASIC continuation triangles. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {createBuildingGeometry as original} from '../../../3d-viewer/city/building-geometry.js';
import {createBuildingGeometry as proposed} from '../../../3d-viewer/city/source-bound-basic-geometry-private.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[input,output]=process.argv.slice(2),hash=b=>createHash('sha256').update(b).digest('hex');
for(const p of [input,output])assert(p.startsWith('docs/astra-city/government-import/')&&!p.includes('..'));
const closure=snapshotModuleClosure(new URL('3d-viewer/city/source-bound-basic-geometry-private.js',root),root),raw=readFileSync(input),packet=JSON.parse(raw);
assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);assert(packet.privateProposalOnly&&!packet.publication);
const rows=packet.rows.map(r=>{
 const old=original(r.originalBuilding),next=proposed(r.proposedBuilding),count=old.attributes.position.count;
 for(const [name,a]of Object.entries(old.attributes))assert.deepEqual(next.attributes[name].array.slice(0,a.array.length),a.array);
 const position=Array.from(next.attributes.position.array.slice(count*3));assert(position.length&&position.length%9===0);
 old.dispose();next.dispose();return {uid:r.uid,position,index:Array.from({length:position.length/3},(_,i)=>i)};
});
assert(verifyModuleClosure(closure,root));
const inputHashes={...closure.inputHashes,[input]:hash(raw),'source-scripts/city/government-import/source_bound_basic_additions_capture_v1_20261029.mjs':hash(readFileSync(new URL('source-scripts/city/government-import/source_bound_basic_additions_capture_v1_20261029.mjs',root)))};
writeFileSync(output,gzipSync(JSON.stringify({rows,inputHashes,privateProposalOnly:true,sourceGeometryChanges:0,publication:false})));
