/** Complete literal world/F32 bound witness; no geometry or acceptance changes. */
import assert from 'node:assert/strict';
export function completeActorBounds(position,index){
 assert(position&&index&&position.length>0&&position.length%3===0&&index.length>0&&index.length%3===0);
 assert(Array.from(position).every(Number.isFinite));assert(Array.from(index).every(i=>Number.isInteger(i)&&i>=0&&i<position.length/3));
 const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity],flo=[Infinity,Infinity,Infinity],fhi=[-Infinity,-Infinity,-Infinity];
 // Includes every authored loaded vertex, even an unreferenced original vertex.
 for(let i=0;i<position.length;i++){const k=i%3,v=position[i],f=Math.fround(v);assert(Number.isFinite(f));lo[k]=Math.min(lo[k],v);hi[k]=Math.max(hi[k],v);flo[k]=Math.min(flo[k],f);fhi[k]=Math.max(fhi[k],f);}
 return{completeLiteralWorldBounds:[lo,hi],completeFloat32CastWorldBounds:[flo,fhi],completeLiteralAndFloat32Bounds:[lo.map((v,i)=>Math.min(v,flo[i])),hi.map((v,i)=>Math.max(v,fhi[i]))],completeIndexedVertices:position.length/3,completeOriginalTriangles:index.length/3,allOriginalVerticesIncluded:true,clearanceOrSupportAcceptance:false};
}
