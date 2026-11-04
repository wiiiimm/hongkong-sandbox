"""Exact saved-source geometric minimum-level edge context, no support/role credit."""
from fractions import Fraction as Q
import numpy as np
from exact_original_finite_triangle_contacts_20261010 import dimension,finite_intersection_points
from exact_original_shell_intersections_20261009 import rational_face

def closed_interval_account(intervals,points):
 merged=[]
 for lo,hi in sorted(intervals):
  assert Q(0)<=lo<hi<=Q(1)
  if merged and lo<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],hi)
  else:merged.append([lo,hi])
 assert all(Q(0)<=v<=Q(1) for v in points)
 return {'positiveClosedIntervals':[[str(lo),str(hi)] for lo,hi in merged],
         'pointOnlyContactParameters':sorted(set(map(str,points))),
         'entireEdgeExactPositiveDimensionalContact':merged==[[Q(0),Q(1)]],
         'structuralSupportAccepted':False}

def lower_level_edge_context(tower,podium,heartbeat=lambda:None):
 # A geometric level only, not inferred foundation, underside or support role.
 tower,podium=np.asarray(tower,dtype=float),np.asarray(podium,dtype=float)
 level=float(tower[:,:,1].min());edges={};zeros=[]
 for face,tri in enumerate(tower):
  q=rational_face(tri)
  if dimension(q)!=2:zeros.append(face);continue
  for i in range(3):
   a,b=q[i],q[(i+1)%3]
   if a!=b and a[1]==b[1]==Q(level):edges.setdefault(tuple(sorted((a,b))),set()).add(face)
 qpod={};lo,hi=podium.min(1),podium.max(1);records=[]
 for index,((a,b),incident) in enumerate(sorted(edges.items())):
  heartbeat();axes=max(range(3),key=lambda k:abs(b[k]-a[k]));delta=b[axes]-a[axes];assert delta
  edge=np.asarray([[float(v) for v in a],[float(v) for v in b]])
  candidates=np.flatnonzero(np.all(hi>=edge.min(0),axis=1)&np.all(lo<=edge.max(0),axis=1))
  intervals=[];points=[];contacts=[]
  for j in candidates:
   j=int(j)
   if j not in qpod:qpod[j]=rational_face(podium[j])
   vertices=finite_intersection_points([a,b,b],qpod[j])
   if not vertices:continue
   params=sorted((v[axes]-a[axes])/delta for v in vertices);assert all(Q(0)<=t<=Q(1) for t in params)
   if params[0]<params[-1]:intervals.append((params[0],params[-1]))
   else:points.append(params[0])
   contacts.append({'podiumOriginalFaceId':j,'exactPoints':[[str(x) for x in v] for v in sorted(vertices)],'parameters':[str(t) for t in params],'pointOrSegmentOnly':True})
  records.append({'originalEndpoints':[[str(v) for v in a],[str(v) for v in b]],'towerIncidentOriginalFaceIds':sorted(incident),'completeCandidatePodiumFaceIds':candidates.tolist(),'contacts':contacts,**closed_interval_account(intervals,points)})
 return {'geometricMinimumOriginalY':level,'completeMinimumLevelNonzeroEdges':records,'nonrenderingTowerFacesRetainedUncredited':zeros,'hasNonemptyMinimumLevelEdges':bool(records),'wholeEdgesWithoutCompleteExactContact':[i for i,r in enumerate(records) if not r['entireEdgeExactPositiveDimensionalContact']],'pointContactsProvideNoBridge':True,'noArchitecturalLevelRole':True,'structuralSupportAccepted':False}
