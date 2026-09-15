/** Bounded source-profile/terrain/collision diagnostics. Not a navigation pass. */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {routeContext} from '../tai-o-completion/route_context.mjs';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
const here=new URL('./',import.meta.url),doc=new URL('../../../docs/astra-city/central-completion/',here);
const routes=JSON.parse(await readFile(new URL('route-candidates.json',doc),'utf8')).routes;
const patchRaw=await readFile(new URL('terrain-central.json',here)),patch=JSON.parse(patchRaw);
const coarse=JSON.parse(await readFile(new URL('../../../3d-viewer/city/data/terrain.json',here),'utf8'));
const fine=makeTerrainSampler({...coarse,patches:[patch]});
function stats(values){const sorted=values.toSorted((a,b)=>a-b);return{median:sorted[Math.floor(sorted.length*.5)],p95:sorted[Math.floor(sorted.length*.95)],max:sorted.at(-1)}}
const results=[];
for(const route of routes){
 const {sampler:current,index}=routeContext(route),errors={current:[],staged:[]},wet={current:0,staged:0},contacts={current:0,staged:0},blockers=new Map();let samples=0;
 for(const [i,a]of route.sourceCentrelineXYZ.entries()){
  const b=route.sourceCentrelineXYZ[i+1];if(!b)break;const length=Math.hypot(...a.map((v,k)=>v-b[k])),count=Math.max(1,Math.ceil(length));
  for(let j=0;j<count;j++){
   const p=a.map((v,k)=>v+(b[k]-v)*j/count);samples++;
   for(const [name,sampler]of [['current',current],['staged',fine]]){
    const y=sampler.height(p[0],p[2]);errors[name].push(Math.abs(y-p[1]));if(sampler.raw(p[0],p[2])<=0||sampler.mappedWater(p[0],p[2]))wet[name]++;
    const collision=index.collision(p[0],p[2],y+.09,y+1.8,.55);if(collision){contacts[name]++;if(name==='staged'&&!blockers.has(collision.uid))blockers.set(collision.uid,{uid:collision.uid,name:collision.name,sample:p,terrainY:y})}
   }
  }
 }
 results.push({id:route.id,samples,absoluteGroundToSourceNetworkHeightMetres:{current:stats(errors.current),staged:stats(errors.staged)},wetSamples:wet,buildingContactSamples:contacts,stagedBlockerBuildings:[...blockers.values()]});
}
const old=makeTerrainSampler(coarse),patchSampler=makeTerrainSampler(patch),g=patch.meta.georef;let maxPerimeterError=0,perimeterSamples=0;
for(let row=0;row<patch.h;row++)for(const col of [0,patch.w-1]){const x=g.bE+col*5-834500,z=816500-g.bN+row*5;maxPerimeterError=Math.max(maxPerimeterError,Math.abs(patchSampler.height(x,z)-old.height(x,z)));perimeterSamples++}
for(let col=1;col<patch.w-1;col++)for(const row of [0,patch.h-1]){const x=g.bE+col*5-834500,z=816500-g.bN+row*5;maxPerimeterError=Math.max(maxPerimeterError,Math.abs(patchSampler.height(x,z)-old.height(x,z)));perimeterSamples++}
const report={status:'preflight-only-not-navigation-acceptance',stagedTerrainSha256:createHash('sha256').update(patchRaw).digest('hex'),sampling:'Every original 3D route edge subdivided into intervals no longer than 1 m; no source geometry changes.',sourceAccuracy:{horizontalMetres:1,verticalMetres:2},collisionPolicy:'Existing live BuildingIndex, 0.55 m actor radius, 1.8 m height above each sampled ground; detailed Central meshes not integrated. Contacts identify review work, not proof of private access.',terrainPerimeter:{samples:perimeterSamples,maxRenderedHeightDifferenceMetres:maxPerimeterError},routes:results,limits:['No continuous Navigation.update replay performed.','Original 3DPN Z can differ by its stated ±2 m vertical accuracy; it is not a surveyed deck surface.','Bridge floors, public stairs and mapped coastline require separate source integration.','Current collision blockers remain; no automatic model/ground shifts or collision suppression.']};
await writeFile(new URL('route-preflight.json',doc),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...report,routes:results.map(({stagedBlockerBuildings,...r})=>({...r,stagedBlockerBuildingCount:stagedBlockerBuildings.length}))},null,2));
