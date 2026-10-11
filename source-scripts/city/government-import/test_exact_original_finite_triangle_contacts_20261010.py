from fractions import Fraction as F
import unittest
import numpy as np
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_finite_triangle_contacts_20261010 import finite_intersection_points,dimension,primitive_census,exact_finite_contacts
def face(*p):return rational_face(p)
TRI=face((0,0,0),(2,0,0),(0,2,0))
class ExactFiniteOriginals(unittest.TestCase):
 def test_ordinary_triangles_unchanged(self):
  b=face((1,-1,0),(1,1,0),(3,1,0));self.assertEqual(finite_intersection_points(TRI,b),intersection_points(TRI,b))
 def test_authored_collinear_middle_vertex_preserved(self):
  a=face((-1,1,0),(1,1,0),(3,1,0));self.assertEqual(finite_intersection_points(a,TRI),{(F(0),F(1),F(0)),(F(1),F(1),F(0))})
 def test_transverse_segment_inside(self):
  a=face((F(1,2),F(1,2),-1),(F(1,2),F(1,2),0),(F(1,2),F(1,2),1));self.assertEqual(len(finite_intersection_points(a,TRI)),1)
 def test_transverse_segment_outside(self):
  a=face((3,3,-1),(3,3,0),(3,3,1));self.assertFalse(finite_intersection_points(a,TRI))
 def test_parallel_distinct_planes(self):
  z=2.0**-80;a=face((0,0,z),(1,0,z),(2,0,z));self.assertFalse(finite_intersection_points(a,TRI))
 def test_point_in_triangle(self):
  a=face((1,1,0),(1,1,0),(1,1,0));self.assertEqual(finite_intersection_points(a,TRI),{a[0]})
 def test_point_just_outside(self):
  a=face((-2.0**-80,0,0),(-2.0**-80,0,0),(-2.0**-80,0,0));self.assertFalse(finite_intersection_points(a,TRI))
 def test_point_point_distinct(self):
  a=face((0,0,0),(0,0,0),(0,0,0));b=face((0,0,2.0**-80),(0,0,2.0**-80),(0,0,2.0**-80));self.assertFalse(finite_intersection_points(a,b))
 def test_collinear_segment_overlap(self):
  a=face((0,0,0),(1,0,0),(2,0,0));b=face((1,0,0),(2,0,0),(3,0,0));self.assertEqual(finite_intersection_points(a,b),{(F(1),F(0),F(0)),(F(2),F(0),F(0))})
 def test_collinear_segment_disjoint(self):
  a=face((0,0,0),(1,0,0),(2,0,0));b=face((3,0,0),(4,0,0),(5,0,0));self.assertFalse(finite_intersection_points(a,b))
 def test_skew_segments(self):
  a=face((0,0,0),(1,0,0),(2,0,0));b=face((1,-1,2.0**-80),(1,0,2.0**-80),(1,1,2.0**-80));self.assertFalse(finite_intersection_points(a,b))
 def test_crossing_segments(self):
  a=face((0,0,0),(1,0,0),(2,0,0));b=face((1,-1,0),(1,0,0),(1,1,0));self.assertEqual(finite_intersection_points(a,b),{(F(1),F(0),F(0))})
 def test_tiny_true_area_is_not_degenerate(self):
  a=face((0,0,0),(1,0,0),(0,2.0**-80,0));self.assertEqual(dimension(a),2)
 def test_complete_census_preserves_all_faces(self):
  a=np.asarray([TRI,face((0,0,0),(1,0,0),(2,0,0)),face((1,1,0),(1,1,0),(1,1,0))],dtype=float);c=primitive_census(a);self.assertEqual(c['exactPointFaceIDs'],[2]);self.assertEqual(c['exactSegmentFaceIDs'],[1]);self.assertEqual(c['exactAreaFaceIDs'],[0])
 def test_point_contact_never_positive_dimension(self):
  a=np.asarray([face((1,1,0),(1,1,0),(1,1,0))],dtype=float);b=np.asarray([TRI],dtype=float);r=exact_finite_contacts(a,[0],b,[0]);self.assertEqual(r['contacts'][0]['dimension'],0);self.assertFalse(r['physicalSupportAccepted'])
 def test_resource_bound_not_increased(self):
  a=np.asarray([TRI],dtype=float)
  with self.assertRaises(AssertionError):exact_finite_contacts(a,[0],a,[0],maximum_pairs=0)
 def test_swapping_hulls_symmetric(self):
  a=face((-1,1,0),(1,1,0),(3,1,0));self.assertEqual(finite_intersection_points(a,TRI),finite_intersection_points(TRI,a))
if __name__=='__main__':unittest.main()
