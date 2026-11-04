"""Exact closed finite source-piece necessary anchor tests; no mesh approval."""
import unittest
from fractions import Fraction as F
from mongkok_stadium240332_one_ring_inner_outer_anchor_feasibility_v1_20261011 import closed_height,boundary_nodes
class Tests(unittest.TestCase):
 def setUp(self):self.tri=[(0,1,0),(2,3,0),(0,5,2)]
 def test_interior_rational(self):self.assertEqual(closed_height(self.tri,(F(1,3),F(2,3))),F(8,3))
 def test_closed_vertex(self):self.assertEqual(closed_height(self.tri,(F(0),F(0))),1)
 def test_closed_edge(self):self.assertEqual(closed_height(self.tri,(F(1),F(1))),4)
 def test_outside(self):self.assertIsNone(closed_height(self.tri,(F(2),F(2))))
 def test_tiny_outside_not_snapped(self):self.assertIsNone(closed_height(self.tri,(F(-1,10**30),F(0))))
 def test_collinear_prefix(self):self.assertEqual(closed_height([(0,1,0),(1,2,0),(2,3,0),(0,5,2)],(F(1),F(0))),2)
 def test_reversed_reject(self):
  with self.assertRaises(AssertionError):closed_height(list(reversed(self.tri)),(F(0),F(0)))
 def test_degenerate_reject(self):
  with self.assertRaises(AssertionError):closed_height([(0,0,0),(1,1,0),(2,2,0)],(F(0),F(0)))
 def test_nonfinite_reject(self):
  with self.assertRaises(ValueError):closed_height([(0,'nan',0),(2,3,0),(0,5,2)],(F(0),F(0)))
 def test_conflicting_incidence_preserved(self):
  d={'allBoundaryAtomicEdges':[{'allOriginalIncidences':[{'face':0,'start':['0','0'],'end':['1','0'],'exactEndpointY':['1','2']}]},{'allOriginalIncidences':[{'face':1,'start':['1','0'],'end':['0','0'],'exactEndpointY':['3','1']}]}]};n=boundary_nodes(d);self.assertEqual({r['height']for r in n[(F(1),F(0))]},{F(2),F(3)})
if __name__=='__main__':unittest.main()
