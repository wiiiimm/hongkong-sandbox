/** Exact original source surface at higher support layers; diagnostic only. */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {trianglePointIndex} from './triangle-point-index.mjs';
const root=new URL('../../../',import.meta.url),[base,uid,out]=process.argv.slice(2),hashes={};
assert(base?.startsWith('docs/astra-city/government-import/government-xl-')&&base.endsWith('/')&&!base.includes('..'));
assert(out?.startsWith('source-scripts/city/government-import/local/government-xl-')&&!out.includes('..'));
assert(!existsSync(new URL(out,root)),'Fresh diagnostic only');
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));hashes[path]=sha(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);}
const inputs=read(base+'diagnostic-inputs.json'),layers=read(base+'layer-checks.json.gz'),row=layers.rows.find(r=>r.uid===uid);assert(row);
const source=inputs.sources.find(r=>r.uid===uid),support=inputs.sources.find(r=>r.uid===row.supportUid);assert(source&&support);
const light={night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
async function load(r){const raw=readFileSync(new URL(r.candidate.path,root));hashes[r.candidate.path]=sha(raw);assert.equal(sha(raw),r.sourceSHA256);assert.equal(sha(raw),r.candidate.entry.sha256);return loadOfficialModel({...r.candidate.entry,assetURL:'https://diagnostic.invalid/model.glb.gz'},r.source.building,light,{fetcher:async()=>new Response(raw)});}
const a=await load(source),b=await load(support),g=a.record.modelGeometry,s=b.record.modelGeometry;
try{
 const index=trianglePointIndex(g),tri=new THREE.Triangle(),point=new THREE.Vector3(),near=new THREE.Vector3(),normal=new THREE.Vector3();
 const rows=row.points.map(f=>{
  const high=f.originalSupportFaces.filter(h=>h.height>f.position[1]+.5);
  const hits=high.map(h=>{
   const actual=[0,1,2].map(k=>Array.from(s.position.slice(s.index[h.faceIndex*3+k]*3,s.index[h.faceIndex*3+k]*3+3)));assert.deepEqual(actual,h.vertices);
   const p=[f.position[0],h.height,f.position[2]],incident=[];point.fromArray(p);
   for(const face of index.candidates(p)){
    const verts=[0,1,2].map(k=>Array.from(g.position.slice(g.index[face*3+k]*3,g.index[face*3+k]*3+3)));
    [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(verts[k]));tri.closestPointToPoint(point,near);const distance=near.distanceTo(point);
    if(distance<=.001){tri.getNormal(normal);incident.push({faceIndex:face,distanceM:distance,normal:normal.toArray(),vertices:verts});}
   }
   return {supportFaceIndex:h.faceIndex,point:p,higherGapM:f.position[1]-h.height,sourceIncidentFaces:incident};
  });
  return {position:f.position,contactFaces:f.contactFaces,higherLayers:hits,higherLayerOnSourceSurface:hits.some(h=>h.sourceIncidentFaces.length)};
 });
 for(const path of ['source-scripts/city/government-import/support-overlap-point-diagnostic.mjs','source-scripts/city/government-import/triangle-point-index.mjs','3d-viewer/city/official-model-assets.js'])hashes[path]=sha(readFileSync(new URL(path,root)));
 for(const [path,pinned] of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(path,root))),pinned);
 const result={uid,supportUid:row.supportUid,sourceSHA256:source.sourceSHA256,supportSHA256:support.sourceSHA256,rows,inputHashes:hashes,
  higherLayerOnSourceSurface:rows.filter(r=>r.higherLayerOnSourceSurface).length,samples:rows.length,diagnosticOnly:true,publication:false,newlyInstalled:0,modelGeometryChanges:0,scriptExternalAICalls:0,
  qualification:'Exact original higher-layer vertical intersections tested against original source triangles at 1mm distance. A point off the source surface does not prove absence of interior penetration, triangle intersections elsewhere or full foundation. No interface exemption or acceptance credit.'};
 mkdirSync(new URL('.',new URL(out,root)),{recursive:true});writeFileSync(new URL(out,root),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({uid,samples:result.samples,higherLayerOnSourceSurface:result.higherLayerOnSourceSurface,diagnosticOnly:true}));
}finally{disposeOfficialModel(a);disposeOfficialModel(b);}
