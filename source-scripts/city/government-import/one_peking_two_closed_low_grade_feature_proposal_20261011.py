"""Named unchanged low exterior features intersecting literal drawn grade.

A proposal only: no closed-solid, function, load-bearing or current root credit.
The caller must independently bind full source/runtime/ground and all current
physical actors. Raw ordinary-rim/JS failures are never removed by this helper.
"""
from fractions import Fraction as F
import hashlib
import numpy as np
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_paired_finite_clearance_20261010 import verify as finite
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
UID='landsd/233985:0'
SCOPE={13:dict(ids=[2425,2426,2427,2428,*range(3759,3767)],down=[2425,2426],up=[2427,2428],side=list(range(3759,3767))),15:dict(ids=[2433,2434,2435,2436,*range(3767,3775)],down=[2433,2434],up=[2435,2436],side=list(range(3767,3775)))}
def sha(a):return hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
def cap_relation(proof,relation):
 assert proof['groundProjectionCovered'] and proof['existingOrdinaryClearanceBoundProved']
 pieces=proof['allExactFiniteSourceGroundPieces'];values=[]
 for p in pieces:
  if p.get('closedProjectionDisjoint'):continue
  assert not p.get('collapsedProjectionConservative'),'Collapsed terrain receives no cap-level role proof'
  assert p['allExactSourcePrismIntersectionVertices']
  values.extend(F(v['exactGapM']) for v in p['allExactSourcePrismIntersectionVertices'])
 assert values
 assert (min(values)>0 if relation=='exposed-upward-cap' else max(values)<0),relation
 return dict(relation=relation,exactMinimumGapM=str(min(values)),exactMaximumGapM=str(max(values)),completeFinitePieceVertices=len(values))
def verify(whole,component,ground,*,uid,expected_world_sha,expected_ground_sha,complete_face_ids):
 assert uid==UID and component in SCOPE
 a=np.asarray(whole,dtype='<f8');g=np.asarray(ground,dtype='<f8');scope=SCOPE[component]
 assert a.shape==(15784,3,3) and g.ndim==3 and g.shape[1:]==(3,3) and len(g)
 assert np.isfinite(a).all() and np.isfinite(g).all()
 assert sha(a)==expected_world_sha and sha(g)==expected_ground_sha
 assert list(complete_face_ids)==scope['ids']
 topology=census(a,scope['ids'])
 assert topology['boundaryEdges']==topology['nonmanifoldEdges']==topology['twoFaceOrientationConflicts']==0
 assert topology['exactNonrenderingOriginalFaces']==[] and topology['sharedEdgeConnectedComponents']==[scope['ids']]
 normals={i:np.cross(a[i,1]-a[i,0],a[i,2]-a[i,0]) for i in scope['ids']}
 assert all(normals[i][1]>0 for i in scope['up']) and all(normals[i][1]<0 for i in scope['down'])
 # Source-owned IDs are complete; orientation alone never selects or omits faces.
 proofs={i:finite(a[i],g) for i in scope['ids']}
 assert all(p['groundProjectionCovered'] and p['existingOrdinaryClearanceBoundProved'] for p in proofs.values())
 caps=[dict(sourceFace=i,**cap_relation(proofs[i],'exposed-upward-cap')) for i in scope['up']]
 bases=[dict(sourceFace=i,**cap_relation(proofs[i],'below-drawn-grade')) for i in scope['down']]
 contacts=exact_finite_contacts(a,scope['side'],g,range(len(g)));assert contacts['allPairsExamined']
 grade=[c for c in contacts['contacts'] if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
 assert {c['sourceFaceA'] for c in grade}==set(scope['side']),'Every complete side facet needs genuine finite grade intersection'
 return dict(contract='one-peking-two-named-closed-edge-low-grade-feature-source-proposal-v1',uid=uid,component=component,completeSourceFaces=15784,completeFeatureFaceIDs=scope['ids'],completeWorldSHA256=sha(a),completeDrawnGroundSHA256=sha(g),completeNonzeroEdgeTopology=topology,completeFiniteFeatureGroundProofs=proofs,completeExposedUpwardCapProofs=caps,completeBelowGradeDownwardCapProofs=bases,completePositiveDimensionalSideGradeInterfaces=grade,sourceRoleProposalSupported=True,closedSolidCertification=False,structuralFunctionClaim=False,loadBearingClaim=False,sourceGroundRootAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,ordinaryRimAndStrictJSFailuresPreserved=True,currentRegionalRebindRequired=True)
