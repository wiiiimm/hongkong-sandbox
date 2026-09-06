// Illustrative occupancy schedules, not measured activity or astronomical times.
// One shared clock drives every material, including sections loaded after dark.
import {smoothStep} from './geo.js';
export const LIGHT_PROFILES=['home','office','overnight','mixed'];
const SCHEDULE=[
 [0, .44,.18,.72,.32], [2, .16,.075,.48,.13], [4, .06,.035,.26,.065],
 [5, .10,.06,.30,.10], [6, .30,.18,.45,.23], [8, .36,.80,.70,.60],
 [12,.22,.80,.65,.55], [17,.45,.75,.72,.65], [19,.88,.64,.95,.82],
 [21,.80,.50,.92,.72], [22,.69,.36,.87,.60], [24,.44,.18,.72,.32]
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
  /office|commercial|retail|school|university|industrial|warehouse/.test(kind)?1:
  /residential|apartment|house|dormitory|bungalow/.test(kind)?0:3;
 return {seed:(hash%65521)/65521,profile,base:b.base,floorHeight:3.5};
}
