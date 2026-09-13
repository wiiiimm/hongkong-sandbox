import {readFile,writeFile} from 'node:fs/promises';
import {performance} from 'node:perf_hooks';
import {makeRoads} from '../../../3d-viewer/city/world.js';
import {makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
const read=async p=>JSON.parse(await readFile(p,'utf8'));
const manifest=await read('3d-viewer/city/data/manifest.json'),terrain=await read('3d-viewer/city/data/terrain.json');
terrain.patches=await Promise.all(manifest.terrainPatches.map(p=>read('3d-viewer/'+p.url)));
for(const p of (await read('docs/astra-city/roof-occlusion-review/patch-review.json')).rows)terrain.patches.push(await read(p.candidate));
const sampler=makeTerrainSampler(terrain),results=[];
for(const id of ['0_0','1_0','0_-3']){
 const tile=await read('3d-viewer/'+manifest.tiles.find(t=>t.id===id).url),start=performance.now(),g=makeRoads(tile.roads,sampler);
 let minimumFineRoadClearance=Infinity,fineRoadTriangles=0;g.traverse(o=>{if(!o.isMesh)return;const a=o.geometry.attributes.position;for(let i=0;i<a.count;i+=3){const x=(a.getX(i)+a.getX(i+1)+a.getX(i+2))/3,z=(a.getZ(i)+a.getZ(i+1)+a.getZ(i+2))/3;if(sampler.resolutionAt(x,z)>1.01)continue;const y=(a.getY(i)+a.getY(i+1)+a.getY(i+2))/3;minimumFineRoadClearance=Math.min(minimumFineRoadClearance,y-sampler.height(x,z));fineRoadTriangles++;}});
 let vertices=0;g.traverse(o=>{if(o.isMesh)vertices+=o.geometry.attributes.position.count});
 let baselineVertices=0;for(const road of tile.roads)for(let i=1;i<road.path.length;i++){const a=road.path[i-1],b=road.path[i],length=Math.hypot(b[0]-a[0],b[1]-a[1]);if(length>=.1)baselineVertices+=Math.ceil(length/15)*6;}
 results.push({tile:id,roads:tile.roads.length,vertices,baselineVertices,cpuMs:performance.now()-start,positionAndUvBytes:vertices*20,fineRoadTriangles,minimumFineRoadClearance:Number.isFinite(minimumFineRoadClearance)?minimumFineRoadClearance:null});
 g.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose()}});
}
await writeFile('docs/astra-city/model-integration-20260909/roads-check.json',JSON.stringify({results,scope:'Three city tiles, final sampler including staged roof patches; one CPU run, not device frame-rate proof'},null,2)+'\n');console.log(results);
