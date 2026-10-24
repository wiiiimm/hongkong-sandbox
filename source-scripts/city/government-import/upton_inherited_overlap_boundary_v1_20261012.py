"""Exact completed-input diagnostics only; no terrain edits or approval writing.

Rational arithmetic operates on saved binary floats, not pre-JSON shader bytes.
MAX certificates describe the complete ideal affine envelope; JS evaluation and
sampler branch eligibility are separately pinned facts, never epsilon credit.
"""
from fractions import Fraction as F
from collections import defaultdict, deque
import hashlib
import numpy as np
from exact_original_projection_coverage_20261009 import signed_area

def points(a,shape=None):
 numeric=np.asarray(a,dtype='<f8');assert np.isfinite(numeric).all()
 if shape is not None:assert numeric.shape==shape
 return [tuple(x if isinstance(x,F)else F(float(x)) for x in p) for p in a]
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def clip(poly,line):
 if not poly:return []
 out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  a=line[0]*p[0]+line[1]*p[1]+line[2];b=line[0]*q[0]+line[1]*q[1]+line[2]
  if a>=0:out.append(p)
  if (a<0<b)or(b<0<a):out.append(tuple(p[k]+a/(a-b)*(q[k]-p[k])for k in range(2)))
 return list(dict.fromkeys(out))
def area(poly):return abs(signed_area(poly))if len(poly)>2 else F(0)
def intersection(first,second):
 # Keep previously generated rational clip vertices rational. The older public
 # float-input wrapper intentionally rebinds its inputs through binary64.
 poly=list(first);boundary=list(second);assert signed_area(boundary)!=0
 if signed_area(boundary)<0:boundary.reverse()
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):
  poly=clip(poly,(-(b[1]-a[1]),b[0]-a[0],(b[1]-a[1])*a[0]-(b[0]-a[0])*a[1]))
 return poly
def projection(face):return [(p[0],p[2])for p in points(face,(3,3))]
def plane(face):
 p,q,r=points(face,(3,3));u=sub(q,p);v=sub(r,p);d=u[0]*v[2]-u[2]*v[0]
 if d==0:return None
 a=(u[1]*v[2]-u[2]*v[1])/d;b=(u[0]*v[1]-u[1]*v[0])/d
 return a,b,p[1]-a*p[0]-b*p[2]
def height(h,p):return h[0]*p[0]+h[1]*p[1]+h[2]
def within(poly,triangle):return area(intersection(poly,triangle))==area(poly)
def exact_ranges(poly,h):
 values=[height(h,p)for p in poly];return [str(min(values)),str(max(values))]
def projected_dimension(poly):return 'area'if area(poly)>0 else 'line'if len(set(poly))>1 else 'point'if poly else 'empty'
def source_attribution(global_faces,sources):
 """Byte-geometry multiset bijection, retaining every ambiguous source identity."""
 global_faces=np.asarray(global_faces,dtype='<f8').reshape(-1,3,3)
 def key(f):return tuple(sorted(tuple(float(x)for x in p)for p in f))
 identities=defaultdict(list)
 for source in sources:
  faces=np.asarray(source['completeSelectedDrawnTriplets'],dtype='<f8').reshape(-1,3,3);ids=source['allSelectedMeshFaceIDs'];assert len(ids)==len(faces)
  assert len(set(ids))==len(ids)
  for i,f in zip(ids,faces):identities[key(f)].append(dict(sourcePath=source['sourcePath'],sourceMeshFace=int(i),sourceLineage=source['lineage'],orderedSavedFaceSHA256=sha(f)))
 queues={k:deque(v)for k,v in identities.items()};out=[]
 for i,f in enumerate(global_faces):
  k=key(f);assert k in queues and queues[k],'Missing actual source attribution'
  out.append(dict(globalCurrentFace=i,assignedMultisetOccurrence=queues[k].popleft(),allIdenticalSavedGeometrySourceAlternatives=identities[k],uniqueSourceIdentity=len(identities[k])==1,globalOrderedSavedFaceSHA256=sha(f)))
 assert all(not q for q in queues.values()),'Unconsumed captured source facets'
 return out
