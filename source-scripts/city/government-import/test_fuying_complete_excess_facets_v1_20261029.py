import unittest
import numpy as np
import shapely
from fuying_complete_excess_facets_v1_20261029 import clipped_height
class FacetContext(unittest.TestCase):
    def test_crossing_face_extrema_are_clipped(self):
        face=np.array([[0.,0.,0.],[10.,10.,0.],[0.,0.,10.]])
        result=clipped_height(face,shapely.box(-1,-1,5,11))
        self.assertAlmostEqual(result['minY'],5)
        self.assertAlmostEqual(result['maxY'],10)
    def test_covered(self):
        self.assertIsNone(clipped_height(np.array([[0.,0.,0.],[1.,2.,0.],[0.,0.,1.]]),shapely.box(-1,-1,2,2)))
    def test_vertical_conservative(self):
        result=clipped_height(np.array([[0.,-2.,0.],[0.,8.,0.],[0.,1.,10.]]),shapely.box(-1,-1,1,5))
        self.assertTrue(result['verticalConservative'])
        self.assertEqual((result['minY'],result['maxY']),(-2,8))
    def test_hole_kept(self):
        face=np.array([[0.,0.,0.],[10.,10.,0.],[0.,0.,10.]])
        region=shapely.Polygon([(-1,-1),(11,-1),(11,11),(-1,11)], [[(1,1),(2,1),(2,2),(1,2)]])
        result=clipped_height(face,region)
        self.assertAlmostEqual(result['minY'],1)
        self.assertAlmostEqual(result['maxY'],2)
if __name__=='__main__':unittest.main()
