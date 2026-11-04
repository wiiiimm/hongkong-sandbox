import unittest
import numpy as np
import shapely
from shapely.geometry import Polygon,Point
from source_surface_inset import inset_faces,plane

def square(height):
 p=np.array([[0,height(0,0),0],[2,height(2,0),0],[2,height(2,2),2],[0,height(0,2),2]],float)
 return p[[[0,1,2],[0,2,3]]]
def sample(faces,x,z):
 hits=[np.dot(plane(t),[x,z,1]) for t in faces if Polygon(t[:,[0,2]]).covers(Point(x,z))]
 return max(hits)
class InsetTests(unittest.TestCase):
 def test_crossing_planes_preserve_exact_lower_envelope_and_coverage(self):
  terrain=square(lambda x,z:1);source=square(lambda x,z:x);out,proof=inset_faces(terrain,source)
  self.assertAlmostEqual(proof['removedProjectedAreaM2'],2)
  self.assertAlmostEqual(shapely.union_all(shapely.polygons(out[:,:,[0,2]])).area,4)
  for x in [.13,.6,1,1.4,1.9]:
   for z in [.1,.7,1.3,1.9]:self.assertAlmostEqual(sample(out,x,z),min(1,x),places=8)
 def test_higher_surface_never_raises_ground(self):
  terrain=square(lambda x,z:1);out,proof=inset_faces(terrain,square(lambda x,z:2));np.testing.assert_array_equal(out,terrain);self.assertEqual(proof['changedTerrainFaceIndices'],[])
 def test_disjoint_geometry_remains_byte_identical(self):
  terrain=square(lambda x,z:1);source=square(lambda x,z:0);source[:,:,0]+=10;out,_=inset_faces(terrain,source);np.testing.assert_array_equal(out,terrain)
 def test_overlapping_source_is_rejected(self):
  source=square(lambda x,z:0)
  with self.assertRaises(ValueError):inset_faces(square(lambda x,z:1),np.concatenate([source,source]))
if __name__=='__main__':unittest.main()
