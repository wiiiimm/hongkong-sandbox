/** Independent exact original contact diagnostic only; no runtime loader acceptance. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009/';
const raw=readFileSync(new URL(base+'exact-original-contact-inputs.json.gz',root)),inputs=JSON.parse(gunzipSync(raw));
const hash=raw=>createHash('sha256').update(raw).digest('hex'),rows=[];
for(const r of inputs.rows){assert.equal(r.index.length/3,r.triangles);assert.equal(hash(Buffer.from(new Float64Array(r.position).buffer)),r.worldTriangleSHA256);}
const support=inputs.rows.find(r=>r.uid==='landsd/295538:0'),source=inputs.rows.find(r=>r.uid==='landsd/295539:0');
const proof=verifySupportInterface(source,source.worldBounds[0][1],support);
const query=createSourceFaceQuery(source);rows.push({uid:source.uid,supportUid:support.uid,sourceSHA256:source.sourceSHA256,supportSHA256:support.sourceSHA256,interface:proof,unresolved:proof.unresolved.map(f=>({...f,originalSourceFaces:query(f.position)})),installationApproved:false,runtimeFootprintAccepted:false});
const paths=['source-scripts/city/government-import/xl-popcorn-original-pair-interface-20261009.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/triangle-point-index.mjs'];
const refs=Object.fromEntries(paths.map(p=>[p,hash(readFileSync(new URL(p,root)))]));refs[base+'exact-original-contact-inputs.json.gz']=hash(raw);
writeFileSync(new URL(base+'exact-original-interface-diagnostic.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:refs,geometryChanges:0,installationApproved:false,runtimeFootprintAccepted:false,qualification:'Independent untouched-source support diagnostic. No loader rejection suppressed or runtime gate bypassed; live load acceptance remains required.'})));
console.log(JSON.stringify({uid:source.uid,passed:proof.passed,samples:proof.samples,strictContacts:proof.strictContacts,wallIntersections:proof.wallIntersections,unresolved:proof.unresolved.length}));
