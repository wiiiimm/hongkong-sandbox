/** Exact vertical-wall contact at the podium surface; no coordinate correction. */
import * as THREE from '../../../3d-viewer/vendor/three.module.js';
import {lowRimSamples,measureSupport,supportSurface} from './support-contact.mjs';
import {trianglePointIndex} from './triangle-point-index.mjs';

export function verifySupportInterface(geometry,bottom,support,{maximumEmbedding=.5,metrics=null}={}){
 if(!(maximumEmbedding>0&&maximumEmbedding<=.5))throw new Error('Embedding exceeds ordinary source clearance allowance');
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
 return {policy:'exact-native-wall-podium-interface-v1',passed,samples:rim.length,
  strictContacts:strict.contacts,wallIntersections:resolved.length,strictLowRim:strict,
  maximumEmbeddingM:maximumEmbedding,resolved,unresolved,
  qualification:'Actual same-triangle vertical wall/podium intersection resolves a rim below the deck by at most the existing ordinary 0.5m source-clearance allowance. Requires other strict rim contacts. No horizontal buried floor, floating point, missing support, fully embedded source or coordinate edit is accepted.'};
}
