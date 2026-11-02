/** Exact captured-facet lookup through production terrain, including grid faces. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const root=new URL('../../../',import.meta.url),hash=b=>createHash('sha256').update(b).digest('hex'),inputs={};
const load=path=>{const raw=readFileSync(new URL(path,root));inputs[path]=hash(raw);return JSON.parse(path.endsWith('.gz')?gunzipSync(raw):raw);};
const [groundPath,proofPath,output]=process.argv.slice(2);assert(groundPath&&proofPath&&output);
const ground=load(groundPath).before,proof=load(proofPath),ids=proof.changedTerrainFaceIndices;
const key=t=>t.map(p=>p.map(v=>Object.is(v,-0)?0:v)).sort((a,b)=>a[0]-b[0]||a[1]-b[1]||a[2]-b[2]).flat().join(',');
const lookup=new Map(),matches=new Map(ids.map(i=>[i,[]]));
for(const id of ids){const k=key(ground[id]);if(!lookup.has(k))lookup.set(k,[]);lookup.get(k).push(id);}
const manifest=load('3d-viewer/city/data/manifest.json'),base=load('3d-viewer/city/data/terrain.json');
const patches=manifest.terrainPatches.map(entry=>({entry,data:load('3d-viewer/'+entry.url)}));
for(const path of ['3d-viewer/city/world.js','3d-viewer/city/native-terrain.js','3d-viewer/city/geo.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js'])inputs[path]=hash(readFileSync(new URL(path,root)));
const own='source-scripts/city/government-import/original_captured_ground_parent_lookup_v1_20261103.mjs';inputs[own]=hash(readFileSync(new URL(own,root)));
let examined=0;
function inspect(data,url){
 const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);
 function visit(mesh,path){
  if(mesh.isMesh){
   const p=mesh.geometry.attributes.position,ix=mesh.geometry.index,n=ix?.count??p.count;
   for(let offset=0;offset<n;offset+=3){
    const tri=[0,1,2].map(j=>{const i=ix?ix.getX(offset+j):offset+j;return[p.getX(i),p.getY(i),p.getZ(i)];});examined++;
    for(const id of lookup.get(key(tri))||[])matches.get(id).push({url,meshPath:path,meshName:mesh.name,renderedFace:offset/3});
   }
  }
  for(let i=0;i<mesh.children.length;i++)visit(mesh.children[i],path+'/children/'+i);
 }
 visit(terrain,'');terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m?.dispose();});
}
// The root grid excludes exactly the same complete top-level cells as the full
// renderer. Individual parents preserve child exclusions and global hydro data.
inspect({...base,patches:[],patchExclusions:[...(base.patchExclusions||[]),...patches.map(p=>p.data.coarseCells)]},'city/data/terrain.json');
for(const {entry,data}of patches)inspect(data.nativeMesh?data:{...data,hydro:base.hydro,hydroChunk:true},entry.url);
for(const [path,sha]of Object.entries(inputs))assert.equal(hash(readFileSync(new URL(path,root))),sha,'Input changed: '+path);
const rows=ids.map(id=>({capturedFace:id,currentRenderedParentMatches:matches.get(id)}));
const result={inputHashes:inputs,rows,completeRenderedFacesExamined:examined,uniquelyMatched:rows.filter(r=>r.currentRenderedParentMatches.length===1).length,
 unmatched:rows.filter(r=>!r.currentRenderedParentMatches.length).map(r=>r.capturedFace),ambiguous:rows.filter(r=>r.currentRenderedParentMatches.length>1).map(r=>r.capturedFace),
 capturedSceneApprovalTransferred:false,sourceGeometryChanges:0,physicalAcceptance:false,installationApproved:false};
writeFileSync(new URL(output,root),JSON.stringify(result)+'\n');console.log(JSON.stringify({uniquelyMatched:result.uniquelyMatched,unmatched:result.unmatched,ambiguous:result.ambiguous}));
