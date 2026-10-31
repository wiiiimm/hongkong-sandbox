/** Recheck original source pairs using exact seam geometry; diagnostic only. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifyOriginalContactSeams} from './original-contact-seams.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2];assert(doc?.startsWith('docs/astra-city/government-import/government-xl-'));
const hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function read(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return JSON.parse(path.endsWith('.gz')?gunzipSync(b):b);}
const inputs=read(doc+'inputs.json'),light={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const item of inputs.pairs){
 const pair=item.pair,loaded=[];let result;
 try{
  assert.equal(sha(readFileSync(new URL(item.path,root))),item.sha256);hashes[item.path]=item.sha256;
  for(const row of item.sources){const b=read('3d-viewer/'+row.source.tile).buildings.find(b=>b.uid===row.uid);assert.deepEqual(b,row.source.building);const raw=readFileSync(new URL(row.candidate.path,root));assert.equal(sha(raw),row.sourceSHA256);hashes[row.candidate.path]=sha(raw);loaded.push(await loadOfficialModel(row.candidate.entry,b,light,{fetcher:async()=>new Response(raw)}));}
  const source=item.sources[0],support=item.sources[1];assert.equal(source.uid,pair.uid);assert.equal(support.uid,pair.supportUid);
  const p=verifyOriginalContactSeams(loaded[0].record.modelGeometry,source.native.model.worldBounds[0][1],loaded[1].record.modelGeometry);
  result={...pair,sourceSHA256:source.sourceSHA256,supportSHA256:support.sourceSHA256,interface:p,passed:p.passed,rawPassed:p.rawInterface.passed,newlyPasses:p.passed&&!p.rawInterface.passed,installationApproved:false};
 }catch(error){result={...pair,passed:false,error:String(error.message),installationApproved:false};}
 finally{for(const asset of loaded)disposeOfficialModel(asset);}
 rows.push(result);mkdirSync(new URL(doc+'pairs/',root),{recursive:true});const name=sha(Buffer.from(JSON.stringify([pair,item.sources.map(r=>r.sourceSHA256)]))).slice(0,20);writeFileSync(new URL(doc+'pairs/'+name+'.json',root),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({done:rows.length,total:inputs.pairs.length,uid:pair.uid,supportUid:pair.supportUid,passed:result.passed,newlyPasses:result.newlyPasses,seamCorrections:result.interface?.seamCorrections,error:result.error}));
}
for(const p of ['source-scripts/city/government-import/original-contact-seam-batch.mjs','source-scripts/city/government-import/original-contact-seams.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','source-scripts/city/government-import/source-face-query.mjs','source-scripts/city/government-import/triangle-point-index.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
writeFileSync(new URL(doc+'checks.json',root),JSON.stringify({rows,inputHashes:hashes,publication:false,newlyInstalled:0,modelGeometryChanges:0},null,2)+'\n');
