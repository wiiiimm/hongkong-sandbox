/** Stage a conservative obstacle screen for source-path alternatives; no runtime edits. */
import {readFile,writeFile} from 'node:fs/promises';
import {gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {routeContext} from '../tai-o-completion/route_context.mjs';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
import {collisionVolumes} from '../../../3d-viewer/city/building-geometry.js';
import {loadContactModels,nearModel} from './contact_models.mjs';
import {modelSurfaceCollision} from '../../../3d-viewer/city/model-collision.js';
const {models,meshStats}=await loadContactModels();
const here=new URL('./',import.meta.url),doc=new URL('../../../docs/astra-city/central-completion/',here);
const config=JSON.parse(await readFile(new URL('config.json',here))),[e0,n0,e1,n1]=config.sourceBoundsHK1980;
const box=[e0-834500,816500-n1,e1-834500,816500-n0];
const sourceBytes=await readFile(new URL('pedestrian-network.json.gz',here)),network=JSON.parse(gunzipSync(sourceBytes));
const {sampler:current,index}=routeContext({centreline:[[box[0],box[1]],[box[2],box[3]]]});
const coarse=JSON.parse(await readFile(new URL('../../../3d-viewer/city/data/terrain.json',here))),patch=JSON.parse(await readFile(new URL('terrain-central.json',here)));
const fine=makeTerrainSampler({...coarse,patches:[patch]}),blocked={},clear=[],outside=[];let samples=0;
const recordedContacts=new Set(JSON.parse(await readFile(new URL('route-preflight.json',doc))).routes.flatMap(r=>r.stagedBlockerBuildings.map(b=>b.uid))),contacts={};
const contactFeatures=network.features.filter(f=>f.attributes.Location===1&&f.attributes.Enabled===1&&![5,8,9,10].includes(f.attributes.FeatureType));
for(const feature of contactFeatures){
 const a=feature.attributes;
 for(const [part,line]of feature.geometry.paths.entries()){
  const id=`${a.PedestrianRouteID}:${part}`;
  if(line.some(p=>p[0]<e0||p[0]>e1||p[1]<n0||p[1]>n1)){outside.push(id);continue}
  const findings=new Map();
  for(let i=0;i<line.length-1;i++){
   const start=line[i],end=line[i+1],length=Math.hypot(...start.map((v,k)=>v-end[k])),steps=Math.max(1,Math.ceil(length/.25));
   for(let j=0;j<=steps;j++){
    const p=start.map((v,k)=>v+(end[k]-v)*j/steps),x=p[0]-834500,z=816500-p[1];samples++;
    for(const [version,sampler]of [['current',current],['staged',fine]]){
     const y=sampler.height(x,z),hit=index.collision(x,z,y+.09,y+1.8,.58);
     for(const [uid,model]of models)if(nearModel(model,x,z,.58)&&modelSurfaceCollision(model,x,z,y+.09,y+1.8,.58)){const key=`${version}:source-model:${uid}`;if(!findings.has(key))findings.set(key,{version,uid,sourceModelSurface:true,worldXYZ:[x,y,z],sourceNetworkY:p[2]})}
     if(hit){
      const key=`${version}:${hit.uid}`;
      if(!findings.has(key))findings.set(key,{version,uid:hit.uid,name:hit.name,structureType:hit.structureType,worldXYZ:[x,y,z],sourceNetworkY:p[2]});
      if(recordedContacts.has(hit.uid)){
       contacts[hit.uid]??={uid:hit.uid,name:hit.name,structureType:hit.structureType,baseHeightHKPD:hit.baseHeightHKPD,topHeightHKPD:hit.topHeightHKPD,sourceSegments:{},volumeKinds:collisionVolumes(hit).map(v=>v.kind)};
       contacts[hit.uid].sourceSegments[id]??={id,pedestrianRouteId:a.PedestrianRouteID,alias:a.AliasNameEN,street:a.StreetNameEN,kind:a.FeatureType,sourceLevel:a.LevelSource,firstContact:[x,y,z]};
      }
     }
    }
   }
  }
  if(findings.size)blocked[id]=[...findings.values()];else clear.push(id);
 }
}
const report={schemaVersion:1,sourceSha256:createHash('sha256').update(sourceBytes).digest('hex'),terrain:'Current live ground and staged Central 5 m patch',sourceModels:meshStats,actorScreen:{radiusMetres:.58,gameplayRadiusMetres:.55,extraClearanceMetres:.03,heightMetres:1.8,bottomEpsilonMetres:.09,maximumSampleSpacingMetres:.25},policy:'An original path segment is screened out if any sample contacts the existing building volumes or any of the five exact contact-model surfaces on either terrain version. This adds a 3 cm planning margin to the unchanged gameplay actor. No route vertices, buildings or runtime collisions are changed. Segments extending outside the source review envelope are excluded whole, never clipped.',samples,clearIds:clear,blocked,outsideIds:outside,contacts:Object.values(contacts).map(c=>({...c,sourceSegments:Object.values(c.sourceSegments)})),limits:['Point sampling is a route-planning screen, not continuous Navigation acceptance.','Bridge/stair/source-floor validation remains separate.','Contacts with estimated open-sided supports do not establish surveyed real-world column locations.']};
await writeFile(new URL('contact-edge-audit.json',doc),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({samples,clear:clear.length,blocked:Object.keys(blocked).length,outside:outside.length,contacts:report.contacts.map(c=>({uid:c.uid,kind:c.structureType,volumes:c.volumeKinds,segments:c.sourceSegments.length}))},null,2));
