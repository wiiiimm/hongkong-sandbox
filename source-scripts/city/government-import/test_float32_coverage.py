import copy,unittest
from float32_coverage import approve_roundoff,geometry_sha

class CoverageTest(unittest.TestCase):
    def mesh(self,gap,width=1):
        return {'nativeMesh':{'position':[0,0,0, width,0,0, width,0,1-gap, 0,0,1-gap],
                              'index':[0,1,2,0,2,3],'source':{}}}
    def test_tiny_edge_sliver_declared_without_geometry_change(self):
        p=self.mesh(.001);before=geometry_sha(p);proof=approve_roundoff(p,[0,0,1,1]);self.assertEqual(before,geometry_sha(p));self.assertLess(proof['measuredAreaM2'],.25)
    def test_small_area_wide_hole_rejected(self):
        p=self.mesh(.01)
        with self.assertRaises(AssertionError):approve_roundoff(p,[0,0,1,1])
        self.assertNotIn('numericalCoverageGap',p['nativeMesh']['source'])
    def test_distance_valid_but_total_area_excess_rejected(self):
        p=self.mesh(.001,1000)
        with self.assertRaises(AssertionError):approve_roundoff(p,[0,0,1000,1])
    def test_source_unchanged_on_zero_gap_rejection(self):
        p=self.mesh(0);original=copy.deepcopy(p)
        with self.assertRaises(AssertionError):approve_roundoff(p,[0,0,1,1])
        self.assertEqual(p,original)

if __name__=='__main__':unittest.main()
