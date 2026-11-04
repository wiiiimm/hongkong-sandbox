"""Exact finite overlay/equal-height source context, never frontier qualification."""
from fractions import Fraction as F
import numpy as np
from exact_source_planar_domain_recovery_seams_v1_20261011 import projected,oriented,source_height
from exact_original_projection_coverage_v2_20261010 import clip,signed_area

def locus(source,current):
 source=np.asarray(source,dtype='<f8');current=np.asarray(current,dtype='<f8')
 for face in [source,current]:
  assert face.shape==(3,3) and np.isfinite(face).all(),'Nonfinite or malformed finite original facet'
 polys=[projected(f)for f in [source,current]]
 if any(signed_area(p)==0 for p in polys):
  return dict(classification='degenerate-projection-unqualified',positiveAreaOverlay=False)
 polygon=oriented(polys[0]);host=oriented(polys[1])
 for a,b in zip(host,host[1:]+host[:1]):polygon=clip(polygon,a,b,True)
 if signed_area(polygon)==0:
  return dict(classification='no-positive-area-overlay',positiveAreaOverlay=False)
 gaps=[source_height(source,p)-source_height(current,p)for p in polygon]
 common=dict(positiveAreaOverlay=True,polygon=polygon,exactAreaM2=abs(signed_area(polygon)),exactVertexHeightGapsM=gaps,sourceContextOnly=True,qualifiedRetainedFrontier=False)
 if all(g==0 for g in gaps):return dict(common,classification='equal-plane-finite-overlay',zeroHeightPolygon=polygon)
 points=set()
 for i,(a,b)in enumerate(zip(polygon,polygon[1:]+polygon[:1])):
  ga,gb=gaps[i],gaps[(i+1)%len(polygon)]
  if ga==0:points.add(a)
  if ga*gb<0:
   t=ga/(ga-gb);points.add(tuple(a[k]+t*(b[k]-a[k])for k in [0,1]))
 if not points:return dict(common,classification='no-equal-height-locus',sourceAlwaysAbove=min(gaps)>0,sourceAlwaysBelow=max(gaps)<0)
 if len(points)==1:return dict(common,classification='isolated-equal-height-point',point=next(iter(points)),positiveDimensionalSeam=False)
 # A nonzero affine function has a line zero set; choose exact extreme endpoints.
 axis=0 if len({p[0]for p in points})>1 else 1
 ordered=sorted(points,key=lambda p:p[axis]);a,b=ordered[0],ordered[-1];assert a!=b
 for p in points:assert (b[0]-a[0])*(p[1]-a[1])==(b[1]-a[1])*(p[0]-a[0])
 xyz=[(p[0],source_height(source,p),p[1])for p in [a,b]]
 assert all(source_height(source,p)==source_height(current,p)for p in [a,b])
 return dict(common,classification='finite-positive-3D-equal-height-segment',exactSegment=xyz,positiveDimensionalSeam=True,sourcePlaneContainmentOfCurrentFacetProved=False)
