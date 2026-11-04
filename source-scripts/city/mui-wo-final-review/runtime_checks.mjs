/** Staged individual meshes, nested sampler and the unchanged public route. No GPU. */
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {BuildingIndex,makeTerrainSampler,terrainVertexHeight} from '../../../3d-viewer/city/geo.js';
import {makeTerrain} from '../../../3d-viewer/city/world.js';
import {routeContext,root,read} from '../tai-o-completion/route_context.mjs';
import {stagedSurfaces} from '../mui-wo-completion/context.mjs';
import {makeRouteNavigation,replayRoute} from '../tai-o-completion/route_navigation.mjs';
const bundle=read('source-scripts/city/mui-wo-final-review/terrain-refinements.json'),manifest=read('3d-viewer/city/data/manifest.json'),terrain=read('3d-viewer/city/data/terrain.json');
terrain.patches=manifest.terrainPatches.map(p=>{const d=read('3d-viewer/'+p.url);if(p.url===bundle.parentTerrainURL)d.patches=bundle.patches;return d;});
const sampler=makeTerrainSampler(terrain),oldParent=read('3d-viewer/'+bundle.parentTerrainURL),oldSampler=makeTerrainSampler(oldParent);let vertices=0,seams=0,maxVertexError=0,maxSeamError=0,mappedWaterNodes=0;
for(const p of bundle.patches){
 const mesh=makeTerrain(p),position=mesh.geometry.attributes.position,g=p.meta.georef;
 for(let r=0;r<p.h;r++)for(let c=0;c<p.w;c++){
  const i=r*p.w+c,x=g.bE+c-834500,z=816500-g.bN+r;vertices++;
  const error=Math.abs(position.getY(i)-terrainVertexHeight(p,i));maxVertexError=Math.max(maxVertexError,error);assert(error<.001);
  assert.equal(sampler.mappedWater(x,z),false,'Bounded refinements avoid mapped water');mappedWaterNodes+=sampler.mappedWater(x,z)?1:0;
  if(r===0||c===0||r===p.h-1||c===p.w-1){const error=Math.abs(sampler.height(x,z)-oldSampler.height(x,z));maxSeamError=Math.max(maxSeamError,error);assert(error<.001);seams++;}
  else assert.equal(sampler.resolutionAt(x,z),1);
 }
 mesh.geometry.dispose();mesh.material.dispose();
}
const source=read('docs/astra-city/mui-wo-completion/route-navigation.json'),line=source.walkCentreline,ctx={...routeContext({centreline:line}),sampler,surfaces:stagedSurfaces()},options={maxFrames:90000};
const estimateUpdates=read('source-scripts/city/mui-wo-final-review/building-estimate-updates.json').buildings;
for(const update of estimateUpdates){const building=ctx.buildings.find(b=>b.uid===update.uid);if(building){assert.equal(building.base,update.previousBase);assert.equal(building.baseHeightHKPD,null);assert.equal(building.topHeightHKPD,null);assert.equal(building.modelGeometry,undefined);building.base=update.base;}}
ctx.index=new BuildingIndex(ctx.buildings);
const forward=replayRoute(makeRouteNavigation(ctx),line,options),reverse=replayRoute(makeRouteNavigation(ctx),line,{...options,reverse:true});assert.equal(forward.passed,true);assert.equal(reverse.passed,true);
const report={stagedOnly:true,refinementSha256:createHash('sha256').update(readFileSync(root+'/source-scripts/city/mui-wo-final-review/terrain-refinements.json')).digest('hex'),checks:{estimatedBasesStaged:estimateUpdates.length,vertices,seams,maxVertexError,maxSeamError,mappedWaterNodes},route:{forward,reverse,source:'docs/astra-city/mui-wo-completion/route-navigation.json'},scope:'Actual existing individual terrain mesh builder and nested sampler; continuous Navigation replay through the same retained public surfaces. Complete coarse-to-nested rendering and browser acceptance await root integration.'};
writeFileSync(root+'/docs/astra-city/mui-wo-final-review/runtime-checks.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
