"""Exact diagnostic column at an actual JS guard boundary, not terrain construction."""
from fractions import Fraction as F
import numpy as np
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import nonzero

def assess(face,xz,minimum_accepted_binary64_height):
 t=np.asarray(face,dtype='<f8');p=np.asarray(xz,dtype='<f8');h=float(minimum_accepted_binary64_height)
 assert t.shape==(3,3)and p.shape==(2,)and np.isfinite(t).all()and np.isfinite(p).all()and np.isfinite(h)
 a,b,c=[[F(float(v))for v in q]for q in t];u=[b[k]-a[k]for k in range(3)];v=[c[k]-a[k]for k in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];zero=not any(n)
 descriptor='exactNonrendering'if zero else'vertical'if n[1]==0 else('horizontalUp'if n[1]>0 else'horizontalDown')if n[0]==n[2]==0 else'steep'if 16*n[1]*n[1]<=sum(q*q for q in n)else'obliqueUp'if n[1]>0 else'obliqueDown'
 ground=np.repeat(np.array([[p[0],h,p[1]]],dtype='<f8'),3,axis=0);proof=column(t,ground);gap=F(proof['exactMinimumFiniteColumnGapM'])if proof['exactClosedHorizontalProjectionsMeet']else None
 return dict(completeClosedSourceColumn=proof,exactUnnormalisedSourceNormal=list(map(str,n)),geometricOrientationDescriptorOnly=descriptor,exactSourceNonrendering=zero,ordinaryConflictAtSmallestAcceptedHeight=bool(not zero and gap is not None and gap<F(-1,2)),existingOrdinaryLowerBoundM='-1/2',syntheticPointIsDiagnosticOnlyNotTerrain=True,noCoverageRoleSupportOrAcceptanceCredit=True)
