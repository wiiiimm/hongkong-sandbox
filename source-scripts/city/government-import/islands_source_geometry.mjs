/** Full unchanged source arrays from the actual production loader; diagnostic only. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,existsSync,mkdirSync} from 'node:fs';
import {dirname,resolve} from 'node:path';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';

const root=resolve(new URL('../../../',import.meta.url).pathname),[selectionPath,outputPath]=process.argv.slice(2);
const sha=raw=>createHash('sha256').update(raw).digest('hex'),hashes={};
const path=relative=>{const p=resolve(root,relative);assert.ok(p.startsWith(root+'/'),'repository-relative input');return p;};
function bytes(relative){const raw=readFileSync(path(relative));hashes[relative]=sha(raw);return raw;}
function read(relative){const raw=bytes(relative);return JSON.parse(relative.endsWith('.gz')?gunzipSync(raw):raw);}
assert.ok(selectionPath && outputPath?.startsWith('source-scripts/city/government-import/local/'));
assert.ok(!existsSync(path(outputPath)),'fresh diagnostic output required');
const selection=read(selectionPath),seen=new Set(),rows=[],tiles=new Map();
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
for(const row of selection.rows){
  assert.ok(!seen.has(row.uid));seen.add(row.uid);
  const tilePath='3d-viewer/'+row.source.tile;
  if(!tiles.has(tilePath))tiles.set(tilePath,read(tilePath));
  assert.equal(hashes[tilePath],row.source.tileSHA256);
  assert.deepEqual(tiles.get(tilePath).buildings.find(b=>b.uid===row.uid),row.source.building);
  const raw=bytes(row.candidate.path),expected=row.sourceSHA256??row.candidate.entry.sha256;
  assert.equal(sha(raw),expected);assert.equal(row.candidate.entry.sha256,expected);
  const model=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});
  try{
    const geometry=model.record.modelGeometry;
    assert.ok(geometry.position.length && geometry.index.length);
    rows.push({uid:row.uid,sourceSHA256:expected,position:Array.from(geometry.position),index:Array.from(geometry.index)});
  }finally{disposeOfficialModel(model);}
  if(rows.length%100===0)console.log(JSON.stringify({decoded:rows.length,total:selection.rows.length}));
}
for(const relative of ['3d-viewer/city/official-model-assets.js','3d-viewer/city/model-byte-cache.js',
  '3d-viewer/vendor/three.module.js','source-scripts/city/government-import/islands_source_geometry.mjs'])bytes(relative);
for(const [relative,hash]of Object.entries(hashes))assert.equal(sha(readFileSync(path(relative))),hash);
mkdirSync(dirname(path(outputPath)),{recursive:true});
writeFileSync(path(outputPath),gzipSync(JSON.stringify({rows,inputHashes:hashes,diagnosticOnly:true,
  publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0}),{mtime:0}),{flag:'wx'});
console.log(JSON.stringify({decoded:rows.length,complete:true,publication:false}));
