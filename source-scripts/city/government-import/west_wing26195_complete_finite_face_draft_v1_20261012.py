"""Diagnostic only: closed-AABB subset and unchanged coarse/paired kernels.
The nested subset hash/IDs remain nested; explicit mapping binds full ground.
"""
from fractions import Fraction as F
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column

def face_proof(face, complete, face_id, body):
 ids,selection=complete.select([[F(float(v)) for v in p] for p in face])
 if not len(ids):
  return dict(face=face_id,originalBody=body,selection=selection,selectedGroundKernelProof=None,originalGroundFaceBySelectedKernelFace=[],allRefinedFiniteColumnPairs=[],exactLowerM=None,completeProjectionCovered=False,ordinaryFiniteProved=False,strictPositiveFiniteProved=False,finiteSameXZZeroGapPairs=[],pointOrFacetContactIsNotWholeEdgeGradeRoot=True)
 terrain=complete.ground[ids];prior=finite(face,terrain);lower=F(prior['exactCertifiedLowerClearanceM']);pairs=[];minimum=maximum=None
 if lower<=0:
  for j in prior['allProjectedBoundingCandidateOriginalGroundFacets']:
   q=column(face,terrain[j]);values=[F(v['exactGapM'])for v in q['allExactBasicFeasibleColumnVertices']];pair=dict(selectedGroundFace=int(j),originalGroundFace=int(ids[j]),proof=q)
   if values:
    pair['exactMaximumFiniteColumnGapM']=str(max(values));minimum=min(values)if minimum is None else min(minimum,min(values));maximum=max(values)if maximum is None else max(maximum,max(values))
   pairs.append(pair)
  if prior['groundProjectionCovered']:assert minimum is not None,'Covered finite column has no witness'
  if minimum is not None:lower=minimum
 return dict(face=face_id,originalBody=body,selection=selection,selectedGroundKernelProof=prior,originalGroundFaceBySelectedKernelFace=ids.tolist(),allRefinedFiniteColumnPairs=pairs,exactLowerM=str(lower),exactMinimumFiniteColumnGapM=str(minimum)if minimum is not None else None,exactMaximumFiniteColumnGapM=str(maximum)if maximum is not None else None,minimumIsExactFiniteColumnWitness=minimum is not None,completeProjectionCovered=prior['groundProjectionCovered'],ordinaryFiniteProved=bool(prior['groundProjectionCovered']and lower>=-F(1,2)),strictPositiveFiniteProved=bool(prior['groundProjectionCovered']and lower>0),finiteSameXZZeroGapPairs=[p['originalGroundFace']for p in pairs if p['proof']['exactClosedHorizontalProjectionsMeet']and 'exactMaximumFiniteColumnGapM'in p and F(p['proof']['exactMinimumFiniteColumnGapM'])<=0<=F(p['exactMaximumFiniteColumnGapM'])],pointOrFacetContactIsNotWholeEdgeGradeRoot=True)
