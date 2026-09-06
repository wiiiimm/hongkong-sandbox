import test from 'node:test';
import assert from 'node:assert/strict';
import {Navigation,waterAllowsStep} from '../navigation.js';
import {tidePlot} from '../tide-graph.js';
test('resting tide prevents entering submerged ground but permits retreat if water rises',()=>{
 assert.equal(waterAllowsStep(1.2,.3),true);assert.equal(waterAllowsStep(1.2,2),false);
 assert.equal(waterAllowsStep(1.5,2,1.2),true);assert.equal(waterAllowsStep(1.2,2,1.2),true);assert.equal(waterAllowsStep(1,2,1.2),false);
 assert.equal(waterAllowsStep(2,2),true);assert.equal(waterAllowsStep(NaN,2),false);assert.equal(waterAllowsStep(2,NaN),false);
});
test('walk arrivals choose dry ground without modifying the terrain',()=>{
 const sampler={contains:()=>true,raw:()=>1.2,height:(x,z)=>x>5?3:1.2};
 const nav={sampler,index:{collision:()=>false},waterLevel:()=>2};
 const safe=Navigation.prototype.safeGround.call(nav,0,0);assert.ok(safe.x>5);assert.equal(safe.y,3);assert.equal(sampler.height(0,0),1.2);
 assert.equal(Navigation.prototype.safeGround.call({...nav,waterLevel:()=>4},0,0),null);
});
test('tide plot uses a 24-hour time window and leaves missing prediction hours disconnected',()=>{
 const time=Date.parse('2026-09-06T04:00:00Z'),series=Array.from({length:27},(_,i)=>({time:time+(i-13)*3600000,heightHKPD:i===13?null:1+Math.sin(i/4)}));
 const p=tidePlot({time:new Date(time).toISOString(),heightHKPD:1.2,series});assert.ok(p);assert.equal(p.markerX,132);assert.equal((p.path.match(/M/g)||[]).length,2);assert.ok(Number.isFinite(p.markerY));assert.equal(tidePlot(null),null);assert.equal(tidePlot({time,series:[]}),null);
 const gap=tidePlot({time,heightHKPD:1,series:[{time:time-3600000,heightHKPD:1},{time:time+3600000,heightHKPD:2}]});assert.equal((gap.path.match(/M/g)||[]).length,2);
});
