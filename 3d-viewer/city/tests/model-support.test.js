import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {modelSupportDependencies,supportedModelPlan,retainVisibleNativeSupports} from '../model-support.js';
import {OfficialModelLayer,MODEL_PROFILES} from '../official-models.js';
import {modelBudget} from '../official-model-assets.js';
const uid=n=>'landsd/'+n+':0';
const meta=(n,deps=[])=>({uid:uid(n),worldBounds:[[0,2,0],[10,12,10]],priority:'landmark',decodedGeometryBytes:1000,indexedVertices:24,triangles:12,supportDependencies:deps});
const support=(n,state='candidate')=>({uid:uid(n),state});
const camera=()=>{const c=new THREE.PerspectiveCamera(50,1,1,100000);c.position.set(5,10,100);c.lookAt(5,7,5);c.updateProjectionMatrix();return c;};
const tick=()=>new Promise(r=>setTimeout(r,0));
async function settled(layer){for(let i=0;i<200&&layer.cache.running.size;i++)await tick();assert.equal(layer.cache.running.size,0,'model lifecycle settled');}
function fixture(entries,{profile='desktop',download=async()=>{},restore=async()=>{}}={}){
 const log=[],buildings=new Map(entries.map(m=>[m.uid,{uid:m.uid,modelGeometry:null,tile:'0_0'}]));
 const stream={detailedModels:new Map(),lighting:{},getLoadedBuilding(key){return this.detailedModels.get(key)?.record||buildings.get(key);},async setDetailedModel(key,value){
  if(value){value.active=true;this.detailedModels.set(key,value);log.push('attach:'+key);}
  else{log.push('restore-start:'+key);await restore(key);const old=this.detailedModels.get(key);if(old)old.active=false;this.detailedModels.delete(key);log.push('restore-end:'+key);}return true;
 }};
 const layer=new OfficialModelLayer({stream,profile,loadAsset:async(m)=>{
  log.push('download:'+m.uid);await download(m.uid);
  const group=new THREE.Group();group.visible=true;return {entry:m,group,record:{...buildings.get(m.uid),modelGeometry:{}},meshes:[],active:false,budget:modelBudget(m)};
 }});
 for(const m of entries)layer.models.set(m.uid,m);
 return {layer,stream,log,buildings};
}
test('native closures are ordered, shared supports counted once, and cycles/missing supports retain fallback',()=>{
 const models=new Map([meta(1,[support(2)]),meta(2),meta(3,[support(2)])].map(m=>[m.uid,m]));
 const plan=(ids)=>supportedModelPlan(ids,models,MODEL_PROFILES.mobile,modelBudget,()=>true);
 assert.deepEqual(plan([uid(1),uid(3)]).wanted,[uid(2),uid(1),uid(3)]);
 models.get(uid(2)).supportDependencies=[support(1)];assert.deepEqual(plan([uid(1),uid(3)]).wanted,[]);assert.match(plan([uid(1)]).blocked.get(uid(1)),/Cyclic/);
 models.delete(uid(2));assert.deepEqual(plan([uid(1)]).wanted,[]);
});
test('whole support assemblies obey mobile count, memory and triangle budgets without raising limits',()=>{
 for(const key of ['count','geometryBytes','residentBytes','triangles']){
  const models=new Map([meta(1,[support(2)]),meta(2)].map(m=>[m.uid,m]));const cost=modelBudget(models.get(uid(1)));
  const limits={...MODEL_PROFILES.mobile,[key]:key==='count'?1:cost[key]*2-1};
  const p=supportedModelPlan([uid(1)],models,limits,modelBudget,()=>true);assert.deepEqual(p.wanted,[],key);assert.match(p.blocked.get(uid(1)),/budget/);
 }
});
test('surveyed fallback dependencies never request native assets and cannot be upgraded within the same plan',()=>{
 const models=new Map([meta(1,[support(2,'surveyed-footprint-fallback')]),meta(2)].map(m=>[m.uid,m]));
 const p=supportedModelPlan([uid(1),uid(2)],models,MODEL_PROFILES.mobile,modelBudget,()=>true);assert.deepEqual(p.wanted,[uid(1)]);assert.match(p.blocked.get(uid(2)),/surveyed support/);
 models.delete(uid(2));assert.deepEqual(supportedModelPlan([uid(1)],models,MODEL_PROFILES.mobile,modelBudget,()=>true).wanted,[uid(1)]);
 assert.deepEqual(modelSupportDependencies(meta(1,[uid(2)])).map(d=>d.kind),['fallback']);
 assert.throws(()=>modelSupportDependencies(meta(1,[support(2,'unknown')])),/Invalid/);
});
test('a small off-camera native support bypasses its own LOD filter while a visible tower needs it',async t=>{
 const tower=meta(1,[support(2)]),podium={...meta(2),priority:'detail',worldBounds:[[-1000,2,-1000],[-999,3,-999]]};
 const f=fixture([tower,podium],{profile:'mobile'});t.after(()=>f.layer.dispose());
 assert.deepEqual(f.layer.plan(camera(),{selectedUid:uid(1),force:true}),[uid(2),uid(1)]);await f.layer.cache.waitFor([uid(1)]);
 assert.ok(f.log.indexOf('attach:'+uid(2))<f.log.indexOf('download:'+uid(1)));assert.equal(f.layer.cache.entries.size,2);
});
test('slow native support cannot expose a floating tower, and support failure leaves tower fallback until Retry',async t=>{
 let finish,failed=true;const f=fixture([meta(1,[support(2)]),meta(2)],{download:async key=>{if(key===uid(2)){await new Promise(r=>finish=r);if(failed)throw new Error('support HTTP503');}}});t.after(()=>f.layer.dispose());
 f.layer.plan(camera(),{selectedUid:uid(1),force:true});while(!finish)await tick();assert.equal(f.stream.detailedModels.has(uid(1)),false);assert.equal(f.log.includes('download:'+uid(1)),false);
 finish();await settled(f.layer);assert.equal(f.stream.detailedModels.size,0);assert.match(f.layer.cache.errors.get(uid(1)).message,/503/);
 failed=false;finish=undefined;const retry=f.layer.retry();while(!finish)await tick();finish();await retry;await f.layer.cache.waitFor([uid(1)]);
 assert.ok(f.stream.detailedModels.get(uid(2)).active);assert.ok(f.stream.detailedModels.get(uid(1)).active);
});
test('retiring a support waits for its tower fallback and retains both when that restoration fails',async t=>{
 let rejectRestore=true,releaseRestore;const f=fixture([meta(1,[support(2)]),meta(2)],{restore:async key=>{if(key===uid(1)){await new Promise(r=>releaseRestore=r);if(rejectRestore)throw new Error('tower fallback failed');}}});t.after(()=>f.layer.dispose());
 const c=camera();f.layer.plan(c,{force:true,selectedUid:uid(1)});await f.layer.cache.waitFor([uid(1)]);
 c.position.set(50000,500,50000);c.lookAt(50000,0,40000);f.layer.plan(c,{force:true});while(!releaseRestore)await tick();
 assert.ok(f.stream.detailedModels.has(uid(2)));assert.equal(f.log.includes('restore-start:'+uid(2)),false);releaseRestore();await Promise.allSettled([...f.layer.retiring.values()]);
 assert.ok(f.stream.detailedModels.has(uid(1)));assert.ok(f.stream.detailedModels.has(uid(2)));assert.ok(f.layer.stats.residentBytes>0);
 rejectRestore=false;releaseRestore=undefined;const retry=f.layer.retry();while(!releaseRestore)await tick();releaseRestore();await retry;
 assert.equal(f.stream.detailedModels.size,0);assert.ok(f.log.indexOf('restore-end:'+uid(1))<f.log.indexOf('restore-start:'+uid(2)));
});
test('camera travel cancels waiting dependents without a blocked concurrency slot or late attachment',async t=>{
 let finish;const f=fixture([meta(1,[support(2)]),meta(2)],{download:async key=>{if(key===uid(2))await new Promise(r=>finish=r);}});t.after(()=>f.layer.dispose());
 const c=camera();f.layer.plan(c,{force:true,selectedUid:uid(1)});while(!finish)await tick();c.position.set(50000,500,50000);c.lookAt(50000,0,40000);f.layer.plan(c,{force:true});finish();await settled(f.layer);
 assert.equal(f.stream.detailedModels.size,0);assert.equal(f.log.includes('attach:'+uid(1)),false);assert.equal(f.layer.cache.listeners.size,0);
});
test('source-tile visibility retains transitive native supports but not unrelated models or fallback-only dependencies',()=>{
 const detail=(n,deps,visible)=>({entry:meta(n,deps),active:true,group:{visible},meshes:[{castShadow:visible}]});
 const map=new Map([[uid(1),detail(1,[support(2)],true)],[uid(2),detail(2,[support(3)],false)],[uid(3),detail(3,[],false)],[uid(4),detail(4,[],false)]]);
 retainVisibleNativeSupports(map);assert.deepEqual([...map.values()].map(d=>d.group.visible),[true,true,true,false]);assert.equal(map.get(uid(3)).meshes[0].castShadow,true);
 map.get(uid(1)).entry.supportDependencies=[support(4,'fallback')];retainVisibleNativeSupports(map);assert.equal(map.get(uid(4)).group.visible,false);
});

test('support stays visible while its tower leaves the lookup map during an asynchronous fallback bake',()=>{
 const tower={active:true,group:{visible:true}},support={entry:meta(2),active:true,group:{visible:false},supportVisibilityDependents:new Set([tower]),meshes:[]};
 const map=new Map([[uid(2),support]]);retainVisibleNativeSupports(map);assert.equal(support.group.visible,true);
 tower.active=false;support.group.visible=false;retainVisibleNativeSupports(map);assert.equal(support.group.visible,false);
});
