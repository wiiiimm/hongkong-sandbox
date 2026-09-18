import {tideAt} from '../tide-series.js';

export const CHART_DATUM_BELOW_HKPD=.146;
export const TIDE_REFRESH_MS=5*60*1000;
export const TIDE_MANUAL_RANGE=Object.freeze([-1,4]);
export const HKO_TIDE_URL='https://data.weather.gov.hk/weatherAPI/opendata/opendata.php';
export const TIDE_DATUM_SOURCE='https://www.hko.gov.hk/en/tide/enotes.htm';
// Tide-gauge coordinates, not the similarly named automatic weather stations.
export const TIDE_STATIONS=Object.freeze({
 QUB:Object.freeze({code:'QUB',name:'Quarry Bay',zh:'鰂魚涌',lat:22+17/60+28/3600,lon:114+12/60+48/3600,source:'https://www.hko.gov.hk/en/cis/stn.htm'}),
 CCH:Object.freeze({code:'CCH',name:'Cheung Chau',zh:'長洲',lat:22+12/60+51/3600,lon:114+1/60+23/3600,source:'https://www.hko.gov.hk/tc/tide/tide_tables/2022/files/TideTable2022.pdf'}),
});
const HOUR=3600000,DAY=24*HOUR;
const numeric=value=>(typeof value==='number'||typeof value==='string')&&String(value).trim()!==''&&Number.isFinite(Number(value));
export const chartDatumToHKPD=value=>numeric(value)?Number(value)-CHART_DATUM_BELOW_HKPD:null;
export function chooseTideStation(observer){
 if(!numeric(observer?.lat)||!numeric(observer?.lon))return TIDE_STATIONS.QUB;
 const longitudeScale=Math.cos(Number(observer.lat)*Math.PI/180);
 const distance=station=>Math.hypot(station.lat-Number(observer.lat),(station.lon-Number(observer.lon))*longitudeScale);
 return distance(TIDE_STATIONS.CCH)<distance(TIDE_STATIONS.QUB)?TIDE_STATIONS.CCH:TIDE_STATIONS.QUB;
}
export function hongKongDay(now=Date.now(),offsetDays=0){
 const d=new Date(now+8*HOUR+offsetDays*DAY);return {year:d.getUTCFullYear(),month:d.getUTCMonth()+1,day:d.getUTCDate()};
}
const dateKey=day=>`${day.year}-${day.month}-${day.day}`;
export function tideURL(station,day){
 if(!TIDE_STATIONS[station])throw new Error('Unsupported tide station');
 return `${HKO_TIDE_URL}?dataType=HHOT&lang=en&rformat=json&station=${station}&year=${day.year}&month=${day.month}&day=${day.day}`;
}
export function parseTideDay(payload,day){
 const expected=['MM','DD',...Array.from({length:24},(_,i)=>String(i+1).padStart(2,'0'))];
 if(!Array.isArray(payload?.fields)||expected.some((field,i)=>payload.fields[i]!==field)||payload.fields.length!==26)throw new Error('HKO HHOT hourly fields are invalid');
 const rows=Array.isArray(payload.data)?payload.data:[],row=rows.find(r=>Array.isArray(r)&&Number(r[0])===day.month&&Number(r[1])===day.day);
 if(!row||row.length!==26)throw new Error('HKO HHOT has no matching daily row');
 const midnight=Date.UTC(day.year,day.month-1,day.day)-8*HOUR;
 // HHOT has 01..24 HKT, so column 24 is the following day's midnight.
 return Object.freeze(row.slice(2).map((value,i)=>{
  const heightCD=numeric(value)?Number(value):null;
  return Object.freeze({time:midnight+(i+1)*HOUR,heightCD,heightHKPD:chartDatumToHKPD(heightCD)});
 }));
}
export function sampleTide(series,time){
 if(!Array.isArray(series)||!series.length||!Number.isFinite(time))return null;
 const i=series.findIndex(p=>p.time>=time);if(i<0)return null;
 const b=series[i];if(b.time===time)return Number.isFinite(b.heightCD)?b.heightCD:null;
 const a=series[i-1];
 if(!a||b.time-a.time!==HOUR||!Number.isFinite(a.heightCD)||!Number.isFinite(b.heightCD))return null;
 // Retain the original linear interpolation, while refusing stale coverage or gaps.
 return tideAt([a.heightCD,b.heightCD],1+(time-a.time)/HOUR);
}
export function tidePrediction(series,time,metadata={}){
 const heightCD=sampleTide(series,time),before=sampleTide(series,time-HOUR/2),after=sampleTide(series,time+HOUR/2);
 const change=before===null||after===null?null:after-before;
 return {...metadata,time,heightCD,heightHKPD:chartDatumToHKPD(heightCD),trend:change===null?'unavailable':change>.02?'rising':change<-.02?'falling':'slack',series};
}

