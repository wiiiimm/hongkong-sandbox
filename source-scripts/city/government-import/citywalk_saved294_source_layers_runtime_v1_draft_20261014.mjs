/** Saved points/source arrays only: no loader, rim resampling, terrain or approval. */
import {readFileSync} from 'node:fs';import {gunzipSync} from 'node:zlib';import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
import {attribute} from './citywalk_saved294_source_layers_helper_v1_draft_20261014.mjs';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {writeExactJsonGzip} from './exact_incremental_json_gzip_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/'));
function read(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz'),closure=snapshotModuleClosure(new URL(import.meta.url),root);verifyModuleClosure(closure,root);
assert.equal(input.savedPoints.length,294);assert.equal(input.bodyLabels.length,41277);assert.equal(input.originalSourceFaces,41277);
for(const q of input.runtimeInputRefs)assert.equal(sha(readFileSync(new URL(q.path,root))),q.sha256,q.path);
const rows=[];
for(const world of input.sourceWorlds){
 assert.equal(world.position.length,41277*9);assert(world.position.every(Number.isFinite));const raw=Buffer.allocUnsafe(world.position.length*8);for(let i=0;i<world.position.length;i++)raw.writeDoubleLE(world.position[i],i*8);assert.equal(sha(raw),world.worldSHA256,'Exact saved binary64 world SHA');
 const geometry={position:world.position,index:Array.from({length:41277*3},(_,i)=>i)},result=attribute(geometry,input.savedPoints,input.bodyLabels);
 rows.push({sourceWorld:world.label,completeSourceWorldSHA256:world.worldSHA256,...result,expandedFaceCoordinatesNotAnAssetEdit:true});
 console.log(JSON.stringify({sourceWorld:world.label,completeSavedPoints:result.rows.length,sourceFaces:result.completeSourceFacets}));
}
verifyModuleClosure(closure,root);for(const q of input.runtimeInputRefs)assert.equal(sha(readFileSync(new URL(q.path,root))),q.sha256,q.path);
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
await writeExactJsonGzip(new URL(doc+'/complete-saved294-source-layer-attribution.json.gz',root),{sourceOnly:true,currentAcceptance:false,physicalAccepted:false,installationApproved:false,savedPointCount:294,rawHistoricalWarningsUnchanged:true,sourceWorldRows:rows,sourceBytesAndPosesUnchanged:true,terrainNotReadOrChanged:true,EPSAndStrictFloat32ContractsSeparate:true,noThresholdOrAutomaticRoleChange:true,currentRelevantTupleRebind:input.currentRelevantTupleRebind,explicitArithmeticNotUniversalGPUProof:true,completeRecursiveProductionModuleClosure:closure,inputHashes:hashes,startEndAllInputsVerified:true});
