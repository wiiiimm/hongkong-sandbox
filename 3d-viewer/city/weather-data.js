// HKO observations stay separate from their approximate visual interpretation.
import {ORIGIN} from './geo.js';

export const HKO_CURRENT_URL='https://data.weather.gov.hk/weatherAPI/opendata/weather.php?lang=en&dataType=rhrread';
export const HKO_WIND_URL='https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind.csv';
export const WEATHER_REFRESH_MS=5*60*1000;
export const WEATHER_STALE_MS=90*60*1000;
export const DEFAULT_WEATHER=Object.freeze({rain:0,clouds:0,fog:0,wind:.12,waves:.18,snow:0,windFrom:90});
const INTENSITIES=['rain','clouds','fog','wind','waves','snow'];
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const finite=x=>x!==null&&x!==undefined&&String(x).trim()!==''&&Number.isFinite(Number(x));
const ICONS={50:'Sunny',51:'Sunny periods',52:'Sunny intervals',53:'Sunny periods with showers',54:'Sunny intervals with showers',60:'Cloudy',61:'Overcast',62:'Light rain',63:'Rain',64:'Heavy rain',65:'Thunderstorms',70:'Fine',71:'Fine',72:'Fine',73:'Fine',74:'Fine',75:'Fine',76:'Mainly cloudy',77:'Mainly fine',80:'Windy',81:'Dry',82:'Humid',83:'Fog',84:'Mist',85:'Haze',90:'Hot',91:'Warm',92:'Cool',93:'Cold'};
// The existing viewer's station-to-district mapping; these anchors are not district boundaries.
const DISTRICTS={
 'Central Pier':'Central & Western District','Chek Lap Kok':'Islands District','Cheung Chau':'Islands District',
 'Cheung Chau Beach':'Islands District','Clear Water Bay':'Sai Kung','Green Island':'Central & Western District',
 'HK Observatory':'Yau Tsim Mong','HK Park':'Central & Western District','Happy Valley':'Wan Chai',
 'Hong Kong Sea School':'Southern District','Kai Tak':'Kowloon City','Kai Tak Runway Park':'Kowloon City',
 'Kau Sai Chau':'Sai Kung',"King's Park":'Yau Tsim Mong','Kowloon City':'Kowloon City','Kwun Tong':'Kwun Tong',
 'Lamma Island':'Islands District','Lau Fau Shan':'Yuen Long','Ngong Ping':'Islands District','North Point':'Eastern District',
 'Pak Tam Chung':'Sai Kung','Peng Chau':'Islands District','Sai Kung':'Sai Kung','Sha Chau':'Islands District',
 'Sha Tin':'Sha Tin','Sham Shui Po':'Sham Shui Po','Shau Kei Wan':'Eastern District','Shek Kong':'Yuen Long',
 'Sheung Shui':'North District','Stanley':'Southern District','Star Ferry':'Yau Tsim Mong','Ta Kwu Ling':'North District',
 'Tai Lung':'Yuen Long','Tai Mei Tuk':'Tai Po','Tai Mo Shan':'Tsuen Wan','Tai Po':'Tai Po','Tai Po Kau':'Tai Po',
 'Tap Mun':'Tai Po',"Tate's Cairn":'Wong Tai Sin','The Peak':'Central & Western District','Tseung Kwan O':'Sai Kung',
 'Tsing Yi':'Kwai Tsing','Tsuen Wan Ho Koon':'Tsuen Wan','Tsuen Wan Shing Mun Valley':'Tsuen Wan','Tuen Mun':'Tuen Mun',
 'Waglan Island':'Islands District','Wetland Park':'Yuen Long','Wong Chuk Hang':'Southern District','Wong Tai Sin':'Wong Tai Sin','Yuen Long Park':'Yuen Long',
};
const normalName=name=>String(name).replace(/^Hong Kong Observatory$/,'HK Observatory').replace(/^Hong Kong Park$/,'HK Park');

