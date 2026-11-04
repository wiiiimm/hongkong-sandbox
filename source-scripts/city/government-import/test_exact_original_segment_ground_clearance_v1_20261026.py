import unittest
from fractions import Fraction as F
from exact_original_segment_ground_clearance_v1_20261026 import verify

class SegmentGroundTests(unittest.TestCase):
    def test_full_segment_below_ground(self):
        p=verify([[0,-1,0],[1,-1,0]],[[[0,0,-1],[2,0,-1],[0,0,2]]]);self.assertTrue(p['entireSegmentBelowEveryOverlappingGroundFacet']);self.assertEqual(p['maximumGapAgainstEveryOverlappingGroundFacetM'],'-1')
    def test_gap_not_hidden_by_endpoint_tests(self):
        p=verify([[0,-1,0],[2,-1,0]],[[[0,0,-1],[.5,0,-1],[0,0,1]],[[1.5,0,-1],[2,0,-1],[2,0,1]]]);self.assertFalse(p['exactParameterDomainCovered']);self.assertFalse(p['entireSegmentBelowEveryOverlappingGroundFacet'])
    def test_terrain_crosses_segment(self):
        p=verify([[0,-1,0],[1,1,0]],[[[0,0,-1],[2,0,-1],[0,0,2]]]);self.assertTrue(p['exactParameterDomainCovered']);self.assertFalse(p['entireSegmentBelowEveryOverlappingGroundFacet'])
    def test_exact_rational_points_no_rounding(self):
        p=verify([[F(1,3),-1,0],[F(2,3),-1,0]],[[[0,0,-1],[2,0,-1],[0,0,2]]]);self.assertTrue(p['entireSegmentBelowEveryOverlappingGroundFacet'])
    def test_contact_is_not_strictly_below(self):
        p=verify([[0,0,0],[1,0,0]],[[[0,0,-1],[2,0,-1],[0,0,2]]]);self.assertFalse(p['entireSegmentBelowEveryOverlappingGroundFacet'])
    def test_vertical_ground_primitive_not_omitted(self):
        p=verify([[0,-1,0],[0,-2,0]],[[[0,0,-1],[0,0,1],[0,-3,0]]]);self.assertTrue(p['exactParameterDomainCovered']);self.assertFalse(p['entireSegmentBelowEveryOverlappingGroundFacet']);self.assertEqual(len(p['exactFiniteGroundPairs']),1)

if __name__=='__main__':unittest.main()
