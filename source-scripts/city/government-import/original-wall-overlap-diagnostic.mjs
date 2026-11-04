/** Diagnostic of original wall/deck intersections beyond the acceptance allowance. Never an acceptance route. */
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {lowRimSamples,measureSupport,supportSurface} from './support-contact.mjs';
import {trianglePointIndex} from './triangle-point-index.mjs';

export function diagnoseOriginalWallOverlap(geometry,bottom,support,{maximumEmbedding=Infinity,metrics=null}={}){
 if(!(maximumEmbedding>0))throw new Error('Positive diagnostic search extent required');
 const rim=lowRimSamples(geometry,bottom),surface=supportSurface(support),strict=measureSupport(rim,surface);
 const resolved=[],unresolved=[],tri=new THREE.Triangle(),point=new THREE.Vector3(),closest=new THREE.Vector3(),normal=new THREE.Vector3();
 let walls=null,exactTests=0,eligibleSamples=0;
 for(const failure of strict.failed){
  const [x,y,z]=failure.position,deck=surface.height(x,z);
  if(failure.reason!=='support-above-rim'||-failure.gap>maximumEmbedding){unresolved.push(failure);continue;}
  eligibleSamples++;
  if(!walls)walls=trianglePointIndex(geometry,{acceptFace(vertices){
   [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(vertices[k]));tri.getNormal(normal);
   return Math.abs(normal.y)<=1e-6&&normal.lengthSq()>=.99;
  }});
  const incident=[];
  for(const faceIndex of walls.candidates(failure.position)){
   const i=faceIndex*3;exactTests++;
   [tri.a,tri.b,tri.c].forEach((v,k)=>v.fromArray(geometry.position,geometry.index[i+k]*3));
   tri.getNormal(normal);if(Math.abs(normal.y)>1e-6||normal.lengthSq()<.99)continue;
   // Both the bottom sample and actual deck contact must lie on this same
   // original vertical triangle; a nearby wall or disconnected roof is insufficient.
   point.set(x,y,z);tri.closestPointToPoint(point,closest);if(closest.distanceTo(point)>.001)continue;
   point.set(x,deck,z);tri.closestPointToPoint(point,closest);if(closest.distanceTo(point)>.001)continue;
   incident.push({faceIndex:i/3,vertices:[tri.a.toArray(),tri.b.toArray(),tri.c.toArray()],contact:[x,deck,z]});
  }
  if(incident.length)resolved.push({...failure,contactGapM:0,sourceWallFaces:incident,supportFaces:surface.intersectionDetails(x,z).filter(h=>Math.abs(h.height-deck)<.001)});
  else unresolved.push(failure);
 }
 // An entirely embedded mesh is not accepted through this bounded wall rule.
 const passed=Boolean(rim.length&&strict.contacts&&unresolved.length===0);
 if(metrics)Object.assign(metrics,{eligibleSamples,totalSourceFaces:geometry.index.length/3,indexedWallFaces:walls?.faces||0,indexCells:walls?.cells||0,largeFaces:walls?.largeFaces||0,exactTriangleTests:exactTests,priorFullScanTriangleVisits:eligibleSamples*geometry.index.length/3});
 return {policy:'original-wall-overlap-beyond-allowance-diagnostic-v1',geometricIntersectionsComplete:passed,installationApproved:false,acceptanceGranted:false,originalMaximumEmbeddingM:.5,samples:rim.length,
  strictContacts:strict.contacts,wallIntersections:resolved.length,strictLowRim:strict,
  maximumEmbeddingM:Number.isFinite(maximumEmbedding)?maximumEmbedding:null,resolved,unresolved,
  qualification:'Diagnostic of exact same-original-triangle vertical wall/deck intersections with no embedding search cutoff. This does NOT replace or satisfy the unchanged 0.5m acceptance allowance. Horizontal floors, missing walls and floating points remain unresolved. No model, terrain, acceptance or publication edits.'};
}
