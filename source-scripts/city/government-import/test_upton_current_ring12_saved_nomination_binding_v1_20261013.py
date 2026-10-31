"""Adversarial binding tests; synthetic geometry only, no source workers."""
import copy
import hashlib
import unittest
from upton_current_ring12_saved_nomination_binding_v1_20261013 import triplet_bytes, validate_binding


def fixture():
    faces = [[[float(i), 0.0, 0.0], [float(i), 1.0, 0.0], [float(i), 0.0, 1.0]] for i in range(4)]
    def record(face, index):
        return dict(candidateFace=index, kind='synthetic', rawNominationFaceSHA256=hashlib.sha256(triplet_bytes(face)).hexdigest())
    original = dict(candidateRawPositionTriplets=faces)
    common = dict(originalNomination={'path': 'original', 'sha256': 'pinned'}, originalSourceTriplets={'path': 'source', 'sha256': 'pinned'}, exactSourceFamilyPartitionProof={'exact': True}, completeSavedFailuresVerbatim={'negative': [1]}, completeUnchangedSource35677CandidateFamily=[{'unchanged': True}])
    before = [faces[0], faces[1], copy.deepcopy(faces[1]), faces[2], faces[3]]
    old_map = [dict(oldCandidateFace=i, newCandidateFaces=ids, allOldRawBytesUnchanged=i!=1) for i, ids in enumerate([[0], [1, 2], [3], [4]])]
    protected = [dict(oldCandidate=0, newCandidate=0, rawTripletSHA256=hashlib.sha256(triplet_bytes(faces[0])).hexdigest())]
    previous = dict(common, candidateRawPositionTriplets=before, candidateFaceProvenance=[record(f,i)for i,f in enumerate(before)], completeOldNewIndexMapping=old_map, protectedWholeCurrentTripletsUnchanged=protected)
    after = [*before[:3], before[3], copy.deepcopy(before[3]), before[4]]
    mapping = [dict(oldCandidateFace=i,newCandidateFaces=ids,allOldRawBytesUnchanged=i!=3)for i,ids in enumerate([[0],[1],[2],[3,4],[5]])]
    cumulative = [{**old,'newCandidateFaces':[j for i in old['newCandidateFaces']for j in mapping[i]['newCandidateFaces']],'allOldRawBytesUnchanged':old['allOldRawBytesUnchanged']and 3 not in old['newCandidateFaces']}for old in old_map]
    new = dict(common,candidateRawPositionTriplets=after,candidateFaceProvenance=[record(f,i)for i,f in enumerate(after)],completeOldNewIndexMapping=cumulative,computedCurrentRing12PreviousCandidateMapping=mapping,protectedWholeCurrentTripletsUnchanged=copy.deepcopy(protected),allOther11575RawCandidateTripletsUnchanged=True,allFreshActualDrawAndFullActorRuntimeAcceptancePending=True,physicalAccepted=False,installationApproved=False,originalBuildingGeometryPoseChanges=0)
    return copy.deepcopy(new), copy.deepcopy(previous), copy.deepcopy(original)


class BindingTests(unittest.TestCase):
    def validate(self, values):
        return validate_binding(*values,target=3,protected_count=1)
    def rejected(self, mutate):
        values=copy.deepcopy(fixture());mutate(values[0])
        with self.assertRaises(AssertionError):self.validate(values)
    def test_exact_composed_binding(self):self.assertTrue(self.validate(fixture()))
    def test_duplicate_mapping_rejected(self):self.rejected(lambda n:n['computedCurrentRing12PreviousCandidateMapping'][4].update(newCandidateFaces=[4]))
    def test_reordered_mapping_rejected(self):self.rejected(lambda n:n['computedCurrentRing12PreviousCandidateMapping'][3].update(newCandidateFaces=[4,3]))
    def test_cumulative_old_split_loss_rejected(self):self.rejected(lambda n:n['completeOldNewIndexMapping'][1].update(newCandidateFaces=[1]))
    def test_unrelated_negative_zero_change_rejected(self):
        def mutate(n):
            n['candidateRawPositionTriplets'][0][0][1]=-0.0
            n['candidateFaceProvenance'][0]['rawNominationFaceSHA256']=hashlib.sha256(triplet_bytes(n['candidateRawPositionTriplets'][0])).hexdigest()
        self.rejected(mutate)
    def test_nonfinite_rejected(self):self.rejected(lambda n:n['candidateRawPositionTriplets'][3][0].__setitem__(1,float('nan')))
    def test_protected_mapping_drift_rejected(self):self.rejected(lambda n:n['protectedWholeCurrentTripletsUnchanged'][0].update(newCandidate=1))
    def test_preserved_provenance_change_rejected(self):self.rejected(lambda n:n['candidateFaceProvenance'][5].update(kind='changed'))
    def test_source_reference_drift_rejected(self):self.rejected(lambda n:n['originalSourceTriplets'].update(sha256='other'))
    def test_saved_negative_erasure_rejected(self):self.rejected(lambda n:n['completeSavedFailuresVerbatim'].update(negative=[]))
    def test_copied_acceptance_rejected(self):self.rejected(lambda n:n.update(physicalAccepted=True))
    def test_building_pose_change_rejected(self):self.rejected(lambda n:n.update(originalBuildingGeometryPoseChanges=1))


if __name__=='__main__':unittest.main()
