import unittest
import numpy as np
from exact_original_perpendicular_edge_facet_band_20261010 import verify
class Tests(unittest.TestCase):
 def wall(self,x=0):return np.array([[[x,-1,-1],[x,2,-1],[x,2,2]],[[x,-1,-1],[x,2,2],[x,-1,2]]],float)
 def test_exact_limit(self):self.assertTrue(verify([[.1,0,0],[.1,1,1]],self.wall())['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_next_float_real_gap(self):self.assertFalse(verify([[np.nextafter(.1,1),0,0],[np.nextafter(.1,1),1,1]],self.wall())['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_finite_missing_segment(self):self.assertFalse(verify([[0,0,0],[0,3,1]],self.wall())['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_far_opposite_wall_cannot_mask_near(self):self.assertTrue(verify([[0,0,0],[0,1,1]],np.concatenate([self.wall(),self.wall(40)]))['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_only_far_rejects(self):self.assertFalse(verify([[0,0,0],[0,1,1]],self.wall(40))['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_diagonal_plane_small_perpendicular_large_coordinate(self):
  t=self.wall();t[:,:,0]+=t[:,:,2]*10
  self.assertTrue(verify([[.5,0,0],[10.5,1,1]],t)['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_real_diagonal_gap_rejects(self):
  t=self.wall();t[:,:,0]+=t[:,:,2]*10
  self.assertFalse(verify([[2,0,0],[12,1,1]],t)['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_roof_is_not_facade(self):self.assertFalse(verify([[0,0,0],[1,0,1]],self.wall()[:,:,[1,0,2]])['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_gap_in_union_rejects(self):
  t=self.wall();t[0,:,1]=[-1,.4,.4];t[1,:,1]=[.6,2,2];self.assertFalse(verify([[0,0,0],[0,1,0]],t)['verifiedCompleteOriginalEdgePerpendicularBand'])
 def test_nonfinite_rejects(self):
  with self.assertRaises(AssertionError):verify([[float('nan'),0,0],[0,1,1]],self.wall())
if __name__=='__main__':unittest.main()
