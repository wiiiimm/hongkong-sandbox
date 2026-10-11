// Hong Kong civil time is UTC+08:00. Never depend on the browser's timezone.
import {sunPosition,sunTimes,moonPosition,moonTimes,moonIllumination,compassDeg} from '../vendor/astro.js';

const HOUR_MS=3600000,DEG=180/Math.PI;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const smooth=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};

export function hktParts(date){
 if(!(date instanceof Date)||!Number.isFinite(date.getTime()))throw new RangeError('A valid instant is required');
 const local=new Date(date.getTime()+8*HOUR_MS);
 const hours=local.getUTCHours(),minutes=local.getUTCMinutes(),seconds=local.getUTCSeconds();
 return {date:local.toISOString().slice(0,10),time:local.toISOString().slice(11,16),hour:hours+minutes/60+seconds/3600+local.getUTCMilliseconds()/3600000,hours,minutes,seconds};
}

// Finite hours may cross midnight: dateFromHKT('2026-12-31',25) is 1 am on 1 January.
// Invalid form input returns null instead of silently normalising a bad civil date.
export function dateFromHKT(dateString,hour=12){
 if(!/^\d{4}-\d{2}-\d{2}$/.test(dateString)||!Number.isFinite(hour))return null;
 const midnight=new Date(`${dateString}T00:00:00+08:00`);
 if(!Number.isFinite(midnight.getTime())||hktParts(midnight).date!==dateString)return null;
 const date=new Date(midnight.getTime()+hour*HOUR_MS);
 return Number.isFinite(date.getTime())?date:null;
}

// astro.js azimuth is south=0, west=+90°. City coordinates: east +x, up +y, south +z.
export function horizontalDirection(azimuth,altitude){
 const horizontal=Math.cos(altitude);
 return {x:-Math.sin(azimuth)*horizontal,y:Math.sin(altitude),z:Math.cos(azimuth)*horizontal};
}

const dayCache=new Map();
function dailyTimes(dateString,lat,lon){
 const key=`${dateString}:${lat}:${lon}`;
 if(dayCache.has(key))return dayCache.get(key);
 // sunTimes chooses a solar cycle around its argument; noon prevents the HKT
 // midnight/UTC previous-date bug. moonTimes explicitly starts at HKT midnight.
 const solar=sunTimes(dateFromHKT(dateString,12),lat,lon),lunar=moonTimes(dateFromHKT(dateString,0),lat,lon);
 const result={sunrise:solar.sunrise,sunset:solar.sunset,solarNoon:solar.solarNoon,moonrise:lunar.rise||null,moonset:lunar.set||null};
 dayCache.set(key,result);if(dayCache.size>12)dayCache.delete(dayCache.keys().next().value);
 return result;
}

export function getSkyState(date,lat=22.3,lon=114.17){
 const hkt=hktParts(date);
 if(!Number.isFinite(lat)||Math.abs(lat)>90||!Number.isFinite(lon)||Math.abs(lon)>180)throw new RangeError('Invalid observer coordinates');
 const solar=sunPosition(date,lat,lon),lunar=moonPosition(date,lat,lon),illumination=moonIllumination(date);
 const body=position=>({...position,altitudeDeg:position.altitude*DEG,bearing:compassDeg(position.azimuth),direction:horizontalDirection(position.azimuth,position.altitude)});
 const altitude=solar.altitude*DEG;
 return {
  date:date.toISOString(),hkt,lat,lon,sun:body(solar),moon:{...body(lunar),...illumination},
  ...dailyTimes(hkt.date,lat,lon),
  night:1-smooth(-6,3,altitude),
  golden:smooth(-8,-1,altitude)*(1-smooth(3,13,altitude)),
  starVisibility:1-smooth(-18,-6,altitude),
  phase:altitude>=0?'Daylight':altitude>=-6?'Civil twilight':altitude>=-12?'Nautical twilight':altitude>=-18?'Astronomical twilight':'Night'
 };
}
