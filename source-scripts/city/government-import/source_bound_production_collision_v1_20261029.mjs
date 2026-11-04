/** Actual production collision: unchanged roofs/cell index, bounded lower deltas. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {BuildingIndex,inPolygon} from '../../../3d-viewer/city/geo.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),[inputPath,outputPath]=process.argv.slice(2),sha=b=>createHash('sha256').update(b).digest('hex'),raw=p=>readFileSync(new URL(p,root)),read=p=>JSON.parse(raw(p));
const input=read(inputPath);for(const [path,hash]of Object.entries(input.inputHashes))assert.equal(sha(raw(path)),hash);
const config=read(input.config),before=read(input.basics).rows.map(r=>r.currentBuilding),after=structuredClone(before),changes=config.privateSourceBoundTileOverlays.flatMap(o=>o.changes);
assert(config.productionBasicGeometryIntegrated&&changes.length===4&&before.length===70);
for(const change of changes){const i=after.findIndex(b=>b.uid===change.uid);assert(i>=0);assert.deepEqual(after[i],change.before);after[i]=change.after;}
const old=new BuildingIndex(before),next=new BuildingIndex(after);assert.deepEqual(next.cells,old.cells);
const volumeRows=[];
for(let i=0;i<before.length;i++){
 const a=old.volumes[i],b=next.volumes[i],change=changes.find(c=>c.uid===before[i].uid);
 assert.equal(Math.max(...a.map(v=>v.top)),Math.max(...b.map(v=>v.top)));
 if(!change){assert.deepEqual(b,a);continue;}
 const added=[];
 if(change.role==='source-bound-basic-continuation'){
  assert.deepEqual(b.slice(0,-1),a);const part=b.at(-1),core=a.find(p=>p.kind==='building');
  assert.equal(part.kind,'basic-ground-continuation');assert.deepEqual(part.rings,core.rings);assert.deepEqual(part.bounds,core.bounds);assert.equal(part.top,core.bottom);assert.equal(part.bottom,change.hint.base);assert.equal(part.windows,false);added.push(part);
 }else{
  assert.equal(change.role,'existing-estimated-open-canopy');assert.equal(a.length,b.length);
  for(let j=0;j<a.length;j++){
   if(a[j].kind==='post'){assert.deepEqual(b[j],{...a[j],bottom:change.foundationBase});assert(b[j].bottom<a[j].bottom);added.push({...b[j],top:a[j].bottom});}
   else assert.deepEqual(b[j],a[j]);
  }
  assert(added.length>0);
 }
 volumeRows.push({uid:before[i].uid,role:change.role,oldRoofAndBodyVolumesPreserved:true,exactCellMembershipUnchanged:true,roofMaximumUnchanged:true,lowerIntervals:added.map(v=>({rings:v.rings,bounds:v.bounds,bottom:v.bottom,top:v.top,windows:v.windows})),deltaSemantics:'Same existing horizontal footprint/predicate, downward interval only; unchanged production generic-volume collision method.'});
}
const report={uids:changes.map(c=>c.uid),regionalForms:before.length,unchangedRegionalForms:before.length-changes.length,volumeRows,exactCellMapUnchanged:true,allRoofMaximaUnchanged:true,probes:0,roofQueries:0,newlyBlockedProbes:0,changedFirstHitUidProbes:0,physicalAcceptance:false,collisionReviewApproved:false,installationApproved:false,publication:false};
for(const row of volumeRows){
 const boxes=row.lowerIntervals.map(v=>v.bounds),x0=Math.min(...boxes.map(b=>b[0]))-2,z0=Math.min(...boxes.map(b=>b[1]))-2,x1=Math.max(...boxes.map(b=>b[2]))+2,z1=Math.max(...boxes.map(b=>b[3]))+2;
 const heights=[...new Set(row.lowerIntervals.flatMap(v=>[v.bottom-.02,v.bottom+.02,(v.bottom+v.top)/2,v.top-.02,v.top,v.top+.02]))];
 for(let x=x0;x<=x1;x+=2.5)for(let z=z0;z<=z1;z+=2.5)for(const radius of [0,.55,2]){
  assert.equal(old.maximumRoof(x,z,radius),next.maximumRoof(x,z,radius));report.roofQueries++;
  for(const bottom of heights)for(const span of [.02,1.8]){
   const top=bottom+span,a=old.collision(x,z,bottom,top,radius),b=next.collision(x,z,bottom,top,radius);assert(!a||b,'Existing collision removed');
   if(a&&b&&a.uid!==b.uid)report.changedFirstHitUidProbes++;
   if(!a&&b){
    const changed=volumeRows.find(r=>r.uid===b.uid);assert(changed,'Unexpected actor became collidable');
    assert(changed.lowerIntervals.some(v=>bottom<v.top&&top>v.bottom),'Collision outside added lower interval');
    if(radius===0)assert(changed.lowerIntervals.some(v=>inPolygon(x,z,v.rings)),'Point collision outside exact footprint');
    report.newlyBlockedProbes++;
   }
   report.probes++;
  }
 }
}
assert(report.newlyBlockedProbes>0);
const closure=snapshotModuleClosure(new URL('3d-viewer/city/geo.js',root),root);assert(closure.completeAuditedLiteralImportClosure&&closure.computedImportsRejected);assert(verifyModuleClosure(closure,root));
for(const [path,hash]of Object.entries(input.inputHashes))assert.equal(sha(raw(path)),hash);
report.inputHashes={...input.inputHashes,...closure.inputHashes,[inputPath]:sha(raw(inputPath)),'source-scripts/city/government-import/source_bound_production_collision_v1_20261029.mjs':sha(raw('source-scripts/city/government-import/source_bound_production_collision_v1_20261029.mjs'))};
report.qualification='Actual production BuildingIndex/collisionVolumes,70forms/fourexact private overlays: all existing BASIC body/roof volumes retained, new closed-body or post intervals use only the identical original footprint below old bottoms; exact cell map and per-building roof maxima unchanged. These structural invariants preserve roof query results for every query and contain all generic-volume collision deltas in the declared lower intervals. Finite actual grid probes supplement them. Raw foreign surface contacts and first-hit UID changes at overlaps remain reported; no physical/interface/publication approval follows from this software packet.';
writeFileSync(new URL(outputPath,root),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({probes:report.probes,roofQueries:report.roofQueries,newlyBlockedProbes:report.newlyBlockedProbes,changedFirstHitUidProbes:report.changedFirstHitUidProbes}));
