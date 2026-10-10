// Exact source TIN surfaces share Float32 vertices with the rendered terrain.
// A small spatial index avoids scanning every source triangle during walking.
const cache=new WeakMap();
export function nativeTerrainSurface(mesh) {
 if(cache.has(mesh))return cache.get(mesh);
 if(!Array.isArray(mesh.position)||mesh.position.length%3||!mesh.position.every(Number.isFinite))throw new Error('Invalid native terrain positions');
 const position=new Float32Array(mesh.position),index=mesh.index;
 if(!Array.isArray(index)||index.length%3||!index.every(i=>Number.isInteger(i)&&i>=0&&i<position.length/3))throw new Error('Invalid native terrain indices');
 const cells=new Map(),triangles=[],cell=20;
 for(let t=0;t<index.length;t+=3){
  const a=index[t]*3,b=index[t+1]*3,c=index[t+2]*3;
  const ax=position[a],az=position[a+2],bx=position[b],bz=position[b+2],cx=position[c],cz=position[c+2];
  const determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz);
  if(Math.abs(determinant)<1e-10)continue; // Vertical retaining faces have no area in a height field.
  const row={a,b,c,ax,az,bx,bz,cx,cz,determinant},id=triangles.push(row)-1;
  for(let x=Math.floor(Math.min(ax,bx,cx)/cell);x<=Math.floor(Math.max(ax,bx,cx)/cell);x++)for(let z=Math.floor(Math.min(az,bz,cz)/cell);z<=Math.floor(Math.max(az,bz,cz)/cell);z++){
   const key=x+','+z;let bin=cells.get(key);if(!bin)cells.set(key,bin=[]);bin.push(id);
  }
 }
 function height(x,z){
  let result=-Infinity;
  for(const id of cells.get(Math.floor(x/cell)+','+Math.floor(z/cell))||[]){
   const t=triangles[id],u=((t.bz-t.cz)*(x-t.cx)+(t.cx-t.bx)*(z-t.cz))/t.determinant,v=((t.cz-t.az)*(x-t.cx)+(t.ax-t.cx)*(z-t.cz))/t.determinant,w=1-u-v;
   if(u>=-1e-8&&v>=-1e-8&&w>=-1e-8)result=Math.max(result,u*position[t.a+1]+v*position[t.b+1]+w*position[t.c+1]);
  }
  return Number.isFinite(result)?result:null;
 }
 const value={position,index,height,triangles:triangles.length};cache.set(mesh,value);return value;
}
