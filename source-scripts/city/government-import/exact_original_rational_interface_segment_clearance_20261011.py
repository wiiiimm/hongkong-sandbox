"""Finite ground clearance of an unchanged exact rational contact segment.

Retains exact source intersection coordinates (no float round trip). Every
finite noncollapsed ground triangle contributes a closed parameter interval;
all affine gap endpoints bound its entire piece. Collapsed projections receive
only conservative max-height accounting. No support/root/acceptance credit.
"""
from fractions import Fraction as F
import hashlib,json,numpy as np

def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def rational(v):
 assert isinstance(v,(str,F,int)) and not isinstance(v,bool),'Exact rational coordinates, never rounded floats'
 return F(v)
def verify(endpoints,ground):
 assert len(endpoints)==2 and all(len(p)==3 for p in endpoints)
 a,b=[tuple(rational(v)for v in p)for p in endpoints];assert a!=b,'Positive-length original interface required'
 terrain=np.asarray(ground,float);assert terrain.ndim==3 and terrain.shape[1:]==(3,3) and len(terrain) and np.isfinite(terrain).all()
 ranges=[];pieces=[];gaps=[]
 def at(t):return tuple(a[i]+t*(b[i]-a[i])for i in range(3))
 def interval(constraints):
  lo,hi=F(0),F(1)
  for start,slope in constraints:
   if not slope:
    if start<0:return None
   elif slope>0:lo=max(lo,-start/slope)
   else:hi=min(hi,-start/slope)
  return (lo,hi)if lo<=hi else None
 for i,raw in enumerate(terrain):
  p,q,r=[tuple(F(float(x))for x in v)for v in raw];area=(q[0]-p[0])*(r[2]-p[2])-(q[2]-p[2])*(r[0]-p[0])
  if not area:
   # Conservative closed projected AABB even for a point/line terrain actor.
   lo=[min(v[k]for v in [p,q,r])for k in [0,2]];hi=[max(v[k]for v in [p,q,r])for k in [0,2]];cs=[]
   for axis,l,h in zip([0,2],lo,hi):cs.extend([(a[axis]-l,b[axis]-a[axis]),(h-a[axis],a[axis]-b[axis])])
   covered=interval(cs)
   if covered is None:continue
   left,right=covered;maximum=max(v[1]for v in [p,q,r]);gap=min(at(left)[1],at(right)[1])-maximum;gaps.append(gap);pieces.append(dict(groundFace=i,collapsedProjectionConservative=True,projectionCoverageCredit=False,exactParameterInterval=list(map(str,covered)),exactMinimumGapM=str(gap)));continue
  tri=[p,q,r]if area>0 else[p,r,q];cs=[]
  for u,v in zip(tri,tri[1:]+tri[:1]):
   side=lambda x:(v[0]-u[0])*(x[2]-u[2])-(v[2]-u[2])*(x[0]-u[0]);start,end=side(a),side(b);cs.append((start,end-start))
  covered=interval(cs)
  if covered is None:continue
  left,right=covered;ranges.append(covered)
  u=[q[k]-p[k]for k in range(3)];v=[r[k]-p[k]for k in range(3)];n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]);assert n[1]
  points=[at(t)for t in covered];heights=[p[1]-(n[0]*(x[0]-p[0])+n[2]*(x[2]-p[2]))/n[1]for x in points];values=[x[1]-h for x,h in zip(points,heights)];gap=min(values);gaps.append(gap);pieces.append(dict(groundFace=i,exactParameterInterval=list(map(str,covered)),exactEndpointSourcePoints=[[str(v)for v in x]for x in points],exactEndpointGroundHeights=list(map(str,heights)),exactMinimumGapM=str(gap)))
 reach=F(0);holes=[]
 for left,right in sorted(ranges):
  if left>reach:holes.append([str(reach),str(left)]);break
  reach=max(reach,right)
 covered=bool(ranges)and reach>=1 and not holes;minimum=min(gaps)if gaps else None
 return dict(contract='exact-original-rational-positive-interface-segment-finite-clearance-diagnostic-v1',exactEndpoints=[[str(v)for v in p]for p in [a,b]],completeFiniteGroundFacesAccounted=len(terrain),completeGroundSHA256=hashlib.sha256(terrain.tobytes()).hexdigest(),exactInterfaceSHA256=canonical([[str(v)for v in p]for p in[a,b]]),allFinitePieces=pieces,closedWholeSegmentProjectionCovered=covered,exactCoveredParameterThrough=str(reach),firstExactParameterGaps=holes,exactMinimumGapM=str(minimum)if minimum is not None else None,strictlyExposedWholePositiveInterface=covered and minimum is not None and minimum>0,noFloatIntersectionCoordinateRoundTrip=True,rootOrContactCredit=False,fullAcceptance=False,geometryChanges=0)
