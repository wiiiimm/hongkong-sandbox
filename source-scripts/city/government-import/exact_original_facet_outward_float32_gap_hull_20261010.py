"""Minimal convex Float32-cell hull around an exact bounded terrain gap.

Long diagonal seam gaps do not justify their large axis-aligned rectangle.
Enclose each exact vertex in its minimal outward Float32 cell, then compute the
exact convex hull. The full hull must stay inside one authentic finite original
TIN triangle; new heights are interpolated only on that source plane. Explicit
new proposal extent/quantization, no buffer, extrapolation or acceptance credit.
"""
from fractions import Fraction as F
import hashlib,numpy as np
from exact_original_facet_outward_float32_gap_patch_20261010 import fraction,cross,outward
def hull(points):
 pts=sorted(set(points));assert len(pts)>2
 def half(seq):
  out=[]
  for p in seq:
   while len(out)>1 and cross(out[-2],out[-1],p)<=0:out.pop()
   out.append(p)
  return out
 return half(pts)[:-1]+half(pts[::-1])[:-1]
def propose(exact_gap_region,original_finite_terrain_face):
 region=[tuple(fraction(v) for v in p) for p in exact_gap_region];assert region and all(len(p)==2 for p in region)
 face=np.asarray(original_finite_terrain_face,float);assert face.shape==(3,3) and np.isfinite(face).all();cells=[];corners=[]
 for p in region:
  bounds=[outward(p[0],True),outward(p[1],True),outward(p[0],False),outward(p[1],False)]
  for k in range(2):
   if bounds[k]==bounds[k+2]:bounds[k]=float(np.nextafter(np.float32(bounds[k]),np.float32(-np.inf),dtype=np.float32));bounds[k+2]=float(np.nextafter(np.float32(bounds[k+2]),np.float32(np.inf),dtype=np.float32))
  cell=[(F(bounds[0]),F(bounds[1])),(F(bounds[2]),F(bounds[1])),(F(bounds[2]),F(bounds[3])),(F(bounds[0]),F(bounds[3]))];cells.append(dict(exactGapVertex=[str(v) for v in p],minimalOutwardFloat32BoundsXZ=bounds));corners.extend(cell)
 polygon=hull(corners);assert len(polygon)>=3 and all(all(cross(a,b,p)>=0 for a,b in zip(polygon,polygon[1:]+polygon[:1])) for p in region)
 source=[tuple(F(float(v)) for v in p) for p in face];xz=[(p[0],p[2]) for p in source];area=cross(*xz);assert area
 assert all(all(cross(a,b,p)*(1 if area>0 else -1)>=0 for a,b in zip(xz,xz[1:]+xz[:1])) for p in polygon),'Complete outward hull must stay inside authentic finite facet'
 a,b,c=source;u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];assert n[1]
 ys=[a[1]-(n[0]*(x-a[0])+n[2]*(z-a[2]))/n[1] for x,z in polygon];vertices=[[float(x),float(np.float32(float(y))),float(z)] for (x,z),y in zip(polygon,ys)];assert np.isfinite(vertices).all();faces=[[vertices[i] for i in [0,j,j+1]] for j in range(1,len(vertices)-1)];projected_area=sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(polygon,polygon[1:]+polygon[:1]))/2;assert projected_area>0
 return dict(contract='bounded-authentic-finite-TIN-minimal-outward-Float32-cell-hull-gap-proposal-v1',originalFiniteSourceTerrainFaceSHA256=hashlib.sha256(face.tobytes()).hexdigest(),originalFiniteSourceTerrainFace=face.tolist(),completeExactGapRegion=[[str(v) for v in p] for p in region],allMinimalOutwardFloat32VertexCells=cells,exactConvexOutwardHullXZ=[[str(v) for v in p] for p in polygon],fullProposedProjectedAreaM2=str(projected_area),allHullVerticesExactlyWithinAuthenticFiniteFacet=True,exactSourcePlaneVertexHeightsM=[str(y) for y in ys],explicitFloat32HeightQuantizationM=[str(F(p[1])-y) for p,y in zip(vertices,ys)],proposedVertices=vertices,proposedFaces=faces,terrainProposalGeometryChanged=True,buildingGeometryChanges=0,sourcePlaneExtrapolation=False,toleranceOrBufferCredit=False,fullAcceptance=False,installationApproved=False)
