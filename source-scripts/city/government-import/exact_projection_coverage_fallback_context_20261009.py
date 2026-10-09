"""Prove a floating closed-facet coverage failure with identical exact facets.

Original minimum/maximum/face context stays untouched; original false flag is
retained alongside the exact Fraction proof. Real gaps remain false.
"""
import copy
from exact_original_projection_coverage_20261009 import exact_coverage

def apply_exact_coverage(context,source_face,same_ground):
 result=copy.deepcopy(context)
 if not result['groundProjectionCovered']:
  proof=exact_coverage(source_face,same_ground)
  result['rawFloatingCoverageFalseRetained']=True
  result['exactSameGroundCoverageProof']=proof
  if proof['exactProjectionCovered']:result['groundProjectionCovered']=True
 return result
