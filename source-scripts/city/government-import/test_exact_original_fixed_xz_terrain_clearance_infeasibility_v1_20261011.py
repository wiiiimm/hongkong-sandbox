import unittest
from fractions import Fraction as F
from exact_original_fixed_xz_terrain_clearance_infeasibility_v1_20261011 import verify
class Infeasibility(unittest.TestCase):
 def setUp(self):self.source=[[0,0,0],[1,0,0],[0,0,1]];self.ground=[[0,2,0],[1,2,0],[0,2,1]];self.p=['1/4','0','1/4']
 def test_infeasible(self):self.assertTrue(verify(self.source,self.ground,self.p)['ordinaryClearanceInfeasibleForThisCandidateFamily'])
 def test_exact_threshold_is_not_infeasible(self):self.assertFalse(verify(self.source,self.ground,self.p,maximum_total_lowering_m=F(3,2))['ordinaryClearanceInfeasibleForThisCandidateFamily'])
 def test_above_limit_one_rational_unit(self):self.assertTrue(verify(self.source,self.ground,self.p,maximum_total_lowering_m=F(3,2)-F(1,10**20))['ordinaryClearanceInfeasibleForThisCandidateFamily'])
 def test_sloped_ground(self):r=verify(self.source,[[0,1,0],[1,3,0],[0,5,1]],self.p);self.assertEqual(F(r['exactAuthenticGroundHeightM']),F(5,2))
 def test_ground_outside(self):
  with self.assertRaises(AssertionError):verify(self.source,[[2,2,0],[3,2,0],[2,2,1]],self.p)
 def test_source_outside(self):
  with self.assertRaises(AssertionError):verify(self.source,self.ground,['2','0','2'])
 def test_wrong_source_plane(self):
  with self.assertRaises(AssertionError):verify(self.source,self.ground,['1/4','1','1/4'])
 def test_degenerate_source(self):
  with self.assertRaises(AssertionError):verify([[0,0,0]]*3,self.ground,self.p)
 def test_collapsed_ground(self):
  with self.assertRaises(AssertionError):verify(self.source,[[0,0,0],[0,1,0],[0,2,1]],self.p)
 def test_limits(self):
  for limit in [-1,float('nan'),float('inf'),True]:
   with self.assertRaises(AssertionError):verify(self.source,self.ground,self.p,maximum_total_lowering_m=limit)
 def test_cannot_weaken_ordinary(self):
  with self.assertRaises(AssertionError):verify(self.source,self.ground,self.p,ordinary_minimum_m=-3)
 def test_actual_hoi_body104_source3320(self):
  source=[[-804.9375,12.146200180053711,-4542.5859375],[-804.9375,6.4175004959106445,-4542.5859375],[-803.1796875,6.4175004959106445,-4544.091796875]]
  ground=[[-804.,9.542760372161865,-4540.5],[-803.5,9.617495059967041,-4540.5],[-804.28515625,9.028229236602783,-4543.5302734375]]
  p=['-2439477077/3033408','6729237/1048576','-165377089529/36400896'];r=verify(source,ground,p)
  self.assertEqual(F(r['exactAuthenticOrdinaryGapM']),F('-113828926355/42599448576'))
  self.assertTrue(r['ordinaryClearanceInfeasibleForThisCandidateFamily']);self.assertGreater(F(r['exactNecessaryTotalLoweringM']),2)
  self.assertFalse(r['rootOrBridgeCredit']);self.assertTrue(r['gradeSpanningRoleNotRejected'])
if __name__=='__main__':unittest.main()
