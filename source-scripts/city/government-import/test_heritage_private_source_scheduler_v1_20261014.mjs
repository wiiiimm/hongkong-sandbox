import assert from 'node:assert/strict';
import {installPrivateSourceScheduler} from './heritage_private_source_scheduler_v1_20261014.mjs';
let callback=null,clears=0,calls=[],paused=true,throwPlan=false;
const original=value=>{paused=value;calls.push(['pause',value]);},officialModels={setLoadingPaused:original,plan(camera,o){if(throwPlan)throw Error('synthetic planning failure');calls.push(['plan',camera,o]);}},camera={synthetic:true},timers={innerWidth:1600,innerHeight:1100,setInterval(cb,ms){assert.equal(ms,200);callback=cb;return 7;},clearInterval(id){assert.equal(id,7);clears++;}};
const s=installPrivateSourceScheduler({officialModels,camera},timers);s.start('landsd/165054:0');assert.equal(paused,false);assert.equal(calls.at(-1)[2].selectedUid,'landsd/165054:0');assert.equal(calls.at(-1)[2].viewportWidth,1600);assert.equal(calls.at(-1)[2].force,true);
// The actual app's next paused frame cannot undo private unpause while loading.
officialModels.setLoadingPaused(true);assert.equal(paused,false);callback();assert.equal(calls.at(-1)[2].selectedUid,'landsd/165054:0');
s.start('landsd/57455:0');assert.equal(clears,1);callback();assert.equal(calls.at(-1)[2].selectedUid,'landsd/57455:0');
throwPlan=true;callback();assert.match(s.lastError,/synthetic planning failure/);s.stop();assert.equal(clears,2);assert.equal(officialModels.setLoadingPaused,original);officialModels.setLoadingPaused(true);assert.equal(paused,true);
assert.throws(()=>installPrivateSourceScheduler({officialModels,camera},timers).start(''),/Exact requested UID/);
console.log(JSON.stringify({passed:true,cases:5,privateSchedulingOnly:true,productionModelArraysDBBrowser:false}));
