import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {hktParts,dateFromHKT,horizontalDirection,getSkyState} from '../sky-time.js';
import {starPosition} from '../../vendor/astro.js';

const minutes=date=>hktParts(date).hour*60;
const close=(actual,expected,tolerance)=>assert.ok(Math.abs(actual-expected)<=tolerance,`${actual} is outside ${expected} ± ${tolerance}`);

test('HKT inputs are timezone-independent and carry the civil date across midnight',()=>{
 assert.deepEqual(hktParts(new Date('2026-09-06T16:15:30Z')),{date:'2026-09-07',time:'00:15',hour:.25833333333333336,hours:0,minutes:15,seconds:30});
 assert.equal(dateFromHKT('2026-09-06',0).toISOString(),'2026-09-05T16:00:00.000Z');
 assert.equal(dateFromHKT('2026-12-31',25).toISOString(),'2026-12-31T17:00:00.000Z');
 assert.equal(hktParts(dateFromHKT('2026-12-31',25)).date,'2027-01-01');
 assert.equal(hktParts(dateFromHKT('2026-01-01',-1)).date,'2025-12-31');
 assert.equal(hktParts(dateFromHKT('2028-02-29',12)).date,'2028-02-29');
 for(const date of ['2026-02-29','2026-02-30','2026-13-01','2026-00-04','not-a-date'])assert.equal(dateFromHKT(date),null);
 assert.equal(dateFromHKT('2026-09-06',NaN),null);assert.throws(()=>getSkyState(new Date(NaN)),RangeError);
});

test('cardinal sky directions match city east/up/south coordinates',()=>{
 const pi=Math.PI;
 for(const [az,alt,expected]of [[0,0,[0,0,1]],[-pi/2,0,[1,0,0]],[pi,0,[0,0,-1]],[pi/2,0,[-1,0,0]],[0,pi/2,[0,1,0]]]){
  const d=horizontalDirection(az,alt);[d.x,d.y,d.z].forEach((v,i)=>close(v,expected[i],1e-12));
 }
 const morning=getSkyState(dateFromHKT('2026-09-06',8)),afternoon=getSkyState(dateFromHKT('2026-09-06',17));
 assert.ok(morning.sun.direction.x>0);assert.ok(afternoon.sun.direction.x<0);
 for(const body of [morning.sun,morning.moon,afternoon.sun,afternoon.moon])close(Math.hypot(...Object.values(body.direction)),1,1e-12);
});

test('rise/set agrees with HKO seasonal reference days and remains on the selected HKT day',()=>{
 // HKO Almanac 2026, June 21 / September 6 / December 21 (linked in SKY-INTEGRATION.md).
 // Compact solar ephemeris is within 3 minutes; lunar ephemeris within 15 minutes.
 for(const [day,rise,set,moonRise,moonSet]of [
  ['2026-06-21',340,1150,706,null],['2026-09-06',367,1116,40,893],['2026-12-21',418,1064,891,219]
 ]){
  const state=getSkyState(dateFromHKT(day,0));
  close(minutes(state.sunrise),rise,3);close(minutes(state.sunset),set,3);
  close(minutes(state.moonrise),moonRise,15);
  if(moonSet===null)assert.equal(state.moonset,null);else close(minutes(state.moonset),moonSet,15);
  assert.equal(hktParts(state.sunrise).date,day);assert.equal(hktParts(state.sunset).date,day);
  const evening=getSkyState(dateFromHKT(day,23.9));
  assert.equal(evening.sunrise.getTime(),state.sunrise.getTime());
 }
 const summer=getSkyState(dateFromHKT('2026-06-21')),winter=getSkyState(dateFromHKT('2026-12-21'));
 assert.ok(summer.sun.altitudeDeg>80);assert.ok(winter.sun.altitudeDeg<46);
 assert.ok(summer.sunset-summer.sunrise>winter.sunset-winter.sunrise+2*3600000);
});

test('night follows solar altitude and moon phase follows the date',()=>{
 const day=getSkyState(dateFromHKT('2026-09-06',12)),night=getSkyState(dateFromHKT('2026-09-06',0));
 assert.equal(day.night,0);assert.equal(day.starVisibility,0);assert.equal(night.night,1);assert.equal(night.starVisibility,1);
 assert.ok(getSkyState(dateFromHKT('2026-06-30',7.95)).moon.fraction>.99);
 assert.ok(getSkyState(dateFromHKT('2026-06-15',10.9)).moon.fraction<.01);
 // Same civil clock time in summer/winter must produce different twilight.
 const summer=getSkyState(dateFromHKT('2026-06-21',18.5)),winter=getSkyState(dateFromHKT('2026-12-21',18.5));
 assert.equal(summer.night,0);assert.equal(winter.night,1);
});

test('the original catalogue keeps every constellation member and Polaris stays over north',async()=>{
 const catalogue=JSON.parse(await readFile(new URL('../../data/hk-sky.json',import.meta.url))),ids=new Set(catalogue.stars.map(s=>s[0]));
 assert.equal(catalogue.stars.length,1573);assert.equal(catalogue.constellations.length,24);assert.equal(ids.size,catalogue.stars.length);
 for(const c of catalogue.constellations)for(const line of c.lines)for(const id of line)assert.ok(ids.has(id),`${c.iau} missing HR ${id}`);
 const polaris=catalogue.stars.find(s=>s[0]===424);assert.ok(polaris);
 for(const hour of [0,6,12,18]){
  const p=starPosition(dateFromHKT('2026-09-06',hour),22.3,114.17,polaris[1]*Math.PI/12,polaris[2]*Math.PI/180),d=horizontalDirection(p.azimuth,p.altitude);
  assert.ok(d.z<-.90);close(p.altitude*180/Math.PI,22.3,1);
 }
});
