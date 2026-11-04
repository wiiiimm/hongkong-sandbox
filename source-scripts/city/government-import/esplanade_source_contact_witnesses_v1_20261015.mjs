/** Preserve actual production rim contacts and their incident source faces. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {lowRimSamples,supportSurface,measureSupport} from './support-contact.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),out='docs/astra-city/government-import/government-xl-esplanade-source-roles-v1-20261015/',hashes={};
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=createHash('sha256').update(raw).digest('hex');return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const data=read('source-scripts/city/government-import/local/government-xl-esplanade-pair-current-physical-v3-20261015/runtime-geometry.json.gz');
const tower=data.rows.find(r=>r.uid==='landsd/268828:0'),podium=data.rows.find(r=>r.uid==='landsd/309385:0');
const previous=read('docs/astra-city/government-import/government-xl-esplanade-original-support-ground-v1-20261015/support-checks.json.gz').rows[0];
const bottom=Math.min(...tower.position.filter((_,i)=>i%3===1)),rim=lowRimSamples(tower,bottom),surface=supportSurface(podium),strict=measureSupport(rim,surface);
assert.deepEqual(strict,previous.interface.strictLowRim);
const query=createSourceFaceQuery(tower),contacts=[];
for(const position of rim){const height=surface.height(position[0],position[2]);if(height===null)continue;const gap=position[1]-height;if(gap>=strict.minimumGap&&gap<=strict.maximumGap)contacts.push({position,height,gap,sourceFaces:query(position)});}
assert.equal(contacts.length,strict.contacts);
for(const p of ['source-scripts/city/government-import/esplanade_source_contact_witnesses_v1_20261015.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/source-face-query.mjs'])hashes[p]=createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex');
mkdirSync(new URL(out,root),{recursive:true});writeFileSync(new URL(out+'tower-contact-witnesses.json',root),JSON.stringify({contacts,inputHashes:hashes,installationApproved:false,qualification:'Existing production low-rim contact interval; face incidence uses the existing source-face query tolerance. This is not an exact positive-dimensional contact or structural-support certificate.'}));
console.log(JSON.stringify({samples:rim.length,contacts:contacts.length}));
