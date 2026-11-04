import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from '../../vendor/three.module.js';
import {createTideData,parseTideDay,sampleTide,tidePrediction,chartDatumToHKPD,hongKongDay,chooseTideStation,tideURL} from '../tide-data.js';
import {createTidalWater} from '../tidal-water.js';
import {applyWaterSurfaceShader} from '../../water-surface.js';
import {applyShorelineShader,createWaterNoiseTexture} from '../../shoreline-surface.js';
import {tideAt} from '../../tide-series.js';
const HOUR=3600000,DAY=24*HOUR;
const anchor=Date.parse('2026-09-06T12:30:00+08:00');
const fixture=(station='QUB',day=6)=>JSON.parse(fs.readFileSync(new URL(`./fixtures/tides/hhot-${station.toLowerCase()}-2026-09-0${day}.json`,import.meta.url)));
const response=(payload,status=200)=>({ok:status===200,status,json:async()=>payload});
const feeds=async url=>{const q=new URL(url).searchParams;return response(fixture(q.get('station'),+q.get('day')));};
const day={year:2026,month:9,day:6};

test('Official HHOT fixtures use hours 01–24 HKT, correct CD to HKPD sign, and real station coordinates',()=>{
 const payload=fixture(),series=parseTideDay(payload,day);
 assert.equal(series.length,24);assert.equal(series[0].time,Date.parse('2026-09-06T01:00:00+08:00'));
 assert.equal(series[23].time,Date.parse('2026-09-07T00:00:00+08:00'));
 assert.equal(series[0].heightCD,+payload.data[0][2]);assert.equal(series[0].heightHKPD,+payload.data[0][2]-.146);
 assert.equal(chartDatumToHKPD(.146),0);assert.equal(chartDatumToHKPD(null),null);
 assert.equal(chooseTideStation({lat:22.267,lon:114.0}).code,'CCH');assert.equal(chooseTideStation({lat:22.29,lon:114.2}).code,'QUB');
 assert.deepEqual(hongKongDay(Date.parse('2026-12-31T16:00:00Z')),{year:2027,month:1,day:1});
 assert.deepEqual(hongKongDay(Date.parse('2026-12-31T16:00:00Z'),-1),{year:2026,month:12,day:31});
 assert.throws(()=>tideURL('BAD',day));
});
test('Strict parser and interpolation refuse schema changes, missing cells, gaps and expired forecasts',()=>{
 const payload=fixture();assert.throws(()=>parseTideDay({...payload,fields:['MM','DD']},day));assert.throws(()=>parseTideDay(payload,{...day,day:1}));
 payload.data[0][3]='';payload.data[0][4]=null;payload.data[0][5]='***';
 const series=parseTideDay(payload,day);for(const i of [1,2,3])assert.equal(series[i].heightHKPD,null);
 assert.equal(sampleTide(series,series[0].time+HOUR/2),null);
 assert.equal(sampleTide(series,series[0].time-1),null);assert.equal(sampleTide(series,series.at(-1).time+1),null);
 assert.equal(sampleTide([series[5],series[7]],series[6].time),null);
 assert.equal(sampleTide(series,series[5].time),series[5].heightCD);
 assert.equal(sampleTide(series,series[5].time+HOUR/2),(series[5].heightCD+series[6].heightCD)/2);
 const falling=tidePrediction([{time:0,heightCD:2},{time:HOUR,heightCD:1}],HOUR/2);assert.equal(falling.trend,'falling');
});
test('Live current-clock forecast, request bounds, station switching and exact manual restoration',async()=>{
 let time=anchor,calls=0;const data=createTideData({now:()=>time,fetchImpl:async url=>{calls++;return feeds(url);}});
 assert.equal(calls,0);data.setManual(1.77);await data.setLive(true);
 assert.equal(calls,3);assert.equal(data.state.status,'live');assert.equal(data.state.prediction.series.length,72);
 assert.equal(data.state.prediction.time,time);assert.equal(data.state.restingLevelHKPD,(.72+.73)/2-.146);
 await data.refresh();assert.equal(calls,3,'rapid refresh clicks are bounded');
 time+=HOUR;data.update();await data.refresh();assert.equal(calls,6);assert.equal(data.state.prediction.time,time);
 await data.setStation('CCH');assert.equal(calls,9);assert.equal(data.state.station.code,'CCH');assert.equal(data.state.prediction.station.code,'CCH');
 await data.setLive(false);assert.equal(data.state.restingLevelHKPD,1.77);assert.equal(data.state.prediction,null);
 data.setManual(20);assert.equal(data.state.restingLevelHKPD,4);data.setManual(-20);assert.equal(data.state.restingLevelHKPD,-1);data.setManual(null);assert.equal(data.state.restingLevelHKPD,-1);
 data.dispose();
});
test('Late requests cannot overwrite Manual or another station; disposal cancels pending requests',async()=>{
 const pending=[];let signals=[];const data=createTideData({now:()=>anchor,fetchImpl:(url,{signal})=>{signals.push(signal);return new Promise(resolve=>pending.push(()=>feeds(url).then(resolve)));}});
 const old=data.setLive(true);assert.equal(data.state.status,'loading');await data.setLive(false);data.setManual(2.25);
 assert.ok(signals.every(s=>s.aborted));for(const resolve of pending.splice(0))resolve();await old;
 assert.equal(data.state.mode,'manual');assert.equal(data.state.restingLevelHKPD,2.25);assert.equal(data.state.prediction,null);
 // Station transition invalidates the previous generation even if a fetch ignores abort.
 const cch=data.setStation('CCH');await cch;const live=data.setLive(true);const delayed=pending.splice(0);
 const changed=data.setStation('QUB');for(const resolve of delayed)resolve();await live;await changed;
 assert.equal(data.state.station.code,'QUB');assert.equal(data.state.prediction,null);
 data.dispose();assert.ok(signals.every(s=>s.aborted));
});
test('Offline requests never become observations; recovery and missing graph hours stay explicit',async()=>{
 let time=anchor,fail=true,failDay=0,calls=0;
 const data=createTideData({now:()=>time,fetchImpl:async url=>{calls++;if(fail||+new URL(url).searchParams.get('day')===failDay)throw new Error('Offline fixture');return feeds(url);}});
 data.setManual(.8);await data.setLive(true);assert.equal(data.state.status,'error');assert.equal(data.state.restingLevelHKPD,.8);assert.equal(data.state.basis,'manual-fallback');assert.equal(data.state.prediction,null);
 await data.refresh();assert.equal(calls,3);time+=10000;fail=false;await data.refresh();assert.equal(data.state.status,'live');assert.equal(data.state.basis,'prediction');assert.equal(data.state.predictionKind,'astronomical');
 const retained=data.state.prediction.fetchedAt;time+=60000;fail=true;await data.refresh();assert.equal(data.state.status,'stale');assert.match(data.state.error,/Offline fixture/);assert.equal(data.state.prediction.fetchedAt,retained,'failed refresh cannot relabel old data freshly retrieved');
 // Expiry is rejected rather than clamping the last predicted height indefinitely.
 time+=4*DAY;data.update({paused:true});data.update({paused:false});await data.refresh();assert.equal(data.state.restingLevelHKPD,.8);assert.equal(data.state.basis,'manual-fallback');
 data.dispose();
 const partial=createTideData({now:()=>anchor,fetchImpl:async url=>+new URL(url).searchParams.get('day')===5?response({}):feeds(url)});
 await partial.setLive(true);assert.ok(['partial','stale'].includes(partial.state.status));assert.ok(Number.isFinite(partial.state.prediction.heightHKPD));assert.equal(partial.state.prediction.series[0].heightCD,null);partial.dispose();
});
test('Pause and Stargaze hold tide level and prevent refresh, then resume current time',async()=>{
 let time=anchor,calls=0;const data=createTideData({now:()=>time,fetchImpl:async url=>{calls++;return feeds(url);}});
 await data.setLive(true);const level=data.state.restingLevelHKPD;
 data.update({suspended:true});time+=HOUR;data.update({suspended:true});await data.refresh();assert.equal(data.state.restingLevelHKPD,level);assert.equal(calls,3);
 data.update({paused:true});assert.equal(data.state.restingLevelHKPD,level);
 data.update();await data.refresh();assert.notEqual(data.state.restingLevelHKPD,level);assert.equal(calls,6);data.dispose();
});
test('Original tide and complete water shader extraction retain byte-equivalent behaviour',()=>{
 const baseline=JSON.parse(fs.readFileSync(new URL('./fixtures/tides/original-water-functions.json',import.meta.url)));
 const legacy=new Function(baseline.functions.tideAt+';return tideAt;')();
 for(const values of [[1,2,3],[NaN,1,2],[null,1,2]])for(const hour of [-3,1,1.5,2.2,3,9])assert.equal(tideAt(values,hour),legacy(values,hour));
 const current=fs.readFileSync(new URL('../../main.js',import.meta.url),'utf8'),start=current.indexOf('function attachTerrainFX('),end=current.indexOf('\n\n',current.indexOf('  tidalMats.push(mat);',start));
 const makeAttach=body=>new Function('THREE','CLOUD_SHADOW_TEX','tidalMats','applyWaterSurfaceShader','applyShorelineShader',body+';return attachTerrainFX;')(THREE,null,[],applyWaterSurfaceShader,applyShorelineShader);
 for(const water of [false,true])for(const wet of [false,true]){
  const originalMat=new THREE.MeshStandardMaterial(),sharedMat=new THREE.MeshStandardMaterial();
  makeAttach(baseline.functions.attachTerrainFX)(originalMat,wet,water);makeAttach(current.slice(start,end))(sharedMat,wet,water);
  const makeShader=()=>({uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader});
  const a=makeShader(),b=makeShader();originalMat.onBeforeCompile(a);sharedMat.onBeforeCompile(b);
  assert.equal(a.vertexShader,b.vertexShader);assert.equal(a.fragmentShader,b.fragmentShader);assert.deepEqual(a.uniforms,b.uniforms);
 }
 // The extracted texture factory retains the original random calls and gradient draw order.
 function drawing(){const calls=[],ctx={fillRect:(...a)=>calls.push(['fillRect',...a]),createRadialGradient:(...a)=>{calls.push(['gradient',...a]);return {addColorStop:(...b)=>calls.push(['stop',...b])};}},canvas={getContext:()=>ctx};return {calls,document:{createElement:()=>canvas}};}
 const before=drawing(),after=drawing();
 new Function('THREE','document','Math',baseline.functions.cloudTexture+';return CLOUD_SHADOW_TEX;')(THREE,before.document,{random:()=>.4});
 createWaterNoiseTexture({documentImpl:after.document,random:()=>.4});assert.deepEqual(before.calls,after.calls);
});
test('Water keeps real resting metres separate from illustrative heave, with pause, reduction and disposal',()=>{
 const water=createTidalWater(),camera=new THREE.PerspectiveCamera();camera.updateMatrixWorld();
 const settings={waves:1,wind:1,rain:1};water.setLevel(-.6);let max=0,min=0;
 for(let i=0;i<500;i++){water.update(.05,{settings,camera,sunDirection:new THREE.Vector3(0,1,0)});const s=water.state;assert.equal(s.restingLevelHKPD,-.6);assert.ok(Math.abs(s.renderedLevelHKPD-s.restingLevelHKPD)<=.18);max=Math.max(max,s.waveOffset);min=Math.min(min,s.waveOffset);}
 assert.ok(max>.17&&min<-.17);assert.equal(water.levelAt(0,0),water.state.renderedLevelHKPD);
 const before=water.state;water.update(.1,{settings,paused:true});assert.equal(water.state.shaderTime,before.shaderTime);assert.equal(water.state.waveOffset,before.waveOffset);
 water.update(.1,{settings,suspended:true});assert.equal(water.state.shaderTime,before.shaderTime);
 water.update(.1,{settings,reducedMotion:true});assert.equal(water.state.shaderTime,before.shaderTime);assert.equal(water.state.waveOffset,0);assert.equal(water.state.rainSpark,0);
 water.update(.1,{settings:{...settings,waves:0}});assert.equal(water.state.waveOffset,0);assert.equal(water.state.waveNormalAmplitude,.05);
 const shader={uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader};water.material.onBeforeCompile(shader);
 assert.match(shader.vertexShader,/#include <logdepthbuf_vertex>/);assert.match(shader.fragmentShader,/#include <logdepthbuf_fragment>/);assert.match(shader.fragmentShader,/uSunDirV/);
 let geometry=0,material=0;water.mesh.geometry.addEventListener('dispose',()=>geometry++);water.material.addEventListener('dispose',()=>material++);water.dispose();water.dispose();assert.equal(geometry,1);assert.equal(material,1);
});

test('Shoreline attaches once to existing terrain, tracks the rendered sea and releases owned texture',()=>{
 const water=createTidalWater(),terrain=new THREE.Group(),material=new THREE.MeshStandardMaterial();
 terrain.add(new THREE.Mesh(new THREE.PlaneGeometry(),material),new THREE.Mesh(new THREE.PlaneGeometry(),material));
 const texture=new THREE.DataTexture(new Uint8Array([255,255,255,255]),1,1);const original=material.onBeforeCompile;
 water.attachShoreline(terrain,{texture});water.attachShoreline(terrain,{texture});assert.equal(water.state.shorelineMaterials,1);
 const shader={uniforms:{},vertexShader:THREE.ShaderLib.standard.vertexShader,fragmentShader:THREE.ShaderLib.standard.fragmentShader};material.onBeforeCompile(shader);
 assert.match(shader.fragmentShader,/float d = vWpos.y - uWaterY/);assert.equal(shader.uniforms.uBand.value,.6);
 water.setLevel(2.1);water.update(.1,{settings:{wind:1,waves:1}});assert.equal(shader.uniforms.uWaterY.value,water.state.renderedLevelHKPD);
 const time=shader.uniforms.uTime.value;water.update(.1,{suspended:true});assert.equal(shader.uniforms.uTime.value,time);
 water.dispose();assert.equal(material.onBeforeCompile,original);assert.equal(water.state.shorelineMaterials,0);
});
