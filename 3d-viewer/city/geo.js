import {collisionVolumes} from './building-geometry.js';
import {modelSurfaceCollision} from './model-collision.js';

// All coordinates are metres in EPSG:2326, translated to a local origin.
export const ORIGIN = [834500, 816500];
// Optional transition vertices join the already rendered coarse mesh; raw source heights stay intact.
export function terrainVertexHeight(data,index) {
  const height=data.renderedElev?.[index];
  return Number.isFinite(height)?height:(data.elev[index]>0?Math.max(1.2,data.elev[index]):-4);
}
export function makeTerrainSampler(data) {
  const { w, h, elev } = data, g = data.meta.georef;
  const patches=(data.patches||[]).map(makeTerrainSampler);
  const patchAt=(x,z)=>patches.find(p=>p.contains(x,z));
  const hydro=data.hydro,regions=hydro?.region==='composite'?hydro.regions.map(region=>{
    const [start,length]=region.geometryRanges.water;return {...region,water:hydro.water.slice(start,start+length)};
  }):hydro?[hydro]:[];
  const waterAt=(x,z)=>regions.find(({bounds,water})=>x>=bounds[0]&&x<=bounds[2]&&z>=bounds[1]&&z<=bounds[3]&&water.some(p=>inPolygon(x,z,p.rings)));
  const mappedWater=(x,z)=>Boolean(waterAt(x,z));
  const grid = (x, z) => [(x + ORIGIN[0] - g.bE) / g.aE, (ORIGIN[1] - z - g.bN) / g.aN];
  const contains = (x, z) => { const [c,r]=grid(x,z);return c>=0&&r>=0&&c<w-1&&r<h-1; };
  function sample(x,z,rendered=false) {
    let [c,r]=grid(x,z); c=Math.max(0,Math.min(w-1,c));r=Math.max(0,Math.min(h-1,r));
    const i=Math.min(w-2,Math.floor(c)),j=Math.min(h-2,Math.floor(r)),u=c-i,v=r-j;
    const at=i=>rendered?terrainVertexHeight(data,i):elev[i];
    const a=at(j*w+i),b=at(j*w+i+1),d=at((j+1)*w+i),e=at((j+1)*w+i+1);
    // Matches mesh triangle diagonal exactly: no feet floating on steep slopes.
    return u+v<=1 ? a+(b-a)*u+(d-a)*v : e+(d-e)*(1-u)+(b-e)*(1-v);
  }
  return {raw:(x,z)=>patchAt(x,z)?.raw(x,z)??sample(x,z),contains,grid,mappedWater,height:(x,z)=>waterAt(x,z)?.illustrativeBed??(patchAt(x,z)?.height(x,z)??Math.max(1.2,sample(x,z,true))),resolutionAt:(x,z)=>patchAt(x,z)?.resolutionAt(x,z)??Math.abs(g.aE)};
}
export function inRing(x,z,ring) {
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const [a,b]=ring[i],[c,d]=ring[j];
    if((b>z)!==(d>z)&&x<(c-a)*(z-b)/(d-b)+a)inside=!inside;
  }
  return inside;
}
export function inPolygon(x,z,rings){return inRing(x,z,rings[0])&&!rings.slice(1).some(r=>inRing(x,z,r));}
export function segmentDistanceSq(x,z,a,b){
  const dx=b[0]-a[0],dz=b[1]-a[1],l=dx*dx+dz*dz;
  const t=l?Math.max(0,Math.min(1,((x-a[0])*dx+(z-a[1])*dz)/l)):0;
  return (x-a[0]-t*dx)**2+(z-a[1]-t*dz)**2;
}
export class BuildingIndex {
  constructor(buildings,cell=100){
    this.buildings=buildings;this.volumes=buildings.map(collisionVolumes);this.cell=cell;this.cells=new Map();
    buildings.forEach((b,i)=>{
      const volumes=this.volumes[i],xs=volumes.flatMap(p=>[p.bounds[0],p.bounds[2]]),zs=volumes.flatMap(p=>[p.bounds[1],p.bounds[3]]);
      for(let x=Math.floor(Math.min(...xs)/cell);x<=Math.floor(Math.max(...xs)/cell);x++)
        for(let z=Math.floor(Math.min(...zs)/cell);z<=Math.floor(Math.max(...zs)/cell);z++){
          const key=`${x},${z}`;if(!this.cells.has(key))this.cells.set(key,[]);this.cells.get(key).push(i);
        }
    });
  }
  candidates(x,z,r=0){const out=new Set();for(let i=Math.floor((x-r)/this.cell);i<=Math.floor((x+r)/this.cell);i++)for(let j=Math.floor((z-r)/this.cell);j<=Math.floor((z+r)/this.cell);j++)for(const k of this.cells.get(`${i},${j}`)||[])out.add(k);return out;}
  maximumRoof(x,z,radius=20){let h=0;for(const i of this.candidates(x,z,radius)){const b=this.buildings[i],outline=b.base+b.height;if(Number.isFinite(outline))h=Math.max(h,outline);for(const volume of this.volumes[i])if(Number.isFinite(volume.top))h=Math.max(h,volume.top);}return h;}
  collision(x,z,bottom,top,radius=.5){
    for(const i of this.candidates(x,z,radius)){
      const b=this.buildings[i];
      for(const volume of this.volumes[i]){
        if(top<=volume.bottom||bottom>=volume.top)continue;
        const [x0,z0,x1,z1]=volume.bounds;if(x+radius<x0||x-radius>x1||z+radius<z0||z-radius>z1)continue;
        if(volume.kind==='model-surface'){if(modelSurfaceCollision(volume.model,x,z,bottom,top,radius))return b;continue;}
        if(inPolygon(x,z,volume.rings))return b;
        if(radius>0)for(const ring of volume.rings)for(let j=1;j<ring.length;j++)if(segmentDistanceSq(x,z,ring[j-1],ring[j])<radius*radius)return b;
      }
    }
    return null;
  }
}
export function random(seed=271828){return()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};}
export function smoothStep(a,b,x){const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);}