export function normaliseWeather(values={},previous=DEFAULT_WEATHER){
 const out={...previous};
 for(const key of INTENSITIES)if(finite(values[key]))out[key]=clamp(Number(values[key]));
 if(finite(values.windFrom))out.windFrom=((Number(values.windFrom)%360)+360)%360;
 return out;
}
export function windBearing(value){
 if(finite(value))return ((Number(value)%360)+360)%360;
 const cardinal=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
 const words=['NORTH','NORTHNORTHEAST','NORTHEAST','EASTNORTHEAST','EAST','EASTSOUTHEAST','SOUTHEAST','SOUTHSOUTHEAST','SOUTH','SOUTHSOUTHWEST','SOUTHWEST','WESTSOUTHWEST','WEST','WESTNORTHWEST','NORTHWEST','NORTHNORTHWEST'];
 const key=String(value??'').toUpperCase().replace(/[^A-Z]/g,'');
 let i=cardinal.indexOf(key);if(i<0)i=words.indexOf(key);return i<0?null:i*22.5;
}
export function windArchiveURL(now=Date.now()){
 // DATA.GOV.HK archive snapshots trail current observations; never label this exact-now wind.
 const local=new Date(now+8*3600000-15*60000).toISOString();
 const stamp=local.slice(0,10).replaceAll('-','')+'-'+local.slice(11,16).replace(':','');
 return 'https://api.data.gov.hk/v1/historical-archive/get-file?url='+encodeURIComponent(HKO_WIND_URL)+'&time='+stamp;
}
function csvRows(text){
 // Quoted cells are handled so a future station with punctuation does not shift columns.
 return String(text).trim().split(/\r?\n/).slice(1).map(line=>{
  const cells=[];let current='',quoted=false;
  for(let i=0;i<line.length;i++){const c=line[i];if(c==='"'){if(quoted&&line[i+1]==='"'){current+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){cells.push(current.trim());current='';}else current+=c;}
  cells.push(current.trim());return cells;
 });
}
export function parseWindCSV(text){
 const rows=[];
 for(const [stamp,station,direction,speed,gust] of csvRows(text)){
  if(!/^\d{12}$/.test(stamp)||!station||!finite(speed)||Number(speed)<0)continue;
  const iso=`${stamp.slice(0,4)}-${stamp.slice(4,6)}-${stamp.slice(6,8)}T${stamp.slice(8,10)}:${stamp.slice(10,12)}:00+08:00`;
  if(!Number.isFinite(Date.parse(iso)))continue;
  rows.push({station:normalName(station),from:windBearing(direction),speedKmh:Number(speed),gustKmh:finite(gust)&&Number(gust)>=0?Number(gust):null,updatedAt:iso});
 }
 return rows;
}
export function parseCurrentWeather(payload){
 if(!payload||!Number.isFinite(Date.parse(payload.updateTime)))throw new Error('HKO report has no valid observation timestamp');
 const readings=(block,min,max)=>(Array.isArray(block?.data)?block.data:[]).filter(x=>typeof x.place==='string'&&finite(x.value)&&Number(x.value)>=min&&Number(x.value)<=max).map(x=>({station:normalName(x.place),value:Number(x.value),updatedAt:block.recordTime||payload.updateTime}));
 const temperature=readings(payload.temperature,-30,60),humidity=readings(payload.humidity,0,100);
 const icons=(Array.isArray(payload.icon)?payload.icon:[]).map(Number).filter(x=>ICONS[x]);
 if(!temperature.length&&!icons.length&&!humidity.length)throw new Error('HKO report contains no usable observations');
 const rainfall=(Array.isArray(payload.rainfall?.data)?payload.rainfall.data:[]).filter(x=>typeof x.place==='string'&&finite(x.max)&&Number(x.max)>=0).map(x=>({district:x.place,millimetres:Number(x.max)}));
 return {updatedAt:payload.updateTime,icon:icons[0]??null,condition:ICONS[icons[0]]||'Conditions unavailable',temperature,humidity,rainfall,rainStart:payload.rainfall?.startTime||null,rainEnd:payload.rainfall?.endTime||null,warning:Array.isArray(payload.warningMessage)?payload.warningMessage.join(' '):String(payload.warningMessage||'')};
}
function nearest(rows,stations,position){
 if(!rows?.length)return null;
 if(!position)return rows.find(r=>r.station==='HK Observatory')||rows[0];
 let best=null,bestDistance=Infinity;
 for(const row of rows){const station=stations.find(s=>normalName(s.name)===row.station);if(!station)continue;
  const d=Math.hypot(station.E-ORIGIN[0]-position.x,ORIGIN[1]-station.N-position.z);
  if(d<bestDistance){bestDistance=d;best={...row,distanceMetres:Math.round(d)};}
 }
 return best||rows.find(r=>r.station==='HK Observatory')||rows[0];
}
export function localObservation(report,wind,stations=[],position=null){
 const temperature=nearest(report.temperature,stations,position),humidity=nearest(report.humidity,stations,position);
 const anchor=nearest(stations.map(s=>({station:normalName(s.name)})),stations,position);
 const district=DISTRICTS[anchor?.station];
 const rain=report.rainfall.find(r=>r.district===district)||null;
 return {updatedAt:report.updatedAt,condition:report.condition,icon:report.icon,temperature,humidity,wind:nearest(wind,stations,position),rainfall:rain?{...rain,startTime:report.rainStart,endTime:report.rainEnd,basis:'Nearest station district; approximate boundary'}:null,warning:report.warning};
}
export function weatherFromObservation(observation){
 const code=observation.icon,mm=observation.rainfall?.millimetres;
 // District past-hour totals are not instantaneous rain rates. They guide a visual estimate only.
 const rain=mm!=null?clamp(Math.log1p(mm)/Math.log(36)):({53:.12,54:.20,62:.20,63:.45,64:.85,65:.65}[code]||0);
 let clouds=({50:.06,51:.24,52:.40,53:.43,54:.58,60:.78,61:1,62:.85,63:.94,64:1,65:1,76:.72,77:.22,83:.8,84:.6,85:.3}[code]??.12);
 clouds=Math.max(clouds,rain*.9);
 // High humidity alone is not evidence of fog. Only an explicit condition activates fog.
 const fog=({83:.72,84:.40,85:.24}[code]||0);
 const speed=observation.wind?.speedKmh;
 const wind=speed==null?0:clamp(speed/65);
 const settings=normaliseWeather({rain,clouds,fog,wind,waves:wind*.85,snow:0,windFrom:observation.wind?.from??0});
 // Variable or missing direction must not silently become an observed northerly.
 if(observation.wind?.from==null)settings.windFrom=null;
 return settings;
}

export function createWeatherData({fetchImpl=globalThis.fetch?.bind(globalThis),now=Date.now,timeoutMs=12000}={}){
 let mode='manual',status='idle',manual={...DEFAULT_WEATHER},settings={...manual},observation=null;
 let report=null,wind=[],stations=[],error=null,windError=null,checkedAt=null,lastAttempt=-Infinity,inflight=null,abort=null,generation=0,disposed=false,position=null;
 const recompute=()=>{if(report){observation=localObservation(report,wind,stations,position);if(mode==='live')settings=weatherFromObservation(observation);}};
 const snapshot=()=>({mode,status:mode==='manual'?'idle':(status==='live'&&now()-Date.parse(observation?.updatedAt)>WEATHER_STALE_MS?'stale':status),settings:{...settings},manual:{...manual},observation:observation?structuredClone(observation):null,error,windError,checkedAt,updatedAt:observation?.updatedAt||null,source:'Hong Kong Observatory / DATA.GOV.HK',approximate:true});
 async function refresh(){
  if(disposed||mode!=='live')return snapshot();
  if(inflight)return inflight;
  // Button retries cannot create an unbounded fetch loop; failed attempts can retry after 10 s.
  if(now()-lastAttempt<(error?10000:60000))return snapshot();
  lastAttempt=now();status='loading';const token=++generation;
  const controller=new AbortController();abort=controller;
  const timer=setTimeout(()=>controller.abort(),timeoutMs);
  inflight=(async()=>{
   try{
    if(!fetchImpl)throw new Error('Network access is unavailable');
    const request=async(url,type)=>{const response=await fetchImpl(url,{signal:controller.signal});if(!response.ok)throw new Error('HTTP '+response.status);return response[type]();};
    const results=await Promise.allSettled([
     request(HKO_CURRENT_URL,'json'),request(windArchiveURL(now()),'text'),
     stations.length?Promise.resolve({stations}):request(new URL('../data/hko-stations.json',import.meta.url).href,'json'),
    ]);
    if(disposed||mode!=='live'||generation!==token)return snapshot();
    if(results[0].status==='rejected')throw results[0].reason;
    const current=parseCurrentWeather(results[0].value);
    // Reject future-dated feeds instead of making their age negative.
    if(Date.parse(current.updatedAt)>now()+15*60000)throw new Error('HKO observation timestamp is ahead of the current clock');
    report=current;
    if(results[2].status==='fulfilled'&&Array.isArray(results[2].value.stations))stations=results[2].value.stations.filter(s=>finite(s.E)&&finite(s.N));
    wind=results[1].status==='fulfilled'?parseWindCSV(results[1].value).filter(row=>now()-Date.parse(row.updatedAt)<=WEATHER_STALE_MS&&Date.parse(row.updatedAt)<=now()+15*60000):[];
    windError=wind.length?null:'Observed wind unavailable; wind and waves are calm until readings return';
    checkedAt=new Date(now()).toISOString();error=null;status='live';recompute();
   }catch(cause){
    if(!disposed&&mode==='live'&&generation===token){error=cause?.name==='AbortError'?'HKO request timed out':String(cause?.message||'Live weather unavailable');status=report?'stale':'error';}
   }finally{clearTimeout(timer);if(generation===token){inflight=null;abort=null;}}
   return snapshot();
  })();
  return inflight;
 }
 return {
  get state(){return snapshot();},
  setManual(values){if(disposed)return snapshot();if(inflight)lastAttempt=-Infinity;generation++;abort?.abort();inflight=null;abort=null;mode='manual';status='idle';manual=normaliseWeather(values,manual);settings={...manual};return snapshot();},
  setLive(enabled){if(disposed)return Promise.resolve(snapshot());if(!enabled){if(inflight)lastAttempt=-Infinity;generation++;abort?.abort();inflight=null;abort=null;mode='manual';status='idle';settings={...manual};return Promise.resolve(snapshot());}mode='live';if(!report)status=error?'error':'idle';if(report){status='live';recompute();}return refresh();},
  setPosition(value){position=value?{x:value.x,z:value.z}:null;recompute();},
  poll(){if(mode==='live'&&now()-lastAttempt>=WEATHER_REFRESH_MS)return refresh();return null;},
  refresh,
  dispose(){disposed=true;generation++;abort?.abort();inflight=null;},
 };
}
