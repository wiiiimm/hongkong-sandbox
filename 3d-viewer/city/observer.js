import {OBSERVER_GRID as grid} from './observer-grid.js';

export const OBSERVER_BOUNDS=Object.freeze([...grid.bounds]);

// EPSG:2326 terrain coordinates -> WGS 84 using a validated inverse-PROJ grid.
// Returns null outside the measured terrain rectangle or for non-finite inputs.
// This locates the simulated observer; it does not read device GPS.
export function worldToWgs84(x,z){
 const [x0,z0,x1,z1]=grid.bounds;
 if(!Number.isFinite(x)||!Number.isFinite(z)||x<x0||x>x1||z<z0||z>z1)return null;
 const gx=(x-x0)/grid.step[0],gz=(z-z0)/grid.step[1];
 const col=Math.min(grid.width-2,Math.floor(gx)),row=Math.min(grid.height-2,Math.floor(gz));
 const u=gx-col,v=gz-row,index=row*grid.width+col;
 const a=grid.nodes[index],b=grid.nodes[index+1],c=grid.nodes[index+grid.width],d=grid.nodes[index+grid.width+1];
 const blend=k=>(a[k]*(1-u)+b[k]*u)*(1-v)+(c[k]*(1-u)+d[k]*u)*v;
 return {lat:blend(0),lon:blend(1)};
}