def overlap_pair(candidate_left,candidate_right,old_left,old_right):
 poly=intersection(projection(candidate_left),projection(candidate_right));old=intersection(projection(old_left),projection(old_right))
 hs=[plane(f)for f in [candidate_left,candidate_right,old_left,old_right]]
 result=dict(exactCandidateProjectionDimension=projected_dimension(poly),exactCandidatePairAreaM2=str(area(poly)),exactOriginalPairAreaM2=str(area(old)),exactCandidateIntersectionXZ=[[str(v)for v in p]for p in poly],exactOriginalIntersectionXZ=[[str(v)for v in p]for p in old])
 if area(poly)==0 or any(h is None for h in hs):return dict(**result,projectionInherited=False,heightInherited=False,reason='No positive-area affine pair')
 contained=within(poly,projection(old_left))and within(poly,projection(old_right));deltas=[]
 for h,o in zip(hs[:2],hs[2:]):deltas.append(exact_ranges(poly,tuple(x-y for x,y in zip(h,o))))
 return dict(**result,projectionInherited=contained,exactCandidateFullAffineHeightRanges=[exact_ranges(poly,h)for h in hs[:2]],exactOriginalAffineHeightRangesOnCandidateRegion=[exact_ranges(poly,h)for h in hs[2:]],exactPerLineageHeightDifferenceRangesM=deltas,heightInherited=contained and all(F(x)==0 for pair in deltas for x in pair),noPackingDifferenceDiscarded=True)
def complete_max_difference(poly,candidate_faces,old_faces):
 """Partition footprints, then exact winner regions: every closed vertex counted."""
 assert area(poly)>0
 groups=[];cells=[poly];omitted=[]
 for label,faces in [('candidate',candidate_faces),('current',old_faces)]:
  rows=[]
  for i,f in enumerate(faces):
   h=plane(f);p=projection(f)
   if h is None:omitted.append(dict(group=label,face=i,reason='Zero exact horizontal area'));continue
   # Actual JS Number determinant expression, separate from exact rational area.
   a,b,c=np.asarray(f,dtype='<f8');det=(float(b[2])-float(c[2]))*(float(a[0])-float(c[0]))+(float(c[0])-float(b[0]))*(float(a[2])-float(c[2]))
   if abs(det)<1e-10:omitted.append(dict(group=label,face=i,reason='Pinned runtime determinant exclusion',jsNumberDeterminant=det));continue
   if area(intersection(poly,p))==0:continue
   if signed_area(p)<0:p.reverse()
   rows.append((i,p,h))
   for a,b in zip(p,p[1:]+p[:1]):
    line=(-(b[1]-a[1]),b[0]-a[0],(b[1]-a[1])*a[0]-(b[0]-a[0])*a[1]);new=[]
    for cell in cells:
     for part in [clip(cell,line),clip(cell,tuple(-v for v in line))]:
      if area(part)>0 and part not in new:new.append(part)
    cells=new
  groups.append(rows)
 assert sum(area(c)for c in cells)==area(poly),'Incomplete footprint partition'
 output=[];missing=[]
 for cell in cells:
  mid=tuple(sum(p[k]for p in cell)/len(cell)for k in range(2));active=[]
  for rows in groups:
   active.append([(i,h)for i,p,h in rows if all((b[0]-a[0])*(mid[1]-a[1])-(b[1]-a[1])*(mid[0]-a[0])>=0 for a,b in zip(p,p[1:]+p[:1]))])
  if any(not a for a in active):missing.append([[str(v)for v in p]for p in cell]);continue
  for ci,ch in active[0]:
   for oi,oh in active[1]:
    winner=cell
    for rows,h in [(active[0],ch),(active[1],oh)]:
     for _,other in rows:winner=clip(winner,tuple(x-y for x,y in zip(h,other)))
    if area(winner)==0:continue
    dif=tuple(x-y for x,y in zip(ch,oh));output.append(dict(candidateFace=ci,currentFace=oi,exactWinnerRegionXZ=[[str(v)for v in p]for p in winner],exactFullHeightDifferenceRangeM=exact_ranges(winner,dif)))
 ranges=[F(x)for r in output for x in r['exactFullHeightDifferenceRangeM']];assert output or missing
 return dict(completeIdealAffineMaxRegionCovered=not missing,exactMaximumAbsoluteIdealAffineMaxDifferenceM=str(max(map(abs,ranges)))if ranges else None,exactIdealAffineMaxUnchanged=not missing and all(x==0 for x in ranges),allExactWinnerRegions=output,allUncoveredFootprintCells=missing,allRuntimeDeterminantExclusions=omitted,notBitwiseJSHeightEvaluationProof=True,noSamplerThresholdChanged=True)
