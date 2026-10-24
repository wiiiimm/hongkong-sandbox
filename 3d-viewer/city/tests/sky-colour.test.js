import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {skyColour,skyNightBlend} from '../../sky-colour.js';
import {getSkyState,dateFromHKT} from '../sky-time.js';
test('shared sky palette exactly preserves sampled original renderer colours in both themes',async()=>{
 const reference=JSON.parse(await readFile(new URL('../../../docs/astra-city/golden-hour/original-colour-reference.json',import.meta.url)));
 for(const c of reference.cases)assert.deepEqual(skyColour(c.altitude,c.onPaper).toArray(),c.rgb);
 const day=skyColour(30,true),gold=skyColour(6,true),dusk=skyColour(0,true),night=skyColour(-18,true);
 assert.ok(day.b>day.r);assert.ok(gold.r>gold.b);assert.ok(dusk.r>dusk.b*3);assert.ok(night.r<dusk.r*.02);
});
test('clear haze cannot erase golden/civil twilight; night darkening begins below minus six degrees',()=>{
 for(const altitude of [90,12,6,0,-6])assert.equal(skyNightBlend(altitude),0);
 assert.equal(skyNightBlend(-14),1);assert.ok(skyNightBlend(-10)>0&&skyNightBlend(-10)<1);
});
test('golden sky follows the selected seasonal date and real observer solar altitude',()=>{
 const summer=getSkyState(dateFromHKT('2026-06-21',18)),winter=getSkyState(dateFromHKT('2026-12-21',18));
 assert.ok(summer.sun.altitudeDeg>10);assert.ok(winter.sun.altitudeDeg<-3);
 assert.notDeepEqual(skyColour(summer.sun.altitudeDeg,true).toArray(),skyColour(winter.sun.altitudeDeg,true).toArray());
});
