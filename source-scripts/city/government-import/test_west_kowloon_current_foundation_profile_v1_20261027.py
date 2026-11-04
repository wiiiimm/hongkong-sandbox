import copy
import unittest
from west_kowloon_pair_physical_review_v1_20261027 import MASKED, verify_current_foundation_record


class ExactFoundationPartition(unittest.TestCase):
    def setUp(self):
        self.record = dict(mode='original', groundSHA256='ground', reviewedSourceFaces=MASKED.copy(),
            allOtherSourceFaces=[i for i in range(10322) if i not in set(MASKED)],
            currentMaskedFacets=[dict(sourceFace=i, completeProjectionCovered=True, strictlyMasked=True,
                maximumAllFinitePairGapM='-1/2', strictCoreSeparatingAxisGapsM=[1, -1]) for i in MASKED],
            ordinaryFoundation=dict(triangles=10287, completeTerrainTriangles=10287, fullyBuriedTriangles=0,
                fullyBuriedUpwardTriangles=0, fullyBuriedAreaFraction=0),
            wholeRawFoundation=dict(triangles=10322, completeTerrainTriangles=10322, fullyBuriedTriangles=35, fullyBuriedUpwardTriangles=24),
            ordinaryFoundationPolicyPassed=True, allReviewedFacesStrictlyMasked=True)

    def test_complete_exact_case(self): self.assertTrue(verify_current_foundation_record(self.record, 'ground'))

    def test_changed_ground_rejected(self):
        with self.assertRaises(AssertionError): verify_current_foundation_record(self.record, 'other')

    def test_no_ordinary_face_may_disappear(self):
        self.record['allOtherSourceFaces'].pop()
        with self.assertRaises(AssertionError): verify_current_foundation_record(self.record, 'ground')

    def test_any_ordinary_upward_burial_rejected(self):
        self.record['ordinaryFoundation']['fullyBuriedUpwardTriangles'] = 1
        with self.assertRaises(AssertionError): verify_current_foundation_record(self.record, 'ground')

    def test_zero_or_positive_mask_gap_rejected(self):
        for gap in ['0', '1/1000000000000']:
            record = copy.deepcopy(self.record)
            record['currentMaskedFacets'][0]['maximumAllFinitePairGapM'] = gap
            with self.subTest(gap=gap), self.assertRaises(AssertionError): verify_current_foundation_record(record, 'ground')

    def test_missing_projection_or_core_separation_rejected(self):
        for changes in [dict(completeProjectionCovered=False), dict(strictCoreSeparatingAxisGapsM=[0, -1])]:
            record = copy.deepcopy(self.record); record['currentMaskedFacets'][0].update(changes)
            with self.assertRaises(AssertionError): verify_current_foundation_record(record, 'ground')

    def test_different_exception_faces_rejected(self):
        self.record['reviewedSourceFaces'] = [*MASKED[:-1], 1]
        with self.assertRaises(AssertionError): verify_current_foundation_record(self.record, 'ground')


if __name__ == '__main__': unittest.main()
