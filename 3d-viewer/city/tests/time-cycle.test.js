import test from 'node:test';
import assert from 'node:assert/strict';
import {advanceTimelapse,timeCycleState,normaliseTimelapseSpeed,timelapseDuration,timeCycleElapsed} from '../time-cycle.js';
import {dateFromHKT,hktParts,getSkyState} from '../sky-time.js';
import {cityLighting} from '../lighting.js';
const active={enabled:true,mode:'manual'};
test('Existing default remains one hour per eight real seconds, with useful bounded speeds',()=>{
 const start=dateFromHKT('2026-09-06',15).valueOf();assert.equal(advanceTimelapse(start,8,active)-start,3600000);
 assert.equal(normaliseTimelapseSpeed(-5),1);assert.equal(normaliseTimelapseSpeed(500),120);assert.equal(normaliseTimelapseSpeed(null),7.5);assert.equal(normaliseTimelapseSpeed(''),7.5);assert.equal(normaliseTimelapseSpeed('30.5'),30.5);
 assert.equal(timelapseDuration(1),'24m');assert.equal(timelapseDuration(7.5),'3m 12s');assert.equal(timelapseDuration(30),'48s');assert.equal(timelapseDuration(120),'12s');
});
test('Playback advances through HKT midnight, leap day, year end and multiple complete cycles',()=>{
 for(const [day,next]of [['2026-09-06','2026-09-07'],['2026-12-31','2027-01-01'],['2028-02-28','2028-02-29'],['2028-02-29','2028-03-01']]){
  const start=dateFromHKT(day,23+59/60).valueOf(),after=advanceTimelapse(start,1,{...active,speed:2});assert.equal(hktParts(new Date(after)).date,next);assert.equal(hktParts(new Date(after)).time,'00:01');
 }
 const start=dateFromHKT('2026-09-06',4).valueOf(),after=advanceTimelapse(start,36,{...active,speed:120});assert.equal(hktParts(new Date(after)).date,'2026-09-09');assert.equal(hktParts(new Date(after)).time,'04:00');
});
test('Pause, Stargaze, Reduced Motion and Live suspend progression without discarding speed/enabled',()=>{
 const start=dateFromHKT('2026-09-06',18).valueOf();
 for(const option of [{paused:true},{stargazing:true},{reducedMotion:true},{mode:'live'}]){
  const options={...active,speed:45,...option},s=timeCycleState(options);assert.equal(s.enabled,true);assert.equal(s.running,false);assert.equal(s.speedMinutesPerSecond,45);assert.ok(s.suspendedBy);assert.equal(advanceTimelapse(start,10,options),start);
 }
 assert.equal(advanceTimelapse(start,10,{enabled:false,speed:45}),start);assert.equal(advanceTimelapse(start,10,{...active,speed:45})-start,27000000);
 for(const dt of [-1,NaN,Infinity,0])assert.equal(advanceTimelapse(start,dt,active),start);
});
test('Continuous simulated time drives the existing sun position and distinct building sleep schedules',()=>{
 const start=dateFromHKT('2026-09-06',8).valueOf(),noon=advanceTimelapse(start,8,{...active,speed:30}),evening=advanceTimelapse(noon,12,{...active,speed:30}),late=advanceTimelapse(evening,20,{...active,speed:30});
 const dates=[start,noon,evening,late].map(n=>new Date(n));assert.deepEqual(dates.map(d=>hktParts(d).time),['08:00','12:00','18:00','04:00']);
 const sky=dates.map(d=>getSkyState(d,22.28,114.16));assert.ok(sky[0].sun.bearing<sky[1].sun.bearing&&sky[1].sun.bearing<sky[2].sun.bearing);assert.ok(sky[3].sun.altitude<0);
 const home=cityLighting(20),sleep=cityLighting(4);assert.ok(home.activity[0]>sleep.activity[0]);assert.ok(home.activity[1]<home.activity[0]);assert.ok(sleep.activity[0]>0);
});

test('Monotonic playback keeps the advertised speed at 10 fps and never catches up a pause',()=>{
 let instant=dateFromHKT('2026-09-06',12).valueOf(),tick=null;const before=instant,options={...active,speed:30},state=timeCycleState(options);
 for(let at=0;at<=1000;at+=100){const elapsed=timeCycleElapsed(at,tick,state);instant=advanceTimelapse(instant,elapsed,options);tick={at,running:state.running};}
 assert.equal(instant-before,30*60000,'one real second still equals 30 simulated minutes despite physics dt cap');
 assert.equal(timeCycleElapsed(100000,null,state),0,'visibility reset discards a hidden-tab gap');
 assert.equal(timeCycleElapsed(100000,{at:1000,running:false},state),0,'first frame after any suspension does not catch up');
 assert.equal(timeCycleElapsed(100000,{at:1000,running:true},timeCycleState({...options,paused:true})),0);
 assert.equal(timeCycleElapsed(0,{at:1000,running:true},state),0);assert.equal(timeCycleElapsed(NaN,tick,state),0);
});
