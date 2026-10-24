import unittest,numpy as np
from exact_subgrade_face_coverage_v1 import prove
class SubgradeTests(unittest.TestCase):
 def ground(self,y):return np.array([[[-1,y,-1],[3,y,-1],[-1,y,1]],[[3,y,-1],[3,y,1],[-1,y,1]]],float)
 def test_vertical_wall_fully_below_ground(self):
  p=prove([[0,0,0],[0,5,0],[2,0,0]],self.ground(6));self.assertTrue(p['wholeOriginalFaceAtOrBelowFiniteTerrain']);self.assertEqual(p['exactUncoveredSourceUVArea'],'0')
 def test_exposed_upper_tip_remains_uncovered(self):
  self.assertFalse(prove([[0,0,0],[0,7,0],[2,0,0]],self.ground(6))['wholeOriginalFaceAtOrBelowFiniteTerrain'])
 def test_missing_finite_ground_cannot_cover_wall(self):
  self.assertFalse(prove([[0,0,0],[0,5,0],[20,0,0]],self.ground(6))['wholeOriginalFaceAtOrBelowFiniteTerrain'])
 def test_higher_finite_surface_can_cover_lower_overlapping_surface(self):
  self.assertTrue(prove([[0,0,0],[0,5,0],[2,0,0]],np.concatenate([self.ground(-2),self.ground(6)]))['wholeOriginalFaceAtOrBelowFiniteTerrain'])
if __name__=='__main__':unittest.main()
