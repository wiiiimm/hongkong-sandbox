"""Exact bounded segment arrangement context; cycles never imply terrain approval."""
from fractions import Fraction as F
from collections import defaultdict
import math

def point(p):
 assert len(p)==3,'Malformed3Dpoint'
 out=[]
 for x in p:
  if isinstance(x,float):assert math.isfinite(x),'Nonfinite coordinate'
  try:out.append(F(x))
  except (ValueError,OverflowError,ZeroDivisionError):raise AssertionError('Nonfinite or malformed rational coordinate')
 return tuple(out)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def at(a,u,t):return tuple(x+t*y for x,y in zip(a,u))
def parameter(a,b,p):
 u=sub(b,a);assert any(u),'Zero-length original segment'
 k=next(k for k in range(3)if u[k]);t=(p[k]-a[k])/u[k]
 return t if 0<=t<=1 and at(a,u,t)==p else None

def intersect(a,b,c,d):
 a,b,c,d=map(point,[a,b,c,d]);u,v,w=sub(b,a),sub(d,c),sub(c,a);assert any(u)and any(v),'Zero-length segment'
 axes=[(i,j)for i in range(3)for j in range(i+1,3)]
 for i,j in axes:
  det=u[j]*v[i]-u[i]*v[j]
  if det:
   t=(w[j]*v[i]-w[i]*v[j])/det;s=(u[i]*w[j]-u[j]*w[i])/det
   if 0<=t<=1 and 0<=s<=1 and at(a,u,t)==at(c,v,s):return dict(kind='exact-point-incidence',points=[at(a,u,t)])
   return dict(kind='disjoint')
 k=next(k for k in range(3)if u[k]);tc=(c[k]-a[k])/u[k];td=(d[k]-a[k])/u[k]
 if at(a,u,tc)!=c or at(a,u,td)!=d:return dict(kind='disjoint')
 lo,hi=max(F(0),min(tc,td)),min(F(1),max(tc,td))
 if lo>hi:return dict(kind='disjoint')
 if lo==hi:return dict(kind='exact-point-incidence',points=[at(a,u,lo)])
 return dict(kind='positive-collinear-overlap',points=[at(a,u,lo),at(a,u,hi)])

def network(segments):
 segments=[tuple(map(point,s))for s in segments];assert all(len(s)==2 and s[0]!=s[1]for s in segments);assert len(segments)<=256,'Bounded existing locus inventory; no expansion'
 cuts=[{F(0),F(1)}for s in segments];pairs=[];paircount=0
 for i,(a,b)in enumerate(segments):
  for j in range(i+1,len(segments)):
   paircount+=1;c,d=segments[j];r=intersect(a,b,c,d)
   if r['kind']=='disjoint':continue
   for p in r['points']:
    ti,tj=parameter(a,b,p),parameter(c,d,p);assert ti is not None and tj is not None;cuts[i].add(ti);cuts[j].add(tj)
   pairs.append(dict(segmentA=i,segmentB=j,**r))
 atomic=defaultdict(list)
 for i,(a,b)in enumerate(segments):
  ts=sorted(cuts[i]);u=sub(b,a)
  for lo,hi in zip(ts,ts[1:]):
   assert lo<hi;p,q=at(a,u,lo),at(a,u,hi);atomic[tuple(sorted((p,q)))].append(dict(segment=i,exactInterval=[lo,hi]))
 graph=defaultdict(set)
 for a,b in atomic:graph[a].add(b);graph[b].add(a)
 seen=set();components=[]
 for a in graph:
  if a in seen:continue
  todo=[a];vertices=set()
  while todo:
   b=todo.pop()
   if b in vertices:continue
   vertices.add(b);todo.extend(graph[b]-vertices)
  seen.update(vertices);edges=sum(len(graph[v])for v in vertices)//2;rank=edges-len(vertices)+1
  components.append(dict(vertices=sorted(vertices),atomicEdges=edges,cycleRank=rank,allDegreeTwo=all(len(graph[v])==2 for v in vertices)))
 return dict(completeSegmentPairCount=paircount,exactPairIncidences=pairs,atomicEdges=[dict(endpoints=e,sourceSegmentIncidences=v)for e,v in atomic.items()],components=components,positiveOverlapPairs=sum(p['kind']=='positive-collinear-overlap'for p in pairs),cycleRank=sum(c['cycleRank']for c in components),sourceContextOnly=True,qualifiedTerrainFrontier=False)
