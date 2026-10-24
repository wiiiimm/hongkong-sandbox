"""DRAFT introduced-seam adverse cases, source-open context stays explicit."""
import unittest
from fractions import Fraction as F
from exact_faithful_multisurface_transition_mesh_v1_20261011 import production_faces,generated_seams
T=[(F(0),F(0),F(0)),(F(0),F(0),F(1)),(F(1),F(0),F(0))]
class Tests(unittest.TestCase):
 def test_original_open_edges_preserved_without_invented_failure(self):
  d=generated_seams([T],1,1);self.assertEqual(len(d['allPositive3DBoundaryAtomIds']),3)
 def test_introduced_open_edge_reject(self):
  with self.assertRaises(AssertionError):generated_seams([T],0,1)
 def test_point_touch_not_generated_seam(self):
  q=[(1,0,0),(1,0,1),(2,0,0)]
  with self.assertRaises(AssertionError):generated_seams([T,q],1,2)
 def test_nonmanifold_introduced_edge_reject(self):
  with self.assertRaises(AssertionError):generated_seams([T,list(reversed(T)),T],2,3)
 def test_same_direction_reject(self):
  with self.assertRaises(AssertionError):generated_seams([T,T],1,2)
 def test_existing_renderer_orientation_is_literal(self):
  q=list(reversed(T));r=production_faces([q]);self.assertEqual(r[0],[q[0],q[2],q[1]])
 def test_vertical_renderer_triangle_stays_drawn(self):
  q=[(0,0,0),(0,1,0),(0,0,1)];r=production_faces([q]);self.assertEqual(r[0],[tuple(map(F,p))for p in q])
 def test_byte_rendered_nodes_not_near_snap(self):
  r=production_faces([[(0,0,0),(0,F(1,10**12),1),(1,0,0)]]);self.assertNotEqual(r[0][1][1],0)
if __name__=='__main__':unittest.main()
