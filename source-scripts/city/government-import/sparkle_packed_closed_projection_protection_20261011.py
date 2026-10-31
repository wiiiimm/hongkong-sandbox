"""Exact finite protection diagnostic; no construction/support acceptance.

Inclusive AABB nominations are exhaustive. Strict separation requires a
rational SAT interval witness. Every point/edge/area intersection is retained
as a failure, including projected degeneracies. No epsilon or rounding.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_closed_projection_intersection_20261010 import intersection

def rational(value):
 return [value.numerator,value.denominator]

def closed_pair(first,second):
 a=[tuple(F(float(v))for v in p)for p in first]
 b=[tuple(F(float(v))for v in p)for p in second]
 assert len(a)>=1 and len(b)>=1 and all(len(p)==2 for p in a+b)
 axes={(F(1),F(0)),(F(0),F(1))}
 for poly in [a,b]:
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dx,dy=q[0]-p[0],q[1]-p[1]
   if dx or dy:
    axes.add((-dy,dx));axes.add((dx,dy))
 # Edge tangents also separate collinear collapsed polygons. Extra axes cannot
 # create a false separator: projections of every original vertex are bound.
 for axis in sorted(axes):
  left=[p[0]*axis[0]+p[1]*axis[1]for p in a]
  right=[p[0]*axis[0]+p[1]*axis[1]for p in b]
  if max(left)<min(right)or max(right)<min(left):
   assert not intersection(a,b),'SAT and complete closed intersection disagree'
   return dict(strictlySeparated=True,axis=[rational(v)for v in axis],
    firstInterval=[rational(min(left)),rational(max(left))],
    secondInterval=[rational(min(right)),rational(max(right))])
 points=intersection(a,b)
 assert points,'No exact separator and no closed intersection'
 return dict(strictlySeparated=False,completeClosedIntersection=[
  [rational(v)for v in p]for p in points])

def audit(new,rectangles,retained):
 n=np.asarray(new,dtype=np.float64);r=np.asarray(rectangles,dtype=np.float64)
 g=np.asarray(retained,dtype=np.float64)
 assert n.ndim==g.ndim==3 and n.shape[1:]==g.shape[1:]==(3,3)
 assert len(n)and len(g)and r.ndim==2 and r.shape[1]==4 and len(r)
 assert all(np.isfinite(v).all()for v in [n,r,g])
 assert np.array_equal(n,n.astype(np.float32).astype(np.float64))
 assert np.array_equal(g,g.astype(np.float32).astype(np.float64))
 assert np.all(r[:,:2]<r[:,2:])
 projected=n[:,:,[0,2]];lo=projected.min(axis=1);hi=projected.max(axis=1)
 rows=[];complete_pairs=0;omitted=0
 for kind,targets in [('closedRectangle',r),('wholeRetainedLiteralFacet',g)]:
  for target_id,target in enumerate(targets):
   if kind=='closedRectangle':
    x,z,X,Z=target;poly=np.array([[x,z],[X,z],[X,Z],[x,Z]])
   else:poly=target[:,[0,2]]
   lower,upper=poly.min(axis=0),poly.max(axis=0)
   hits=np.flatnonzero(np.all(lo<=upper,axis=1)&np.all(hi>=lower,axis=1))
   complete_pairs+=len(n);omitted+=len(n)-len(hits)
   for face_id in hits:
    rows.append(dict(newPackedFaceID=int(face_id),targetKind=kind,
     targetID=target_id,**closed_pair(projected[face_id],poly)))
 failures=[row for row in rows if not row['strictlySeparated']]
 return dict(completeNewPackedFacets=len(n),completeInnerClosedRectangles=len(r),
  completeWholeRetainedLiteralFacets=len(g),completePairs=complete_pairs,
  strictAABBSeparatedPairs=omitted,completeInclusiveAABBNominations=len(rows),
  nominations=rows,actualClosedIntersectionPairs=len(failures),
  allFiniteProjectedPairsStrictlySeparated=not failures,noTolerance=True,
  projectedDegeneraciesRetained=True,pointAndEdgeTouchesFail=True,
  newPackedXYZSHA256=hashlib.sha256(n.tobytes()).hexdigest(),
  retainedLiteralXYZSHA256=hashlib.sha256(g.tobytes()).hexdigest(),
  innerClosedRectanglesSHA256=hashlib.sha256(r.tobytes()).hexdigest(),
  currentAcceptance=False,nativeReacceptance=False)
