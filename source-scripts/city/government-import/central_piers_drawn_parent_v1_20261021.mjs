/** Capture actual current drawn terrain, including the installed native pier child. */
import{readFileSync,writeFileSync,mkdirSync,readdirSync}from'node:fs';
import{createHash}from'node:crypto';
import{gzipSync}from'node:zlib';
import assert from'node:assert/strict';
import*as THREE from'../../../3d-viewer/vendor/three.module.js';
import{makeTerrain}from'../../../3d-viewer/city/world.js';
const root=new URL('../../../',import.meta.url),inputs={},hash=b=>createHash('sha256').update(b).digest('hex');
const raw=p=>{const b=readFileSync(new URL(p,root));inputs[p]=hash(b);return b},read=p=>JSON.parse(raw(p));
const batch='government-xl-central-piers-drawn-parent-v1-20261021',scopePath='docs/astra-city/government-import/government-xl-central-piers-current-scope-v1-20261021/scope.json';
const scope=read(scopePath),bounds=scope.localChildBounds,manifest=read('3d-viewer/city/data/manifest.json'),data=read('3d-viewer/city/data/terrain.json');
function pinTree(p){for(const d of readdirSync(new URL(p,root),{withFileTypes:true})){if(d.isDirectory()){if(d.name!=='data')pinTree(p+d.name+'/')}else if(/\.(m?js)$/.test(d.name))raw(p+d.name)}}
pinTree('3d-viewer/city/');raw('3d-viewer/vendor/three.module.js');raw('source-scripts/city/government-import/central_piers_drawn_parent_v1_20261021.mjs');
data.patches=(manifest.terrainPatches||[]).map(e=>read('3d-viewer/'+e.url));assert.equal(inputs['3d-viewer/'+scope.replacedWrapper.url],scope.replacedWrapper.sha256);
const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);const identity=new THREE.Matrix4(),position=[],lineage=[];let meshOrdinal=0;
terrain.traverse(mesh=>{if(!mesh.isMesh)return;const ordinal=meshOrdinal++;assert(mesh.matrixWorld.equals(identity));const p=mesh.geometry.attributes.position,ix=mesh.geometry.index,n=ix?.count??p.count;
for(let i=0;i<n;i+=3){const ids=[0,1,2].map(k=>ix?ix.getX(i+k):i+k),v=ids.map(j=>[p.getX(j),p.getY(j),p.getZ(j)]);if(Math.max(...v.map(a=>a[0]))<bounds[0]||Math.min(...v.map(a=>a[0]))>bounds[2]||Math.max(...v.map(a=>a[2]))<bounds[1]||Math.min(...v.map(a=>a[2]))>bounds[3])continue;position.push(...v.flat());lineage.push([ordinal,i/3]);}});
assert(position.length>0);for(const[p,h]of Object.entries(inputs))assert.equal(hash(readFileSync(new URL(p,root))),h,p);
const dir=new URL('source-scripts/city/government-import/local/'+batch+'/',root);mkdirSync(dir,{recursive:true});writeFileSync(new URL('drawn-ground.json.gz',dir),gzipSync(JSON.stringify({bounds,position,lineage,inputHashes:inputs,installationApproved:false})));console.log(JSON.stringify({triangles:position.length/9,bounds,inputFiles:Object.keys(inputs).length}));
