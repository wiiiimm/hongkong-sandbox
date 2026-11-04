/** Actual nested terrain renderer/sampler and retained Pui O public route checks. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {makeTerrainSampler,terrainVertexHeight,BuildingIndex} from '../../../3d-viewer/city/geo.js';
import {prepareModelCatalogue,loadOfficialModel,disposeOfficialModel} from '../../../3d-viewer/city/official-model-assets.js';
import {InfrastructureSurfaces} from '../../../3d-viewer/city/infrastructure-data.js';
import {root,read,routeContext} from '../tai-o-completion/route_context.mjs';
import {makeRouteNavigation,replayRoute} from '../tai-o-completion/route_navigation.mjs';
const base='source-scripts/city/pui-o-detail-completion/',doc='docs/astra-city/pui-o-detail-completion/',bundle=read(base+'terrain-refinements.json'),parent=read('3d-viewer/'+bundle.parentTerrainURL),oldSampler=makeTerrainSampler(parent),staged={...parent,patches:bundle.patches},sampler=makeTerrainSampler(staged),mesh=makeTerrain(staged);mesh.updateMatrixWorld(true);let checkedVertices=0,seams=0,waterChanges=0,rayChecks=0,maxSeamError=0,maxRayError=0;
for(const patch of bundle.patches){const g=patch.meta.georef;
 for(let r=0;r<patch.h;r++)for(let c=0;c<patch.w;c++){
  const x=g.bE+c-834500,z=816500-g.bN+r,i=r*patch.w+c;checkedVertices++;assert(Math.abs(sampler.height(x,z)-terrainVertexHeight(patch,i))<.001);waterChanges+=Number(sampler.mappedWater(x,z)!==oldSampler.mappedWater(x,z));
  if(!r||!c||r===patch.h-1||c===patch.w-1){maxSeamError=Math.max(maxSeamError,Math.abs(sampler.height(x,z)-oldSampler.height(x,z)));seams++;}
 }
 for(const u of [.25,.5,.75])for(const v of [.25,.5,.75]){const x=g.bE+u*(patch.w-1)-834500,z=816500-g.bN+v*(patch.h-1),expected=sampler.height(x,z),ray=new THREE.Raycaster(new THREE.Vector3(x,1000,z),new THREE.Vector3(0,-1,0)),hits=ray.intersectObject(mesh,true);assert(hits.length);const error=Math.abs(hits[0].point.y-expected);maxRayError=Math.max(maxRayError,error);assert(error<.002);const surfaces=new Set(hits.map(h=>h.point.y.toFixed(2)));assert.equal(surfaces.size,1,'No retained coarse ground overlaps nested source terrain');rayChecks++;}
}
assert.equal(waterChanges,0);assert(maxSeamError<.001);
const route=read('docs/astra-city/pui-o-completion/route.json'),ctx=routeContext(route),terrain=read('3d-viewer/city/data/terrain.json');terrain.patches=ctx.manifest.terrainPatches.map(p=>p.url===bundle.parentTerrainURL?staged:read('3d-viewer/'+p.url));const routeSampler=makeTerrainSampler(terrain),changes=read(base+'building-estimate-updates.json').buildings;
for(const u of changes){const b=ctx.buildings.find(b=>b.uid===u.uid);if(!b)continue;assert.equal(b.base,u.previousBase);assert.equal(b.baseHeightHKPD,null);assert.equal(b.topHeightHKPD,null);assert.equal(b.height,u.height);assert(!b.modelGeometry);b.base=u.base;}
const models=[],lighting={night:{value:1},activity:{value:new THREE.Vector4(1,1,1,1)},retail:{value:1},elapsed:{value:0},shimmer:{value:0}},entries=prepareModelCatalogue(read(base+'compact/catalogue.json'),'http://localhost/pui-o/catalogue.json');
for(const e of entries){const b=ctx.buildings.find(b=>b.uid===e.uid);assert(b);const asset=readFileSync(root+'/'+base+'compact/'+e.asset),model=await loadOfficialModel(e,b,lighting,{fetcher:async()=>new Response(asset)});models.push(model);Object.assign(b,model.record);}
const context={sampler:routeSampler,index:new BuildingIndex(ctx.buildings),surfaces:new InfrastructureSurfaces()},forward=replayRoute(makeRouteNavigation(context),route.centreline),reverse=replayRoute(makeRouteNavigation(context),route.centreline,{reverse:true});assert(forward.passed);assert(reverse.passed);
mesh.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});for(const m of models)disposeOfficialModel(m);
const report={staged:true,checks:{checkedVertices,seams,waterChanges,rayChecks,maxSeamError,maxRayError,sourceModelsLoaded:models.length,dependentEstimatedBases:changes.length},route:{lengthMetres:route.lengthMetres,forward,reverse},refinementSha256:createHash('sha256').update(readFileSync(root+'/'+base+'terrain-refinements.json')).digest('hex'),scope:'Actual shared nested renderer, nested sampler, loaded source-model collision records and existing Navigation on retained public beach route. CPU-only; root still needs browser/day/night/mobile visual acceptance.'};writeFileSync(root+'/'+doc+'terrain-runtime.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
