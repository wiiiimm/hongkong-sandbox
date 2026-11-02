import unittest
import numpy as np
from exact_native_height_equivalence_v1_20261102 import verify


class ExactNativeHeightEquivalence(unittest.TestCase):
    def setUp(self):
        self.top=np.asarray([[[0,2,0],[0,2,4],[4,2,0]],[[4,2,4],[4,2,0],[0,2,4]]],float)
        self.bounds=[.25,.25,3.75,3.75]

    def test_retriangulated_equal_surface(self):
        other=np.asarray([[[0,2,0],[0,2,4],[4,2,4]],[[0,2,0],[4,2,4],[4,2,0]]],float)
        self.assertTrue(verify(self.top,other,self.bounds)['exactHighestHeightEquivalent'])

    def test_changed_hidden_lower_layer(self):
        lower=self.top.copy();lower[:,:,1]=1
        other=lower.copy();other[:,:,1]=0
        self.assertTrue(verify(np.concatenate([self.top,lower]),np.concatenate([self.top,other]),self.bounds)['exactHighestHeightEquivalent'])

    def test_single_float32_ulp_is_not_waived(self):
        other=self.top.copy();other[:,:,1]=np.nextafter(np.float32(2),np.float32(3))
        self.assertFalse(verify(self.top,other,self.bounds)['exactHighestHeightEquivalent'])

    def test_local_island_and_missing_coverage_fail(self):
        island=np.asarray([[[1,3,1],[1,3,2],[2,3,1]]],float)
        self.assertFalse(verify(self.top,np.concatenate([self.top,island]),self.bounds)['exactHighestHeightEquivalent'])
        self.assertFalse(verify(self.top,self.top[:1],self.bounds)['exactHighestHeightEquivalent'])

    def test_vertical_face_cannot_supply_height_credit(self):
        vertical=np.asarray([[[1,1,1],[1,3,1],[1,2,2]]],float)
        result=verify(self.top,vertical,self.bounds)
        self.assertFalse(result['exactHighestHeightEquivalent'])
        self.assertEqual(result['afterIndexedFacets'],0)


if __name__=='__main__':unittest.main()
