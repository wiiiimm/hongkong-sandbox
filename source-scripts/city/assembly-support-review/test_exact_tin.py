import unittest
import numpy as np
from exact_tin import rect,parent_clip
class ExactClipping(unittest.TestCase):
 def test_vertical_retaining_face_is_not_dropped(self):
  p=rect([np.array([0.,0.,0.]),np.array([0.,10.,0.]),np.array([0.,10.,10.])],[-1,2,1,8]);self.assertGreaterEqual(len(p),3);self.assertTrue(all(2<=v[2]<=8 for v in p));self.assertGreater(max(v[1] for v in p)-min(v[1] for v in p),0)
 def test_clip_preserves_native_plane(self):
  p=[np.array([0.,0.,0.]),np.array([10.,10.,0.]),np.array([0.,20.,10.])];q=parent_clip(p,np.array([[1.,1.],[3.,1.],[1.,3.]]));self.assertEqual(len(q),3)
  for v in q:self.assertAlmostEqual(v[1],v[0]+2*v[2])
if __name__=='__main__':unittest.main()
