import unittest
import numpy as np
from fractions import Fraction as F
from west_wing26195_complete_finite_face_draft_v1_20261012 import CompleteGround,face_proof
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
class Tests(unittest.TestCase):
 def ground(self):return np.array([[[0,0,0],[2,0,0],[0,0,2]],[[2,0,0],[2,0,2],[0,0,2]],[[10,100,10],[12,100,10],[10,100,12]]],float)
 def compare(self,face):
  g=self.ground();p=face_proof(face,CompleteGround(g),0,None);q=finite(face,g)
  self.assertEqual(p['completeProjectionCovered'],q['groundProjectionCovered']);self.assertEqual(p['ordinaryFiniteProved'],q['existingOrdinaryClearanceBoundProved']);self.assertEqual(p['selection']['selectedOriginalGroundFaces'],q['allProjectedBoundingCandidateOriginalGroundFacets'])
 def test_clear_equivalent(self):self.compare([[.1,2,.1],[.5,2,.1],[.1,2,.5]])
 def test_negative_refined(self):
  p=face_proof([[.1,-1,.1],[.5,-1,.1],[.1,-1,.5]],CompleteGround(self.ground()),1,7);self.assertFalse(p['ordinaryFiniteProved']);self.assertEqual(F(p['exactMinimumFiniteColumnGapM']),-1)
 def test_vertical_touch_retained(self):self.compare([[2,1,0],[2,2,0],[2,1,1]])
 def test_zero_source_retained(self):self.compare([[0,1,0]]*3)
 def test_no_ground_failure(self):
  p=face_proof([[20,1,20]]*3,CompleteGround(self.ground()),3,None);self.assertFalse(p['ordinaryFiniteProved']);self.assertIsNone(p['exactLowerM'])
 def test_remapping_not_subset_relabel(self):
  g=np.concatenate([self.ground()[2:],self.ground()[:2]]);p=face_proof([[.1,-1,.1],[.5,-1,.1],[.1,-1,.5]],CompleteGround(g),0,None);self.assertEqual(p['originalGroundFaceBySelectedKernelFace'],[1,2]);self.assertEqual(p['allRefinedFiniteColumnPairs'][0]['originalGroundFace'],1);self.assertNotEqual(p['selectedGroundKernelProof']['completeCurrentGroundSHA256'],p['selection']['completeGroundSHA256'])
 def test_wrongheight_never_pruned(self):
  g=self.ground();g[0,:,1]=100;p=face_proof([[.1,1,.1],[.5,1,.1],[.1,1,.5]],CompleteGround(g),0,None);self.assertIn(0,p['selection']['selectedOriginalGroundFaces']);self.assertEqual(F(p['exactLowerM']),-99)
 def test_nonfinite_rejected(self):
  with self.assertRaises(AssertionError):CompleteGround([[[0,float('nan'),0]]*3])
if __name__=='__main__':unittest.main()
