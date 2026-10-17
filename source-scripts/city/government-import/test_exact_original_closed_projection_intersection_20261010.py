import unittest
from exact_original_closed_projection_intersection_20261010 import intersection
class ClosedProjection(unittest.TestCase):
 def test_disjoint_lines_with_overlapping_bounds(self):self.assertEqual(intersection([[0,0],[1,1],[.5,.5]],[[0,.1],[.9,1],[.45,.55]]),[])
 def test_touching_endpoint_retained(self):self.assertTrue(intersection([[0,0],[1,1]],[[1,1],[2,0]]))
 def test_crossing_lines_retained(self):self.assertTrue(intersection([[0,0],[1,1]],[[0,1],[1,0]]))
 def test_collinear_overlap_retained(self):self.assertEqual(len(intersection([[0,0],[1,1]],[[.5,.5],[2,2]])),2)
 def test_collinear_real_gap_retained(self):self.assertEqual(intersection([[0,0],[1,1]],[[1.000000000000001,1.000000000000001],[2,2]]),[])
 def test_point_on_line(self):self.assertTrue(intersection([[.5,.5]],[[0,0],[1,1]]))
 def test_point_off_line(self):self.assertEqual(intersection([[.5,.500000000000001]],[[0,0],[1,1]]),[])
 def test_vertical_point_in_triangle(self):self.assertTrue(intersection([[.1,.1],[.1,.1]],[[0,0],[1,0],[0,1]]))
 def test_line_crosses_triangle(self):self.assertTrue(intersection([[-1,.1],[2,.1]],[[0,0],[1,0],[0,1]]))
 def test_triangle_disjoint(self):self.assertEqual(intersection([[0,0],[1,0],[0,1]],[[2,2],[3,2],[2,3]]),[])
if __name__=='__main__':unittest.main()
