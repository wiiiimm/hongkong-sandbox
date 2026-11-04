/** Diagnostic contracts stay separate; no old failure/pass field is rewritten. */
import assert from 'node:assert/strict';
import {supportSurface} from './support-contact.mjs';
import {nativeTerrainSurface} from '../../../3d-viewer/city/native-terrain.js';
import {withinFiniteTriangleProjection} from '../../../3d-viewer/city/exact-finite-triangle-projection.js';

export function strictNativeRows(geometry){
 const p=new Float32Array(geometry.position),idx=geometry.index,rows=[],excluded=[],bins=new Map();
 for(let t=0;t<idx.length;t+=3){
  const a=idx[t]*3,b=idx[t+1]*3,c=idx[t+2]*3,ax=p[a],az=p[a+2],bx=p[b],bz=p[b+2],cx=p[c],cz=p[c+2];
  const determinant=(bz-cz)*(ax-cx)+(cx-bx)*(az-cz),face=t/3;
  if(Math.abs(determinant)<1e-10){excluded.push(face);continue;}
  const row={face,a,b,c,ax,az,bx,bz,cx,cz,determinant};rows.push(row);
  for(let x=Math.floor(Math.min(ax,bx,cx)/20);x<=Math.floor(Math.max(ax,bx,cx)/20);x++)for(let z=Math.floor(Math.min(az,bz,cz)/20);z<=Math.floor(Math.max(az,bz,cz)/20);z++){
   const key=x+','+z;if(!bins.has(key))bins.set(key,[]);bins.get(key).push(row);
  }
 }
 const surface=nativeTerrainSurface({position:geometry.position,index:geometry.index});assert.equal(surface.triangles,rows.length);
 return {completeFacets:idx.length/3,admitted:rows.length,excluded,query(x,z){
  const hits=[];
  for(const r of bins.get(Math.floor(x/20)+','+Math.floor(z/20))||[]){
   const u=((r.bz-r.cz)*(x-r.cx)+(r.cx-r.bx)*(z-r.cz))/r.determinant,v=((r.cz-r.az)*(x-r.cx)+(r.ax-r.cx)*(z-r.cz))/r.determinant,w=1-u-v;
   if(withinFiniteTriangleProjection([r.ax,r.az],[r.bx,r.bz],[r.cx,r.cz],[x,z]))hits.push({faceIndex:r.face,height:u*p[r.a+1]+v*p[r.b+1]+w*p[r.c+1],barycentric:[u,v,w],vertices:[Array.from(p.slice(r.a,r.a+3)),Array.from(p.slice(r.b,r.b+3)),Array.from(p.slice(r.c,r.c+3))]});
  }
  const top=hits.length?Math.max(...hits.map(h=>h.height)):null;assert.equal(top,surface.height(x,z));return {hits,top};
 }};
}

export function attribute(geometry,points,labels){
 assert(Array.isArray(geometry.position)&&geometry.position.every(Number.isFinite)&&geometry.position.length%3===0);
 assert(Array.isArray(geometry.index)&&geometry.index.length%3===0&&geometry.index.every(i=>Number.isInteger(i)&&i>=0&&i<geometry.position.length/3));
 assert.equal(labels.length,geometry.index.length/3);assert(labels.every(i=>Number.isInteger(i)&&i>=0));
 const eps=supportSurface(geometry),native=strictNativeRows(geometry),rows=[];
 const decorate=h=>({...h,providerOriginalBodyOrdinal:labels[h.faceIndex],bodyOrdinalNotRoleOrExactOriginalMembershipProof:true});
 for(const point of points){
  const [x,y,z]=point.failure.position;assert([x,y,z].every(Number.isFinite));
  const hits=eps.intersectionDetails(x,z).map(h=>({...decorate(h),strictClosedFloat64Projection:withinFiniteTriangleProjection([h.vertices[0][0],h.vertices[0][2]],[h.vertices[1][0],h.vertices[1][2]],[h.vertices[2][0],h.vertices[2][2]],[x,z])}));
  const top=hits.length?hits.at(-1).height:null;assert.equal(top,eps.height(x,z));const n=native.query(x,z);
  rows.push({...point,legacyFailureVerbatim:point.failure,savedPointNotResampled:true,EPSModelGeometry:{highestHeight:top,computedGap:top===null?null:y-top,oldGapMinusComputedGap:top===null?null:point.failure.gap-(y-top),allSourceLayerHits:hits,highestSourceHits:top===null?[]:hits.filter(h=>h.height===top),lowerHitsWithinExistingContactInterval:hits.filter(h=>y-h.height>=-.1&&y-h.height<=1),allOldNegativeFieldsPreserved:true},nativeStyleFloat32StrictDiagnostic:{highestHeight:n.top,computedGap:n.top===null?null:y-n.top,allSourceLayerHits:n.hits.map(decorate),notActualTerrainOrTowerSupportAcceptance:true},noToleranceSubstitutionOrAcceptance:true});
 }
 return {rows,completeSourceFacets:geometry.index.length/3,legacyEPSAdmittedFacets:eps.triangles,nativeFloat32AdmittedFacets:native.admitted,nativeFloat32ExcludedFacets:native.excluded,allSourceSlotsAccounted:true,noAllFacesHeightIndexedRequirement:true};
}
