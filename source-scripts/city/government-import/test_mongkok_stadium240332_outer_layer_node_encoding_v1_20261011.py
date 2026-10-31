import unittest
from fractions import Fraction as F
from mongkok_stadium240332_complete_outer_layer_encoding_inventory_v1_20261011 import f32node
class Tests(unittest.TestCase):
 def test_first_actual_exact_gap_same_bytes(self):
  p=(F(51171,40),F(-8615,2));a=F(11671,1400);b=F(70577894589,8466202624);self.assertNotEqual(a,b);self.assertEqual(f32node(p,a)['bytesHex'],f32node(p,b)['bytesHex'])
 def test_distinct_adjacent_float32_heights_reject_byte_equality(self):
  p=(F(0),F(0));self.assertNotEqual(f32node(p,F(1))['bytesHex'],f32node(p,F(8388609,8388608))['bytesHex'])
 def test_tiny_nonzero_near_zero_not_epsilon_accepted(self):
  p=(F(0),F(0));self.assertNotEqual(f32node(p,F(0))['bytesHex'],f32node(p,F(1,10**20))['bytesHex'])
 def test_actual_cast_xz_recorded(self):
  p=(F(51171,40),F(-8615,2));r=f32node(p,F(11671,1400));self.assertNotEqual(F(r['actualPosition'][0]),p[0]);self.assertEqual(F(r['actualPosition'][2]),p[1])
 def test_nonfinite_cast_rejected(self):
  with self.assertRaises(AssertionError):f32node((F(10**100),F(0)),F(0))
if __name__=='__main__':unittest.main()
