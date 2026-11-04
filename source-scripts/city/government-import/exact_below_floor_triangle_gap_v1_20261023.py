"""Exact finite column gap restricted to source Y <= the stated floor.

A nonnegative slack adds the source-height half-space to both triangles'
finite barycentric constraints. Every basic feasible polytope vertex is
accounted; no rounded clipping coordinates or tolerance are used.
"""
from fractions import Fraction as F
from itertools import combinations
import hashlib
import numpy as np
from exact_original_triangle_pair_column_gap_20261010 import rref


def verify(source,ground,ceiling=1.2):
    a=np.asarray(source,float);b=np.asarray(ground,float)
    assert a.shape==b.shape==(3,3)and np.isfinite(a).all()and np.isfinite(b).all()
    limit=F(float(ceiling));s=[[F(float(v))for v in p]for p in a];g=[[F(float(v))for v in p]for p in b]
    original=[[F(1)]*3+[F(0)]*4+[F(1)], [F(0)]*3+[F(1)]*3+[F(0),F(1)],
              *[[s[j][axis]for j in range(3)]+[-g[j][axis]for j in range(3)]+[F(0),F(0)]for axis in [0,2]],
              [s[j][1]for j in range(3)]+[F(0)]*3+[F(1),limit]]
    independent,_=rref(original);vertices={}
    if independent is not None:
        rank=len(independent)
        for columns in combinations(range(7),rank):
            reduced,pivots=rref([[row[j]for j in columns]+[row[-1]]for row in independent])
            if reduced is None or len(pivots)!=rank:continue
            values=[F(0)]*7
            for k,row in enumerate(reduced):values[columns[pivots[k]]]=row[-1]
            if any(x<0 for x in values):continue
            assert all(sum(c*x for c,x in zip(row[:-1],values))==row[-1]for row in original)
            sp=tuple(sum(values[j]*s[j][axis]for j in range(3))for axis in range(3));gp=tuple(sum(values[j+3]*g[j][axis]for j in range(3))for axis in range(3))
            assert sp[0]==gp[0]and sp[2]==gp[2]and sp[1]<=limit and values[6]==limit-sp[1]
            vertices[tuple(values)]=dict(exactSourceWeights=[str(v)for v in values[:3]],exactGroundWeights=[str(v)for v in values[3:6]],exactHeightSlackM=str(values[6]),exactSourcePoint=[str(v)for v in sp],exactGroundPoint=[str(v)for v in gp],exactGapM=str(sp[1]-gp[1]))
    records=list(vertices.values());minimum=min((F(r['exactGapM'])for r in records),default=None)
    return dict(contract='exact-finite-subfloor-column-gap-v1',sourceFaceSHA256=hashlib.sha256(a.tobytes()).hexdigest(),groundFaceSHA256=hashlib.sha256(b.tobytes()).hexdigest(),exactSourceHeightCeilingM=str(limit),allExactBasicFeasibleColumnVertices=records,exactClosedHorizontalProjectionsMeet=bool(records),exactMinimumFiniteColumnGapM=str(minimum)if minimum is not None else None,noToleranceOrBufferCredit=True,sourcePlaneInversionUsed=False,installationApproved=False)
