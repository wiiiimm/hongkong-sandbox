import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULT_HAZE,HAZE_STORAGE_KEY,CLEAR_WEATHER_DENSITY,normaliseHaze,readHaze,saveHaze,hazePresentation} from '../atmosphere.js';
import {weatherAtmosphere} from '../weather.js';
import {DEFAULT_WEATHER} from '../weather-data.js';
test('clear removes background fog in city and Stargaze; stronger haze is monotonic',()=>{
 for(const stargazing of [false,true]){
  const clear=hazePresentation({amount:0,stargazing});assert.equal(clear.fogDensity,0);assert.equal(clear.limitingMagnitude,6);
  let lastDensity=-1,lastMagnitude=Infinity;
  for(const amount of [0,.2,.35,.5,.8,1]){const a=hazePresentation({amount,stargazing});assert.ok(a.fogDensity>lastDensity);assert.ok(a.limitingMagnitude<=lastMagnitude);lastDensity=a.fogDensity;lastMagnitude=a.limitingMagnitude;}
 }
 assert.equal(hazePresentation({amount:.5}).fogDensity,CLEAR_WEATHER_DENSITY);assert.equal(hazePresentation({amount:.5}).limitingMagnitude,2.8);
});
test('visual clarity preserves intentional manual/live weather fog and all input observations',()=>{
 const weather={...DEFAULT_WEATHER,rain:.6,fog:.7},before=structuredClone(weather),density=weatherAtmosphere(weather).fogDensity;
 const clear=hazePresentation({amount:0,weatherDensity:density});assert.ok(clear.fogDensity>0);assert.equal(clear.fogDensity,density-CLEAR_WEATHER_DENSITY);assert.deepEqual(weather,before);
 assert.equal(hazePresentation({amount:0,weatherDensity:density,stargazing:true}).fogDensity,0);
});
test('saved preference survives reload and invalid/unavailable storage safely falls back',()=>{
 const map=new Map(),storage={getItem:k=>map.get(k)??null,setItem:(k,v)=>map.set(k,v)};
 assert.equal(readHaze(storage),DEFAULT_HAZE);saveHaze(storage,0);assert.equal(readHaze(storage),0);saveHaze(storage,.78);assert.equal(readHaze(storage),.78);
 storage.setItem(HAZE_STORAGE_KEY,'invalid');assert.equal(readHaze(storage),DEFAULT_HAZE);storage.setItem(HAZE_STORAGE_KEY,'Infinity');assert.equal(readHaze(storage),DEFAULT_HAZE);
 const denied={getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}};assert.equal(readHaze(denied),DEFAULT_HAZE);assert.doesNotThrow(()=>saveHaze(denied,.2));
 assert.equal(normaliseHaze(-2),0);assert.equal(normaliseHaze(2),1);assert.equal(normaliseHaze(NaN),DEFAULT_HAZE);
});
test('measured visibility replaces estimated weather extinction without counting rain or fog twice',()=>{
 for(const stargazing of [false,true]){
  const observed=hazePresentation({amount:0,weatherDensity:.01,visibilityMetres:12000,stargazing});
  assert.equal(observed.source,'visibility');assert.equal(observed.fogDensity,Math.sqrt(-Math.log(.02))/12000);
  const clear=hazePresentation({amount:0,visibilityMetres:null,stargazing});assert.equal(clear.source,'manual');assert.equal(clear.fogDensity,0);
 }
 for(const visibilityMetres of [0,-1,NaN,Infinity])assert.equal(hazePresentation({visibilityMetres}).source,'manual');
});
