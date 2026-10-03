// Measured visibility and AQHI are independent observations, never interchangeable units.
import {ORIGIN} from './geo.js';

export const HKO_VISIBILITY_URL='https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=LTMV&rformat=json&lang=en';
export const EPD_AQHI_URL='https://dashboard.data.gov.hk/api/aqhi-individual?format=json';
export const AIR_REFRESH_MS=5*60*1000;
export const VISIBILITY_STALE_MS=30*60*1000;
export const AQHI_STALE_MS=90*60*1000;
export const AIR_FUTURE_TOLERANCE_MS=5*60*1000;
const MIN_RETRY_MS=10000, MIN_REFRESH_MS=60000;
const HKO_STATIONS_URL=new URL('../data/hko-stations.json',import.meta.url).href;
const AQHI_STATIONS_URL=new URL('../data/epd-aqhi-stations.json',import.meta.url).href;
const finite=x=>(typeof x==='number'||typeof x==='string')&&String(x).trim()!==''&&Number.isFinite(Number(x));
const normalName=x=>String(x??'').trim().replace(/^Central Pier$/,'Central');

export function parseAirTimestamp(value){
 let text=String(value??'').trim();
 if(/^\d{12}$/.test(text))text=`${text.slice(0,4)}-${text.slice(4,6)}-${text.slice(6,8)}T${text.slice(8,10)}:${text.slice(10,12)}:00`;
 const m=text.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?(Z|[+-]\d{2}:\d{2})?$/);
 if(!m)return null;
 const [year,month,day,hour,minute,second]=m.slice(1,7).map(x=>Number(x??0));
 const test=new Date(Date.UTC(year,month-1,day,hour,minute,second));
 if(year<2000||test.getUTCFullYear()!==year||test.getUTCMonth()!==month-1||test.getUTCDate()!==day||hour>23||minute>59||second>59)return null;
 const zone=m[7]||'+08:00';
 if(zone!=='Z'&&(Number(zone.slice(1,3))>23||Number(zone.slice(4))>59))return null;
 const iso=`${m[1]}-${m[2]}-${m[3]}T${m[4]}:${m[5]}:${m[6]||'00'}${zone}`;
 return Number.isFinite(Date.parse(iso))?iso:null;
}

export function parseVisibility(payload){
 if(!Array.isArray(payload?.fields)||!Array.isArray(payload?.data))throw new Error('HKO visibility response has no fields/data arrays');
 const fields=payload.fields.map(x=>String(x).trim().toLowerCase());
 const columns=['date time','automatic weather station','10 minute mean visibility'].map(key=>fields.indexOf(key));
 if(columns.some(i=>i<0))throw new Error('HKO visibility response has unrecognised columns');
 const rows=[];
 for(const row of payload.data){
  if(!Array.isArray(row))continue;
  const updatedAt=parseAirTimestamp(row[columns[0]]),station=normalName(row[columns[1]]);
  if(!updatedAt||!station)continue;
  const raw=String(row[columns[2]]??'').trim(),match=raw.match(/^(\d+(?:\.\d+)?)\s*(km|m)$/i);
  const metres=match?Number(match[1])*(match[2].toLowerCase()==='km'?1000:1):null;
  // HKO's reporting range is 100 m–50 km; its endpoints are censored bounds.
  const visibilityMetres=metres!==null&&metres>=100&&metres<=50000?metres:null;
  rows.push({station,updatedAt,visibilityMetres,raw,limit:visibilityMetres===100?'at-most':visibilityMetres===50000?'at-least':null});
 }
 if(!rows.length)throw new Error('HKO visibility response has no timestamped station rows');
 return rows;
}

export function parseAQHI(payload){
 if(!Array.isArray(payload))throw new Error('EPD AQHI response is not a station array');
 const rows=[];
 for(const row of payload){
  const station=String(row?.station??'').trim(),updatedAt=parseAirTimestamp(row?.publish_date);
  if(!station||!updatedAt)continue;
  const raw=String(row.aqhi??'').trim();
  const aqhi=raw==='10+'?10:/^(?:[1-9]|10)$/.test(raw)?Number(raw):null;
  rows.push({station,updatedAt,aqhi,aqhiLabel:aqhi===null?null:raw,healthRisk:typeof row.health_risk==='string'?row.health_risk.trim():null,limit:raw==='10+'?'above':null});
 }
 if(!rows.length)throw new Error('EPD AQHI response has no timestamped station rows');
 return rows;
}

