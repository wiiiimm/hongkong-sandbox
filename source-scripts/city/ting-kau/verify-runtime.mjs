import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {makeTerrainSampler,inPolygon} from '../../../3d-viewer/city/geo.js';
import {modelSurfaceCollision} from '../../../3d-viewer/city/model-collision.js';
import {geometryFor} from '../../../3d-viewer/city/bridges.js';
const root=fileURLToPath(new URL('../../../',import.meta.url)),here=fileURLToPath(new URL('./',import.meta.url));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const foundationsCandidate=process.argv.includes('--foundations');
const combined=process.argv.includes('--combined')||foundationsCandidate;
const candidateDir=foundationsCandidate?'foundation-candidate/':'combined/';
const data=read(here+'bridges-ting-kau.json'),cables=read(here+'cables-ting-kau.json'),patch=read(here+(combined?candidateDir+'terrain-tsing-ma-ting-kau.json':'terrain-ting-kau.json')),hydro=read(here+(combined?candidateDir+'hydro-tsing-ma-ting-kau.json':'hydro-ting-kau.json')),base=read(root+'3d-viewer/city/data/terrain.json'),model=data.models[0];
const sampler=makeTerrainSampler({...base,hydro,patches:[patch]}),samples=[];
for(const [x,z]of [[-8350.76,-8704.7],[-8300.76,-8604.7],[-8190.76,-8374.7],[-8150.76,-8294.7]]){
 assert.equal(sampler.mappedWater(x,z),true);assert.equal(sampler.height(x,z),-4);
 assert.equal(modelSurfaceCollision(model.modelGeometry,x,z,0,55,.55),false);
 const intersections=[];for(let y=60;y<100;y+=.5)if(modelSurfaceCollision(model.modelGeometry,x,z,y,y+.4,.55))intersections.push(y);
 assert.ok(intersections.length>0,'Expected actual source deck collision at '+[x,z]);samples.push({world:[x,z],ground:sampler.height(x,z),underSpanClearToHKPD:55,sourceCollisionRange:[Math.min(...intersections),Math.max(...intersections)+.4]});
}
const foundations=[[-8427.765,-8887.478],[-8229.83,-8485.528],[-8019.633,-8059.256]].map(([x,z])=>{assert.equal(sampler.mappedWater(x,z),false);return {world:[x,z],heightHKPD:sampler.height(x,z)};});
let g=geometryFor(model);assert.equal(g.attributes.position.count/3,16995);assert.ok([...g.attributes.position.array].every(Number.isFinite));g.dispose();
g=geometryFor({modelGeometry:cables.modelGeometry});assert.equal(g.attributes.position.count/3,4104);g.dispose();
assert.equal(model.walkable,false);assert.equal(data.models.length,1);
const report={status:'pass',originalSourceModels:1,sourceTriangles:16995,illustrativeTriangles:4104,marineSamples:samples,preservedFoundations:foundations,gpuUsed:false,limits:['Actual shared geometry, terrain and source-surface collision helpers exercised. Generic source-package loader integration, composite terrain/hydro, source picking and browser rendering remain root-owned.','55m here is a sampled software collision check, not a navigational clearance assertion.']};
if(combined){
 const tsing=read(here+'../tsing-ma/bridges-tsing-ma.json');
 const points=[[-9250,-6940],[-9000,-7010],[-8750,-7090],[-8500,-7160],[-8250,-7240]];
 for(const p of points){assert.equal(sampler.mappedWater(...p),true);assert.equal(sampler.height(...p),-4);assert.equal(tsing.models.some(m=>modelSurfaceCollision(m.modelGeometry,...p,0,55,.55)),false);}
 assert.equal(sampler.mappedWater(-9500,-6860),false);assert.ok(Math.abs(sampler.height(-9500,-6860)-6.785)<.001);
 assert.equal(tsing.models.some(m=>modelSurfaceCollision(m.modelGeometry,-9000,-7010,76,78,.55)),true);
 assert.equal(tsing.models.some(m=>modelSurfaceCollision(m.modelGeometry,-9000,-7010,80,82,.55)),false);
 report.tsingMa={marineSamples:points.length,underSpanClearToHKPD:55,sourceDeckCollision:'present at 76–78 m; absent at 80–82 m for selected centre point',preservedIslandHeightHKPD:sampler.height(-9500,-6860)};
 report.combinedTerrainDimensions=[patch.w,patch.h];report.limits[0]='Actual shared geometry, combined terrain/hydro and both bridges’ source-surface collision helpers exercised. Generic package loading, picking and browser rendering remain root-owned.';
}
if(foundationsCandidate){
 const features=read(here+'foundation-candidate/foundation-scope.geojson').features,local=makeTerrainSampler(patch),g=patch.meta.georef;
 report.wholeIslandSampler=[];
 for(const feature of features.filter(f=>f.properties.role==='mapped-foundation-island')){
  const rings=feature.geometry.coordinates,samples=[];
  for(let r=0;r<patch.h;r++)for(let c=0;c<patch.w;c++){const x=g.bE+c*5-834500,z=816500-g.bN+r*5;if(!inPolygon(x,z,rings))continue;assert.equal(sampler.mappedWater(x,z),false);assert.equal(sampler.height(x,z),local.height(x,z));assert.ok(sampler.height(x,z)>1.2&&sampler.height(x,z)<11.3);samples.push(sampler.height(x,z));}
  report.wholeIslandSampler.push({name:feature.properties.name,samples:samples.length,heightHKPD:[Math.min(...samples),Math.max(...samples)]});
 }
}
fs.writeFileSync(root+'docs/astra-city/ting-kau/'+(foundationsCandidate?'foundations/':combined?'combined/':'')+'runtime-helper-verification.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
