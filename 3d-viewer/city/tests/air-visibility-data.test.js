import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {ORIGIN} from '../geo.js';
import {createAirVisibilityData,parseVisibility,parseAQHI,parseAirTimestamp,HKO_VISIBILITY_URL,EPD_AQHI_URL,AIR_REFRESH_MS,VISIBILITY_STALE_MS,AQHI_STALE_MS,AIR_FUTURE_TOLERANCE_MS} from '../air-visibility-data.js';

const START=Date.parse('2026-09-07T12:00:00+08:00');
const hko=JSON.parse(await readFile(new URL('../../data/hko-stations.json',import.meta.url)));
const epd=JSON.parse(await readFile(new URL('../../data/epd-aqhi-stations.json',import.meta.url)));
const stamp=time=>new Date(time+8*3600000).toISOString().slice(0,16).replace(/[-T:]/g,'');
const iso=time=>new Date(time+8*3600000).toISOString().slice(0,19);
const vis=(time=START,rows=[['Central','17 km'],['Chek Lap Kok','40 km'],['Sai Wan Ho','30 km'],['Waglan Island','N/A']])=>({fields:['Date time','Automatic Weather Station','10 minute mean visibility'],data:rows.map(([station,value])=>[stamp(time),station,value])});
const air=(time=START)=>[{station:'Central/Western',aqhi:3,health_risk:'Low',publish_date:iso(time)},{station:'Central',aqhi:'10+',health_risk:'Serious',publish_date:iso(time)},{station:'Tung Chung',aqhi:2,health_risk:'Low',publish_date:iso(time)}];
const response=data=>({ok:true,status:200,json:async()=>data});
function fixture({visibility=vis(),aqhi=air(),timeoutMs=1000,hook}={}){
 let time=START;const calls=[];
 const fetchImpl=async(url,options)=>{calls.push({url,options});if(hook){const result=hook(url,options);if(result!==undefined)return result;}
  return response(url===HKO_VISIBILITY_URL?typeof visibility==='function'?visibility():visibility:url===EPD_AQHI_URL?typeof aqhi==='function'?aqhi():aqhi:url.endsWith('epd-aqhi-stations.json')?epd:hko);
 };
 const controller=createAirVisibilityData({fetchImpl,now:()=>time,timeoutMs});
 controller.setPosition({x:0,z:0});
 return {controller,calls,setTime:value=>time=value};
}
const tick=()=>new Promise(resolve=>setTimeout(resolve,0));

test('official visibility schema recognises units, censored endpoints, N/A, and reordered fields',()=>{
 const rows=parseVisibility(vis(START,[['Central','17 km'],['Sai Wan Ho','100 m'],['Chek Lap Kok','50 km'],['Waglan Island','N/A']]));
 assert.deepEqual(rows.map(x=>[x.visibilityMetres,x.limit]),[[17000,null],[100,'at-most'],[50000,'at-least'],[null,null]]);
 for(const bad of ['0','0 km','-1 km','Infinity km','1','51 km','',null,true,'N/A'])assert.equal(parseVisibility(vis(START,[['Central',bad]]))[0].visibilityMetres,null);
 const reordered={fields:['10 minute mean visibility','Date time','Automatic Weather Station'],data:[['500 m',stamp(START),'Central']]};
 assert.equal(parseVisibility(reordered)[0].visibilityMetres,500);
 assert.throws(()=>parseVisibility({fields:['unknown'],data:[]}));
});

test('AQHI keeps 10+ separate and never treats missing values as zero',()=>{
 assert.deepEqual(parseAQHI(air())[1],{station:'Central',updatedAt:'2026-09-07T12:00:00+08:00',aqhi:10,aqhiLabel:'10+',healthRisk:'Serious',limit:'above'});
 for(const bad of ['',null,undefined,0,-1,11,true,'N/A'])assert.equal(parseAQHI([{...air()[0],aqhi:bad}])[0].aqhi,null);
 assert.throws(()=>parseAQHI({}));
});

test('source timestamps use Hong Kong time and reject invalid calendar dates',()=>{
 assert.equal(Date.parse(parseAirTimestamp('202609071200')),START);
 assert.equal(Date.parse(parseAirTimestamp('2026-09-07T12:00:00')),START);
 assert.equal(Date.parse(parseAirTimestamp('2026-09-07T04:00:00Z')),START);
 for(const bad of ['202602301200','202609072400','202613010000','202609071299','2026-09-07T12:00:61',null,'yesterday'])assert.equal(parseAirTimestamp(bad),null);
});

