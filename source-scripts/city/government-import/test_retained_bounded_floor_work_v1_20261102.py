import unittest,numpy as np
from retained_bounded_floor_work_v1_20261102 import inset
class RetainedBoundedFloorWork(unittest.TestCase):
 def test_large_literal_retained_surface_is_not_charged_as_new_work(self):
  source=np.asarray([[[0,9,0],[0,9,1],[1,9,0]]],float)
  local=np.asarray([[[-10,10,-10],[-10,10,10],[10,10,-10]],[[10,10,10],[10,10,-10],[-10,10,10]]],float)
  far=np.repeat(np.asarray([[[0,10,0],[0,10,1],[1,10,0]]],float),25001,axis=0);far[:,:,0]+=1000+np.arange(len(far))[:,None]*2;far[:,:,2]+=1000
  terrain=np.concatenate([local,far]);out,p=inset(terrain,source);self.assertGreater(len(out),25000);self.assertTrue(p['outsideWorkFacesLiteral']);self.assertTrue(np.array_equal(out[:len(far)],far));self.assertEqual(p['boundedWorkInputFaces'],2);self.assertLessEqual(p['retainedWorkBudget']['newWorkFaces'],25000);self.assertTrue(p['retainedWorkBudget']['allParentFacesAccounted']);self.assertEqual(p['sourceClearanceM'],.05)
 def test_source_below_existing_land_minimum_still_fails(self):
  terrain=np.asarray([[[-10,2,-10],[-10,2,20],[20,2,-10]]],float);source=np.asarray([[[0,1,0],[0,1,1],[1,1,0]]],float)
  with self.assertRaises(AssertionError):inset(terrain,source)
if __name__=='__main__':unittest.main()
