import assert from'node:assert/strict';
import{createBuildingGeometry}from'../../../3d-viewer/city/building-geometry.js';
export function surveyedFallbackGeometry(building){
 assert(building&&!building.modelGeometry&&typeof building.buildingCSUID==='string');
 const geometry=createBuildingGeometry(building);
 try{
  const position=Array.from(geometry.attributes.position.array),index=geometry.index?Array.from(geometry.index.array):Array.from({length:position.length/3},(_,i)=>i),triangles=[];
  const low=[Infinity,Infinity,Infinity],high=[-Infinity,-Infinity,-Infinity];
  for(let i=0;i<position.length;i+=3)for(let k=0;k<3;k++){low[k]=Math.min(low[k],position[i+k]);high[k]=Math.max(high[k],position[i+k]);}
  for(let i=0;i<index.length;i+=3){const p=index.slice(i,i+3).map(j=>position.slice(j*3,j*3+3)),det=(p[1][0]-p[0][0])*(p[2][2]-p[0][2])-(p[1][2]-p[0][2])*(p[2][0]-p[0][0]);if(Math.abs(det)>1e-9)triangles.push({ax:p[0][0],az:p[0][2],ay:p[0][1],bx:p[1][0],bz:p[1][2],by:p[1][1],cx:p[2][0],cz:p[2][2],cy:p[2][1],det,minX:Math.min(...p.map(v=>v[0])),maxX:Math.max(...p.map(v=>v[0])),minZ:Math.min(...p.map(v=>v[2])),maxZ:Math.max(...p.map(v=>v[2]))});}
  return{entry:{uid:building.uid,buildingCSUID:building.buildingCSUID,worldBounds:[low,high]},geometryKind:'surveyed-basic',position,index,triangles};
 }finally{geometry.dispose();}
}
