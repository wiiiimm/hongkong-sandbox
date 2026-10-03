import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {worldToWgs84,OBSERVER_BOUNDS} from '../observer.js';
import {PLACES} from '../places.js';
import {ORIGIN} from '../geo.js';

const radians=Math.PI/180;
function metres(a,b){
 const dLat=(b.lat-a.lat)*radians,dLon=(b.lon-a.lon)*radians;
 return 6371008.8*2*Math.asin(Math.sqrt(Math.sin(dLat/2)**2+Math.cos(a.lat*radians)*Math.cos(b.lat*radians)*Math.sin(dLon/2)**2));
}

test('runtime observer coordinates agree with independent direct-PROJ check points',async()=>{
 const references=JSON.parse(await readFile(new URL('./observer-reference.json',import.meta.url)));
 assert.ok(references.length>=40);
 for(const ref of references){const actual=worldToWgs84(ref.x,ref.z);assert.ok(actual);assert.ok(metres(actual,ref)<.25,`Projection error at ${ref.x}, ${ref.z}: ${metres(actual,ref)} m`);}
 // Origin reference from EPSG:2326 (834500 E, 816500 N), not a guessed city centre.
 assert.ok(metres(worldToWgs84(0,0),{lat:22.287394706232032,lon:114.15971810666576})<.25);
});

test('observer grid matches the current terrain and rejects unmeasured extrapolation',async()=>{
 const {w,h,meta}=JSON.parse(await readFile(new URL('../data/terrain.json',import.meta.url))),g=meta.georef;
 assert.deepEqual(meta.origin,ORIGIN);
 assert.deepEqual(OBSERVER_BOUNDS,[g.bE-ORIGIN[0],ORIGIN[1]-g.bN,g.bE+(w-1)*g.aE-ORIGIN[0],ORIGIN[1]-g.bN-(h-1)*g.aN]);
 const [x0,z0,x1,z1]=OBSERVER_BOUNDS;
 for(const [x,z]of [[x0,z0],[x1,z0],[x0,z1],[x1,z1]])assert.ok(worldToWgs84(x,z));
 for(const [x,z]of [[x0-.001,z0],[x1+.001,z0],[x0,z0-.001],[x0,z1+.001],[NaN,0],[0,Infinity],[-Infinity,0],['0',0],[null,0]])assert.equal(worldToWgs84(x,z),null);
});

test('free movement changes sky coordinates with east/north orientation and preset consistency',()=>{
 const origin=worldToWgs84(0,0),east=worldToWgs84(1000,0),north=worldToWgs84(0,-1000);
 assert.ok(east.lon>origin.lon);assert.ok(north.lat>origin.lat);
 assert.ok(metres(origin,east)>995&&metres(origin,east)<1005);assert.ok(metres(origin,north)>995&&metres(origin,north)<1005);
 let compared=0;
 for(const place of Object.values(PLACES)){
  const actual=worldToWgs84(place.target[0],place.target[2]);if(!actual)continue;
  assert.ok(metres(actual,place)<.5,place.title);compared++;
 }
 assert.ok(compared>20);
});
