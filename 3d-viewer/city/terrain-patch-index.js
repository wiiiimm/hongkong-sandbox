/** Broad-phase lookup only: the sampler still applies its exact contains test. */
export function terrainGridBounds(data,origin){
 const g=data.meta.georef,x=[g.bE-origin[0],g.bE-origin[0]+(data.w-1)*g.aE],z=[origin[1]-g.bN,origin[1]-g.bN-(data.h-1)*g.aN];
 if(!g.aE||!g.aN||![...x,...z].every(Number.isFinite))return null;
 // Subtraction against the projected origin can round differently from the
 // sampler's inverse transform. Include a conservative numerical halo, then
 // defer boundary membership to the original contains calculation.
 const halo=Math.max(1e-8,32*Number.EPSILON*Math.max(...origin.map(Math.abs),Math.abs(g.bE),Math.abs(g.bN),...x.map(Math.abs),...z.map(Math.abs)));
 return [Math.min(...x)-halo,Math.min(...z)-halo,Math.max(...x)+halo,Math.max(...z)+halo];
}

const contains=(b,x,z)=>x>=b[0]&&z>=b[1]&&x<=b[2]&&z<=b[3];
/** Immutable rectangle BVH; returned values preserve original source order. */
export class TerrainPatchIndex{
 constructor(entries){
  this.fallback=[];
  const rows=entries.map((entry,order)=>({...entry,order})).filter(row=>{
   if(!row.bounds||row.bounds.length!==4||!row.bounds.every(Number.isFinite)){this.fallback.push(row);return false;}return true;
  });
  const build=rows=>{
   if(!rows.length)return null;
   const bounds=[Infinity,Infinity,-Infinity,-Infinity];
   for(const row of rows){bounds[0]=Math.min(bounds[0],row.bounds[0]);bounds[1]=Math.min(bounds[1],row.bounds[1]);bounds[2]=Math.max(bounds[2],row.bounds[2]);bounds[3]=Math.max(bounds[3],row.bounds[3]);}
   if(rows.length<=8)return {bounds,rows};
   const axis=bounds[2]-bounds[0]>=bounds[3]-bounds[1]?0:1;
   rows.sort((a,b)=>(a.bounds[axis]+a.bounds[axis+2])-(b.bounds[axis]+b.bounds[axis+2]));const middle=rows.length>>1;
   return {bounds,left:build(rows.slice(0,middle)),right:build(rows.slice(middle))};
  };
  this.root=build(rows);
 }
 query(x,z){
  const found=[...this.fallback],stack=this.root?[this.root]:[];
  while(stack.length){const node=stack.pop();if(!contains(node.bounds,x,z))continue;
   if(node.rows){for(const row of node.rows)if(contains(row.bounds,x,z))found.push(row);}else stack.push(node.left,node.right);
  }
  if(found.length>1)found.sort((a,b)=>a.order-b.order);
  return found.map(row=>row.value);
 }
}
