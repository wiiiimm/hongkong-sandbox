/** Three pinned HSBC originals; diagnostic intersections only, no acceptance. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {diagnoseOriginalWallOverlap} from './original-wall-overlap-diagnostic.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-hsbc-original-wall-overlap-diagnostic-20261008/',hashes={};
const hash=b=>createHash('sha256').update(b).digest('hex');
const read=p=>{const raw=readFileSync(new URL(p,root));hashes[p]=hash(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);};
assert(!existsSync(new URL(base+'interfaces.json',root)));mkdirSync(new URL(base,root),{recursive:true});
const rows=read('docs/astra-city/government-import/government-xl-hsbc-centre-supports-20261005/selection.json.gz').rows;
rows.push(read('docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/physical-selection.json.gz').rows.find(r=>r.uid==='landsd/265848:0'));
assert.equal(rows.length,3);
const manifest=read('3d-viewer/city/data/manifest.json'),current=new Map();
for(const tile of manifest.tiles){if(!tile.url.endsWith('/0_-2.json'))continue;const data=read('3d-viewer/'+tile.url);for(const b of data.buildings)current.set(b.uid,b);}
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=new Map();
try{
 for(const row of rows){const building=current.get(row.uid);assert.deepEqual(building,row.source.building,'Current form changed');const raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=hash(raw);assert.equal(hash(raw),row.sourceSHA256);
  loaded.set(row.uid,await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},building,lighting,{fetcher:async()=>new Response(raw)}));}
 const support=loaded.get('landsd/265848:0'),results=[];
 for(const row of rows.filter(r=>r.uid!=='landsd/265848:0')){const source=loaded.get(row.uid),diagnostic=diagnoseOriginalWallOverlap(source.record.modelGeometry,row.native.model.worldBounds[0][1],support.record.modelGeometry);
  results.push({uid:row.uid,sourceSHA256:row.sourceSHA256,supportUid:'landsd/265848:0',supportSHA256:rows.find(r=>r.uid==='landsd/265848:0').sourceSHA256,diagnostic});}
 for(const p of ['source-scripts/city/government-import/run-original-wall-overlap-diagnostic.mjs','source-scripts/city/government-import/original-wall-overlap-diagnostic.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/triangle-point-index.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=hash(readFileSync(new URL(p,root)));
 writeFileSync(new URL(base+'interfaces.json',root),JSON.stringify({rows:results,inputHashes:hashes,newlyInstalled:0,publication:false,modelGeometryChanges:0,installationApproved:false},null,2)+'\n');
 console.log(JSON.stringify(results.map(r=>({uid:r.uid,samples:r.diagnostic.samples,strictContacts:r.diagnostic.strictContacts,wallIntersections:r.diagnostic.wallIntersections,unresolved:r.diagnostic.unresolved.length,geometricIntersectionsComplete:r.diagnostic.geometricIntersectionsComplete,acceptanceGranted:false}))));
}finally{for(const model of loaded.values())disposeOfficialModel(model);}
