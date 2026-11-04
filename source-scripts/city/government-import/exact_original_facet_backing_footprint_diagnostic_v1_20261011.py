"""Whole finite orthogonal footprint on one genuine original coplanar patch.

This records placement separately from proximity: no distance band is increased
or credited. Signed distances and the existing .1m plane-band result remain
explicit. Complete source barycentric coverage uses unchanged exact clipping
and finite union primitives. A footprint never supplies a mount/role/root.
"""
import hashlib
from fractions import Fraction as F
import numpy as np
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import point,sub,dot,cross
from exact_original_surface_coordinate_band_20261010 import linear_clip,polygon_union_covers
from original_coplanar_exterior_continuation_20261009 import plane

def verify(source,hosts,*,expected_binding=None):
 s=np.asarray(source,float);h=np.asarray(hosts,float);assert s.shape==(3,3)and h.ndim==3 and h.shape[1:]==(3,3)and len(h)and np.isfinite(s).all()and np.isfinite(h).all()
 binding=dict(completeSourceFacetSHA256=hashlib.sha256(s.tobytes()).hexdigest(),completeOriginalHostPatchSHA256=hashlib.sha256(h.tobytes()).hexdigest())
 if expected_binding is not None:assert binding==expected_binding,'Original complete source/backing patch changed'
 keys=[plane(f)for f in h];nonzero={key for key in keys if key is not None};assert len(nonzero)<=1,'One genuine complete coplanar host patch required'
 a,b,c=map(point,s);u,v=sub(b,a),sub(c,a);sn=cross(u,v);simplex=[(F(0),F(0)),(F(1),F(0)),(F(0),F(1))];regions=[];rows=[];zero=[];collapsed=[]
 if not dot(sn,sn):return dict(binding=binding,sourceDimensionLessThan2=True,wholeFiniteBackingFootprintCovered=False,sourceReceivesNoSupportCredit=True,visualRoleAccepted=False,structuralRootOrBridgeCredit=False)
 for j,f in enumerate(h):
  if keys[j]is None:zero.append(j);continue
  p,q,r=map(point,f);hu,hv=sub(q,p),sub(r,p);hn=cross(hu,hv);n2=dot(hn,hn);assert n2>0
  if dot(sn,hn)==0:collapsed.append(j);continue
  aa,ab,bb=dot(hu,hu),dot(hu,hv),dot(hv,hv);det=aa*bb-ab*ab;assert det==n2;offset=sub(a,p)
  beta=tuple((dot(x,hu)*bb-dot(x,hv)*ab)/det for x in (u,v,offset));gamma=tuple((dot(x,hv)*aa-dot(x,hu)*ab)/det for x in (u,v,offset));poly=list(simplex)
  for coeff in (beta,gamma,tuple((F(1)if k==2 else F(0))-beta[k]-gamma[k]for k in range(3))):poly=linear_clip(poly,coeff)
  if len(poly)<3:continue
  from exact_original_projection_coverage_20261009 import signed_area
  if signed_area(poly)==0:continue
  signed=tuple(dot(hn,x)for x in (u,v,offset));values=[signed[0]*x+signed[1]*y+signed[2]for x,y in simplex];squared=[x*x/n2 for x in values];regions.append(poly)
  rows.append(dict(originalHostPatchFace=j,completeExactSourceBarycentricFootRegion=[[str(x),str(y)]for x,y in poly],exactSignedUnnormalizedSourceVertexDistances=list(map(str,values)),exactHostNormalSquared=str(n2),exactMaximumSourceVertexSquaredPlaneDistanceM2=str(max(squared)),allSourceVerticesWithinExistingPointOnePlaneBand=max(squared)<=F(.1)**2,orthogonalFootDimensionTwo=True))
 covered,proof=polygon_union_covers(simplex,regions)
 return dict(contract='exact-original-whole-facet-coplanar-backing-footprint-diagnostic-v1',binding=binding,wholeFiniteBackingFootprintCovered=covered,completeOriginalHostFacets=len(h),allCompleteFiniteFootRegionRecords=rows,sourceBarycentricCoverage=proof,exactZeroAreaHostPatchFaces=zero,collapsedOrthogonalProjectionsReceiveNoFootprintCredit=collapsed,sourceToHostSignedDistanceKeptExplicit=True,existingPointOneDistanceBandNotChanged=True,footprintIsNotProximityOrMount=True,sourceGeometryChanges=0,visualRoleAccepted=False,currentAcceptance=False,structuralRootOrBridgeCredit=False)
