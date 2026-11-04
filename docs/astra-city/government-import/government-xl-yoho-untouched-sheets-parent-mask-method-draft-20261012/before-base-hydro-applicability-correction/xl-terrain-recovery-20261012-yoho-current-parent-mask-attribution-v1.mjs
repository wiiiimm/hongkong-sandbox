/** UNEXECUTED read-only actual parent/chunk attribution; exact tuple equality. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2];
const sha=b=>createHash('sha256').update(b).digest('hex'),hashes={};
function raw(p){const b=readFileSync(new URL(p,root));const h=sha(b);if(hashes[p])assert.equal(hashes[p],h);hashes[p]=h;return b;}
function read(p){const b=raw(p);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const input=read(doc+'/input.json.gz');assert.equal(input.currentManifestSHA256,'2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540');
const closure=snapshotModuleClosure(new URL('source-scripts/city/government-import/acceptance-metrics-multi-retained.mjs',root),root);
assert.equal(closure.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.opaqueResourcesAreNotParsedModules);assert.equal(closure.unsupportedDynamicImports,0);
for(const [p,h]of Object.entries(closure.inputHashes))assert.equal(sha(raw(p)),h,p);
const {makeTerrain}=await import(new URL('3d-viewer/city/world.js',root));
const manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],input.currentManifestSHA256);
const base=read('3d-viewer/city/data/terrain.json'),sourceRecords=[];
const patches=manifest.terrainPatches.map((entry,i)=>{const path='3d-viewer/'+entry.url;return {entry,path,data:read(path),id:'manifestPatch:'+i};});
const data={...base,patches:patches.map(p=>p.data)};
const saved=read(input.capturedRuntimePath).rows;assert.deepEqual(saved.map(r=>r.uid),input.rows.map(r=>r.uid));
const identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
const tuple=t=>JSON.stringify(t); // Same Number/JSON semantics as the frozen capture; no rounding/tolerance.
const counts=xs=>{const m=new Map();for(const t of xs)m.set(tuple(t),(m.get(tuple(t))||0)+1);return [...m].sort(([a],[b])=>a.localeCompare(b));};
function faces(mesh){assert.deepEqual(mesh.matrixWorld.elements,identity);const p=mesh.geometry.attributes.position,idx=mesh.geometry.index,n=idx?.count??p.count;assert.equal(n%3,0);const out=[];
 for(let i=0;i<n;i+=3){const t=[];for(let j=0;j<3;j++){const k=idx?idx.getX(i+j):i+j;t.push(p.getX(k),p.getY(k),p.getZ(k));}assert(t.every(Number.isFinite));out.push(t);}return out;}
function intersects(t,b){const x=[t[0],t[3],t[6]],z=[t[2],t[5],t[8]];return !(Math.max(...x)<b[0]||Math.min(...x)>b[2]||Math.max(...z)<b[1]||Math.min(...z)>b[3]);}
function dispose(o){o.traverse(x=>{x.geometry?.dispose();for(const m of [].concat(x.material||[]))m?.dispose();});}
const selected=new Map(input.rows.map(r=>[r.uid,[]]));
function capture(o,source){o.updateMatrixWorld(true);o.traverse(mesh=>{if(!mesh.isMesh)return;const all=faces(mesh);for(const row of input.rows){const ids=[];for(let i=0;i<all.length;i++)if(intersects(all[i],row.closedCaptureBounds))ids.push(i);
 if(ids.length)selected.get(row.uid).push({...source,meshName:mesh.name,completeMeshFaces:all.length,completeMeshPositionVertices:mesh.geometry.attributes.position.count,completeMeshIndexedVertexCount:mesh.geometry.index?.count??null,allSelectedMeshFaceIDs:ids,completeSelectedDrawnTriplets:ids.map(i=>all[i])});}});}
// The actual complete renderer, with every base/patch/hydro mesh retained.
const actual=makeTerrain(data);actual.updateMatrixWorld(true);const actualByUID=new Map(input.rows.map(r=>[r.uid,[]]));
actual.traverse(m=>{if(!m.isMesh)return;const f=faces(m);for(const r of input.rows)for(const t of f)if(intersects(t,r.closedCaptureBounds))actualByUID.get(r.uid).push(t);});
// Base mesh and its hydro extras are direct actual objects: no reconstruction.
const topMeshes=actual.isMesh?[actual]:actual.children;
// Hydro cut-cell emission depends on covered parent masks, so a generic inferred
// prefix is not used. Explicitly reject it here rather than misattribute meshes.
assert(!data.hydro&&!data.nativeMesh,'Unreviewed base hydro/native attribution obligation');assert(topMeshes[0]?.isMesh);capture(topMeshes[0],{sourcePath:'3d-viewer/city/data/terrain.json',lineage:['base'],rawCoarseCells:null,rawPatchExclusions:base.patchExclusions||[],rawCoveredChildCells:patches.map(p=>p.data.coarseCells),rawGeoref:base.meta.georef,rawGridDimensions:[base.w,base.h],actualBaseMeshDirect:true});
// Read-only reproduction of world.js addPatch chunk arguments. Each result
// must match the actual union with full winding/order/multiplicity exactly.
function addPatch(patch,path,lineage){
 const record={sourcePath:path,lineage,rawCoarseCells:patch.coarseCells??null,rawPatchExclusions:patch.patchExclusions||[],rawCoveredChildCells:(patch.patches||[]).map(p=>p.coarseCells),rawGeoref:patch.meta.georef,rawGridDimensions:[patch.w,patch.h],native:!!patch.nativeMesh};sourceRecords.push(record);
 if(patch.nativeMesh){const o=makeTerrain(patch);capture(o,record);dispose(o);return;}
 for(let r=0;r<patch.h-1;r+=196)for(let c=0;c<patch.w-1;c+=196){const w=Math.min(197,patch.w-c),h=Math.min(197,patch.h-r),elev=[],vegetation=[],renderedElev=patch.renderedElev?[]:undefined,g=patch.meta.georef;
  for(let y=0;y<h;y++){if(renderedElev)renderedElev.push(...patch.renderedElev.slice((r+y)*patch.w+c,(r+y)*patch.w+c+w));elev.push(...patch.elev.slice((r+y)*patch.w+c,(r+y)*patch.w+c+w));vegetation.push(...patch.vegetation.slice((r+y)*patch.w+c,(r+y)*patch.w+c+w));}
  const patchExclusions=[...(patch.patches||[]).map(p=>p.coarseCells),...(patch.patchExclusions||[])].map(([x0,z0,x1,z1])=>[x0-c,z0-r,x1-c,z1-r]);
  const args={w,h,elev,vegetation,renderedElev,patchExclusions,hydro:data.hydro,hydroChunk:true,meta:{georef:{...g,bE:g.bE+c*g.aE,bN:g.bN+r*g.aN}}};
  const o=makeTerrain(args);capture(o,{...record,chunkOriginalCellOrigin:[c,r],rawChunkGeoref:args.meta.georef,chunkGridDimensions:[w,h],chunkExclusions:patchExclusions});dispose(o);
 }
 for(const [i,child]of (patch.patches||[]).entries())addPatch(child,path,[...lineage,'patches',i]);
}
for(const p of patches)addPatch(p.data,p.path,[p.id]);
const rows=[];
for(const row of input.rows){const expected=saved.find(r=>r.uid===row.uid).drawnGroundGeometry;const frozen=Array.from({length:expected.length/9},(_,i)=>expected.slice(i*9,i*9+9));const drawn=actualByUID.get(row.uid);assert.deepEqual(drawn.flat(),expected,'Actual whole renderer capture changed');
 const attributed=selected.get(row.uid);assert.deepEqual(counts(attributed.flatMap(x=>x.completeSelectedDrawnTriplets)),counts(drawn),'Parent/chunk attribution differs from full actual multiset');
 rows.push({...row,completeActualDrawnTriplets:drawn,completeAttributedSources:attributed,completeClosedUnionMatchedFrozenCapture:true,completeAttributionMultisetMatchedActual:true,allActualFacesIncludingDegeneraciesRetained:true,tupleConvention:'Exact JSON Number tuple, winding and multiplicity; not epsilon/area filtering',frozenCapturedFaces:frozen.length});}
dispose(actual);verifyModuleClosure(closure,root);for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);
const output=doc+'/actual-parent-mask-attribution.json.gz';assert(!existsSync(new URL(output,root)));writeFileSync(new URL(output,root),gzipSync(JSON.stringify({rows,wholeParentRegistry:sourceRecords,inputHashes:hashes,completeRecursiveProductionModuleClosure:closure,startEndAllInputsVerified:true,sourceGeometryChanges:0,terrainGeometryChanges:0,physicalAccepted:false,installationApproved:false})));
console.log(JSON.stringify({rows:rows.map(r=>({uid:r.uid,faces:r.completeActualDrawnTriplets.length,sources:r.completeAttributedSources.length})),exactActualAndFrozenAndAttributionEquality:true}));
