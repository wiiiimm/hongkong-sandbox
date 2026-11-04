/** ROOT-only41 saved failure layers. Highest-source guard remains unchanged. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {supportSurface,inspectSupportLayers} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/government-xl-')&&doc.endsWith('/')&&!doc.includes('..'));
function read(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'input.json'),saved=read(input.actualSupportChecks.path);assert.equal(hashes[input.actualSupportChecks.path],input.actualSupportChecks.sha256);
const runtime=read(input.actualRuntimeGeometry.path);assert.equal(hashes[input.actualRuntimeGeometry.path],input.actualRuntimeGeometry.sha256);
const support=saved.rows[0];assert.equal(support.uid,'landsd/338946:0');assert.equal(support.supportUid,'landsd/12728:0');assert.equal(support.unresolved.length,41);assert.equal(support.interface.strictContacts,97);assert.equal(support.interface.samples,138);
const podium=runtime.rows.find(r=>r.uid===support.supportUid),tower=runtime.rows.find(r=>r.uid===support.uid);assert(podium&&tower);
const surface=supportSurface({position:podium.position,index:podium.index});
const diagnostic=inspectSupportLayers(support.unresolved.map(r=>r.position),surface);
assert.equal(diagnostic.conservative.contacts,0);assert.equal(diagnostic.rows.length,41);
const rows=diagnostic.rows.map((r,i)=>{const old=support.unresolved[i];assert.deepEqual(r.position,old.position);assert.equal(r.reason,old.reason);assert.equal(r.gap,old.gap);return {...r,originalFailureVerbatim:old,completeActualSupportFaceHits:surface.intersectionDetails(r.position[0],r.position[2]),highestSurfaceFailureRetained:true,sourceRoleOrContactAccepted:false};});
for(const p of ['source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/upton_tower41_actual_support_layers_v1_20261014.mjs'])hashes[p]=sha(readFileSync(new URL(p,root)));
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const output=doc+'actual41-highest-and-all-source-layers.json.gz';assert(!existsSync(new URL(output,root)));writeFileSync(new URL(output,root),gzipSync(JSON.stringify({rows,inputHashes:hashes,actualHighestSourceGuardUnchanged:true,sourceGeometryChanges:0,sourceRoleAccepted:false,physicalAccepted:false,installationApproved:false})));
console.log(JSON.stringify({rows:41,highestFailuresRetained:true,classifications:rows.reduce((a,r)=>(a[r.classification]=(a[r.classification]||0)+1,a),{})}));
