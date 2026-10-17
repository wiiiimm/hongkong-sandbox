/** Exact original mesh seams and zero-area deck-corner occlusion corrections.
 * Numeric clearance limits and raw ray evidence are preserved. No geometry edits.
 */
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {verifySupportInterface} from './support-interface.mjs';
import {supportSurface} from './support-contact.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const tolerance=.001;
function normal(vertices){const [a,b,c]=vertices.map(v=>new THREE.Vector3(...v));return new THREE.Vector3().crossVectors(b.clone().sub(a),c.clone().sub(a)).normalize();}
function vertical(face){const n=normal(face.vertices);return n.lengthSq()>=.99&&Math.abs(n.y)<=1e-6;}
function pointOnTriangle(position,vertices){const [a,b,c]=vertices.map(v=>new THREE.Vector3(...v)),p=new THREE.Vector3(...position),closest=new THREE.Vector3();new THREE.Triangle(a,b,c).closestPointToPoint(p,closest);return closest.distanceTo(p)<=tolerance;}
function upperEdgeContact(position,face){
 if(!vertical(face))return null;
 const top=Math.max(...face.vertices.map(v=>v[1])),vertices=face.vertices.filter(v=>v[1]===top);
 if(vertices.length!==2||Math.abs(position[1]-top)>tolerance)return null;
 const p=new THREE.Vector3(...position),edge=new THREE.Line3(new THREE.Vector3(...vertices[0]),new THREE.Vector3(...vertices[1])),closest=new THREE.Vector3();edge.closestPointToPoint(p,true,closest);
 if(closest.distanceTo(p)>tolerance)return null;
 return {faceIndex:face.faceIndex,vertices:face.vertices,upperEdge:vertices,contact:closest.toArray(),distanceM:closest.distanceTo(p)};
}
export function verifyOriginalContactSeams(geometry,bottom,support){
 const raw=verifySupportInterface(geometry,bottom,support),sourceQuery=createSourceFaceQuery(geometry),supportQuery=createSourceFaceQuery(support),surface=supportSurface(support),resolved=[],unresolved=[];
 for(const failure of raw.unresolved){
  const p=failure.position,faces=sourceQuery(p),walls=faces.filter(f=>vertical(f)&&Math.max(...f.vertices.map(v=>v[1]))>p[1]+tolerance);
  if(!walls.length){unresolved.push(failure);continue;}
  if(failure.reason==='rim-above-support'||failure.reason==='no-vertical-support'){
   const edges=supportQuery(p).map(f=>upperEdgeContact(p,f)).filter(Boolean);
   if(edges.length){resolved.push({...failure,kind:'original-wall-upper-edge-seam',sourceWallFaces:walls,supportUpperEdges:edges});continue;}
  }
  if(failure.reason==='support-above-rim'){
   const hits=surface.intersectionDetails(p[0],p[2]),strict=hits.filter(h=>p[1]-h.height>=-.1&&p[1]-h.height<=1&&h.barycentric.every(w=>w>0));
   const higher=hits.filter(h=>p[1]-h.height<-.1);
   // A higher roof touching this ray only at a vertex has zero projected
   // covering area here. Require a separate actual interior contact layer,
   // exclusively vertical source faces at the sample, and same-face original
   // wall contact at EVERY higher vertex. A buried floor/sloped surface rejects.
   const corners=higher.length>0&&higher.every(h=>h.barycentric.filter(w=>w===0).length===2&&walls.some(f=>pointOnTriangle([p[0],h.height,p[2]],f.vertices)));
   if(strict.length&&faces.length&&faces.every(vertical)&&corners){resolved.push({...failure,kind:'zero-area-higher-deck-corners',strictInteriorSupportFaces:strict,higherCornerFaces:higher,sourceWallFaces:walls});continue;}
  }
  unresolved.push(failure);
 }
 return {policy:'exact-original-contact-seams-v1',passed:Boolean(raw.samples&&raw.strictContacts&&unresolved.length===0),samples:raw.samples,strictContacts:raw.strictContacts,wallIntersections:raw.wallIntersections,seamCorrections:resolved.length,resolved,unresolved,rawInterface:raw,maximumEmbeddingM:raw.maximumEmbeddingM,exactSeamToleranceM:tolerance,installationApproved:false,qualification:'Original support wall upper-edge seams and higher zero-area deck corners only. All original triangles, poses and raw failures retained; strict contact interval and 0.5m wall embedding limit unchanged. Full identity, source terrain/foundation, neighbours, runtime/browser and publication remain separate.'};
}
