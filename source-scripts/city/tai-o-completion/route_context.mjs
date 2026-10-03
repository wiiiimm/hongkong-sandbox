/** Shared bounded route-data loader: reuse the live terrain and BuildingIndex. */
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {BuildingIndex,makeTerrainSampler} from '../../../3d-viewer/city/geo.js';
export const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
export const read=p=>JSON.parse(readFileSync(path.join(root,p)));
export function routeContext(route){

const manifest=read('3d-viewer/city/data/manifest.json');
const terrain=read('3d-viewer/city/data/terrain.json');
terrain.patches=(manifest.terrainPatches||[]).map(p=>read('3d-viewer/'+p.url));
const sampler=makeTerrainSampler(terrain),xs=route.centreline.map(p=>p[0]),zs=route.centreline.map(p=>p[1]);
const box=[Math.min(...xs)-10,Math.min(...zs)-10,Math.max(...xs)+10,Math.max(...zs)+10];
const tiles=manifest.tiles.filter(t=>t.bounds[0]<=box[2]&&t.bounds[2]>=box[0]&&t.bounds[1]<=box[3]&&t.bounds[3]>=box[1]);
const buildings=tiles.flatMap(t=>read('3d-viewer/'+t.url).buildings),index=new BuildingIndex(buildings);
return {manifest,sampler,buildings,index};
}
