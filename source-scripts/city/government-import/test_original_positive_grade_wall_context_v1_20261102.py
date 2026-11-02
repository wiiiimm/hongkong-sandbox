import unittest
import numpy as np
from original_positive_grade_wall_context_v1_20261102 import wall_evidence
class GradeWallTests(unittest.TestCase):
 def setUp(self):
  self.wall=np.array([[0.,-1.,0.],[0.,3.,0.],[0.,3.,2.]])
  self.ground=np.array([[[-2.,0.,-2.],[2.,0.,-2.],[0.,0.,4.]]])
 def test_positive_grade_and_exposure(self):
  r=wall_evidence(self.wall,self.ground,[0]);self.assertGreater(r['independentlyRecomputedPositiveGradeContact']['dimension'],0);self.assertEqual(r['exactExposedMargin'],'3')
 def test_reject_missing_grade(self):
  with self.assertRaises(AssertionError):wall_evidence(self.wall,self.ground,[])
 def test_reject_covered_top(self):
  with self.assertRaises(AssertionError):wall_evidence(self.wall,self.ground+np.array([0.,4.,0.]),[0])
 def test_reject_point_only_grade(self):
  point_ground=np.array([[[0.,0.,0.],[2.,0.,0.],[2.,0.,-2.]]])
  with self.assertRaises(AssertionError):wall_evidence(self.wall,point_ground,[0])
 def test_reject_nonwall(self):
  with self.assertRaises(AssertionError):wall_evidence(self.ground[0],self.ground,[0])
if __name__=='__main__':unittest.main()
