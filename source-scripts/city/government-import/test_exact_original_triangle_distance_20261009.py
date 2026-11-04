import unittest
from fractions import Fraction as F
from exact_original_triangle_distance_20261009 import triangle_distance
class Distance(unittest.TestCase):
 def distance(self,a,b):return F(triangle_distance(a,b)['exactSquaredDistanceM2'])
 def test_parallel_planes_continuous_interior(self):
  a=[[0,0,0],[4,0,0],[0,0,4]];b=[[1,2,1],[2,2,1],[1,2,2]];self.assertEqual(self.distance(a,b),4)
 def test_crossing_edges_not_vertex_distance(self):
  a=[[-2,0,0],[2,0,0],[0,-1,0]];b=[[0,1,-2],[0,1,2],[0,2,0]];self.assertEqual(self.distance(a,b),1)
 def test_exact_crossing_faces(self):
  self.assertEqual(self.distance([[0,0,0],[2,0,0],[0,0,2]],[[.5,-1,.5],[.5,1,.5],[1,0,1]]),0)
 def test_nested_coplanar_contact(self):
  self.assertEqual(self.distance([[0,0,0],[3,0,0],[0,0,3]],[[.1,0,.1],[1,0,.1],[.1,0,1]]),0)
 def test_point_degenerate_not_omitted(self):
  self.assertEqual(self.distance([[1,3,1]]*3,[[0,0,0],[4,0,0],[0,0,4]]),9)
 def test_segment_degenerate_not_omitted(self):
  self.assertEqual(self.distance([[-2,2,0],[2,2,0],[0,2,0]],[[0,0,-2],[0,0,2],[0,0,0]]),4)
 def test_symmetric_distance(self):
  a=[[0,0,0],[2,0,0],[0,0,2]];b=[[4,1,0],[6,1,0],[4,1,2]];self.assertEqual(self.distance(a,b),self.distance(b,a));self.assertEqual(self.distance(a,b),5)
 def test_near_miss_never_exact_contact(self):
  a=[[0,0,0],[2,0,0],[0,0,2]];b=[[0,.001,0],[2,.001,0],[0,.001,2]];r=triangle_distance(a,b);self.assertFalse(r['exactOriginalContact']);self.assertFalse(r['supportCredit'])
if __name__=='__main__':unittest.main()
