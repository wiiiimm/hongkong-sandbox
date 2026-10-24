"""Exact interpretation of complete saved affine segment pieces; no geometry edits."""
from fractions import Fraction as Q
from exact_original_shell_intersections_20261009 import sub,cross
from exact_original_finite_triangle_contacts_20261010 import point_in_triangle

def rational(v):
 assert isinstance(v,(str,int,Q))and not isinstance(v,bool),'Exact rational values required'
 return Q(v)
def point(v):
 assert len(v)==3
 return tuple(rational(x)for x in v)
def at(a,b,t):return tuple(a[k]+t*(b[k]-a[k])for k in range(3))
def source_segment(face,endpoints):
 assert len(face)==3 and len(endpoints)==2
 f=tuple(point(v)for v in face);a,b=map(point,endpoints);assert a!=b,'No point bridge';assert any(cross(sub(f[1],f[0]),sub(f[2],f[0]))),'Nonzero source facet required'
 assert point_in_triangle(a,f)and point_in_triangle(b,f),'Both endpoints must be in the exact original source facet'
 return dict(exactSourceFacet=[list(map(str,p))for p in f],exactEndpoints=[list(map(str,p))for p in [a,b]],closedConvexOriginalFacetContainment=True,noGeometryChange=True)

def classify(wrapper,*,expected_ground_sha,expected_ground_faces,expected_endpoints):
 s=wrapper['selection'];p=wrapper['selectedGroundKernelProof'];assert s['completeGroundSHA256']==expected_ground_sha and s['completeGroundFacetCount']==expected_ground_faces and s['everyNoncandidateStrictlyDisjoint']and s['touchingAndCollapsedProjectionsRetained']
 assert p and wrapper['closedWholeSegmentProjectionCovered']and p['closedWholeSegmentProjectionCovered'],'Complete closed coverage required'
 a,b=map(point,p['exactEndpoints']);assert a!=b and [a,b]==list(map(point,expected_endpoints));ids=wrapper['originalGroundFaceBySelectedKernelFace'];assert ids==s['selectedOriginalGroundFaces']and len(ids)==p['completeFiniteGroundFacesAccounted']and ids==sorted(set(ids))and all(type(i)is int and 0<=i<expected_ground_faces for i in ids);cuts={Q(0),Q(1)};rows=[];ranges=[];all_gaps=[]
 for i in p['allFinitePieces']:
  assert not i.get('collapsedProjectionConservative'),'Do not reinterpret a collapsed conservative piece as an affine finite plane'
  j=i['groundFace'];assert type(j)is int and 0<=j<len(ids);l,r=map(rational,i['exactParameterInterval']);assert 0<=l<=r<=1
  src=list(map(point,i['exactEndpointSourcePoints']));assert src==[at(a,b,l),at(a,b,r)],'Saved source points must match the unchanged segment and parameter interval'
  h=list(map(rational,i['exactEndpointGroundHeights']));assert len(h)==2;g0,g1=src[0][1]-h[0],src[1][1]-h[1];assert rational(i['exactMinimumGapM'])==min(g0,g1)
  if l==r:assert g0==g1
  rows.append((l,r,g0,g1,j));ranges.append((l,r));all_gaps.extend([g0,g1]);cuts.update([l,r])
  if g0!=g1:
   zero=l-g0*(r-l)/(g1-g0)
   if l<=zero<=r:cuts.add(zero)
 assert rows and min(all_gaps)==rational(p['exactMinimumGapM'])==rational(wrapper['exactMinimumGapM'])
 reach=Q(0)
 for l,r in sorted(ranges):assert l<=reach,'Missing closed coverage';reach=max(reach,r)
 assert reach==1
 def gap(t):
  active=[g0 if l==r else g0+(t-l)*(g1-g0)/(r-l)for l,r,g0,g1,j in rows if l<=t<=r];assert active;return min(active)
 ordered=sorted(cuts);cut_records=[dict(parameter=str(t),exactUpperEnvelopeGapM=str(gap(t)),strictPositive=gap(t)>0)for t in ordered];atomic=[];nominees=[]
 for l,r in zip(ordered,ordered[1:]):
  g=gap((l+r)/2);positive=g>0;atomic.append(dict(exactOpenParameterInterval=[str(l),str(r)],strictPositiveThroughoutOpenInterval=positive,midpointGapM=str(g)))
  if positive:
   u=l+(r-l)/4;v=r-(r-l)/4;nominees.append(dict(exactClosedInteriorParameterInterval=[str(u),str(v)],exactEndpoints=[list(map(str,at(a,b,t)))for t in [u,v]],representativePoint=list(map(str,at(a,b,(u+v)/2)))))
 fully_buried=all(gap(t)<0 for t in ordered)and all(gap((l+r)/2)<0 for l,r in zip(ordered,ordered[1:]))
 # Gap sign cannot change inside an atom: every active affine zero and every
 # closed finite coverage boundary is explicitly in the cut set.
 except_start=all(gap(t)>0 for t in ordered if t>0)and all(x['strictPositiveThroughoutOpenInterval']for x in atomic)
 return dict(exactEndpoints=p['exactEndpoints'],completeGroundSHA256=expected_ground_sha,completeGroundFaces=expected_ground_faces,allSavedFinitePiecesPreserved=True,exactCutRecords=cut_records,completeAtomicOpenIntervals=atomic,positiveLengthExposedNominees=nominees,fullyStrictlyBuried=fully_buried,noPositiveLengthExposedComponent=not nominees,isolatedStrictPositiveCutPoints=[x for n,x in enumerate(cut_records)if x['strictPositive']and not((n>0 and atomic[n-1]['strictPositiveThroughoutOpenInterval'])or(n<len(atomic)and atomic[n]['strictPositiveThroughoutOpenInterval']))],strictPositiveExceptInitialEndpoint=except_start,initialEndpointGapM=str(gap(Q(0))),wholeEdgePredicateUnchanged=True,sourceGeometryChanges=0,rootOrPhysicalCredit=False)
