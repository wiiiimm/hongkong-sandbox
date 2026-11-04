import unittest,sys
from pathlib import Path
import numpy as np
import shapely
from source_surface_inset import plane
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'assembly-support-review'))
import exact_tin
from native_facet_band_return_v1 import join

def faces(b,y):
 x,z,X,Z=b;return np.array([[[x,y,z],[X,y,z],[x,y,Z]],[[X,y,z],[X,y,Z],[x,y,Z]]],float)
class Tests(unittest.TestCase):
 def test_flat_source_boundaries_and_full_projected_area(self):
  out,p=join(faces([-4,-4,4,4],0),faces([-3,-3,3,3],2),[-4,-4,4,4],[-3,-3,3,3],1,exact_tin,lambda q:[])
  self.assertAlmostEqual(sum(abs(np.cross(t[1]-t[0],t[2]-t[0])[1])/2 for t in out),64)
  for v in out.reshape(-1,3):
   if max(abs(v[0]),abs(v[2]))==3:self.assertEqual(v[1],0)
   if max(abs(v[0]),abs(v[2]))==2:self.assertEqual(v[1],2)
  self.assertAlmostEqual(p['oldFieldFallbackAreaM2']+p['newFieldFallbackAreaM2'],0)
 def test_authored_outer_step_is_retained_as_separate_layers(self):
  old=np.concatenate([faces([-4,-4,0,4],0),faces([0,-4,4,4],7)]);out,p=join(old,faces([-3,-3,3,3],2),[-4,-4,4,4],[-3,-3,3,3],1,exact_tin,lambda q:[])
  outer=[v for v in out.reshape(-1,3)if v[2]==-3];self.assertTrue(any(v[1]==0 for v in outer));self.assertTrue(any(v[1]==7 for v in outer));self.assertFalse(p['singleContinuousUpperGraphRequired'])
 def test_higher_new_field_selected_for_overlapping_layers(self):
  new=np.concatenate([faces([-3,-3,3,3],2),faces([-3,-3,3,3],8)]);out,p=join(faces([-4,-4,4,4],0),new,[-4,-4,4,4],[-3,-3,3,3],1,exact_tin,lambda q:[])
  self.assertEqual(p['newFieldFallbackAreaM2'],0);point=shapely.Point(0,-2.5);values=[np.array([0,-2.5])@plane(f)[:2]+plane(f)[2]for f in out if shapely.Polygon(f[:,[0,2]]).area>1e-10 and shapely.Polygon(f[:,[0,2]]).covers(point)];self.assertAlmostEqual(max(values),4)
if __name__=='__main__':unittest.main()
