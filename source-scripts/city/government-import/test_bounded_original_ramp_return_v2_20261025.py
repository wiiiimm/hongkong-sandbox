import unittest
import numpy as np
from bounded_original_ramp_return_v1_20261025 import inset as prior
from bounded_original_ramp_return_v2_20261025 import inset

class DisconnectedReturns(unittest.TestCase):
 def test_distant_planes_do_not_lower_other_domains(self):
  terrain=np.array([[[-10,10,-10],[110,10,-10],[110,10,10]],[[-10,10,-10],[110,10,10],[-10,10,10]]],float)
  ramps=np.array([[[0,8,0],[0,8,1],[1,7,0]],[[100,8,0],[100,8,1],[101,9,0]]],float)
  with self.assertRaises(AssertionError):prior(terrain,ramps)
  result,proof=inset(terrain,ramps)
  self.assertEqual(len(proof['componentProofs']),2)
  self.assertGreaterEqual(result[:,:,1].min(),1.2)
  self.assertAlmostEqual(proof['removedProjectedAreaM2'],proof['insertedProjectedAreaM2'],places=6)
 def test_one_domain_is_identical_to_existing_kernel(self):
  terrain=np.array([[[-10,10,-10],[10,10,-10],[10,10,10]],[[-10,10,-10],[10,10,10],[-10,10,10]]],float)
  ramps=np.array([[[0,8,0],[0,8,1],[1,9,0]]],float)
  a,_=prior(terrain,ramps);b,p=inset(terrain,ramps)
  self.assertTrue(np.array_equal(a,b));self.assertEqual(len(p['componentProofs']),1)
if __name__=='__main__':unittest.main()
