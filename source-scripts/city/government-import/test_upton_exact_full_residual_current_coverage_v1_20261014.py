import unittest
from fractions import Fraction as F
from upton_exact_full_residual_current_coverage_v1_20261014 import polygon,cover_whole_polygon,closed_boundary_cover


class Tests(unittest.TestCase):
    def test_full_polygon_and_every_boundary_covered_by_two_exact_planes(self):
        p=polygon([[0,0],[1,0],[1,1],[0,1]])
        ts=[(7,polygon([[0,0],[1,0],[0,1]])),(9,polygon([[1,0],[1,1],[0,1]]))]
        r=cover_whole_polygon(p,ts);self.assertTrue(r['wholeClosedResidualCovered']);self.assertEqual(r['exactUncoveredByOriginalCurrentAreaM2'],0)
        self.assertEqual({q['originalCurrentFace']for q in r['allPositiveAreaCurrentCounterpartIntersections']},{7,9})
    def test_two_nearby_endpoint_incidents_do_not_cover_whole_boundary(self):
        ts=[(1,polygon([[0,0],['1/4',0],[0,1]])),(2,polygon([['3/4',0],[1,0],[1,1]]))]
        r=closed_boundary_cover((F(0),F(0)),(F(1),F(0)),ts);self.assertFalse(r['wholeClosedGapEdgeCovered']);self.assertEqual(len(r['completeClosedParameterUnion']),2)
    def test_arbitrarily_thin_real_gap_is_not_waived(self):
        e=F(1,10**30);p=[(F(0),F(0)),(F(1),F(0)),(F(1),e),(F(0),e)]
        ts=[(1,[(F(0),F(0)),(F(1),F(0)),(F(0),e)])]
        r=cover_whole_polygon(p,ts);self.assertFalse(r['wholeClosedResidualCovered']);self.assertEqual(r['exactUncoveredByOriginalCurrentAreaM2'],e/2)
    def test_fractional_coordinates_are_preserved_without_float_roundtrip(self):
        p=polygon([['1/3','1/7'],['2/3','1/7'],['1/3','2/7']]);r=cover_whole_polygon(p,[(42,p)])
        self.assertTrue(r['wholeClosedResidualCovered']);self.assertEqual(r['exactWholeSavedResidualPolygonXZ'],p)
    def test_whole_boundary_can_require_multiple_current_faces(self):
        ts=[(1,polygon([[0,0],['1/2',0],[0,1]])),(2,polygon([['1/2',0],[1,0],[1,1]]))]
        r=closed_boundary_cover((F(0),F(0)),(F(1),F(0)),ts);self.assertTrue(r['wholeClosedGapEdgeCovered']);self.assertEqual(r['completeClosedParameterUnion'],[[F(0),F(1)]])
    def test_wrong_face_only_touches_corner_and_receives_no_area_credit(self):
        p=polygon([[0,0],[1,0],[0,1]]);ts=[(88,polygon([[1,0],[2,0],[1,1]]))]
        r=cover_whole_polygon(p,ts);self.assertFalse(r['wholeClosedResidualCovered']);self.assertEqual(r['allPositiveAreaCurrentCounterpartIntersections'],[])
    def test_zero_area_residual_is_unresolved_not_promoted(self):
        with self.assertRaises(AssertionError):cover_whole_polygon([[0,0],[1,0],[2,0]],[])

if __name__=='__main__':unittest.main()
