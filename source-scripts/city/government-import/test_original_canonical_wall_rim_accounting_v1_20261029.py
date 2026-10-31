import unittest
import numpy as np
from original_canonical_wall_rim_accounting_v1_20261029 import verify
from original_wall_rim_accounting_20261009 import original_samples


class CanonicalWallRimTests(unittest.TestCase):
    def data(self,gap=-.46):
        p=np.asarray([[0.,5.,0.],[1.,5.,0.],[0.,7.,0.]])
        index=np.asarray([[0,1,2]])
        samples=[dict(r,ground=5-gap,gap=r['point'][1]-(5-gap))for r in original_samples(p,index,5)]
        low=[r for r in samples if r['point'][1]<=5.35]
        metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(r['gap']for r in samples),minLowGap=min(r['gap']for r in low),maxLowGap=max(r['gap']for r in low))
        return p,index,samples,metric

    def run_case(self,gap=-.46,**changes):
        p,index,samples,metric=self.data(gap)
        args=dict(approved_wall_faces=[0],wall_role_review_approved=True,positive_finite_grade_faces=[0],expected_metric=metric);args.update(changes)
        return verify(p,index,5,samples,**args)

    def test_negative_contact_does_not_require_an_invented_near_zero_sample(self):
        r=self.run_case();self.assertTrue(r['verified']);self.assertEqual(r['strictOrdinaryAnchorSamples'],0);self.assertFalse(r['nearZeroOrdinarySampleRequired'])

    def test_reviewed_wall_failures_are_retained_not_clamped(self):
        r=self.run_case(-.8);self.assertGreater(r['rawReviewedClearanceFailuresRetained'],0);self.assertAlmostEqual(r['canonicalMinimumLowGapM'],-.8)

    def test_floating_contact_still_rejected(self):
        with self.assertRaises(AssertionError):self.run_case(.10001)

    def test_raised_low_rim_still_rejected(self):
        with self.assertRaises(AssertionError):self.run_case(1.00001)

    def test_wall_role_and_exact_grade_evidence_are_mandatory(self):
        for changes in [dict(wall_role_review_approved=False),dict(positive_finite_grade_faces=[]),dict(positive_finite_grade_faces=[1]),dict(positive_finite_grade_faces=[False]),dict(positive_finite_grade_faces=[0,0]),dict(approved_wall_faces=[])]:
            with self.assertRaises(AssertionError):self.run_case(**changes)

    def test_original_sample_inventory_and_attribution_cannot_change(self):
        p,index,samples,metric=self.data();samples[0]['point'][0]=.2
        with self.assertRaises(AssertionError):verify(p,index,5,samples,approved_wall_faces=[0],wall_role_review_approved=True,positive_finite_grade_faces=[0],expected_metric=metric)

    def test_unreviewed_source_burial_still_rejected(self):
        p,index,_,_=self.data();p=np.concatenate([p,p+np.asarray([3,0,0])]);index=np.asarray([[0,1,2],[3,4,5]])
        samples=[dict(r,ground=5.8,gap=r['point'][1]-5.8)for r in original_samples(p,index,5)]
        low=[r for r in samples if r['point'][1]<=5.35]
        metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(r['gap']for r in samples),minLowGap=min(r['gap']for r in low),maxLowGap=max(r['gap']for r in low))
        with self.assertRaisesRegex(AssertionError,'Unreviewed source clearance'):
            verify(p,index,5,samples,approved_wall_faces=[0],wall_role_review_approved=True,positive_finite_grade_faces=[0],expected_metric=metric)

    def test_ordinary_horizontal_face_cannot_receive_wall_credit(self):
        p,index,samples,metric=self.data();p[2]=[0,5,1]
        with self.assertRaises(AssertionError):verify(p,index,5,samples,approved_wall_faces=[0],wall_role_review_approved=True,positive_finite_grade_faces=[0],expected_metric=metric)


if __name__=='__main__':unittest.main()
