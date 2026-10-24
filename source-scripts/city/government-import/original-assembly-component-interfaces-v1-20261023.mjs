/** Complete runtime component support census; diagnostics never grant approval. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {verifySupportInterface} from './support-interface.mjs';
import {lowRimSamples,inspectSupportLayers,supportSurface} from './support-contact.mjs';
const root=new URL('../../../',import.meta.url),base=process.argv[2],hashes={};
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
const sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const raw=readFileSync(new URL(p,root));hashes[p]=sha(raw);return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
const inputs=read(base+'support-inputs.json'),sources=new Map(inputs.sources.map(r=>[r.uid,r])),loaded=new Map();
const lighting={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
async function load(uid){
 if(loaded.has(uid))return loaded.get(uid).record.modelGeometry;
 const row=sources.get(uid),raw=readFileSync(new URL(row.candidate.path,root));hashes[row.candidate.path]=sha(raw);assert.equal(sha(raw),row.sourceSHA256);
 const model=await loadOfficialModel({...row.candidate.entry,assetURL:'https://diagnostic.invalid/original.glb.gz'},row.source.building,lighting,{fetcher:async()=>new Response(raw)});
 loaded.set(uid,model);return model.record.modelGeometry;
}
const rows=[];
try{
 for(const pair of inputs.pairs){
  const source=await load(pair.uid),support=await load(pair.supportUid),count=source.index.length/3;
  assert.equal(count,sources.get(pair.uid).triangles);
  const parent=Array.from({length:count},(_,i)=>i),edges=new Map();
  function find(i){while(parent[i]!==i){parent[i]=parent[parent[i]];i=parent[i];}return i;}
  const vertex=i=>Array.from(source.position.slice(i*3,i*3+3));
  for(let f=0;f<count;f++){
   const ids=Array.from(source.index.slice(f*3,f*3+3));
   for(let k=0;k<3;k++){
    const edge=[JSON.stringify(vertex(ids[k])),JSON.stringify(vertex(ids[(k+1)%3]))].sort().join('|');
    if(edges.has(edge))parent[find(f)]=find(edges.get(edge));else edges.set(edge,f);
   }
  }
  const groups=new Map();for(let f=0;f<count;f++){const id=find(f);if(!groups.has(id))groups.set(id,[]);groups.get(id).push(f);}
  const surface=supportSurface(support),components=[];
  for(const faces of groups.values()){
   const index=Uint32Array.from(faces.flatMap(f=>Array.from(source.index.slice(f*3,f*3+3)))),geometry={position:source.position,index};
   const bounds=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]];
   for(const i of new Set(index))for(let k=0;k<3;k++){const value=source.position[i*3+k];bounds[0][k]=Math.min(bounds[0][k],value);bounds[1][k]=Math.max(bounds[1][k],value);}
   const rim=lowRimSamples(geometry,bounds[0][1]);
   components.push({originalRuntimeFaces:faces,triangles:faces.length,bounds,
    interface:verifySupportInterface(geometry,bounds[0][1],support),layers:inspectSupportLayers(rim,surface)});
  }
  assert.equal(components.reduce((sum,c)=>sum+c.triangles,0),count);
  rows.push({...pair,sourceSHA256:sources.get(pair.uid).sourceSHA256,supportSHA256:sources.get(pair.supportUid).sourceSHA256,
   sourceFaces:count,components,completeRuntimeFaceAccounting:true});
  console.log(JSON.stringify({uid:pair.uid,components:components.length,strictPassed:components.filter(c=>c.interface.passed).length}));
 }
}finally{for(const model of loaded.values())disposeOfficialModel(model);}
for(const p of ['source-scripts/city/government-import/original-assembly-component-interfaces-v1-20261023.mjs','source-scripts/city/government-import/support-interface.mjs','source-scripts/city/government-import/support-contact.mjs','3d-viewer/city/official-model-assets.js'])hashes[p]=sha(readFileSync(new URL(p,root)));
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);
writeFileSync(new URL(base+'component-support-checks.json.gz',root),gzipSync(JSON.stringify({rows,inputHashes:hashes,sourceGeometryChanges:0,installationApproved:false,
 qualification:'Every runtime face belongs to exactly one exact shared-edge component. Strict interfaces and lower layers retained separately, without role classification, omitted components, support acceptance or original-asset edits.'})));
