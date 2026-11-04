import unittest
import numpy as np
from shapely.geometry import Polygon
from component_roof_coverage import above_height_projection,measure
class CoverageTest(unittest.TestCase):
 def test_crossing_triangle_uses_interpolated_intersection(self):
  source=np.array([[[0,0,0],[4,4,0],[0,4,4]]],dtype=float);copy=source.copy()
  projected=above_height_projection(source,2)
  self.assertAlmostEqual(projected.area,6)
  self.assertTrue(np.array_equal(source,copy))
 def test_tall_face_outside_component_does_not_credit_short_roof(self):
  source=np.array([[[0,8,0],[2,8,0],[0,8,2]],[[10,50,10],[12,50,10],[10,50,12]]],dtype=float)
  result=measure(source,Polygon([(0,0),(2,0),(2,2),(0,2)]),49.5)
  self.assertEqual(result['coveredFraction'],0)
  self.assertFalse(result['acceptanceGranted'])
 def test_full_flat_roof_and_empty_above_roof(self):
  source=np.array([[[0,10,0],[2,10,0],[0,10,2]],[[2,10,0],[2,10,2],[0,10,2]]],dtype=float)
  self.assertAlmostEqual(above_height_projection(source,10).area,4)
  self.assertTrue(above_height_projection(source,11).is_empty)
 def test_invalid_height_rejected(self):
  with self.assertRaises(ValueError):above_height_projection(np.zeros((1,3,3)),float('nan'))
if __name__=='__main__':unittest.main()