test('nearest measured visibility reselects with movement; general AQHI stays independent',async()=>{
 const f=fixture();await f.controller.setLive(true);
 assert.equal(f.controller.state.visibilityMetres,17000);
 assert.equal(f.controller.state.aqhi.station,'Central/Western');
 assert.equal(f.controller.state.aqhi.stationKind,'general');
 const station=hko.stations.find(x=>x.name==='Chek Lap Kok');
 f.controller.setPosition(station.E-ORIGIN[0],ORIGIN[1]-station.N);
 assert.equal(f.controller.state.visibility.station,'Chek Lap Kok');
 assert.equal(f.controller.state.visibilityMetres,40000);
 assert.equal(f.controller.state.aqhi.station,'Tung Chung');
 f.controller.setPosition(841313.4-ORIGIN[0],ORIGIN[1]-816297.1);
 assert.equal(f.controller.state.visibility.station,'Sai Wan Ho');
 assert.equal(f.calls.length,4,'moving uses retained observations and coordinates');
 f.controller.dispose();
});

test('nearby N/A and unknown coordinates do not mask fresh measured stations',async()=>{
 const f=fixture({visibility:vis(START,[['Central','N/A'],['Unknown','100 m'],['Chek Lap Kok','40 km']])});
 await f.controller.setLive(true);assert.equal(f.controller.state.visibilityMetres,40000);assert.equal(f.controller.state.visibility.station,'Chek Lap Kok');
 f.controller.dispose();
});

test('AQHI cannot produce visibility, and all N/A remains unavailable',async()=>{
 const f=fixture({visibility:vis(START,[['Central','N/A']])});await f.controller.setLive(true);
 assert.equal(f.controller.state.visibilityMetres,null);assert.equal(f.controller.state.visibility.status,'unavailable');assert.equal(f.controller.state.aqhi.aqhi,3);
 f.controller.dispose();
});

test('visibility and AQHI expire independently even without another network response',async()=>{
 const f=fixture();await f.controller.setLive(true);
 f.setTime(START+VISIBILITY_STALE_MS+1);assert.equal(f.controller.state.visibilityMetres,null);assert.equal(f.controller.state.visibility.status,'stale');assert.equal(f.controller.state.aqhi.fresh,true);
 f.setTime(START+AQHI_STALE_MS+1);assert.equal(f.controller.state.aqhi.fresh,false);assert.equal(f.controller.state.aqhi.status,'stale');
 f.controller.dispose();
});

test('future timestamps cannot become negative-age live values',async()=>{
 const f=fixture({visibility:vis(START+AIR_FUTURE_TOLERANCE_MS+60000),aqhi:air(START+AIR_FUTURE_TOLERANCE_MS+60000)});
 await f.controller.setLive(true);assert.equal(f.controller.state.visibilityMetres,null);assert.equal(f.controller.state.visibility.status,'future');assert.equal(f.controller.state.aqhi.fresh,false);
 f.controller.dispose();
});

test('failed AQHI does not block HKO or cause repeated successful-feed requests',async()=>{
 const f=fixture({hook:url=>url===EPD_AQHI_URL?Promise.reject(new Error('AQHI unavailable')):undefined});await f.controller.setLive(true);
 assert.equal(f.controller.state.visibilityMetres,17000);assert.match(f.controller.state.aqhi.error,/AQHI unavailable/);
 await f.controller.refresh();assert.equal(f.calls.length,4);
 f.setTime(START+10000);await f.controller.poll();
 assert.equal(f.calls.filter(x=>x.url===HKO_VISIBILITY_URL).length,1);assert.equal(f.calls.filter(x=>x.url===EPD_AQHI_URL).length,2);
 f.controller.dispose();
});

test('one hanging feed times out without delaying the other feed state',async()=>{
 const f=fixture({timeoutMs:30,hook:url=>url===HKO_VISIBILITY_URL?new Promise(()=>{}):undefined});const pending=f.controller.setLive(true);
 await tick();assert.equal(f.controller.state.aqhi.fresh,true);assert.equal(f.controller.state.visibilityMetres,null);
 await pending;assert.match(f.controller.state.visibility.error,/timed out/);assert.equal(f.controller.state.aqhi.fresh,true);
 f.controller.dispose();
});

