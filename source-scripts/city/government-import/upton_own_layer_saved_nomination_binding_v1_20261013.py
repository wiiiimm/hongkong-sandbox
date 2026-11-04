"""Byte-exact current own-layer nomination binding; inherited maps stay historical."""
import hashlib
from upton_current_ring12_saved_nomination_binding_v1_20261013 import triplet_bytes

HISTORICAL_FIELDS=('computedCurrentRing12PreviousCandidateMapping','computedCurrentRing12PartitionProof','allOther11575RawCandidateTripletsUnchanged','exactSourceFamilyPartitionProof','completeSavedFailuresVerbatim','completeUnchangedSource35677CandidateFamily','originalNomination','originalSourceTriplets','previousEdgeDiagnostic')

def validate_own_layer_binding(new,previous,original,*,targets,protected_count):
 targets=set(targets);before=previous['candidateRawPositionTriplets'];after=new['candidateRawPositionTriplets'];mapping=new['computedOwnLayer11577To11580Mapping'];pv=new['candidateFaceProvenance']
 assert len(after)==len(before)+len(targets)and len(mapping)==len(before)
 assert [r['candidateFace']for r in pv]==list(range(len(after)))and [r['oldCandidateFace']for r in mapping]==list(range(len(before)))
 assert [i for r in mapping for i in r['newCandidateFaces']]==list(range(len(after)))
 proof_rows={r['oldCandidateFace']:r for r in new['threeOwnLayerSubdivisionProofs']};assert len(new['threeOwnLayerSubdivisionProofs'])==len(proof_rows)==len(targets)and set(proof_rows)==targets
 for i,row in enumerate(mapping):
  ids=row['newCandidateFaces'];assert len(ids)==(2 if i in targets else 1)and row['allOldRawBytesUnchanged']is(i not in targets)
  old_p=previous['candidateFaceProvenance'][i]
  for part,j in enumerate(ids):
   assert pv[j]['rawNominationFaceSHA256']==hashlib.sha256(triplet_bytes(after[j])).hexdigest()
   if i not in targets:
    assert triplet_bytes(after[j])==triplet_bytes(before[i])and pv[j]=={**old_p,'candidateFace':j}
   else:
    row=proof_rows[i];assert row['feasibleOwnLayerSubdivision']and row['noOtherHeightLayerBridge']and row['noCoverageOrPhysicalApproval']
    proof=row['exactOwnLayerProof'];partition=proof['exactPartitionProof']
    saved_aliases=row['savedRejectingEdgeVerbatim']['completeInteriorSubdivisionNodes'];assert len(saved_aliases)==3
    assert proof['unchangedOtherLayerXYZ']==[r['exactIdealXYZ']for r in saved_aliases]and proof['unchangedOtherLayerPackedXYZ']==[r['actualPackedXYZ']for r in saved_aliases]
    assert proof['ownYInterpolatedOnlyFromTargetEdge']and proof['neverCopiedOtherLayerY']and proof['packedXZMatchesAllUnchangedAliases']and proof['allOriginalEndpointRawBytesRetained']and proof['noOtherLayerVerticesMoved']and proof['noPackedCoverageHeightOrAcceptanceClaim']
    assert partition['completeIdealTrianglePreserved']and partition['idealPiecesShareOnlyFiniteOppositeToNodeBoundary']and partition['noPackedCoverageHeightOrAcceptanceClaim']and len(partition['exactPiecesXYZ'])==2
    assert triplet_bytes(after[j])==triplet_bytes(proof['packedPieceTriplets'][part])
    original_points=old_p['exactOriginalPlanePoints'];assert partition['exactOriginalXYZ']in[original_points,[original_points[k]for k in[0,2,1]]]
    assert row['savedRejectingEdgeVerbatim']['provenanceVerbatim']==old_p
    for corner,point in enumerate(partition['exactPiecesXYZ'][part]):
     assert point in original_points or point==proof['exactOwnLayerNodeXYZ']
     if point in original_points:
      old_point=before[i][original_points.index(point)];new_point=after[j][corner]
      assert triplet_bytes([new_point]*3)==triplet_bytes([old_point]*3)
     else:assert triplet_bytes([after[j][corner]]*3)==triplet_bytes([proof['packedOwnLayerNodeXYZ']]*3)
    expected={**old_p,'candidateFace':j,'rawNominationFaceSHA256':pv[j]['rawNominationFaceSHA256'],'computedFragment':True,'savedInputByteExact':False,'exactOriginalPlanePoints':partition['exactPiecesXYZ'][part],'computedOwnLayerProjectedSubdivision':dict(oldCandidateFace=i,originalFace=49215,part=part,exactNodeXYZ=proof['exactOwnLayerNodeXYZ'],ownYOnly=True,noOtherLayerYReuse=True)}
    assert old_p['kind']=='originalTIN'and old_p['originalFace']==49215 and pv[j]==expected
 old_map=previous['completeOldNewIndexMapping'];new_map=new['completeOldNewIndexMapping'];assert len(old_map)==len(new_map)==len(original['candidateRawPositionTriplets'])
 for i,(old,current)in enumerate(zip(old_map,new_map)):
  assert old['oldCandidateFace']==current['oldCandidateFace']==i
  expected={**old,'newCandidateFaces':[j for k in old['newCandidateFaces']for j in mapping[k]['newCandidateFaces']],'allOldRawBytesUnchanged':old['allOldRawBytesUnchanged']and not any(k in targets for k in old['newCandidateFaces'])}
  assert current==expected
  if current['allOldRawBytesUnchanged']:
   assert len(current['newCandidateFaces'])==1 and triplet_bytes(after[current['newCandidateFaces'][0]])==triplet_bytes(original['candidateRawPositionTriplets'][i])
 assert [i for r in new_map for i in r['newCandidateFaces']]==list(range(len(after)))
 protected=previous['protectedWholeCurrentTripletsUnchanged'];assert len(protected)==len(new['protectedWholeCurrentTripletsUnchanged'])==protected_count
 for old,current in zip(protected,new['protectedWholeCurrentTripletsUnchanged']):
  prior=old['newCandidate'];assert prior not in targets and len(mapping[prior]['newCandidateFaces'])==1
  assert current=={**old,'newCandidate':mapping[prior]['newCandidateFaces'][0]}
  assert triplet_bytes(after[current['newCandidate']])==triplet_bytes(before[prior])
 aliases=new['allOtherLayerVertexIncidentBindings'];assert aliases
 expected_aliases=[]
 for row in new['threeOwnLayerSubdivisionProofs']:
  for alias in row['savedRejectingEdgeVerbatim']['completeInteriorSubdivisionNodes']:
   for incident in alias['completeVertexIncidents']:
    old_ids=previous['computedCurrentRing12PreviousCandidateMapping'][incident['candidateFace']]['newCandidateFaces'];assert len(old_ids)==1
    old=old_ids[0]
    expected_aliases.append(dict(target=row['oldCandidateFace'],oldIncidentVerbatim=incident,newIncidentFace=old,unchangedWholeRawTripletSHA256=hashlib.sha256(triplet_bytes(before[old])).hexdigest(),unchangedWholeRawTriplet=before[old],otherLayerIdealXYZ=alias['exactIdealXYZ'],otherLayerPackedXYZ=alias['actualPackedXYZ'],otherLayerYNotCopiedOrMoved=True))
 assert aliases==expected_aliases,'Missing, duplicate, reordered or changed other-layer incidence binding'
 for row in aliases:
  old=row['newIncidentFace'];assert old not in targets and row['target']in targets and row['otherLayerYNotCopiedOrMoved']
  assert row['unchangedWholeRawTripletSHA256']==hashlib.sha256(triplet_bytes(before[old])).hexdigest()and triplet_bytes(row['unchangedWholeRawTriplet'])==triplet_bytes(before[old])
  ids=mapping[old]['newCandidateFaces'];assert len(ids)==1 and triplet_bytes(after[ids[0]])==triplet_bytes(before[old])
 for key in HISTORICAL_FIELDS:assert new[key]==previous[key]
 assert new['allOther11574RawTripletsUnchanged']and new['all68ProtectedLiteralTripletsUnchanged']and new['wholeSourceAndForeignAndCoverageFiniteSeamMAXRuntimeAcceptancePending']
 assert new['originalBuildingGeometryPoseChanges']==0 and new['physicalAccepted']is False and new['installationApproved']is False
 return True
