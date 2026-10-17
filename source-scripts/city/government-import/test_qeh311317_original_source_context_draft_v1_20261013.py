import unittest,tempfile,hashlib
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
import qeh311317_original_far_neighbour_source_context_draft_v1_20261013 as Q
class Cases(unittest.TestCase):
 def setUp(self):self.target=Polygon([(0,0),(2,0),(2,2),(0,2)]);self.region=Polygon([(12,0),(13,0),(13,2),(12,2)])
 def tri(self,x):return np.array([[[x,0,0],[x+1,0,0],[x,0,1]]],dtype=float)
 def test_far_strict_threshold(self):self.assertEqual(Q.selections(self.tri(11),self.target,self.region)[0],[])
 def test_far_whole_face_id(self):self.assertEqual(Q.selections(self.tri(12),self.target,self.region)[0],[0])
 def test_neighbour_boundary_touch_preserved(self):self.assertEqual(Q.selections(self.tri(11),self.target,self.region)[1],[0])
 def test_vertical_not_projected_region_credit(self):self.assertEqual(Q.selections(np.array([[[12,0,0],[12,2,0],[12,3,1]]]),self.target,self.region)[1],[])
 def test_nonfinite_rejected(self):
  t=self.tri(12);t[0,0,1]=np.nan
  with self.assertRaises(AssertionError):Q.selections(t,self.target,self.region)
 def test_complete_partition_zeros(self):self.assertEqual(Q.validate_partition({'sharedEdgeConnectedComponents':[[0,2]],'exactNonrenderingOriginalFaces':[1]},3),({0:0,2:0},[1]))
 def test_partition_duplicate_rejected(self):
  with self.assertRaises(AssertionError):Q.validate_partition({'sharedEdgeConnectedComponents':[[0,1]],'exactNonrenderingOriginalFaces':[1]},3)
 def test_changed_pin_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d);(r/'x').write_bytes(b'b')
   with self.assertRaises(AssertionError):Q.check_pins([{'path':'x','sha256':hashlib.sha256(b'a').hexdigest()}],r)
 def test_escape_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(AssertionError):Q.check_pins([{'path':'../escape','sha256':'x'}],Path(d))
if __name__=='__main__':unittest.main()
