import test from 'node:test';
import assert from 'node:assert/strict';
import {cityLighting,buildingLighting,formatHour,normaliseHour,LIGHT_PROFILES} from '../lighting.js';

test('the night crosses midnight continuously and reaches its quietest point at 4 am',()=>{
 for(let h=21;h<28;h+=.125){
  const before=cityLighting(h),after=cityLighting(h+.125);
  for(let p=0;p<LIGHT_PROFILES.length;p++)assert.ok(after.activity[p]<=before.activity[p]+1e-9,`${LIGHT_PROFILES[p]} at ${h}`);
 }
 const quiet=cityLighting(4);
 for(let h=0;h<24;h+=.125){
  const sample=cityLighting(h);
  assert.ok(sample.night>=0&&sample.night<=1);
  for(let p=0;p<LIGHT_PROFILES.length;p++)assert.ok(sample.activity[p]>=quiet.activity[p]&&sample.activity[p]<=1);
 }
 assert.equal(cityLighting(0).night,1);assert.equal(cityLighting(4).night,1);assert.equal(cityLighting(12).night,0);
 const before=cityLighting(24-1e-6),after=cityLighting(1e-6);
 for(const key of ['quiet','night','golden'])assert.ok(Math.abs(before[key]-after[key])<.00001);
 for(let p=0;p<LIGHT_PROFILES.length;p++)assert.ok(Math.abs(before.activity[p]-after.activity[p])<.00001);
 assert.equal(quiet.quiet,1);
});

test('overnight windows survive the minimum and early risers wake before daylight',()=>{
 const evening=cityLighting(20),rest=cityLighting(4),dawn=cityLighting(6);
 for(let p=0;p<LIGHT_PROFILES.length;p++){
  assert.ok(rest.activity[p]>0);
  assert.ok(rest.activity[p]<evening.activity[p]*.4);
  assert.ok(dawn.activity[p]>rest.activity[p]);
 }
 assert.ok(rest.activity[2]>rest.activity[0]*3);
 assert.ok(rest.activity[2]>rest.activity[1]*5);
 assert.ok(dawn.night>0&&dawn.night<1);
});

test('building profiles and random seeds remain stable across streaming and support every form',()=>{
 const home={id:'way/1234',kind:'apartments',base:5};
 assert.equal(buildingLighting(home).profile,0);
 assert.equal(buildingLighting({...home,kind:'office'}).profile,1);
 assert.equal(buildingLighting({...home,kind:'hotel'}).profile,2);
 assert.equal(buildingLighting({...home,kind:'hospital'}).profile,2);
 assert.equal(buildingLighting({...home,kind:'yes'}).profile,3);
 assert.deepEqual(buildingLighting(home),buildingLighting({...home,tile:'new-tile'}));
 assert.equal(buildingLighting({...home,id:'way/2345',parent:home.id}).seed,buildingLighting(home).seed);
 assert.notEqual(buildingLighting({...home,id:'way/2345'}).seed,buildingLighting(home).seed);
});

test('clock formatting wraps midnight without invalid minutes',()=>{
 assert.equal(formatHour(0),'00:00');assert.equal(formatHour(24),'00:00');assert.equal(formatHour(23.999),'00:00');
 assert.equal(formatHour(4),'04:00');assert.equal(formatHour(19.75),'19:45');assert.equal(formatHour(-1),'23:00');
 assert.equal(normaliseHour(52),4);assert.equal(normaliseHour(NaN),15);
});

test('homes welcome evening arrivals while offices dim first and retail closes later',()=>{
 const day=cityLighting(16).activity,evening=cityLighting(20).activity,late=cityLighting(22).activity,close=cityLighting(0).activity;
 assert.ok(evening[0]>day[0]*2);assert.ok(cityLighting(21).activity[0]>evening[0]);
 assert.ok(late[1]<evening[1]*.3);assert.ok(late[4]>evening[4]*.9);
 assert.ok(close[4]<late[4]*.2);assert.ok(close[0]>close[1]*4);
 assert.equal(buildingLighting({id:'way/3',kind:'retail',base:0}).profile,4);
});
