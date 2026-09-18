/** Exercise the existing source-geometry, water and collision adapters without GPU. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {prepareInfrastructure,InfrastructureSurfaces} from '../../../3d-viewer/city/infrastructure-data.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {geometryFor} from '../../../3d-viewer/city/bridges.js';
const read=p=>JSON.parse(fs.readFileSync(new URL(p,import.meta.url),'utf8'));
const data=read('bridges-stonecutters.json'),patch=read('terrain-stonecutters.json'),hydro=read('hydro-stonecutters.json'),base=read('../../../3d-viewer/city/data/terrain.json');
const records=prepareInfrastructure(data),surfaces=new InfrastructureSurfaces(),sampler=makeTerrainSampler({...base,patches:[patch],hydro});
assert.equal(records.length,3);let triangles=0;
for(const record of records){surfaces.add(record);const g=geometryFor(record);triangles+=g.attributes.position.count/3;assert.deepEqual([...g.attributes.position.array],Array.from(new Float32Array(record.modelGeometry.position)));g.dispose();}
assert.equal(triangles,23634);
const a=[-4634.028,-4573.747],b=[-3849.81,-3924.645],length=Math.hypot(b[0]-a[0],b[1]-a[1]),side=[-(b[1]-a[1])/length,(b[0]-a[0])/length],samples=[];
for(const fraction of [.2,.35,.5,.65,.8]){
 const x=a[0]+fraction*(b[0]-a[0])+side[0]*15,z=a[1]+fraction*(b[1]-a[1])+side[1]*15;
 assert.equal(sampler.mappedWater(x,z),true);assert.equal(sampler.height(x,z),-4);assert.deepEqual(surfaces.heights(x,z),[]);assert.equal(surfaces.collision(x,z,0,60,.55),null);
 const contact=[];for(let y=65;y<105;y+=.5)if(surfaces.collision(x,z,y,y+.4,.55))contact.push(y);assert.ok(contact.length,'Source deck collision at '+[x,z]);samples.push({world:[x,z],underSpanClearToHKPD:60,collisionRange:[Math.min(...contact),Math.max(...contact)+.4]});
}
const report={status:'pass',sourceModels:records.length,sourceTriangles:triangles,marineSamples:samples,publicWalkModels:0,gpuUsed:false,scope:'Existing adapters accept the staged original packet and preserve source geometry/collision. This is not live/browser acceptance or navigational clearance.',remaining:['Port shoreline height-mask repair:1211 mapped-land nodes remain flagged.','Separate cable reconstruction and actual-city AFTER browser acceptance.']};
fs.writeFileSync(new URL('../../../docs/astra-city/stonecutters/runtime-helper-verification.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
