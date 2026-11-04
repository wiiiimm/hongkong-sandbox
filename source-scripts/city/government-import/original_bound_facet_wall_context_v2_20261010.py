"""Refine only conservative exposure bounds at actual original source vertices.

Complete finite minimum-clearance certificates stay unchanged. An actual highest
original vertex is compared with every closed finite ground facet covering its
XZ, including collapsed projections. No sampled or tolerance exposure credit.
"""
import copy
from fractions import Fraction as F
import numpy as np
from original_bound_facet_wall_context_20261010 import contexts as prior_contexts,down
from exact_original_triangle_pair_column_gap_20261010 import verify as column
from exact_original_projection_coverage_v2_20261010 import exact_coverage

def exposure_at_vertex(vertex,ground):
 v=np.asarray(vertex,float);g=np.asarray(ground,float)
 assert v.shape==(3,) and g.ndim==3 and g.shape[1:]==(3,3) and len(g) and np.isfinite(v).all() and np.isfinite(g).all()
 point=np.repeat(v[None,:],3,axis=0)
 coverage=exact_coverage(point,g);assert coverage['exactProjectionCovered'],'Actual source vertex has no complete finite ground coverage'
 xz=g[:,:,[0,2]];ids=np.flatnonzero(np.all(xz.max(1)>=v[[0,2]],axis=1)&np.all(xz.min(1)<=v[[0,2]],axis=1));pieces=[];gaps=[]
 for i in ids:
  proof=column(point,g[i]);pieces.append(dict(originalGroundFace=int(i),completeFiniteColumnProof=proof))
  if proof['exactClosedHorizontalProjectionsMeet']:gaps.append(F(proof['exactMinimumFiniteColumnGapM']))
 assert gaps;gap=min(gaps)
 return dict(exactExposureLowerBoundM=str(gap),maximumObservedGapM=down(gap),actualHighestOriginalVertex=v.tolist(),completeVertexProjectionCoverage=coverage,allPointAABBOriginalGroundFacets=list(map(int,ids)),allPointFiniteColumnProofs=pieces,qualification='Certified gap at the actual highest original vertex against every finite closed terrain facet at its exact XZ; no horizontal tolerance, interpolation outside facets or distant AABB height credit.',sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False)

def contexts(triangles,ground,proof_rows,*,expected_binding,current_binding):
 out=copy.deepcopy(prior_contexts(triangles,ground,proof_rows,expected_binding=expected_binding,current_binding=current_binding));tri=np.asarray(triangles,float)
 for i,c in enumerate(out):
  if c['minimum']['minimumGapM']>=-.5:continue
  prior={k:copy.deepcopy(c[k]) for k in ['maximumObservedGapM','exposureQualification','exactExposureLowerBoundM','actualHighestOriginalVertex','allExposureBoundingGroundFacets']}
  vertex=tri[i,int(np.argmax(tri[i,:,1]))];proof=exposure_at_vertex(vertex,ground)
  assert F(proof['exactExposureLowerBoundM'])>=F(prior['exactExposureLowerBoundM']),'Refinement cannot reduce the prior conservative exposure bound'
  c.update(maximumObservedGapM=proof['maximumObservedGapM'],exactExposureLowerBoundM=proof['exactExposureLowerBoundM'],exposureQualification=proof['qualification'],priorConservativeVertexExposureVerbatim=prior,actualHighestVertexFiniteExposure=proof)
 return out
