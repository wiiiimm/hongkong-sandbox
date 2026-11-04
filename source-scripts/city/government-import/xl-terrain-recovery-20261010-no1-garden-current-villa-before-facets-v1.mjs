/** Source-only literal before-state terrain facets; no candidate or viewer edits. */
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const root=new URL('../../../',import.meta.url),inputs={},hash=b=>createHash('sha256').update(b).digest('hex');
const load=p=>{const raw=readFileSync(new URL(p,root));inputs[p]=hash(raw);return JSON.parse(raw);};
const manifestPath='docs/astra-city/government-import/xl-terrain-recovery-20261010-festival-source-closed-scope-v1/acceptance-manifest.json',manifest=load(manifestPath);assert.equal(inputs[manifestPath],'422e9d4df4478282d7745f9f804699e9acfbd807021710af5eb3c12925525e41');
for(const p of ['source-scripts/city/government-import/xl-terrain-recovery-20261010-no1-garden-current-villa-before-facets-v1.mjs','3d-viewer/city/world.js','3d-viewer/city/native-terrain.js','3d-viewer/city/exact-finite-triangle-projection.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js'])inputs[p]=hash(readFileSync(new URL(p,root)));
const data=load('3d-viewer/city/data/terrain.json');data.patches=manifest.terrainPatches.map(p=>load('3d-viewer/'+p.url));const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);const bounds=[-597.5,1187.5,-487.5,1282.5],faces=[],identity=new THREE.Matrix4();
terrain.traverse(mesh=>{if(!mesh.isMesh)return;assert(mesh.matrixWorld.equals(identity));const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;for(let i=0;i<n;i+=3){const points=[0,1,2].map(k=>idx?idx.getX(i+k):i+k).map(j=>[p.getX(j),p.getY(j),p.getZ(j)]),x=points.map(v=>v[0]),z=points.map(v=>v[2]);if(Math.max(...x)<bounds[0]||Math.min(...x)>bounds[2]||Math.max(...z)<bounds[1]||Math.min(...z)>bounds[3])continue;faces.push(points);}});
const out=new URL('source-scripts/city/government-import/local/xl-terrain-recovery-20261010-no1-garden-current-villa-before-facets-v1/diagnostic.json.gz',root);mkdirSync(new URL('.',out),{recursive:true});writeFileSync(out,gzipSync(JSON.stringify({bounds,completeBeforeDrawnFaces:faces,completeBeforeDrawnFacesSHA256:hash(new Float64Array(faces.flat(2))),inputHashes:inputs,historicalManifestSHA256:inputs[manifestPath],currentAcceptance:false,sourceGeometryChanges:0})));console.log(JSON.stringify({completeBeforeDrawnFaces:faces.length,currentAcceptance:false}));terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m.dispose();});
