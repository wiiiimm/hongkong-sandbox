import unittest
import shapely
from selected_original_primary_revision_diagnostic_v2_20261102 import provider_single_shell

def provider(shell,holes=()):
 return [[[834500+x,816500-z]for x,z in ring]for ring in [shell,*holes]]

class RingTests(unittest.TestCase):
 def setUp(self):
  self.shell=[[0,0],[10,0],[10,10],[0,10],[0,0]]
  self.hole=[[2,2],[2,4],[4,4],[4,2],[2,2]]
 def test_single_ring_identical(self):
  self.assertTrue(provider_single_shell(provider(self.shell)).equals_exact(shapely.Polygon(self.shell),0))
 def test_hole_is_preserved(self):
  p=provider_single_shell(provider(self.shell,[self.hole]));self.assertEqual(p.area,96);self.assertEqual(len(p.interiors),1);self.assertFalse(p.covers(shapely.Point(3,3)))
 def test_wrong_winding_rejected(self):
  with self.assertRaises(AssertionError):provider_single_shell(provider(self.shell,[list(reversed(self.hole))]))
 def test_escaped_hole_rejected(self):
  with self.assertRaises(AssertionError):provider_single_shell(provider(self.shell,[[[x+20,z]for x,z in self.hole]]))
 def test_overlapping_holes_rejected(self):
  with self.assertRaises(AssertionError):provider_single_shell(provider(self.shell,[self.hole,self.hole]))

if __name__=='__main__':unittest.main()
