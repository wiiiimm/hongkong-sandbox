/** ROOT-only exact current BASIC338946 constructor. No model/terrain changes. */
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {createBuildingGeometry} from '../../../3d-viewer/city/building-geometry.js';
import {snapshotModuleClosure,verifyModuleClosure} from './exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';
const root=new URL('../../../',import.meta.url),doc=process.argv[2],sha=b=>createHash('sha256').update(b).digest('hex');
const closure=snapshotModuleClosure(import.meta.url,root);assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure&&closure.unsupportedDynamicImports===0);
if(process.argv.includes('--closure-only')){assert(!existsSync(new URL(doc,root)));writeFileSync(new URL(doc,root),JSON.stringify(closure,null,2)+'\n');process.exit(0);}
assert(doc?.startsWith('docs/astra-city/government-import/government-xl-')&&doc.endsWith('/')&&!doc.includes('..'));
const hashes={...closure.inputHashes};
function raw(path,expected){const b=readFileSync(new URL(path,root)),h=sha(b);if(expected!==undefined)assert.equal(h,expected,path);if(hashes[path])assert.equal(hashes[path],h,path);hashes[path]=h;return b;}
const input=JSON.parse(raw(doc+'fallback-input.json')),form=input.currentForm;
assert.equal(form.uid,'landsd/338946:0');assert.equal(input.standaloneOwnedUID,'landsd/12728:0');
const manifest=JSON.parse(raw(input.currentManifest.path,input.currentManifest.sha256));
for(const url of manifest.officialModelCatalogues){const c=JSON.parse(raw('3d-viewer/'+url));assert(!c.models.some(r=>r.uid===form.uid),'Tower official source already installed');}
const tile=JSON.parse(raw(input.currentTile.path,input.currentTile.sha256));assert.deepEqual(tile.buildings.find(r=>r.uid===form.uid),form);
const output=doc+'current-tower-BASIC-constructor.json.gz';assert(!existsSync(new URL(output,root)));
let g;
try{
 g=createBuildingGeometry(form);assert(g?.attributes.position);const p=g.attributes.position;assert(p.array instanceof Float32Array);
 const attrs={};for(const [key,a]of Object.entries(g.attributes)){assert(!a.isInterleavedBufferAttribute&&Array.from(a.array).every(Number.isFinite));attrs[key]={array:Array.from(a.array),arrayType:a.array.constructor.name,itemSize:a.itemSize,count:a.count,normalized:a.normalized,byteSHA256:sha(Buffer.from(a.array.buffer,a.array.byteOffset,a.array.byteLength))};}
 const row={uid:form.uid,currentForm:form,position:Array.from(p.array),index:g.index?Array.from(g.index.array):Array.from({length:p.count},(_,i)=>i),allActualAttributes:attrs,identityModelMatrix:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],currentConstructorPreserved:true,allUnusedPositionsIncluded:true,completeOriginalGovernmentTowerUninstalled:true,sourceGeometryChanges:0};
 assert(row.position.length&&row.index.length%3===0);assert(verifyModuleClosure(closure,root));for(const [path,h]of Object.entries(hashes))assert.equal(sha(raw(path)),h,path);
 writeFileSync(new URL(output,root),gzipSync(JSON.stringify({row,inputHashes:hashes,completeRecursiveProductionModuleClosure:closure,startEndAllInputsVerified:true,physicalAccepted:false,installationApproved:false,sourceGeometryChanges:0,terrainGeometryChanges:0})));
 console.log(JSON.stringify({uid:form.uid,faces:row.index.length/3,positions:p.count,captureOnly:true}));
}finally{g?.dispose();}
