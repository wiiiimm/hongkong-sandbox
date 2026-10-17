/** Inspect every original support layer at unresolved samples; no acceptance changes. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {supportSurface} from './support-contact.mjs';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),base=process.argv[2],hashes={};
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const inputs=read(base+'diagnostic-inputs.json'),sources=new Map(inputs.sources.map(r=>[r.uid,r]));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
async function get(uid){if(loaded.has(uid))return loaded.get(uid);const row=sources.get(uid),raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.sourceSHA256);assert.equal(sha(raw),row.candidate.entry.sha256);const asset=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});loaded.set(uid,asset);return asset;}
const rows=[];
try{for(const pair of inputs.pairs){const source=await get(pair.uid),support=await get(pair.supportUid),g=source.record.modelGeometry,s=support.record.modelGeometry;
 const previous=read(pair.previousChecks).rows.find(r=>r.uid===pair.uid&&r.supportUid===pair.supportUid);assert(previous);
 const proof=verifySupportInterface(g,sources.get(pair.uid).candidate.entry.worldBounds[0][1],s);assert.deepEqual(proof,previous.interface);
 const surface=supportSurface(s),points=proof.unresolved.map(f=>{const hits=surface.intersectionDetails(f.position[0],f.position[2]),contact=hits.filter(h=>{const gap=f.position[1]-h.height;return gap>=proof.strictLowRim.minimumGap&&gap<=proof.strictLowRim.maximumGap;});return {...f,originalSupportFaces:hits,contactFaces:contact,classification:contact.length?'contact-layer-with-higher-overlap':hits.length?'no-layer-in-contact-interval':'no-vertical-support'};});
 const counts=points.reduce((a,r)=>(a[r.classification]=(a[r.classification]||0)+1,a),{});const row={...pair,sourceSHA256:sources.get(pair.uid).sourceSHA256,supportSHA256:sources.get(pair.supportUid).sourceSHA256,existingInterfacePassed:proof.passed,unresolvedSamples:points.length,counts,points};rows.push(row);console.log(JSON.stringify({uid:pair.uid,unresolved:points.length,counts}));
}}finally{for(const m of loaded.values())disposeOfficialModel(m);}
for(const path of ['source-scripts/city/government-import/original-support-layer-diagnostic.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/support-interface.mjs','3d-viewer/city/official-model-assets.js'])hashes[path]=sha(readFileSync(new URL(path,root)));
for(const [path,pinned] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),pinned);
writeFileSync(new URL(base+'layer-checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,scriptExternalAICalls:0,modelGeometryChanges:0,publication:false,qualification:'All exact original support facets at unresolved contact samples. Historical strict interface reproduced unchanged. Additional layers are diagnostics only; no acceptance, geometry edits or progress credit.'})));
