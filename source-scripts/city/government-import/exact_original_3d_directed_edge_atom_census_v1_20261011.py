"""DRAFT genuine exact3D original vertex/T-junction edge atoms; no point bridge."""
from collections import defaultdict
from fractions import Fraction as F
import math
from itertools import product
from exact_original_shell_intersections_20261009 import cross,sub

def point(p):
 assert len(p)==3
 for v in p:
  if isinstance(v,float):assert math.isfinite(v)
 return tuple(F(v)for v in p)
def at(a,b,t):return tuple(a[i]+t*(b[i]-a[i])for i in range(3))
def parameter(a,b,p):
 delta=sub(b,a);assert any(delta)
 axis=max(range(3),key=lambda i:abs(delta[i]));t=(p[axis]-a[axis])/delta[axis]
 return t if 0<=t<=1 and at(a,b,t)==p else None

def census(triangles,checkpoints=None):
 faces=[tuple(point(p)for p in f)for f in triangles];assert all(len(f)==3 for f in faces);edges=[];zero=[]
 for i,f in enumerate(faces):
  if not any(cross(sub(f[1],f[0]),sub(f[2],f[0]))):zero.append(i);continue
  for a,b in zip(f,f[1:]+f[:1]):assert a!=b;edges.append(dict(face=i,start=a,end=b))
 points=sorted({p for e in edges for p in[e['start'],e['end']]});buckets=defaultdict(list)
 for p in points:buckets[tuple(v//5 for v in p)].append(p)
 def compute(part):
  rows=[]
  for i in part:
   e=edges[i];a,b=e['start'],e['end'];cuts={F(0),F(1)};ranges=[range(min(a[k],b[k])//5,max(a[k],b[k])//5+1)for k in range(3)];examined=0
   for cell in product(*ranges):
    for p in buckets[cell]:
     examined+=1;t=parameter(a,b,p)
     if t is not None:cuts.add(t)
   rows.append(dict(edge=i,allExactOrderedCutParameters=sorted(cuts),closedExactBucketNominatedPoints=examined))
  return rows
 plan=list(range(len(edges)));rows=checkpoints.map('complete-source3d-directed-edge-cuts',plan,compute)if checkpoints else compute(plan);assert [r['edge']for r in rows]==plan;atoms=defaultdict(list)
 for r in rows:
  e=edges[r['edge']];cuts=r['allExactOrderedCutParameters'];assert cuts[0]==0 and cuts[-1]==1 and all(a<b for a,b in zip(cuts,cuts[1:]));parts=[]
  for lo,hi in zip(cuts,cuts[1:]):
   a,b=at(e['start'],e['end'],lo),at(e['start'],e['end'],hi);assert a!=b;atoms[tuple(sorted((a,b)))].append(dict(face=e['face'],sourceDirectedEdge=r['edge'],start=a,end=b,exactSourceEdgeInterval=[lo,hi]));parts.append([lo,hi])
  r['allCompletePartitionIntervals']=parts
 result=[]
 for (a,b),inc in sorted(atoms.items()):
  opposed=len(inc)==2 and inc[0]['start']==inc[1]['end']and inc[0]['end']==inc[1]['start'];result.append(dict(exactEndpoints=[a,b],allDirectedIncidences=inc,incidenceCount=len(inc),exactOpposedTwoIncidences=opposed))
 return dict(completeFaces=len(faces),allExactZeroOriginalFaceIds=zero,completeNonzeroFaces=len(faces)-len(zero),allDirectedOriginalEdges=edges,allCompleteDirectedEdgeCutProofs=rows,allExact3DAtomicEdges=result,allPositive3DBoundaryAtomIds=[i for i,r in enumerate(result)if r['incidenceCount']==1],allNonmanifoldAtomIds=[i for i,r in enumerate(result)if r['incidenceCount']>2],allTwoSameDirectionAtomIds=[i for i,r in enumerate(result)if r['incidenceCount']==2 and not r['exactOpposedTwoIncidences']],pointOrCrossingIntersectionsCreateNoBridge=True,completeOriginalVertexAABBNomination=True,partialCollinearEdgesAtomizedExactly=True,currentAcceptance=False)
