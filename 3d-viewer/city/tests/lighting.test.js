import test from 'node:test';
import assert from 'node:assert/strict';
import {cityLighting,buildingLighting,formatHour,normaliseHour,LIGHT_PROFILES} from '../lighting.js';

test('the night crosses midnight continuously and reaches its quietest point at 4 am',()=>{
 for(let h=22;h<28;h+=.125){
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

test('homes peak at 10 pm, offices leave from 6 pm and shops close from 9 to 11 pm',()=>{
 const at=h=>cityLighting(h).activity;
 for(const h of [18,19,20,21])assert.ok(at(h+1)[0]>at(h)[0],`homes return at ${h+1}`);
 assert.ok(at(21)[0]-at(20)[0]>.1,'more people return around 9 pm');
 for(let h=0;h<24;h+=.125)assert.ok(at(h)[0]<=at(22)[0],'10 pm is the residential peak');
 assert.ok(at(23)[0]<at(22)[0]&&at(23)[0]>.6,'sleep begins around 11 pm');
 assert.ok(at(0)[0]<at(23)[0]&&at(4)[0]<at(0)[0]);
 for(const h of [18,19,20,21,22,23,24])assert.ok(at(h)[1]<at(h-1)[1],`offices wind down at ${h}`);
 assert.ok(at(20)[1]>.3,'some offices work until 8 pm');
 assert.ok(at(0)[1]<.1&&at(4)[1]>0,'midnight mostly dark with all-night exceptions');
 assert.ok(at(21)[4]<at(20)[4]&&at(21)[4]>.8,'shops begin closing around 9 pm');
 assert.ok(at(22)[4]<at(21)[4]&&at(23)[4]<.3,'most retail closes by 11 pm');
 assert.ok(at(0)[4]>at(4)[4]&&at(4)[4]>0,'late retail and a small overnight reserve');
 assert.ok(at(0)[0]<.06&&at(4)[0]<.01,'midnight is quiet and fewer than 1% of home windows remain by 4 am');
 for(let p=0;p<LIGHT_PROFILES.length;p++)assert.ok(at(4)[p]<at(0)[p]*.25,'4 am is substantially quieter than midnight');
 assert.equal(buildingLighting({id:'way/3',kind:'retail',base:0}).profile,4);
});
