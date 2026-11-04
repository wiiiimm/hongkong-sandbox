from fractions import Fraction as F
import unittest
import numpy as np
from exact_original_finite_facade_backing_context_v1_20261024 import verify


def rectangle(y0,z0,y1,z1):
    return [[[0,y0,z0],[0,y1,z0],[0,y1,z1]],[[0,y0,z0],[0,y1,z1],[0,y0,z1]]]


class FiniteBackingTests(unittest.TestCase):
    def test_backing_at_one_metre_is_not_mount_or_distance_credit(self):
        r=verify([[1,.2,.2],[1,1.8,.2],[1,.2,1.8]],rectangle(0,0,2,2));self.assertTrue(r['verifiedCompleteFiniteBackingProjection']);self.assertFalse(r['existingPointOneMetreBandPassed']);self.assertFalse(r['visualRoleAccepted']);self.assertEqual(r['allPassingFiniteBackingWitnesses'][0]['exactVertexSquaredPerpendicularDistancesM2'],['1']*3)
    def test_infinite_plane_is_not_finite_backing(self):
        self.assertFalse(verify([[.1,3,3],[.1,4,3],[.1,3,4]],rectangle(0,0,2,2))['verifiedCompleteFiniteBackingProjection'])
    def test_corners_do_not_fill_a_real_host_hole(self):
        hosts=rectangle(0,0,.75,2)+rectangle(1.25,0,2,2)+rectangle(.75,0,1.25,.75)+rectangle(.75,1.25,1.25,2)
        self.assertFalse(verify([[.1,.5,.5],[.1,1.5,.5],[.1,1,1.5]],hosts)['verifiedCompleteFiniteBackingProjection'])
    def test_projected_segment_requires_entire_interval(self):
        source=[[.1,1,.5],[.2,1,1.5],[.3,1,1.0]]
        self.assertTrue(verify(source,rectangle(0,0,2,2))['verifiedCompleteFiniteBackingProjection'])
        self.assertFalse(verify(source,rectangle(0,0,2,.9)+rectangle(0,1.1,2,2))['verifiedCompleteFiniteBackingProjection'])
    def test_nondyadic_feet_are_not_rounded(self):
        host=[[[3,0,0],[-3,0,2],[3,4,0]],[[-3,0,2],[-3,4,2],[3,4,0]]]
        r=verify([[2.9,.5,.2],[2.5,1,.4],[2,1.5,.5]],host);self.assertTrue(r['verifiedCompleteFiniteBackingProjection'])
        for w in r['allPassingFiniteBackingWitnesses']:
            for p in w['exactOrthogonalFeet']:self.assertEqual(F(p[0])+3*F(p[2]),3)
    def test_collapsed_source_and_nonfacade_host_get_no_credit(self):
        with self.assertRaises(AssertionError):verify([[0,0,0]]*3,rectangle(0,0,2,2))
        self.assertFalse(verify([[0,1,0],[1,1,0],[0,1,1]],[[[0,0,0],[1,0,0],[0,0,1]]])['verifiedCompleteFiniteBackingProjection'])


if __name__=='__main__':unittest.main()
