"""Named relationship mutation tests plus stable complete even/odd ring parity."""
import unittest
from unittest.mock import patch
import shapely
import science_attached_open_canopy_identity_v2_20261009 as identity
import test_science_attached_open_canopy_identity_20261009 as existing
existing.identity=identity
ScienceRelationshipTests=existing.ScienceRelationshipTests
class StableRingParityTests(unittest.TestCase):
 def test_three_nested_rings_preserve_island(self):
  rings=[[(0,0),(4,0),(4,4),(0,4),(0,0)],[(1,1),(3,1),(3,3),(1,3),(1,1)],[(1.5,1.5),(2.5,1.5),(2.5,2.5),(1.5,2.5),(1.5,1.5)]];shape=identity.polygon(rings);self.assertEqual(shape.area,13);self.assertTrue(shape.covers(shapely.Point(2,2)));self.assertFalse(shape.covers(shapely.Point(1.25,1.25)))
 def test_three_overlap_parity_keeps_triple_area(self):
  rings=[[(0,0),(3,0),(3,3),(0,3),(0,0)],[(1,0),(4,0),(4,3),(1,3),(1,0)],[(2,0),(5,0),(5,3),(2,3),(2,0)]];shape=identity.polygon(rings);self.assertEqual(shape.area,9);self.assertTrue(shape.covers(shapely.Point(2.5,1)));self.assertFalse(shape.covers(shapely.Point(1.5,1)))
 def test_removed_deprecated_api_is_never_called(self):
  with patch.object(shapely,'symmetric_difference_all',side_effect=RuntimeError('future API removed')):self.assertEqual(identity.polygon([[(0,0),(1,0),(1,1),(0,1),(0,0)]]).area,1)
if __name__=='__main__':unittest.main()
