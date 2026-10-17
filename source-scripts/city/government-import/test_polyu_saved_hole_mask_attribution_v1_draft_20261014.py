"""UNEXECUTED exact point/GIS/F32 admission synthetic cases."""
from fractions import Fraction as F
import unittest
import polyu_saved_hole_mask_attribution_v1_draft_20261014 as h


class PointFixtures(unittest.TestCase):
    def test_closed_source_triangle_keeps_vertex_and_edge(self):
        t=[[[0,2,0],[2,2,0],[0,2,2]]]
        for p in [(F(0),F(0)),(F(1),F(1))]:self.assertEqual(1,len(h.probe(p,t,native_admission=True)['admittedNativeMembers']))
    def test_raw_gis_vertex_can_be_outside_float32_constructor(self):
        raw=F(1,3);rounded=F(float(__import__('numpy').float32(float(raw))))
        ring=[[(float(raw)),0],[1,0],[float(raw),1]]
        p=(F(float(raw)),F(1));self.assertTrue(h.raw_ring_location(p,[ring])['closedRawGISSupport'])
        t=[[(rounded,F(2),F(0)),(F(1),F(2),F(0)),(rounded,F(2),F(1))]]
        self.assertFalse(h.probe(p,t)['closedMembers'])
    def test_hole_interior_excluded_but_authored_boundary_retained(self):
        rings=[[[0,0],[4,0],[4,4],[0,4]],[[1,1],[2,1],[2,2],[1,2]]]
        self.assertFalse(h.raw_ring_location((F(3,2),F(3,2)),rings)['closedRawGISSupport'])
        self.assertTrue(h.raw_ring_location((F(1),F(3,2)),rings)['closedRawGISSupport'])
    def test_tiny_positive_draw_member_is_height_excluded(self):
        d=F(1,2**20);t=[[(0,2,0),(d,2,0),(0,2,d)]]
        q=h.probe((d/4,d/4),t,native_admission=True)
        self.assertEqual(1,len(q['closedMembers']));self.assertEqual([],q['admittedNativeMembers'])
    def test_vertical_line_is_closed_geometry_not_height(self):
        q=h.probe((F(0),F(1)),[[[0,0,0],[0,2,0],[0,0,2]]],native_admission=True)
        self.assertEqual(1,len(q['closedMembers']));self.assertEqual([],q['admittedNativeMembers'])
    def test_layer_height_never_substitutes_between_source_planes(self):
        q=h.probe((F(1,4),F(1,4)),[[[0,2,0],[2,2,0],[0,2,2]],[[0,9,0],[2,9,0],[0,9,2]]])
        self.assertEqual(['2','9'],[r['exactAffineHeightM']for r in q['closedMembers']]);self.assertTrue(q['noWholeCoverageOrMAXClaim'])
    def test_strict_outside_candidate_and_no_epsilon(self):
        tiny=F(1,2**50);q=h.probe((F(-1)*tiny,F(0)),[[[0,2,0],[2,2,0],[0,2,2]]])
        self.assertEqual([],q['closedMembers'])
    def test_ideal_convex_piece_boundary_is_rational_not_float_rounded(self):
        p=[(F(1,3),0,0),(1,0,0),(F(1,3),0,1)]
        self.assertTrue(h.convex_member((F(1,3),F(1)),p))
        self.assertFalse(h.convex_member((F(1,3)-F(1,2**100),F(1)),p))


if __name__=='__main__':unittest.main(verbosity=2)
