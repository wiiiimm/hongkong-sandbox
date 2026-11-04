/** Render complete old/new parent geometry, including the exact root mask cell. */
import {readFileSync,writeFileSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
const root=new URL('../../../',import.meta.url),pins={},hash=b=>createHash('sha256').update(b).digest('hex');
function read(path){const raw=readFileSync(new URL(path,root));pins[path]=hash(raw);return JSON.parse(raw);}
const [scopePath,outPath]=process.argv.slice(2),scope=read(scopePath);
for(const ref of scope.inputRefs)assert.equal(hash(readFileSync(new URL(ref.path,root))),ref.sha256);
const base=read('3d-viewer/city/data/terrain.json');
function triangles(node){const data=node.nativeMesh?node:{...node,hydro:base.hydro,hydroChunk:true},terrain=makeTerrain(data),out=[];terrain.updateMatrixWorld(true);terrain.traverse(mesh=>{if(!mesh.isMesh)return;const p=mesh.geometry.attributes.position,ix=mesh.geometry.index,n=ix?.count??p.count;for(let i=0;i<n;i+=3)out.push([0,1,2].map(k=>{const j=ix?ix.getX(i+k):i+k;return[p.getX(j),p.getY(j),p.getZ(j)];}));});terrain.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m?.dispose();});return out;}
const old=read(scope.oldParent.path),candidate=read(scope.candidate.path),north=read(scope.north.path);
assert.equal(pins[scope.oldParent.path],scope.oldParent.sha256);assert.equal(pins[scope.candidate.path],scope.candidate.sha256);assert.equal(pins[scope.north.path],scope.north.sha256);
assert.deepEqual(candidate.coarseCells,old.coarseCells);
const before=[...triangles(old),...scope.rootBeforeFacets],after=[...triangles(candidate),...triangles(north)];
for(const path of ['3d-viewer/city/world.js','3d-viewer/city/geo.js','3d-viewer/city/native-terrain.js','3d-viewer/city/terrain-patch-index.js','3d-viewer/city/rendered-patch-height.js','source-scripts/city/government-import/source_floor_complete_terrain_delta_v1_20261103.mjs'])pins[path]=hash(readFileSync(new URL(path,root)));
for(const [path,sha]of Object.entries(pins))assert.equal(hash(readFileSync(new URL(path,root))),sha);
for(const ref of scope.inputRefs)assert.equal(hash(readFileSync(new URL(ref.path,root))),ref.sha256);
writeFileSync(new URL(outPath,root),gzipSync(Buffer.from(JSON.stringify({before,after,inputHashes:pins,allOldAndNewParentFacetsRendered:true,installationApproved:false}))));console.log(JSON.stringify({completeBeforeFaces:before.length,completeAfterFaces:after.length}));
