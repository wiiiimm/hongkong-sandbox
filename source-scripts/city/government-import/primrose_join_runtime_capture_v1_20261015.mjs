/** Read-only actual BASIC and whole-domain before/after terrain capture. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
import {actualFloat32ModelMatrixPositions} from './actual_float32_model_matrix_bounds_20261011.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function read(p){const raw=readFileSync(new URL(p,root)),h=sha(raw);if(hashes[p])assert.equal(hashes[p],h);hashes[p]=h;return JSON.parse(p.endsWith('.gz')?gunzipSync(raw):raw);}
function save(n,d){const p=new URL(doc+'/'+n,root);assert(!existsSync(p));writeFileSync(p,gzipSync(JSON.stringify(d)));}
const input=read(doc+'/input.json.gz'),manifest=read('3d-viewer/city/data/manifest.json');assert.equal(hashes['3d-viewer/city/data/manifest.json'],input.currentManifestSHA256);
const closures=['3d-viewer/city/world.js','3d-viewer/city/building-geometry.js','source-scripts/city/government-import/actual_float32_model_matrix_bounds_20261011.mjs'].map(p=>snapshotModuleClosure(new URL(p,root),root));
for(const c of closures){assert(c.completeAuditedLiteralImportClosure&&c.computedImportsRejected&&c.unsupportedDynamicImports===0);Object.assign(hashes,c.inputHashes);}
const {createBuildingGeometry}=await import('../../../3d-viewer/city/building-geometry.js'),{makeTerrain}=await import('../../../3d-viewer/city/world.js');
const prior='docs/astra-city/government-import/government-xl-primrose-basic-ground-capture-v1-20261015';
const saved=read(prior+'/basic-actors.json.gz'),priorReport=read(prior+'/capture-report.json.gz');
for(const[p,h]of Object.entries(priorReport.inputHashes))assert.equal(sha(readFileSync(new URL(p,root))),h);Object.assign(hashes,priorReport.inputHashes);
const rows=saved.rows,seen={size:saved.completeCurrentForms},domain=input.domain,roi=saved.roi,identity=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];assert.deepEqual(saved.domain,domain);
function outside(b,d){return b[2]<d[0]||b[0]>d[2]||b[3]<d[1]||b[1]>d[3];}
function bounds(a){const b=[Infinity,Infinity,-Infinity,-Infinity];for(let i=0;i<a.length;i+=3){b[0]=Math.min(b[0],a[i]);b[1]=Math.min(b[1],a[i+2]);b[2]=Math.max(b[2],a[i]);b[3]=Math.max(b[3],a[i+2]);}return b;}
const base=read('3d-viewer/city/data/terrain.json'),patches=manifest.terrainPatches.map(p=>read('3d-viewer/'+p.url)),candidate=read(input.candidate.path);assert.equal(hashes[input.candidate.path],input.candidate.sha256);assert.deepEqual(candidate.coarseCells,input.cells);
function capture(data,label){const terrain=makeTerrain(data);terrain.updateMatrixWorld(true);const selected=[],hash=createHash('sha256'),buffer=Buffer.allocUnsafe(9*8*4096);let count=0,used=0,total=0;const flush=()=>{if(used){hash.update(buffer.subarray(0,used));used=0;}};
 terrain.traverse(m=>{if(!m.isMesh)return;assert.deepEqual(m.matrixWorld.elements,identity);const p=m.geometry.attributes.position,ix=m.geometry.index,n=ix?.count??p.count;assert(n%3===0);for(let i=0;i<n;i+=3){const t=[];for(let k=0;k<3;k++){const j=ix?ix.getX(i+k):i+k;t.push(p.getX(j),p.getY(j),p.getZ(j));}assert(t.every(Number.isFinite));const b=bounds(t);if(!outside(b,roi))selected.push(t);if(outside(b,domain)){for(const v of t){buffer.writeDoubleLE(v,used);used+=8;}count++;if(used===buffer.length)flush();}total++;}});flush();terrain.traverse(m=>{m.geometry?.dispose();for(const mat of [].concat(m.material||[]))mat?.dispose();});const result={completeRelevantDrawnTriplets:selected,roi,domain,totalDrawnFaces:total,strictExteriorOrderedSHA256:hash.digest('hex'),strictExteriorFaces:count,allDrawnFacetsIncludingVerticalAndDegenerateRetained:true};save(label+'-ground.json.gz',result);console.log(JSON.stringify({phase:label,selected:selected.length,total,outside:count}));return result;}
const before=read(prior+'/before-ground.json.gz'),after=capture({...base,patches:[...patches,candidate]},'after');assert.equal(before.strictExteriorFaces,after.strictExteriorFaces);assert.equal(before.strictExteriorOrderedSHA256,after.strictExteriorOrderedSHA256,'Actual exterior triangle sequence changed');
for(const c of closures)assert(verifyModuleClosure(c,root));for(const[p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h);save('capture-report.json.gz',{inputHashes:hashes,closures,completeCurrentForms:seen.size,basicActors:rows.length,roi,domain,strictExteriorUnchanged:true,startEndAllInputsVerified:true,publication:false});
