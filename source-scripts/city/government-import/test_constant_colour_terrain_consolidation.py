import copy,unittest
import numpy as np
from constant_colour_terrain_consolidation_v1 import consolidate_patch,colours

def fixture(veg):
 faces=[]
 for z in [0,1]:
  for x in [0,1]:
   a=[x,5,z];b=[x+1,5,z];c=[x,5,z+1];d=[x+1,5,z+1];faces.extend([[a,b,c],[b,d,c]])
 t=np.asarray(faces,float)
 return dict(w=3,h=3,vegetation=veg,meta=dict(georef=dict(aE=1,aN=-1,bE=834500,bN=816500)),nativeMesh=dict(position=t.reshape(-1).tolist(),index=list(range(t.size//3))))
class ColourConsolidationTests(unittest.TestCase):
 def test_uniform_plane_consolidates_and_leaves_input_unchanged(self):
  p=fixture([0]*9);before=copy.deepcopy(p);out,proof=consolidate_patch(p);self.assertLess(len(out),8);self.assertTrue(proof['allOriginalFacesAccounted']);self.assertEqual(p,before);self.assertFalse(colours(out,p).any())
 def test_mixed_faces_preserve_colour_interpolation(self):
  p=fixture([0,1,0,1,0,1,0,1,0]);out,proof=consolidate_patch(p);self.assertEqual(len(out),8);self.assertEqual(len(proof['mixedColourOriginalFaceIds']),8);np.testing.assert_array_equal(out,np.asarray(p['nativeMesh']['position']).reshape(-1,3,3))
 def test_js_rounding_ties_follow_positive_infinity(self):
  p=fixture([0,1,0,0,0,0,0,0,0]);self.assertTrue(colours(np.array([[.5,5,0]]),p)[0])
 def test_shared_vertex_shading_is_not_silently_changed(self):
  p=fixture([0]*9);p['nativeMesh']['index'][1]=0
  with self.assertRaisesRegex(AssertionError,'nonshared'):consolidate_patch(p)
