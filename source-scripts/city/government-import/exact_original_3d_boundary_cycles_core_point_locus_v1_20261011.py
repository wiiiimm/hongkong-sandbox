"""DRAFT full positive-edge component boundary cycles + exact core local cones."""
from collections import defaultdict
from fractions import Fraction as F
from functools import cmp_to_key
from math import gcd,lcm
from exact_original_projection_coverage_v2_20261010 import signed_area,cross

def cycles(atoms,face_count):
 parent=list(range(face_count))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for r in atoms:
  inc=r['allDirectedIncidences'];assert inc and r['incidenceCount']==len(inc)and all(0<=e['face']<face_count for e in inc)
  for e in inc:assert tuple(sorted((tuple(e['start']),tuple(e['end']))))==tuple(tuple(p)for p in r['exactEndpoints'])and tuple(e['start'])!=tuple(e['end'])
  for e in inc[1:]:
   a,b=find(inc[0]['face']),find(e['face'])
   if a!=b:parent[max(a,b)]=min(a,b)
 comps=defaultdict(list)
 for i in range(face_count):comps[find(i)].append(i)
 roots=sorted(comps);label={r:i for i,r in enumerate(roots)};by=defaultdict(list)
 for i,r in enumerate(atoms):
  if r['incidenceCount']==1:by[label[find(r['allDirectedIncidences'][0]['face'])]].append(i)
 result=[]
 for k,root in enumerate(roots):
  ids=by[k];out=defaultdict(list);incoming=defaultdict(list)
  for i in ids:
   e=atoms[i]['allDirectedIncidences'][0];a,b=tuple(e['start']),tuple(e['end']);assert a!=b;out[a].append(i);incoming[b].append(i)
  vertices=sorted(set(out)|set(incoming));branch=[dict(exactVertex=p,incomingAtoms=incoming[p],outgoingAtoms=out[p])for p in vertices if len(incoming[p])!=1 or len(out[p])!=1];loops=[];visited=set()
  if not branch:
   for first in ids:
    if first in visited:continue
    current=first;loop=[]
    while current not in visited:
     visited.add(current);loop.append(current);e=atoms[current]['allDirectedIncidences'][0];current=out[tuple(e['end'])][0]
    assert current==first and len(loop)>=3,'Genuine complete simple directed cycle required';loops.append(dict(allOrderedAtomicEdgeIds=loop,allExactOrderedVertices=[atoms[i]['allDirectedIncidences'][0]['start']for i in loop]))
   assert visited==set(ids)
  result.append(dict(positiveEdgeComponent=k,allOriginalAndGeneratedFaceIds=comps[root],allPositiveBoundaryAtomIds=ids,allBoundaryVertexBranchOrOpenDegreeFailures=branch,allCompleteSimpleDirected3DCycles=loops,completeBoundaryCyclePartitionQualified=not branch,pointContactsDoNotMergeComponents=True))
 return result

def ray(v):
 a,b=map(F,v);assert a or b;d=lcm(a.denominator,b.denominator);x,y=int(a*d),int(b*d);g=gcd(abs(x),abs(y));return(x//g,y//g)
def angular_compare(a,b):
 half=lambda p:0 if p[1]>0 or p[1]==0 and p[0]>0 else 1
 if half(a)!=half(b):return -1 if half(a)<half(b)else 1
 z=a[0]*b[1]-a[1]*b[0];return -1 if z>0 else 1 if z<0 else 0

def core_point_locus(p,polygons,original_ids=None):
 p=tuple(map(F,p));assert len(p)==2;ids=list(range(len(polygons)))if original_ids is None else original_ids;assert len(ids)==len(polygons);cones=[];strict=[]
 for i,poly in zip(ids,polygons):
  t=[tuple(map(F,q))for q in poly];assert len(t)==3 and signed_area(t)!=0
  if signed_area(t)<0:t.reverse()
  signs=[cross(a,b,p)for a,b in zip(t,t[1:]+t[:1])]
  if any(v<0 for v in signs):continue
  active=[(b[0]-a[0],b[1]-a[1])for (a,b),v in zip(zip(t,t[1:]+t[:1]),signs)if v==0];cones.append(dict(originalCoreFace=i,allExactActiveOrientedHalfplaneDirections=active))
  if not active:strict.append(i)
 if not cones:return dict(location='outside-closed-core',allClosedContainingOriginalCoreFaces=[],allContainingFacetTangentCones=[],allAtomicDirectionConeTests=[],exactFiniteUnionLocalNeighborhoodCovered=False)
 if strict:return dict(location='interior-core',allClosedContainingOriginalCoreFaces=[r['originalCoreFace']for r in cones],allContainingFacetTangentCones=cones,allAtomicDirectionConeTests=[],strictContainingOriginalCoreFaces=strict,exactFiniteUnionLocalNeighborhoodCovered=True)
 rays=sorted({v for r in cones for e in r['allExactActiveOrientedHalfplaneDirections']for v in[ray(e),ray((-e[0],-e[1]))]},key=cmp_to_key(angular_compare));assert len(rays)>=2;tests=[]
 def covered(v):return[r['originalCoreFace']for r in cones if all(e[0]*v[1]-e[1]*v[0]>=0 for e in r['allExactActiveOrientedHalfplaneDirections'])]
 for a,b in zip(rays,rays[1:]+rays[:1]):
  m=(a[0]+b[0],a[1]+b[1]);m=(-a[1],a[0])if m==(0,0)else m;tests.append(dict(exactBoundaryRay=a,allRayCoveringOriginalCoreFaces=covered(a),nextExactBoundaryRay=b,exactOpenSectorWitness=m,allOpenSectorCoveringOriginalCoreFaces=covered(m)))
 interior=all(r['allRayCoveringOriginalCoreFaces']and r['allOpenSectorCoveringOriginalCoreFaces']for r in tests)
 return dict(location='interior-core'if interior else'exterior-boundary-of-closed-core',allClosedContainingOriginalCoreFaces=[r['originalCoreFace']for r in cones],allContainingFacetTangentCones=cones,allAtomicDirectionConeTests=tests,exactFiniteUnionLocalNeighborhoodCovered=interior,completeFiniteActiveHalfplaneRayArrangement=True,noRadiusEpsilonOrBuffer=True)
