"""UNEXECUTED pure fixtures for the bounded one-face packing alternative."""
from fractions import Fraction as F
import copy,unittest
import numpy as np
import polyu_face891_outside_float32_cell_enclosure_v1_draft_20261014 as h


class CellFixtures(unittest.TestCase):
    def test_exact_float32_node_has_zero_cell_width(self):self.assertEqual((F(2),F(2)),h.cell(F(2)))
    def test_non_dyadic_node_is_between_immediate_float32_neighbors(self):
        lo,hi=h.cell(F(1,3));self.assertLess(lo,F(1,3));self.assertGreater(hi,F(1,3))
        self.assertEqual(float(hi),float(np.nextafter(np.float32(float(lo)),np.float32(np.inf))))
    def test_negative_bin_transition_uses_both_closed_sides(self):
        lo,hi=h.cell(-F(1,3));self.assertLess(lo,-F(1,3));self.assertGreater(hi,-F(1,3))
    def test_subnormal_cell_is_not_arbitrary_epsilon(self):
        lo,hi=h.cell(F(1,2**150));self.assertEqual(F(0),lo);self.assertEqual(F(1,2**149),hi)
    def test_complete_convex_hull_encloses_all_ideal_edges(self):
        p=[(F(1,3),F(1,3)),(F(4,3),F(1,3)),(F(1,3),F(4,3))]
        result=h.enclose(p,[[0,2,0],[2,2,0],[0,2,2]],{})
        self.assertTrue(result['exactDrawnOutsideProjection']['completeClosedXZCovered'])
        self.assertTrue(result['noArbitraryBuffer']);self.assertGreater(result['exactHullExpansionAreaM2'],0)
    def test_original_float32_polygon_does_not_expand(self):
        result=h.enclose([(F(0),F(0)),(F(2),F(0)),(F(0),F(2))],[[0,2,0],[2,2,0],[0,2,2]],{})
        self.assertEqual(0,result['exactHullExpansionAreaM2'])
    def test_shared_vertex_uses_identical_cells_and_inputs_stay_immutable(self):
        p=[(F(1,3),F(0)),(F(2),F(0)),(F(1,3),F(2))];original=copy.deepcopy(p);shared={}
        first=h.enclose(p,[[0,2,0],[3,2,0],[0,2,3]],shared)
        second=h.enclose(list(reversed(p)),[[0,2,0],[3,2,0],[0,2,3]],shared)
        self.assertEqual(original,p);self.assertEqual(3,len(shared))
        self.assertEqual(first['exactFloat32CellEnclosingHull'],second['exactFloat32CellEnclosingHull'])
    def test_each_layer_y_comes_from_its_own_plane(self):
        p=[(F(1,3),F(0)),(F(2),F(0)),(F(1,3),F(2))]
        low=h.enclose(p,[[0,2,0],[3,2,0],[0,2,3]],{})
        high=h.enclose(p,[[0,100,0],[3,100,0],[0,100,3]],{})
        self.assertEqual(low['exactFloat32CellEnclosingHull'],high['exactFloat32CellEnclosingHull'])
        self.assertTrue(all(v[1]==100 for t in high['triangles']for v in t['packedPieceTriplet']))
    def test_sloped_plane_is_exact_before_storage_not_claimed_after(self):
        r=h.enclose([(F(1,3),F(0)),(F(2),F(0)),(F(1,3),F(2))],[[0,0,0],[3,1,0],[0,0,3]],{})
        self.assertGreater(r['maxAbsVerticalPackingResidualM'],0)
        self.assertTrue(r['expandedCurrentProtectedRegionCompatibilityPending'])
    def test_tiny_drawn_triangle_does_not_fabricate_height_index_credit(self):
        tiny=F(1,2**20);r=h.enclose([(F(0),F(0)),(tiny,F(0)),(F(0),tiny)],[[0,2,0],[2,2,0],[0,2,2]],{})
        self.assertTrue(r['exactDrawnOutsideProjection']['completeClosedXZCovered'])
        self.assertFalse(r['exactHeightAdmittedOutsideProjection']['completeClosedXZCovered'])
    def test_vertical_source_is_not_infilled(self):
        with self.assertRaisesRegex(AssertionError,'Vertical/zero'):h.enclose([(F(0),F(0)),(F(1),F(0)),(F(0),F(1))],[[0,0,0],[0,1,0],[0,0,1]],{})
    def test_shared_xz_does_not_donate_y_between_layers(self):
        p=[(F(1,3),F(0)),(F(2),F(0)),(F(1,3),F(2))];shared={}
        h.enclose(p,[[0,2,0],[3,2,0],[0,2,3]],shared)
        r=h.enclose(p,[[0,9,0],[3,9,0],[0,9,3]],shared)
        self.assertTrue(all(v[1]==9 for t in r['triangles']for v in t['packedPieceTriplet']))


if __name__=='__main__':unittest.main(verbosity=2)
