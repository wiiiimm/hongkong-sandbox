"""Exact complete source-face coverage by finite terrain lying at or above it.

Work in source barycentric coordinates, so vertical walls retain full dimension.
Finite closed convex certificate regions with zero uncovered unit-triangle area
cover its closure. No distance, area tolerance or projected rank exemption.
"""
from fractions import Fraction as F
import numpy as np
from exact_original_projection_coverage_v2_20261010 import signed_area,subtract

def clip_affine(poly,values):
 if not poly:return []
 def value(p):return values[0]+(values[1]-values[0])*p[0]+(values[2]-values[0])*p[1]
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  x,y=value(a),value(b)
  if x>=0:out.append(a)
  if (x>=0)!=(y>=0):
   t=x/(x-y);out.append(tuple(a[k]+t*(b[k]-a[k])for k in range(2)))
 result=[]
 for p in out:
  if not result or result[-1]!=p:result.append(p)
 if len(result)>1 and result[-1]==result[0]:result.pop()
 return result

def prove(face,ground):
 face=np.asarray(face,float);ground=np.asarray(ground,float);assert face.shape==(3,3)and ground.ndim==3 and ground.shape[1:]==(3,3)and np.isfinite(face).all()and np.isfinite(ground).all();assert np.linalg.norm(np.cross(face[1]-face[0],face[2]-face[0]))>0
 source=[tuple(F.from_float(float(v))for v in p)for p in face];unit=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];remaining=[unit];certificates=[];lo,hi=face.min(0),face.max(0);ids=np.flatnonzero((ground[:,:,0].max(1)>=lo[0])&(ground[:,:,0].min(1)<=hi[0])&(ground[:,:,2].max(1)>=lo[2])&(ground[:,:,2].min(1)<=hi[2]))
 for j in ids:
  g=[tuple(F.from_float(float(v))for v in p)for p in ground[j]];a,b,c=g;u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
  if n[1]==0:continue
  xz=[(p[0],p[2])for p in g]
  if signed_area(xz)<0:xz.reverse()
  region=unit
  for p,q in zip(xz,xz[1:]+xz[:1]):
   values=[(q[0]-p[0])*(s[2]-p[1])-(q[1]-p[1])*(s[0]-p[0])for s in source];region=clip_affine(region,values)
   if not region:break
  if not region or signed_area(region)==0:continue
  differences=[a[1]-(n[0]*(s[0]-a[0])+n[2]*(s[2]-a[2]))/n[1]-s[1]for s in source];region=clip_affine(region,differences)
  if len(region)<3 or signed_area(region)==0:continue
  certificates.append(dict(terrainFace=int(j),sourceUVRegion=[[str(v)for v in p]for p in region],terrainMinusSourceAtSourceCorners=[str(v)for v in differences]))
  for k in range(1,len(region)-1):
   t=[region[0],region[k],region[k+1]];remaining=[part for piece in remaining for part in subtract(piece,t)]
   if not remaining:break
  if not remaining:break
 uncovered=sum((abs(signed_area(p))for p in remaining),F(0))
 return dict(wholeOriginalFaceAtOrBelowFiniteTerrain=uncovered==0,exactUncoveredSourceUVArea=str(uncovered),completeSourceUVArea='1/2',completeGroundFaces=len(ground),closedAABBCandidateFacets=len(ids),finiteTerrainCertificates=certificates,remainingSourceUVPolygons=[[[str(v)for v in p]for p in q]for q in remaining],noToleranceOrSnap=True,verticalSourceFacesRetainTwoDimensionalDomain=True,installationApproved=False)
