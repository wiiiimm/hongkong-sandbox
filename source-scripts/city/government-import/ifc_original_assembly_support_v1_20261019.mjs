/** Exact original IFC support comparison; diagnostic only, no publication. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={};
assert(doc?.startsWith('docs/astra-city/government-import/')&&doc.endsWith('/')&&!doc.includes('..'));
const sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=sha(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const inputs=read(doc+'input.json'),models=new Map();
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
try{
 for(const r of inputs.sources){const raw=readFileSync(new URL(r.candidate.path,root));assert.equal(sha(raw),r.candidate.entry.sha256);hashes[r.candidate.path]=sha(raw);models.set(r.uid,await loadOfficialModel({...r.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},r.source.building,lighting,{fetcher:async()=>new Response(raw)}));}
 assert.deepEqual([...models.keys()].sort(),['landsd/161250:0','landsd/232441:0','landsd/64856:0']);
 const tower=models.get('landsd/161250:0').record.modelGeometry,podium=models.get('landsd/232441:0').record.modelGeometry,mall=models.get('landsd/64856:0').record.modelGeometry;
 const combined={position:[...podium.position,...mall.position],index:[...podium.index,...Array.from(mall.index,i=>i+podium.position.length/3)]};
 const bottom=inputs.sources.find(r=>r.uid==='landsd/161250:0').candidate.entry.worldBounds[0][1],rows=[];
 for(const [name,geometry]of [['installed-podium',podium],['proposed-mall',mall],['combined-originals',combined]]){const proof=verifySupportInterface(tower,bottom,geometry);rows.push({name,interface:proof});console.log(JSON.stringify({name,passed:proof.passed,samples:proof.samples,strictContacts:proof.strictContacts,wallIntersections:proof.wallIntersections,unresolved:proof.unresolved.length}));}
 for(const path of ['source-scripts/city/government-import/ifc_original_assembly_support_v1_20261019.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js'])hashes[path]=sha(readFileSync(new URL(path,root)));
 writeFileSync(new URL(doc+'support-checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,sourceGeometryChanges:0,installationApproved:false})));
}finally{for(const model of models.values())disposeOfficialModel(model);}
