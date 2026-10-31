import unittest
import numpy as np
from fractions import Fraction as F
from exact_original_rational_interface_segment_clearance_20261011 import verify
class Tests(unittest.TestCase):
 def setUp(self):self.g=np.array([[[-1,0,-1],[2,0,-1],[-1,0,2]],[[2,0,2],[-1,0,2],[2,0,-1]]],float);self.s=[['0','1','0'],['1','1','0']]
 def test_clear(self):self.assertTrue(verify(self.s,self.g)['strictlyExposedWholePositiveInterface'])
 def test_raise_island(self):
  island=np.array([[[.4,2,-.1],[.6,2,-.1],[.5,2,.1]]]);r=verify(self.s,np.concatenate([self.g,island]));self.assertFalse(r['strictlyExposedWholePositiveInterface']);self.assertEqual(F(r['exactMinimumGapM']),-1)
 def test_missing_ground(self):self.assertFalse(verify(self.s,np.array([[[0,0,0],[.4,0,0],[0,0,1]]]))['closedWholeSegmentProjectionCovered'])
 def test_boundary_inside(self):self.assertTrue(verify([['-1','1','-1'],['2','1','-1']],self.g)['strictlyExposedWholePositiveInterface'])
 def test_outside_tiny(self):self.assertFalse(verify([['-1','1','-100000001/100000000'],['2','1','-100000001/100000000']],self.g)['closedWholeSegmentProjectionCovered'])
 def test_vertical(self):self.assertTrue(verify([['0','1','0'],['0','2','0']],self.g)['strictlyExposedWholePositiveInterface'])
 def test_zero_gap(self):self.assertFalse(verify([['0','0','0'],['1','0','0']],self.g)['strictlyExposedWholePositiveInterface'])
 def test_exact_rational_no_round_trip(self):self.assertEqual(verify([['1/3','1','0'],['2/3','1','0']],self.g)['exactEndpoints'][0][0],'1/3')
 def test_collapsed_no_cover(self):self.assertFalse(verify(self.s,np.array([[[0,0,0],[1,0,0],[.5,0,0]]]))['closedWholeSegmentProjectionCovered'])
 def test_collapsed_height_kept(self):
  r=verify(self.s,np.concatenate([self.g,np.array([[[.4,2,0],[.6,2,0],[.5,2,0]]])]))
  self.assertFalse(r['strictlyExposedWholePositiveInterface']);self.assertEqual(F(r['exactMinimumGapM']),-1)
 def test_point_and_float_rejected(self):
  for s in [[self.s[0],self.s[0]],[[0.,1.,0.],[1.,1.,0.]]]:
   with self.assertRaises(AssertionError):verify(s,self.g)
 def test_nonfinite(self):
  g=self.g.copy();g[0,0,1]=np.nan
  with self.assertRaises(AssertionError):verify(self.s,g)
if __name__=='__main__':unittest.main()
