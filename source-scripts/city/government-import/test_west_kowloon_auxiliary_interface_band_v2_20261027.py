import unittest
from fractions import Fraction as F
from west_kowloon_auxiliary_basic_interface_band_v2_20261027 import segmented_finite_host_bound

class SegmentedInterface(unittest.TestCase):
 def hosts(self,gap=False):
  return [(0,dict(dimension=1,exactPoints=[[0,0,0],[4 if gap else 5,0,0]])),(1,dict(dimension=1,exactPoints=[[6 if gap else 5,0,0],[10,0,0]]))]
 def test_tessellation_split_does_not_create_five_metre_false_bound(self):
  r=segmented_finite_host_bound(dict(dimension=1,exactPoints=[[0,0,0],[10,0,0]]),self.hosts())
  self.assertEqual(r['exactMaximumEndpointDistanceSquaredM2'],'0');self.assertEqual(len(r['pieces']),2)
 def test_parallel_rational_offset_retained_for_whole_partition(self):
  r=segmented_finite_host_bound(dict(dimension=1,exactPoints=[[0,'1/10',0],[10,'1/10',0]]),self.hosts())
  self.assertEqual(F(r['exactMaximumEndpointDistanceSquaredM2']),F(1,100));self.assertFalse(r['thresholdApplied'])
 def test_genuine_finite_gap_never_gets_exact_interface_credit(self):
  r=segmented_finite_host_bound(dict(dimension=1,exactPoints=[[0,0,0],[10,0,0]]),self.hosts(True))
  self.assertGreater(F(r['exactMaximumEndpointDistanceSquaredM2']),0)
 def test_noncollinear_contact_is_rejected(self):
  with self.assertRaises(AssertionError):segmented_finite_host_bound(dict(dimension=1,exactPoints=[[0,0,0],[10,0,0],[5,1,0]]),self.hosts())

if __name__=='__main__':unittest.main()
