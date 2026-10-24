/** Conservative broad phase for exact source triangle tests; never acceptance. */
export function trianglePointIndex({position,index},{cell=8,tolerance=.001,maxCells=4096,acceptFace=()=>true}={}){
 if(!(Number.isFinite(cell)&&cell>0&&Number.isFinite(tolerance)&&tolerance>=0&&Number.isInteger(maxCells)&&maxCells>0))throw new Error('Invalid triangle index parameters');
 const grid=new Map(),large=[],bounds=new Map();
 for(let i=0;i<index.length;i+=3){
  const vertices=[0,1,2].map(k=>Array.from(position.slice(index[i+k]*3,index[i+k]*3+3))),faceIndex=i/3;
  if(!acceptFace(vertices,faceIndex))continue;
  const low=[0,1,2].map(k=>Math.min(...vertices.map(v=>v[k]))-tolerance),high=[0,1,2].map(k=>Math.max(...vertices.map(v=>v[k]))+tolerance);
  if(![...low,...high].every(Number.isFinite))throw new Error('Nonfinite source triangle');
  bounds.set(faceIndex,{low,high});
  const x0=Math.floor(low[0]/cell),x1=Math.floor(high[0]/cell),z0=Math.floor(low[2]/cell),z1=Math.floor(high[2]/cell);
  if((x1-x0+1)*(z1-z0+1)>maxCells){large.push(faceIndex);continue;}
  for(let x=x0;x<=x1;x++)for(let z=z0;z<=z1;z++){
   const key=x+','+z;if(!grid.has(key))grid.set(key,[]);grid.get(key).push(faceIndex);
  }
 }
 return {faces:bounds.size,cells:grid.size,largeFaces:large.length,candidates(point){
  if(point.length!==3||!point.every(Number.isFinite))throw new Error('Invalid query point');
  const candidates=[...(grid.get(Math.floor(point[0]/cell)+','+Math.floor(point[2]/cell))||[]),...large];
  return candidates.filter(face=>{const {low,high}=bounds.get(face);return point.every((v,k)=>v>=low[k]&&v<=high[k]);}).sort((a,b)=>a-b);
 }};
}
