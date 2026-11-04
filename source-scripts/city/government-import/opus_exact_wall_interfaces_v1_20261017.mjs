/** Existing same-triangle original wall contact rule, unchanged tolerances. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),dir=process.argv[2],hashes={};
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=createHash('sha256').update(raw).digest('hex');return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const input=read(dir+'input.json'),actor=read(input.actorsPath),rows=read(input.geometryPath).rows;
const podium=rows.find(r=>r.uid==='landsd/248432:0'),targets=[actor,rows.find(r=>r.uid==='landsd/322573:0')];assert(podium&&targets.every(Boolean));
const results=targets.map(g=>{let bottom=Infinity;for(const i of g.index)bottom=Math.min(bottom,g.position[i*3+1]);const proof=verifySupportInterface(g,bottom,podium);const query=createSourceFaceQuery(g);return {uid:g.uid,bottom,proof,unresolved:proof.unresolved.map(f=>({...f,sourceFaces:query(f.position)}))};});
for(const p of ['source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/triangle-point-index.mjs','source-scripts/city/government-import/source-face-query.mjs'])hashes[p]=createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex');
for(const [p,h]of Object.entries(hashes))assert.equal(createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex'),h);
writeFileSync(new URL(dir+'interfaces.json.gz',root),gzipSync(JSON.stringify({rows:results,inputHashes:hashes})));
const summary={rows:results.map(r=>({uid:r.uid,samples:r.proof.samples,strictContacts:r.proof.strictContacts,wallIntersections:r.proof.wallIntersections,unresolved:r.proof.unresolved.length,passed:r.proof.passed})),fullAcceptance:false,modelGeometryChanges:0};
writeFileSync(new URL(dir+'summary.json',root),JSON.stringify(summary));console.log(JSON.stringify(summary));
