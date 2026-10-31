import unittest
import numpy as np
from exact_private_parent_partition_v1_20261101 import partition_bound_parent
from test_exact_float32_parent_level_partition_v2_20261031 import REAL

def node(faces):return dict(nativeMesh=dict(position=np.asarray(faces).reshape(-1).tolist(),index=list(range(np.asarray(faces).size//3))))
def represented(faces):
 t=np.asarray(faces,dtype='<f4').astype(float).copy();n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);t[n[:,1]<0]=t[n[:,1]<0][:,[0,2,1]];return t
class PrivatePartitionTests(unittest.TestCase):
 def test_private_ramp_and_retaining_faces_remain_verbatim(self):
  private=represented([[[4,1.2,0],[7,3.6043324,0],[4,1.2,3]],[[8,1.2,0],[8,4,0],[8,4,2]],[[9,2,0],[9,2,0],[9,2,0]]]);raw=np.concatenate([REAL,private]);before=raw.copy();out,p=partition_bound_parent(raw,node(private));np.testing.assert_array_equal(raw,before);np.testing.assert_array_equal(out[-3:],private);self.assertEqual(p['completePrivateFaces'],3);self.assertEqual(p['retainedPrivateInputFaceIds'],[4,5,6]);self.assertTrue(p['exactPrivateFacetMultiplicityAndWindingPreserved']);self.assertEqual(p['subdividedParentFaces'],2)
 def test_missing_changed_or_insufficient_duplicate_private_faces_reject(self):
  private=represented([[[4,2,0],[7,4,0],[4,2,3]]]);raw=np.concatenate([REAL,private]);changed=node(private);changed['nativeMesh']['position'][0]+=1
  with self.assertRaisesRegex(AssertionError,'missing or changed'):partition_bound_parent(raw,changed)
  with self.assertRaisesRegex(AssertionError,'missing or changed'):partition_bound_parent(REAL,node(private))
  with self.assertRaisesRegex(AssertionError,'missing or changed'):partition_bound_parent(raw,node(np.concatenate([private,private])))
 def test_private_below_floor_rejects(self):
  private=represented([[[4,0,0],[7,4,0],[4,2,3]]])
  with self.assertRaisesRegex(AssertionError,'below'):partition_bound_parent(np.concatenate([REAL,private]),node(private))
 def test_unrepresented_capture_rejects(self):
  private=represented([[[4,2,0],[7,4,0],[4,2,3]]]);raw=np.concatenate([REAL,private]);raw[0,0,0]+=.00001
  with self.assertRaisesRegex(AssertionError,'represented Float32'):partition_bound_parent(raw,node(private))
 def test_rendered_winding_and_full_private_only_parent(self):
  original=np.array([[[4,2,0],[7,4,0],[4,2,3]]],float);actual=represented(original);out,p=partition_bound_parent(actual,node(original));np.testing.assert_array_equal(out,actual);self.assertEqual(p['subdividedParentFaces'],0)
if __name__=='__main__':unittest.main()
