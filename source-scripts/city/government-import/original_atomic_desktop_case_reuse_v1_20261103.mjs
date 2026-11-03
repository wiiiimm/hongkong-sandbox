/** Reuse one completed exact-source desktop case, never a failed whole run. */
import assert from 'node:assert/strict';
export function verifyDesktopCase(previous,catalogue,owner){
 assert(previous.diagnosticOnly&&previous.physicalAcceptance===false&&previous.installationApproved===false&&previous.publication===false);
 assert(previous.actualProductionGeometryHTTPVerified&&previous.moduleSubstitution===false);
 assert.deepEqual(previous.pageErrors,[]);assert.equal(previous.cases.length,1);
 const c=previous.cases[0],uids=catalogue.models.map(m=>m.uid).sort();
 assert.equal(c.width,1280);assert.equal(c.name,'1280-success');assert.equal(c.failedUid,null);
 assert.equal(c.sources.length,uids.length);
 for(const m of catalogue.models){const rows=c.sources.filter(r=>r.uid===m.uid);assert.equal(rows.length,1);assert.equal(rows[0].sha256,m.sha256);assert.equal(rows[0].triangles,m.triangles);assert(rows[0].active);}
 assert(c.baseOnlyRestoredCompleteGroup&&c.completeGroupEvicted);
 for(const [key,active]of [['retainedOwnerActive',true],['retainedOwnerBaseFallback',false],['retainedOwnerRecovered',true],['retainedOwnerEvictedFallback',false]]){
  const r=c[key];assert.equal(r.uid,owner.uid);assert.equal(r.sourceSHA256,owner.sha256);assert.equal(r.active,active);assert.equal(r.basicFaces>0,!active);assert.equal(r.collisionKinds.includes('model-surface'),active);if(active)assert.equal(r.originalTriangles,owner.triangles);
 }
 assert(c.audit.frames>0);assert.deepEqual(c.audit.violations,[]);
 assert(c.audit.transitions.some(t=>JSON.stringify([...t.active].sort())===JSON.stringify(uids)));
 assert.equal(c.audit.transitions.at(-1).active.length,0);
 return c;
}
