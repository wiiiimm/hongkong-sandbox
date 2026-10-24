/** ROOT-only current BASIC→exact original podium interface; no waiver. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {verifySupportInterface} from './support-interface.mjs';
import {lowRimSamples,supportSurface,measureSupport,inspectSupportLayers} from './support-contact.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
assert(doc?.startsWith('docs/astra-city/government-import/government-xl-')&&doc.endsWith('/')&&!doc.includes('..'));
function read(q){const b=readFileSync(new URL(q.path,root));hashes[q.path]=sha(b);assert.equal(hashes[q.path],q.sha256);return JSON.parse(q.path.endsWith('.gz')?gunzipSync(b):b);}
const input=JSON.parse(readFileSync(new URL(doc+'input.json',root))),basic=read(input.actualBasicConstructor).row,runtime=read(input.actualOriginalRuntime),prior=read(input.actualBasicFinite),physical=read(input.actualPhysicalSupport);
assert.equal(basic.uid,'landsd/338946:0');assert.equal(prior.uid,basic.uid);assert.equal(prior.completeFaces,basic.index.length/3);assert.equal(prior.currentClearCandidateUnproved.length,0);
const podium=runtime.rows.find(r=>r.uid==='landsd/12728:0');assert(podium);assert.equal(podium.index.length/3,1655);assert.equal(input.sourceSHA256,podium.sourceSHA256);
const bottom=basic.currentForm.base+(basic.currentForm.minimum||0),g={position:basic.position,index:basic.index},support={position:podium.position,index:podium.index};
const surface=supportSurface(support),rim=lowRimSamples(g,bottom),measured=measureSupport(rim,surface),proof=verifySupportInterface(g,bottom,support);
assert.deepEqual(measured,proof.strictLowRim);assert(rim.length>0);const query=createSourceFaceQuery(g);
const strict=proof.passed&&proof.samples>0&&proof.strictContacts===proof.samples&&proof.wallIntersections===0&&proof.unresolved.length===0;
const failures=proof.unresolved.map(f=>({...f,actualBasicIncidentFaces:query(f.position),allOriginalPodiumFaceHits:surface.intersectionDetails(f.position[0],f.position[2])}));
const bytes=Buffer.alloc(basic.index.length*24);let at=0;for(const vertex of basic.index)for(let axis=0;axis<3;axis++){bytes.writeDoubleLE(basic.position[vertex*3+axis],at);at+=8;}assert.equal(sha(bytes),prior.completeWorldSHA256);
const original=physical.rows[0];assert.equal(original.interface.strictContacts,97);assert.equal(original.interface.samples,138);assert.equal(original.unresolved.length,41);
for(const p of ['source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/triangle-point-index.mjs','source-scripts/city/government-import/upton_basic338946_original12728_support_v1_20261014.mjs'])hashes[p]=sha(readFileSync(new URL(p,root)));
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const output=doc+'actual-BASIC338946-original12728-support.json.gz';assert(!existsSync(new URL(output,root)));
writeFileSync(new URL(output,root),gzipSync(JSON.stringify({uid:basic.uid,supportUid:podium.uid,supportSourceSHA256:input.sourceSHA256,actualBasicWholeWorldSHA256:prior.completeWorldSHA256,completeActualBasicFaces:prior.completeFaces,completeActualOriginalPodiumFaces:1655,interface:proof,strictCompleteBasicInterfacePassed:strict,unresolved:failures,layerDiagnostics:inspectSupportLayers(rim,surface),originalTowerInterfaceVerbatim:original,originalTower41NeverResolved:true,native50PercentRuleNotApplied:true,inputHashes:hashes,sourceGeometryChanges:0,terrainGeometryChanges:0,physicalAccepted:false,installationApproved:false})));
console.log(JSON.stringify({basicSamples:proof.samples,strictContacts:proof.strictContacts,wallIntersections:proof.wallIntersections,unresolved:proof.unresolved.length,strictCompleteBasicInterfacePassed:strict,originalTowerStillHeld:true}));
