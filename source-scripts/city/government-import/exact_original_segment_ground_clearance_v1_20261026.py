"""Exact finite original segment/ground clearance with complete parameter coverage."""
from fractions import Fraction as F
from itertools import combinations
import numpy as np
from exact_original_triangle_pair_column_gap_20261010 import rref


def pair(segment,ground):
    s=[[F(x)for x in p]for p in segment];g=[[F(float(x))for x in p]for p in ground]
    assert len(s)==2 and len(g)==3 and all(len(p)==3 for p in s+g)
    matrix=[[F(1),F(1),F(0),F(0),F(0),F(1)],[F(0),F(0),F(1),F(1),F(1),F(1)],*[ [s[j][axis]for j in range(2)]+[-g[j][axis]for j in range(3)]+[F(0)]for axis in [0,2]]]
    independent,_=rref(matrix);vertices={}
    if independent is None:return None
    rank=len(independent)
    for columns in combinations(range(5),rank):
        reduced,pivots=rref([[row[j]for j in columns]+[row[-1]]for row in independent])
        if reduced is None or len(pivots)!=rank:continue
        values=[F(0)]*5
        for k,row in enumerate(reduced):values[columns[pivots[k]]]=row[-1]
        if any(x<0 for x in values):continue
        assert all(sum(c*x for c,x in zip(row[:-1],values))==row[-1]for row in matrix)
        gap=sum(values[j]*s[j][1]for j in range(2))-sum(values[j+2]*g[j][1]for j in range(3));vertices[tuple(values)]=(values[1],gap)
    if not vertices:return None
    points=list(vertices.values())
    return dict(parameterInterval=[str(min(p[0]for p in points)),str(max(p[0]for p in points))],minimumGapM=str(min(p[1]for p in points)),maximumGapM=str(max(p[1]for p in points)))


def verify(segment,ground):
    assert len(segment)==2
    exact=[[F(x)for x in p]for p in segment];assert all(len(p)==3 for p in exact)
    terrain=np.asarray(ground,dtype='<f8');assert terrain.ndim==3 and terrain.shape[1:]==(3,3)and np.isfinite(terrain).all()
    # Outward rounding provides a conservative float broad phase; all feasible
    # finite relations and interval unions are then computed with rationals.
    lo=np.nextafter(np.asarray([float(min(p[a]for p in exact))for a in [0,2]]),-np.inf);hi=np.nextafter(np.asarray([float(max(p[a]for p in exact))for a in [0,2]]),np.inf)
    ids=np.flatnonzero(np.all(terrain[:,:,[0,2]].max(1)>=lo,axis=1)&np.all(terrain[:,:,[0,2]].min(1)<=hi,axis=1));rows=[]
    for i in ids:
        result=pair(exact,terrain[i])
        if result is not None:rows.append(dict(groundFace=int(i),**result))
    intervals=sorted((F(r['parameterInterval'][0]),F(r['parameterInterval'][1]))for r in rows);end=F(0);covered=bool(intervals)
    for lo,hi in intervals:
        if lo>end:covered=False
        end=max(end,hi)
    covered=covered and intervals[0][0]==0 and end==1
    maximum=max((F(r['maximumGapM'])for r in rows),default=None)
    return dict(completeGroundFacets=len(terrain),conservativeCandidateGroundFacets=len(ids),exactFiniteGroundPairs=rows,exactParameterDomainCovered=covered,maximumGapAgainstEveryOverlappingGroundFacetM=str(maximum)if maximum is not None else None,entireSegmentBelowEveryOverlappingGroundFacet=covered and maximum is not None and maximum<0,installationApproved=False,sourceGeometryChanges=0)