export function createTideData({fetchImpl=globalThis.fetch?.bind(globalThis),now=Date.now,timeoutMs=12000}={}){
 let mode='manual',station=TIDE_STATIONS.QUB,manualLevelHKPD=.3,restingLevelHKPD=.3,basis='manual',prediction=null;
 let error=null,status='idle',paused=false,suspended=false,disposed=false,generation=0,inflight=null,abort=null,lastComputed=-Infinity;
 const cache=new Map(),attempts=new Map();
 const snapshot=()=>({mode,status,station,manualLevelHKPD,restingLevelHKPD,basis,prediction,error,paused,suspended,datum:'HKPD',predictionKind:'astronomical',datumOffsetMetres:-CHART_DATUM_BELOW_HKPD});
 function recompute(){
  if(paused||suspended||disposed)return;
  if(mode==='manual'){restingLevelHKPD=manualLevelHKPD;basis='manual';prediction=null;status='idle';return;}
  const entry=cache.get(station.code),time=now();lastComputed=time;
  prediction=entry?tidePrediction(entry.series,time,{station,sourceUrls:entry.sourceUrls,fetchedAt:entry.fetchedAt,checkedAt:entry.checkedAt,sourceFetches:entry.sourceFetches,source:'Hong Kong Observatory',datumSource:TIDE_DATUM_SOURCE,partial:entry.partial}):null;
  if(prediction?.heightHKPD!=null){
   restingLevelHKPD=prediction.heightHKPD;basis='prediction';
   if(!inflight)status=entry.usingCached?'stale':entry.partial?'partial':'live';
  }else{
   // A missing or expired forecast never becomes zero or a fabricated observation.
   basis='manual-fallback';restingLevelHKPD=manualLevelHKPD;
   if(!inflight)status=entry?'unavailable':error?'error':'idle';
  }
 }
 function cancel(){generation++;abort?.abort();abort=null;inflight=null;}
 async function refresh(){
  if(disposed||mode!=='live'||paused||suspended)return snapshot();
  if(inflight)return inflight;
  const time=now(),last=attempts.get(station.code);
  if(last&&time-last.time<(last.failed?10000:60000))return snapshot();
  const code=station.code,token=++generation,controller=new AbortController();abort=controller;
  // Mark pending requests as retryable after 10 s if a station change cancels them.
  attempts.set(code,{time,failed:true});status='loading';
  const timer=setTimeout(()=>controller.abort(),timeoutMs);
  inflight=(async()=>{
   try{
    if(!fetchImpl)throw new Error('Network access is unavailable');
    const days=[-1,0,1].map(offset=>hongKongDay(time,offset)),urls=days.map(day=>tideURL(code,day));
    const results=await Promise.allSettled(urls.map(async(url,i)=>{
     const response=await fetchImpl(url,{signal:controller.signal});if(!response.ok)throw new Error('HTTP '+response.status);
     return parseTideDay(await response.json(),days[i]);
    }));
    if(disposed||token!==generation||mode!=='live'||station.code!==code)return snapshot();
    const previous=cache.get(code),failures=[];let usingCached=false;
    const series=days.flatMap((day,i)=>{
     if(results[i].status==='fulfilled')return results[i].value;
     if(previous?.series.some(p=>hongKongDay(p.time-1).day===day.day&&p.heightCD!==null))usingCached=true;
     failures.push(`${dateKey(day)}: ${results[i].reason?.message||'request failed'}`);
     // Old valid values may fill the same dated day only, never another date or station.
     const midnight=Date.UTC(day.year,day.month-1,day.day)-8*HOUR;
     return Array.from({length:24},(_,hour)=>previous?.series.find(p=>p.time===midnight+(hour+1)*HOUR)||Object.freeze({time:midnight+(hour+1)*HOUR,heightCD:null,heightHKPD:null}));
    });
    if(!series.some(p=>p.heightCD!==null))throw new Error(failures.join('; ')||'HKO HHOT contains no usable predictions');
    const partial=failures.length>0||series.some(p=>p.heightCD===null);
    const sourceFetches=Object.freeze(days.map((day,i)=>Object.freeze({url:urls[i],fetchedAt:results[i].status==='fulfilled'?new Date(now()).toISOString():previous?.sourceFetches?.find(p=>p.url===urls[i])?.fetchedAt||null,cached:results[i].status!=='fulfilled'})));
    cache.set(code,{series:Object.freeze(series),sourceUrls:Object.freeze(urls),sourceFetches,usingCached,fetchedAt:results.some(r=>r.status==='fulfilled')?new Date(now()).toISOString():previous?.fetchedAt,checkedAt:new Date(now()).toISOString(),partial,day:dateKey(hongKongDay(time))});
    error=failures.length?failures.join('; '):partial?'Some hourly predictions are unavailable':null;
    attempts.set(code,{time,failed:!!error});
   }catch(e){if(token===generation&&!disposed){error=e.name==='AbortError'?'HKO tide request timed out':String(e.message||e);}}
   finally{
    clearTimeout(timer);
    if(token===generation){inflight=null;abort=null;recompute();}
   }
   return snapshot();
  })();return inflight;
 }
 return {
  get state(){return snapshot();},
  setManual(value){if(disposed)return snapshot();if(!numeric(value))return snapshot();manualLevelHKPD=Math.max(-1,Math.min(4,Number(value)));if(mode==='manual')recompute();return snapshot();},
  setLive(enabled){
   if(disposed)return Promise.resolve(snapshot());
   const next=enabled?'live':'manual';if(next!==mode){cancel();mode=next;prediction=null;error=null;status='idle';recompute();}
   return enabled?refresh():Promise.resolve(snapshot());
  },
  setStation(code){
   if(!TIDE_STATIONS[code]||disposed)return Promise.resolve(snapshot());
   if(station.code===code)return Promise.resolve(snapshot());
   cancel();station=TIDE_STATIONS[code];prediction=null;error=null;status='idle';recompute();
   return mode==='live'?refresh():Promise.resolve(snapshot());
  },
  refresh,
  update(options={}){
   const wasFrozen=paused||suspended;paused=!!options.paused;suspended=!!options.suspended;
   if(disposed)return snapshot();
   if(!paused&&!suspended){
    if(wasFrozen||mode==='manual'||now()-lastComputed>=1000)recompute();
    const last=attempts.get(station.code),entry=cache.get(station.code);
    if(mode==='live'&&!inflight&&(!last||now()-last.time>=(last.failed?10000:TIDE_REFRESH_MS)||entry?.day!==dateKey(hongKongDay(now()))))void refresh();
   }return snapshot();
  },
  dispose(){disposed=true;cancel();cache.clear();},
 };
}
