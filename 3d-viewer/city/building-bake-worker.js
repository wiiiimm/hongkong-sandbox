import {makeBuildings} from './world.js';
self.onmessage=async({data:features})=>{
 const start=performance.now();
 try{
  const result=await makeBuildings(features,null,{worker:false,yield:false}),transfer=[];
  const meshes=result.group.children.map(mesh=>({material:result.materials.indexOf(mesh.material),attributes:Object.fromEntries(Object.entries(mesh.geometry.attributes).map(([name,a])=>{transfer.push(a.array.buffer);return [name,{array:a.array,itemSize:a.itemSize,normalized:a.normalized}];}))}));
  self.postMessage({meshes,totalVertices:result.totalVertices,workMs:performance.now()-start},transfer);
 }catch(error){self.postMessage({error:error.message});}
};
