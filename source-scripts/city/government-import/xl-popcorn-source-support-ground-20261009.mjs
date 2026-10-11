/** Full original mall low-rim ground contact diagnostic; no source role waiver. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {lowRimSamples,supportSurface,measureSupport} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009/';
const raw=readFileSync(new URL(base+'exact-original-mall-ground-contact-inputs.json.gz',root)),inp=JSON.parse(gunzipSync(raw));
const hash=x=>createHash('sha256').update(x).digest('hex');
for(const r of [inp.source,inp.terrain])assert.equal(hash(Buffer.from(new Float64Array(r.position).buffer)),r.worldTriangleSHA256);
const rim=lowRimSamples(inp.source,inp.source.worldBounds[0][1]),proof=measureSupport(rim,supportSurface(inp.terrain));
const result={uid:inp.source.uid,sourceSHA256:inp.source.sourceSHA256,sourceWorldTriangleSHA256:inp.source.worldTriangleSHA256,terrainWorldTriangleSHA256:inp.terrain.worldTriangleSHA256,inputSHA256:hash(raw),wholeOriginalLowRim:proof,physicalSupportAccepted:false,installationApproved:false,geometryChanges:0};
writeFileSync(new URL(base+'whole-original-mall-ground-contact.json.gz',root),gzipSync(JSON.stringify(result)));
console.log(JSON.stringify({samples:proof.samples,contacts:proof.contacts,failed:proof.failed.length,minGap:proof.minGap,maxGap:proof.maxGap}));
