/** Complete actual current BASIC podium body; no original-podium credit. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
const root=new URL('../../../',import.meta.url),doc='docs/astra-city/government-import/government-xl-lippo-current-basic-podium-support-inputs-v1-20261011';
const sha=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function bytes(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return b;}
const closure=snapshotModuleClosure(import.meta.url,root);Object.assign(hashes,closure.inputHashes);
const input=JSON.parse(gunzipSync(bytes(doc+'/input.json.gz')));assert(input.currentBasicUID==='landsd/231645:0');
const manifestBytes=bytes('3d-viewer/city/data/manifest.json');assert.equal(sha(manifestBytes),input.manifestSHA256);const manifest=JSON.parse(manifestBytes);
const installed=manifest.officialModelCatalogues.flatMap(url=>JSON.parse(bytes('3d-viewer/'+url)).models);assert(!installed.some(e=>e.uid===input.currentBasicUID));
const tileBytes=bytes('3d-viewer/'+input.currentTile);assert.equal(sha(tileBytes),input.currentTileSHA256);
const matches=JSON.parse(tileBytes).buildings.filter(b=>b.uid===input.currentBasicUID);assert.equal(matches.length,1);const building=matches[0];assert.deepEqual(building,input.currentForm);
assert.equal(building.buildingCSUID,'3551417531P20050812');assert.equal(building.structureType,'Podium');assert.equal(building.base,4.1);assert.equal(building.base+building.height,18.6);
const geometry=createBuildingGeometry(building);let body;
try{const p=geometry.attributes.position;assert(p.array instanceof Float32Array);body={position:Array.from(p.array),index:geometry.index?Array.from(geometry.index.array):Array.from({length:p.count},(_,i)=>i),normal:Array.from(geometry.attributes.normal.array),positionAttributeArrayType:p.array.constructor.name,identityModelMatrix:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]};assert(body.index.length%3===0&&body.position.every(Number.isFinite));}finally{geometry.dispose();}
for(const [path,pin] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),pin);assert(verifyModuleClosure(closure,root));
const output=doc+'/complete-current-basic-podium-geometry.json.gz';assert(!existsSync(new URL(output,root)));writeFileSync(new URL(output,root),gzipSync(JSON.stringify({uid:input.currentBasicUID,currentForm:building,completeCurrentRendererBody:body,currentRendererPositionFloat32SHA256:sha(Buffer.from(new Float32Array(body.position).buffer)),inputHashes:hashes,completeRecursiveProductionModuleClosure:closure,startAndEndInputHashesVerified:true,currentActorChanges:0,originalGovernmentPodiumUsedAsSupport:false,physicalAccepted:false,installationApproved:false})));
console.log(JSON.stringify({uid:input.currentBasicUID,completeCurrentBasicFaces:body.index.length/3,originalGovernmentPodiumUsedAsSupport:false}));
