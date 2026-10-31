import test from 'node:test';
import assert from 'node:assert/strict';
import {DEFAULT_WEATHER,WEATHER_STALE_MS,WEATHER_REFRESH_MS,normaliseWeather,windBearing,windArchiveURL,parseWindCSV,parseCurrentWeather,localObservation,weatherFromObservation,createWeatherData} from '../weather-data.js';

const NOW=Date.parse('2026-09-06T06:00:00Z');
const report=()=>({updateTime:'2026-09-06T13:55:00+08:00',icon:[54],temperature:{recordTime:'2026-09-06T13:50:00+08:00',data:[{place:'Hong Kong Observatory',value:30},{place:'Chek Lap Kok',value:29}]},humidity:{data:[{place:'Hong Kong Observatory',value:96}]},rainfall:{startTime:'2026-09-06T12:45:00+08:00',endTime:'2026-09-06T13:45:00+08:00',data:[{place:'Yau Tsim Mong',max:0},{place:'Islands District',max:18}]},warningMessage:['Heavy showers nearby']});
const stations=[{name:'HK Observatory',E:836234.9,N:817936.6},{name:'Chek Lap Kok',E:810258.2,N:818745.3}];
const windText='Date time,Station,Direction,Speed,Gust\n202609061340,HK Observatory,East,18,25\n202609061340,Chek Lap Kok,Northwest,32,45\n202609061340,Missing,N/A,N/A,N/A\n202609061340,Calm,Variable,0,1\n';
const json=value=>({ok:true,status:200,json:async()=>value});
const text=value=>({ok:true,status:200,text:async()=>value});
const fetchGood=async url=>url.includes('rhrread')?json(report()):url.includes('historical-archive')?text(windText):json({stations});

