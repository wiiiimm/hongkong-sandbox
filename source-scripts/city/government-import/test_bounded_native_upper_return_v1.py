import unittest,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'assembly-support-review'))
import exact_tin
from bounded_native_upper_return_v1 import join,boundary,value

def faces(b,y):
 x,z,X,Z=b;return np.array([[[x,y,z],[X,y,z],[x,y,Z]],[[X,y,z],[X,y,Z],[x,y,Z]]],float)
class Tests(unittest.TestCase):
 def test_complete_strip_retains_outer_and_inner_heights_and_area(self):
  out,proof=join(faces([-4,-4,4,4],0),faces([-3,-3,3,3],2),[-4,-4,4,4],[-3,-3,3,3],1,exact_tin)
  self.assertAlmostEqual(sum(abs(np.cross(t[1]-t[0],t[2]-t[0])[1])/2 for t in out),64)
  for p in out.reshape(-1,3):
   if max(abs(p[0]),abs(p[2]))==3:self.assertEqual(p[1],0)
   if max(abs(p[0]),abs(p[2]))==2:self.assertEqual(p[1],2)
  self.assertTrue(proof['exactPrepackingBoundaryHeights'])
 def test_maximum_layer_selected_not_lower_source(self):
  rows,_=boundary(np.concatenate([faces([-4,-4,4,4],0),faces([-4,-4,4,4],7)]),[-3,-3,3,3]);self.assertEqual(value(rows,0,0),7)
 def test_missing_finite_parent_coverage_rejects(self):
  with self.assertRaises(AssertionError):join(faces([-1,-1,1,1],0),faces([-3,-3,3,3],2),[-4,-4,4,4],[-3,-3,3,3],1,exact_tin)
if __name__=='__main__':unittest.main()
