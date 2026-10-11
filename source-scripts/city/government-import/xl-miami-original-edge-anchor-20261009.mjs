/** Every exact source-edge component versus separately pinned original podium/TIN. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-miami-original-edge-anchor-20261009/';
const bytes=readFileSync(new URL(base+'complete-edge-anchor-inputs.json.gz',root)),input=JSON.parse(gunzipSync(bytes)),hash=b=>createHash('sha256').update(b).digest('hex');
for(const r of [input.podium,input.terrain])assert.equal(hash(Buffer.from(new Float64Array(r.position).buffer)),r.worldTriangleSHA256);
const rows=[];
for(const r of input.rows){const components=[];
 for(const p of r.parts){const podium=verifySupportInterface(p,p.bottomHKPD,input.podium),ground=verifySupportInterface(p,p.bottomHKPD,input.terrain);const strict=q=>q.passed&&q.strictContacts===q.samples&&q.wallIntersections===0&&q.strictLowRim.minGap<=.1;
 components.push({component:p.component,originalFaceIds:p.originalFaceIds,worldBounds:p.worldBounds,podium,ground,strictOriginalPodiumAnchor:strict(podium),strictOriginalGroundAnchor:strict(ground)});}
 rows.push({uid:r.uid,sourceSHA256:r.sourceSHA256,worldTriangleSHA256:r.worldTriangleSHA256,wholeOriginalFaces:r.wholeOriginalFaces,components,physicalAccepted:false,sourceGeometryChanges:0});console.log(JSON.stringify({uid:r.uid,edgeComponents:components.length,strictPodiumAnchors:components.filter(p=>p.strictOriginalPodiumAnchor).length,strictGroundAnchors:components.filter(p=>p.strictOriginalGroundAnchor).length}));}
writeFileSync(new URL(base+'complete-edge-anchor-interfaces.json.gz',root),gzipSync(JSON.stringify({rows,inputSHA256:hash(bytes),physicalAccepted:false,sourceGeometryChanges:0})));
