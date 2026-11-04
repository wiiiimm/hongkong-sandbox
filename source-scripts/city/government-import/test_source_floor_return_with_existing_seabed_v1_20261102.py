import unittest,numpy as np
from source_floor_return_with_existing_seabed_v1_20261102 import inset
class RetainedSeabedTests(unittest.TestCase):
    def setUp(self):
        self.land=np.array([[[0,5,0],[20,5,0],[0,5,20]],[[20,5,0],[20,5,20],[0,5,20]]],dtype=float)
        self.water=np.array([[[30,-4,0],[35,-4,0],[30,-4,5]]],dtype=float)
        self.ground=np.concatenate([self.land,self.water]);self.source=np.array([[[6,4.3,6],[8,4.3,6],[6,4.3,8]]])
    def test_retains_original_seabed_and_land_floor(self):
        after,p=inset(self.ground,self.source)
        self.assertTrue(any(np.array_equal(t,self.water[0])for t in after));self.assertTrue(p['unchangedSeabedFacesRetained'])
        self.assertEqual(p['sourceClearanceM'],.05)
        self.assertTrue(all(after[i,:,1].min()>=1.2 for i,r in enumerate(p['outputLineage'])if r['kind']in ['ramp-plane-core','ramp-derived-return']))
    def test_rejects_new_land_below_existing_minimum(self):
        source=self.source.copy();source[:,:,1]=1.24
        with self.assertRaises(AssertionError):inset(self.ground,source)
    def test_does_not_edit_input_source_or_terrain(self):
        source=self.source.copy();terrain=self.ground.copy();inset(self.ground,self.source)
        np.testing.assert_array_equal(source,self.source);np.testing.assert_array_equal(terrain,self.ground)
if __name__=='__main__':unittest.main()
