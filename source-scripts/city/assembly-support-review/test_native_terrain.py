import unittest
import numpy as np
import shapely
from native_terrain import samples
class NativeTerrainTests(unittest.TestCase):
 def test_barycentric_slope_and_missing_coverage(self):
  tri=np.array([[[0,10,0],[10,20,0],[0,30,10]]],dtype=float);tree=shapely.STRtree(shapely.polygons(tri[:,:,[0,2]]));result=samples(np.array([[2,3],[9,9]]),tri,tree)
  self.assertAlmostEqual(result[0],18);self.assertFalse(np.isfinite(result[1]))
 def test_overlapping_source_levels_take_upper_actual_triangle(self):
  tri=np.array([[[0,10,0],[10,10,0],[0,10,10]],[[0,12,0],[10,12,0],[0,12,10]]],dtype=float);tree=shapely.STRtree(shapely.polygons(tri[:,:,[0,2]]));self.assertEqual(samples(np.array([[2,2]]),tri,tree)[0],12)
if __name__=='__main__':unittest.main()
