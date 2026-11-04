import test from 'node:test';
import assert from 'node:assert/strict';
import {activationGroupMembers} from '../model-activation-groups.js';
import {supportedModelPlan,retainVisibleNativeSupports} from '../model-support.js';
const uid=n=>'landsd/'+n+':0',group=[uid(1),uid(2)];
const entry=(n,activationGroup=n<=2?group:undefined,supportDependencies=[])=>({uid:uid(n),activationGroup,supportDependencies});
const limits={count:8,geometryBytes:800,residentBytes:800,triangles:800,drawCalls:8},cost=()=>({geometryBytes:100,residentBytes:100,triangles:100,drawCalls:1});
const plan=(models,roots=[uid(1)],options={})=>supportedModelPlan(roots,new Map(models.map(m=>[m.uid,m])),{...limits,...options},cost,()=>true);
test('group declarations are complete, canonical and never physical support metadata',()=>{
 assert.deepEqual(activationGroupMembers(entry(2,[uid(2),uid(1)])),group);
 for(const value of [[uid(1)],[uid(1),uid(1)],[uid(1),'bad'],[uid(2),uid(3)]])assert.throws(()=>activationGroupMembers(entry(1,value)),/Invalid/);
 const result=plan([entry(1),entry(2)]);assert.deepEqual(result.wanted,group);assert.equal(result.used.triangles,200);
});
test('missing or inconsistent peer blocks the complete group',()=>{
 for(const models of [[entry(1)],[entry(1),entry(2,[uid(2),uid(3)])]])assert.deepEqual(plan(models).wanted,[]);
});
test('internal physical support ordering survives atomic availability without allowing physical cycles',()=>{
 assert.deepEqual(plan([entry(1,group,[{uid:uid(2),state:'candidate'}]),entry(2)]).wanted,[uid(2),uid(1)]);
 assert.deepEqual(plan([entry(1,group,[{uid:uid(2),state:'candidate'}]),entry(2,group,[{uid:uid(1),state:'candidate'}])]).wanted,[]);
});
test('group-collapsed physical dependency cycles cannot deadlock decoding',()=>{
 const models=[entry(1,group,[{uid:uid(3),state:'candidate'}]),entry(2),entry(3,undefined,[{uid:uid(2),state:'candidate'}])];
 const result=plan(models);assert.deepEqual(result.wanted,[]);assert.match(result.blocked.get(uid(1)),/Cyclic/);
});
test('external physical support is admitted first and shared peers are counted once',()=>{
 const models=[entry(1,group,[{uid:uid(3),state:'installed'}]),entry(2),entry(3,undefined)];
 assert.deepEqual(plan(models,[uid(2),uid(1)]).wanted,[uid(3),uid(1),uid(2)]);
});
test('whole group obeys every existing device budget',()=>{
 for(const [key,value]of Object.entries({count:1,geometryBytes:199,residentBytes:199,triangles:199,drawCalls:1}))assert.deepEqual(plan([entry(1),entry(2)],undefined,{[key]:value}).wanted,[],key);
});
test('a surveyed fallback cannot simultaneously be an active group member',()=>{
 assert.deepEqual(plan([entry(1,group,[{uid:uid(2),state:'surveyed-footprint-fallback'}]),entry(2)]).wanted,[]);
});
test('visible group retains all active peers across source-tile boundaries',()=>{
 const details=new Map([1,2,3].map(n=>[uid(n),{entry:entry(n,n===3?undefined:group),active:true,group:{visible:n===1},meshes:[]} ]));
 retainVisibleNativeSupports(details);assert.deepEqual([...details.values()].map(d=>d.group.visible),[true,true,false]);
});
