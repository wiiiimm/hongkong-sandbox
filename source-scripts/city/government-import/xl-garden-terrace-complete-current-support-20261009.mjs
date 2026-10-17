/** Complete original connected-component support census; diagnostic only. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
import {inspectSupportLayers,lowRimSamples,supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),base='docs/astra-city/government-import/government-xl-garden-terrace-complete-current-support-20261009/';
const inputPath='docs/astra-city/government-import/government-xl-garden-terrace-complete-original-physical-v2-20261009/selection.json.gz';
const hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
assert(!existsSync(new URL(base+'diagnostic.json.gz',root)));mkdirSync(new URL(base,root),{recursive:true});
const input=read(inputPath),lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},loaded=[];
async function load(uid){const row=input.rows.find(r=>r.uid===uid);assert(row);const raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.sourceSHA256);const model=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/original.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});loaded.push(model);return model.record.modelGeometry;}
try{
 const source=await load('landsd/21894:0'),podium=await load('landsd/162285:0'),ground=read('source-scripts/city/government-import/local/government-xl-garden-terrace-complete-original-physical-v2-20261009/runtime-geometry.json.gz').rows.flatMap(r=>r.drawnGroundGeometry);
 const support={position:Float64Array.from([...podium.position,...ground]),index:Uint32Array.from([...podium.index,...Array.from({length:ground.length/3},(_,i)=>i+podium.position.length/3)])},faceCount=source.index.length/3;
 assert.equal(faceCount,10670);const parent=Array.from({length:faceCount},(_,i)=>i),edges=new Map();
 function find(i){while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;}
 const vertex=i=>Array.from(source.position.slice(i*3,i*3+3)),key=i=>JSON.stringify(vertex(i));
 for(let f=0;f<faceCount;f++){const ids=Array.from(source.index.slice(f*3,f*3+3));for(let k=0;k<3;k++){const edge=[key(ids[k]),key(ids[(k+1)%3])].sort().join('|');if(edges.has(edge))parent[find(f)]=find(edges.get(edge));else edges.set(edge,f);}}
 const groups=new Map();for(let f=0;f<faceCount;f++){const p=find(f);if(!groups.has(p))groups.set(p,[]);groups.get(p).push(f);}
 assert.equal([...groups.values()].flat().length,faceCount);const surface=supportSurface(support),rows=[];
 for(const faces of groups.values()){
  const index=Uint32Array.from(faces.flatMap(f=>Array.from(source.index.slice(f*3,f*3+3)))),g={position:source.position,index};
  const bounds=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]];
  for(const id of new Set(index)){const p=vertex(id);for(let k=0;k<3;k++){bounds[0][k]=Math.min(bounds[0][k],p[k]);bounds[1][k]=Math.max(bounds[1][k],p[k]);}}
  const rim=lowRimSamples(g,bounds[0][1]),interfaceProof=verifySupportInterface(g,bounds[0][1],support);
  rows.push({triangles:faces.length,originalRuntimeFaces:faces,bounds,interface:interfaceProof,layers:inspectSupportLayers(rim,surface)});
 }
 rows.sort((a,b)=>a.bounds[0][1]-b.bounds[0][1]||b.triangles-a.triangles);
 for(const p of ['source-scripts/city/government-import/xl-garden-terrace-complete-current-support-20261009.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
 const result={uid:'landsd/21894:0',supportUid:'landsd/162285:0',supportScope:'Original podium plus fresh complete pair drawn nested ground; every component retains missing-ground counts',rows,inputHashes:hashes,sourceTriangles:faceCount,completeFaceAccounting:true,newlyInstalled:0,publication:false,modelGeometryChanges:0,qualification:'Every original connected component independently checked against exact original podium using unchanged strict interface and support-layer diagnostics. Roof attachments are not expected to be ground-supported; these raw results do not classify roles, omit failed parts or approve installation.'};
 writeFileSync(new URL(base+'diagnostic.json.gz',root),gzipSync(JSON.stringify(result)));
 console.log(JSON.stringify({components:rows.length,rows:rows.slice(0,1).map(r=>({triangles:r.triangles,minY:r.bounds[0][1],passed:r.interface.passed,samples:r.interface.samples,contacts:r.interface.strictContacts,wall:r.interface.wallIntersections,unresolved:r.interface.unresolved.length,layerExplanations:r.layers.rows.filter(x=>x.classification==='contact-layer-with-higher-overlap').length}))}));
}finally{for(const m of loaded)disposeOfficialModel(m);}
