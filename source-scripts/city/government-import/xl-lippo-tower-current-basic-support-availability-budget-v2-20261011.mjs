/** Actual production support/budget methods and unchanged local source loader.
 * Availability counterexamples are hermetic captured-current stream fixtures;
 * the source loader is independently executed with byte/module start/end pins.
 */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {snapshotModuleClosure,verifyModuleClosure} from './literal_production_module_dependency_closure_20261010.mjs';
const root=new URL('../../../',import.meta.url),inputPath='docs/astra-city/government-import/government-xl-lippo-tower-only-current-complete-inputs-v5-20261011/input.json.gz',geometryPath=inputPath.replace('input.json.gz','complete-current-geometry.json.gz');
const hashes={},sha=b=>createHash('sha256').update(b).digest('hex');
function bytes(p){const u=new URL(p,root);assert(u.pathname.startsWith(root.pathname));const b=readFileSync(u);hashes[p]=sha(b);return b;}
function read(p){const b=bytes(p);return JSON.parse(p.endsWith('.gz')?gunzipSync(b):b);}
const closures=['3d-viewer/city/official-models.js','3d-viewer/city/official-model-assets.js'].map(p=>snapshotModuleClosure(new URL(p,root),root));
for(const c of closures)Object.assign(hashes,c.inputHashes);
bytes('source-scripts/city/government-import/xl-lippo-tower-current-basic-support-availability-budget-v2-20261011.mjs');bytes('source-scripts/city/government-import/literal_production_module_dependency_closure_20261010.mjs');
const inp=read(inputPath),geo=read(geometryPath),entry=JSON.parse(readFileSync(process.argv[2]));
assert.equal(sha(bytes(inp.currentManifest.path)),inp.currentManifest.sha256);for(const r of inp.currentCatalogueRefs)assert.equal(sha(bytes(r.path)),r.sha256);for(const [p,h]of Object.entries(geo.inputHashes))assert.equal(sha(bytes(p)),h);
const {OfficialModelLayer,MODEL_PROFILES}=await import(new URL('3d-viewer/city/official-models.js',root).href),{supportedModelPlan,modelSupportDependencies}=await import(new URL('3d-viewer/city/model-support.js',root).href),{modelBudget,loadOfficialModel,disposeOfficialModel}=await import(new URL('3d-viewer/city/official-model-assets.js',root).href),THREE=await import(new URL('3d-viewer/vendor/three.module.js',root).href);
const uid='landsd/239465:0',carrier='landsd/231645:0',dependency={uid:carrier,csuid:'3551417531P20050812',state:'surveyed-footprint-fallback'};
assert.equal(entry.uid,uid);assert.equal(entry.sha256,inp.rows[0].sourceSHA256);assert.deepEqual(entry.supportDependencies,[dependency]);assert.equal(entry.proceduralWindows,false);
assert.deepEqual(modelSupportDependencies(entry),[{...dependency,kind:'fallback'}]);
const basic=geo.completeCurrentBasicGeometry.find(r=>r.uid===carrier);assert(basic);assert.equal(basic.index.length/3,284);
const forms=inp.currentAllSourceForms,passed=[];
function context({missing=false,wrongCSUID=false,wanted=true,infrastructure=false,baked=false,managed=false}={}){
 const p={...forms[carrier]};if(wrongCSUID)p.buildingCSUID='wrong';if(baked)p.modelGeometry={};
 return {stream:{infrastructureBuildingUids:new Set(infrastructure?[carrier]:[]),getLoadedBuilding:u=>u===carrier?(missing?null:p):forms[u],cache:{wanted:wanted?[p.tile]:[]},detailedModels:new Map()},cache:{entries:new Map(managed?[[carrier,{}]]:[])}};
}
function available(ctx,u,kind,d={}){return OfficialModelLayer.prototype.supportAvailable.call(ctx,u,kind,d);}
function check(name,fn){fn();passed.push(name);}
check('exact-current-basic-uid-csuid-tile-available',()=>assert(available(context(),carrier,'fallback',dependency)));
for(const [name,options]of [['missing-current-carrier',{missing:true}],['wrong-current-csuid',{wrongCSUID:true}],['unwanted-carrier-tile',{wanted:false}],['infrastructure-carrier',{infrastructure:true}],['unmanaged-baked-geometry',{baked:true}]])check(name,()=>assert.equal(available(context(options),carrier,'fallback',dependency),false));
const cost=modelBudget(entry);assert.equal(cost.triangles,3597);assert(cost.geometryBytes>0&&cost.residentBytes>cost.geometryBytes);
function plan(profile=MODEL_PROFILES.mobile,ctx=context(),candidates=[uid],models=new Map([[uid,entry]])){return supportedModelPlan(candidates,models,profile,modelBudget,(u,k,d)=>available(ctx,u,k,d));}
for(const profile of ['mobile','desktop'])check(profile+'-unchanged-production-budget-accepts',()=>{const p=plan(MODEL_PROFILES[profile]);assert.deepEqual(p.wanted,[uid]);assert.equal(p.blocked.size,0);assert.equal(p.used.triangles,3597);});
for(const k of ['geometryBytes','residentBytes','triangles','drawCalls','count'])check('strict-'+k+'-budget-blocks',()=>{const limit={...MODEL_PROFILES.mobile,[k]:k==='count'?0:k==='drawCalls'?0:cost[k]-1};const p=plan(limit);assert.deepEqual(p.wanted,[]);assert.match(p.blocked.get(uid),/budget/);});
check('missing-basic-reserves-no-unsupported-tower',()=>{const p=plan(MODEL_PROFILES.mobile,context({missing:true}));assert.deepEqual(p.wanted,[]);assert.match(p.blocked.get(uid),/Surveyed model support unavailable/);});
check('current-basic-native-upgrade-conflict-is-blocked',()=>{const upgrade={...entry,uid:carrier,supportDependencies:[]};const p=plan(MODEL_PROFILES.desktop,context(),[uid,carrier],new Map([[uid,entry],[carrier,upgrade]]));assert.deepEqual(p.wanted,[uid]);assert.match(p.blocked.get(carrier),/conflicts/);});
check('reverse-order-native-upgrade-does-not-credit-basic-carrier',()=>{const upgrade={...entry,uid:carrier,supportDependencies:[]};const p=plan(MODEL_PROFILES.desktop,context(),[carrier,uid],new Map([[uid,entry],[carrier,upgrade]]));assert.deepEqual(p.wanted,[carrier]);assert.match(p.blocked.get(uid),/conflicts/);});
const source=bytes(inp.rows[0].candidate.path);assert.equal(sha(source),entry.sha256);let model;
try{
 model=await loadOfficialModel({...entry,assetURL:'https://readonly.invalid/original.glb.gz'},forms[uid],{night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}},{fetcher:async()=>new Response(source),getBuilding:u=>forms[u]});
 check('real-local-staged-metadata-source-loader-preserves-full-literal-position',()=>assert.deepEqual(Array.from(model.record.modelGeometry.position),geo.row.completeLiteralWorldPosition));
 check('real-local-staged-metadata-source-loader-preserves-full-original-index',()=>assert.deepEqual(Array.from(model.record.modelGeometry.index),geo.row.completeOriginalIndex));
 check('real-local-source-meshes-solid-and-opaque',()=>{assert(model.meshes.length);for(const mesh of model.meshes)for(const material of [].concat(mesh.material)){assert.equal(material.wireframe,false);assert.equal(material.transparent,false);assert.equal(material.opacity,1);}});
}finally{if(model)disposeOfficialModel(model);}
for(const [p,h]of Object.entries(hashes))assert.equal(sha(readFileSync(new URL(p,root))),h,p);for(const c of closures)assert(verifyModuleClosure(c,root));
const report={uid,carrierUid:carrier,sourceSHA256:entry.sha256,currentManifest:inp.currentManifest,productionBudget:cost,productionProfiles:MODEL_PROFILES,passedCounterexamples:passed,checksPassed:passed.length,hermeticCapturedActualCurrentSupportAvailabilityCounterexamples:true,actualProductionSupportAndBudgetMethods:true,separateActualProductionSourceLoaderExecuted:true,ordinaryBudgetLimitsUnchanged:true,wholeBasicReaccepted:false,sourceGeometryChanges:0,terrainGeometryChanges:0,completeRecursiveProductionModuleClosures:closures,inputHashes:hashes,startAndEndInputHashesVerified:true,installationApproved:false};
writeFileSync(process.argv[3],JSON.stringify(report));console.log(JSON.stringify({checksPassed:report.checksPassed,productionBudget:cost,sourceGeometryChanges:0}));
