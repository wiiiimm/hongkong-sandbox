/** Diagnostic of exact zero-area shared original wall/roof boundary edges.
 * A real lower interior support facet, complete original rising source wall,
 * and both original higher-edge endpoints on that SAME wall face are required.
 * This does not accept higher roof interiors or grant installation approval.
 */
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {verifyOriginalContactSeams} from './original-contact-seams.mjs';
import {supportSurface} from './support-contact.mjs';
import {createSourceFaceQuery} from './source-face-query.mjs';
const tolerance=.001;
function vertical(face){const [a,b,c]=face.vertices.map(v=>new THREE.Vector3(...v)),n=new THREE.Vector3().crossVectors(b.clone().sub(a),c.clone().sub(a)).normalize();return n.lengthSq()>=.99&&Math.abs(n.y)<=1e-6;}
function onFace(p,face){const [a,b,c]=face.vertices.map(v=>new THREE.Vector3(...v)),point=new THREE.Vector3(...p),closest=new THREE.Vector3();new THREE.Triangle(a,b,c).closestPointToPoint(point,closest);return closest.distanceTo(point)<=tolerance;}
export function verifyOriginalSharedRoofEdges(geometry,bottom,support){
 const base=verifyOriginalContactSeams(geometry,bottom,support),query=createSourceFaceQuery(geometry),surface=supportSurface(support),resolved=[],unresolved=[];
 for(const failure of base.unresolved){
  if(failure.reason!=='support-above-rim'){unresolved.push(failure);continue;}
  const p=failure.position,faces=query(p),walls=faces.filter(f=>vertical(f)&&Math.max(...f.vertices.map(v=>v[1]))>p[1]+tolerance),hits=surface.intersectionDetails(p[0],p[2]);
  const strict=hits.filter(h=>p[1]-h.height>=-.1&&p[1]-h.height<=1&&h.barycentric.every(w=>w>0)),higher=hits.filter(h=>p[1]-h.height<-.1);
  const boundaries=higher.map(h=>{
   const zeros=h.barycentric.map((w,i)=>w===0?i:-1).filter(i=>i>=0);
   if(zeros.length===2)return walls.some(f=>onFace([p[0],h.height,p[2]],f))?{kind:'corner',face:h}:null;
   if(zeros.length!==1)return null;
   // The nonzero barycentric coordinates identify the complete actual original
   // roof edge. Checking only the ray point would admit unrelated/interior roofs.
   const edge=h.vertices.filter((_,i)=>i!==zeros[0]);
   const wall=walls.find(f=>edge.every(v=>onFace(v,f)));
   return wall?{kind:'shared-edge',face:h,edge,sourceWallFace:wall}:null;
  });
  if(strict.length&&faces.length&&faces.every(vertical)&&boundaries.length&&boundaries.every(Boolean)&&boundaries.some(b=>b.kind==='shared-edge'))resolved.push({...failure,kind:'zero-area-higher-original-shared-roof-edge',strictInteriorSupportFaces:strict,higherBoundaries:boundaries,sourceWallFaces:walls});
  else unresolved.push(failure);
 }
 return {policy:'exact-original-shared-roof-edges-v1',passed:Boolean(base.samples&&base.strictContacts&&unresolved.length===0),samples:base.samples,strictContacts:base.strictContacts,wallIntersections:base.wallIntersections,seamCorrections:base.seamCorrections+resolved.length,sharedRoofEdgeCorrections:resolved.length,resolved:[...base.resolved,...resolved],unresolved,baseInterface:base,rawInterface:base.rawInterface,maximumEmbeddingM:base.maximumEmbeddingM,exactSeamToleranceM:tolerance,installationApproved:false,qualification:'Diagnostic exact zero-area higher roof boundary shared with a rising original source wall, with both edge endpoints on one actual original wall triangle and separate strict lower interior support. All raw failures and source bytes retained. All full physical, compound foundation, identity, neighbour, runtime/browser and publication checks remain separate.'};
}
