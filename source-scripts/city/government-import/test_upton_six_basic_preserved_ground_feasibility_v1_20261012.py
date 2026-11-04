import unittest
from fractions import Fraction as F
from upton_six_basic_preserved_ground_feasibility_v1_20261012 import polygon_masks,area,masked_current_pair,nonzero
class ExactSavedPreservation(unittest.TestCase):
 def setUp(self):self.m=[[0,0],[2,0],[0,2]];self.g=[[0,0,0],[2,0,0],[0,0,2]]
 def face(self,y):return[[0,y,0],[2,y,0],[0,y,2]]
 def test_current_burial_witness(self):
  q=masked_current_pair(self.face(-1),self.g,self.m);self.assertTrue(q['violatesExistingOrdinaryBound']);self.assertEqual(q['exactMinimumGapM'],'-1')
 def test_exact_limit(self):self.assertFalse(masked_current_pair(self.face(-.5),self.g,self.m)['violatesExistingOrdinaryBound'])
 def test_below_limit_without_epsilon(self):self.assertTrue(masked_current_pair(self.face(float.fromhex('-0x1.0000000000001p-1')),self.g,self.m)['violatesExistingOrdinaryBound'])
 def test_mask_excludes_buried_corner(self):
  q=masked_current_pair([[0,-2,0],[2,2,0],[0,2,2]],self.g,[[1,0],[2,0],[1,1]]);self.assertFalse(q['violatesExistingOrdinaryBound'])
 def test_closed_mask_boundary_witness(self):
  q=masked_current_pair(self.face(-1),self.g,[[2,0],[3,0],[2,1]]);self.assertTrue(q['violatesExistingOrdinaryBound']);self.assertEqual(len(q['completeConvexMaskedPairVertices']),1)
 def test_vertical_source_no_plane_inversion(self):
  q=masked_current_pair([[1,-1,0],[1,2,0],[1,2,1]],self.g,self.m);self.assertTrue(q['violatesExistingOrdinaryBound'])
 def test_opposite_ground_winding(self):self.assertEqual(masked_current_pair(self.face(1),self.g,self.m),masked_current_pair(self.face(1),self.g[::-1],self.m))
 def test_collapsed_current_kept_uncredited(self):self.assertTrue(masked_current_pair(self.face(0),[[0,0,0],[0,2,0],[0,2,1]],self.m)['collapsedCurrentGroundProjection'])
 def test_exact_source_zero_uncredited(self):self.assertTrue(masked_current_pair([[0,0,0],[1,0,0],[2,0,0]],self.g,self.m)['exactSourceZero'])
 def test_tiny_source_is_not_zero(self):self.assertTrue(nonzero([[0,0,0],[F(1,10**400),0,0],[0,1,0]]))
 def test_concave_ring_not_bbox(self):
  ring=[[0,0],[2,0],[2,1],[1,1],[1,2],[0,2]];m=polygon_masks(ring);self.assertEqual(len(m),4);self.assertEqual(sum(area(t)for t in m),6)
 def test_reversed_closed_ring(self):self.assertEqual(sum(area(t)for t in polygon_masks([[0,0],[0,2],[2,0],[0,0]])),4)
 def test_self_crossing_rejected(self):
  with self.assertRaises(AssertionError):polygon_masks([[0,0],[2,2],[0,2],[2,0]])
 def test_repeated_nonterminal_point_rejected(self):
  with self.assertRaises(AssertionError):polygon_masks([[0,0],[2,0],[0,2],[2,0]])
 def test_nonfinite_rejected(self):
  with self.assertRaises((AssertionError,ValueError,OverflowError)):masked_current_pair(self.face(float('nan')),self.g,self.m)
 def test_degenerate_mask_rejected(self):
  with self.assertRaises(AssertionError):masked_current_pair(self.face(1),self.g,[[0,0],[1,0],[2,0]])
if __name__=='__main__':unittest.main()
