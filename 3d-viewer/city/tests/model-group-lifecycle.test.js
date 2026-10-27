import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import {OfficialModelLayer} from '../official-models.js';
import {modelBudget} from '../official-model-assets.js';
const uid=n=>'landsd/'+n+':0',members=[uid(1),uid(2)],tick=()=>new Promise(r=>setTimeout(r,0));
const meta=(n,group=members,deps=[])=>({uid:uid(n),activationGroup:group,supportDependencies:deps,worldBounds:[[0,2,0],[10,12,10]],priority:'landmark',decodedGeometryBytes:1000,indexedVertices:24,triangles:12});
const camera=()=>{const c=new THREE.PerspectiveCamera(50,1,1,100000);c.position.set(5,10,100);c.lookAt(5,7,5);c.updateProjectionMatrix();return c;};
async function until(fn){for(let i=0;i<300&&!fn();i++)await tick();assert.ok(fn(),'lifecycle made progress');}
function fixture({entries=[meta(1),meta(2)],download=async()=>{},commit=async()=>true,budget=modelBudget}={}){
 const log=[],frames=[],disposed=[],revealed=[],buildings=new Map(entries.map(m=>[m.uid,{uid:m.uid,modelGeometry:null,tile:'0_0'}]));
 const stream={detailedModels:new Map(),lighting:{},getLoadedBuilding(key){return this.detailedModels.get(key)?.record||buildings.get(key);},sync(){},async setDetailedModels(changes,{signal}={}){
  log.push('prepare:'+changes.map(([uid,value])=>uid+'='+!!value).join(','));
  if(!await commit(changes,signal)||signal?.aborted)return false;
  const next=new Map(this.detailedModels);for(const [key,value]of changes){const old=next.get(key);if(old)old.active=false;if(value){value.active=true;next.set(key,value);}else next.delete(key);}this.detailedModels=next;frames.push([...next.keys()]);return true;
 },async setDetailedModel(key,value){assert.ok(!members.includes(key),'group member never switches individually');if(value){value.active=true;this.detailedModels.set(key,value);}else{const old=this.detailedModels.get(key);if(old)old.active=false;this.detailedModels.delete(key);}frames.push([...this.detailedModels.keys()]);return true;}};
 const layer=new OfficialModelLayer({stream,profile:'mobile',warmMs:0,onReveal:entry=>revealed.push(entry.record.uid),loadAsset:async(m,b,l,options)=>{
  log.push('download:'+m.uid);await download(m.uid,options.signal);if(options.signal.aborted)throw new DOMException('Aborted','AbortError');
  const group=new THREE.Group(),geometry=new THREE.BufferGeometry();geometry.addEventListener('dispose',()=>disposed.push(m.uid));group.add(new THREE.Mesh(geometry,new THREE.MeshBasicMaterial()));
  return {entry:m,group,record:{...buildings.get(m.uid),modelGeometry:{}},meshes:[],active:false,budget:budget(m)};
 }});
 for(const m of entries)layer.models.set(m.uid,m);
 return {layer,stream,log,frames,disposed,revealed,buildings};
}
test('single-slot mobile loader decodes every peer without deadlock and exposes only the complete group',async t=>{
 let release;const f=fixture({download:async key=>{if(key===uid(2))await new Promise(r=>release=r);}});t.after(()=>f.layer.dispose());
 f.layer.plan(camera(),{force:true});await until(()=>release);assert.equal(f.layer.cache.concurrency,1);assert.equal(f.stream.detailedModels.size,0);assert.equal(f.layer.cache.entries.size,0);
 release();await f.layer.cache.waitFor(members);assert.deepEqual(f.frames,[members]);assert.deepEqual(f.revealed,members);assert.deepEqual(f.log.filter(x=>x.startsWith('download:')),members.map(x=>'download:'+x));assert.equal(f.layer.activationGroups.reservations.size,0);
});
test('a failed member retains every basic, disposes decoded peers and requires one group Retry',async t=>{
 let fail=true;const f=fixture({download:async key=>{if(key===uid(2)&&fail)throw new Error('peer HTTP503');}});t.after(()=>f.layer.dispose());
 f.layer.plan(camera(),{force:true});await until(()=>!f.layer.cache.running.size);assert.equal(f.stream.detailedModels.size,0);assert.equal(f.layer.cache.entries.size,0);assert.deepEqual(f.disposed,[uid(1)]);assert.ok(members.every(id=>f.layer.cache.errors.has(id)));
 fail=false;await f.layer.retry();await f.layer.cache.waitFor(members);assert.deepEqual(f.frames,[members]);
});
test('camera travel cancels the whole pending group and never attaches a late peer',async t=>{
 let release;const f=fixture({download:async key=>{if(key===uid(2))await new Promise(r=>release=r);}});t.after(()=>f.layer.dispose());const c=camera();
 f.layer.plan(c,{force:true});await until(()=>release);c.position.set(50000,100,50000);c.lookAt(60000,100,50000);f.layer.plan(c,{force:true});release();await until(()=>!f.layer.cache.running.size);
 assert.equal(f.stream.detailedModels.size,0);assert.equal(f.layer.cache.entries.size,0);assert.deepEqual(f.frames,[]);assert.equal(f.layer.activationGroups.reservations.size,0);
});
test('internal physical supports activate together while an external support still activates first',async t=>{
 const group=[uid(1),uid(2)],entries=[meta(1,group,[{uid:uid(2),state:'candidate'},{uid:uid(3),state:'installed'}]),meta(2),meta(3,undefined)];entries[2].activationGroup=undefined;
 const f=fixture({entries});t.after(()=>f.layer.dispose());f.layer.plan(camera(),{force:true});await f.layer.cache.waitFor([uid(1)]);
 assert.deepEqual(f.frames,[[uid(3)],[uid(3),...members]]);
});
test('whole-group fallback is delayed until every model can retire safely',async t=>{
 let release;const f=fixture({commit:async changes=>{if(changes.every(([,v])=>!v))await new Promise(r=>release=r);return true;}});t.after(()=>f.layer.dispose());const c=camera();
 f.layer.plan(c,{force:true});await f.layer.cache.waitFor(members);c.position.set(50000,100,50000);c.lookAt(60000,100,50000);f.layer.plan(c,{force:true});await until(()=>release);
 assert.equal(f.stream.detailedModels.size,2);assert.equal(f.layer.retiring.size,2);release();await Promise.allSettled([...f.layer.retiring.values()]);assert.deepEqual(f.frames,[members,[]]);assert.ok(members.every(id=>f.disposed.includes(id)));
});
test('failed fallback keeps the complete original group accounted until Retry succeeds',async t=>{
 let fail=true;const f=fixture({commit:async changes=>{if(changes.every(([,v])=>!v)&&fail)throw new Error('fallback failed');return true;}});t.after(()=>f.layer.dispose());const c=camera();
 f.layer.plan(c,{force:true});await f.layer.cache.waitFor(members);c.position.set(50000,100,50000);c.lookAt(60000,100,50000);f.layer.plan(c,{force:true});await until(()=>f.layer.releaseFailures.size===2&&!f.layer.retiring.size);
 assert.equal(f.stream.detailedModels.size,2);assert.equal(f.disposed.length,0);assert.ok(f.layer.stats.residentBytes>0);fail=false;await f.layer.retry();assert.equal(f.stream.detailedModels.size,0);assert.equal(f.layer.releaseFailures.size,0);
});
test('decoded peak over budget cannot partially install a group',async t=>{
 const f=fixture({budget:m=>({...modelBudget(m),residentBytes:100*1024*1024})});t.after(()=>f.layer.dispose());f.layer.plan(camera(),{force:true});await until(()=>!f.layer.cache.running.size);
 assert.equal(f.stream.detailedModels.size,0);assert.equal(f.layer.cache.entries.size,0);assert.deepEqual(f.frames,[]);assert.equal(f.layer.activationGroups.reservations.size,0);assert.ok(f.disposed.length>=1);
});
test('Base-only selection cancels and restores the complete source family',async t=>{
 const f=fixture();t.after(()=>f.layer.dispose());f.layer.plan(camera(),{force:true});await f.layer.cache.waitFor(members);f.layer.setQuality('base');await until(()=>!f.layer.retiring.size);assert.equal(f.stream.detailedModels.size,0);assert.deepEqual(f.frames,[members,[]]);
});
