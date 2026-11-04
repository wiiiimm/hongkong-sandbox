/** Staging adapter around the existing city sampler, source mesh and route helpers. */
import {readFileSync,existsSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {root,read,routeContext} from '../tai-o-completion/route_context.mjs';
import {makeTerrainSampler,BuildingIndex} from '../../../3d-viewer/city/geo.js';
import {prepareInfrastructure,InfrastructureSurfaces} from '../../../3d-viewer/city/infrastructure-data.js';
import {walkingSurfaceFor} from '../../../3d-viewer/city/bridges.js';
export {root,read};
const manifest=read('3d-viewer/city/data/manifest.json'),terrain=read('3d-viewer/city/data/terrain.json');
terrain.patches=manifest.terrainPatches.map(p=>p.url.endsWith('terrain-mui-wo.json')?read('source-scripts/city/mui-wo-completion/staged-terrain-mui-wo.json'):read('3d-viewer/'+p.url));
terrain.hydro=read('source-scripts/city/mui-wo-completion/hydro-mui-wo.json');
export const sampler=makeTerrainSampler(terrain);
const source=JSON.parse(gunzipSync(readFileSync(root+'/source-scripts/city/mui-wo-completion/infrastructure-models.json.gz')));
// The fixture bridges only the legacy metadata discriminator until root accepts
// the generic regional kind. Geometry and all validation are the normal runtime.
export const models=prepareInfrastructure({...source,kind:'tai-o-official-infrastructure'});
export function stagedSurfaces(withApproaches=true){
 const surfaces=new InfrastructureSurfaces();for(const m of models)surfaces.add(m);
 const file='source-scripts/city/mui-wo-completion/approaches.json';
 if(withApproaches&&existsSync(root+'/'+file))for(const r of read(file).records)surfaces.add(walkingSurfaceFor(r));
 return surfaces;
}
const estimates=new Map(read('docs/astra-city/mui-wo-completion/terrain-audit.json').rows.filter(r=>r.missingBaseReestimated).map(r=>[r.uid,r]));
export function stagedContext(route){
 const ctx=routeContext(route),buildings=ctx.buildings.map(b=>estimates.has(b.uid)?{...b,base:estimates.get(b.uid).proposedBase}:b);
 return {...ctx,sampler,buildings,index:new BuildingIndex(buildings),surfaces:stagedSurfaces()};
}
