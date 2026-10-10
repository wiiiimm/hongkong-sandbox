"""Exact finite same-XZ triangle-pair vertical gap, including collapsed facets.

A bounded linear polytope of BOTH original triangles' barycentric weights
requires equal X and Z and each triple summing to one. Every basic feasible
vertex is enumerated by exact rational elimination. Minimising sourceY-groundY
there proves the finite column gap without global unrelated height extrema,
plane inversion, omitted facets, buffers or a changed clearance threshold.
Diagnostic only; complete projection/ground coverage is independently required.
"""
from fractions import Fraction as F
from itertools import combinations
import hashlib,numpy as np

def rref(matrix):
 rows=[list(r) for r in matrix];n=len(rows);m=len(rows[0])-1;pivots=[];cursor=0
 for col in range(m):
  pivot=next((j for j in range(cursor,n) if rows[j][col]),None)
  if pivot is None:continue
  rows[cursor],rows[pivot]=rows[pivot],rows[cursor];d=rows[cursor][col];rows[cursor]=[x/d for x in rows[cursor]]
  for j in range(n):
   if j!=cursor and rows[j][col]:
    factor=rows[j][col];rows[j]=[x-factor*y for x,y in zip(rows[j],rows[cursor])]
  pivots.append(col);cursor+=1
  if cursor==n:break
 if any(not any(r[:-1]) and r[-1] for r in rows):return None,None
 return rows[:cursor],pivots

def verify(source,ground):
 a=np.asarray(source,float);b=np.asarray(ground,float);assert a.shape==b.shape==(3,3) and np.isfinite(a).all() and np.isfinite(b).all();s=[[F(float(v)) for v in p] for p in a];g=[[F(float(v)) for v in p] for p in b]
 original=[[F(1),F(1),F(1),F(0),F(0),F(0),F(1)],[F(0),F(0),F(0),F(1),F(1),F(1),F(1)],*[ [s[j][axis] for j in range(3)]+[-g[j][axis] for j in range(3)]+[F(0)] for axis in [0,2]]]
 independent,_=rref(original);vertices={}
 if independent is not None:
  rank=len(independent)
  for columns in combinations(range(6),rank):
   reduced,pivots=rref([[row[j] for j in columns]+[row[-1]] for row in independent])
   if reduced is None or len(pivots)!=rank:continue
   values=[F(0)]*6
   for k,row in enumerate(reduced):values[columns[pivots[k]]]=row[-1]
   if any(x<0 for x in values):continue
   assert all(sum(c*x for c,x in zip(row[:-1],values))==row[-1] for row in original)
   source_point=tuple(sum(values[j]*s[j][axis] for j in range(3)) for axis in range(3));ground_point=tuple(sum(values[j+3]*g[j][axis] for j in range(3)) for axis in range(3));assert source_point[0]==ground_point[0] and source_point[2]==ground_point[2];gap=source_point[1]-ground_point[1];vertices[tuple(values)]=dict(exactSourceBarycentricWeights=[str(x) for x in values[:3]],exactGroundBarycentricWeights=[str(x) for x in values[3:]],exactSourcePoint=[str(x) for x in source_point],exactGroundPoint=[str(x) for x in ground_point],exactGapM=str(gap))
 records=list(vertices.values());minimum=min((F(r['exactGapM']) for r in records),default=None)
 return dict(contract='exact-original-finite-same-XZ-triangle-pair-column-gap-diagnostic-v1',sourceFaceSHA256=hashlib.sha256(a.tobytes()).hexdigest(),groundFaceSHA256=hashlib.sha256(b.tobytes()).hexdigest(),exactColumnConstraintRank=len(independent) if independent is not None else None,allExactBasicFeasibleColumnVertices=records,exactClosedHorizontalProjectionsMeet=bool(records),exactMinimumFiniteColumnGapM=str(minimum) if minimum is not None else None,noGroundOrSourceFaceOmitted=True,sourcePlaneInversionUsed=False,noToleranceOrBufferCredit=True,geometryChanges=0,rootOrContactCredit=False,fullAcceptance=False,installationApproved=False)