function stationAnchors(payload,visibility){
 const stations=(Array.isArray(payload?.stations)?payload.stations:[]).filter(s=>typeof s.name==='string'&&finite(s.E)&&finite(s.N)).map(s=>({...s,name:visibility?normalName(s.name):s.name,E:Number(s.E),N:Number(s.N)}));
 if(!stations.length)throw new Error('Station coordinates are unavailable');
 // SWH is missing from the existing regional-weather anchors. HKO SMO station
 // table: 22°17′08″N, 114°13′33″E, projected WGS84→HK1980. Approximate selection only.
 if(visibility&&!stations.some(s=>s.name==='Sai Wan Ho'))stations.push({name:'Sai Wan Ho',E:841313.4,N:816297.1,kind:'visibility',coordinateSource:'HKO SMO station table; approximate selection anchor'});
 return stations;
}

function selectObservation(feed,position,time){
 const candidates=[];
 for(const row of feed.rows){
  const anchor=feed.stations.find(s=>s.name===row.station);if(!anchor)continue;
  const age=time-Date.parse(row.updatedAt),value=row[feed.valueKey];
  const fresh=value!==null&&Number.isFinite(value)&&age>=-AIR_FUTURE_TOLERANCE_MS&&age<=feed.staleMs;
  const distance=position?Math.hypot(anchor.E-ORIGIN[0]-position.x,ORIGIN[1]-anchor.N-position.z):null;
  candidates.push({...row,fresh,ageMs:age,distanceMetres:distance===null?null:Math.round(distance),stationKind:anchor.kind||(feed.key==='visibility'?'visibility':null),stationCoordinatesApproximate:true});
 }
 // A nearby N/A/stale reading must not hide a valid observation at another station.
 // General AQHI is preferred for regional ambient context; roadside is explicit fallback.
 const general=feed.key==='aqhi'?candidates.filter(x=>x.stationKind==='general'):candidates;
 const usable=general.filter(x=>x.fresh),otherUsable=candidates.filter(x=>x.fresh);
 const pool=usable.length?usable:otherUsable.length?otherUsable:general.length?general:candidates;
 return pool.sort((a,b)=>(a.distanceMetres??0)-(b.distanceMetres??0)||Date.parse(b.updatedAt)-Date.parse(a.updatedAt))[0]||null;
}

