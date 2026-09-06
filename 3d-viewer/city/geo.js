// All coordinates are metres in EPSG:2326, translated to a local origin.
export const ORIGIN = [834500, 816500];
export function makeTerrainSampler(data) {
  const { w, h, elev } = data, g = data.meta.georef;
  const grid = (x, z) => [(x + ORIGIN[0] - g.bE) / g.aE, (ORIGIN[1] - z - g.bN) / g.aN];
  const contains = (x, z) => { const [c,r]=grid(x,z);return c>=0&&r>=0&&c<w-1&&r<h-1; };
  function sample(x,z,rendered=false) {
    let [c,r]=grid(x,z); c=Math.max(0,Math.min(w-1.001,c));r=Math.max(0,Math.min(h-1.001,r));
    const i=Math.floor(c),j=Math.floor(r),u=c-i,v=r-j;
    const at=i=>rendered?(elev[i]>0?Math.max(1.2,elev[i]):-4):elev[i];
    const a=at(j*w+i),b=at(j*w+i+1),d=at((j+1)*w+i),e=at((j+1)*w+i+1);
    // Matches mesh triangle diagonal exactly: no feet floating on steep slopes.
    return u+v<=1 ? a+(b-a)*u+(d-a)*v : e+(d-e)*(1-u)+(b-e)*(1-v);
  }
  return {raw:(x,z)=>sample(x,z),contains,grid,height:(x,z)=>Math.max(1.2,sample(x,z,true))};
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
    this.buildings=buildings;this.cell=cell;this.cells=new Map();
    buildings.forEach((b,i)=>{
      const xs=b.rings[0].map(p=>p[0]),zs=b.rings[0].map(p=>p[1]);
      for(let x=Math.floor(Math.min(...xs)/cell);x<=Math.floor(Math.max(...xs)/cell);x++)
        for(let z=Math.floor(Math.min(...zs)/cell);z<=Math.floor(Math.max(...zs)/cell);z++){
          const key=`${x},${z}`;if(!this.cells.has(key))this.cells.set(key,[]);this.cells.get(key).push(i);
        }
    });
  }
  candidates(x,z,r=0){const out=new Set();for(let i=Math.floor((x-r)/this.cell);i<=Math.floor((x+r)/this.cell);i++)for(let j=Math.floor((z-r)/this.cell);j<=Math.floor((z+r)/this.cell);j++)for(const k of this.cells.get(`${i},${j}`)||[])out.add(k);return out;}
  collision(x,z,bottom,top,radius=.5){
    for(const i of this.candidates(x,z,radius)){
      const b=this.buildings[i];if(top<=b.base+b.minimum||bottom>=b.base+b.height)continue;
      if(inPolygon(x,z,b.rings))return b;
      if(radius>0)for(const ring of b.rings)for(let j=1;j<ring.length;j++)if(segmentDistanceSq(x,z,ring[j-1],ring[j])<radius*radius)return b;
    }
    return null;
  }
}
export function random(seed=271828){return()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};}
export function smoothStep(a,b,x){const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);}
