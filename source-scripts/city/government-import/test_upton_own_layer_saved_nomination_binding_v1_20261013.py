"""Synthetic mapping counterfixtures; no terrain or geometry acceptance tests."""
import copy,hashlib,unittest
from fractions import Fraction as F
from upton_own_layer_saved_nomination_binding_v1_20261013 import validate_own_layer_binding,HISTORICAL_FIELDS
from upton_current_ring12_saved_nomination_binding_v1_20261013 import triplet_bytes

def sha(t):return hashlib.sha256(triplet_bytes(t)).hexdigest()
def points(t):return[[str(F(float(v)))for v in p]for p in t]
def split(t):
 a,b,c=t;node=[(a[k]+b[k])/2 for k in range(3)];return[[c,a,node],[c,node,b]],node

def fixture():
 original_faces=[[[float(i),0.,0.],[float(i+1),0.,0.],[float(i),0.,1.]]for i in range(6)]
 earlier,_=split(original_faces[1]);before=[original_faces[0],*earlier,*original_faces[2:]]
 old_map=[dict(oldCandidateFace=i,newCandidateFaces=ids,allOldRawBytesUnchanged=i!=1)for i,ids in enumerate([[0],[1,2],[3],[4],[5],[6]])]
 pv=[dict(candidateFace=i,kind='originalTIN',originalFace=49215,computedFragment=False,savedInputByteExact=True,exactOriginalPlanePoints=points(t),rawNominationFaceSHA256=sha(t))for i,t in enumerate(before)]
 protected=[dict(oldCandidate=5,newCandidate=6,rawTripletSHA256=sha(before[6]))]
 previous=dict(candidateRawPositionTriplets=before,candidateFaceProvenance=pv,completeOldNewIndexMapping=old_map,protectedWholeCurrentTripletsUnchanged=protected)
 for k in HISTORICAL_FIELDS:previous[k]={'historical':k}
 previous['computedCurrentRing12PreviousCandidateMapping']=copy.deepcopy(old_map)
 new=copy.deepcopy(previous);mapping=[];after=[];newpv=[];proofs=[];aliases=[]
 for i,t in enumerate(before):
  ids=[];parts=[t]
  if i in {0,3,5}:
   parts,node=split(t);aliasrows=[dict(exactIdealXYZ=points([[node[0],y,node[2]]])[0],actualPackedXYZ=points([[node[0],y,node[2]]])[0],completeVertexIncidents=[dict(candidateFace=5,vertex=0)])for y in [7,8,9]]
   proof=dict(exactOwnLayerNodeXYZ=points([node])[0],packedOwnLayerNodeXYZ=node,packedPieceTriplets=parts,exactPartitionProof=dict(exactOriginalXYZ=points(t),exactPiecesXYZ=[points(part)for part in parts],completeIdealTrianglePreserved=True,idealPiecesShareOnlyFiniteOppositeToNodeBoundary=True,noPackedCoverageHeightOrAcceptanceClaim=True),ownYInterpolatedOnlyFromTargetEdge=True,neverCopiedOtherLayerY=True,packedXZMatchesAllUnchangedAliases=True,allOriginalEndpointRawBytesRetained=True,noOtherLayerVerticesMoved=True,noPackedCoverageHeightOrAcceptanceClaim=True,unchangedOtherLayerXYZ=[a['exactIdealXYZ']for a in aliasrows],unchangedOtherLayerPackedXYZ=[a['actualPackedXYZ']for a in aliasrows])
   proofs.append(dict(oldCandidateFace=i,feasibleOwnLayerSubdivision=True,noOtherHeightLayerBridge=True,noCoverageOrPhysicalApproval=True,exactOwnLayerProof=proof,savedRejectingEdgeVerbatim=dict(provenanceVerbatim=pv[i],completeInteriorSubdivisionNodes=aliasrows)))
   for a in aliasrows:aliases.append(dict(target=i,oldIncidentVerbatim=a['completeVertexIncidents'][0],newIncidentFace=6,unchangedWholeRawTripletSHA256=sha(before[6]),unchangedWholeRawTriplet=before[6],otherLayerIdealXYZ=a['exactIdealXYZ'],otherLayerPackedXYZ=a['actualPackedXYZ'],otherLayerYNotCopiedOrMoved=True))
  for part,q in enumerate(parts):
   j=len(after);after.append(q);record={**pv[i],'candidateFace':j,'rawNominationFaceSHA256':sha(q)}
   if i in {0,3,5}:record.update(computedFragment=True,savedInputByteExact=False,exactOriginalPlanePoints=points(q),computedOwnLayerProjectedSubdivision=dict(oldCandidateFace=i,originalFace=49215,part=part,exactNodeXYZ=proof['exactOwnLayerNodeXYZ'],ownYOnly=True,noOtherLayerYReuse=True))
   newpv.append(record);ids.append(j)
  mapping.append(dict(oldCandidateFace=i,newCandidateFaces=ids,allOldRawBytesUnchanged=i not in{0,3,5}))
 new.update(candidateRawPositionTriplets=after,candidateFaceProvenance=newpv,computedOwnLayer11577To11580Mapping=mapping,threeOwnLayerSubdivisionProofs=proofs,allOtherLayerVertexIncidentBindings=aliases,allOther11574RawTripletsUnchanged=True,all68ProtectedLiteralTripletsUnchanged=True,wholeSourceAndForeignAndCoverageFiniteSeamMAXRuntimeAcceptancePending=True,originalBuildingGeometryPoseChanges=0,physicalAccepted=False,installationApproved=False)
 new['completeOldNewIndexMapping']=[{**r,'newCandidateFaces':[j for i in r['newCandidateFaces']for j in mapping[i]['newCandidateFaces']],'allOldRawBytesUnchanged':r['allOldRawBytesUnchanged']and not any(i in{0,3,5}for i in r['newCandidateFaces'])}for r in old_map]
 new['protectedWholeCurrentTripletsUnchanged']=[{**r,'newCandidate':mapping[r['newCandidate']]['newCandidateFaces'][0]}for r in protected]
 return copy.deepcopy(new),copy.deepcopy(previous),dict(candidateRawPositionTriplets=copy.deepcopy(original_faces))

