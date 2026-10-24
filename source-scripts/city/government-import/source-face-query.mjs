/** Locate exact original faces at a point without scanning every triangle. */
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {trianglePointIndex} from './triangle-point-index.mjs';

export function createSourceFaceQuery(geometry,{tolerance=.001,metrics=null}={}){
 const index=trianglePointIndex(geometry,{tolerance}),triangle=new THREE.Triangle(),point=new THREE.Vector3(),closest=new THREE.Vector3(),normal=new THREE.Vector3();
 if(metrics)Object.assign(metrics,{sourceFaces:geometry.index.length/3,indexedFaces:index.faces,indexCells:index.cells,largeFaces:index.largeFaces,queries:0,exactTriangleTests:0});
 return position=>{
  const candidates=index.candidates(position),hits=[];point.fromArray(position);
  if(metrics){metrics.queries++;metrics.exactTriangleTests+=candidates.length;}
  for(const faceIndex of candidates){
   [triangle.a,triangle.b,triangle.c].forEach((v,k)=>v.fromArray(geometry.position,geometry.index[faceIndex*3+k]*3));
   triangle.closestPointToPoint(point,closest);const distanceM=closest.distanceTo(point);
   if(distanceM<=tolerance)hits.push({faceIndex,vertices:[triangle.a.toArray(),triangle.b.toArray(),triangle.c.toArray()],distanceM,normal:triangle.getNormal(normal).toArray()});
  }return hits;
 };
}
