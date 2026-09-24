import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {modelSurfaceCollision} from '../../../3d-viewer/city/model-collision.js';
import {geometryFor} from '../../../3d-viewer/city/bridges.js';
const root=fileURLToPath(new URL('../../../',import.meta.url)),here=fileURLToPath(new URL('./',import.meta.url));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const data=read(here+'bridges-tsing-ma.json'),cables=read(here+'cables-tsing-ma.json'),patch=read(here+'terrain-tsing-ma.json'),hydro=read(here+'hydro-tsing-ma.json'),base=read(root+'3d-viewer/city/data/terrain.json');
const sampler=makeTerrainSampler({...base,hydro,patches:[patch]});
for(const p of [[-9250,-6940],[-9000,-7010],[-8750,-7090],[-8500,-7160],[-8250,-7240]]){assert.equal(sampler.mappedWater(...p),true);assert.equal(sampler.height(...p),-4);assert.equal(data.models.some(m=>modelSurfaceCollision(m.modelGeometry,...p,0,55,.55)),false);}
assert.equal(sampler.mappedWater(-9500,-6860),false);assert.ok(Math.abs(sampler.height(-9500,-6860)-6.785)<.001);
assert.equal(data.models.some(m=>modelSurfaceCollision(m.modelGeometry,-9000,-7010,76,78,.55)),true);
assert.equal(data.models.some(m=>modelSurfaceCollision(m.modelGeometry,-9000,-7010,80,82,.55)),false);
let triangles=0;for(const model of data.models){assert.equal(model.walkable,false);const g=geometryFor(model);assert.ok(g.boundingBox.min.distanceTo(g.boundingBox.max)>0);triangles+=g.attributes.position.count/3;assert.ok([...g.attributes.position.array].every(Number.isFinite));g.dispose();}
const c=geometryFor({modelGeometry:cables.modelGeometry});assert.equal(c.attributes.position.count/3,6432);c.dispose();
const report={status:'pass',sourceModels:data.models.length,sourceTriangles:triangles,illustrativeTriangles:6432,marineUnderSpanSamples:5,underSpanCollisionFreeToHKPD:55,sourceDeckCollision:'present at76–78m; absent at80–82m for selected centre point',islandHeightHKPD:sampler.height(-9500,-6860),gpuUsed:false,limits:['Shared geometry and collision helpers exercised directly. Actual city loading, composite hydro integration, source picking and GPU browser proof are root-owned follow-up checks.']};
fs.writeFileSync(root+'docs/astra-city/tsing-ma/runtime-helper-verification.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
