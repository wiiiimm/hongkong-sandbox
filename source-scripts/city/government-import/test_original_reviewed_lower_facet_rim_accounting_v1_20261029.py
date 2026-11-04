import copy
import unittest
import numpy as np
from original_wall_rim_accounting_20261009 import original_samples
from original_reviewed_lower_facet_rim_accounting_v1_20261029 import verify


class LowerFacetAccounting(unittest.TestCase):
    def setUp(self):
        self.position = np.array([[0.,0.,0.],[0.,0.,1.],[1.,0.,0.],[3.,0.,0.],[4.,0.,0.],[3.,0.,1.]])
        self.index = np.arange(6).reshape(-1, 3)
        self.samples = [dict(r, ground=0. if r['point'][0]<2 else 1., gap=0. if r['point'][0]<2 else -1.) for r in original_samples(self.position,self.index,0.)]

    def run_case(self, samples=None, roles=None, approved=True):
        samples = self.samples if samples is None else samples
        metric=dict(checks=len(samples),lowRimChecks=len(samples),minSurfaceGap=min(r['gap'] for r in samples),minLowGap=min(r['gap'] for r in samples),maxLowGap=max(r['gap'] for r in samples))
        return verify(self.position,self.index,0.,samples,approved_roles={1:'downward-skin'} if roles is None else roles,source_role_review_approved=approved,expected_metric=metric)

    def test_complete_reviewed_lower_skin_retains_raw_failures(self):
        s=self.run_case();self.assertTrue(s['verified']);self.assertGreater(s['rawReviewedClearanceFailuresRetained'],0);self.assertGreater(s['strictOrdinaryAnchorSamples'],0);self.assertFalse(s['physicalAcceptance'])

    def test_unapproved_or_mislabelled_roles_fail(self):
        for args in [dict(approved=False),dict(roles={1:'wall'}),dict(roles={0:'downward-skin',1:'downward-skin'})]:
            with self.assertRaises(AssertionError):self.run_case(**args)

    def test_omitted_or_changed_source_samples_fail(self):
        with self.assertRaises(AssertionError):self.run_case(samples=self.samples[:-1])
        s=copy.deepcopy(self.samples);s[0]['point'][0]+=.001
        with self.assertRaises(AssertionError):self.run_case(samples=s)

    def test_ordinary_clearance_anchor_and_maximum_remain_required(self):
        for ground in [.2,1.,-2.]:
            s=copy.deepcopy(self.samples)
            for row in s:
                if row['point'][0]<2:row.update(ground=ground,gap=-ground)
            with self.assertRaises(AssertionError):self.run_case(samples=s)


if __name__=='__main__':unittest.main()