def interval_clip(interval,constant,slope):
 lo,hi=interval
 if slope==0:return interval if constant>=0 else None
 cut=-constant/slope
 lo=max(lo,cut)if slope>0 else lo;hi=min(hi,cut)if slope<0 else hi
 return (lo,hi)if lo<=hi else None
def union_intervals(intervals):
 out=[]
 for lo,hi in sorted(intervals):
  if out and lo<=out[-1][1]:out[-1]=(out[-1][0],max(hi,out[-1][1]))
  else:out.append((lo,hi))
 return out
def segment_to_facets(segment,faces,limit):
 """Conservative whole finite 3D orthogonal-foot/edge union; never endpoint-only."""
 a,b=points(segment,(2,3));delta=sub(b,a);assert dot(delta,delta)>0,'Collapsed segment has no boundary credit'
 limit=F(limit);assert limit>=0;rows=[];intervals=[];zeros=[]
 for faceid,face in enumerate(faces):
  p,q,r=points(face,(3,3));u=sub(q,p);v=sub(r,p);uu=dot(u,u);uv=dot(u,v);vv=dot(v,v);det=uu*vv-uv*uv
  if det==0:zeros.append(faceid);continue
  maps=[];ap=sub(a,p);du=dot(delta,u);dv=dot(delta,v)
  uc=(dot(ap,u)*vv-dot(ap,v)*uv)/det;us=(du*vv-dv*uv)/det;vc=(dot(ap,v)*uu-dot(ap,u)*uv)/det;vs=(dv*uu-du*uv)/det
  iv=(F(0),F(1))
  for c,s in [(uc,us),(vc,vs),(1-uc-vc,-us-vs)]:
   iv=interval_clip(iv,c,s)if iv is not None else None
  if iv is not None:maps.append(('orthogonal-interior',iv,tuple(p[k]+uc*u[k]+vc*v[k]for k in range(3)),tuple(us*u[k]+vs*v[k]for k in range(3))))
  for edge,(p0,p1)in enumerate([(p,q),(q,r),(r,p)]):
   d=sub(p1,p0);dd=dot(d,d);assert dd>0;t0=dot(sub(a,p0),d)/dd;ts=dot(delta,d)/dd
   for name,constraints,base,slope in [('edge-interior',[(t0,ts),(1-t0,-ts)],tuple(p0[k]+t0*d[k]for k in range(3)),tuple(ts*d[k]for k in range(3))),('edge-start',[(-t0,-ts)],p0,(F(0),)*3),('edge-end',[(t0-1,ts)],p1,(F(0),)*3)]:
    iv=(F(0),F(1))
    for c,s in constraints:iv=interval_clip(iv,c,s)if iv is not None else None
    if iv is not None:maps.append((str(edge)+'/'+name,iv,base,slope))
  for branch,iv,base,slope in maps:
   distances=[]
   for t in iv:
    e=tuple(a[k]+t*delta[k]-base[k]-t*slope[k]for k in range(3));distances.append(dot(e,e))
   if max(distances)>limit*limit:continue
   intervals.append(iv);rows.append(dict(facet=faceid,branch=branch,exactClosedParameterInterval=list(map(str,iv)),exactEndpointSquaredDistancesM2=list(map(str,distances)),wholeIntervalCertifiedByConvexSquaredDistance=True))
 merged=union_intervals(intervals);complete=merged==[(F(0),F(1))]
 return dict(completeFinite3DCorrespondence=complete,exactExistingDistanceLimitM=str(limit),completeClosedParameterUnion=[list(map(str,p))for p in merged],allCompleteIntervalCertificates=rows,allExactDegenerateFacetsUncredited=zeros,notGlobalWatertightnessProof=True,noGeometryOrRootCredit=True)
