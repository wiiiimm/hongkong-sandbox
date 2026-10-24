import unittest
import numpy as np
import shapely
from bounded_float32_terrain_gap_boxes_v2_20261010 import bounded_boxes,down,up

class BoundedBoxesTests(unittest.TestCase):
    def check(self,p):
        rows,proof=bounded_boxes(p)
        self.assertTrue(rows)
        self.assertEqual(proof["exactInputAreaM2"],proof["exactOutputAreaM2"])
        self.assertEqual(p.difference(shapely.union_all([b for a,b in rows])).area,0)
        for a,b in rows:
            self.assertGreater(a["positiveAreaM2"],0);self.assertLess(a["positiveAreaM2"],.0001);self.assertLess(b.area,.1)
            self.assertTrue(a["exactClippedRings"])
            self.assertTrue(np.array_equal(np.asarray(b.bounds,dtype=np.float32).astype(float),b.bounds))
        self.assertFalse(proof['exactFiniteAcceptance'])
        return rows
    def test_long_diagonal_sliver(self):
        p=shapely.Polygon([(-12889.,-16885.),(-12883.,-16878.),(-12883.,-16877.9999),(-12889.,-16884.9999)])
        self.assertGreater(len(self.check(p)),10)
    def test_wide_positive_gap_split_without_limit_increase(self):
        self.assertGreater(len(self.check(shapely.box(0,0,.1,.1))),1)
    def test_tiny_positive_polygon_retained(self):
        self.check(shapely.Polygon([(0.,0.),(1.,1.),(1.,1.+2**-40)]))
    def test_hole_retained_in_piece_accounting(self):
        self.check(shapely.Polygon([(0,0),(.01,0),(.01,.01),(0,.01)],holes=[[(.002,.002),(.008,.002),(.008,.008),(.002,.008)]]))
    def test_actual_large_coordinate_short_strip(self):
        self.check(shapely.box(-12855.6875,-16895.107421875,-12855.620286673367,-16894.191517732383))
    def test_outward_rounding_both_signs(self):
        for x in [1.0000000001,-1.0000000001,12855.620286673367,-12855.620286673367]:
            self.assertLessEqual(down(x),x);self.assertGreaterEqual(up(x),x)
    def test_nonfinite_rejected(self):
        for x in [float('nan'),float('inf'),float('-inf'),1e300]:
            with self.assertRaises(ValueError):down(x)
            with self.assertRaises(ValueError):up(x)
    def test_zero_area_rejected(self):
        with self.assertRaises(ValueError):bounded_boxes(shapely.Polygon([(0,0),(1,1),(2,2)]))
    def test_nonpolygon_rejected(self):
        with self.assertRaises(ValueError):bounded_boxes(shapely.LineString([(0,0),(1,1)]))
    def test_resource_budget_rejected(self):
        with self.assertRaises(ValueError):bounded_boxes(shapely.box(0,0,1,1),max_pieces=1)

    def test_active_piece_counts_against_exact_two_piece_boundary(self):
        p=shapely.box(0,0,.015,.01)
        rows,proof=bounded_boxes(p,max_pieces=2)
        self.assertEqual(len(rows),2)
        with self.assertRaises(ValueError):bounded_boxes(p,max_pieces=1)

if __name__=='__main__':unittest.main()
