/** Data-only validator using the exact collision and terrain modules used by the city. */
import {readFileSync} from 'node:fs';
import {createInterface} from 'node:readline';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {PLACES} from '../../3d-viewer/city/places.js';
import {BuildingIndex,makeTerrainSampler} from '../../3d-viewer/city/geo.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const read=p=>JSON.parse(readFileSync(path.join(root,p)));
const rawManifest=readFileSync(path.join(root,'3d-viewer/city/data/manifest.json')),manifest=JSON.parse(rawManifest);
const terrain=read('3d-viewer/city/data/terrain.json');terrain.patches=(manifest.terrainPatches||[]).map(p=>read('3d-viewer/'+p.url));
const sampler=makeTerrainSampler(terrain),patches=terrain.patches.map(data=>({data,sampler:makeTerrainSampler(data)}));
let index=null;
function sample(x,z){
 const patch=patches.find(p=>p.sampler.contains(x,z)),data=patch?.data||terrain,s=patch?.sampler||sampler;
 if(!s.contains(x,z))return {ground:null,raw:null,dry:false,resolution:Math.abs(data.meta.georef.aE)};
 const [c,r]=s.grid(x,z),i=Math.floor(c),j=Math.floor(r),u=c-i,v=r-j,w=data.w;
 const cells=u+v<=1?[j*w+i,j*w+i+1,(j+1)*w+i]:[j*w+i+1,(j+1)*w+i,(j+1)*w+i+1];
 return {ground:sampler.height(x,z),raw:sampler.raw(x,z),dry:cells.every(k=>data.elev[k]>0),resolution:Math.abs(data.meta.georef.aE)};
}
function setup(){
 if(index)return;
 const anchors=Object.values(PLACES).filter(p=>!p.aerialOnly).map(p=>p.spawn),buildings=[];
 // All geometry that could intersect the bounded 1 km search and 2 m walk checks.
 for(const tile of manifest.tiles){
  const [x0,z0,x1,z1]=tile.bounds;
  if(!anchors.some(([x,z])=>Math.hypot(Math.max(0,x0-x,x-x1),Math.max(0,z0-z,z-z1))<=1010))continue;
  buildings.push(...read('3d-viewer/'+tile.url).buildings);
 }
 index=new BuildingIndex(buildings);
}
function audit([x,z]){
 const s=sample(x,z);if(s.raw===null||s.raw<=.8||!s.dry)return {...s,valid:false,reason:'outside-dry-terrain'};
 const hit=index.collision(x,z,s.ground,s.ground+1.8,1.2)||index.collision(x,z,s.raw,s.raw+1.8,1.2);
 if(hit)return {...s,valid:false,reason:'building-clearance',collisionUid:hit.uid};
 for(const [dx,dz] of [[2,0],[-2,0],[0,2],[0,-2]]){
  const n=sample(x+dx,z+dz);if(!n.dry||n.raw===null||Math.abs(n.raw-s.raw)>=1.5||Math.abs(n.ground-s.ground)>=1.5)return {...s,valid:false,reason:'steep-or-wet-terrain-edge'};
 }
 return {...s,valid:true};
}
for await(const line of createInterface({input:process.stdin,crlfDelay:Infinity})){
 try{const request=JSON.parse(line);let result;
  if(request.op==='places')result={places:PLACES,manifestSha256:createHash('sha256').update(rawManifest).digest('hex'),counts:manifest.counts,terrainPatches:manifest.terrainPatches||[]};
  else if(request.op==='sample')result=request.points.map(([x,z])=>sample(x,z));
  else if(request.op==='audit'){setup();result=request.points.map(audit);}
  else throw new Error('Unsupported request');
  process.stdout.write(JSON.stringify({result})+'\n');
 }catch(error){process.stdout.write(JSON.stringify({error:error.stack||String(error)})+'\n');}
}
