"""Exact West Wing source-only visual mounting INTERFACE DIAGNOSIS, no role credit."""
from fractions import Fraction as Q
import numpy as np
from complete_original_lower_opening_mounts_v3_20261011 import binding
from west_wing26195_body108_113_strict_host_association_draft_v1_20261012 import boundary,lower4_context
from exact_original_edge_finite_facade_distance_band_v2_20261010 import verify as finite_band,merge
ORDERS=[[0,1,2],[1,0,2],[0,2,1]]

def host_inventory(t,main_ids,records):
 eligible=[];excluded=[]
 for i in main_ids:
  if records[i]['strictPositiveFiniteProved']:
   assert records[i]['ordinaryFiniteProved']and records[i]['completeProjectionCovered'];eligible.append(i)
  else:excluded.append(i)
 return dict(completeMainBodySourceFaces=main_ids,completeStrictFiniteHostFaces=eligible,completeNotStrictHostFaces=excluded,strictHostGroundedIndependently=False,wholeBody0RootAccepted=False)

def edge_candidates(t,edge,host_ids):
 a=np.asarray(edge,dtype='<f8');assert a.shape==(2,3)and np.isfinite(a).all()and not np.array_equal(*a)
 lo=[min(Q(float(x))for x in a[:,k])-Q(.1)for k in range(3)];hi=[max(Q(float(x))for x in a[:,k])+Q(.1)for k in range(3)];selected=[];excluded=[]
 for i in host_ids:
  separators=[]
  for k in range(3):
   low=min(Q(float(v))for v in t[i,:,k]);high=max(Q(float(v))for v in t[i,:,k])
   if high<lo[k]:separators.append(dict(axis=k,kind='strictly-below-expanded-segment-box',exactHostExtreme=str(high),exactBandBoundary=str(lo[k])))
   if low>hi[k]:separators.append(dict(axis=k,kind='strictly-above-expanded-segment-box',exactHostExtreme=str(low),exactBandBoundary=str(hi[k])))
  if separators:excluded.append(dict(sourceHostFace=i,exactSeparationWitnesses=separators))
  else:selected.append(i)
 return dict(allCompleteStrictHostIDs=host_ids,completeFiniteBandCandidateHostIDs=selected,allExactClosed3DAABBExclusions=excluded,fixedBandM=.1,noNearestOrHeightLayerChoice=True)

def diagnose_edge(t,edge,hosts):
 inventory=edge_candidates(t,edge,hosts);ids=inventory['completeFiniteBandCandidateHostIDs'];assert len(ids)<=512,'Finite interface workload bound exceeded';proofs=[];certified=[]
 for order in ORDERS:
  # Exact coordinate permutations only: squared Euclidean distances are unchanged.
  p=finite_band(np.asarray(edge)[:,order],t[ids][:,:,order])if ids else None;orientation=[]
  for i in ids:
   a,b,c=[[Q(float(x))for x in v]for v in t[i][:,order]];u=[b[j]-a[j]for j in range(3)];v=[c[j]-a[j]for j in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];n2=sum(x*x for x in n);assert n2
   orientation.append(dict(sourceHostFace=i,exactPermutedNormal=list(map(str,n)),eligibleForUnchangedKernelOrientation=n[1]*n[1]<=n2/Q(16)))
  proofs.append(dict(exactOrthonormalCoordinateOrder=order,allCandidateHostOrientationAccounting=orientation,actualKernelHostIDs=ids,finiteEdgeProof=p))
  if p:certified.extend(tuple(map(Q,x))for x in p['exactFacetAndEdgeCertifiedMergedIntervals'])
 union=merge(certified)
 return dict(unchangedWholeSourceEdge=edge,completeHostInventory=inventory,allThreeExactCoordinateOrderProofs=proofs,exactWholeEdgeCertifiedIntervalUnion=[[str(a),str(b)]for a,b in union],wholePositiveLengthFiniteBandContext=union==[(Q(0),Q(1))],coordinatePermutationsDoNotChangeDistance=True,bandIsNotPhysicalContact=True,visualRoleAccepted=False,structuralRootCredit=False,installationApproved=False)

def diagnose(t,body_ids,main_ids,records,prior,*,expected_binding):
 t=np.asarray(t,dtype='<f8');assert np.isfinite(t).all()and binding(t,body_ids,main_ids)==expected_binding,'Changed exact source/body/main-host binding';host=host_inventory(t,main_ids,records);topology=boundary(t,body_ids)
 if len(body_ids)==8:
  lower=lower4_context(t,body_ids);assert prior['kind']=='body108-minimum-edge-context'and prior['completeBodyFaces']==body_ids and prior['unchangedOpeningV3Rejection']['rejected']and not prior['completeLowerOpeningAssociated'];proofs=prior['allFourMinimumEdgeProofs'];assert len(proofs)==4 and all(p['proof']['verifiedCompleteOriginalEdgeContactBand']for p in proofs)
  assert [(p['sourceFace'],tuple(map(tuple,p['unchangedOriginalEdge'])))for p in proofs]==[(i,(a,b))for i,a,b in lower['completeMinimumDirectedCycle']]
  assert set(prior['completeHostFaces'])<=set(host['completeStrictFiniteHostFaces']);assert binding(t,body_ids,prior['completeHostFaces'])==prior['binding']
  return dict(kind='source-bound-upright-two-open-boundary-visual-surface-minimum-rim-context',binding=expected_binding,completeSourceTopology=topology,completeStrictHostInventory=host,priorFourMinimumEdgeFiniteBandProofsReusedVerbatim=prior,allFourMinimumRimEdgesAssociatedContext=True,higherCompleteBoundaryRetainedUnfilled=True,openingV3RejectionPreserved=True,engineeringFunctionUnknown=True,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,physicalAccepted=False,installationApproved=False)
 assert len(body_ids)==2 and len(topology['completeDirectedBoundaryEdges'])==4 and len(topology['completeDirectedBoundaryCycles'])==1;assert prior['kind']=='body113-whole-two-face-surface-context'and prior['completeBodyFaces']==body_ids and prior['literalPointOnlyContactNegativeNotRewritten']
 edges=[dict(sourceFace=i,interface=diagnose_edge(t,[list(a),list(b)],host['completeStrictFiniteHostFaces']))for i,a,b in topology['completeDirectedBoundaryEdges']]
 return dict(kind='source-bound-horizontal-projecting-two-facet-perimeter-wedge-complete-boundary-interface-context',binding=expected_binding,completeSourceTopology=topology,completeStrictHostInventory=host,allFourBoundaryEdgeDiagnostics=edges,wholeBandAssociatedBoundaryEdgeIndices=[i for i,e in enumerate(edges)if e['interface']['wholePositiveLengthFiniteBandContext']],allFreeOriginalEdgesRetained=True,priorWholeHostBandAndLiteralPointFailuresReusedVerbatim=prior,mountingEdgeDesignationNotAutomatic=True,engineeringFunctionUnknown=True,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,physicalAccepted=False,installationApproved=False)
