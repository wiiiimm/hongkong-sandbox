import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const root=new URL('../../../',import.meta.url),pins={};
function load(p){const raw=readFileSync(new URL(p,root));pins[p]=createHash('sha256').update(raw).digest('hex');return JSON.parse(raw);}
const scope=load('docs/astra-city/government-import/government-xl-ronsdale-terrain-scope-v2-20261022/scope.json');
assert.equal(scope.overlappingTerrain.length,0);
const manifest=load('3d-viewer/city/data/manifest.json'),data=load('3d-viewer/city/data/terrain.json');
data.patches=manifest.terrainPatches.map(p=>load('3d-viewer/'+p.url));
for(const p of ['3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/native-terrain.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js'])pins[p]=createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex');
const [x0,z0,x1,z1]=scope.baseReplacementExtent,faces=[];
const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);
terrain.traverse(mesh=>{if(!mesh.isMesh)return;assert(mesh.matrixWorld.elements.every((v,i)=>v===(i%5===0?1:0)));const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;
for(let i=0;i<n;i+=3){const f=[0,1,2].map(k=>{const j=idx?idx.getX(i+k):i+k;return [p.getX(j),p.getY(j),p.getZ(j)];});const xs=f.map(v=>v[0]),zs=f.map(v=>v[2]);if(Math.max(...xs)<=x0||Math.min(...xs)>=x1||Math.max(...zs)<=z0||Math.min(...zs)>=z1)continue;assert(f.every(v=>v[0]>=x0&&v[0]<=x1&&v[2]>=z0&&v[2]<=z1),'Terrain face crosses parent domain');faces.push(f);}});
for(const [p,h] of Object.entries(pins))assert.equal(createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex'),h);
const dir=new URL('source-scripts/city/government-import/local/government-xl-ronsdale-parent-capture-v1-20261022/',root);mkdirSync(dir,{recursive:true});writeFileSync(new URL('parent.json',dir),JSON.stringify({triangles:faces,inputHashes:pins,domain:scope.baseReplacementExtent}));console.log({faces:faces.length});
