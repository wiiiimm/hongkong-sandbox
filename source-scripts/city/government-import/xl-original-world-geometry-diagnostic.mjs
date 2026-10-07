/** Decode exact frozen government meshes in the production pose. Diagnostic only. */
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
const [base,out]=process.argv.slice(2),root=new URL('../../../',import.meta.url),hashes={},sha=raw=>createHash('sha256').update(raw).digest('hex');
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&out?.startsWith('source-scripts/city/government-import/local/government-xl-')&&!out.includes('..')&&!base.includes('..'));
assert(!existsSync(new URL(out,root)));
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const selection=read(base+'/check-selection.json.gz'),contexts=read(base+'/context.json.gz');
assert.equal(selection.manifestSHA256,sha(readFileSync(new URL('3d-viewer/city/data/manifest.json',root))));
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},rows=[];
for(const row of selection.rows){
 const context=contexts.rows.find(c=>c.uid===row.uid);assert.equal(context.sourceSHA256,row.sourceSHA256);
 for(const [path,hash] of Object.entries(context.neighbourTileHashes))assert.equal(sha(readFileSync(new URL('3d-viewer/'+path,root))),hash);
 const tile=read('3d-viewer/'+row.source.tile);assert.equal(hashes['3d-viewer/'+row.source.tile],row.source.tileSHA256);assert.deepEqual(tile.buildings.find(b=>b.uid===row.uid),row.source.building);
 const raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.sourceSHA256);
 const model=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});
 try{const geometry=model.record.modelGeometry;assert(geometry.position.length&&geometry.index.length);rows.push({uid:row.uid,sourceSHA256:row.sourceSHA256,position:Array.from(geometry.position),index:Array.from(geometry.index),source:row.source});console.log(JSON.stringify({uid:row.uid,triangles:geometry.index.length/3}));}
 finally{disposeOfficialModel(model);}
}
for(const path of ['3d-viewer/city/official-model-assets.js','source-scripts/city/government-import/xl-original-world-geometry-diagnostic.mjs'])hashes[path]=sha(readFileSync(new URL(path,root)));
hashes['3d-viewer/city/data/manifest.json']=selection.manifestSHA256;
for(const [path,hash] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),hash);
mkdirSync(new URL(out.substring(0,out.lastIndexOf('/')+1),root),{recursive:true});
writeFileSync(new URL(out,root),gzipSync(JSON.stringify({rows,inputHashes:hashes,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0})));
