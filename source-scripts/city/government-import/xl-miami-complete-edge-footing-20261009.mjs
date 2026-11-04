/** Complete unchanged original podium component versus full source TIN; no graph credit. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-miami-complete-edge-footing-20261009/';
const bytes=readFileSync(new URL(base+'complete-reached-original-podium-footing-inputs.json.gz',root)),input=JSON.parse(gunzipSync(bytes)),hash=b=>createHash('sha256').update(b).digest('hex');
assert.equal(hash(Buffer.from(new Float64Array(input.terrain.position).buffer)),input.terrain.worldTriangleSHA256);
const rows=input.reachedComponents.map(p=>{const ground=verifySupportInterface(p,p.bottomHKPD,input.terrain),strict=ground.passed&&ground.strictContacts===ground.samples&&ground.wallIntersections===0&&ground.strictLowRim.minGap<=.1;
 console.log(JSON.stringify({component:p.component,faces:p.originalFaceIds.length,samples:ground.samples,contacts:ground.strictContacts,wallIntersections:ground.wallIntersections,missing:ground.strictLowRim.missing,minGap:ground.strictLowRim.minGap,maxGap:ground.strictLowRim.maxGap,strictOriginalGroundAnchor:strict}));
 return {component:p.component,originalFaceIds:p.originalFaceIds,worldBounds:p.worldBounds,closedConsistentlyWound:p.closedConsistentlyWound,ground,strictOriginalGroundAnchor:strict};});
writeFileSync(new URL(base+'complete-reached-original-podium-footing-interfaces.json.gz',root),gzipSync(JSON.stringify({uid:input.uid,sourceSHA256:input.sourceSHA256,worldTriangleSHA256:input.worldTriangleSHA256,rows,inputSHA256:hash(bytes),physicalSupportAccepted:false,sourceGeometryChanges:0,qualification:'Independent complete low-rim replay for every reached original podium edge component against the entire pinned source TIN. Strict ground anchors require all sampled contacts, no wall fallback, and a real <=0.1m nearest footing contact. Other exact paths, complete original-face clearance and full current runtime gates remain independent.'})));
