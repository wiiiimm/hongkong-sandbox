import unittest
import numpy as np
from retained_native_floor_domains_v1_20261102 import inset
from bounded_original_upward_floor_domains_v4_20261102 import inset as all_land

def floor(x,y):return np.array([[x,y,3.],[x,y,4.],[x+1,y,3.]])
def terrain():return np.array([[[0.,6.,0.],[0.,6.,20.],[40.,6.,0.]],[[40.,6.,0.],[0.,6.,20.],[40.,6.,20.]]])
class RetainedDomainsTests(unittest.TestCase):
    def test_matches_existing_all_land_geometry(self):
        source=np.array([floor(5,2),floor(25,4)]);after,proof=inset(terrain(),source);expected,_=all_land(terrain(),source)
        np.testing.assert_array_equal(after,expected);self.assertEqual(len(proof['componentProofs']),2)
        self.assertEqual(proof['componentProofs'][0]['sourceDerivedMinimumTerrainY'],1.95)
        self.assertEqual(proof['componentProofs'][1]['sourceDerivedMinimumTerrainY'],3.95)
    def test_preserves_old_low_face_and_inputs(self):
        low=np.array([[[100.,1.,0.],[100.,1.,1.],[101.,1.1,0.]]]);before=np.concatenate([terrain(),low]);source=np.array([floor(5,2),floor(25,4)]);copy=before.copy();scopy=source.copy();after,p=inset(before,source)
        np.testing.assert_array_equal(before,copy);np.testing.assert_array_equal(source,scopy)
        self.assertEqual(p['existingLowTerrainProof']['existingLowFaces'],1);self.assertTrue(any(np.array_equal(t,low[0])for t in after))
    def test_low_face_in_edit_domain_rejected(self):
        low=np.array([floor(5,1.)]);
        with self.assertRaises(AssertionError):inset(np.concatenate([terrain(),low]),np.array([floor(5,2.)]))
    def test_source_below_new_land_floor_rejected(self):
        with self.assertRaises(AssertionError):inset(terrain(),np.array([floor(5,1.)]))
if __name__=='__main__':unittest.main()
