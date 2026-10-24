"""One complete open exterior source feature: finite exposed caps and grade."""
import numpy as np
from one_peking_two_closed_low_grade_feature_proposal_20261011 import sha,cap_relation
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_paired_finite_clearance_20261010 import verify as finite
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
IDS=[2418,2419,3579,3580,3581,3582,3583,3584,3585,3586,3587,3615,3616,3619,3620,3696,3697,3698,3699,3700,3701,3723,3724,3725,3726,3744,3745]
CAPS=[3723,3724,3725,3726]
def verify(whole,ground,*,uid,component,expected_world_sha,expected_ground_sha,complete_face_ids):
 a=np.asarray(whole,dtype='<f8');g=np.asarray(ground,dtype='<f8')
 assert uid=='landsd/233985:0' and component==12 and complete_face_ids==IDS
 assert a.shape==(15784,3,3) and g.ndim==3 and g.shape[1:]==(3,3) and len(g) and np.isfinite(a).all() and np.isfinite(g).all()
 assert sha(a)==expected_world_sha and sha(g)==expected_ground_sha
 t=census(a,IDS);assert t['boundaryEdges']==7 and t['nonmanifoldEdges']==0 and t['twoFaceOrientationConflicts']==0
 assert t['exactNonrenderingOriginalFaces']==[] and t['sharedEdgeConnectedComponents']==[IDS]
 n=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);assert all(n[i,1]>0 and n[i,1]**2>n[i,0]**2+n[i,2]**2 for i in CAPS)
 # Fixed source-owned face IDs, not an orientation-based face selection.
 sides=sorted(set(IDS)-set(CAPS));assert all(n[i,1]**2<n[i,0]**2+n[i,2]**2 for i in sides)
 proofs={i:finite(a[i],g) for i in IDS};assert all(p['groundProjectionCovered'] and p['existingOrdinaryClearanceBoundProved'] for p in proofs.values())
 caps=[dict(sourceFace=i,**cap_relation(proofs[i],'exposed-upward-cap')) for i in CAPS]
 contact=exact_finite_contacts(a,sides,g,range(len(g)));assert contact['allPairsExamined']
 lines=[c for c in contact['contacts'] if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2];assert lines
 # Entire feature is independently proven nonzero-edge connected, so every
 # exposed cap and grade-contact wall lies in the same literal source feature.
 return dict(contract='one-peking-named-complete-open-low-grade-source-feature-proposal-v1',uid=uid,component=component,completeFeatureFaceIDs=IDS,completeWorldSHA256=sha(a),completeDrawnGroundSHA256=sha(g),completeNonzeroEdgeTopology=t,completeFiniteFeatureGroundProofs=proofs,completeExposedCapProofs=caps,completePositiveDimensionalWallGradeInterfaces=lines,sourceRoleProposalSupported=True,openSurfaceExplicit=True,closedSolidCertification=False,structuralFunctionClaim=False,loadBearingClaim=False,sourceGroundRootAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,currentRegionalRebindRequired=True)
