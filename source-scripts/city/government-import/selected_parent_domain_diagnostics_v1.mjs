/** Capture complete current terrain faces intersecting explicit failed domains.
 * Diagnostic only: retain crossing triangles without clipping or accepting them.
 */
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';

const root=new URL('../../../',import.meta.url),pins={};
const sha=raw=>createHash('sha256').update(raw).digest('hex');
function load(p){const raw=readFileSync(new URL(p,root));pins[p]=sha(raw);return JSON.parse(raw);}
const [inputPath,outputPath]=process.argv.slice(2);
assert(inputPath?.startsWith('docs/astra-city/government-import/')&&!inputPath.includes('..'));
assert(outputPath?.startsWith('source-scripts/city/government-import/local/')&&!outputPath.includes('..'));
const output=new URL(outputPath,root);assert(!existsSync(output));
const input=load(inputPath);assert(input.rows.length>0&&input.rows.length<=40);
assert.equal(new Set(input.rows.map(r=>r.uid)).size,input.rows.length);
const manifest=load('3d-viewer/city/data/manifest.json');
assert.equal(pins['3d-viewer/city/data/manifest.json'],input.manifestSHA256);
const data=load('3d-viewer/city/data/terrain.json');
data.patches=manifest.terrainPatches.map(p=>load('3d-viewer/'+p.url));
for(const p of ['3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/native-terrain.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js'])pins[p]=sha(readFileSync(new URL(p,root)));
const rows=input.rows.map(r=>({...r,faces:[],crossingFaces:[],insideFaces:0}));
const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);
terrain.traverse(mesh=>{
 if(!mesh.isMesh)return;
 assert(mesh.matrixWorld.elements.every((v,i)=>v===(i%5===0?1:0)));
 const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;
 for(let i=0;i<n;i+=3){
  const face=[0,1,2].map(k=>{const j=idx?idx.getX(i+k):i+k;return[p.getX(j),p.getY(j),p.getZ(j)];});
  const xs=face.map(v=>v[0]),zs=face.map(v=>v[2]),a=Math.min(...xs),b=Math.min(...zs),c=Math.max(...xs),d=Math.max(...zs);
  for(const row of rows){
   const [x0,z0,x1,z1]=row.bounds;if(c<=x0||a>=x1||d<=z0||b>=z1)continue;
   const index=row.faces.length;row.faces.push(face);
   if(a<x0||b<z0||c>x1||d>z1)row.crossingFaces.push({capturedFace:index,meshName:mesh.name,meshFace:i/3,bounds:[a,b,c,d]});
   else row.insideFaces++;
  }
 }
});
for(const [p,h]of Object.entries(pins))assert.equal(sha(readFileSync(new URL(p,root))),h,'Current input changed: '+p);
mkdirSync(new URL('./',output),{recursive:true});
writeFileSync(output,gzipSync(JSON.stringify({rows,inputHashes:pins,installationApproved:false,sourceGeometryChanges:0,qualification:'Whole current drawn terrain triangles, including complete crossing faces. No clipping, filling, source edits or coverage approval.'})));
console.log(rows.map(r=>({uid:r.uid,faces:r.faces.length,crossingFaces:r.crossingFaces.length,insideFaces:r.insideFaces})));