test('manual controls clamp valid values, retain missing values and wrap wind from bearing',()=>{
 const value=normaliseWeather({rain:2,clouds:-1,fog:NaN,snow:'0.6',wind:Infinity,windFrom:-90});
 assert.equal(value.rain,1);assert.equal(value.clouds,0);assert.equal(value.fog,0);assert.equal(value.snow,.6);assert.equal(value.wind,DEFAULT_WEATHER.wind);assert.equal(value.windFrom,270);
 assert.equal(normaliseWeather({rain:null},{...DEFAULT_WEATHER,rain:.4}).rain,.4);
});
test('wind parses compass words, numeric bearings, calm/missing cells and source timestamps',()=>{
 assert.equal(windBearing('East-southeast'),112.5);assert.equal(windBearing('NNW'),337.5);assert.equal(windBearing('360'),0);assert.equal(windBearing('Variable'),null);assert.equal(windBearing(null),null);
 const rows=parseWindCSV(windText);assert.equal(rows.length,3);assert.equal(rows[0].speedKmh,18);assert.equal(rows[0].updatedAt,'2026-09-06T13:40:00+08:00');assert.equal(rows[2].from,null);assert.equal(rows[2].speedKmh,0);
 assert.match(windArchiveURL(NOW),/time=20260906-1345$/);
});
test('current report rejects invalid data and preserves missing measurements rather than zero',()=>{
 assert.throws(()=>parseCurrentWeather({}),/timestamp/);assert.throws(()=>parseCurrentWeather({updateTime:new Date(NOW).toISOString()}),/usable observations/);
 const payload=report();payload.temperature.data.push({place:'Bad',value:null},{place:'Also bad',value:'N/A'});payload.rainfall.data.push({place:'Unknown',max:null});
 const value=parseCurrentWeather(payload);assert.equal(value.temperature.length,2);assert.equal(value.rainfall.length,2);assert.equal(value.temperature[0].station,'HK Observatory');assert.equal(value.warning,'Heavy showers nearby');
});
test('rain follows the nearest district anchor and wind follows the nearest reporting station',()=>{
 const value=parseCurrentWeather(report()),wind=parseWindCSV(windText);
 const urban=localObservation(value,wind,stations,{x:1735,z:-1437}),island=localObservation(value,wind,stations,{x:-24242,z:-2245});
 assert.equal(urban.rainfall.district,'Yau Tsim Mong');assert.equal(urban.rainfall.millimetres,0);assert.equal(island.rainfall.district,'Islands District');assert.equal(island.wind.speedKmh,32);
 assert.equal(weatherFromObservation(urban).rain,0);assert.ok(weatherFromObservation(island).rain>.7);
 assert.equal(weatherFromObservation(urban).fog,0,'Humidity alone must not fabricate fog');
 assert.equal(weatherFromObservation({...urban,icon:83}).fog,.72);
 assert.equal(localObservation(value,[],[],null).wind,null);
});
test('live data reports original timestamps, throttles repeated refreshes, and restores manual settings',async()=>{
 let clock=NOW,calls=0;const weather=createWeatherData({now:()=>clock,fetchImpl:async(...args)=>{calls++;return fetchGood(...args);}});
 weather.setManual({rain:.6,windFrom:225});await weather.setLive(true);
 assert.equal(weather.state.status,'live');assert.equal(weather.state.observation.wind.speedKmh,18);assert.equal(weather.state.updatedAt,report().updateTime);assert.equal(weather.state.checkedAt,new Date(NOW).toISOString());
 await weather.refresh();assert.equal(calls,3);clock+=WEATHER_REFRESH_MS;await weather.poll();assert.equal(calls,5,'Station metadata is cached');
 await weather.setLive(false);assert.equal(weather.state.mode,'manual');assert.equal(weather.state.settings.rain,.6);assert.equal(weather.state.settings.windFrom,225);weather.dispose();
});
test('unavailable wind is clearly missing and never invents observed speed or waves',async()=>{
 const weather=createWeatherData({now:()=>NOW,fetchImpl:async url=>url.includes('historical-archive')?Promise.reject(new Error('CORS unavailable')):fetchGood(url)});
 await weather.setLive(true);assert.equal(weather.state.status,'live');assert.equal(weather.state.observation.wind,null);assert.match(weather.state.windError,/unavailable/);assert.equal(weather.state.settings.wind,0);assert.equal(weather.state.settings.waves,0);weather.dispose();
});
test('failed live requests retain an honest error, recover, then become stale after an outage',async()=>{
 let clock=NOW,offline=true;const weather=createWeatherData({now:()=>clock,fetchImpl:async url=>{if(offline)throw new Error('Offline');return fetchGood(url);}});
 await weather.setLive(true);assert.equal(weather.state.status,'error');assert.equal(weather.state.observation,null);assert.match(weather.state.error,/Offline/);
 clock+=11000;offline=false;await weather.refresh();assert.equal(weather.state.status,'live');assert.equal(weather.state.error,null);
 clock+=60000;offline=true;await weather.refresh();assert.equal(weather.state.status,'stale');assert.equal(weather.state.updatedAt,report().updateTime);weather.dispose();
});
test('stale or future-dated feeds cannot masquerade as fresh live observations',async()=>{
 let clock=NOW;const weather=createWeatherData({now:()=>clock,fetchImpl:fetchGood});await weather.setLive(true);clock+=WEATHER_STALE_MS;assert.equal(weather.state.status,'stale');weather.dispose();
 const future=createWeatherData({now:()=>NOW-3600000,fetchImpl:fetchGood});await future.setLive(true);assert.equal(future.state.status,'error');assert.equal(future.state.observation,null);assert.match(future.state.error,/ahead/);future.dispose();
});
test('switching to manual cancels a late live response without overwriting user settings',async()=>{
 let resolve;const pending=new Promise(r=>resolve=r);const weather=createWeatherData({now:()=>NOW,fetchImpl:url=>url.includes('rhrread')?pending:fetchGood(url)});
 const request=weather.setLive(true);weather.setManual({rain:.75});resolve(json(report()));await request;
 assert.equal(weather.state.mode,'manual');assert.equal(weather.state.settings.rain,.75);assert.equal(weather.state.observation,null);weather.dispose();
});
test('requests time out and a disposed controller never retries',async()=>{
 let calls=0;const weather=createWeatherData({now:()=>NOW,timeoutMs:5,fetchImpl:(_url,{signal})=>{calls++;return new Promise((_,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('aborted','AbortError'))));}});
 await weather.setLive(true);assert.equal(weather.state.status,'error');assert.match(weather.state.error,/timed out/);weather.dispose();await weather.setLive(true);assert.equal(calls,3);
});

test('quick manual/live toggles restart cancelled requests and retain failed status during cooldown',async()=>{
 let resolve,first=true;const pending=new Promise(r=>resolve=r);const weather=createWeatherData({now:()=>NOW,fetchImpl:url=>{if(first&&url.includes('rhrread')){first=false;return pending;}return fetchGood(url);}});
 const initial=weather.setLive(true);await weather.setLive(false);await weather.setLive(true);resolve(json(report()));await initial;assert.equal(weather.state.status,'live');weather.dispose();
 const failed=createWeatherData({now:()=>NOW,fetchImpl:async()=>{throw new Error('Offline');}});await failed.setLive(true);await failed.setLive(false);await failed.setLive(true);assert.equal(failed.state.status,'error');failed.dispose();
});
