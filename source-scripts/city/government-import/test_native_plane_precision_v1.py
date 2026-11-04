import unittest
from native_plane_precision_v1 import assess
class Tests(unittest.TestCase):
 def test_horizontal_and_vertical_source_planes(self):
  self.assertTrue(assess([[0,6,0],[2,6,0],[0,6,2]],[1,6,1])['withinNativeCoordinatePrecision'])
  self.assertTrue(assess([[2,0,0],[2,9,0],[2,0,3]],[2,4,1])['withinNativeCoordinatePrecision'])
 def test_wrong_height_not_accepted_as_packing(self):
  self.assertFalse(assess([[0,6,0],[2,6,0],[0,6,2]],[1,6.01,1])['withinNativeCoordinatePrecision'])
if __name__=='__main__':unittest.main()
