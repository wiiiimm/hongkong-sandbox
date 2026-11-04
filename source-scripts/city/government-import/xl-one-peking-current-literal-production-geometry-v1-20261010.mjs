/** Fresh read-only production-loader replay; complete dependency/source pins. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2];
assert(/^docs\/astra-city\/government-import\/government-xl-one-peking-current-bound-installed-foreign-inputs-v[0-9]+-20261010$/.test(doc));
const sha=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function bytes(path){const b=readFileSync(new URL(path,root));hashes[path]=sha(b);return b;}
const loaderModuleClosure=snapshotModuleClosure(import.meta.url,root);Object.assign(hashes,loaderModuleClosure.inputHashes);
const input=JSON.parse(gunzipSync(bytes(doc+'/literal-source-inputs.json.gz')));
assert(!existsSync(new URL(doc+'/literal-production-geometry.json.gz',root)));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const role of ['own','foreign']){
 const entry=input[role+'Entry'],building=input[role+'Building'],path=input[role+'Path'],raw=bytes(path);assert.equal(sha(raw),entry.sha256);
 let model;
 try{
  model=await loadOfficialModel({...entry,assetURL:'https://diagnostic.invalid/unchanged-original.glb.gz'},building,lighting,{fetcher:async()=>new Response(raw)});
  const g=model.record.modelGeometry;assert.equal(g.index.length/3,entry.triangles);
  rows.push({uid:entry.uid,sourceSHA256:sha(raw),loaderPassed:true,completeFaces:g.index.length/3,position:Array.from(g.position),index:Array.from(g.index)});
 }finally{if(model)disposeOfficialModel(model);}
}
for(const [path,pin] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),pin,'Loader/source/input changed during literal replay: '+path);
assert(verifyModuleClosure(loaderModuleClosure,root));
writeFileSync(new URL(doc+'/literal-production-geometry.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,completeProductionLoaderDependencyClosure:true,loaderModuleClosure,loaderModules:loaderModuleClosure.modules.length,unsupportedDynamicImports:0,startAndEndInputHashesVerified:true,modelGeometryChanges:0,publication:false,newlyInstalled:0})));
console.log(JSON.stringify({rows:rows.map(r=>({uid:r.uid,completeFaces:r.completeFaces})),dependencies:Object.keys(hashes).length}));
