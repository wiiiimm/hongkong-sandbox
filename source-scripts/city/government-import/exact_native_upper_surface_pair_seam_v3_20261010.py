"""Complete exact finite upper-envelope equality in the existing2mm seam band."""
from fractions import Fraction as F
import numpy as np
def pieces(segment,triangles):
 a,b=[tuple(F(float(v)) for v in p) for p in segment];t=np.asarray(triangles,float);assert np.isfinite(t).all()
 lo=np.minimum(segment[0],segment[1])[[0,2]];hi=np.maximum(segment[0],segment[1])[[0,2]];ids=np.flatnonzero(np.all(t[:,:,[0,2]].max(1)>=lo,axis=1)&np.all(t[:,:,[0,2]].min(1)<=hi,axis=1));out=[]
 for i in ids:
  p,q,r=[tuple(F(float(v)) for v in x) for x in t[i]];den=(q[2]-r[2])*(p[0]-r[0])+(r[0]-q[0])*(p[2]-r[2])
  if den==0:continue
  def bary(v):
   u=((q[2]-r[2])*(v[0]-r[0])+(r[0]-q[0])*(v[2]-r[2]))/den;w=((r[2]-p[2])*(v[0]-r[0])+(p[0]-r[0])*(v[2]-r[2]))/den;return u,w,1-u-w
  aa,bb=bary(a),bary(b);l,h=F(0),F(1)
  for x,y in zip(aa,bb):
   slope=y-x
   if slope==0:
    if x<0:l,h=F(1),F(0);break
   elif slope>0:l=max(l,-x/slope)
   else:h=min(h,-x/slope)
  if l<=h:out.append((l,h,sum(v*f[1] for v,f in zip(aa,[p,q,r])),sum(v*f[1] for v,f in zip(bb,[p,q,r])),int(i)))
 return out
def verify_pair(segment,original,candidate):
 segment=np.asarray(segment,float);assert segment.shape==(2,3) and np.isfinite(segment).all()
 original,candidate=pieces(segment,original),pieces(segment,candidate);cuts={F(0),F(1)}
 for group in [original,candidate]:
  for l,h,*_ in group:cuts.update([l,h])
  for i,(l,h,a,b,_) in enumerate(group):
   for L,H,A,B,_ in group[i+1:]:
    den=(b-a)-(B-A)
    if den:
     s=(A-a)/den
     if max(l,L)<=s<=min(h,H):cuts.add(s)
 def upper(group,s):
  vals=[a+s*(b-a) for l,h,a,b,_ in group if l<=s<=h];return max(vals) if vals else None
 ordered=sorted(cuts);rows=[];limit=F(float(.002))
 for s in ordered+[(a+b)/2 for a,b in zip(ordered,ordered[1:])]:
  a,b=upper(original,s),upper(candidate,s);rows.append({'parameter':str(s),'originalUpperY':str(a) if a is not None else None,'candidateUpperY':str(b) if b is not None else None,'exactGapM':str(b-a) if a is not None and b is not None else None,'within2mm':a is not None and b is not None and abs(b-a)<=limit})
 for l,h in zip(ordered,ordered[1:]):
  midpoint=(l+h)/2;oa=[r for r in original if r[0]<=midpoint<=r[1]];ca=[r for r in candidate if r[0]<=midpoint<=r[1]]
  for s in [l,h]:
   a=upper(oa,s);b=upper(ca,s);rows.append({'openInterval':[str(l),str(h)],'limitParameter':str(s),'originalUpperY':str(a) if a is not None else None,'candidateUpperY':str(b) if b is not None else None,'exactGapM':str(b-a) if a is not None and b is not None else None,'within2mm':a is not None and b is not None and abs(b-a)<=limit})
 return {'passedCompleteFiniteUpperSeam':bool(rows) and all(r['within2mm'] for r in rows),'allFacetCoverageAndUpperBranchBreakpoints':list(map(str,ordered)),'completeClosedPointsAndAffineOpenIntervals':rows,'strictBandM':.002,'projectedPointOnly':bool(np.array_equal(segment[0,[0,2]],segment[1,[0,2]])),'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Every facet domain endpoint and pairwise upper-branch crossing partitions the complete segment. Both envelopes are affine within every open interval; closed endpoints and interval limits remain checked. No endpoint-only or lower-branch seam credit.'}
