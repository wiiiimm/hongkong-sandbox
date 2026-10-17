/** Exercise existing illustrative-post foundations; no live form writes. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {describeBuilding,createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],mode=process.argv[3],read=p=>JSON.parse(p.endsWith('.gz')?gunzipSync(readFileSync(new URL(p,root))):readFileSync(new URL(p,root))),input=read(dir+'input.json'),b=input.building;
assert.equal(b.uid,'landsd/83471:0');assert.equal(b.baseSource,'terrain-estimated');assert.equal(b.structureType,'Open-sided Structure');assert(!b.modelGeometry&&!b.foundationBase);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/building-geometry.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);
const old=describeBuilding(b);assert(old.openSided&&old.parts.every(p=>p.kind==='roof'||p.kind==='post')&&old.parts.some(p=>p.kind==='post'));
if(mode==='describe'){writeFileSync(new URL(dir+'description.json',root),JSON.stringify({parts:old.parts,inputHashes:closure.inputHashes}));}
else{
 const proposal=read(dir+'proposal.json'),next={...b,foundationBase:proposal.foundationBase},d=describeBuilding(next);assert(d.foundationApplied);assert.deepEqual(d.parts.filter(p=>p.kind==='roof'),old.parts.filter(p=>p.kind==='roof'));assert.equal(d.parts.length,old.parts.length);
 for(let i=0;i<d.parts.length;i++){if(d.parts[i].kind==='post'){assert.deepEqual({...d.parts[i],bottom:old.parts[i].bottom},old.parts[i]);assert.equal(d.parts[i].bottom,proposal.foundationBase);}}
 const a=createBuildingGeometry(b),z=createBuildingGeometry(next),ap=Array.from(a.attributes.position.array),zp=Array.from(z.attributes.position.array);assert.equal(ap.length,zp.length);let changed=0;
 for(let i=0;i<ap.length;i++){if(i%3!==1)assert.equal(ap[i],zp[i]);else if(ap[i]!==zp[i]){assert(Math.abs(ap[i]-b.base)<.002);assert(Math.abs(zp[i]-proposal.foundationBase)<.002);changed++;}}
 assert(changed>0);writeFileSync(new URL(dir+'geometry.json.gz',root),gzipSync(JSON.stringify({before:{position:ap,index:Array.from({length:ap.length/3},(_,i)=>i)},after:{position:zp,index:Array.from({length:zp.length/3},(_,i)=>i)},proposal:next})));
 writeFileSync(new URL(dir+'render-proof.json',root),JSON.stringify({roofPartsExactlyUnchanged:true,allXZExactlyUnchanged:true,onlyIllustrativePostBottomVerticesChanged:true,changedYValues:changed,postCount:d.illustrativeSupports,inputHashes:closure.inputHashes,governmentGeometryChanges:0,liveChanges:false}));a.dispose();z.dispose();
}
assert(verifyModuleClosure(closure,root));
