import unittest
import numpy as np
import shapely
from original_degenerate_ground_context_20261009 import degenerate_ground_context

class DegenerateGroundTests(unittest.TestCase):
    def check(self,face,ground):
        g=np.asarray(ground,float);p=shapely.polygons(g[:,:,[0,2]])
        return degenerate_ground_context(face,g,p,shapely.STRtree(p))
    def ground(self):return [[[-3,0,-3],[3,0,-3],[0,0,3]]]
    def test_vertical_original_line_keeps_lowest_point(self):
        r=self.check([[0,-2,0],[0,1,0],[0,4,0]],self.ground())
        self.assertTrue(r['groundProjectionCovered']);self.assertEqual(r['minimum']['minimumGapM'],-2)
    def test_projected_line_continuous_clearance(self):
        r=self.check([[-1,1,0],[0,2,0],[1,3,0]],self.ground())
        self.assertEqual(r['minimum']['minimumGapM'],1);self.assertFalse(r['installationApproved'])
    def test_coincident_point_is_not_dropped(self):
        r=self.check([[0,.2,0]]*3,self.ground())
        self.assertEqual(r['minimum']['minimumGapM'],.2)
    def test_missing_ground_is_not_excused_by_zero_area(self):
        r=self.check([[-5,0,0],[0,0,0],[5,0,0]],self.ground())
        self.assertFalse(r['groundProjectionCovered']);self.assertGreater(r['uncoveredProjectionLengthM'],0)
    def test_nondegenerate_face_rejects(self):
        with self.assertRaises(AssertionError):self.check([[0,0,0],[1,0,0],[0,0,1]],self.ground())
    def test_highest_overlapping_ground_controls_clearance(self):
        g=self.ground()+[[[x,2,z] for x,y,z in self.ground()[0]]]
        r=self.check([[0,1,0]]*3,g)
        self.assertEqual(r['minimum']['minimumGapM'],-1)

if __name__=='__main__':unittest.main()
