/** Continuous replay of the actual Navigation.update method, without a GPU or GLTF loads.
 * There is one setMode/spawn per run; all subsequent positions come from walking
 * inputs and swept collision steps. Nothing teleports between route samples.
 */
import {readFileSync,writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {Navigation} from '../../../3d-viewer/city/navigation.js';
import {InfrastructureSurfaces} from '../../../3d-viewer/city/infrastructure-data.js';
import {BridgeLayer} from '../../../3d-viewer/city/bridges.js';
import {root,read,routeContext} from './route_context.mjs';
export function makeRouteNavigation({sampler,index,surfaces,waterLevel=.3}){
 const nav=Object.create(Navigation.prototype);
 Object.assign(nav,{sampler,index,surfaces,waterLevel:()=>waterLevel,waterSurface:()=>waterLevel,mode:'orbit',keys:new Set(),position:new THREE.Vector3(),heading:0,pitch:0,lookPitch:.12,lookYaw:0,time:0,distance:0,firstPerson:true,walker:new THREE.Group(),plane:new THREE.Group(),camera:new THREE.PerspectiveCamera(50,1.6,.1,100000),controls:{enabled:true,target:new THREE.Vector3(),update(){}},onMode(){},toast(){},mixer:null});
 return nav;
}
export function replayRoute(nav,line,{reverse=false,waterLevelChange=null}={}){
 const points=reverse?[...line].reverse():line;
 if(!nav.setMode('walk',points[0]))return {passed:false,reason:'unsafe-initial-arrival',frames:0};
 if(Math.hypot(nav.position.x-points[0][0],nav.position.z-points[0][1])>.001)return {passed:false,reason:'initial-arrival-would-relocate',frames:0};
 nav.firstPerson=true;nav.keys.add('KeyW');let frames=0,simulatedSeconds=0,maxStep=0,stillFrames=0;
 const samples=[{index:0,position:nav.position.toArray()}],start=performance.now();
 for(let i=1;i<points.length;i++){
  let error=Math.hypot(points[i][0]-nav.position.x,points[i][1]-nav.position.z);const initialError=error;
  while(error>.002){
   if(frames>60000)return {passed:false,reason:'frame-limit',frames,atIndex:i,position:nav.position.toArray()};
   const before=nav.position.clone(),dt=Math.min(1/60,error/3.9);
   nav.heading=Math.atan2(points[i][0]-nav.position.x,-(points[i][1]-nav.position.z));
   if(waterLevelChange)waterLevelChange(nav,frames);
   nav.update(dt);frames++;simulatedSeconds+=dt;
   const moved=nav.position.distanceTo(before);maxStep=Math.max(maxStep,moved);
   stillFrames=moved<1e-7?stillFrames+1:0;
   error=Math.hypot(points[i][0]-nav.position.x,points[i][1]-nav.position.z);
   if(stillFrames>30||error>initialError+2){nav.keys.clear();return {passed:false,reason:stillFrames>30?'blocked':'off-route',atIndex:i,target:points[i],position:nav.position.toArray(),frames,distanceMetres:nav.distance,simulatedSeconds,groundHeights:nav.groundHeights(points[i][0],points[i][1]),collisionUid:nav.collides(points[i][0],points[i][1],nav.position.y,nav.position.y+1.8,.55,true)?.uid||null};}
  }
  if(i%100===0||i===points.length-1)samples.push({index:i,position:nav.position.toArray()});
 }
 nav.keys.clear();return {passed:true,frames,distanceMetres:nav.distance,simulatedSeconds,cpuMilliseconds:performance.now()-start,maxFrameMovementMetres:maxStep,initialisations:1,positionResetsAlongRoute:0,samples};
}
export async function loadRouteSurfaces({staged=false,sampler}={}){
 const urls=staged?['staged-bridge-source']:(read('3d-viewer/city/data/manifest.json').bridgeModels||[]);
 if(!urls.length)throw Error('No published source infrastructure surfaces');
 const layer=new BridgeLayer({scene:new THREE.Scene(),sampler}),savedFetch=globalThis.fetch;
 // Reuse the real layer loader and its rendered approach-triangle extraction.
 // Only its network boundary is replaced with the same on-disk manifest bytes.
 globalThis.fetch=async url=>({ok:true,json:async()=>url==='staged-bridge-source'?JSON.parse(gunzipSync(readFileSync(path.join(root,'source-scripts/city/tai-o-completion/infrastructure-models.json.gz')))):read('3d-viewer/'+url)});
 try{for(const url of urls)if(!await layer.load(url))throw Error('Bridge layer failed to prepare '+url);}
 finally{globalThis.fetch=savedFetch;}
 const surfaces=new InfrastructureSurfaces();for(const record of layer.surfaces.models.values())surfaces.add(record);layer.dispose();return surfaces;
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const route=read('docs/astra-city/tai-o-completion/route.json'),context=routeContext(route),surfaces=await loadRouteSurfaces({staged:process.argv.includes('--staged'),sampler:context.sampler}),line=route.walkCentreline||route.centreline;
 const forward=replayRoute(makeRouteNavigation({...context,surfaces}),line),reverse=replayRoute(makeRouteNavigation({...context,surfaces}),line,{reverse:true});
 let negativeCases=null;
 if(forward.passed&&reverse.passed){
  const noFloors=makeRouteNavigation({...context,surfaces:new InfrastructureSurfaces()}),missingFloor=replayRoute(noFloors,line);
  const waterProbe=line.find(([x,z])=>context.sampler.mappedWater?.(x,z));
  const highWater=context.sampler.height(...line[0])+.195,highTide=replayRoute(makeRouteNavigation({...context,surfaces,waterLevel:highWater}),line);
  negativeCases={missingFloor:{...missingFloor,expectedBlocked:!missingFloor.passed,waterProbe,waterHasNoFallbackGround:!!waterProbe&&noFloors.groundHeights(...waterProbe).length===0},highTide:{...highTide,waterLevelHKPD:highWater,expectedBlocked:!highTide.passed}};
 }

 const hash=value=>createHash('sha256').update(value).digest('hex'),dependencyPaths=['3d-viewer/city/data/terrain.json',...context.manifest.terrainPatches.map(p=>'3d-viewer/'+p.url),...context.manifest.bridgeModels.map(p=>'3d-viewer/'+p),...context.manifest.tiles.filter(t=>context.buildings.some(b=>b.tile===t.id)).map(t=>'3d-viewer/'+t.url)];
 const inputs={walkCentrelineSha256:hash(JSON.stringify(line)),files:[...new Set(dependencyPaths)].map(file=>({file,sha256:hash(readFileSync(path.join(root,file)))}))};
 const report={schemaVersion:1,inputs,method:'Actual Navigation.setMode once, then held W and heading changes through Navigation.update, <=1/60s frame steps. Real terrain, mapped-water predicate, BuildingIndex and InfrastructureSurfaces. No inter-sample position resets or collision overrides.',staged:process.argv.includes('--staged'),adjustedLine:!!route.walkCentreline,forward,reverse,negativeCases};
 const passed=forward.passed&&reverse.passed&&negativeCases?.missingFloor.expectedBlocked&&negativeCases?.missingFloor.waterHasNoFallbackGround&&negativeCases?.highTide.expectedBlocked;
 if(passed&&process.argv.includes('--publish')&&!process.argv.includes('--staged')){
  route.continuousWalkVerified=true;route.status='source-and-continuous-navigation-verified';route.walkLengthMetres=line.slice(1).reduce((sum,p,i)=>sum+Math.hypot(p[0]-line[i][0],p[1]-line[i][1]),0);route.runtimeVerification={report:'docs/astra-city/tai-o-completion/route-navigation.json',walkCentrelineSha256:inputs.walkCentrelineSha256,forwardMetres:forward.distanceMetres,reverseMetres:reverse.distanceMetres,collisionRadiusMetres:.55,actorHeightMetres:1.8,maximumStepMetres:.32,positionResetsAlongRoute:0,missingFloorBlocked:true,highWaterBlocked:true};
  for(const file of ['docs/astra-city/tai-o-completion/route.json','3d-viewer/city/data/tai-o-route.json'])writeFileSync(path.join(root,file),JSON.stringify(route,null,2)+'\n');
 }
 const output=process.argv.includes('--staged')?'route-navigation-diagnostic.json':'route-navigation.json';writeFileSync(path.join(root,'docs/astra-city/tai-o-completion',output),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({forward,reverse,negativeCases},null,2));if(!passed)process.exitCode=1;
}
