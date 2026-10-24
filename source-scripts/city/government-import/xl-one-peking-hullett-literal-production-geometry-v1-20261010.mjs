/** Read-only complete production-loader geometry. Historical context; no approval. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
const root=new URL('../../../',import.meta.url);
const base='docs/astra-city/government-import/government-xl-one-peking-hullett-literal-production-geometry-v1-20261010/';
const contextPath='docs/astra-city/government-import/government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010/diagnostic.json.gz';
const sha=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function read(p){const b=readFileSync(new URL(p,root));hashes[p]=sha(b);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
assert(!existsSync(new URL(base+'diagnostic.json.gz',root)));mkdirSync(new URL(base,root),{recursive:true});
const context=read(contextPath),lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const row of context.sources){
 let model;
 try{
  const raw=readFileSync(new URL(row.source.path,root));hashes[row.source.path]=sha(raw);assert.equal(sha(raw),row.source.sha256);
  const form=context.completeCurrentForms.find(x=>x.building.uid===row.uid);assert(form);
  const entry=row.entry??row.metadata.candidate.entry;
  model=await loadOfficialModel({...entry,assetURL:'https://diagnostic.invalid/unchanged-original.glb.gz'},form.building,lighting,{fetcher:async()=>new Response(raw)});
  const g=model.record.modelGeometry;assert.equal(g.index.length/3,row.completeFaces);
  const position=Array.from(g.position),index=Array.from(g.index);assert(position.every(Number.isFinite));
  assert(index.every(i=>Number.isInteger(i)&&i>=0&&i<position.length/3));
  rows.push({uid:row.uid,sourceSHA256:sha(raw),loaderPassed:true,completeFaces:g.index.length/3,position,index,positionConstructor:g.position.constructor.name,indexConstructor:g.index.constructor.name});
 }catch(error){rows.push({uid:row.uid,sourceSHA256:row.source.sha256,loaderPassed:false,error:String(error),stack:error.stack});}
 finally{if(model)disposeOfficialModel(model);}
}
for(const p of ['source-scripts/city/government-import/xl-one-peking-hullett-literal-production-geometry-v1-20261010.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
const result={rows,inputHashes:hashes,historicalManifestSHA256:context.capturedManifestSHA256,currentManifestAcceptanceClaimed:false,identityAccepted:false,physicalAccepted:false,collisionExemption:false,newlyInstalled:0,publication:false,modelGeometryChanges:0,qualification:'All source faces exported through unchanged strict production loader. Per-source exceptions retained; source-only historical context, not current acceptance.'};
writeFileSync(new URL(base+'diagnostic.json.gz',root),gzipSync(JSON.stringify(result)));
console.log(JSON.stringify({rows:rows.map(({uid,loaderPassed,completeFaces,error})=>({uid,loaderPassed,completeFaces,error}))}));
