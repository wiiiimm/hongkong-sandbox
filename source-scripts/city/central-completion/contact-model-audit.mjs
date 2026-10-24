/** Inspect the seven contacts against available exact original model surfaces. */
import {readFile,writeFile} from 'node:fs/promises';
import {routeContext} from '../tai-o-completion/route_context.mjs';
import {makeTerrainSampler,BuildingIndex} from '../../../3d-viewer/city/geo.js';
import {collisionVolumes} from '../../../3d-viewer/city/building-geometry.js';
import {modelSurfaceCollision} from '../../../3d-viewer/city/model-collision.js';
import {loadContactModels} from './contact_models.mjs';
const here=new URL('./',import.meta.url),doc=new URL('../../../docs/astra-city/central-completion/',here),read=async u=>JSON.parse(await readFile(u));
const preflight=await read(new URL('route-preflight.json',doc)),contacts=preflight.routes.flatMap(r=>r.stagedBlockerBuildings),uids=new Set(contacts.map(c=>c.uid));
const original=(await read(new URL('route-candidates.json',doc))).routes,alternatives=(await read(new URL('route-alternatives.json',doc))).routes;
const {index,buildings}=routeContext({centreline:[[-1150,-450],[1250,1350]]}),byUid=new Map(buildings.map(b=>[b.uid,b]));
const coarse=await read(new URL('../../../3d-viewer/city/data/terrain.json',here)),fine=makeTerrainSampler({...coarse,patches:[await read(new URL('terrain-central.json',here))]});
const {models,meshStats}=await loadContactModels();
const details=contacts.map(c=>{
 const b=byUid.get(c.uid),[x,,z]=c.sample,y=fine.height(x,z),touching=collisionVolumes(b).filter(volume=>{
  const only=new BuildingIndex([{uid:b.uid,rings:volume.rings,base:volume.bottom,height:volume.top-volume.bottom,kind:'yes'}]);return Boolean(only.collision(x,z,y+.09,y+1.8,.55));
 });
 return{uid:c.uid,name:b.name,structureType:b.structureType,sourceBaseHeight:b.baseHeightHKPD,sourceTopHeight:b.topHeightHKPD,firstSample:[x,y,z],touchingVolumeKinds:touching.map(v=>({kind:v.kind,illustrative:Boolean(v.illustrative)})),availableSourceModel:models.has(c.uid),actualSourceSurfaceContact:models.has(c.uid)?modelSurfaceCollision(models.get(c.uid),x,z,y+.09,y+1.8,.55):null};
});
const results=[];
for(const [label,routes]of [['original',original],['alternative',alternatives]])for(const route of routes){
 let samples=0,footprintContacts=0;const sourceHits=new Map();
 for(let i=0;i<route.sourceCentrelineXYZ.length-1;i++){
  const a=route.sourceCentrelineXYZ[i],b=route.sourceCentrelineXYZ[i+1],n=Math.max(1,Math.ceil(Math.hypot(...a.map((v,k)=>v-b[k]))/.25));
  for(let j=0;j<=n;j++){
   const p=a.map((v,k)=>v+(b[k]-v)*j/n),[x,,z]=p,y=fine.height(x,z);samples++;
   if(index.collision(x,z,y+.09,y+1.8,.55))footprintContacts++;
   for(const [uid,model]of models){const [lo,hi]=model.bounds;if(x+.55<lo[0]||x-.55>hi[0]||z+.55<lo[2]||z-.55>hi[2])continue;if(modelSurfaceCollision(model,x,z,y+.09,y+1.8,.55)){const value=sourceHits.get(uid)||{uid,samples:0,firstSample:[x,y,z]};value.samples++;sourceHits.set(uid,value)}}
  }
 }
 results.push({version:label,route:route.id,samples,existingBuildingContactSamples:footprintContacts,availableContactModelSurfaceHits:[...sourceHits.values()]});
}
const report={status:'source-contact-diagnostic-not-runtime-acceptance',models:meshStats,contacts:details,routes:results,policy:'Five exact source models are decoded with the real GLTFLoader and original node matrices, translated once into city coordinates. Original indexed triangles are tested with the existing modelSurfaceCollision helper at the unchanged 0.55 m gameplay radius and 1.8 m actor height. Shared building collision is not modified.',limits:['Surface-only source tests explain possible footprint infill errors; they do not establish a closed-volume replacement or public floor.','The two open-sided canopy records have no exact model match; their illustrative supports are not surveyed column positions.','Only the five contact models are included here; full landmark loading and continuous navigation need later integration checks.']};
await writeFile(new URL('contact-model-audit.json',doc),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
