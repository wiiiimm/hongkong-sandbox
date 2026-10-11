"""Pruning preserves complete exact pair constraints and real failures."""
import unittest
import numpy as np
from exact_original_paired_finite_clearance_v2_20261010 import verify as old
from exact_original_paired_finite_clearance_v3_20261011 import verify

class Equivalence(unittest.TestCase):
 def compare(self,s,g):
  a=old(s,g);b=verify(s,g)
  for k in ['exactCertifiedLowerClearanceM','existingOrdinaryClearanceBoundProved','groundProjectionCovered','sourceFaceSHA256','completeCurrentGroundSHA256','allExactFiniteSourceGroundPieces']:
   self.assertEqual(a[k],b[k],k)
  self.assertEqual(a['completeOriginalProjectionCoverage'],b['completeOriginalProjectionCoverage'])
  self.assertTrue(b['oldPairedV1OrV2NotRewritten']);self.assertNotIn('rawPriorPairedProofVerbatim',b)
  return b
 def fixtures(self,y=0):
  return np.array([[[0,y,0],[2,y,0],[0,y,2]],[[2,y,0],[2,y,2],[0,y,2]]],float)
 def test_horizontal(self):self.compare([[.2,.2,.2],[1.8,.2,.2],[.2,.2,1.8]],self.fixtures())
 def test_vertical(self):self.compare([[1,-.2,.1],[1,.8,1.9],[1,2,.1]],self.fixtures())
 def test_almost_vertical(self):self.compare([[1,-.2,.1],[1+2**-30,.8,1.9],[1,2,.1]],self.fixtures())
 def test_sloping_terrain(self):
  g=self.fixtures();g[:,:,1]=g[:,:,0]/4+g[:,:,2]/8;self.compare([[.2,.2,.2],[1.8,.9,.2],[.2,.7,1.8]],g)
 def test_overlapping_upper_surface(self):
  g=np.concatenate([self.fixtures(),self.fixtures(.4)]);p=self.compare([[.2,0,.2],[1.8,0,.2],[.2,0,1.8]],g);self.assertEqual(float(p['exactCertifiedLowerClearanceM']),-.4)
 def test_burial(self):self.assertFalse(self.compare([[.2,-.51,.2],[1.8,-.51,.2],[.2,-.51,1.8]],self.fixtures())['existingOrdinaryClearanceBoundProved'])
 def test_exact_threshold(self):self.assertTrue(self.compare([[.2,-.5,.2],[1.8,-.5,.2],[.2,-.5,1.8]],self.fixtures())['existingOrdinaryClearanceBoundProved'])
 def test_true_tiny_gap(self):
  g=self.fixtures();g[0,1,0]-=2**-30;g[0,2,2]-=2**-30;p=self.compare([[.1,.1,.1],[1.9,.1,.1],[.1,.1,1.9]],g);self.assertFalse(p['groundProjectionCovered'])
 def test_point_projection(self):self.compare([[1,0,1],[1,.5,1],[1,1,1]],self.fixtures())
 def test_collapsed_ground_crossing(self):
  g=np.concatenate([self.fixtures(),np.array([[[1,-2,0],[1,2,2],[1,0,1]]],float)]);self.compare([[.2,.2,.2],[1.8,.2,.2],[.2,.2,1.8]],g)
 def test_closed_touching(self):self.compare([[0,0,0],[0,1,1],[0,2,2]],self.fixtures())
 def test_nonfinite(self):
  with self.assertRaises(AssertionError):verify([[0,float('nan'),0],[1,0,0],[0,0,1]],self.fixtures())
if __name__=='__main__':unittest.main()
