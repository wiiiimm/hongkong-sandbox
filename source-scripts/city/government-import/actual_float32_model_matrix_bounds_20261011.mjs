/** Declared Float32 model-matrix arithmetic on every loaded attribute vertex.
 * No universal GPU/FMA/camera guarantee and no clearance or support approval. */
import assert from 'node:assert/strict';
export function actualFloat32ModelMatrixPositions(position,matrix){
 assert(position instanceof Float32Array&&position.length>0&&position.length%3===0);
 assert(matrix.length===16&&Array.from(matrix).every(Number.isFinite));
 assert(matrix[3]===0&&matrix[7]===0&&matrix[11]===0&&matrix[15]===1,'Non-affine matrix');
 const m=Array.from(matrix,Math.fround);assert(m.every(Number.isFinite));const left=[],balanced=[];
 for(let i=0;i<position.length;i+=3){const p=Array.from(position.slice(i,i+3));assert(p.every(Number.isFinite));
  for(let j=0;j<3;j++){const a=Math.fround(m[j]*p[0]),b=Math.fround(m[4+j]*p[1]),c=Math.fround(m[8+j]*p[2]),d=m[12+j];
   left.push(Math.fround(Math.fround(Math.fround(a+b)+c)+d));
   balanced.push(Math.fround(Math.fround(a+b)+Math.fround(c+d)));
  }
 }
 assert([...left,...balanced].every(Number.isFinite));
 return {modelMatrixUniformFloat32:m,leftAssociatedPerMultiplyAddFloat32WorldPosition:left,balancedPerMultiplyAddFloat32WorldPosition:balanced};
}
export function positionBounds(position){assert(position.length>0&&position.length%3===0&&position.every(Number.isFinite));const lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];for(let i=0;i<position.length;i++){const j=i%3;lo[j]=Math.min(lo[j],position[i]);hi[j]=Math.max(hi[j],position[i]);}return[lo,hi];}
