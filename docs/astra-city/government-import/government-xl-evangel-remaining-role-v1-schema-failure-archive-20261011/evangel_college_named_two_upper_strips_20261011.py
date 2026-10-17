"""Named source strips: three backed edges and one authored free upper edge.

The existing unchanged .1m whole-edge proofs are mandatory for the lower edge
and both ends. The upper-edge failure stays verbatim. No function, structural
root, bridge or independently approved physical placement is inferred here.
"""
from fractions import Fraction as F
import numpy as np
from evangel_college_named_lower_source_skin_20261011 import sha,edges,WORLD_HASHES
IDS={221:[13826,13827],222:[13828,13829]}
def verify(*,world,qualification_row,parts,qualified_host_face_ids):
 w=np.asarray(world,dtype='<f8');wh=sha(w);assert w.shape==(13960,3,3)and np.isfinite(w).all()and wh in WORLD_HASHES and wh==qualification_row['completeWorldSHA256']and len(parts)==226
 allowed=set(qualified_host_face_ids);assert len(allowed)==len(qualified_host_face_ids)and not allowed&{i for ids in IDS.values()for i in ids}
 result=[]
 for component,ids in IDS.items():
  assert parts[component]==ids
  rows=[v for v in qualification_row['completeFiveVisualDispositions']if v['originalComponent']==component];assert len(rows)==1;v=rows[0];assert v['completeOriginalFaces']==ids and v['allOriginalFacetsOrdinaryClear']is True and v['structuralRootCredit']is False and v['structuralBridgeCredit']is False
  t=w[ids];points={tuple(F(float(x))for x in p)for p in t.reshape(-1,3)};assert len(points)==4
  ee=[edges(f)for f in t];shared=ee[0]&ee[1];outer=ee[0]^ee[1];assert len(shared)==1 and len(outer)==4
  low=min(p[1]for p in points);high=max(p[1]for p in points);assert low<high and {p[1]for p in points}=={low,high}
  free=[e for e in outer if all(p[1]==high for p in e)];bottom=[e for e in outer if all(p[1]==low for p in e)];ends=[e for e in outer if {p[1]for p in e}=={low,high}];assert len(free)==len(bottom)==1 and len(ends)==2
  proofs=v['completeBoundaryEdgeFiniteHostBandProofs'];assert len(proofs)==4
  byedge={tuple(sorted(tuple(F(float(x))for x in p)for p in r['completeOriginalEdge'])):r for r in proofs};assert len(byedge)==4 and set(byedge)==outer
  near=v['completeHostCandidateFaceIds'];far=v['strictlyOutsideUnchangedBandHostFaces'];assert near and len(near)==len(set(near))and not set(near)&set(far)and set(near)|set(far)==set(qualification_row['completeConditionalHostFaceIds'])and set(near)<=allowed
  mounted=[]
  for e in bottom+ends:
   r=byedge[e];assert r['fullEdgeAssociated']is True and r['emptyHostScopeExplicitlyUnqualified']is False
   trials=r['completeCoordinatePermutationTrials'];assert [p['coordinatePermutation']for p in trials]==[[0,1,2],[1,0,2],[0,2,1]]and any(p['completeFiniteHostBandProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']is True for p in trials)
   mounted.append(r)
  failed=byedge[free[0]];assert failed['fullEdgeAssociated']is False and failed['emptyHostScopeExplicitlyUnqualified']is False
  assert all(p['completeFiniteHostBandProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']is False for p in failed['completeCoordinatePermutationTrials'])
  result.append(dict(originalComponent=component,completeOriginalFaces=ids,completeOriginalGeometrySHA256=sha(t),completeOriginalSharedDiagonal=[[str(v)for v in p]for p in next(iter(shared))],completeMountedLowerAndSideEdgeProofsVerbatim=mounted,completeAuthoredFreeUpperEdgeFailureVerbatim=failed,completeQualifiedHostFaceIds=near,unchangedFiniteHostBandM=.1,nonstructuralVisualInterpretationOnly=True,structuralRootCredit=False,structuralBridgeCredit=False,functionClaim=False))
 return dict(contract='Evangel-exact-two-original-upper-strips-lower-and-side-backed-free-upper-v1',completeWholeSourceWorldSHA256=wh,completeTwoStrips=result,rawWholeBoundaryFailureRetained=True,sourceGeometryChanges=0,currentAcceptance=False,installationApproved=False)
