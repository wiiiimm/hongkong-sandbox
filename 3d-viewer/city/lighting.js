// Illustrative occupancy schedules, not measured activity or astronomical times.
// One shared clock drives every material, including sections loaded after dark.
import {smoothStep} from './geo.js';
export const LIGHT_PROFILES=['home','office','overnight','mixed','retail'];
const SCHEDULE=[
 // hour, homes, offices, overnight, unknown/mixed, retail
 [0,.48,.08,.65,.34,.14], [2,.16,.04,.42,.12,.04], [4,.055,.025,.24,.045,.02],
 [5,.10,.045,.28,.08,.03], [6,.30,.14,.42,.20,.075], [8,.40,.82,.68,.59,.30],
 [10,.25,.90,.74,.58,.88], [12,.22,.90,.75,.58,.90], [16,.28,.90,.80,.62,.92],
 [18,.60,.86,.84,.74,.94], [19,.76,.84,.89,.77,.94],
 [20,.87,.68,.92,.78,.93], [21,.90,.34,.92,.78,.93],
 [22,.83,.16,.88,.70,.88], [23,.68,.11,.78,.53,.48], [24,.48,.08,.65,.34,.14]
];
export function normaliseHour(hour){return Number.isFinite(hour)?((hour%24)+24)%24:15;}
export function formatHour(hour){const minutes=Math.round(normaliseHour(hour)*60)%1440;return `${String(Math.floor(minutes/60)).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')}`;}
export function cityLighting(hour){
 const h=normaliseHour(hour),next=SCHEDULE.findIndex(row=>row[0]>h),a=SCHEDULE[next-1],b=SCHEDULE[next];
 const t=smoothStep(a[0],b[0],h),activity=a.slice(1).map((value,i)=>value+(b[i+1]-value)*t);
 const night=h<12?1-smoothStep(5.5,7.2,h):smoothStep(17.6,19.75,h);
 const golden=h<12?Math.sin(smoothStep(5.5,8,h)*Math.PI):Math.sin(smoothStep(16,20,h)*Math.PI);
 const quiet=h<4?smoothStep(22,28,h+24):h<12?1-smoothStep(4,7,h):smoothStep(22,28,h);
 const phase=h>=19&&h<22?'Evening buzz':h>=22||h<2?'Winding down':h<5?'City at rest':h<7.2?'Early risers':h<17.6?'Daylight':'Lights coming on';
 return {hour:h,night,golden,quiet,activity,phase};
}
export function buildingLighting(b){
 // FNV ID hash: stable across reloads, palette changes and tile order.
 let hash=2166136261;for(const c of b.parent||b.id||b.uid||'building')hash=Math.imul(hash^c.charCodeAt(0),16777619)>>>0;
 const kind=b.kind||'';
 const profile=/hotel|hospital|clinic|fire_station|police/.test(kind)?2:
  /retail|shop|mall/.test(kind)?4:
  /office|commercial|school|university|industrial|warehouse/.test(kind)?1:
  /residential|apartment|house|dormitory|bungalow/.test(kind)?0:3;
 return {seed:(hash%65521)/65521,profile:b.activity?.profile??profile,base:b.base,retailTop:b.activity?.retailTop||0};
}

export function activityDescription(activity){
 if(!activity)return 'Night use: mixed / unknown · estimated pattern.';
 const names=['Residential','Office / daytime use','Hotel / overnight use','Mixed / unknown','Retail'];
 const evidence={'building-tag':'mapped building use','parent-tag':'mapped parent-building use',landuse:'estimated from mapped land use',research:'researched mixed-use building',fallback:'estimated use'};
 return `Night use: ${names[activity.profile]} · ${evidence[activity.source]||'estimated use'}.${activity.retailTop?' Lower floors follow retail hours; the vertical split is approximate.':''}`;
}
