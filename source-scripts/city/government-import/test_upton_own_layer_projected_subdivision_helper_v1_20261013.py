import unittest
from fractions import Fraction as F
import numpy as np
from upton_own_layer_projected_subdivision_helper_v1_20261013 import own_layer_subdivision

class OwnLayer(unittest.TestCase):
 def setUp(self):
  self.t=((0,0,0),(2,2,0),(0,0,2));self.raw=np.asarray(self.t,dtype='<f8');self.aliases=[(1,9,0),(1,10,0),(1,11,0)]
 def run_case(self,**kw):
  args=dict(triangle=self.t,raw_triangle=self.raw,edge=0,aliases=self.aliases,packed_aliases=self.aliases,ancestor=self.t,saved_parameter='1/2');args.update(kw);return own_layer_subdivision(**args)
 def test_own_height_not_other_layer(self):
  p=self.run_case();self.assertEqual(p['exactOwnLayerNodeXYZ'],(F(1),F(1),F(0)));self.assertTrue(p['exactPartitionProof']['completeIdealTrianglePreserved']);self.assertEqual([p[1]for p in p['unchangedOtherLayerXYZ']],[9,10,11])
 def test_different_other_heights_cannot_change_new_y(self):self.assertEqual(self.run_case(aliases=[(1,-999,0),(1,100,0),(1,99,0)])['exactOwnLayerNodeXYZ'][1],1)
 def test_noncollinear_projected_alias_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(aliases=[(1,9,F(1,1000000)),(1,10,F(1,1000000)),(1,11,F(1,1000000))])
 def test_packed_xz_mismatch_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(packed_aliases=[(1,9,1),(1,10,1),(1,11,1)])
 def test_wrong_saved_parameter_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(saved_parameter='1/3')
 def test_protected_target_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(protected_target=True)
 def test_protected_own_node_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(protected_points=[(1,1,0)])
 def test_ancestor_plane_mismatch_rejected(self):
  with self.assertRaises(AssertionError):self.run_case(ancestor=((0,1,0),(2,3,0),(0,1,2)))
 def test_signed_zero_original_endpoints_preserved(self):
  raw=self.raw.copy();raw[0,0]=-0.0;p=self.run_case(raw_triangle=raw);points=np.asarray(p['packedPieceTriplets'],dtype='<f8');found=[q for piece in points for q in piece if q[1]==0 and q[2]==0];self.assertTrue(any(q.tobytes()==raw[0].tobytes()for q in found))
if __name__=='__main__':unittest.main()
