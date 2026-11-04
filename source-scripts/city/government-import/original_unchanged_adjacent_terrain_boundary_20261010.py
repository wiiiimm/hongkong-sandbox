"""Exact seam-only adjacency to an unchanged replaced terrain parent.

Not an overlap allowance: rectangles must have disjoint interiors and share one
positive-length straight boundary. Complete candidate/parent triangle inventories
must remain inside their pinned extent, and every exact seam interval/endpoint
must carry the identical original parent height on the candidate. An adjacent
terrain actor remains unchanged; all current physics/native checks stay separate.
"""
import hashlib
from fractions import Fraction as F
import numpy as np

def sha(x):return hashlib.sha256(np.asarray(x,dtype=np.float64).tobytes()).hexdigest()
def _seam(a,b):
 a,b=[list(map(lambda x:F.from_float(float(x)),v)) for v in [a,b]]
 assert len(a)==len(b)==4 and a[0]<a[2] and a[1]<a[3] and b[0]<b[2] and b[1]<b[3]
 lo=[max(a[0],b[0]),max(a[1],b[1])];hi=[min(a[2],b[2]),min(a[3],b[3])]
 assert all(l<=h for l,h in zip(lo,hi)) and sum(l==h for l,h in zip(lo,hi))==1,'Not positive-length exact seam-only adjacency'
 fixed=0 if lo[0]==hi[0] else 2;return fixed,lo[0 if fixed==0 else 1],lo[1 if fixed==0 else 0],hi[1 if fixed==0 else 0]
def _pieces(tri,bounds,fixed,value,start,end):
 assert tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(tri).all()
 assert np.all(tri[:,:,0]>=bounds[0]) and np.all(tri[:,:,0]<=bounds[2]) and np.all(tri[:,:,2]>=bounds[1]) and np.all(tri[:,:,2]<=bounds[3]),'Terrain triangle outside complete pinned bounds'
 varying=2 if fixed==0 else 0;segments=[];points=[]
 for i,t in enumerate(tri):
  vertices=[tuple(F.from_float(float(x)) for x in p) for p in t];p=[v for v in vertices if v[fixed]==value and start<=v[varying]<=end]
  for a,b in zip(vertices,vertices[1:]+vertices[:1]):
   if a[fixed]==b[fixed]:
    if a[fixed]!=value:continue
    left,right=sorted([a,b],key=lambda v:v[varying]);lo=max(start,left[varying]);hi=min(end,right[varying])
    if lo>hi or left[varying]==right[varying]:continue
    def at(s):return tuple(left[k]+(s-left[varying])/(right[varying]-left[varying])*(right[k]-left[k]) for k in range(3))
    p.extend([at(lo),at(hi)])
   elif min(a[fixed],b[fixed])<=value<=max(a[fixed],b[fixed]):
    ratio=(value-a[fixed])/(b[fixed]-a[fixed]);q=tuple(a[k]+ratio*(b[k]-a[k]) for k in range(3))
    if start<=q[varying]<=end:p.append(q)
  p=sorted(set(p),key=lambda v:(v[varying],v[1]))
  if p:
   points.extend((v[varying],v[1],i) for v in p)
   if p[0][varying]!=p[-1][varying]:segments.append((p[0][varying],p[-1][varying],p[0][1],p[-1][1],i))
 return segments,points

def verify(parent,proposal,adjacent,*,parent_bounds,proposal_bounds,adjacent_bounds,expected_binding,current_binding):
 assert expected_binding==current_binding
 parent,proposal,adjacent=[np.asarray(t,dtype=np.float64) for t in [parent,proposal,adjacent]]
 for key,t in [('completeOriginalParentTrianglesSHA256',parent),('completeProposalTrianglesSHA256',proposal),('completeUnchangedAdjacentTrianglesSHA256',adjacent)]:assert current_binding[key]==sha(t)
 assert list(parent_bounds)==list(proposal_bounds),'Parent extent changed'
 fixed,value,start,end=_seam(proposal_bounds,adjacent_bounds)
 # The complete adjacent original actor is pinned and bounded; no triangles
 # are removed, clipped or substituted by this proof.
 _pieces(adjacent,adjacent_bounds,fixed,value,start,end)
 pp,pa=_pieces(parent,parent_bounds,fixed,value,start,end);qp,qa=_pieces(proposal,proposal_bounds,fixed,value,start,end)
 cuts=sorted({start,end,*[x for s in pp+qp for x in s[:2]],*[x[0] for x in pa+qa]})
 def heights(x,segments,points):
  values={a+(x-l)/(r-l)*(b-a) for l,r,a,b,_ in segments if l<=x<=r};values.update(y for px,y,_ in points if px==x);assert len(values)==1,'Missing seam coverage or conflicting original seam heights';return next(iter(values))
 witnesses=[]
 for x in cuts:
  a=heights(x,pp,pa);b=heights(x,qp,qa);assert a==b,'Candidate changed original terrain boundary height';witnesses.append(dict(exactSeamParameter=str(x),exactUnchangedHeightM=str(a)))
 intervals=[]
 for l,r in zip(cuts,cuts[1:]):
  x=(l+r)/2;a=heights(x,pp,pa);b=heights(x,qp,qa);assert a==b,'Candidate changed continuous original terrain boundary';intervals.append(dict(exactOpenInterval=[str(l),str(r)],exactMidpoint=str(x),exactUnchangedHeightM=str(a)))
 assert intervals
 return dict(contract='exact-original-parent-unchanged-adjacent-terrain-boundary-v1',binding=current_binding,completeParentFaces=len(parent),completeProposalFaces=len(proposal),completeUnchangedAdjacentFaces=len(adjacent),fixedWorldAxis=fixed,exactFixedCoordinateM=str(value),completeSharedIntervalM=[str(start),str(end)],exactEndpointWitnesses=witnesses,completeAffineOpenIntervals=intervals,positiveAreaOverlap=False,sourceGeometryChanges=0,terrainGeometryChanges=0,adjacentActorChanged=False,fullAcceptance=False,installationApproved=False)
