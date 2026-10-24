"""Fixed ±.1m contact band for a complete ORIGINAL edge on finite upper facets.

No tolerance expansion, synthetic cap, snapping or structural credit. Every
finite facet coverage endpoint and strict-band equality partitions the edge.
On each interval every plane's relationship to both limits is constant; the
maximum covering plane therefore stays within the band iff the witness does.
"""
from fractions import Fraction as F
import numpy as np
def verify_contact_segment(segment,surfaces,band=.1):
 assert band==.1,'Existing strict original contact band cannot change'
 line=np.asarray(segment,float);tri=np.asarray(surfaces,float)
 assert line.shape==(2,3) and tri.ndim==3 and tri.shape[1:]==(3,3) and len(tri) and np.isfinite(line).all() and np.isfinite(tri).all()
 assert not np.array_equal(line[0],line[1]),'Collapsed original edge'
 a,b=[tuple(F(float(v)) for v in p) for p in line];limit=F(float(band));cuts={F(0),F(1)};pieces=[]
 lo=line[:,[0,2]].min(axis=0);hi=line[:,[0,2]].max(axis=0)
 candidates=np.flatnonzero(np.all(tri[:,:,[0,2]].max(axis=1)>=lo,axis=1)&np.all(tri[:,:,[0,2]].min(axis=1)<=hi,axis=1))
 for k in candidates:
  p,q,r=[tuple(F(float(v)) for v in x) for x in tri[k]];den=(q[2]-r[2])*(p[0]-r[0])+(r[0]-q[0])*(p[2]-r[2])
  if not den:continue
  def bary(v):
   u=((q[2]-r[2])*(v[0]-r[0])+(r[0]-q[0])*(v[2]-r[2]))/den;w=((r[2]-p[2])*(v[0]-r[0])+(p[0]-r[0])*(v[2]-r[2]))/den;return u,w,1-u-w
  aa,bb=bary(a),bary(b);left,right=F(0),F(1)
  for x,y in zip(aa,bb):
   slope=y-x
   if not slope:
    if x<0:left,right=F(1),F(0);break
   elif slope>0:left=max(left,-x/slope)
   else:right=min(right,-x/slope)
  if left>right:continue
  h0=sum(v*f[1] for v,f in zip(aa,[p,q,r]));h1=sum(v*f[1] for v,f in zip(bb,[p,q,r]));gap0=a[1]-h0;gap1=b[1]-h1
  cuts.update([left,right])
  if gap0!=gap1:
   for bound in [-limit,limit]:
    crossing=(bound-gap0)/(gap1-gap0)
    if left<=crossing<=right:cuts.add(crossing)
  pieces.append(dict(originalSurfaceFace=int(k),left=left,right=right,h0=h0,h1=h1))
 def upper_gap(s):
  y=a[1]+s*(b[1]-a[1]);values=[r['h0']+s*(r['h1']-r['h0']) for r in pieces if r['left']<=s<=r['right']]
  return y-max(values) if values else None
 ordered=sorted(cuts);points=[dict(exactParameter=str(s),exactUpperGapM=str(gap) if (gap:=upper_gap(s)) is not None else None,withinFixedContactBand=gap is not None and -limit<=gap<=limit) for s in ordered]
 intervals=[]
 for l,r in zip(ordered,ordered[1:]):
  if l==r:continue
  s=(l+r)/2;gap=upper_gap(s);intervals.append(dict(exactOpenParameterInterval=[str(l),str(r)],exactMidpointParameter=str(s),exactUpperGapAtWitnessM=str(gap) if gap is not None else None,completeFiniteCoverage=gap is not None,withinFixedContactBand=gap is not None and -limit<=gap<=limit))
 verified=bool(intervals) and all(r['withinFixedContactBand'] for r in points+intervals)
 return dict(contract='exact-original-edge-upper-source-surface-fixed-contact-band-v1',verifiedCompleteOriginalEdgeContactBand=verified,strictBandM=.1,completeFiniteCoverage=all(r['completeFiniteCoverage'] for r in intervals) and all(r['exactUpperGapM'] is not None for r in points),exactOriginalEdge=[[str(v) for v in p] for p in [a,b]],completeOriginalSurfacePieces=[{k:str(v) if isinstance(v,F) else v for k,v in p.items()} for p in pieces],exactBandAndCoverageBreakpoints=points,certifiedOpenIntervals=intervals,continuousBandCertified=True,endpointOnlyAcceptance=False,sourceGeometryChanges=0,structuralRootCredit=False,installationApproved=False)