test('manual switch cancels a request which ignores AbortSignal, and late results cannot win',async()=>{
 let resolveOld;const f=fixture({hook:url=>url===HKO_VISIBILITY_URL?new Promise(resolve=>{resolveOld=resolve;}):undefined});
 const old=f.controller.setLive(true);await tick();await f.controller.setLive(false);await old;
 resolveOld(response(vis(START,[['Central','100 m']])));await tick();
 assert.equal(f.controller.state.mode,'manual');assert.equal(f.controller.state.visibilityMetres,null);assert.equal(f.controller.state.visibility.observedVisibilityMetres,null);
 assert.equal(f.calls.find(x=>x.url===HKO_VISIBILITY_URL).options.signal.aborted,true);
 f.controller.dispose();
});

test('dispose prevents resurrection, polling, and future live requests',async()=>{
 const f=fixture({hook:url=>url===HKO_VISIBILITY_URL?new Promise(()=>{}):undefined});const pending=f.controller.setLive(true);f.controller.dispose();await pending;
 assert.equal(f.controller.state.visibilityMetres,null);assert.equal(f.controller.state.disposed,true);
 const count=f.calls.length;await f.controller.setLive(true);await f.controller.refresh();assert.equal(f.controller.poll(),null);assert.equal(f.calls.length,count);
});

test('refresh coalesces, successful stations are cached, and poll honours refresh interval',async()=>{
 const f=fixture();await Promise.all([f.controller.setLive(true),f.controller.refresh(),f.controller.refresh()]);assert.equal(f.calls.length,4);
 assert.equal(f.controller.poll(),null);f.setTime(START+AIR_REFRESH_MS);await f.controller.poll();
 assert.equal(f.calls.length,6);assert.equal(f.calls.filter(x=>x.url.endsWith('stations.json')).length,2);
 await f.controller.setLive(false);assert.equal(f.controller.state.visibilityMetres,null);await f.controller.setLive(true);assert.equal(f.controller.state.visibilityMetres,17000);
 f.controller.dispose();
});

test('a failed refresh retains a usable cached reading only until its normal expiry',async()=>{
 let fail=false;const f=fixture({hook:url=>fail&&url===HKO_VISIBILITY_URL?Promise.resolve({ok:false,status:503}):undefined});await f.controller.setLive(true);
 fail=true;f.setTime(START+AIR_REFRESH_MS);await f.controller.poll();assert.equal(f.controller.state.visibilityMetres,17000);assert.match(f.controller.state.visibility.error,/503/);
 f.setTime(START+VISIBILITY_STALE_MS+1);assert.equal(f.controller.state.visibilityMetres,null);
 f.controller.dispose();
});

test('bad coordinate assets cannot be silently labelled a nearest station',async()=>{
 const f=fixture({hook:url=>url.endsWith('hko-stations.json')?Promise.resolve(response({stations:[]})):undefined});await f.controller.setLive(true);
 assert.equal(f.controller.state.visibilityMetres,null);assert.match(f.controller.state.visibility.error,/coordinates/);assert.equal(f.controller.state.aqhi.fresh,true);
 f.controller.dispose();
});

test('stale/future display metadata retains the observed reading while active metres stay null',async()=>{
 const old=fixture({visibility:vis(START-VISIBILITY_STALE_MS-60000,[['Central','17 km']])});await old.controller.setLive(true);
 assert.equal(old.controller.state.visibility.visibilityMetres,null);assert.equal(old.controller.state.visibility.observedVisibilityMetres,17000);assert.equal(old.controller.state.visibility.fresh,false);assert.equal(old.controller.state.visibilityMetres,null);
 const future=fixture({visibility:vis(START+AIR_FUTURE_TOLERANCE_MS+60000,[['Central','50 km']])});await future.controller.setLive(true);
 assert.equal(future.controller.state.visibility.visibilityMetres,null);assert.equal(future.controller.state.visibility.observedVisibilityMetres,50000);assert.equal(future.controller.state.visibility.limit,'at-least');assert.equal(future.controller.state.visibilityMetres,null);
 old.controller.dispose();future.controller.dispose();
});

test('nearest selection rejects non-finite readings and does not invent a distance for invalid position',async()=>{
 const f=fixture({visibility:vis(START,[['Central','Infinity km'],['Sai Wan Ho','NaN m'],['Chek Lap Kok','40 km']])});await f.controller.setLive(true);
 assert.equal(f.controller.state.visibility.station,'Chek Lap Kok');assert.equal(f.controller.state.visibilityMetres,40000);
 f.controller.setPosition({x:NaN,z:0});assert.equal(f.controller.state.visibility.distanceMetres,null);assert.match(f.controller.state.visibility.selection,/position unavailable/);
 assert.equal(f.controller.state.visibilityMetres,40000);
 f.controller.dispose();
});
