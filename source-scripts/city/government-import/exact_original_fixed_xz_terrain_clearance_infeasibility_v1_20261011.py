"""Necessary terrain-lowering bound at an untouched original face point.

Only XZ/index-preserving terrain with every vertex >= authentic Y minus the
stated total limit is covered. No source role, current acceptance or support.
"""
from fractions import Fraction as F
import hashlib,math
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot

def verify(source_face,original_ground_face,exact_source_point,*,maximum_total_lowering_m=F(13,20),ordinary_minimum_m=F(-1,2)):
 source=np.asarray(source_face,float);ground=np.asarray(original_ground_face,float)
 assert source.shape==ground.shape==(3,3)and np.isfinite(source).all()and np.isfinite(ground).all()
 assert len(exact_source_point)==3;p=tuple(F(v)for v in exact_source_point)
 assert not isinstance(maximum_total_lowering_m,bool)and math.isfinite(float(maximum_total_lowering_m))
 limit=F(maximum_total_lowering_m);assert limit>=0
 assert F(ordinary_minimum_m)==F(-1,2),'Existing ordinary minimum is fixed'
 face=rational_face(source);n=cross(sub(face[1],face[0]),sub(face[2],face[0]));assert any(n)
 assert dot(n,sub(p,face[0]))==0,'Point is not on untouched original source plane'
 drop=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3)if i!=drop]
 def bary(triangle,axes):
  a,b,c=triangle;x,y=axes;den=(b[y]-c[y])*(a[x]-c[x])+(c[x]-b[x])*(a[y]-c[y]);assert den,'Collapsed projection provides no height certificate'
  u=((b[y]-c[y])*(p[x]-c[x])+(c[x]-b[x])*(p[y]-c[y]))/den;v=((c[y]-a[y])*(p[x]-c[x])+(a[x]-c[x])*(p[y]-c[y]))/den
  weights=(u,v,1-u-v);assert min(weights)>=0,'Witness outside complete finite triangle';return weights
 source_weights=bary(face,axes);g=rational_face(ground);weights=bary(g,[0,2]);height=sum(w*v[1]for w,v in zip(weights,g));gap=p[1]-height;best=gap+limit;required=max(F(0),F(-1,2)-gap)
 return dict(contract='exact-original-fixed-XZ-total-vertex-lowering-ordinary-infeasibility-v1',exactSourcePoint=list(map(str,p)),exactSourceBarycentricWeights=list(map(str,source_weights)),exactAuthenticGroundBarycentricWeights=list(map(str,weights)),exactAuthenticGroundHeightM=str(height),exactAuthenticOrdinaryGapM=str(gap),exactMaximumTotalVertexLoweringM=str(limit),exactNecessaryTotalLoweringM=str(required),exactBestPossibleOrdinaryGapM=str(best),ordinaryClearanceInfeasibleForThisCandidateFamily=best<F(-1,2),candidateFamilyRequiresIdenticalGroundXZAndIndices=True,candidateFamilyRequiresEveryOriginalVertexTotalLoweringBound=True,sourceFaceSHA256=hashlib.sha256(source.tobytes()).hexdigest(),authenticGroundFaceSHA256=hashlib.sha256(ground.tobytes()).hexdigest(),gradeSpanningRoleNotRejected=True,sourceGeometryChanges=0,terrainGenerated=False,currentAcceptance=False,rootOrBridgeCredit=False)