class Binding(unittest.TestCase):
 def check(self,v):return validate_own_layer_binding(*v,targets={0,3,5},protected_count=1)
 def rejected(self,fn):
  v=fixture();fn(v[0])
  with self.assertRaises(AssertionError):self.check(v)
 def test_exact_complete_binding(self):self.assertTrue(self.check(fixture()))
 def test_child_missing(self):self.rejected(lambda n:n['computedOwnLayer11577To11580Mapping'][3].update(newCandidateFaces=[4]))
 def test_child_reordered(self):self.rejected(lambda n:n['computedOwnLayer11577To11580Mapping'][3]['newCandidateFaces'].reverse())
 def test_unrelated_provenance_changed(self):self.rejected(lambda n:n['candidateFaceProvenance'][3].update(kind='changed'))
 def test_signed_zero_unrelated_raw_changed(self):
  def change(n):
   n['candidateRawPositionTriplets'][3][0][1]=-0.;n['candidateFaceProvenance'][3]['rawNominationFaceSHA256']=sha(n['candidateRawPositionTriplets'][3])
  self.rejected(change)
 def test_original_split_loss(self):self.rejected(lambda n:n['completeOldNewIndexMapping'][1].update(newCandidateFaces=[2]))
 def test_protected_index_changed(self):self.rejected(lambda n:n['protectedWholeCurrentTripletsUnchanged'][0].update(newCandidate=8))
 def test_alias_binding_dropped(self):self.rejected(lambda n:n['allOtherLayerVertexIncidentBindings'].pop())
 def test_alias_binding_y_changed(self):self.rejected(lambda n:n['allOtherLayerVertexIncidentBindings'][0].update(otherLayerIdealXYZ=['0','99','0']))
 def test_alias_raw_bytes_changed(self):self.rejected(lambda n:n['allOtherLayerVertexIncidentBindings'][0]['unchangedWholeRawTriplet'][0].__setitem__(1,99.))
 def test_original_endpoint_byte_changed_even_with_updated_proof(self):
  def change(n):
   n['candidateRawPositionTriplets'][0][1][0]=-0.;n['threeOwnLayerSubdivisionProofs'][0]['exactOwnLayerProof']['packedPieceTriplets'][0][1][0]=-0.;n['candidateFaceProvenance'][0]['rawNominationFaceSHA256']=sha(n['candidateRawPositionTriplets'][0])
  self.rejected(change)
 def test_historical_ringmap_relabelled(self):self.rejected(lambda n:n['computedCurrentRing12PreviousCandidateMapping'][0].update(newCandidateFaces=[0,1]))
 def test_duplicate_proof(self):self.rejected(lambda n:n['threeOwnLayerSubdivisionProofs'].append(copy.deepcopy(n['threeOwnLayerSubdivisionProofs'][0])))
 def test_copied_acceptance(self):self.rejected(lambda n:n.update(installationApproved=True))
if __name__=='__main__':unittest.main()
