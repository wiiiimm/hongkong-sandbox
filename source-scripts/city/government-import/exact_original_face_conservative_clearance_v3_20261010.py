"""Exact projected terrain maximum + minimum original source vertex height.

Independent conservative bound under unchanged -.5m rule; every original
terrain/source face remains present. Source-plane inversion is never used.
Raw earlier diagnostics and coarse conservative failures remain untouched.
Exact zero-area terrain facets are explicitly accounted as non-rendering, earn
no height/coverage credit, and retain all original coordinates and face indices.
"""
import hashlib
from fractions import Fraction as F
import numpy as np
from exact_original_projection_coverage_20261009 import exact_coverage,point,signed_area,clip
def verify(face,ground):
 source=np.asarray(face,float);terrain=np.asarray(ground,float);assert source.shape==(3,3) and terrain.ndim==3 and terrain.shape[1:]==(3,3) and len(terrain) and np.isfinite(source).all() and np.isfinite(terrain).all()
 lo=source[:,[0,2]].min(axis=0);hi=source[:,[0,2]].max(axis=0);xz=terrain[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(axis=1)>=lo,axis=1)&np.all(xz.min(axis=1)<=hi,axis=1));assert len(ids)
 coverage=exact_coverage(source,terrain[ids]);poly=[point(p) for p in source[:,[0,2]]];pieces=[];heights=[]
 for j in ids:
  original=terrain[j];projected=[point(p) for p in original[:,[0,2]]];area=signed_area(projected)
  if area==0:
   a,b,c=[tuple(F.from_float(float(v)) for v in p) for p in original];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)];normal=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
   if normal==(0,0,0):
    pieces.append(dict(originalGroundFace=int(j),exactZeroAreaNonRenderingGroundFacet=True,allOriginalVertices=original.tolist(),exactOriginalCrossProduct=list(map(str,normal)),sourceGeometryChanged=False,groundHeightOrCoverageCredit=False));continue
   # Collapsed finite drawn projections stay conservatively accounted. They
   # are never discarded or assigned an invented finite ground plane.
   y=max(F.from_float(float(p[1])) for p in original);heights.append(y);pieces.append(dict(originalGroundFace=int(j),collapsedProjectionConservative=True,exactUpperHeightM=str(y)));continue
  if area<0:projected.reverse()
  intersection=poly
  for a,b in zip(projected,projected[1:]+projected[:1]):intersection=clip(intersection,a,b,True)
  if not intersection:continue
  a,b,c=[tuple(F.from_float(float(v)) for v in p) for p in original];u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)];n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]!=0
  ys=[a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1] for x,z in intersection];heights.extend(ys);pieces.append(dict(originalGroundFace=int(j),closedExactProjectedIntersection=[[str(x),str(z)] for x,z in intersection],exactUpperHeightM=str(max(ys))))
 assert heights;low=F.from_float(float(source[:,1].min()));high=max(heights);bound=low-high
 return dict(contract='exact-original-facet-conservative-clipped-terrain-clearance-v3',completeOriginalProjectionCoverage=coverage,groundProjectionCovered=coverage['exactProjectionCovered'],allProjectedBoundingCandidateOriginalGroundFacets=list(map(int,ids)),allExactOriginalTerrainIntersectionHeightPieces=pieces,exactMinimumOriginalSourceHeightM=str(low),exactMaximumAllCandidateOriginalGroundHeightM=str(high),exactCertifiedLowerClearanceM=str(bound),existingOrdinaryClearanceBoundProved=coverage['exactProjectionCovered'] and bound>=F.from_float(-.5),sourceFaceSHA256=hashlib.sha256(source.tobytes()).hexdigest(),completeCurrentGroundSHA256=hashlib.sha256(terrain.tobytes()).hexdigest(),sourcePlaneInversionUsed=False,rawPriorDiagnosticChanged=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False)
