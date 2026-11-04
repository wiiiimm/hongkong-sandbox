import unittest
from fractions import Fraction as F
from original_grade_partition_v1 import partition_triangle,area_vector
class GradePartitionTests(unittest.TestCase):
 def test_wholly_above_and_below_preserve_vertices(self):
  f=[(0,2,0),(2,2,0),(0,3,0)];a,b=partition_triangle(f,1);self.assertEqual(a,[tuple(tuple(F(v)for v in p)for p in f)]);self.assertEqual(b,[])
  a,b=partition_triangle(f,4);self.assertFalse(a);self.assertEqual(len(b),1)
 def test_crossing_exact_intersections_and_vector_area(self):
  f=[(0,-1,0),(2,1,0),(0,1,2)];a,b=partition_triangle(f,0);self.assertEqual(len(a),2);self.assertEqual(len(b),1);points={p for t in a+b for p in t};self.assertIn((F(1),F(0),F(0)),points);self.assertIn((F(0),F(0),F(1)),points);self.assertEqual(area_vector(a+b),(F(4),F(-4),F(4)))
 def test_coplanar_facet_accounted_once(self):
  a,b=partition_triangle([(0,4,0),(1,4,0),(0,4,1)],4);self.assertEqual(len(a),1);self.assertFalse(b)
 def test_boundary_only_has_no_cap_or_duplicate_area(self):
  a,b=partition_triangle([(0,0,0),(1,-1,0),(0,-1,1)],0);self.assertFalse(a);self.assertEqual(len(b),1)
 def test_degenerate_original_still_accounted(self):
  a,b=partition_triangle([(0,-1,0),(0,1,0),(0,2,0)],0);self.assertEqual(len(a)+len(b),1);self.assertEqual(area_vector(a+b),(0,0,0))
if __name__=='__main__':unittest.main()
