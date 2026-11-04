import unittest
import numpy as np
import shapely
import native_patch_resolution as patches
from unittest.mock import patch

class LowerParentProjectionTest(unittest.TestCase):
 def candidate(self):
  return {'nativeMesh':{'position':[0,1,0,4,1,0,0,1,4],'index':[0,1,2]}}
 def test_crossing_planes_keep_only_lower_parent_region(self):
  parent=np.array([[0,0,0],[4,2,0],[0,0,4]],dtype=float)
  with patch.object(patches,'grid_surface_faces',return_value=[parent]):
   region,proof=patches.lower_parent_projection(self.candidate(),[0,0,4,4],shapely.box(0,0,4,4),None)
  self.assertAlmostEqual(region.area,6,places=6)
  self.assertTrue(region.covers(shapely.Point(1,1)))
  self.assertFalse(region.covers(shapely.Point(3,.5)))
  self.assertEqual(proof['planePairs'],1)
 def test_higher_parent_cannot_lower_native_surface(self):
  parent=np.array([[0,2,0],[4,2,0],[0,2,4]],dtype=float)
  with patch.object(patches,'grid_surface_faces',return_value=[parent]):
   region,_=patches.lower_parent_projection(self.candidate(),[0,0,4,4],shapely.box(0,0,4,4),None)
  self.assertTrue(region.is_empty)
 def test_empty_mask_does_not_read_or_change_surfaces(self):
  value=self.candidate();before=repr(value)
  region,_=patches.lower_parent_projection(value,[0,0,4,4],shapely.Polygon(),None)
  self.assertTrue(region.is_empty);self.assertEqual(repr(value),before)

if __name__=='__main__':unittest.main()
