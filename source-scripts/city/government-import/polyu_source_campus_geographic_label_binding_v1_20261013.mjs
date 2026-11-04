// Source-location context only. No geometry, database, acceptance or publication edits.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {worldToWgs84} from '../../../3d-viewer/city/observer.js';

const root=new URL('../../../',import.meta.url);
const source='docs/astra-city/government-import/government-xl-polyu-sports305582-root-primary-interface-lookup-v1-20261013/';
const out='docs/astra-city/government-import/government-xl-polyu-sports305582-geographic-campus-label-context-v1-20261013/';
const digest=b=>createHash('sha256').update(b).digest('hex');
const ref=p=>({path:p,sha256:digest(readFileSync(new URL(p,root)))});
const read=p=>JSON.parse(readFileSync(new URL(p,root),'utf8'));
const pins={
 '3d-viewer/city/data/manifest.json':'c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7',
 '3d-viewer/city/data/tiles/1_-1.json':'90cf321eca8e4da666a8d8ff0be71913a10e9cdeeeae8483384cb8f9895c712a',
 '3d-viewer/city/data/tiles/1_-2.json':'910d3fdb3833c2dad295b88816af46c0555047112e52890b7029a787ec1db346',
 [source+'official-Building-poi.json']:'e630d407ddce205686a378e8f13c75ed5af056437dfb41f34f50e3043c4e5367',
 [source+'official-CoreLocation-poi.json']:'82187c5e395dcff19307eb99dd68a79d20f6ebafe0f5088bacfdd45622fc6fbf',
 [source+'root-primary-label-and-podium-scope-review.json']:'c77663ffc599651bc164f41dc175e6faaaf91ffb805c19aa602a6986f2d64b70',
};
const forms=read(source+'exact-current-four-provider-forms.json');
assert.equal(forms.length,4);
assert.deepEqual(forms.map(f=>f.uid),['landsd/72322:0','landsd/258852:0','landsd/305793:0','landsd/305582:0']);
const liveForms=['1_-1','1_-2'].flatMap(t=>read('3d-viewer/city/data/tiles/'+t+'.json').buildings);
for(const form of forms)assert.deepEqual(liveForms.find(f=>f.uid===form.uid),form);
const inputRefs=[...Object.keys(pins),source+'exact-current-four-provider-forms.json',
 '3d-viewer/city/observer.js','3d-viewer/city/observer-grid.js',
 '3d-viewer/city/tests/observer.test.js','3d-viewer/city/tests/observer-reference.json',
 'source-scripts/city/government-import/polyu_source_campus_geographic_label_binding_v1_20261013.mjs'].map(ref);
function fence(){for(const r of inputRefs)assert.deepEqual(ref(r.path),r);for(const [p,h]of Object.entries(pins))assert.equal(ref(p).sha256,h);}
fence();
const publicData=file=>{const j=read(source+file);assert(!j.error&&Array.isArray(j.value));return j.value;};
const buildings=publicData('official-Building-poi.json'),locations=publicData('official-CoreLocation-poi.json');
assert.equal(buildings.length,53);assert.equal(locations.length,33);
const ringContains=(lon,lat,ring)=>{let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){
 const a=ring[i],b=ring[j];if((a.lat>lat)!==(b.lat>lat)&&lon<(b.lon-a.lon)*(lat-a.lat)/(b.lat-a.lat)+a.lon)inside=!inside;
}return inside;};
const polygonContains=(p,rings)=>ringContains(p.lon,p.lat,rings[0])&&!rings.slice(1).some(r=>ringContains(p.lon,p.lat,r));
const point=v=>{if(!v)return null;const p={lat:Number(v.latitude),lon:Number(v.longitude)};assert(Number.isFinite(p.lat)&&Number.isFinite(p.lon));return p;};
const metres=(a,b)=>{const rad=Math.PI/180,u=(b.lat-a.lat)*rad,v=(b.lon-a.lon)*rad;
 return 6371008.8*2*Math.asin(Math.sqrt(Math.sin(u/2)**2+Math.cos(a.lat*rad)*Math.cos(b.lat*rad)*Math.sin(v/2)**2));};
const rows=forms.map(f=>{
 const rings=f.rings.map(r=>r.map(([x,z])=>{const p=worldToWgs84(x,z);assert(p);return p;}));
 const centre=worldToWgs84(...f.centre);assert(centre);
 const labels=[...buildings,...locations].map(p=>({id:p.id,category:p.category,name:p.name.en_US,loc:p.loc,
  marker:point(p.marker),mapmarker:point(p.mapmarker),waypoint:point(p.waypoint)})).map(p=>({...p,
  markerInsideApproximateGeographicFootprint:polygonContains(p.marker,rings),
  mapMarkerInsideApproximateGeographicFootprint:p.mapmarker?polygonContains(p.mapmarker,rings):false,
  approximateMarkerDistanceFromSourceCentreM:metres(centre,p.marker)}));
 return {uid:f.uid,displayName:f.name,sourceStructureType:f.structureType,sourceBuildingCSUID:f.buildingCSUID,
  sourceBuildingId:f.buildingId,sourceBaseHKPD:f.baseHeightHKPD,sourceTopHKPD:f.topHeightHKPD,
  exactUnchangedSourceCentreXZ:f.centre,approximateCentreWGS84:centre,footprintRingVertexCounts:f.rings.map(r=>r.length),
  exactSourceWorldBoundsXZ:f.rings.map(r=>[Math.min(...r.map(p=>p[0])),Math.min(...r.map(p=>p[1])),Math.max(...r.map(p=>p[0])),Math.max(...r.map(p=>p[1]))]),
  approximateGeographicRings:rings,primaryLabels:labels};
});
const result={executor:'Codex ROOT',sourceOnly:true,sourceGeometryChanges:0,terrainGeometryChanges:0,
 identityAccepted:false,physicalAccepted:false,installationApproved:false,newlyInstalled:0,
 conversion:'Existing worldToWgs84 inverse-PROJ grid interpolation; coordinates are diagnostic approximate geographic labels, not a new surveyed registration.',
 validation:'Existing observer tests compare >=40 independent direct-PROJ points at <0.25m. This is sampled validation, not a universal error certificate or POI survey-accuracy claim.',
 limitations:['Primary POI marker/mapmarker/waypoint locations can differ and are labels/entrances, not footprint ownership.',
 'Approximate point containment does not establish provider mesh ownership, intended contact, solid penetration, engineering joints or physical acceptance.',
 'The government podium outer ring and inner rings are one polygon footprint; ring count does not imply separate objects.',
 'No source face/contact/ground predicate replay or original mesh decoding occurred.'],
 inputRefs,primaryOfficialBuildingRecords:53,primaryOfficialCoreLocationRecords:33,rows};
fence();assert(!existsSync(new URL(out,root)));mkdirSync(new URL(out,root));
writeFileSync(new URL(out+'context.json',root),JSON.stringify(result,null,2)+'\n');fence();
console.log(JSON.stringify({context:ref(out+'context.json'),forms:rows.map(r=>({uid:r.uid,structureType:r.sourceStructureType,
 bounds:r.exactSourceWorldBoundsXZ[0],centre:r.approximateCentreWGS84,
 insideOfficialBuildingLabels:r.primaryLabels.filter(p=>p.category==='Building'&&(p.markerInsideApproximateGeographicFootprint||p.mapMarkerInsideApproximateGeographicFootprint)).map(p=>p.name)}))}));
