"""Exact exposure witnesses at all original wall vertices on sloping terrain.

The highest source vertex need not have the greatest terrain clearance. Keep
all earlier bounds and certify actual complete finite columns at all three
original vertices only when the highest-vertex certificate gives no exposure.
"""
import copy
from fractions import Fraction as F
import numpy as np
from original_bound_facet_wall_context_v2_20261010 import contexts as prior_contexts,exposure_at_vertex

def best_original_vertex_exposure(face,ground):
 tri=np.asarray(face,float);assert tri.shape==(3,3) and np.isfinite(tri).all()
 proofs=[dict(originalVertex=i,**exposure_at_vertex(v,ground)) for i,v in enumerate(tri)]
 winner=max(proofs,key=lambda p:F(p['exactExposureLowerBoundM']))
 return dict(actualExposedOriginalVertex=tri[winner['originalVertex']].tolist(),actualExposedOriginalVertexIndex=winner['originalVertex'],exactExposureLowerBoundM=winner['exactExposureLowerBoundM'],maximumObservedGapM=winner['maximumObservedGapM'],allThreeOriginalVertexFiniteColumnProofs=proofs,qualification='Maximum certified exposure lower bound at the three unchanged original vertices. Each complete finite ground column is tested exactly; a positive value proves an actual original vertex above every drawn terrain facet at its XZ. It is not asserted to be the complete face maximum.',sourceGeometryChanges=0,rootOrContactCredit=False,fullAcceptance=False)

def contexts(triangles,ground,proof_rows,*,expected_binding,current_binding):
 out=copy.deepcopy(prior_contexts(triangles,ground,proof_rows,expected_binding=expected_binding,current_binding=current_binding));tri=np.asarray(triangles,float)
 for i,c in enumerate(out):
  if c['minimum']['minimumGapM']>=-.5 or c['maximumObservedGapM']>0:continue
  old={k:copy.deepcopy(c[k]) for k in ['maximumObservedGapM','exposureQualification','exactExposureLowerBoundM']};proof=best_original_vertex_exposure(tri[i],ground)
  assert F(proof['exactExposureLowerBoundM'])>=F(old['exactExposureLowerBoundM'])
  c.update(maximumObservedGapM=proof['maximumObservedGapM'],exactExposureLowerBoundM=proof['exactExposureLowerBoundM'],exposureQualification=proof['qualification'],priorHighestOriginalVertexExposureVerbatim=old,completeOriginalVertexExposure=proof)
 return out
