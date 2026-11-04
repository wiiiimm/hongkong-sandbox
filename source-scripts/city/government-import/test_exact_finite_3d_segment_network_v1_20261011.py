import unittest
from exact_finite_3d_segment_network_v1_20261011 import intersect,network
class Cases(unittest.TestCase):
 def test_crossing(self):self.assertEqual(intersect([0,0,0],[2,0,0],[1,-1,0],[1,1,0])['kind'],'exact-point-incidence')
 def test_skew_height(self):self.assertEqual(intersect([0,0,0],[2,0,0],[1,-1,2**-40],[1,1,2**-40])['kind'],'disjoint')
 def test_collinear_overlap(self):self.assertEqual(intersect([0,0,0],[2,0,0],[1,0,0],[3,0,0])['kind'],'positive-collinear-overlap')
 def test_parallel(self):self.assertEqual(intersect([0,0,0],[2,0,0],[0,1,0],[2,1,0])['kind'],'disjoint')
 def test_endpoint(self):self.assertEqual(intersect([0,0,0],[1,0,0],[1,0,0],[1,1,0])['kind'],'exact-point-incidence')
 def test_disjoint_collinear(self):self.assertEqual(intersect([0,0,0],[1,0,0],[2,0,0],[3,0,0])['kind'],'disjoint')
 def test_tiny_gap(self):self.assertEqual(intersect([0,0,0],[1,0,0],[1+2**-40,0,0],[2,0,0])['kind'],'disjoint')
 def test_zero(self):
  with self.assertRaises(AssertionError):intersect([0,0,0],[0,0,0],[0,0,0],[1,0,0])
 def test_nonfinite(self):
  for x in [float('inf'),float('-inf'),float('nan'),'inf']:
   with self.assertRaises(AssertionError):intersect([x,0,0],[1,0,0],[0,0,0],[1,0,0])
 def test_schema(self):
  with self.assertRaises(AssertionError):intersect([0,0],[1,0,0],[0,0,0],[1,0,0])
 def test_closed_triangle(self):
  a,b,c=[0,0,0],[1,0,0],[0,1,0];r=network([[a,b],[b,c],[c,a]]);self.assertEqual(r['cycleRank'],1);self.assertFalse(r['qualifiedTerrainFrontier'])
 def test_open_tree(self):self.assertEqual(network([[[0,0,0],[1,0,0]],[[1,0,0],[2,0,0]]])['cycleRank'],0)
 def test_interior_split(self):
  r=network([[[0,0,0],[2,0,0]],[[1,-1,0],[1,1,0]]]);self.assertEqual(len(r['atomicEdges']),4);self.assertEqual(r['cycleRank'],0)
 def test_duplicate_preserved(self):
  r=network([[[0,0,0],[1,0,0]],[[1,0,0],[0,0,0]]]);self.assertEqual(r['positiveOverlapPairs'],1);self.assertEqual(len(r['atomicEdges'][0]['sourceSegmentIncidences']),2)
 def test_y_axis(self):self.assertEqual(intersect([0,0,0],[0,2,0],[0,1,0],[0,3,0])['kind'],'positive-collinear-overlap')
 def test_z_axis(self):self.assertEqual(intersect([0,0,0],[0,0,2],[0,0,1],[0,0,3])['kind'],'positive-collinear-overlap')
if __name__=='__main__':unittest.main()
