/** Complete uncut actual parent facets intersecting the full floor work envelope. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const root=new URL('../../../',import.meta.url),pins={};
const hash=b=>createHash('sha256').update(b).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));pins[path]=hash(raw);return JSON.parse(raw);}
const [scopePath,outPath]=process.argv.slice(2);assert(scopePath.startsWith('docs/astra-city/government-import/')&&outPath.startsWith('source-scripts/city/government-import/local/')&&!scopePath.includes('..')&&!outPath.includes('..'));
const scope=read(scopePath),manifest=read('3d-viewer/city/data/manifest.json'),base=read('3d-viewer/city/data/terrain.json'),parents=manifest.terrainPatches.map(entry=>({url:entry.url,data:read('3d-viewer/'+entry.url)})),rows=[];let currentURL='';
function visit(mesh,path){
 if(mesh.isMesh){const p=mesh.geometry.attributes.position,ix=mesh.geometry.index,n=ix?.count??p.count;
  for(let i=0;i<n;i+=3){const f=[0,1,2].map(k=>{const j=ix?ix.getX(i+k):i+k;return[p.getX(j),p.getY(j),p.getZ(j)];}),xs=f.map(p=>p[0]),zs=f.map(p=>p[2]),[x,z,X,Z]=scope.bounds;
   if(Math.max(...xs)<x||Math.min(...xs)>X||Math.max(...zs)<z||Math.min(...zs)>Z)continue;
   rows.push({triangle:f,url:currentURL,meshPath:path,meshName:mesh.name,renderedFace:i/3});
  }
 }
 for(let i=0;i<mesh.children.length;i++)visit(mesh.children[i],path+'/children/'+i);
}
for(const entry of [{url:'city/data/terrain.json',data:{...base,patches:[],patchExclusions:[...(base.patchExclusions||[]),...parents.map(p=>p.data.coarseCells)]}},...parents]){currentURL=entry.url;const terrain=makeTerrain(entry.data.nativeMesh||entry.url==='city/data/terrain.json'?entry.data:{...entry.data,hydro:base.hydro,hydroChunk:true});terrain.updateMatrixWorld(true);visit(terrain,'');terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m?.dispose();});}
for(const path of ['3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/native-terrain.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js','source-scripts/city/government-import/source_floor_complete_world_capture_v2_20261103.mjs'])pins[path]=hash(readFileSync(new URL(path,root)));
for(const [path,sha]of Object.entries(pins))assert.equal(hash(readFileSync(new URL(path,root))),sha);
const out=new URL(outPath,root);mkdirSync(new URL('./',out),{recursive:true});writeFileSync(out,JSON.stringify({rows,inputHashes:pins,bounds:scope.bounds,completeUncutFacets:true,sourceGeometryChanges:0,installationApproved:false})+'\n');console.log(JSON.stringify({capturedFacets:rows.length}));