export function createAirVisibilityData({fetchImpl=globalThis.fetch?.bind(globalThis),now=Date.now,timeoutMs=12000}={}){
 let mode='manual',disposed=false,generation=0,position=null;
 const makeFeed=(key,url,stationURL,parse,valueKey,staleMs,source)=>({key,url,stationURL,parse,valueKey,staleMs,source,rows:[],stations:[],error:null,checkedAt:null,receivedAt:null,lastAttempt:-Infinity,inflight:null,abort:null});
 const visibility=makeFeed('visibility',HKO_VISIBILITY_URL,HKO_STATIONS_URL,parseVisibility,'visibilityMetres',VISIBILITY_STALE_MS,'Hong Kong Observatory');
 const aqhi=makeFeed('aqhi',EPD_AQHI_URL,AQHI_STATIONS_URL,parseAQHI,'aqhi',AQHI_STALE_MS,'Environmental Protection Department / DATA.GOV.HK');
 const feeds=[visibility,aqhi];
 const feedState=feed=>{
  const row=selectObservation(feed,position,now()),fresh=Boolean(row?.fresh);
  let status=disposed?'disposed':mode==='manual'?'idle':feed.inflight?'loading':fresh?'live':row?.[feed.valueKey]!=null?'stale':feed.error?'error':feed.rows.length?'unavailable':'idle';
  if(row&&row.ageMs<-AIR_FUTURE_TOLERANCE_MS)status=mode==='live'?'future':status;
  return {...row,station:row?.station??null,updatedAt:row?.updatedAt??null,distanceMetres:row?.distanceMetres??null,fresh,status,source:feed.source,sourceURL:feed.url,error:feed.error,checkedAt:feed.checkedAt,receivedAt:feed.receivedAt,selection:position?(feed.key==='aqhi'?'Nearest usable general station; roadside only if general readings are unavailable':'Nearest usable station with approximate coordinates'):'First usable station; city position unavailable',...(feed.key==='visibility'?{visibilityMetres:fresh?row.visibilityMetres:null,observedVisibilityMetres:row?.visibilityMetres??null}:{aqhi:row?.aqhi??null,aqhiLabel:row?.aqhiLabel??null,healthRisk:row?.healthRisk??null,stationKind:row?.stationKind??null})};
 };
 const snapshot=()=>{const v=feedState(visibility),a=feedState(aqhi);return {mode,disposed,visibilityMetres:!disposed&&mode==='live'&&v.fresh?v.visibilityMetres:null,visibility:v,aqhi:a};};
 async function update(feed){
  if(disposed||mode!=='live')return;
  if(feed.inflight)return feed.inflight;
  if(now()-feed.lastAttempt<(feed.error?MIN_RETRY_MS:MIN_REFRESH_MS))return;
  feed.lastAttempt=now();const token=generation,controller=new AbortController();feed.abort=controller;
  let timer;
  const cancelled=new Promise((_,reject)=>{
   controller.signal.addEventListener('abort',()=>reject(new Error('Request cancelled')),{once:true});
   timer=setTimeout(()=>{reject(new Error('Request timed out'));controller.abort();},Math.max(1,timeoutMs));
  });
  const request=async url=>{if(!fetchImpl)throw new Error('Network access is unavailable');const response=await fetchImpl(url,{signal:controller.signal});if(!response.ok)throw new Error('HTTP '+response.status);return response.json();};
  const task=(async()=>{
   try{
    const [payload,anchors]=await Promise.race([Promise.all([request(feed.url),feed.stations.length?Promise.resolve(null):request(feed.stationURL)]),cancelled]);
    if(disposed||mode!=='live'||generation!==token)return;
    const rows=feed.parse(payload),stations=anchors?stationAnchors(anchors,feed.key==='visibility'):feed.stations;
    feed.rows=rows;feed.stations=stations;feed.error=null;feed.receivedAt=new Date(now()).toISOString();
   }catch(cause){
    if(!disposed&&mode==='live'&&generation===token)feed.error=String(cause?.message||'Observation unavailable');
   }finally{
    clearTimeout(timer);controller.abort();
    if(generation===token&&!disposed){feed.checkedAt=new Date(now()).toISOString();feed.inflight=null;feed.abort=null;}
   }
  })();
  feed.inflight=task;return task;
 }
 async function refresh(){if(!disposed&&mode==='live')await Promise.all(feeds.map(update));return snapshot();}
 function stop(){generation++;for(const feed of feeds){if(feed.inflight)feed.lastAttempt=-Infinity;feed.abort?.abort();feed.abort=null;feed.inflight=null;}}
 return {
  get state(){return snapshot();},
  setLive(enabled){if(disposed)return Promise.resolve(snapshot());if(!enabled){mode='manual';stop();return Promise.resolve(snapshot());}mode='live';return refresh();},
  setPosition(x,z){if(disposed)return snapshot();const value=typeof x==='object'&&x!==null?x:{x,z};position=finite(value.x)&&finite(value.z)?{x:Number(value.x),z:Number(value.z)}:null;return snapshot();},
  refresh,
  poll(){if(disposed||mode!=='live')return null;const due=feeds.filter(f=>now()-f.lastAttempt>=(f.error?MIN_RETRY_MS:AIR_REFRESH_MS));return due.length?Promise.all(due.map(update)).then(snapshot):null;},
  dispose(){if(disposed)return;disposed=true;stop();},
 };
}
