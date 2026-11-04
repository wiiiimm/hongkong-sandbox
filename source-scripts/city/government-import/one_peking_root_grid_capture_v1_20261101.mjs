// Reproduce only the existing container grid, with every existing child exclusion.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {clipParentTriangle} from './clip_parent_terrain_triangle_v1.mjs';
const root=new URL('../../../',import.meta.url),pins={};
function read(path){const raw=readFileSync(new URL(path,root));pins[path]=createHash('sha256').update(raw).digest('hex');return JSON.parse(raw);}
const [scopePath,outPath]=process.argv.slice(2);assert(scopePath.startsWith('docs/astra-city/government-import/')&&outPath.startsWith('source-scripts/city/government-import/local/')&&!scopePath.includes('..')&&!outPath.includes('..'));
const scope=read(scopePath),container=read('3d-viewer/'+scope.parentURL),base=read('3d-viewer/city/data/terrain.json');
assert(!container.nativeMesh);const grid={...container,patches:[],patchExclusions:[...(container.patchExclusions||[]),...container.patches.map(p=>p.coarseCells)],hydro:base.hydro,hydroChunk:true};
const terrain=makeTerrain(grid),faces=[];terrain.updateMatrixWorld(true);terrain.traverse(mesh=>{if(!mesh.isMesh)return;const p=mesh.geometry.attributes.position,ix=mesh.geometry.index;for(let i=0;i<ix.count;i+=3){const f=[0,1,2].map(k=>{const j=ix.getX(i+k);return[p.getX(j),p.getY(j),p.getZ(j)];}),x=f.map(p=>p[0]),z=f.map(p=>p[2]);const [x0,z0,x1,z1]=scope.bounds;if(Math.max(...x)<x0||Math.min(...x)>x1||Math.max(...z)<z0||Math.min(...z)>z1)continue;faces.push(...clipParentTriangle(f,scope.bounds));}});
for(const path of ['3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/native-terrain.js','source-scripts/city/government-import/clip_parent_terrain_triangle_v1.mjs'])pins[path]=createHash('sha256').update(readFileSync(new URL(path,root))).digest('hex');
for(const [p,h]of Object.entries(pins))assert.equal(createHash('sha256').update(readFileSync(new URL(p,root))).digest('hex'),h);
const out=new URL(outPath,root);mkdirSync(new URL('./',out),{recursive:true});writeFileSync(out,JSON.stringify({triangles:faces,inputHashes:pins,domain:scope.bounds,source:'Existing production container grid with all original child rectangles excluded; no grid, height or mask edits.'}));console.log({rootGridFaces:faces.length});
