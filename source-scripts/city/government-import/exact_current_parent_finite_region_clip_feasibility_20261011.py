"""Exact finite parent-plane clip feasibility; no terrain candidate or acceptance.

Every rational clip remains on its input plane. Float32 packing is checked
independently and cannot inherit that assertion; real plane residuals remain
negative. Vertical/line/point records are explicitly inventoried, never dropped
by a fixed area threshold or used as a height/support exemption.
"""
from fractions import Fraction as F
import math
import numpy as np
from actual_native_parent_transition_v3_20261010 import triangle_clip,rational,nondegenerate
from exact_original_polygon_triangle_partition_20261010 import exact_partition

def cross3(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def normal(tri):
 a,b,c=tri;return cross3(tuple(b[k]-a[k]for k in range(3)),tuple(c[k]-a[k]for k in range(3)))
def residual(p,tri):
 n=normal(tri);return sum(n[k]*(p[k]-tri[0][k])for k in range(3))
def primitive_dimension(points):
 distinct=list(dict.fromkeys(points))
 if len(distinct)<2:return 0
 return 2 if any(nondegenerate([distinct[0],distinct[1],p])for p in distinct[2:])else 1

def diagnose(parent,rings,region_triangles):
 parent=np.asarray(parent,dtype=float);region=np.asarray(region_triangles,dtype=float)
 assert parent.ndim==3 and parent.shape[1:]==(3,3)and len(parent)and np.isfinite(parent).all()
 assert region.ndim==3 and region.shape[1:]==(3,2)and len(region)and np.isfinite(region).all()
 partition=exact_partition(rings,region.tolist())
 records=[];out=[];plane_failures=[];unrepresentable=[]
 for i,face in enumerate(parent):
  original=[rational(p)for p in face];dimension=primitive_dimension(original);pieces=[]
  for j,t in enumerate(region):
   # Broad phase only, closed boxes; exact finite clipping decides membership.
   if face[:,0].max()<t[:,0].min()or face[:,0].min()>t[:,0].max()or face[:,2].max()<t[:,1].min()or face[:,2].min()>t[:,1].max():continue
   clip=triangle_clip(original,[[p[0],0,p[1]]for p in t])
   if not clip:continue
   for p in clip:assert residual(p,original)==0
   dims=primitive_dimension(clip);exact=[list(map(str,p))for p in clip];packed=np.asarray(clip,dtype=float).astype(np.float32).astype(float);assert np.isfinite(packed).all()
   packed_rational=[rational(p)for p in packed];errs=[residual(p,original)for p in packed_rational]
   unequal=[k for k,(a,b)in enumerate(zip(clip,packed_rational))if a!=b]
   item=dict(regionTriangle=j,exactFinitePrimitiveDimension=dims,exactClippedVertices=exact,packedFloat32Vertices=packed.tolist(),allPrepackVerticesExactlyOnOriginalParentPlane=True,packedVerticesOutsideOriginalParentPlane=[k for k,e in enumerate(errs)if e],exactPackedPlaneResiduals=list(map(str,errs)),newVerticesNotExactlyFloat32Representable=unequal)
   pieces.append(item)
   if any(errs):plane_failures.append(dict(originalParentFace=i,regionTriangle=j,exactPackedPlaneResiduals=item['exactPackedPlaneResiduals']))
   if unequal:unrepresentable.append(dict(originalParentFace=i,regionTriangle=j,vertices=unequal))
   if dims==2:
    for k in range(1,len(clip)-1):
     if nondegenerate([clip[0],clip[k],clip[k+1]]):out.append(packed[[0,k,k+1]].tolist())
  records.append(dict(originalParentFace=i,completeOriginalPrimitiveDimension=dimension,originalFaceVertices=face.tolist(),finiteRegionClips=pieces))
 return dict(completeOriginalParentFacets=len(parent),exactCompleteRegionPartition=partition,allOriginalParentFacetDispositions=records,packedClippedFacets=out,actualFloat32PlaneFailures=plane_failures,unrepresentableClippedVertices=unrepresentable,allPackedFacetsExactlyOnOriginalParentPlanes=not plane_failures,actualPackedDomainCoverageStillRequired=True,actualSeamContinuityStillRequired=True,terrainCandidateCreated=False,terrainGeometryChanges=0,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False)
